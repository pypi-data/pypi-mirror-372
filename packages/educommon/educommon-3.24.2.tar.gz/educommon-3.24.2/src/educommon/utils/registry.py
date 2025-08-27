class ModelHandlerRegistry:
    """Класс для хранения обработчиков модели."""

    def __init__(self, handlers):
        """
        :param handlers: Словарь с обработчиками модели, т.е.
            словарь, где ключ - django модель, значение -
            функция-обработчик (вызываемый объект) для данной модели
        """
        assert isinstance(handlers, dict)
        assert all(map(callable, handlers.values()))

        super().__init__()

        self._handlers = handlers

    def get_model_handler(self, model):
        """Возвращение обработчика для модели.

        :param model: Модель, для которой добавляется обработчик

        :return: Обработчик указанной модели или None, если его нет
        :rtype: Optional[Callable]
        """
        return self._handlers.get(model)

    def add_handler(self, model, handler):
        """Добавление обработчика для модели.

        Если у указанной модели был обработчик, он перезаписывается новым.

        :param model: Модель, для которой добавляется обработчик
        :param handler: Обработчик модели
        """
        assert callable(handler)

        self._handlers[model] = handler

    def is_model_has_handler(self, model):
        """Возвращает признак, имеется ли обработчик у указанной модели.

        :param model: Модель, которую надо проверить

        :return: Признак, имеется ли обработчик у указанной модели
        :rtype: bool
        """
        return model in self._handlers
