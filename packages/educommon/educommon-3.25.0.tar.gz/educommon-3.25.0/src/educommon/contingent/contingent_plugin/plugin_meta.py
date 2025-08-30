def connect_plugin(settings, plugin_settings):
    settings['INSTALLED_APPS'].append(__package__ + '.apps.ContingentPluginAppConfig')
