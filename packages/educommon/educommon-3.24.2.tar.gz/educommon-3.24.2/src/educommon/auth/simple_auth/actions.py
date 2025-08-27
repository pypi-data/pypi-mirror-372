import datetime
from urllib.parse import (
    urljoin,
)
from uuid import (
    uuid4,
)

from django import (
    http,
)
from django.conf import (
    settings,
)
from django.contrib import (
    auth,
)
from django.core.exceptions import (
    ValidationError,
)
from django.core.mail.message import (
    EmailMessage,
)
from django.http import (
    HttpResponseRedirect,
)
from django.shortcuts import (
    render,
)
from django.template.loader import (
    render_to_string,
)
from m3.actions.exceptions import (
    ApplicationLogicException,
)
from m3.actions.results import (
    OperationResult,
    PreJsonResult,
)
from m3_ext.ui.shortcuts import (
    MessageBox,
)

from educommon import (
    ioc,
)
from educommon.auth.simple_auth import (
    checkers,
    const,
    validators,
)
from educommon.auth.simple_auth.models import (
    ResetPasswords,
)
from educommon.m3 import (
    convert_validation_error_to,
)
from m3_django_compat import (
    get_user_model,
)
from objectpack.actions import (
    BaseAction,
    BasePack,
)


class AuthPack(BasePack):
    """Пак аутентификации."""

    url = const.AUTH_PACK_URL

    login_checker = checkers.DefaultLoginChecker()

    def __init__(self):
        super().__init__()

        self.login_page_action = LoginPageAction()
        self.login_action = LoginAction()

        self.logout_confirm_action = LogoutConfirmAction()
        self.logout_action = LogoutAction()

        self.reset_password_page_action = ResetPasswordPageAction()
        self.reset_password_action = ResetPasswordAction()

        self.change_password_page_action = ChangeResetPasswordPageAction()
        self.change_password_action = ChangeResetPasswordAction()

        self.actions.extend(
            (
                self.login_page_action,
                self.logout_confirm_action,
                self.login_action,
                self.logout_action,
                self.reset_password_page_action,
                self.reset_password_action,
                self.change_password_page_action,
                self.change_password_action,
            )
        )

    def declare_context(self, action):
        """Определяет контекст для экшена входа."""
        ctx = super().declare_context(action)

        if action is self.login_action:
            ctx['login'] = dict(type='str', default='')
            ctx['password'] = dict(type='str', default='')

        return ctx

    def get_login_url(self):
        """Возвращает URL экшена входа."""
        return self.login_action.get_absolute_url()

    def get_logout_url(self):
        """Возвращает URL экшена выхода."""
        return self.logout_action.get_absolute_url()

    def get_login_page_url(self):
        """Возвращает URL страницы входа."""
        return self.login_page_action.get_absolute_url()

    def get_reset_password_page_url(self):
        """Возвращает URL страницы восстановления пароля."""
        return self.reset_password_page_action.get_absolute_url()

    def get_reset_password_url(self):
        """Возвращает URL экшена восстановления пароля."""
        return self.reset_password_action.get_absolute_url()

    def get_change_password_page_url(self):
        """Возвращает URL страницы изменения пароля."""
        return self.change_password_page_action.get_absolute_url()

    def get_change_password_url(self):
        """Возвращает URL экшена изменения пароля."""
        return self.change_password_action.get_absolute_url()


class LoginPageAction(BaseAction):
    """Экшн отображает страницу входа."""

    url = const.LOGIN_PAGE_URL
    template_file_name = 'simple_auth/login_page.html'

    def _get_login_panel(self, request, context):
        """Возвращает компонент панели логина."""
        get_login_panel = ioc.get('simple_auth__get_login_panel')

        return self.handle('get_login_panel', get_login_panel(request, context))

    def get_template_context(self, request, context):
        """Формирует контекст шаблона страницы входа."""
        return dict(
            login_url=self.parent.get_login_url(),
            login_panel=self._get_login_panel(request, context),
            reset_password_page_url=self.parent.get_reset_password_page_url(),
        )

    def run(self, request, context):
        return render(request, self.template_file_name, self.get_template_context(request, context))


class LoginAction(BaseAction):
    """Проверяет данные и выполняет вход."""

    url = '/login'

    def run(self, request, context):
        username = context.login
        password = context.password

        err_msg = self.parent.login_checker.check(request, username, password)

        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            result = HttpResponseRedirect('/')
        elif err_msg:
            result = PreJsonResult(
                dict(
                    success=False,
                    redirect='',
                    message=err_msg or '',
                )
            )
        else:
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)

            result = PreJsonResult(
                dict(
                    success=True,
                    redirect='/',
                )
            )

        return result


class ResetPasswordPageAction(BaseAction):
    """Экшен страницы восстановления пароля."""

    url = const.RESET_PASSWORD_PAGE_URL
    template_file_name = 'simple_auth/reset_password_page.html'

    def get_template_context(self, request, context):
        """Формирует контекст для шаблона восстановления пароля."""
        return dict(
            login_page_url=self.parent.get_login_page_url(), reset_password_url=self.parent.get_reset_password_url()
        )

    def run(self, request, context):
        return render(request, self.template_file_name, self.get_template_context(request, context))


