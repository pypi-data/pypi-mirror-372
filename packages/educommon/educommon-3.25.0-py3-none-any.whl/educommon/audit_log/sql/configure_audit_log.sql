-- Обновление параметров подключения к логирующей БД.
-- Проверяет параметры, и если хотя бы один из них изменился, обновляет их.
DO
$do$
BEGIN
    IF pg_try_advisory_lock({lock_id}) THEN
        -- На момент запуска база может быть еще не промигрированна
        IF EXISTS (
            SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name = 'audit'
        ) THEN
            IF NOT audit.is_valid_options(
                '{host}', '{dbname}', '{port}', '{user}', '{password}'
            ) THEN
                ALTER SERVER service_db_server
                    OPTIONS (
                        SET host '{host}',
                        SET dbname '{dbname}',
                        SET port '{port}'
                    );
                ALTER USER MAPPING FOR PUBLIC SERVER service_db_server
                OPTIONS (
                    SET user '{user}',
                    SET password '{password}'
                );
            END IF;
            IF {need_to_update_triggers} THEN
                PERFORM audit.drop_all_triggers();
                PERFORM audit.create_triggers();
            END IF;
        END IF;
        PERFORM pg_advisory_unlock({lock_id});
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        PERFORM pg_advisory_unlock({lock_id});
        RAISE;
END
$do$
LANGUAGE plpgsql;