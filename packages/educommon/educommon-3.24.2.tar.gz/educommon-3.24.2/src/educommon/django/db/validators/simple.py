"""Валидаторы для простых (текстовых, числовых и т.п.) полей модели Django."""

import re
from datetime import (
    datetime,
)
from functools import (
    partial,
)
from itertools import (
    cycle,
)

import magic
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError,
)
from django.core.validators import (
    DecimalValidator,
    RegexValidator,
)
from django.utils.deconstruct import (
    deconstructible,
)

from educommon.django.db.utils import (
    get_original_object,
)
from educommon.django.db.validators import (
    IModelValidator,
    validate_value,
)
from educommon.utils.misc import (
    get_mime_type_for_extension,
)


# =============================================================================
# СНИЛС
# =============================================================================
_snils_re = re.compile(r'^\d{3}-\d{3}-\d{3} \d{2}$')  # СНИЛС


class SNILSValidator(RegexValidator):
    """Валидатор СНИЛС.

    Проверяет корректность формата и контрольное число (последние две цифры).

    :raises django.core.exceptions.ValidationError: Если аргумент value
        содержит значение, несоответствующее формату СНИЛС, либо контрольное
        число некорректно.
    """

    regex = _snils_re.pattern
    message = 'СНИЛС должен быть в формате ###-###-### ##'
    flags = _snils_re.flags

    def __call__(self, value):
        super().__call__(value)
        snils_checksum_validator(value)


def snils_checksum_validator(value):
    value = str(value)

    if value[:11] <= '001-001-998':
        return

    numbers = (int(ch) for ch in reversed(value[:11]) if ch.isdigit())
    checksum = int(value[12:14])
    summa = sum(i * n for i, n in enumerate(numbers, 1))
    if summa > 101:
        summa %= 101

    if summa < 100 and summa != checksum or summa in (100, 101) and checksum != 0:
        raise ValidationError('не пройдена проверка контрольного числа')


regex_snils_validator = SNILSValidator()


# для совместимости со старым валидатором-функцией
def snils_validator(value):
    """Проверка корректности СНИЛС с помощью регулярного выражения и контрольной суммы."""
    value = str(value)

    regex_snils_validator(value)


is_snils_valid = partial(validate_value, validator=snils_validator)


# =============================================================================
# ИНН
# =============================================================================


def _check_inn_checksum(coefficients, numbers, checksum):
    """Проверка контрольного числа ИНН с использованием весовых коэффициентов."""
    summa = sum(c * n for c, n in zip(coefficients, numbers))
    if summa % 11 % 10 != checksum:
        raise ValidationError('Не пройдена проверка контрольного числа')


def inn10_validator(value):
    """Валидатор для ИНН юридического лица (10 цифр).

    Проверяет корректность формата и контрольное число (последняя цифра).

    :raises django.core.exceptions.ValidationError: Если аргумент value
        содержит значение, несоответствующее формату ИНН, либо не пройдена
        проверка контрольного числа.
    """
    value = str(value)

    if len(value) != 10 or not value.isdigit():
        raise ValidationError('ИНН должен быть 10-ти значным числом')

    _check_inn_checksum((2, 4, 10, 3, 5, 9, 4, 6, 8), (int(ch) for ch in value[:-1]), int(value[-1]))


def inn12_validator(value):
    """Валидатор для ИНН физического лица (12 цифр).

    Проверяет корректность формата и контрольное число (последние 2 цифры).

    :raises django.core.exceptions.ValidationError: Если аргумент value
        содержит значение, несоответствующее формату ИНН, либо не пройдена
        проверка контрольного числа.
    """
    value = str(value)

    if len(value) != 12 or not value.isdigit():
        raise ValidationError('ИНН должен быть 12-ти значным числом')

    _check_inn_checksum((7, 2, 4, 10, 3, 5, 9, 4, 6, 8), (int(ch) for ch in value[:-2]), int(value[-2]))

    _check_inn_checksum((3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8), (int(ch) for ch in value[:-1]), int(value[-1]))


