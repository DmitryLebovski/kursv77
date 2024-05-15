CREATE ROLE head;
CREATE ROLE executor;

-- Роль head может видеть и управлять всеми таблицами
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;
GRANT USAGE, SELECT ON SEQUENCE contract_id_seq TO head;
GRANT USAGE, SELECT ON SEQUENCE extra_condition_id_seq TO head;

-- Роль executor может управлять только таблицами contract и extra_condition, но видеть все таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON contract TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON extra_condition TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON executor TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_log TO executor;


CREATE USER ivanov_ii PASSWORD '12345';
CREATE USER smirnov_av PASSWORD '12345';

GRANT head TO ivanov_ii;
GRANT executor TO smirnov_av;

ALTER ROLE head LOGIN;
ALTER ROLE executor LOGIN;


SELECT * FROM pg_roles WHERE rolname=head AND rolsuper AND rolcanlogin
SELECT * FROM pg_roles 


ALTER TABLE executor
ADD COLUMN username VARCHAR(50);

DROP TABLE head
DROP TABLE executor
DROP TABLE contract
DROP TABLE extra_condition

CREATE TABLE head(
	id serial PRIMARY KEY,
	full_name varchar(100) NOT NULL,
	phone_number varchar(18),
	email varchar(100) NOT NULL,
	head_username VARCHAR(50) not NULL
)

CREATE TABLE executor(
	id serial PRIMARY KEY,
	full_name varchar(100) NOT NULL,
	phone_number varchar(18),
	email varchar(100) NOT NULL,
	company_name varchar(100),
	executor_position varchar(100) NOT NULL,
	executor_username VARCHAR(50) NOT NULL,
	head_id INT,
	FOREIGN KEY (head_id) REFERENCES head(id)
)

CREATE TABLE contract(
	id serial PRIMARY KEY,
	contract_num VARCHAR(50) UNIQUE NOT NULL,
	conclusion_date DATE NOT NULL,
	agreement_term DATE NOT NULL,
	agreement_object TEXT,
	status varchar(100) NOT NULL,
	document_scan TEXT,
	executor_id INT,
	head_id INT,
	FOREIGN KEY (executor_id) REFERENCES executor(id),
	FOREIGN KEY (head_id) REFERENCES head(id)
)

CREATE TABLE extra_condition(
	id serial PRIMARY KEY,
	agreement_extras TEXT,
	contract_id INT,
	FOREIGN KEY (contract_id) REFERENCES contract(id)
)

ALTER TABLE executor ALTER COLUMN executor_username DROP NOT NULL;
ALTER TABLE contract ALTER COLUMN contract_num UNIQUE;


-- Данные для таблицы "head"
INSERT INTO head (full_name, phone_number, email, head_username) VALUES
('Иванов Иван Иванович', '+7(999)123-45-67', 'ivanov@example.com', 'ivanov_ii'),
('Петров Петр Петрович', '+7(999)987-65-43', 'petrov@example.com', 'petrov_pp'),
('Сидорова Анна Сергеевна', '+7(999)543-21-09', 'sidorova@example.com', 'sidorova_as');

-- Данные для таблицы "executor"
INSERT INTO executor (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) VALUES
('Смирнов Алексей Владимирович', '+7(999)111-22-33', 'smirnov@example.com', 'ООО "Прогресс"', 'Генеральный директор', 'smirnov_av', 1),
('Кузнецова Елена Игоревна', '+7(999)444-55-66', 'kuznetsova@example.com', 'ООО "СтройИнвест"', 'Главный инженер', 'kuznetsova_ei', 2),
('Никитин Денис Александрович', '+7(999)777-88-99', 'nikitin@example.com', 'ООО "ТехноСервис"', 'Финансовый директор', 'nikitin_da', 3);

INSERT INTO executor (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) VALUES
('Test1', '', 'smirnov@example.com', '', 'Генеральный директор', 'smirnov_av', 1)

-- Данные для таблицы "contract"
INSERT INTO contract (contract_num, conclusion_date, agreement_term, agreement_object, status, executor_id, head_id) VALUES
('КТ-001', '2024-04-15', '2024-10-15', 'Строительство жилого комплекса', 'Создан', 1, 1),
('КТ-002', '2024-03-20', '2024-09-20', 'Разработка программного обеспечения', 'В ожидании', 2, 2),
('КТ-003', '2024-02-10', '2024-08-10', 'Поставка оборудования', 'Закрыт', 3, 3),

