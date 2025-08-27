-------------------------------------------------------------------------------
--
--  Установка/переустановка логирующей подсистемы:
--
--  * Создается Foreign Table - ссылка на таблицу из сервисной БД.
--  * На каждую таблицу создается триггер "audit_trigger", который записывает
--    информацию о каждом INSERT / UPDATE / DELETE запросе в таблицу
--    audit_log_auditlog в сервисной БД.
--  * Создается Event Trigger на создание новой таблицы, по которому
--    на созданную таблицу вешается логирующий триггер.
--  * Создается функция audit.is_valid_options, которая используется
--    при обновлении параметров подключения.
--
--  Перед выполнением запроса, необходимо подставить с помощью метода format
--  следующие параметры для сервисной БД:
--      host - адрес сервера,
--      port - порт,
--      dbname - имя БД,
--      user - имя пользователя,
--      password - пароль.
--
--  Для корректной записи в лог желательно установить в custom settings:
--     audit_log.user_id - модель пользователя,
--     audit_log.user_type_id - content type id модели пользователя,
--     audit_log.ip - IP, с которого пришел запрос

--  В PostgreSQL должна быть поддержка hstore. В Ubuntu требуется
--  установленный пакет postgresql-contrib.
--
--  До подключения логирования от суперпользователя необходимо
--  выполнить SQL команды.
--
--  В основной БД:
--      CREATE EXTENSION IF NOT EXISTS postgres_fdw;
--      CREATE EXTENSION IF NOT EXISTS hstore;
--
--      GRANT USAGE ON FOREIGN DATA WRAPPER postgres_fdw TO PUBLIC;
--
--
--  В сервисной БД:
--      CREATE EXTENSION IF NOT EXISTS hstore;
--  Минимальная поддерживаемая версия PostgreSQL 9.3.
-------------------------------------------------------------------------------


-- Сервер сервисной БД
DROP SERVER IF EXISTS service_db_server CASCADE;
CREATE SERVER service_db_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host '{host}', dbname '{dbname}', port '{port}');


-- Параметры авторизации на сервере.
CREATE USER MAPPING
    FOR PUBLIC SERVER service_db_server
    OPTIONS (user '{user}', password '{password}');


-- Foreign table для таблицы логирования из сервисной базы.
DROP FOREIGN TABLE IF EXISTS audit.audit_log;
CREATE FOREIGN TABLE audit.audit_log (
    user_id integer,
    user_type_id integer,
    time timestamp with time zone NOT NULL,
    table_id integer NOT NULL,
    object_id integer NOT NULL,
    changes HSTORE,
    data HSTORE,
    ip inet,
    operation smallint NOT NULL
) SERVER service_db_server OPTIONS (
    schema_name 'public',
    table_name 'audit_log_auditlog'
);


-- Foreign table для выборки из внутреннего реестра таблиц.
DROP FOREIGN TABLE IF EXISTS audit.table;
CREATE FOREIGN TABLE audit."table" (
    id integer NOT NULL,
    name character varying(250) NOT NULL,
    "schema" character varying(250) NOT NULL
) SERVER service_db_server OPTIONS (
    schema_name 'public',
    table_name 'audit_log_table'
);

-- Foreign table для добавления таблицы во внутренний реестр таблиц.
DROP FOREIGN TABLE IF EXISTS audit.table_for_inserting;
CREATE FOREIGN TABLE audit.table_for_inserting (
    name character varying(250) NOT NULL,
    "schema" character varying(250) NOT NULL,
    "logged" boolean NOT NULL
) SERVER service_db_server OPTIONS (
    schema_name 'public',
    table_name 'audit_log_table'
);
-------------------------------------------------------------------------------


-- Удаляет все функции с указанным именем в схеме audit вне зависимости от
-- типа и количества аргументов.
CREATE OR REPLACE FUNCTION audit.drop_functions_by_name(
    name text
) RETURNS VOID AS
$body$
DECLARE
    rec RECORD;
    sql TEXT;
BEGIN
    FOR rec IN
        SELECT
            pg_proc.oid,
            pg_namespace.nspname,
            pg_proc.proname
        FROM
            pg_proc
            INNER JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
        WHERE
            pg_namespace.nspname = 'audit' and
            pg_proc.proname = name
    LOOP
        EXECUTE
            'DROP FUNCTION ' || rec.nspname || '.' || rec.proname ||
                '(' || pg_get_function_identity_arguments(rec.oid) || ') ' ||
                'CASCADE';
    END LOOP;
END
$body$
LANGUAGE plpgsql;


-- Возвращает значение параметра с соответствующим названием.
-- Параметры устанавливаются в сессии БД приложением.
SELECT audit.drop_functions_by_name('get_param');
CREATE FUNCTION audit.get_param(
    param_name text
) RETURNS text AS
$body$
DECLARE
    result text;
