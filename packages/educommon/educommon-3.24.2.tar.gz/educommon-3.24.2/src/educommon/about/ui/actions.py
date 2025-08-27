from abc import (
    ABCMeta,
    abstractmethod,
)
from platform import (
    python_version,
)

from django.db import (
    connection,
    connections,
)
from m3_builder.build import (
    get_build_info,
)

from objectpack.actions import (
    BasePack,
    BaseWindowAction,
    ObjectPack,
)
from objectpack.models import (
    VirtualModel,
)

from educommon.about.ui.ui import (
    AboutWindow,
)
from educommon.about.utils import (
    get_installed_distributions,
)
from educommon.utils.system import (
    get_os_version,
    get_postgresql_version,
)


# -----------------------------------------------------------------------------


class Package(VirtualModel):
    """Виртуальная модель 'Пакеты, установленные в системе'."""

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.version = data['version']

    @classmethod
    def _get_ids(cls):
        packages = sorted(tuple(get_installed_distributions()), key=lambda p: p.project_name)

        for row_id, package in enumerate(packages, 1):
            yield dict(id=row_id, name=package.project_name, version=package.version)


class PackagesPack(ObjectPack):
    """Пак грида установленных в системе пакетов."""

    model = Package
    allow_paging = False

    columns = (
        dict(
            data_index='id',
            header='№',
            width=50,
            fixed=True,
        ),
        dict(
            data_index='name',
            header='Пакет',
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='version',
            header='Версия',
        ),
    )


# -----------------------------------------------------------------------------


class PostgreSQLExtension(VirtualModel):
    """Виртуальная модель 'Расширение PostgreSQL'."""

    def __init__(self, data):
        self.id = data['id']
        self.database_alias = data['database_alias']
        self.extension_name = data['extension_name']
        self.extension_version = data['extension_version']

    @classmethod
    def _get_ids(cls):
        row_id = 0

        for dbc in connections.all():
            cursor = dbc.cursor()
            cursor.execute('select extname, extversion from pg_extension')
            for extension_name, extension_version in cursor:
                row_id += 1
                yield dict(
                    id=row_id,
                    database_alias=dbc.alias,
                    extension_name=extension_name,
                    extension_version=extension_version,
                )


class PostgreSQLExtensionsPack(ObjectPack):
    """Пак грида расширений БД."""

    model = PostgreSQLExtension
    allow_paging = False

    columns = (
        dict(
            data_index='database_alias',
            header='Алиас БД',
            width=2,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='extension_name',
            header='Расширение',
            width=4,
            column_renderer='monospaceRenderer',
        ),
        dict(
            data_index='extension_version',
            header='Версия',
            width=1,
        ),
    )


# -----------------------------------------------------------------------------


class AboutPack(BasePack, metaclass=ABCMeta):
    """Пак окна 'Информация о системе'."""

    title = 'О системе'

    @property
    @abstractmethod
    def project_title(self):
        """Наименование проекта."""
        pass

    about_window = AboutWindow

    def __init__(self):
        super(AboutPack, self).__init__()
        self.about_action = AboutWindowAction()
        self.actions.append(self.about_action)

        self.packages_pack = PackagesPack()
        self.postgresql_extensions_pack = PostgreSQLExtensionsPack()
        self.subpacks.extend(
            (
                self.packages_pack,
                self.postgresql_extensions_pack,
            )
        )

    @abstractmethod
    def get_version_config_path(self):
        """Получает путь, по которому лежит конфигурация версии сборки."""
        pass

    def get_tab_permissions(self, request, context):
        """Возвращает права для вкладок окна системной информации.

        Права определяются для каждой вкладки раздельно. В использующем
        проекте данный метод может перекрываться с целями:
        - настройки состава вкладок;
        - интеграции с системой прав доступа проекта.
        """
        return dict(can_view_common_tab=True, can_view_packages_tab=True, can_view_postgresql_ext_tab=True)


class AboutWindowAction(BaseWindowAction):
    """Экшен окна 'Информация о системе'."""

    def create_window(self):
        self.win = self.parent.about_window()

    def set_window_params(self):
        self.win_params['data'] = dict(
            version=get_build_info(self.parent.get_version_config_path()), project_title=self.parent.project_title
        )
        self.win_params['version_info'] = (
            (1, 'OC', get_os_version()),
            (2, 'Python', python_version()),
            (3, 'PostgreSQL', '.'.join(map(str, get_postgresql_version(connection)))),
        )
        tab_permissions = self.parent.get_tab_permissions(self.request, self.context)

        self.win_params.update(tab_permissions)
