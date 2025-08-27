class DefaultPasswordValidator:
    """Валидация пароля."""

    _validators = []

    def validate(self, password):
        return [validator(password) for validator in self._validators]