-- Данные для таблицы "extra_condition"
INSERT INTO extra_condition (agreement_extras, contract_id) VALUES 
('Дополнительные работы по благоустройству прилегающей территории', 1),
('Обязательное обучение сотрудников', 2),
('Гарантийное обслуживание на 2 года', 3);

SELECT * FROM head
SELECT * FROM executor
SELECT * FROM contract
SELECT * FROM extra_condition

select id, full_name, company_name from executor
select id from executor where full_name = 'Кузнецова Елена Игоревна'
select full_name, phone_number, email, company_name, executor_position from executor where id = 1

SELECT * 
FROM contract cn 
JOIN executor ex ON cn.executor_id = ex.id;

select id from executor where full_name = 'Кузнецова Елена Игоревна'

update contract cn set executor_id = (select id from executor where full_name = 'Кузнецова Елена Игоревна') where cn.id = 1


DELETE from extra_condition where contract_id=(select id from contract where contract_num='апдейт')
DELETE from contract where id 'апдейт'

DELETE FROM contract
DELETE FROM extra_condition

SELECT cn.contract_num as "Номер договора", cn.status as "Статус", cn.agreement_object as "Наименование договора", 
h.full_name as "ФИО руководителя", ex.full_name as "ФИО агента", 
ex.company_name as "Компания", cn.conclusion_date as "Дата заключения", 
cn.agreement_term as "Срок действия" from contract cn
JOIN head h on head_id = h.id
JOIN executor ex on executor_id = ex.id

SELECT 
    cn.contract_num AS "Номер договора", 
    cn.status AS "Статус", 
    cn.agreement_object AS "Наименование договора", 
    h.full_name AS "ФИО руководителя", 
    h.phone_number AS "Номер телефона руководителя", 
    h.email AS "Почта руководителя", 
    ex.full_name AS "ФИО агента",
    ex.phone_number AS "Номер телефона агента", 
    ex.email AS "Почта агента",
    ex.executor_position AS "Позиция агента",
    ex.company_name AS "Компания", 
    cn.conclusion_date AS "Дата заключения", 
    cn.agreement_term AS "Срок действия",
    cn.document_scan AS "Скан документа",
    exc.agreement_extras AS "Дополнительные условия"
FROM 
    contract cn
JOIN 
    head h ON cn.head_id = h.id
JOIN 
    executor ex ON cn.executor_id = ex.id
LEFT JOIN 
    extra_condition exc ON cn.id = exc.contract_id;

	
	
UPDATE contract AS cn
SET 
	contract_num = 'апдейт'
WHERE id = 1;


UPDATE executor AS ex
SET 
	full_name = 'tetsetesatest',
	email = 'tetsetesatest',
	executor_position = 'tetsetesatest',
	company_name = 'tetsetesatest'
WHERE 
	ex.id = (SELECT executor_id FROM contract WHERE id = 1);


UPDATE head AS h
SET 
	full_name = 'tetsetesatest',
	email = 'tetsetesatest'
WHERE 
	h.id = (SELECT head_id FROM contract WHERE id = 1);


UPDATE extra_condition AS exc
SET 
    agreement_extras = 'agr test'
FROM contract cn
WHERE 
    cn.id = exc.contract_id
    AND cn.id = 1;



update contract set contract_num='kt-00000' where id = '0'
select * from contract
JOIN head h on head_id = h.id
JOIN executor ex on executor_id = ex.id

SELECT full_name FROM head h WHERE h.head_username = 'ivanov_ii';

SELECT role FROM user_roles WHERE username = ivanov_ii

ALTER TABLE contract
ADD CONSTRAINT contract_num_unique UNIQUE (contract_num);

-- ТРИГГЕРЫ
CREATE OR REPLACE FUNCTION update_contract_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NOTIFY contract_updated;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contract_update_trigger
AFTER UPDATE ON contract
FOR EACH ROW
EXECUTE FUNCTION update_contract_trigger();












--Практика:
CREATE TABLE test(t1 integer, t2 text); insert into test
select i, md5(random()::text) from generate_series(1, 1000000) as i;

create table test_join(j1 integer, j2 boolean); insert into test_join
select i, i%2=1
from generate_series(1,500000) as i;

select * from test;
select * from test_join;

drop table test;
drop table test_join;

select * from test t join test_join tj on t.t1 = tj.j1;

explain select * from test t join test_join tj on t.t1 = tj.j1; --60081.00
explain select * from test t join test_join tj on t.t1 = tj.j1 limit 10000; -- 12438.64

create index idx_j1 on test_join(j1);
explain select * from test t join test_join tj on t.t1 = tj.j1; --60081.00
explain select * from test t join test_join tj on t.t1 = tj.j1 limit 10000; -- 9654.05 nested loop