def inn_validator(value):
    """Валидатор для поля ИНН.

    Проверяет корректность формата и контрольное число (1 или 2 последние
    цифры).

    :raises django.core.exceptions.ValidationError: Если аргумент value
        содержит значение, несоответствующее формату ИНН, либо не пройдена
        проверка контрольного числа.
    """
    value = str(value)

    if len(value) not in (10, 12) or not value.isdigit():
        raise ValidationError('ИНН должен быть 10-ти или 12-ти значным числом')

    if len(value) == 10:
        inn10_validator(value)
    else:
        inn12_validator(value)


is_inn_valid = partial(validate_value, validator=inn_validator)
is_inn10_valid = partial(validate_value, validator=inn10_validator)
is_inn12_valid = partial(validate_value, validator=inn12_validator)


# =============================================================================
# КПП, ОКАТО, ОКТМО, ОКПО, ОГРН, ОКВЭД, ОКОПФ, ОКФС
# =============================================================================


def kpp_validator(value):
    """Валидатор для КПП (кода причины постановки на налоговый учет)."""
    value = str(value)

    if len(value) != 9 or not value.isdigit():
        raise ValidationError('КПП должен быть 9-ти значным числом')


is_kpp_valid = partial(validate_value, validator=kpp_validator)


def checksum_pr_50_1_024(value):
    """Расчет контрольного числа в соответствии с ПР 50.1.024-2005.

    Контрольное числорассчитывается следующим образом:
        1. Разрядам кода в общероссийском классификаторе, начиная со старшего
           разряда,присваивается набор весов, соответствующий натуральному
           ряду чисел от 1 до 10. Если разрядность кода больше 10, то набор
           весов повторяется.
        2. Каждая цифра кода умножается на вес разряда и вычисляется сумма
           полученных произведений.
        3. Контрольное число для кода представляет собой остаток от деления
           полученной суммы на модуль 11.
        4. Контрольное число должно иметь один разряд, значение которого
           находится в пределах от 0 до 9.

    Если получается остаток, равный 10, то для обеспечения одноразрядного
    контрольного числа необходимо провести повторный расчет, применяя вторую
    последовательность весов, сдвинутую на два разряда влево (3, 4, 5,...).

    Если в случае повторного расчета остаток от деления вновь сохраняется
    равным 10, то значение контрольного числа проставляется равным 0.
    """
    summa = sum(int(digit) * weight for digit, weight in zip(value, cycle(list(range(1, 11)))))

    remainder = summa % 11
    if remainder < 10:
        result = remainder
    else:
        summa = sum(int(digit) * weight for digit, weight in zip(value, cycle(list(range(3, 13)))))
        remainder = summa % 11
        if remainder < 10:
            result = remainder
        else:
            result = 0

    return result


def okato_validator(value):
    """Валидатор для ОКАТО.

    ОКАТО - общероссийский классификатор объектов административно-
    территориального деления.

    .. seealso::
       `Контрольное число ОКАТО <http://kontragent.info/articles/okato>`_
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКАТО должен состоять только из цифр')

    value_length = len(value)
    if value_length in (3, 6, 9, 12):
        # В последнем разряде указано контрольное число, проверим его
        if not checksum_pr_50_1_024(value[:-1]) != int(value[-1]):
            raise ValidationError('Не пройдена проверка контрольного числа')

    elif value_length not in (2, 5, 8, 11):
        raise ValidationError('Код ОКАТО должен состоять из 2, 5, 8 или 11 цифр')


is_okato_valid = partial(validate_value, validator=okato_validator)


def oktmo_validator(value):
    """Валидатор для ОКТМО.

    ОКТМО - Общероссийский классификатор территорий муниципальных образований.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКТМО должен состоять только из цифр')

    value_length = len(value)
    if value_length not in (2, 5, 8, 11):
        raise ValidationError('ОКТМО не может состоять из {} цифр'.format(value_length))


is_oktmo_valid = partial(validate_value, validator=oktmo_validator)


