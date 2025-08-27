def get_request_params(request):
    """Возвращает параметры HTTP-запроса.

    Аналогична атрибуту ``HttpRequest.REQUEST``, который в Django 1.7 был
    помечен, как устаревший, а в Django 1.9 был удален.
    """
    if request.method == 'GET':
        result = request.GET
    elif request.method == 'POST':
        result = request.POST
    else:
        result = {}

    return result
