DO $$
DECLARE
    chunk_size INT := 1000;
    deleted_count INT := 0;
BEGIN
    LOOP
        DELETE FROM audit_log_auditlog
        WHERE id IN (
            SELECT a.id
            FROM audit_log_auditlog a
            LEFT JOIN audit_log_table t ON a.table_id = t.id
            WHERE EXISTS (
                SELECT 1
                FROM jsonb_each({auto_now_fields}) AS mapping(table_name, keys)
                WHERE
                    t.name = mapping.table_name::text AND
                    akeys(a.changes) <@ ARRAY(SELECT jsonb_array_elements_text(mapping.keys))
            )
            LIMIT chunk_size
        );

        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        EXIT WHEN deleted_count = 0;
    END LOOP;
END $$;