def okpo_validator(value):
    """Валидатор кода ОКПО.

    ОКПО - Общероссийский классификатор предприятий и организаций.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКПО должен состоять только из цифр')

    value_length = len(value)
    if value_length not in (8, 10):
        raise ValidationError('ОКПО должен состоять из 8-ми или 10-ти цифр')


is_okpo_valid = partial(validate_value, validator=okpo_validator)


def _check_ogrn_checksum(value):
    """Проверка контрольного числа ОГРН(ИП).

    Младший разряд остатка от деления предыдущего (n-1)-значного числа на (n-2)
    должен быть равен n-ому знаку ОГРН, где n – длина ОГРН. Если остаток от
    деления равен 10, то контрольное число равно 0 (нулю).
    """
    value_length = len(value)  # количество цифр в ОГРН
    divisor = value_length - 2  # делитель для вычисления контрольного числа
    number = int(value[: value_length - 1])  # ОГРН
    control_number = int(value[-1])  # контрольное число

    if number % divisor % 10 != control_number:
        raise ValidationError('Не пройдена проверка контрольного числа')


def _ogrn_validator(value, valid_length, title):
    """Общая логика для проверки ОГРН и ОГРНИП.

    Проверяет длину и контрольное число.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОГРН должен состоять только из цифр')
    if len(value) not in valid_length:
        raise ValidationError(
            '{} должен состоять из {} цифр!'.format(title, ' или '.join(str(length) for length in valid_length))
        )

    _check_ogrn_checksum(value)


def ogrn13_validator(value):
    """Валитор ОГРН.

    ОГРН - Основной государственный регистрационный номер.
    """
    _ogrn_validator(value, (13,), 'ОГРН')


def ogrn15_validator(value):
    """Валидатор ОГРНИП.

    ОГРНИП - Основной государственный регистрационный номер индивидуального
    предпринимателя.
    """
    _ogrn_validator(value, (15,), 'ОГРНИП')


def ogrn_validator(value):
    """Валидатор ОГРН(ИП).

    ОГРН(ИП) - Основной государственный регистрационный номер (индивидуального
    предпринимателя).
    """
    _ogrn_validator(value, (13, 15), 'ОГРН(ИП)')


is_ogrn_valid = partial(validate_value, validator=ogrn_validator)
is_ogrn13_valid = partial(validate_value, validator=ogrn13_validator)
is_ogrn15_valid = partial(validate_value, validator=ogrn15_validator)


okved_re = re.compile(r'^(\d{2}|\d{2}\.\d{1,2}|\d{2}\.\d{1,2}\.\d{1,2})$')


def okved_validator(value):
    """Валидатор кода ОКВЭД.

    ОКВЭД - Общероссийский классификатор видов экономической деятельности.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКВЭД должен состоять только из цифр')

    value_length = len(value)
    if value_length < 2 or 6 < value_length:
        raise ValidationError('Код ОКВЭД не может состоять из {} цифр'.format(value_length))


is_okved_valid = partial(validate_value, validator=okved_validator)


okopf_re = re.compile(r'^(\d \d\d \d\d)$')


def okopf_validator(value):
    """Валидатор кода ОКОПФ.

    ОКОПФ - Общероссийский классификатор организационно-правовых форм.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКОПФ должен состоять только из цифр')

    value_length = len(value)
    if value_length != 5:
        raise ValidationError('Код ОКОПФ должен состоять из 5-ти цифр')


is_okopf_valid = partial(validate_value, validator=okopf_validator)


def okfs_validator(value):
    """Валидатор кода ОКФС.

    ОКФС - Общероссийский классификатор форм собственности.
    """
    value = str(value)

    if not value.isdigit():
        raise ValidationError('ОКФС должен состоять только из цифр')

    value_length = len(value)
    if value_length != 2:
        raise ValidationError('Код ОКФС должен состоять из 2-ти цифр')


is_okfs_valid = partial(validate_value, validator=okfs_validator)