BEGIN
    result := current_setting(param_name);
    IF result = '' THEN
        RETURN NULL;
    END IF;
    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END
$body$
LANGUAGE plpgsql;


-- Возвращает id таблицы в перечне таблиц
SELECT audit.drop_functions_by_name('get_table_id');
CREATE FUNCTION audit.get_table_id(
    table_schema text,
    table_name text
) RETURNS integer AS $body$
DECLARE
    table_id integer;
BEGIN
    SELECT id INTO table_id
    FROM audit."table"
    WHERE name = table_name and "schema" = table_schema
    LIMIT 1;

    RETURN table_id;
END
$body$
LANGUAGE plpgsql;


-- Триггер на внесение изменений
SELECT audit.drop_functions_by_name('on_modify');
CREATE FUNCTION audit.on_modify(
) RETURNS TRIGGER AS $body$
DECLARE
    data HSTORE;
    changes HSTORE;
    user_id INTEGER;
    user_type_id INTEGER;
    ip TEXT;
    result_value RECORD;
    result_value_id INTEGER;
    operation_code INTEGER;
    len INTEGER;
    text_error TEXT;
    auto_now_field_names TEXT[];
    all_changed_have_auto_now BOOLEAN;
BEGIN
    operation_code := 0;
    user_id := audit.get_param('audit_log.user_id');
    user_type_id := audit.get_param('audit_log.user_type_id');
    ip := audit.get_param('audit_log.ip');
    changes := NULL;
    IF (TG_OP = 'INSERT') THEN
        data := hstore(NEW);
        result_value := NEW;
        operation_code := 1;
    ELSIF (TG_OP = 'UPDATE') THEN
        data := hstore(OLD);
        changes := hstore(NEW) - hstore(OLD);
        len := array_length(akeys(changes),1);
        auto_now_field_names := ARRAY(SELECT jsonb_array_elements_text({auto_now_fields}::jsonb -> TG_TABLE_NAME::TEXT));
        all_changed_have_auto_now := auto_now_field_names @> akeys(changes);
        -- Если изменений нет или изменения, только в автообновляемых полях, то не логируем.
        IF (len IS NOT NULL OR len = 0) AND NOT all_changed_have_auto_now THEN
            result_value := NEW;
            operation_code := 2;
        END IF;
    ELSIF (TG_OP = 'DELETE') THEN
        data := hstore(OLD);
        result_value := OLD;
        operation_code := 3;
    ELSE
        text_error := format(
            '[audit_log] - TABLE_NAME - %s, Other action occurred: %s, at %s',
            TG_TABLE_NAME, TG_OP, NOW()
        );
        PERFORM audit.log_postgres_error('WARNING', text_error);
        RAISE WARNING '%', text_error;
        RETURN NULL;
    END IF;
    IF operation_code != 0 THEN
        BEGIN
            result_value_id := result_value.id;
        EXCEPTION WHEN OTHERS THEN
            result_value_id := 0;
        END;

        INSERT INTO audit.audit_log(
            "user_id", "user_type_id", "time", "table_id", "object_id",
            "data", "changes", "ip", "operation"
        ) VALUES (
            user_id, user_type_id, NOW(),
            audit.get_table_id(TG_TABLE_SCHEMA::TEXT, TG_TABLE_NAME::TEXT),
            result_value_id, data, changes, audit.str_to_ip(ip), operation_code
        );
    END IF;
    RETURN result_value;
EXCEPTION
    WHEN data_exception THEN
        text_error := format(
            '[audit_log] - TABLE_NAME - %s, UDF ERROR [DATA EXCEPTION] - ' ||
            'SQLSTATE: %s, SQLERRM: %s',
            TG_TABLE_NAME, SQLSTATE, SQLERRM
        );
        PERFORM audit.log_postgres_error('WARNING', text_error);
        RAISE WARNING '%', text_error;
        RETURN NULL;
    WHEN unique_violation THEN
        text_error := format(
            '[audit_log] - TABLE_NAME - %s, UDF ERROR [UNIQUE] - ' ||
            'SQLSTATE: %s, SQLERRM: %s',
            TG_TABLE_NAME, SQLSTATE, SQLERRM
        );
        PERFORM audit.log_postgres_error('WARNING', text_error);
        RAISE WARNING '%', text_error;
        RETURN NULL;
    WHEN OTHERS THEN
        text_error := format(
            '[audit_log] - TABLE_NAME - %s, UDF ERROR [OTHER] - ' ||
            'SQLSTATE: %s, SQLERRM: %s', TG_TABLE_NAME, SQLSTATE, SQLERRM);
        PERFORM audit.log_postgres_error('WARNING', text_error);
        RAISE WARNING '%', text_error;
        RETURN NULL;
END;
$body$
LANGUAGE plpgsql;


