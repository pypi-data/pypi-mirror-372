"""Management-команда для удаления обьектов."""

import sys
from collections import (
    defaultdict,
)

from django.apps import (
    apps,
)
from django.core import (
    serializers,
)
from django.core.management import (
    BaseCommand,
    CommandError,
    get_commands,
    handle_default_options,
    load_command_class,
)
from django.core.management.base import (
    SystemCheckError,
)
from django.db import (
    connections,
)
from django.utils.encoding import (
    force_str,
)


def call_custom_command(command_name, *args, **options):
    """Осуществляет вызов команды с регистрацией неизвестных аргументов."""
    if isinstance(command_name, BaseCommand):
        # Command object passed in.
        command = command_name
        command_name = command.__class__.__module__.split('.')[-1]
    else:
        # Load the command object by name.
        try:
            app_name = get_commands()[command_name]
        except KeyError:
            raise CommandError(f'Unknown command: {command_name!r}')

        if isinstance(app_name, BaseCommand):
            # If the command is already loaded, use it directly.
            command = app_name
        else:
            command = load_command_class(app_name, command_name)

    # Simulate argument parsing to get the option defaults (
    # see #10080 for details).
    parser = command.create_parser('', command_name)
    # Use the `dest` option name from the parser option
    opt_mapping = {
        sorted(s_opt.option_strings)[0].lstrip('-').replace('-', '_'): s_opt.dest
        for s_opt in parser._actions
        if s_opt.option_strings
    }
    arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
    options, un_options = parser.parse_known_args(args)
    for opt in un_options:
        if not isinstance(opt, str):
            opt = str(opt)
        com = opt.split('=')
        com = com[0]
        if '__in' in com:
            parser.add_argument(com, action='append')
        elif '__isnull' in com:
            parser.add_argument(com, action='store')
        else:
            parser.add_argument(com)
    defaults = parser.parse_args(args=[force_str(a) for a in args])
    defaults = dict(defaults._get_kwargs(), **arg_options)
    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop('args', ())
    if 'skip_checks' not in options:
        defaults['skip_checks'] = True

    return command.execute(*args, **defaults)


class Command(BaseCommand):
    """Удаление групп и учащихся за заданный период в заданном ОУ."""

    def run_from_argv(self, argv):
        # переопределен в связи с регистрацией аргументов
        # при вызове самой команды
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])

        options, un_options = parser.parse_known_args(argv[2:])
        for opt in un_options:
            if not isinstance(opt, str):
                opt = str(opt)
            com = opt.split('=')
            com = com[0]
            if '__in' in com:
                parser.add_argument(com, action='append')
            elif '__isnull' in com:
                parser.add_argument(com, action='store')
            else:
                parser.add_argument(com)

        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)
        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        handle_default_options(options)
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise
            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write(f'{e.__class__.__name__}: {e}')
            sys.exit(1)
        finally:
            connections.close_all()

    def add_arguments(self, parser):
        parser.add_argument('--count', action='count', help='Количество удаляемых обьектов')
        parser.add_argument('--model', type=str, required=True, help='Модель для удаления')
        parser.add_argument('--data', action='count', help='Вернуть json удаляемых обьектов')

    @staticmethod
    def find_filter(options, ignore_opt=()):
        """Возвращает lookup для поиска по модели.

        :param options: Опции, переданные в команду.
        :type request: dict
        :param ignore_opt: Кортеж игнорируемых значений при построении фильтра.
        :type ignore_opt: tuple
        :rtype : dict
        """
        lookup = dict()
        for key, value in options.items():
            if key and key not in ignore_opt and value:
                if '__in' in key:
                    lookup[key] = value[0].split(',')
                elif '__isnull' in key:
                    if value == 'False':
                        lookup[key] = False
                    else:
                        lookup[key] = True
                else:
                    lookup[key] = value
        return lookup

    @staticmethod
    def find_model(model_name, app_name=None):
        """Возвращает модель, либо список моделей для приложения.

        А также вернет сообщение об ошибке, если такая возникла.

        :param model_name: Название искомой модели.
        :type request: str
        :param app_name: Название приложения.
        :type ignore_opt: str

        :rtype model: list or django.db.models.base.Model
        :rtype message: str or None
        """
        models = []
        message = None
        model = None
        if app_name:
            try:
                model = apps.get_model(app_name, model_name)
            except LookupError:
                message = 'Модели {} в приложении {} не найдено.'.format(model_name, app_name)
            return model, message
        for app_config in apps.get_app_configs():
            try:
                model = app_config.get_model(model_name)
                models.append(model)
            except LookupError:
                pass

        if len(models) > 1:
            model = None
            message = 'Невозможно однозначно определить модель, найдены похожие модели: \n'
            message += '\n'.join(str(model._meta) for model in models)
        elif not model:
            message = 'Модели {} не найдено.'.format(model_name)
        return model, message

    def process_count(self, deleted_objects):
        """Выводит в stdout количество зависимых обьектов."""
        uniq_dict = defaultdict(set)
        for del_obj in deleted_objects:
            for model, model_objects in del_obj.get_related_objects():
                for o in model_objects:
                    uniq_dict[model.__name__ + ' ' + model._meta.verbose_name].add(o)
        for model, objs in uniq_dict.items():
            display_mes = '{} {}'.format(model, len(objs))
            self.stdout.write(display_mes)

    def process_data(self, deleted_objects):
        """Выводит в stdout json зависимых обьектов."""
        objs = []
        for instance in deleted_objects:
            for rel_model, rel_objs in instance.get_related_objects():
                for obj in rel_objs:
                    objs.append(obj)
        data = serializers.serialize('json', objs)
        self.stdout.write(data)

    def handle(self, *args, **options):
        if '.' in options['model']:
            app_label, model_name = options['model'].split('.')
            model, message = self.find_model(model_name, app_label)
        else:
            model, message = self.find_model(options['model'])

        if message:
            raise CommandError(message)
        # опции которые будут игнорироваться в фильтре
        ignore_opt = ('count', 'model', 'data', 'verbosity', 'stdout', 'skip_checks')
        lookup = self.find_filter(options, ignore_opt)
        deleted_objects = model.objects.filter(**lookup)

        if options['count']:
            self.process_count(deleted_objects)

        if options['data']:
            self.process_data(deleted_objects)

        if not options['data'] and not options['count']:
            deleted_objects.delete()