def validate_file_mime_type(file, allowed_mime_types):
    """Валидация mimetype файла.

    При помощи библиотеки python-magic получает mimetype файла и проверять, что
    данный тип в ходит в allowe_mime_types.

    :param file: Проверяемый файл
    :type file: file
    :param allowed_mime_types: Набор Mime types допустимых для загрузки
    :type: iterable
    """
    file.seek(0, 0)
    file_mime_type = magic.from_buffer(file.read(), mime=True)
    if file_mime_type not in allowed_mime_types:
        raise ValidationError('Mime type файла не соотвествует допустимым в системе')


@deconstructible
class FileMimeTypeValidator:
    """Валидатор для FileField модели проверяющий mimetype файла."""

    message = 'Mime type файла не допустим для загрузки в системе.'
    code = 'invalid_mimetype'

    def __init__(self, allowed_extensions, message=None, code=None):
        self.allowed_extensions = [allowed_extension.lower() for allowed_extension in allowed_extensions]

        self.allowed_mime_types = set(
            get_mime_type_for_extension(extension)
            for extension in self.allowed_extensions
            if get_mime_type_for_extension(extension)
        )

        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        try:
            validate_file_mime_type(value, self.allowed_mime_types)
        except ValidationError:
            raise ValidationError(
                self.message,
                code=self.code,
            )


# =============================================================================
# Общие валидаторы на основе классов
# =============================================================================
class OptionalFieldValidator(IModelValidator):
    """
    Валидатор поля, которое являетсяся обязательным при выполнении условий.

    Пример:

    .. code-block::

        class OptionalCommentValidator(OptionalFieldValidator):
            # Если статус равен OTHER, должен быть указан комментарий
            def  _need_check(self, instance):
                return instance.status == Status.OTHER

        class Model(BaseModel):
            status = # ...
            status_comment = models.TextField(null=True, blank=True, ...)
            validators = [OptionalCommentValidator('status_comment'),]
    """

    def __init__(self, field_name, **kwargs):
        """Инициализация валидатора.

        :param str field_name: имя валидируемого поля
        """
        assert isinstance(field_name, str), type(field_name)
        self.field_name = field_name
        self.empty_values = (None, '', [], (), {})

    def _need_check(self, instance):
        """Проверяет, выполнены ли условия для проверки поля ``field_name``.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :rtype: bool
        """
        raise NotImplementedError()

    def _get_message(self, instance):
        """Возвращает сообщение об ошибке.

        Может быть переопределено в реализациях валидатора для вывода
        более подробных сообщений.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :rtype: str
        """
        return 'Обязательное поле.'

    def clean(self, instance, errors):
        """Проверяет заполненность поля.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :param errors: ошибки, выявленные в ходе проверки.
        :type errors: collections.OrderedDict
        """
        if self._need_check(instance):
            if getattr(instance, self.field_name, None) in self.empty_values:
                errors[self.field_name].append(self._get_message(instance))


class RequiredBooleanValidator(OptionalFieldValidator):
    """Валидатор обязательного поля ``BooleanField``.

    Пример:

    .. code-block:: python

        class Model(BaseModel):
            accept_rules = models.BooleanField(...)
            validators = [
                RequiredBooleanValidator('accept_rules'),
            ]
    """

    def __init__(self, field_name, **kwargs):
        """Инициализация валидатора.

        :param str field_name: имя валидируемого поля
        """
        super().__init__(field_name, **kwargs)
        self.empty_values = (False,)

    def _need_check(self, instance):
        """
        Проверяет, выполнены ли условия для проверки поля ``field_name``.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :rtype bool
        """
        return True


class RequiredFieldValidator(OptionalFieldValidator):
    """Валидатор поля, не обязательного на уровне базы данных.

    Пример:

    .. code-block:: python

        class Model(BaseModel):
            # Поле не обязательно в основной системе, но в рамках плагина
            # должно быть обязательным
            employee = models.ForeignKey(
                'employee.Employee',
                null=True,
                blank=True,
            )
            validators = [
                RequiredFieldValidator('employee'),
            ]
    """

    def _need_check(self, instance):
        """
        Проверяет, выполнены ли условия для проверки поля ``field_name``.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :rtype bool
        """
        return True


