begin;


-- Во избежание конфликтов разместим все функции, обеспечивающие
-- партиционирование, в отдельной схеме.
create schema if not exists partitioning;


create or replace function partitioning.getattr(
    rec anyelement,
    table_name text,
    column_name text
) returns text as $BODY$
    ---------------------------------------------------------------------------
    -- Возвращает значение колонки column_name из записи rec
    -- (аналог getattr() в Python)
    ---------------------------------------------------------------------------
    declare
        column_value text;
    begin
        execute
            'select ($1::' || quote_ident(table_name) || ').' ||
            quote_ident(column_name)
            into column_value using rec;
        return column_value;
    end;
$BODY$ language plpgsql immutable;


drop function if exists partitioning.get_sequence_for_field(text, text, text);


-------------------------------------------------------------------------------
-- Удаление функции для исправления опечатки в её имени. Вместо неё создаётся
-- get_partition_name(text, timestamp).

drop function if exists partitioning.get_patrition_name(text, timestamp);
--- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


create or replace function partitioning.get_partition_name(
    parent_table text,
    date_value timestamp
) returns text as $BODY$
    ---------------------------------------------------------------------------
    -- Формирует название раздела из имени родительской таблицы и значения
    -- колонки, определяющей раздел таблицы.
    ---------------------------------------------------------------------------
    declare
        month text;
        year text;
    begin
        month := 'm' || lpad(date_part('month', date_value)::TEXT, 2, '0');
        year := 'y' || date_part('year', date_value)::TEXT;
        return parent_table || '_' || year || month;
    end;
$BODY$ language plpgsql immutable;


drop function if exists partitioning.set_partition_constraint(
    text, text, integer, integer
);


create or replace function partitioning.set_partition_constraint(
    schema_name text,
    partition_name text,
    column_name text,
    year integer,
    month integer
) returns void as $BODY$
    ---------------------------------------------------------------------------
    -- Устанавливает ограничения для указанного раздела.
    --
    -- Ранее установленные check-ограничения удаляются.
    ---------------------------------------------------------------------------
    declare
        rec record;
        constraint_name text;
        min_timestamp timestamp with time zone;
        max_timestamp timestamp with time zone;
    begin
        constraint_name := partition_name || '_date_check';

        -- Удаление имеющихся check-ограничений.
        for rec in
            select pg_constraint.conname
            from pg_constraint
                inner join pg_namespace on (
                    pg_constraint.connamespace = pg_namespace.oid
                )
            where
                pg_constraint.contype = 'c' and  -- тип ограничения: check
                pg_namespace.nspname = schema_name and
                pg_constraint.conname like '%_date_check' and
                pg_constraint.conrelid = partition_name::regclass::oid
        loop
            execute
                'alter table ' || schema_name || '.' || partition_name || ' ' ||
                    'drop constraint ' || rec.conname;
        end loop;

        -- Определение граничных значений для раздела.
        min_timestamp := (year || '-' ||  month || '-1 00:00:00')::timestamp with time zone;
        max_timestamp := min_timestamp + interval '1 month'
                         - interval '1 microseconds';

        execute
            'alter table ' || schema_name || '.' ||  partition_name || ' ' ||
                'add constraint ' || partition_name || '_date_check ' ||
                'check (' ||
                    column_name || ' between ' ||
                    '''' || min_timestamp ||
                    ''' and ''' ||
                    max_timestamp || '''' ||
                ')';
    end;
$BODY$ language plpgsql;


create or replace function partitioning.table_exists(
    name text
) returns boolean as $BODY$
    ---------------------------------------------------------------------------
    -- Проверяет, существует ли в БД таблица table_name.
    ---------------------------------------------------------------------------
    begin
        return exists(
            select 1
            from information_schema.tables
            where table_name = name
        );
    end;
$BODY$ language plpgsql immutable;


create or replace function partitioning.trigger_exists(
    table_name text, trigger_name text
) returns boolean as $BODY$
    ---------------------------------------------------------------------------
    -- Проверяет, существует ли в таблице table_name триггер с именем trigger_name.
    ---------------------------------------------------------------------------
    begin
        return exists(
            select 1
            from pg_catalog.pg_trigger
            where tgrelid = table_name::regclass::oid and
            tgname = trigger_name
        );
    end;
$BODY$ language plpgsql immutable;


create or replace function partitioning.is_table_partitioned(
    table_name text
) returns boolean as $BODY$
    ---------------------------------------------------------------------------
    -- Возвращает true, если указанная таблица разбита на разделы.
    --
    -- Таблица считается разбитой на разделы, если у нее есть триггеры с
    -- соответствующими именами.
    ---------------------------------------------------------------------------
    begin
        return (
            select 1
            from pg_catalog.pg_trigger
            where
                tgrelid = table_name::regclass::oid and
                tgname in (
                    'partitioning__' || table_name || '__before_insert',
                    'partitioning__' || table_name || '__after_insert',
                    'partitioning__' || table_name || '__update'
                )
            limit 1
        );
    end;
$BODY$ language plpgsql immutable;


