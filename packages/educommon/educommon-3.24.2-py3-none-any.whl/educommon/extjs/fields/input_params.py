"""Параметры фильтрации ввода для различного типа полей (ИНН, СНИЛС и тд.).

Примеры использования:

    from educommon.extjs.fields.input_params import snils_field_params

    snils_field = ExtStringField(name='person.snils',
                                 label='Номер СНИЛС',
                                 **snils_field_params)
"""

# параметры для поля ввода СНИЛС
snils_field_params = dict(input_mask='###-###-### ##', regex=r'^\d{3}-\d{3}-\d{3} \d{2}$')

# параметры для поля ввода ИНН юр.лица или физ.лица
inn_field_params = dict(input_mask='############', regex=r'^\d{10}(\d{2})?$')

# параметры для поля ввода ИНН юр. лица
inn10_field_params = dict(input_mask='##########', regex=r'^\d{10}$')

# параметры для поля ввода ИНН физ.лица или ИП
inn12_field_params = dict(input_mask='############', regex=r'^\d{12}$')

children_document_series_field_params = dict(input_mask='****-ZZ', regex='^[A-Za-z0-9]{1,4}-[А-ЯA-Z]{2}$')

children_document_number_field_params = dict(input_mask='#' * 6, regex='^\d{6}$')

delegate_document_series_field_params = dict(input_mask='#' * 4, regex='^\d{4}$')

delegate_document_number_field_params = dict(input_mask='#' * 6, regex='^\d{6}$')

url_field_params = dict(
    regex='^((http|https)\:\/\/)([^\s]*)$',
    invalid_text='Адрес сайта должен начинаться с http:// или https:// и не должен содержать пробелов',
)

# Параметры поля для ввода имён.
name_field_params = dict(
    mask_re="[- \\'а-яёА-ЯЁ]",
)

# Параметры поля для ввода имён,допускает наличи латиницы.
eng_name_field_params = dict(
    mask_re="[- \\'а-яёА-ЯЁa-zA-Z]",
)

# Параметры поля для ввода имён, допускает наличие цифр.
name_digits_field_params = dict(
    mask_re="[- \\'а-яёА-ЯЁ0-9]",
)

# Параметры поля для ввода КПП.
kpp_field_params = dict(
    input_mask='#########',
    regex=r'^\d{9}$',
)

# Параметры поля для ввода ОКАТО.
okato_field_params = dict(
    input_mask='############',
    regex=r'^(\d{2,3}|\d{5,6}|\d{8,9}|\d{11,12})$',
)

# Параметры поля для ввода ОКТМО.
oktmo_field_params = dict(
    input_mask='###########',
    regex=r'^(\d{2}|\d{5}|\d{8}|\d{11})$',
)

# Параметры поля для ввода ОКПО
okpo_field_params = dict(
    input_mask='##########',
    regex=r'^(\d{8}|\d{10})$',
)

# Параметры поля для ввода ОГРН.
ogrn_field_params = dict(
    input_mask='###############',
    regex=r'^(\d{13}|\d{15})$',
)

# Параметры поля для ввода ОКВЭД.
okved_field_params = dict(
    input_mask='##.##.##',
    regex=r'^(\d{2}|\d{2}\.\d{1,2}|\d{2}\.\d{1,2}\.\d{1,2})$',
    max_length=8,
)

# Параметры поля для ввода ОКОПФ.
okopf_field_params = dict(
    input_mask='# ## ##',
    regex=r'^(\d \d\d \d\d)$',
    max_length=7,
)

# Параметры поля для ввода ОКФС.
okfs_field_params = dict(
    input_mask='##',
    regex=r'^(\d{2})$',
)

# Параметры поля ввода Телефон.
phone_field_params = dict(mask_re=r'^[0-9,()-]+$')

# Параметры поля ввода эл. почты.
email_field_params = dict(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

# Параметры поля ввода БИК.
bik_field_params = dict(
    input_mask='#' * 9,
    mask_re=r'\d',
    regex=r'^\d{9}$',
)

# Параметры поля ввода номера счета
common_account_field_params = dict(
    input_mask='#' * 20,
    mask_re=r'\d',
    regex=r'^\d{20}$',
)