class UnchangeableFieldValidator(IModelValidator):
    """Валидатор неизменяемого поля.

    При редактировании объекта, если изменяется поле ``field_name``,
    возвращает ошибку.

    Пример:

    .. code-block:: python

        class Model(BaseModel):
            type = models.BooleanField(...)
            validators = [
                UnchangeableFieldValidator('type'),
            ]

    """

    def __init__(self, field_name, **kwargs):
        """Инициализация валидатора.

        :param str field_name: имя валидируемого поля
        """
        assert isinstance(field_name, str), type(field_name)
        self.field_name = field_name

    def _get_message(self, instance):
        """Возвращает сообщение об ошибке.

        Может быть переопределено в реализациях валидатора для вывода
        более подробных сообщений.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :rtype: str
        """
        verbose_name = instance._meta.get_field(self.field_name).verbose_name

        return 'Поле "{}" не доступно для редактирования.'.format(verbose_name)

    def clean(self, instance, errors):
        """Проверка редактирования поля ``field_name``.

        :param instance: экземпляр проверяемой модели.
        :type instance: .mixins.validation.ModelValidationMixin

        :param errors: ошибки, выявленные в ходе проверки.
        :type errors: collections.OrderedDict
        """
        original = get_original_object(instance)
        if not original:
            return

        old_value = getattr(original, self.field_name, None)
        new_value = getattr(instance, self.field_name, None)
        if old_value != new_value:
            errors[self.field_name].append(self._get_message(instance))


class DuplicationValidator(IModelValidator):
    """Валидатор уникальности объекта.

    Используется для объектов, уникальность которых нельзя проверить
    через ``Meta.unique_together``.

    Пример:

    .. code-block:: python

        class MyModelDuplicationValidator(DuplicationValidator):
            # Проверяет по полям type и status (если оно задано)

            def _get_field_names(self, instance):
                result = ['Тип',]
                if instance.status:
                    result.append('Статус')
                return result

            def _get_duplication_params(self, instance):
                query = Q(type=instance.type)
                if instance.status:
                    query &= Q(status=instance.status)
                return query

        class Model(BaseModel):
            type = # ...
            status = # ...
            validators = [MyModelDuplicationValidator(),]
    """

    def _get_duplication_params(self, instance):
        """Возвращает параметры для проверки уникальности.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :rtype django.db.models.Q
        """
        raise NotImplementedError()

    def _get_field_names(self, instance):
        """Возвращает список названий полей, по которым происходит проверка.

        Получает валидируемый объект, т.к. проверяемый список полей может
        зависеть от значений полей объекта.

        :param instance: экземпляр проверяемой модели.

        :return список строк-названий полей
        :rtype list
        """
        raise NotImplementedError()

    def _get_message(self, instance):
        """Возвращает сообщение об ошибке.

        Может быть переопределено в реализациях валидатора для вывода
        более подробных сообщений.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :rtype: str
        """
        return ('В системе уже существует {} с такими же значениями полей {}.').format(
            instance._meta.verbose_name, ', '.join(self._get_field_names(instance))
        )

    def _get_base_query(self, instance):
        """
        Возвращает базовый кварисет, по которому проверяется уникальность.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :rtype: django.db.models.QuerySet
        """
        return instance._meta.model.objects

    def clean(self, instance, errors):
        """Проверка уникальности объекта.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :param errors: ошибки, выявленные в ходе проверки.
        :type errors: collections.OrderedDict
        """
        original = get_original_object(instance)
        query = self._get_base_query(instance).filter(self._get_duplication_params(instance))

        if original:
            query = query.exclude(id=instance.id)

        if query.exists():
            errors[NON_FIELD_ERRORS].append(self._get_message(instance))


