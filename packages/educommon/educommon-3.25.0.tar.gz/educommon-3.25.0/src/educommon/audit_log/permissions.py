PERM_GROUP__AUDIT_LOG = 'audit_log'
PERM_GROUP__AUDIT_LOG_ERRORS = 'audit_log_errors'


PERM__AUDIT_LOG__VIEW = PERM_GROUP__AUDIT_LOG + '/view'
PERM__AUDIT_LOG__ERRORS__VIEW = PERM_GROUP__AUDIT_LOG_ERRORS + '/view'
PERM__AUDIT_LOG__ERRORS__DELETE = PERM_GROUP__AUDIT_LOG_ERRORS + '/delete'


permissions = (
    (PERM__AUDIT_LOG__VIEW, 'Просмотр', 'Разрешает просмотр журнала изменений.'),
    (
        PERM__AUDIT_LOG__ERRORS__VIEW,
        'Просмотр журнала ошибок PostgreSQL',
        'Разрешает просмотр журнала ошибок PostgreSQL.',
    ),
    (
        PERM__AUDIT_LOG__ERRORS__DELETE,
        'Удаление записей журнала ошибок PostgreSQL',
        'Разрешает удаление записей из журнала ошибок PostgreSQL.',
    ),
)


dependencies = {
    PERM__AUDIT_LOG__ERRORS__DELETE: {
        PERM__AUDIT_LOG__ERRORS__VIEW,
    },
}


groups = {
    PERM_GROUP__AUDIT_LOG: 'Журнал изменений',
    PERM_GROUP__AUDIT_LOG_ERRORS: 'Журнал изменений',
}


partitions = {
    'Администрирование': (
        PERM_GROUP__AUDIT_LOG,
        PERM_GROUP__AUDIT_LOG_ERRORS,
    ),
}