create index idx_t1 on test(t1);
explain select * from test t join test_join tj on t.t1 = tj.j1; -- 39835.86  merge join
explain select * from test t join test_join tj on t.t1 = tj.j1 limit 10000; -- 798.19 merge join

drop index idx_t1;
drop index idx_j1;

explain select * from test t join test_join tj on t.t1 = tj.j1; --60081.00 join запрос
explain select * from test t where t1 in (select j1 from test_join)-- 59518.50 не коррелированный запрос
explain select * from test t where exists(select * from test_join tj where t.t1 = tj.j1 ) -- 59518.50 коррелированный запрос

explain analyze select * from test t join test_join tj on t.t1 = tj.j1; --60081.00 join запрос
--464 ms
explain analyze select * from test t where t1 in (select j1 from test_join)-- 59518.50 некоррелированный запрос
--473 ms
explain analyze select * from test t where exists(select * from test_join tj where t.t1 = tj.j1 ) -- 59518.50 коррелированный запрос
-- 461 ms
-- векторная - возв таблица, скаляр - возвр значение






create table groups
(
	id serial primary key not null,
	name text
);

create table students
(
	id serial primary key not null,
	fio text,
	age int,
	group_id int
);

insert into groups(name) values ('bsbo-01-22'), ('bsbo-(-01)-22')
insert into students(fio, age, group_id) values ('Петухович Вениамин', 65, 2), ('Полено Лена', 20, 1), 
('Пупкин Фёдор', 21, 1), ('Лампасосов Венидикт', 24, 1), ('Гопкин Гордей', 20, 2);
select * from students

--view выполняет запрос
create view v_students as
	select fio, age from students; -- простое обновляемое представления
select * from v_students
insert into v_students(fio, age) values ('Иванов Иван', 25)
delete from v_students where fio='Иванов Иван';

create view v_students_group as
select s.fio, s.age, g.name from students s join groups g on s.group_id = g.id; --сложное не обновляемое представление
select * from v_students_group

delete from v_students_group where age = 20 -- ошибка из-за join



--тригерная функция ДОБАВЛЕНИЯ данные в соединенные таблицы studens, groups
create function insert_v_students_group() 
returns trigger language plpgsql as $$
declare
	g_id integer;
begin
	select id into g_id from groups where name = NEW.name;
	insert into students(fio, age, group_id) values (NEW.fio, NEW.age, g_id);
	return null;
end;$$
-- триггер
create trigger insert_st_group instead of insert on v_students_group 
for each row
execute procedure insert_v_students_group();
insert into insert_v_students_group(fio, age, name) values('Иванов Иван', 23, 'bsbo-01-22');

--тригерная функция ОБНОВЛЕНИЯ данных в соединенные таблицы studens, groups
-- триггер
create trigger update_st_group instead of insert on v_students_group 
for each row
execute procedure update_v_students_group();

--функция
CREATE FUNCTION update_v_students_group()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
	st_id INTEGER;
	g_id INTEGER;
BEGIN
	SELECT id INTO g_id FROM groups WHERE name = OLD.name;
	SELECT id INTO st_id FROM students WHERE fio = OLD.fio AND age = OLD.age;
	
	UPDATE students st SET
	fio = NEW.fio,
	age = NEW.age,
	group_id = g_id WHERE id = st.id;
	return NULL;
END;$$

UPDATE v_students_group SET fio='Bob', age=30, name='bsbo-01-22' where fio='Иванов Иван', age = 23, name='bsbo-01-22'

--материализованное представление 
create materialized view vm_students as
select s.fio, s.age, g.name from students s join groups g on s.group_id = g.id;
select * from vm_students; -- работает, в ней хранится набор данных
insert into students(fio, age, group_id) values ('Курочкин Апполон', 44, 1)
--мат. пред. не обновляется, апполона нет, решается с помощью refresh()
refresh materialized view vm_students;
select * from vm_students;





--курсор
DO
$$
DECLARE 
	cur REFCURSOR;
	g_id INTEGER;
BEGIN
	OPEN cur FOR SELECT id FROM groups;
	LOOP
	FETCH cur INTO g_id;
	IF NOT FOUND THEN EXIT;
	END IF;
	IF (g_id > 1) THEN
	DELETE FROM groups where id = g_id;
	END IF;
	END LOOP;
	CLOSE cur;
END;$$

select * from groups -- осталась группа с id = 1, остальные удалились
select * from students