class SingleErrorDecimalValidator(DecimalValidator):
    """Кастомный класс валидации Decimal поля модели."""

    def __init__(self, max_digits, decimal_places):
        super().__init__(max_digits, decimal_places)
        self.max_whole_digits = max_digits - decimal_places

    def __call__(self, value):
        """
        Переопределенный стандартный метод валилидации Decimal поля.

        При привышенеии целой и дробной части выводит сообщение такое же как и
        при привышении только целой части. Код ошибки остался max_digits.
        """
        digit_tuple, exponent = value.as_tuple()[1:]
        decimals = abs(exponent)
        digits = len(digit_tuple)
        if decimals > digits:
            digits = decimals
        whole_digits = digits - decimals

        if self.max_digits is not None and digits > self.max_digits:
            raise ValidationError(
                self.messages['max_whole_digits'],
                code='max_digits',
                params={'max': self.max_whole_digits},
            )
        if self.decimal_places is not None and decimals > self.decimal_places:
            raise ValidationError(
                self.messages['max_decimal_places'],
                code='max_decimal_places',
                params={'max': self.decimal_places},
            )
        if (
            self.max_digits is not None
            and self.decimal_places is not None
            and whole_digits > (self.max_digits - self.decimal_places)
        ):
            raise ValidationError(
                self.messages['max_whole_digits'],
                code='max_whole_digits',
                params={'max': self.max_whole_digits},
            )


# =============================================================================
# Валидаторы персональных данных
# =============================================================================


class FIOValidator(RegexValidator):
    regex = r'(^$)|(^[a-zA-Zа-яА-ЯёЁ]([\s-]?[a-zA-Zа-яА-ЯёЁ])*$)'


def date_range_validator(
    minimum=None, maximum=None, range_message=None, min_message=None, max_message=None, date_format='%d.%m.%Y'
):
    """Валидатор даты. Возвращает функцию, в которую должен быть помещен один
    аргумент: проверяемое значение
    :param minimum: значение, меньше которого value быть не должно;
        должно быть либо точной датой, либо функцией, принимающей 0 аргументов
        и возвращающей точную дату
    :type minimum: date or callable
    :param maximum: значение, больше которого value быть не должно;
        требования к типу аналогичны
    :type minimum: date or callable
    :param range_message: сообщение для случая, когда value не соответствует
        диапазону. Может содержать плейсхолдеры для приведенных к
        `date_format` дат, такие как:
        * %(val)s - для проверяемого значения;
        * %(min)s - для минимально возможного значения;
        * %(max)s - для максимально возможного значения.
    :type range_message: str
    :param min_message: аналогичное сообщение для случая, когда value
        меньше `minimum`.
    :type range_message: str
    :param max_message: аналогичное сообщение для случая, когда value
        больше maximum
    :type range_message: str
    :param date_format: формат дат (
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes);
        по умолчанию ДД.ММ.ГГГГ
    :type range_message: str
    :return: функция, в которую передается проверяемое значение и которая ведет
    себя как обычный валидатор поля Django
    """
    assert minimum is not None or maximum is not None, 'Необходимо определелить границы для валидатора дат'

    range_message = range_message or ('Значение %(val)s не входит в диапазон %(min)s-%(max)s')
    min_message = min_message or 'Значение %(val)s меньше, чем %(min)s'
    max_message = max_message or 'Значение %(val)s больше %(max)s'

    if minimum is not None and maximum is not None:
        message = range_message
    elif minimum is not None:
        message = min_message
    else:
        message = max_message

    min_date = minimum or datetime.min.date()
    max_date = maximum or datetime.max.date()
    date_format = date_format

    return partial(
        _date_range_validator, min_date=min_date, max_date=max_date, message=message, date_format=date_format
    )