-- Удаляет все триггеры на внесение изменений
SELECT audit.drop_functions_by_name('drop_all_triggers');
CREATE FUNCTION audit.drop_all_triggers(
) RETURNS void AS $body$
DECLARE
    target_table RECORD;
BEGIN
    FOR target_table IN
        SELECT DISTINCT event_object_table as table_name, event_object_schema as table_schema
        FROM information_schema.triggers
        WHERE event_object_schema = 'public'
          AND trigger_name = 'audit_trigger'
          AND trigger_schema = 'public'
    LOOP
        EXECUTE
            'drop trigger if exists audit_trigger ' ||
            'on ' || target_table.table_schema || '.' || target_table.table_name;
    END LOOP;
END
$body$
LANGUAGE plpgsql;


-- Создаёт триггеры на внесение изменений для отслеживаемых таблиц
SELECT audit.drop_functions_by_name('create_triggers');
CREATE FUNCTION audit.create_triggers(
) RETURNS void AS $body$
DECLARE
    target_table RECORD;
BEGIN
    FOR target_table IN
        SELECT name AS table_name, schema AS table_schema
        FROM audit.table_for_inserting
        WHERE logged = TRUE AND name NOT IN (
            SELECT event_object_table
            FROM information_schema.triggers
            WHERE event_object_schema = 'public' AND
                    trigger_name = 'audit_trigger' AND
                    trigger_schema = 'public'
            )
        AND EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = schema
            AND table_name = name
        )
    LOOP
        EXECUTE
            'create trigger audit_trigger after insert or update or delete ' ||
            'on '|| target_table.table_schema || '.' ||
            target_table.table_name || ' ' ||
            'for each row execute procedure audit.on_modify()';
    END LOOP;
END
$body$
LANGUAGE plpgsql;


-- Проверяет, соответствуют ли опции подключения к сервисной БД
-- переданным в аргументах.
SELECT audit.drop_functions_by_name('is_valid_options');
CREATE FUNCTION audit.is_valid_options(
    host TEXT,
    dbname TEXT,
    port TEXT,
    mapped_username TEXT,
    password TEXT
) RETURNS BOOLEAN AS $body$
DECLARE
    options HSTORE;
BEGIN
    SELECT hstore(
        array_agg(option_name::text ORDER BY option_name),
        array_agg(option_value::text ORDER BY option_name)
    ) INTO options
    FROM information_schema.foreign_server_options
    WHERE foreign_server_name = 'service_db_server';

    IF
        options -> 'host' != host OR
        options -> 'dbname' != dbname OR
        options -> 'port' != port
    THEN
        RETURN FALSE;
    END IF;

    SELECT hstore(
        array_agg(option_name::text ORDER BY option_name),
        array_agg(option_value::text ORDER BY option_name)
    ) INTO options
    FROM information_schema.user_mapping_options
    WHERE foreign_server_name = 'service_db_server' AND
          authorization_identifier = 'PUBLIC';

    IF
        options -> 'user' != mapped_username OR
        options -> 'password' != password
    THEN
        RETURN FALSE;
    END IF;

    RETURN TRUE;
END;
$body$
LANGUAGE plpgsql;


-- Функция для получения корректного ip. Возвращает пустое значение и записывает
-- в текстовый лог ошибку в случае, если nginx вернул некорректный ip-адрес.
SELECT audit.drop_functions_by_name('str_to_ip');
CREATE OR REPLACE FUNCTION audit.str_to_ip(
    str TEXT,
    log_error BOOLEAN DEFAULT TRUE
) RETURNS INET AS $body$
DECLARE
    result INTEGER;
    text_error TEXT;
BEGIN
    RETURN str::INET;
EXCEPTION
    WHEN OTHERS THEN
        -- Возможные ошибки:
        --   - invalid input syntax for type inet
        IF log_error THEN
            text_error := format(
                '[audit_log] - UDF ERROR [OTHER] - SQLSTATE: %s, SQLERRM: %s',
                SQLSTATE, SQLERRM
            );
            PERFORM audit.log_postgres_error('WARNING', text_error);
        END IF;
        RAISE WARNING '%', text_error;
        RETURN NULL;
END;
$body$
LANGUAGE plpgsql;


-- Функция логирования ошибок Postgres (конструкций RAISE)
SELECT audit.drop_functions_by_name('log_postgres_error');
CREATE FUNCTION audit.log_postgres_error(
    level_error TEXT,
    text_error TEXT
) RETURNS VOID AS $body$
BEGIN
    INSERT INTO audit.postgresql_errors(
        "user_id",
        "ip",
        "time",
        "level",
        "text"
    ) VALUES (
        audit.get_param('audit_log.user_id')::INTEGER,
        audit.str_to_ip(audit.get_param('audit_log.ip'), false),
        NOW(),
        level_error,
        text_error
    );
END;
$body$
LANGUAGE plpgsql;