create or replace function partitioning.get_table_space(
    schema_name name,
    table_name name
) returns name as $BODY$
    ---------------------------------------------------------------------------
    -- Возвращает имя табличного пространства, в котором расположена таблица.
    --
    -- Если таблица расположена в табличном пространстве по умолчанию, то
    -- функция возвращает null.
    ---------------------------------------------------------------------------
    select
        "tablespace"
    from
        pg_catalog.pg_tables
    where
        schemaname = schema_name and
        tablename = table_name
$BODY$ language sql immutable;


drop function if exists partitioning.create_partition(text, text, text, date);


create or replace function partitioning.create_partition(
    schema_name text,
    parent_table_name text,
    pk_column_name text,
    column_name text,
    column_value date
) returns void as $BODY$
    ---------------------------------------------------------------------------
    -- Создает раздел таблицы.
    ---------------------------------------------------------------------------
    declare
        partition_name text;
        tablespace_name name;
        tablespace_sql text;
        trigger_name text;
    begin
        -- имя создаваемой таблицы
        partition_name := partitioning.get_partition_name(
            parent_table_name, column_value
        );

        tablespace_name := partitioning.get_table_space(
            schema_name::name, parent_table_name::name
        );
        if tablespace_name is null then
            tablespace_sql := '';
        else
            tablespace_sql := ' tablespace ' || tablespace_name;
        end if;

        -- создание раздела
        execute
            'create table if not exists ' ||
                schema_name || '.' || partition_name || ' '
            '(' ||
                'like ' || parent_table_name || ' ' ||
                'including defaults ' ||
                'including constraints ' ||
                'including indexes' ||
            ') ' ||
            'inherits (' || schema_name || '.' || parent_table_name || ')' ||
            tablespace_sql;

        perform partitioning.set_partition_constraint(
            schema_name,
            partition_name,
            column_name,
            date_part('year', column_value)::integer,
            date_part('month', column_value)::integer
        );

        -- создание триггера для раздела обрабатывающего изменения, которые
        -- требуют переноса записи из одного раздела таблицы в другой
        -- перед созданием проверяем, что такого триггера нет для партиции
        trigger_name = 'partitioning__' || partition_name || '__update';
        if not partitioning.trigger_exists(partition_name, trigger_name) then
            execute
                'create trigger ' || trigger_name || ' '
                'before update on ' ||
                    schema_name || '.' || partition_name || ' ' ||
                'for each row ' ||
                'execute procedure partitioning.before_update(' ||
                    '''' || pk_column_name || ''', ''' || column_name || ''''
                ')';
        end if;
    end;
$BODY$ language plpgsql;


create or replace function partitioning.before_insert()
returns trigger as $BODY$
    ---------------------------------------------------------------------------
    -- Обработчик добавления записей в партиционированную таблицу.
    --
    -- При отсутствии необходимого раздела создает его и вставляет в него
    -- добавляемую запись.
    ---------------------------------------------------------------------------
    declare
        partition_name text;  -- имя раздела
        pk_column_name text;  -- имя колонки с первичным ключом
        column_name text;  -- имя колонки, определяющей раздел таблицы
        column_value date;  -- значение поля, определяющее раздел таблицы
    begin
        pk_column_name := TG_ARGV[0];
        column_name := TG_ARGV[1];

        column_value := partitioning.getattr(NEW, TG_TABLE_NAME, column_name);
        partition_name := partitioning.get_partition_name(
            TG_TABLE_NAME, column_value
        );

        if not partitioning.table_exists(partition_name) then
            -- целевого раздела нет, создадим его
            perform partitioning.create_partition(
                TG_TABLE_SCHEMA::text,
                TG_TABLE_NAME::text,
                pk_column_name,
                column_name,
                column_value
            );
        end if;

        -- добавим запись в целевой раздел
        execute
            'insert into ' || partition_name || ' ' ||
            'values (($1).*);'
            USING NEW;

        -- в родительскую таблицу добавлять записи не нужно
        return NEW;
    end;
$BODY$ language plpgsql;


create or replace function partitioning.after_insert()
returns trigger as $BODY$
    ---------------------------------------------------------------------------
    -- Удаляет из родительской таблицы добавленную запись.
    --
    -- Это необходимо в связи с тем, что создание записи в Django выполняется с
    -- параметром RETURNING b и без реального создания записи в родительской
    -- таблице значение ключевого поля будет равно NULL.
    ---------------------------------------------------------------------------
    declare
        pk_column_name text;  -- имя колонки с первичным ключом
    begin
        pk_column_name := TG_ARGV[0];

        execute
            'delete from only ' || TG_TABLE_NAME || ' ' ||
            'where ' || pk_column_name || ' = ' ||
                partitioning.getattr(NEW, TG_TABLE_NAME, pk_column_name);

        -- в родительскую таблицу добавлять записи не нужно
        return NEW;
    end;
$BODY$ language plpgsql;