def _date_range_validator(value, min_date, max_date, message, date_format):
    """Функция, предназначенная для вызова валидатора непосредственно
    на значении.
    Все аргументы кроме `value` должны быть заполнены для совершения валидации,
    поэтому в сигнатуре эти аргументы отделены * - аргументы после *
    обязательны, но задаваться должны по имени
    :param value: проверяемое значение
    :param min_date: см. `date_range_validator`
    :param max_date: см. `date_range_validator`
    :param message: см. `date_range_validator`
    :param date_format: см. `date_range_validator`
    :return:
    :raises ValidationError
    """
    # должны быть все аргументы
    assert all(
        [
            min_date is not None,
            max_date is not None,
            message is not None,
            date_format is not None,
        ]
    ), 'Все аргументы должны быть указаны (см. сигнатуру функции)'

    if isinstance(value, datetime):
        value = value.date()

    _min = min_date() if callable(min_date) else min_date
    _max = max_date() if callable(max_date) else max_date

    message_values = {
        'val': value.strftime(date_format),
        'min': _min.strftime(date_format),
        'max': _max.strftime(date_format),
    }

    if not _min <= value <= _max:
        raise ValidationError(message % message_values)


class HouseValidator(RegexValidator):
    """Валидатор номера дома.

    В ФИАС есть примеры, которые не подойдут под текущую регулярку, например:
    * АэропортШереметьево1
    * Ряд5Блок1Позиция1
    * IV-537
    * IX-7/34

    Эти дома относятся к "специальным" зданиям, хоз. помещениям на закрытых
    территориях (заводы, склады), гаражам и т.д.
    Если нужно будет, что бы они так же считались валидными,
    то регулярку нужно будет расширить до
    '^(?=.{,20}$)([0-9IVXА-ЯЁа-яё"/_,.-]{1,} ?){1,}\b$'
    """

    regex = re.compile(r'^(?=.{,12}$)([0-9а-яё"/_,.-]{1,} ?){1,}\b$', re.IGNORECASE | re.UNICODE)
    message = 'Неверно указан номер дома'


regex_house_validator = HouseValidator()


def house_validator(value):
    """Функция для валидации номера дома."""
    value = str(value)

    regex_house_validator(value)


is_house_number_valid = partial(validate_value, validator=house_validator)


class BuildingValidator(RegexValidator):
    """Валидатор номера корпуса дома."""

    regex = re.compile(r'^[0-9а-яё/_.-]{0,10}$', re.IGNORECASE | re.UNICODE)
    message = 'Неверно указан корпус дома'


class DocumentTypeValidator(RegexValidator):
    """Валидатор для строки тип документа.

    Строка может содержать: кириллицу (нижнего и верхнего регистра),
    символ (пробел), при условии, что он: не первый, не последний,
    не повторяется больше одного раза подряд, не идет до ",",
    знак "," (запятая), при условии, что он: не первый, не последний,
    не повторяется больше одного раза подряд, не идет после символа "пробел".
    Строка не может содержать: цифры и прочие символы.
    """

    regex = r'^[а-яА-ЯёЁ]+([а-яА-ЯёЁ]*[\,]?[\s]{1}[а-яА-ЯёЁ]+)*$'


regex_doc_type_validator = DocumentTypeValidator()


def doc_type_validator(value):
    """Функция для валидации строки с типом документа."""
    value = str(value)

    regex_doc_type_validator(value)


is_doc_type_valid = partial(validate_value, validator=doc_type_validator)


class PassportSeriesValidator(RegexValidator):
    regex = r'^\d{4}$'
    message = 'Неверно задана серия паспорта'


class PassportNumberValidator(RegexValidator):
    regex = r'^\d{6}$'
    message = 'Неверно задан номер паспорта'


class DocumentSeriesValidator(RegexValidator):
    regex = r'(^$)|(^[a-zA-Zа-яА-ЯёЁ\d]([\s|\-|\.|\,|\\|\/]?[a-zA-Zа-яА-ЯёЁ\d])*$)'
    message = 'Неверно задана серия документа'


class DocumentNumberValidator(RegexValidator):
    regex = r'(^$)|(^[a-zA-Zа-яА-ЯёЁ\d]([\s|\-|\.|\,|\\|\/]?[a-zA-Zа-яА-ЯёЁ\d])*$)'
    message = 'Неверно задан номер документа'
