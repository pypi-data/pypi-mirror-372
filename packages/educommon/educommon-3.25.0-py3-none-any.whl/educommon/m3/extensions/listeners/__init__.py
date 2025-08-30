"""Расширение поведения экшнов."""

from m3.actions import (
    OperationResult,
)
from m3.actions.context import (
    ActionContext,
    ContextBuildingError,
    CriticalContextBuildingError,
    RequiredFailed,
)
from m3_ext.ui.results import (
    ExtUIScriptResult,
)

from educommon.m3.extensions.ui import (
    BaseEditWinExtender,
)


class DeclareContextListener:
    """Предок листенеров.

    Предоставляет возможность задекларировать дополнительный контекст
    выполнения экшна.
    """

    def before(self, request, context):
        """Действия перед вызовом экшна."""
        # получение контекста по "обновленным правилам", если они были
        rebuilt_context = self._rebuild_context(request, context)
        rebuilt_context_dict = rebuilt_context.__dict__
        if rebuilt_context_dict:
            # этот же страх делается и внутри метода ``ActionContext.combine``
            context.__dict__.update(rebuilt_context_dict)

    def _declare_additional_context(self):
        """Дополнительная декларация контекста."""
        return {}

    def _rebuild_context(self, request, context):
        """Пересбор контекста с учетом дополнительных правил."""
        rules = self.action.context_declaration()
        additional_rules = self._declare_additional_context()

        if not additional_rules:
            # дополнительно ничего не задекларировали, возврат пустого контекст
            return ActionContext()
        else:
            rules.update(additional_rules)

        context = self.action.parent.controller.build_context(request, rules)

        # ниже стандартное поведение платформы ``ActionController._invoke``
        try:
            context.build(request, rules)
        except CriticalContextBuildingError:
            # критическая ошибка сбора контекста - должна валиться
            raise
        except ContextBuildingError as e:
            # некритичную ошибку - показываем пользователю
            return OperationResult.by_message(str(e))
        except RequiredFailed as e:
            # если контекст неправильный, то возвращаем
            # фейльный результат операции
            return OperationResult.by_message(
                f'Не удалось выполнить операцию. Не задан обязательный<br>параметр: {e.reason}'
            )

        return context


class BaseEditWinListener(DeclareContextListener):
    """Базовый листенер для расширения окна редактирования доп.полями и данными.

    Окно редактирования связано с определенной моделью, она - расширяемая и ее
    данные требуется дополнить с помощью доп.полей.
    """

    # класс-наследник BaseEditWinExtender
    # отвечает за расширение интерфейса окна и биндинг
    ui_extender_cls = None
    # имя поля, которое ссылается на расширяемую модель
    parent_model_field = None

    def _get_id(self, context):
        """Получение из контекста параметра, определяющего id расширяемой модели.

        :rype: int
        """
        raise NotImplementedError()

    def _get_instance(self, row_id):
        """Получение модели, которая расширяет основную ``ui_extender_cls.model``.

        :param row_id: идентификатор расширяемой модели
        :rtype: object
        """
        try:
            instance = self.ui_extender_cls.model.objects.get(**{self.parent_model_field: row_id})
        except self.ui_extender_cls.model.DoesNotExist:
            # расширяющая модель еще только создается
            return

        return instance

    def _get_params(self, instance, context):
        """Дополнение параметров."""
        return {'instance': instance}

    def after(self, request, context, response):
        """Получение истанса модели, которая расширяет и биндинг ее в окно.

        :param request: Request
        :type request: django.http.HttpRequest
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        """
        if not isinstance(response, ExtUIScriptResult):
            # не окно
            return
        assert self.parent_model_field, 'No parent model field defined in listener!'
        assert issubclass(self.ui_extender_cls, BaseEditWinExtender)

        # расширение интерфейса
        extender = self.ui_extender_cls(response.data)

        # получение id родительской модели
        row_id = self._get_id(context)
        if not row_id:
            return

        # получение инстанса расширяющей модели
        instance = self._get_instance(row_id)
        if not instance:
            return

        # биндинг в окно
        extender.bind_from_object(instance)
        # установка параметров
        params = self._get_params(instance, context)
        extender.set_params(params)


class BaseSaveListener(DeclareContextListener):
    """Базовый класс листенеров сохранения доп.данных.

    Обращение к данному листенеру из экшна делается через

    ..code::

        self.handle('post_save', (obj, context))

    после вызова сохранения ``obj`` (в т.ч. внутри транзакции),
    где obj - инстанс родительской модели (``parent_model_instance``)
    """

    # класс-наследник BaseEditWinExtender
    ui_extender_cls = None
    # имя поля, ссылающуюся на родительскую модель
    parent_model_field = None

    def _get_instance(self, parent_model_instance, context):
        """Получение инстанса расширяющей модели.

        Метод вынесен для возможности инстанцирования дополнительных
        зависимых моделей (относительно расширяющей модели ``instance``)

        :param parent_model_instance: инстанс расширяемой модели
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        :returns: инстанс расширяющей модели
        """
        try:
            instance = self.ui_extender_cls.model.objects.get(**{self.parent_model_field: parent_model_instance})
        except self.ui_extender_cls.model.DoesNotExist:
            instance = self.ui_extender_cls.model(**{self.parent_model_field: parent_model_instance})

        return instance

    def post_save(self, arguments):
        """Точка входа для расширения из экшна self.handle('post_save', *).

        :param parent_model_instance: инстанс расширяемой модели
        :param context: Context
        :type context: m3.actions.context.DeclarativeActionContext
        """
        parent_model_instance, context = arguments
        assert self.parent_model_field, 'No parent model field defined in listener!'
        assert issubclass(self.ui_extender_cls, BaseEditWinExtender)

        instance = self._get_instance(parent_model_instance, context)
        self.ui_extender_cls.bind_to_object(instance, context)

        self._save_instance(instance)

        return parent_model_instance, context

    def _save_instance(self, instance):
        """Сохранение расширяющей модели.

        Вынесено для возможности сохранения связанных/зависимых сущностей.
        """
        instance.full_clean()
        instance.save()