class ResetPasswordAction(BaseAction):
    """Экшен восстановления пароля."""

    url = const.RESET_PASSWORD_URL
    email_template_file_name = 'simple_auth/email/reset_password.html'

    def context_declaration(self):
        """Определяет входной контекст с email для восстановления."""
        return {'email': {'type': 'str'}}

    def get_email_template_context(self, request, context):
        """Формирует контекст для email шаблона восстановления пароля."""
        site_url = settings.SITE_URL.rstrip('/')

        return dict(site_url=site_url, recover_url=urljoin(site_url, self.parent.get_change_password_page_url()))

    @staticmethod
    def _get_user_by_email(email):
        """Ищет пользователя по email."""
        if ioc.has_value('get_user_by_email'):
            get_user_by_email = ioc.get('get_user_by_email')
        else:

            def get_user_by_email(email):
                query = get_user_model().objects.filter(email=email)
                if query.count() == 1:
                    return query.get()

        return get_user_by_email(email)

    def run(self, request, context):
        user = ResetPasswordAction._get_user_by_email(context.email)
        if user is None:
            return OperationResult(
                False,
                message=(
                    'Этот адрес электронной почты не связан ни с одной учетной '
                    'записью. Вы уверены, что зарегистрированы?'
                ),
            )

        now = datetime.datetime.now()
        life = getattr(settings, 'RESET_CODES_LIFE', None)
        life = datetime.timedelta(minutes=life or const.RESET_CODES_LIFE)

        # Удаляем устаревшие записи
        ResetPasswords.objects.filter(date__lte=now - life).delete()

        code = uuid4().hex
        ResetPasswords.objects.create(user=user, code=code)
        template_context = self.get_email_template_context(request, context)
        template_context.update({'username': user.username, 'code': code})

        # Шаблон отправки email
        template = render_to_string(self.email_template_file_name, template_context)

        # Отправка письма
        msg = EmailMessage('Восстановление пароля', template, settings.DEFAULT_FROM_EMAIL, [context.email])
        msg.content_subtype = 'html'
        msg.send()

        return OperationResult(message='На указанный адрес отправлено письмо с дальнейшими инструкциями.')


class ChangeResetPasswordPageAction(BaseAction):
    """Экшен страницы изменения сброшенного пароля."""

    url = const.CHANGE_RESET_PASSWORD_PAGE_URL
    template_file_name = 'simple_auth/change_reset_password_page.html'

    def context_declaration(self):
        """Определяет контекст с кодом восстановления пароля."""
        return {'code': {'type': 'str'}}

    def get_template_context(self, request, context):
        """Формирует контекст для шаблона смены пароля."""
        return dict(
            code=context.code,
            login_page_url=self.parent.get_login_page_url(),
            change_password_url=self.parent.get_change_password_url(),
        )

    def run(self, request, context):
        now = datetime.datetime.now()
        life = getattr(settings, 'RESET_CODES_LIFE', None)
        life = datetime.timedelta(minutes=life or const.RESET_CODES_LIFE)
        # Если не найден пользователь
        if not ResetPasswords.objects.filter(date__gte=now - life, code=context.code).exists():
            return HttpResponseRedirect(self.parent.get_reset_password_page_url())

        return render(request, self.template_file_name, self.get_template_context(request, context))


class ChangeResetPasswordAction(BaseAction):
    """Экшен изменения сброшенного пароля."""

    url = const.CHANGE_RESET_PASSWORD_URL
    validator = validators.DefaultPasswordValidator()

    def context_declaration(self):
        """Определяет контекст с кодом и паролями."""
        return {'code': {'type': 'str'}, 'password': {'type': 'str'}, 'password_confirm': {'type': 'str'}}

    @convert_validation_error_to(ApplicationLogicException, model=ResetPasswords)
    def run(self, request, context):
        password = context.password
        confirm = context.password_confirm

        now = datetime.datetime.now()
        life = getattr(settings, 'RESET_CODES_LIFE', None)
        life = datetime.timedelta(minutes=life or const.RESET_CODES_LIFE)

        try:
            user = ResetPasswords.objects.filter(date__gte=now - life).get(code=context.code).user
        except ResetPasswords.DoesNotExist:
            return HttpResponseRedirect(self.parent.get_reset_password_page_url())

        if password != confirm:
            raise ValidationError('Пароль и подтверждение не совпадают!')

        errors = self.validator.validate(password)
        if errors:
            raise ValidationError(errors)

        user.set_password(password)
        user.save()

        ResetPasswords.objects.filter(user=user).delete()

        return OperationResult(message='Новый пароль установлен!')


class LogoutConfirmAction(BaseAction):
    """Экшн для отображения подтверждения выхода."""

    url = '/logout-confirm'

    def run(self, request, context):
        msg_box = MessageBox(
            '', 'Вы действительно хотите выйти из системы?', MessageBox.ICON_QUESTION, MessageBox.BTN_YESNO
        )

        msg_box.handler_yes = """
        Ext.Ajax.request({
            url: '%(url)s',
            params: {'confirm': true},
            success: function(response){
                var json = Ext.util.JSON.decode(response.responseText);
                window.location = json.redirect ? json.redirect : '/';
            }
        });
        """ % {'url': self.parent.logout_action.get_absolute_url()}

        return http.HttpResponse(msg_box.get_script())


class LogoutAction(BaseAction):
    """Экшн выполняет выход."""

    url = '/logout'

    def run(self, request, context):
        auth.logout(request)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return PreJsonResult({})
        else:
            return http.HttpResponseRedirect('/')
