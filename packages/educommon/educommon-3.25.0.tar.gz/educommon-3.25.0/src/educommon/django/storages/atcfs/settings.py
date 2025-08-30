from django.conf import (
    settings,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)


try:
    URL = settings.ATCFS_CONF['URL'].rstrip('/')
    VIS_ID = settings.ATCFS_CONF['VIS_ID']
    VIS_USER = settings.ATCFS_CONF['VIS_USER']
    SECRET_KEY = settings.ATCFS_CONF['SECRET_KEY']
except (AttributeError, KeyError):
    msg = 'settings.ATCFS_CONF is improperly configured.'
    raise ImproperlyConfigured(msg)

# Constants
FILES_PATH = 'files'
FILE_INFO_PATH = 'fileinfo'
TMP_FILE_LINK_PATH = 'tmpFileLink'
TMP_FILES_PATH = 'tmpFiles'

# Секунд, ожидания соединения с сервером.
# Необязательный параметр.
try:
    CONNECT_TIMEOUT = settings.ATCFS_CONF['CONNECT_TIMEOUT']
except (AttributeError, KeyError):
    CONNECT_TIMEOUT = 3
