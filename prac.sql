CREATE TABLE my_table(
	id serial not null primary key,
	name varchar(255)
);

insert into my_table(name) values('Ivan Ivanov'), ('Petr Petrov');

select * from my_table;


-- процедура с откатом
create procedure prc_test_tr(IN st_name text)
language plpgsql as $$
declare 
res integer;
begin
	insert into my_table(name) values(st_name)
	returning id into res;
	
	if (res > 5) then
		rollback;
	else commit;
	end if;
end; $$

call prc_test_tr('Gena Bukin');
call prc_test_tr('hhzhzhz Sidorov');
call prc_test_tr('Masha Sidorov');

call prc_test_tr('Lena');
select * from my_table;

create user resder_user with password '123456';
create role resder_group;
grant resder_user to resder_group;

drop user rarara;
