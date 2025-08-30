import os

from django import (
    http,
)
from django.conf import (
    settings,
)
from django.urls import (
    re_path,
)
from sendfile import (
    sendfile,
)

from m3 import (
    M3JSONEncoder,
)
from m3_django_compat import (
    is_authenticated,
)


def check_autorization(request, path):
    # Если файл в media/public, то отдаем сразу без проверки
    # Вообще это делается соответствующим конфигурированием NGINX
    path_list = path.split(os.path.sep)
    if path_list and path_list[0] == 'public':
        return sendfile(request, os.path.join(settings.MEDIA_ROOT, path))

    if not is_authenticated(request.user):
        result = M3JSONEncoder().encode(
            {
                'success': False,
                'message': 'Вы не авторизованы. Возможно, закончилось время '
                'пользовательской сессии. Для повторной '
                'аутентификации обновите страницу.',
            }
        )
        return http.HttpResponse(result, content_type='application/json')

    return sendfile(request, os.path.join(settings.MEDIA_ROOT, path))


urlpatterns = [re_path(r'^media/(?P<path>.*)$', check_autorization)]
