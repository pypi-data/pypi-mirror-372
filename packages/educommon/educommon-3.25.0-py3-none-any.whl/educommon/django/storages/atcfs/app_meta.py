from django.urls import (
    re_path,
)
from django.views.generic import (
    TemplateView,
)


def register_urlpatterns():
    urlpatterns = [
        re_path(
            r'^atcfs_unavailable/$',
            TemplateView.as_view(template_name='atcfs_unavailable.html'),
            name='atcfs_unavailable',
        ),
    ]

    return urlpatterns
