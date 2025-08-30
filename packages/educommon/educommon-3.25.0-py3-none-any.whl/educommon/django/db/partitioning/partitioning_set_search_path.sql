begin;

alter function partitioning.before_insert() set search_path = '{schema_names}';

alter function partitioning.after_insert() set search_path = '{schema_names}';

alter function partitioning.instead_of_insert() set search_path = '{schema_names}';

alter function partitioning.before_update() set search_path = '{schema_names}';

commit;