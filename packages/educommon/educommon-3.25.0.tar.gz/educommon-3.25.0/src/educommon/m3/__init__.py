"""Вспомогательные средства для работы с компонентами M3."""

import inspect
import sys
from functools import (
    wraps,
)

from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError as DjangoValidationError,
)
from django.db.models.base import (
    Model,
    ModelBase,
)
from django.db.transaction import (
    atomic,
)
from django.utils.encoding import (
    force_str,
)

from m3.actions import (
    Action,
    ActionPack,
    ControllerCache,
)
from objectpack.exceptions import (
    ValidationError as ObjectPackValidationError,
)
from objectpack.models import (
    ModelProxy,
    ModelProxyMeta,
)
from objectpack.observer.base import (
    ObservableController,
)

from educommon import (
    ioc,
)
from educommon.utils.misc import (
    NoOperationCM,
)


def convert_validation_error_to(exc, new_line='<br/>', model=None):
    """Декоратор, преобразующий исключение
    django.core.exceptions.ValidationError, генерируемое в декорируемой
    функции, в исключение, указанное в аргументе exc путем объединения всех
    сообщений об ошибках из ValidationError.message_dict в одно сообщение, по
    одной ошибке на строку.

    Пример использования:

        class Pack(ObjectPack):
            ...
            @convert_validation_error_to(ApplicationLogicException)
            def save_row(self, obj, create_new, request, context):
                obj.full_clean()
                ...

    :param exc: класс исключения, к которому будет преобразовываться
        ValidationError
    :type exc: subclass of Exception

    :param str new_line: разделитель строк в сообщении об ошибке

    :param model: Модель, в которой осуществляется валидация. Должна
        использоваться в тех случаях, когда исключение ValidationError
        генерируется вне модели (например, в методе ObjectPack.save_row).
        Если аргумент указан, то данные будут извлекаться именно из этой
        модели.
    """

    def get_model_meta(error):
        if model is not None:
            return model._meta

        # Достанем из стека вызовов объект модели, в которой было
        # вызвано исключение. Из него будем брать verbose_name полей.
        tb = sys.exc_info()[-1]  # traceback
        # Фрейм, в котором сгенерировано исключение, будет последним.
        error_frame = inspect.getinnerframes(tb)[-1][0]
        # f_locals - локальные переменные функции, в т.ч. аргументы.
        if 'self' not in error_frame.f_locals:
            raise
        model_instance = error_frame.f_locals['self']

        return model_instance._meta

    def get_messages_from_dict(model_meta, data):
        result = []
        for field_name, field_errors in data.items():
            if field_name == NON_FIELD_ERRORS:
                result.append(new_line.join('- {0}'.format(err) for err in field_errors))
            else:
                model_field = model_meta.get_field(field_name)
                verbose_name = model_field.verbose_name or ''
                result.append(new_line.join('- {0}: {1}'.format(verbose_name, err) for err in field_errors))

        return result

    def get_messages_from_list(messages):
        result = ['- ' + message for message in messages]

        return result

    assert issubclass(exc, Exception), type(exc)
    new_line = str(new_line)

    def decorator(func):
        assert inspect.ismethod(func) or inspect.isfunction(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DjangoValidationError as e:
                model_meta = get_model_meta(e)

                if hasattr(e, 'message_dict'):
                    title = 'На форме имеются некорректно заполненные поля:'
                    messages = [title] + get_messages_from_dict(model_meta, e.message_dict)
                else:
                    title = 'При проверке данных найдены ошибки:'
                    messages = [title] + get_messages_from_list(e.messages)
                messages.insert(1, '')

                raise exc(new_line.join(messages))

        return wrapper

    return decorator


class ModelProxyValidationMixin:
    """Примесь для составных прокси-моделей objectpack'а.

    Добавляет к *objectpack.models.ModelProxy* возможность валидации данных
    перед сохранением. Валидация осуществляется, как и в моделях Django, путем
    запуска метода *full_clean()* для каждой зависимой модели, порядок запуска
    соответствует порядку указания моделей в *relations*. После выполнения
    валидации зависимых моделей запускается *full_clean()* основной модели.
    """

    def __update_error_dict(self, error, errors, model_name):
        model_errors = error.update_error_dict({})

        for field_name, messages in model_errors.items():
            # В зависимости от версии Django в messages могут быть
            # как сообщения в виде строк, так и экземпляры ValidationError,
            # поэтому приводим его к списку, содержащему только строки
            messages = sum([m.messages if isinstance(m, DjangoValidationError) else [m] for m in messages], [])

            if field_name != NON_FIELD_ERRORS:
                full_field_name = '.'.join((model_name, field_name))
                try:
                    self._meta.get_field(full_field_name)
                except KeyError:
                    full_field_name += '_id'

                    # В этом месте будет либо KeyError, либо поле
                    # field_name - внешний ключ. В первом случае в
                    # error содержится информация о несуществующем
                    # поле. Во втором случае - поле является внешним
                    # ключом, а в случае составной модели это ошибка,
                    # связанная с тем, что объект связанной модели еще
                    # не сохранен в БД. Поэтому пропустим эту ошибку -
                    # объект будет создан при сохранении составной
                    # модели.
                    field = self._meta.get_field(full_field_name)
                    if force_str(field.error_messages['null']) in messages:
                        messages.remove(field.error_messages['null'])
                    if not messages:
                        continue

                errors.setdefault(full_field_name, []).extend(messages)
            else:
                errors.setdefault(NON_FIELD_ERRORS, []).extend(messages)

        return errors

    def full_clean(self, exclude=None):
        """Валидация данных составной модели.

        :param list exclude: Список полей составной модели, исключаемых из
            проверки. Например: 'relation', 'relation1.relation2.name'.

            .. note::
               При многоуровневой вложенности вложенная составная модель также
               должна поддерживать валидацию данных (иметь метод
               *full_clean()*).

        :raises django.core.exceptions.ValidationError: Если данные составной
            модели некорректны.
        """
        primary_model_name = self.model.__name__.lower()

        # Связывание зависимых объектов с основным объектом составной модели
        primary_model = getattr(self, primary_model_name)
        for relation in self.relations:
            relation = relation.split('.')[0]
            setattr(primary_model, relation, getattr(self, relation))

        exclude = exclude or []
        errors = {}

        models = (  # элементы составной модели
            name for name in (list(self.relations) + [primary_model_name]) if not exclude or name not in exclude
        )

        for model_name in models:
            # В этом цикле вызываем метод full_clean() у всех вложенных моделей
            # в порядке, указанном в relations. После этого вызываем
            # full_clean() для основной модели.
            model = self
            for attr in model_name.split('.'):
                model = getattr(model, attr, None)
                if model is None:
                    break
            else:
                # Здесь в model должен быть объект модели, для которого будет
                # вызван full_clean().

                # Формируем список исключаемых из проверки полей модели model
                model_exclude = []
                for e in exclude:
                    if '.' not in e:
                        # в списке исключений указана вложенная модель целиком,
                        # но они отбрасываются при формировании списка models,
                        # поэтому сразу игнорируем этот элемент
                        continue
                    m, f = e.rsplit('.', 1)
                    if m != model_name:
                        continue
                    model_exclude.append(f)

                try:
                    model.full_clean(model_exclude)
                except DjangoValidationError as error:
                    errors = self.__update_error_dict(error, errors, model_name)
                    if not errors:
                        valid_key = '_ModelValidationMixin__object_is_valid'
                        model.__dict__[valid_key] = True

        if errors:
            raise DjangoValidationError(errors)


class BaseModelProxy(ModelProxyValidationMixin, ModelProxy):
    """Базовый класс для составных прокси моделей с валидацией.

    .. seealso::
        - :py:class: objectpack.models.ModelProxy
        - :py:class: ModelProxyValidationMixin
    """


class PackValidationMixin:
    """Примесь к пакам из objectpack, добавляющая валидацию моделей.

    Перед сохранением объекта в методе *save_row()* пака выполняется проверка
    данных путем вызова метода *full_clean()* сохраняемого объекта.

    .. note::
       При использовании в паке составной модели
       (*objectpack.models.ModelProxy*) в такой модели должен быть реализован
       метод *full_clean()* (см. *ModelProxyValidationMixin* и
       *BaseModelProxy*).

    Пример использования:

       class UnitPack(PackValidationMixin, TreeObjectPack):
           ...

       class PeriodPack(PackValidationMxin, ObjectPack):
           ....
    """

    @convert_validation_error_to(ObjectPackValidationError)
    def save_row(self, obj, create_new, request, context):
        """Вызывает проверку данных перед их сохранением в БД."""
        from objectpack.slave_object_pack.actions import (
            SlavePack,
        )

        if isinstance(self, SlavePack):
            obj.__dict__.update(self._get_parents_dict(context, key_fmt='%s_id'))
            save_row = super(SlavePack, self).save_row
        else:
            save_row = super(PackValidationMixin, self).save_row

        if getattr(obj, 'clean_and_save_inside_transaction', False):
            cm = atomic()
        else:
            cm = NoOperationCM()

        with cm:
            obj.full_clean()
            save_row(obj, create_new, request, context)


def get_pack(pack_or_model):
    """Возвращает экземпляр указанного пака.

    Пак может быть задан:
        - именем класса в пакете: 'extedu.unit.actions.Pack'
        - классом пака: Pack
        - именем класса модели: 'Unit'
        - классом модели: Unit
        - экземпляром класса модели: unit

    В первых двух случаях поиск пака осуществляется с помощью метода
    *ControllerCache.find_pack()*. В остальных случаях - через метод *get()*
    экземпляра Observer, соответственно для модели должен быть зарегистрирован
    основной пак (*_is_primary_for_model* должен быть равен *True*).

    Если указаны аргументы *pack*, либо *model*, то параметр *pack_or_model*
    игнорируется. Эти аргументы не могут быть указаны одновременно.

    :raises AssertionError: Если указанный пак не был найден.
    """
    observer = ioc.get('observer')

    if (isinstance(pack_or_model, str) and '.' in pack_or_model) or (
        inspect.isclass(pack_or_model) and issubclass(pack_or_model, ActionPack)
    ):
        # Пак задан именем класса в пакете или классом
        result = ControllerCache.find_pack(pack_or_model)
    elif isinstance(pack_or_model, str):
        result = observer.get(pack_or_model)
    elif isinstance(pack_or_model, (Model, ModelProxy)):
        # Пак задан экземпляром модели
        result = observer.get(pack_or_model.__class__.__name__)
    elif isinstance(pack_or_model, (ModelBase, ModelProxyMeta)):
        result = observer.get(pack_or_model.__name__)
    else:
        raise TypeError(pack_or_model)

    assert result is not None, repr(pack_or_model)

    return result


def get_pack_id(pack_or_model):
    """Возвращает имя параметра, идентифицирующего объект.

    .. note::
       Вызов get_pack_id('Unit') аналогичен вызову
       get_pack('Unit').id_param_name.

    :param pack_or_model: Аргумент, определяющий пак, из которого будет
        получено имя параметра, идентифицирующего объект (*id_param_name*).

    :rtype: str
    """
    pack = get_pack(pack_or_model)
    result = pack.id_param_name

    return result


def get_id_value(context, pack_or_model):
    """Возвращает значение параметра, идентифицирующего объект.

    Значение извлекается из контекста запроса *context*, имя параметра
    определяется свойством *id_param_name* пака. Пак определяется аргументом
    *pack_or_model*.

    .. note::
        Вызов get_id_value(context, 'Unit') аналогичен вызову
        getattr(context, get_pack('Unit').id_param_name).

    :param context: Контекст HTTP-запроса.
    :type context: VerboseDeclarativeContext

    :param pack_or_model: Аргумент, определяющий пак, из которого будет
        получено имя параметра, идентифицирующего объект (*id_param_name*).
    """
    assert isinstance(context, ObservableController.VerboseDeclarativeContext), type(context)

    if isinstance(pack_or_model, (Action, ActionPack)):
        pack_or_model = pack_or_model.__class__

    pack = get_pack(pack_or_model)
    result = getattr(context, pack.id_param_name)

    return result
