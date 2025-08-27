-- Функция нахождения разницы между двумя jsonb.
CREATE OR REPLACE FUNCTION jsonb_diff(val1 JSONB, val2 JSONB)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_object_agg(
        COALESCE(a.key, b.key),
        COALESCE(b.value, a.value)
    )
    INTO result
    FROM (
        SELECT key, value FROM jsonb_each(val1)
    ) a
    FULL JOIN (
        SELECT key, value FROM jsonb_each(val2)
    ) b ON a.key = b.key
    WHERE a.value IS DISTINCT FROM b.value
        OR a.value IS NULL
        OR b.value IS NULL;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Функция проверки, что текстовое поле можно преобразовать в jsonb.
CREATE OR REPLACE FUNCTION is_valid_jsonb(input_text TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    PERFORM input_text::jsonb;
    RETURN TRUE;
EXCEPTION
    WHEN others THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

DO $$
DECLARE
    chunk_size INT := 1000;
    deleted_count INT := 0;
BEGIN
    LOOP
        DELETE FROM state_log_all
        WHERE id IN (
            SELECT object_previous_and_current.id
            FROM (
                SELECT *,
                    LAG(object) OVER (
                        PARTITION BY model_id, model
                        ORDER BY date
                    ) AS previous_object
                    FROM state_log_all
            ) AS object_previous_and_current
            WHERE previous_object IS NOT NULL
            AND EXISTS (
                SELECT 1
                FROM jsonb_each({auto_now_fields}) AS mapping(table_name, keys)
                WHERE
                    is_valid_jsonb(previous_object) AND
                    is_valid_jsonb(object) AND
                    model = mapping.table_name::text AND
                    ARRAY(
                        SELECT jsonb_object_keys(
                            jsonb_diff(
                                COALESCE(previous_object::jsonb -> 0 -> 'fields', jsonb_build_object()),
                                COALESCE(object::jsonb -> 0 -> 'fields', jsonb_build_object())
                            )
                        )
                    ) <@ ARRAY(SELECT jsonb_array_elements_text(mapping.keys))
            )
            LIMIT chunk_size
        );

        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        EXIT WHEN deleted_count = 0;
    END LOOP;
END $$;