from educommon.django.db.routers import (
    ServiceDbRouterBase,
)


class AuditLogRouter(ServiceDbRouterBase):
    app_name = 'audit_log'
    service_db_model_names = {'AuditLog', 'LogProxy', 'Table'}
