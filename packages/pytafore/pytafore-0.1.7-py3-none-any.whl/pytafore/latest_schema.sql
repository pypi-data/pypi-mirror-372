select s.nspname
from pg_catalog.pg_namespace s
join pg_catalog.pg_user u on u.usesysid = s.nspowner
where s.nspname not in ('information_schema', 'pg_catalog', 'public')
    and s.nspname like '{pattern}'
    and s.nspname not like 'pg_toast%'
    and s.nspname not like 'pg_temp_%'
order by nspname desc
limit {limit};