------------------------------------------------------------------------
--Курсач
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;
GRANT USAGE ON SCHEMA public TO head;
GRANT ALL PRIVILEGES ON vm_executors TO head;
GRANT ALL PRIVILEGES ON vm_executors TO executor;
GRANT ALL PRIVILEGES ON executor_id_seq TO head;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_log TO executor;
ALTER MATERIALIZED VIEW vm_executors OWNER TO head; -- сработало

select * from contract
select * from executor
select * from head
SELECT full_name, id FROM head WHERE head_username =  'ivanov_ii'
DELETE FROM executor WHERE id = 8
INSERT INTO executor (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) VALUES
('TESTTESSTE', '+7(999)444-55-66', 'kuznetsova@example.com', 'ООО "СтройИнвест"', 'TESTTESSTETESTTESSTETESTTESSTE', 'TESTTESSTE', 2);

--Case запрос
SELECT 
    cn.id, 
    cn.contract_num, 
    cn.status, 
    cn.agreement_object, 
    h.full_name as head_name, 
    ex.full_name as executor_name, 
    CASE 
        WHEN ex.company_name IS NULL OR ex.company_name = '' THEN 'Компания отсутствует' 
        ELSE ex.company_name 
    END as company_name, 
    cn.conclusion_date, 
    cn.agreement_term 
FROM 
    contract cn 
JOIN 
    head h ON cn.head_id = h.id 
JOIN 
    executor ex ON cn.executor_id = ex.id;


-- view для таблицы head с case запросом
CREATE VIEW contract_view AS
SELECT 
    cn.id, 
    cn.contract_num, 
    cn.status, 
    cn.agreement_object, 
    h.full_name as head_name, 
    ex.full_name as executor_name, 
    CASE 
        WHEN ex.company_name IS NULL OR ex.company_name = '' THEN 'Компания отсутствует' 
        ELSE ex.company_name 
    END as company_name, 
    cn.conclusion_date, 
    cn.agreement_term 
FROM 
    contract cn 
JOIN 
    head h ON cn.head_id = h.id 
JOIN 
    executor ex ON cn.executor_id = ex.id;

DROP VIEW IF EXISTS contract_view
	
--функция для отображения view у executor
CREATE FUNCTION executor_contract_view(executor_username text) 
RETURNS TABLE (
    id INT,
    contract_num TEXT,
    status TEXT,
    agreement_object TEXT,
    head_name TEXT,
    executor_name TEXT,
    company_name TEXT,
    conclusion_date DATE,
    agreement_term INT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT cn.id, cn.contract_num, cn.status, cn.agreement_object, h.full_name as head_name, 
           ex.full_name as executor_name, ex.company_name, cn.conclusion_date, cn.agreement_term 
    FROM contract cn 
    JOIN head h ON cn.head_id = h.id 
    JOIN executor ex ON cn.executor_id = ex.id 
    WHERE ex.executor_username = executor_username;
END;
$$ LANGUAGE plpgsql;

-- Материализованное представление 
create materialized view vm_executors as
SELECT id, full_name, CASE
WHEN company_name = '' THEN 'Самозанятый'
ELSE company_name
END AS company_name FROM executor;

select * from vm_executors; -- работает, в ней хранится набор данных

refresh materialized view vm_executors;
select * from vm_executors;

--Роли
CREATE ROLE head;
CREATE ROLE executor;

-- Роль head может видеть и управлять всеми таблицами
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;
GRANT USAGE ON SCHEMA public TO head;

-- Роль executor может управлять только таблицами contract и extra_condition, contract_log, но видеть все таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON contract TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON extra_condition TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_log TO executor;


CREATE USER ivanov_ii PASSWORD '12345';
CREATE USER smirnov_av PASSWORD '12345';

GRANT head TO ivanov_ii;
GRANT executor TO smirnov_av;


--OLAP
CREATE TABLE contract_log (LIKE contract);
ALTER TABLE contract_log 
  ADD COLUMN action VARCHAR(1) NOT NULL,
  ADD COLUMN time TIMESTAMP NOT NULL;
  
CREATE OR REPLACE FUNCTION insert_contract_log()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP='INSERT'  THEN 
    INSERT INTO contract_log SELECT NEW.*, 'I', now();
  ELSEIF TG_OP= 'UPDATE' THEN 
    INSERT INTO contract_log SELECT NEW.*, 'U', now();
  ELSEIF TG_OP = 'DELETE' THEN
    INSERT INTO contract_log SELECT OLD.*, 'D', now();
  END IF;
  RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER cont_log AFTER INSERT OR UPDATE OR DELETE ON contract
  FOR EACH ROW 
  EXECUTE PROCEDURE insert_contract_log();

SELECT * FROM contract_log;
