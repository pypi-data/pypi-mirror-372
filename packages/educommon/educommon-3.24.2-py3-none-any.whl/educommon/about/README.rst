Приложение "Информация о системе"
=================================

Введение
-----------

Было принято решение разместить общий код пака приложения в пакете educommon.
Данная реализация определяет три вкладки: "О системе", "Версии ПО",
"Расширения БД". В использующем проекте состав окна может быть расширен,
возможна интеграция с системой контроля доступа, принятой в проекте.

Использование
--------------

1. Подключить приложение ``educommon.about`` в ``INSTALLED_APPS``. Это
необходимо, т.к. приложение использует статические файлы.

2. Кастомизировать пак окна "О системе". Переопределяемые сущности
пака ``AboutPack``:

- ``get_version_config_path`` - определяет путь до конфигурации сборки
- ``get_tab_permissions`` - конфигурация состава вкладок, точка интеграции с
  подсистемой контроля прав доступа использующего проекта
- ``project_title`` - название проекта, отображаемое в окне

.. code-block:: python

  from educommon.about.ui.actions import AboutPack

  class Pack(AboutPack):

    """Приложение "Информация о системе"."""

    project_title = 'Система "Моя система"'

    def get_version_config_path(self):
        """Получает путь для конфигурации версии сборки."""
        return apps.get_app_config('myApp').path

    def get_tab_permissions(self, request, context):
        """Возвращает права для вкладок окна системной информации."""
        return dict(
            can_view_common_tab=rbac.has_access(self.about_action, request),
            can_view_packages_tab=rbac.has_access(
                self.packages_pack.rows_action, request
            ),
            can_view_postgresql_ext_tab=rbac.has_access(
                self.postgresql_extensions_pack.rows_action, request
            ),
        )

3. Зарегистрировать переопределенные паки в app_meta.

.. code-block:: python

  def register_actions():
      """Регистрация экшенов."""
      main_controller.extend_packs((
          Pack(),
      ))

