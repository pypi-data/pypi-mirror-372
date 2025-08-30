-------------------------------------------------------------------------------
-- Триггеры, обеспечивающие сохранение добавляемой записи при работе напрямую
-- с партиционированной таблицей.

do language plpgsql $$
begin
    if not exists(
        select 1
        from pg_catalog.pg_trigger
        where
            tgrelid = '{table_name}'::regclass::oid and
            tgname = 'partitioning__{table_name}__before_insert'
    ) then
        create trigger partitioning__{table_name}__before_insert
            before insert on {table_name}
            for each row execute procedure partitioning.before_insert(
                '{pk_column_name}', '{column_name}'
            );
    end if;
end;
$$;

do language plpgsql $$
begin
    if not exists(
        select 1
        from pg_catalog.pg_trigger
        where
            tgrelid = '{table_name}'::regclass::oid and
            tgname = 'partitioning__{table_name}__after_insert'
    ) then
        create trigger partitioning__{table_name}__after_insert
            after insert on {table_name}
            for each row execute procedure partitioning.after_insert(
                '{pk_column_name}', '{column_name}'
            );
    end if;
end;
$$;
-------------------------------------------------------------------------------
-- Триггер, обеспечивающий перенос записи в другой раздел таблицы при изменении
-- записи в партиционированной таблице.

do language plpgsql $$
begin
    if not exists(
        select 1
        from pg_catalog.pg_trigger
        where
            tgrelid = '{table_name}'::regclass::oid and
            tgname = 'partitioning__{table_name}__update'
    ) then
        create trigger partitioning__{table_name}__update
            before update on {table_name}
            for each row execute procedure partitioning.before_update(
                '{pk_column_name}', '{column_name}'
            );
    end if;
end;
$$;
-------------------------------------------------------------------------------
-- Это представление ркомендуется использовать для вставки записей. В этом
-- случае вставка записи будет выполняться только в раздел, а основная таблица
-- не затрагивается. При этом параметр RETURNING оператора INSERT сработает
-- корректно и вернет id созданной записи.

create or replace view {table_name}{view_name_suffix} as
    select *
    from {table_name};

do language plpgsql $$
begin
    if not exists(
        select 1
        from pg_catalog.pg_trigger
        where
            tgrelid = '{table_name}{view_name_suffix}'::regclass::oid and
            tgname = 'partitioning__{table_name}__instead_of_insert'
    ) then
        create trigger partitioning__{table_name}__instead_of_insert
            instead of insert on {table_name}{view_name_suffix}
            for each row execute procedure partitioning.instead_of_insert(
                '{pk_column_name}', '{column_name}'
            );
    end if;
end;
$$;
-------------------------------------------------------------------------------
