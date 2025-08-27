import json

from django import (
    template,
)
from django.utils.safestring import (
    mark_safe,
)


register = template.Library()


@register.filter
def jsonify(obj):
    """Преобразование объкта в JSON."""
    return mark_safe(json.dumps(obj))