create or replace function partitioning.instead_of_insert()
returns trigger as $BODY$
    ---------------------------------------------------------------------------
    -- Триггер для оптимизированной вставки записей.
    --
    -- В связи с особенностями Django ORM при добавлении записи в раздел ее
    -- также необходимо добавить помимо раздела еще и в основную таблицу, а
    -- затем удалить. Это не оптимально, потому что вместо одной операции
    -- вставки выполняется три операции - 2 вставки и 1 удаление.
    -- Добавление записи через представление позволяет решить эту проблему и
    -- обойтись только одной операцией вставки, при этом вернув в Django ORM
    -- id созданной записи, чтобы Django ORM работал корректно.
    ---------------------------------------------------------------------------
    declare
        table_name text;  -- имя таблицы
        partition_name text;  -- имя раздела

        pk_column_name text;  -- имя колонки с первичным ключом
        pk_column_value integer;  -- значение первичного ключа
        pk_column_sequence regclass;

        column_name text;  -- имя колонки, определяющей раздел таблицы
        column_value date;  -- значение поля, определяющее раздел таблицы
    begin
        pk_column_name := TG_ARGV[0];
        column_name := TG_ARGV[1];
        column_value := partitioning.getattr(NEW, TG_TABLE_NAME, column_name);
        --- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        -- Определение имени партиционированной таблицы (триггер срабатывает
        -- для представления и в TG_TABLE_NAME указано имя представления).

        table_name := left(
            TG_TABLE_NAME, length(TG_TABLE_NAME) - length('{view_name_suffix}')
        );
        --- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        -- Заполнение первичного ключа, если он не был указан.
        -- (т.к. функционал setattr реализовать затруднительно, пока считаем,
        -- что pk_column_name всегда равен id, это актуально почти для всех
        -- случаев).

        if NEW.id is null then
            NEW.id := nextval(pg_get_serial_sequence(
                'public' || '.' || table_name, pk_column_name
            ));
        end if;
        --- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        -- Определение целевого раздела для вставки записи

        partition_name := partitioning.get_partition_name(
            table_name, column_value
        );

        if not partitioning.table_exists(partition_name) then
            -- целевого раздела нет, создадим его
            perform partitioning.create_partition(
                TG_TABLE_SCHEMA::text,
                table_name,
                pk_column_name,
                column_name,
                column_value
            );
        end if;
        --- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        -- добавим запись в целевой раздел
        execute
            'insert into ' || partition_name || ' ' ||
            'values (($1).*);'
            USING NEW;

        return NEW;
    end;
$BODY$ language plpgsql;


create or replace function partitioning.before_update()
returns trigger as $BODY$
    ---------------------------------------------------------------------------
    -- Обработчик изменения записей в разделах таблицы.
    --
    -- В случае изменения в записи значения, определяющего раздел таблицы,
    -- переносит эту запись в другой раздел. При необходимости создает новый
    -- раздел таблицы.
    ---------------------------------------------------------------------------
    declare
        parent_table_name text;  -- имя родительской таблицы
        dst_table_name text;  -- имя раздела, в который будет перенесена запись
        pk_column_name text;  -- имя колонки с первичным ключом
        column_name text;  -- имя колонки, определяющей раздел таблицы
        old_column_value date;  -- исходное значение колонки, определяющее
                               -- раздел таблицы
        new_column_value date;  -- новое значение колонки, определяющей раздел
                               -- таблицы
    begin
        pk_column_name := TG_ARGV[0];
        column_name := TG_ARGV[1];

        old_column_value := date_trunc(
            'month', partitioning.getattr(OLD, TG_TABLE_NAME, column_name)::date
        );
        new_column_value := date_trunc(
            'month', partitioning.getattr(NEW, TG_TABLE_NAME, column_name)::date
        );

        -- определение имени родительской таблицы
        if TG_TABLE_NAME ~  '_y([0-9]{{4}})m([0-9]{{2}})$' then
            -- запись находится в разделе таблицы
            parent_table_name := left(
                TG_TABLE_NAME, length(TG_TABLE_NAME) - length('_yXXXXmXX')
            );
        else
            -- запись находится в родительской таблице
            parent_table_name := TG_TABLE_NAME;
        end if;

        dst_table_name := partitioning.get_partition_name(
            parent_table_name, new_column_value
        );

        if TG_TABLE_NAME = dst_table_name then
            -- перенос записи в другой раздел не требуется
            return NEW;
        end if;

        -- значение поля, определяющего раздел таблицы, изменено так, что
        -- необходим перенос записи в другой раздел

        if not partitioning.table_exists(dst_table_name) then
            -- целевого раздела нет, создадим его
            perform partitioning.create_partition(
                TG_TABLE_SCHEMA::text,
                parent_table_name,
                pk_column_name,
                column_name,
                new_column_value
            );
        end if;

        -- перенос записи в другой раздел таблицы
        execute
            'delete from ' || TG_TABLE_NAME || ' ' ||
            'where ' || pk_column_name || ' = ' ||
                partitioning.getattr(NEW, TG_TABLE_NAME, pk_column_name);
        execute
            'insert into ' || dst_table_name || ' ' ||
            'values (($1).*)' using NEW;

        return null;
    end;
$BODY$ language plpgsql;


commit;
