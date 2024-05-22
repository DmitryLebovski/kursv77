CREATE TABLE head(
	id serial PRIMARY KEY,
	full_name varchar(100) NOT NULL,
	phone_number varchar(18),
	email varchar(100) NOT NULL,
	head_username VARCHAR(50) not NULL
);

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
);

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
);

CREATE TABLE extra_condition(
	id serial PRIMARY KEY,
	agreement_extras TEXT,
	contract_id INT,
	FOREIGN KEY (contract_id) REFERENCES contract(id)
);

select * from contract

INSERT INTO head (full_name, phone_number, email, head_username) 
VALUES 
    ('Сергеев Сидор Иванович', '+7(911)111-11-11', 'ivanov@example.com', 'sergeev_username'),
    ('Петров Игорь Петрович', '+7(922)222-22-22', 'petrov@example.com', 'petrov_username'),
    ('Сидоров Сидор Сидорович', '+7(933)333-33-33', 'sidorov@example.com', 'sidorov_username'),
    ('Козлов Петр Козлович', '+7(944)444-44-44', 'kozlov@example.com', 'kozlov_username');

INSERT INTO executor (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) 
VALUES 
    ('Локсин Алексей Владимирович', '+7(955)555-55-55', 'smirnov@example.com', 'Company A', 'Агент', 'loxin_username', 1),
    ('Федоров Артем Александрович', '+7(966)666-66-66', 'fedorov@example.com', 'Company B', 'Директор', 'fedorov_username', 3),
    ('Волков Дмитрий Николаевич', '+7(977)777-77-77', 'volkov@example.com', 'Company C', 'Финансист', 'volkov_username', 5),
    ('Михайлов Егор Сергеевич', '+7(988)888-88-88', 'mikhailov@example.com', 'Company D', 'Зам. Руководителя', 'mikhailov_username', 6);

INSERT INTO contract (contract_num, conclusion_date, agreement_term, agreement_object, status, executor_id, head_id) 
VALUES 
    ('КТ-1', '2024-05-01', '2024-06-01', 'Поставка оборудования для офиса', 'В процессе', 1, 5),
    ('КТ-12', '2024-05-02', '2024-06-02', 'Проведение маркетинговой кампании', 'Озд', 1, 6),
    ('КТ-13', '2024-05-03', '2024-06-03', 'Разработка программного обеспечения', 'Отменен', 3, 1),
    ('КТ-14', '2024-05-04', '2024-06-04', 'Организация мероприятия', 'В процессе', 1, 1),
    ('КТ-15', '2024-05-05', '2024-06-05', 'Поставка строительных материалов', 'Завершен', 2, 1),
    ('КТ-16', '2024-05-06', '2024-06-06', 'Проведение тренингов для персонала', 'Отменен', 3, 2),
    ('КТ-17', '2024-05-07', '2024-06-07', 'Подготовка дизайн-проекта интерьера', 'В процессе', 2, 4),
    ('КТ-18', '2024-05-08', '2024-06-08', 'Изготовление и доставка рекламных материалов', 'Завершен', 2, 5),
    ('КТ-19', '2024-05-09', '2024-06-09', 'Проведение аудита финансовой отчетности', 'Отменен', 3, 1),
    ('КТ-110', '2024-05-10', '2024-06-10', 'Поставка продуктов питания и напитков', 'В процессе', 17, 4),
    ('КТ-111', '2024-05-11', '2024-06-11', 'Разработка программного обеспечения', 'Завершен', 18, 3),
    ('КТ-112', '2024-05-12', '2024-06-12', 'Проведение аудита финансовой отчетности', 'Отменен', 3, 5),
    ('КТ-113', '2024-05-13', '2024-06-13', 'Организация мероприятия', 'В процессе', 17, 1),
    ('КТ-114', '2024-05-14', '2024-06-14', 'Поставка продуктов питания и напитков', 'Завершен', 19, 2),
    ('КТ-115', '2024-05-15', '2024-06-15', 'Изготовление и доставка рекламных материалов', 'Отменен', 3, 2),
    ('КТ-116', '2024-05-16', '2024-06-16', 'Разработка программного обеспечения', 'В процессе', 20, 4),
    ('КТ-117', '2024-05-17', '2024-06-17', 'Организация мероприятия', 'Завершен', 20, 3),
    ('КТ-118', '2024-05-18', '2024-06-18', 'Изготовление и доставка рекламных материалов', 'Отменен', 2, 6),
    ('КТ-119', '2024-05-19', '2024-06-19', 'Организация мероприятия', 'В процессе', 1, 7),
    ('КТ-120', '2024-05-20', '2024-06-20', 'Проведение аудита финансовой отчетности', 'Завершен', 1, 4);

--Курсач
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;
GRANT ALL PRIVILEGES ON vm_executors TO head;
GRANT ALL PRIVILEGES ON executor_id_seq TO head;
GRANT ALL PRIVILEGES ON contract_view TO head;
ALTER MATERIALIZED VIEW vm_executors OWNER TO head;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;
ALTER ROLE head WITH CREATEROLE;
GRANT USAGE, SELECT ON SEQUENCE contract_id_seq TO head;
GRANT USAGE, SELECT ON SEQUENCE extra_condition_id_seq TO head;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_info_view_status TO head;

GRANT ALL PRIVILEGES ON vm_executors TO executor;
GRANT ALL PRIVILEGES ON contract_info_view_all TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_log TO executor;
GRANT ALL PRIVILEGES ON contract_view TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON extra_condition TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON executor TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_log TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON contract_info_view_status TO executor;

SELECT full_name, id FROM head WHERE head_username =  'ivanov_ii'
DELETE FROM executor WHERE id = 8
INSERT INTO executor (full_name, phone_number, email, company_name, executor_position, executor_username, head_id) VALUES
('TESTTESSTE', '+7(999)444-55-66', 'kuznetsova@example.com', 'ООО "СтройИнвест"', 'TESTTESSTETESTTESSTETESTTESSTE', 'TESTTESSTE', 2);

-- view для таблицы head с case запросом
CREATE VIEW contract_view AS
SELECT 
    cn.id, 
    cn.contract_num as contract_n, 
    cn.status as status, 
    cn.agreement_object as agr_obj, 
    h.full_name as head_name, 
    ex.full_name as executor_name, 
    CASE 
        WHEN ex.company_name IS NULL OR ex.company_name = '' THEN 'Компания отсутствует' 
        ELSE ex.company_name
    END as company_n, 
    cn.conclusion_date as conc_d, 
    cn.agreement_term as agr_d 
FROM 
    contract cn 
JOIN 
    head h ON cn.head_id = h.id 
JOIN 
    executor ex ON cn.executor_id = ex.id;
	
CREATE INDEX idx_contract_head_id ON contract(head_id);
CREATE INDEX idx_contract_ex_id ON contract(executor_id);

select * from contract
DELETE FROM extra_condition where id between 2000 and 4000
DELETE FROM contract where id between 2070 and 3000

	
DROP VIEW IF EXISTS contract_view

SELECT * FROM contract_view;

-- Функция отображения конракта для ContractWindow
CREATE OR REPLACE FUNCTION contract_info_view(contractid INT)
RETURNS TABLE (
    "Номер договора" VARCHAR(50),
    "Наименование договора" TEXT,
    "ФИО руководителя" VARCHAR(100),
    "Номер телефона руководителя" VARCHAR(18),
    "Почта руководителя" VARCHAR(100),
    "ФИО агента" VARCHAR(100),
    "Номер телефона агента" VARCHAR(18),
    "Почта агента" VARCHAR(100),
    "Позиция агента" VARCHAR(100),
    "Компания" VARCHAR(100),
    "Дата заключения" DATE,
    "Срок действия" DATE,
    "Скан документа" TEXT,
    "Дополнительные условия" TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cn.contract_num,
        cn.agreement_object,
        h.full_name,
        h.phone_number,
        h.email,
        ex.full_name,
        ex.phone_number,
        ex.email,
        ex.executor_position,
        ex.company_name,
        cn.conclusion_date,
        cn.agreement_term,
        cn.document_scan,
        exc.agreement_extras
    FROM 
        contract cn
    JOIN 
        head h ON cn.head_id = h.id
    JOIN 
        executor ex ON cn.executor_id = ex.id
    LEFT JOIN 
        extra_condition exc ON cn.id = exc.contract_id
    WHERE 
        cn.id = contractid;
END;
$$ LANGUAGE plpgsql;

-- Многотабличный VIEW, с возможностью его обновления 
CREATE OR REPLACE VIEW contract_info_view_all AS
SELECT 
    cn.contract_num AS "Номер договора", 
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
    exc.agreement_extras AS "Дополнительные условия",
	cn.id
FROM 
    contract cn
JOIN 
    head h ON cn.head_id = h.id
JOIN 
    executor ex ON cn.executor_id = ex.id
LEFT JOIN 
    extra_condition exc ON cn.id = exc.contract_id;
	
CREATE INDEX idx_contract_id ON contract(id);
CREATE INDEX idx_contract_head_id ON contract(head_id);
CREATE INDEX idx_contract_executor_id ON contract(executor_id);
CREATE INDEX ix_head_id_brin ON head USING brin (id);
CREATE INDEX ix_executor_to_head_id_brin ON executor USING brin (head_id);
CREATE INDEX ix_executor_id_brin ON executor USING brin (id);
CREATE INDEX idx_contract_id ON contract(id);

DROP INDEX idx_contract_id;
DROP INDEX idx_contract_head_id;
DROP INDEX idx_contract_executor_id;
DROP INDEX ix_head_id_brin;
DROP INDEX ix_executor_id_brin;
DROP INDEX idx_gin_ext_cond;
DROP INDEX idx_head_username;

CREATE INDEX idx_agr_extr ON extra_condition USING hash(agreement_extras)
EXPLAIN SELECT c.contract_num, c.status FROM contract c LEFT JOIN extra_condition ec on ec.contract_id = c.id WHERE ec.agreement_extras = 'Гарантийное обслуживание на 2 года'

CREATE INDEX idx_head_id ON head(id)
EXPLAIN SELECT h.full_name, ex.full_name FROM executor ex JOIN head h ON h.id = ex.head_id WHERE h.head_username = 'ivanov_ii'

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_gin_ex_name ON executor USING gin(full_name gin_trgm_ops);
EXPLAIN ANALYSE SELECT full_name FROM executor WHERE full_name LIKE 'Иванов'


CREATE INDEX idx_contract_agr_t ON contract USING brin(agreement_term)
EXPLAIN ANALYZE SELECT agreement_term from contract

CREATE INDEX idx_executor_id ON executor USING brin(id)
EXPLAIN SELECT ex.full_name FROM executor ex JOIN contract c ON ex.id = c.executor_id WHERE ex.id > 100


SELECT * FROM contract
INSERT INTO contract (
                        contract_num, conclusion_date, agreement_term, agreement_object, status, document_scan, executor_id, head_id
                    ) VALUES ('test', '2024-01-01', '2025-01-03', 'test', 'test', 'test', 3, 5)

CREATE INDEX idx_contract_conclusion_date_brin ON contract USING brin (conclusion_date);
EXPLAIN ANALYZE SELECT h.full_name FROM contract c JOIN head h ON c.head_id = h.id WHERE c.conclusion_date = '2023-01-01';

SELECT indexname
FROM pg_indexes
WHERE tablename = 'contract' AND indexdef LIKE '%agreement_term%';

DROP index idx_gin_agr_ex_desc;

--extra_condition agreement_extras
-- VIEW для обновления статуса:
CREATE OR REPLACE VIEW contract_info_view_status AS
SELECT 
    cn.contract_num AS "Номер договора", 
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
    exc.agreement_extras AS "Дополнительные условия",
	cn.id,
	cn.status
FROM 
    contract cn
JOIN 
    head h ON cn.head_id = h.id
JOIN 
    executor ex ON cn.executor_id = ex.id
LEFT JOIN 
    extra_condition exc ON cn.id = exc.contract_id;

-- функция обновления статуса для "Согласован" и "Закрыт"
CREATE OR REPLACE FUNCTION update_contract_info_status (contract_id_param INT, new_status_param VARCHAR)
RETURNS VOID AS $$
BEGIN
	UPDATE contract_info_view_status
	SET status = new_status_param
	WHERE id = contract_id_param;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE RULE "update_contract_info_status"
AS ON UPDATE TO  contract_info_view_status
DO INSTEAD (
	UPDATE contract
	SET status = NEW.status
	WHERE id = new.id;
);

--функция для отображения таблицы у executor
DROP FUNCTION contract_view_executor(character varying)
CREATE OR REPLACE FUNCTION contract_view_executor(p_executor_username VARCHAR)
RETURNS TABLE (
    id INT,
    contract_num VARCHAR(50),
    status VARCHAR(100),
    agreement_object TEXT,
    head_name VARCHAR(100),
    executor_name VARCHAR(100),
    company_name VARCHAR(100),
    conclusion_date DATE,
    agreement_term DATE
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cn.id, 
        cn.contract_num, 
        cn.status, 
        cn.agreement_object, 
        h.full_name AS head_name, 
        ex.full_name AS executor_name, 
        ex.company_name, 
        cn.conclusion_date, 
        cn.agreement_term
    FROM 
        contract cn
    JOIN 
        head h ON cn.head_id = h.id
    JOIN 
        executor ex ON cn.executor_id = ex.id
    WHERE 
        ex.executor_username = p_executor_username;
END;
$$ LANGUAGE plpgsql;

-- Материализованное представление 
create materialized view vm_executors as
SELECT id, full_name, 
CASE
   WHEN company_name = '' THEN 'Самозанятый'
   ELSE company_name
END AS company_name 
FROM executor
ORDER BY full_name ASC;

select * from vm_executors; 

refresh materialized view vm_executors;
select * from vm_executors;

-- Триггер и фукнция на обновление contract
CREATE OR REPLACE FUNCTION check_agreement_term()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.agreement_term < NEW.conclusion_date THEN
        RAISE EXCEPTION 'Срок действия должен быть позже даты заключения. Номер договора с ошибкой: %', NEW.contract_num;
    END IF;
	
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_agreement_term_update
BEFORE UPDATE ON contract
FOR EACH ROW
EXECUTE FUNCTION check_agreement_term();

CREATE TRIGGER trigger_check_agreement_term_insert
BEFORE INSERT ON contract
FOR EACH ROW
EXECUTE FUNCTION check_agreement_term();

-- Триггер на добавление в таблицу executor
CREATE OR REPLACE FUNCTION check_unique_executor_usrn()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM executor WHERE executor_username = NEW.executor_username) THEN
        RAISE EXCEPTION 'Исполнитель с таким "Именем пользователя" (%), уже существует.', NEW.executor_username;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_unique_executor_usrn
BEFORE INSERT ON executor
FOR EACH ROW
EXECUTE FUNCTION check_unique_executor_usrn();

-- Триггер на обновление head
CREATE OR REPLACE FUNCTION check_email_format()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.email IS NOT NULL AND NEW.email !~* '.*@.*' THEN
        RAISE EXCEPTION 'Поле "Почта" должно содержать символ @. Значение: %', NEW.email;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_check_email_format_h
BEFORE UPDATE ON head
FOR EACH ROW
EXECUTE FUNCTION check_email_format();

CREATE TRIGGER trigger_check_email_format_ex
BEFORE UPDATE ON executor
FOR EACH ROW
EXECUTE FUNCTION check_email_format();


-- Очень странный триггер на добавление/обновление agreement_extras
CREATE OR REPLACE FUNCTION check_agreement_extras()
RETURNS TRIGGER AS $$
DECLARE
    forbidden_words TEXT[] := ARRAY['взятка', 'штраф', 'отказ'];
    word TEXT;
BEGIN
    FOREACH word IN ARRAY forbidden_words LOOP
        IF NEW.agreement_extras ILIKE '%' || word || '%' THEN
            RAISE EXCEPTION 'Поле "Дополнительные условия" содержит запрещенное слово: %', word, NEW.agreement_extras;
        END IF;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_agreement_extras_update
BEFORE UPDATE ON extra_condition
FOR EACH ROW
EXECUTE FUNCTION check_agreement_extras();

-- Подзапрос SELECT
UPDATE head AS h
SET 
	full_name = %s,
	phone_number = %s,
	email = %s
WHERE 
	h.id = (SELECT head_id FROM contract WHERE contract_num = %s)
	
-- Подзапрос FROM
SELECT
    c.id AS contract_id,
    c.contract_num,
    h.full_name AS head_full_name,
    e.full_name AS executor_full_name
FROM
    (SELECT * FROM contract WHERE status = 'Создан') c
LEFT JOIN head h ON c.head_id = h.id
LEFT JOIN executor e ON c.executor_id = e.id
LEFT JOIN extra_condition ec ON c.id = ec.contract_id
ORDER BY c.contract_num ASC;

-- Подзапрос WHERE
SELECT h.full_name, c.agreement_term
FROM head h
JOIN contract c ON h.id = c.head_id
WHERE h.id IN (SELECT head_id FROM contract WHERE status = 'Закрыт');

-- Скалярная функция
CREATE OR REPLACE FUNCTION count_contracts_by_executor(ex_usr VARCHAR)
RETURNS INT
AS $$
DECLARE
    contract_count INT;
BEGIN
    SELECT COUNT(*)
    INTO contract_count
    FROM contract cn
    JOIN executor ex ON cn.executor_id = ex.id
    WHERE ex.executor_username = ex_usr;

    RETURN contract_count;
END;
$$ LANGUAGE plpgsql;

select * from count_contracts_by_executor('smirnov_av')

-- Векторная функция
CREATE OR REPLACE FUNCTION get_contracts_by_executor(ex_usr VARCHAR)
RETURNS TABLE (
    id INT,
    contract_num VARCHAR(50),
    status VARCHAR(100),
    agreement_object TEXT,
    head_name VARCHAR(100),
    executor_name VARCHAR(100),
    company_name VARCHAR(100),
    conclusion_date DATE,
    agreement_term DATE
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cn.id, 
        cn.contract_num, 
        cn.status, 
        cn.agreement_object, 
        h.full_name AS head_name, 
        ex.full_name AS executor_name, 
        ex.company_name, 
        cn.conclusion_date, 
        cn.agreement_term
    FROM 
        contract cn
    JOIN 
        head h ON cn.head_id = h.id
    JOIN 
        executor ex ON cn.executor_id = ex.id
    WHERE 
        ex.executor_username = ex_usr;
END;
$$ LANGUAGE plpgsql;

select * from get_contracts_by_executor('smirnov_av')

-- Курсор на обновление всем agreement_term на месяц
CREATE OR REPLACE FUNCTION update_agreement_term()
RETURNS VOID AS $$
DECLARE
    contract_rec RECORD;
    contract_cursor CURSOR FOR SELECT id, agreement_term FROM contract;
BEGIN
    OPEN contract_cursor;
    LOOP
        FETCH contract_cursor INTO contract_rec;
        EXIT WHEN NOT FOUND;
        
        UPDATE contract
        SET agreement_term = contract_rec.agreement_term + INTERVAL '1 month'
        WHERE id = contract_rec.id;
    END LOOP;

    CLOSE contract_cursor;
END;
$$ LANGUAGE plpgsql;

select update_agreement_term();
select * from contract;

-- Запрос содержащий HAVING
DROP FUNCTION get_heads_with_contract_count(integer)

CREATE OR REPLACE FUNCTION get_heads_with_contract_count(min_contracts INT)
RETURNS TABLE (
    head_id INT,
    head_name VARCHAR(100),
    contract_count BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id AS head_id,
        h.full_name AS head_name,
        COUNT(c.id) AS contract_count
    FROM 
        head h
    JOIN 
        contract c ON h.id = c.head_id
    GROUP BY 
        h.id, h.full_name
    HAVING 
        COUNT(c.id) > min_contracts;
END;
$$ LANGUAGE plpgsql;
--список руководителей, у которых количество контрактов больше указанного значения

SELECT * FROM get_heads_with_contract_count(2);

-- ANY
SELECT 
    id,
    contract_num,
    conclusion_date,
    status
FROM 
    contract
WHERE 
    conclusion_date > ANY (SELECT conclusion_date FROM contract WHERE status = 'Закрыт');
--все контракты, у которых дата заключения больше любой даты заключения контрактов со статусом "Закрыт"

--ALL
SELECT 
    h.id,
    h.full_name,
    h.phone_number,
    h.email,
    h.head_username
FROM 
    head h
WHERE 
    'Закрыт' = ALL (SELECT c.status FROM contract c WHERE c.head_id = 6);

SELECT * from contract

--Коррелированные подзапросы
SELECT 
    h.id,
    h.full_name,
    h.phone_number,
    h.email,
    h.head_username
FROM 
    head h
WHERE 
    EXISTS (
        SELECT 1
        FROM contract c
        WHERE c.head_id = h.id AND c.status = 'Создан'
    );
	
CREATE OR REPLACE FUNCTION get_table_status
	
SELECT 
    ex.id,
    ex.full_name,
    ex.phone_number,
    ex.email,
    ex.company_name,
    ex.executor_position,
    ex.executor_username
FROM 
    executor ex
WHERE 
    (
        SELECT COUNT(*)
        FROM contract c
        WHERE c.executor_id = ex.id
    ) > 5;

SELECT 
    c.contract_num,
    c.agreement_object,
    c.status
FROM contract c
WHERE EXISTS (SELECT 1 
              FROM extra_condition ec 
              WHERE ec.contract_id = c.id);

SELECT * FROM executor
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


--Функция добавления агента
CREATE OR REPLACE FUNCTION insert_user(fn varchar, pn varchar, em varchar, cpnm varchar, exps varchar, exus varchar, h_id INTEGER)
RETURNS VOID AS $$
BEGIN
	INSERT INTO executor 
	(full_name, phone_number, email, company_name, executor_position, executor_username, head_id) 
	VALUES (fn, pn, em, cpnm, exps, exus, h_id);
END; 
$$ LANGUAGE plpgsql;

--Функция создания агента как пользователя
CREATE OR REPLACE FUNCTION create_user(usnm varchar, pssw varchar)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE USER %I PASSWORD %L', usnm, pssw);
    EXECUTE format('GRANT executor TO %I', usnm);
END;
$$ LANGUAGE plpgsql;

--Функция удаления агента 
CREATE OR REPLACE FUNCTION drop_user(ex_id INT, ex_usnm VARCHAR)
RETURNS VOID AS $$
BEGIN
	EXECUTE format('DROP USER %I', ex_usnm);
    DELETE FROM executor WHERE id = ex_id;
END;
$$ LANGUAGE plpgsql;

--Функция добавления контракта
CREATE OR REPLACE FUNCTION add_contract_and_update_head(
    p_contract_num VARCHAR,
	p_agreement_object TEXT,
	p_head_full_name VARCHAR,
    p_head_phone VARCHAR,
    p_head_email VARCHAR,
	p_executor_id INT,
    p_head_id INT,
    p_conclusion_date DATE,
    p_agreement_term DATE,
	p_document_scan VARCHAR,
    p_agreement_extras TEXT
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO contract (
        contract_num, conclusion_date, agreement_term, agreement_object, status, document_scan, executor_id, head_id
    ) VALUES (
        p_contract_num, p_conclusion_date, p_agreement_term, p_agreement_object, 'Создан', p_document_scan, p_executor_id, p_head_id
    );
    INSERT INTO extra_condition (
        agreement_extras, contract_id
    ) VALUES (
        p_agreement_extras, (SELECT id FROM contract WHERE contract_num = p_contract_num)
    );
    UPDATE head
    SET
        full_name = p_head_full_name,
        phone_number = p_head_phone,
        email = p_head_email
    WHERE
        id = p_head_id;
END;
$$ LANGUAGE plpgsql;

-- Отдельная хранимая процедура - создание контракта
CREATE OR REPLACE PROCEDURE add_contract_final_procedure(
    p_contract_num VARCHAR,
    p_agreement_object TEXT,
    p_head_full_name VARCHAR,
    p_head_phone VARCHAR,
    p_head_email VARCHAR,
    p_executor_id INT,
    p_head_id INT,
    p_conclusion_date DATE,
    p_agreement_term DATE,
    p_document_scan VARCHAR,
    p_agreement_extras TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    contract_id INT; 
	v_contract_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM contract WHERE contract_num = p_contract_num) INTO v_contract_exists;
	
	IF (v_contract_exists) THEN
		ROLLBACK;
	ELSE
		INSERT INTO contract (
			contract_num, conclusion_date, agreement_term, agreement_object, status, document_scan, executor_id, head_id
		) VALUES (
			p_contract_num, p_conclusion_date, p_agreement_term, p_agreement_object, 'Создан', p_document_scan, p_executor_id, p_head_id
		)
		RETURNING id INTO contract_id;

		INSERT INTO extra_condition (
			agreement_extras, contract_id
		) VALUES (
			p_agreement_extras, contract_id
		);

		UPDATE head
		SET
			full_name = p_head_full_name,
			phone_number = p_head_phone,
			email = p_head_email
		WHERE
			id = p_head_id;

		COMMIT;
	END IF;
END;
$$;

 SELECT EXISTS(SELECT 1 FROM contract WHERE contract_num = 'ЖДВАОЬЖВЫДА')


call add_contract_final_procedure('ЖДВАОЬЖВЫДА', 'ИМЬТЧСИМЬЧСМЬСЧ', 'ИМЬТЧСИМЬЧСМЬСЧ', 'TesИМЬТЧСИМЬЧСМЬСЧt', 'Test', 1, 2,'2024-01-01','2025-01-01', '', 'Test')

select * from contract
select * from head


DROP PROCEDURE add_contract_procedure;

DROP TRIGGER trigger_check_agreement_term_insert on contract;
DROP TRIGGER trigger_check_agreement_term_update on contract;
DROP TRIGGER trigger_check_unique_executor_usrn on executor;
DROP TRIGGER trigger_check_email_format_h on head;
DROP TRIGGER trigger_check_email_format_ex on executor;
DROP TRIGGER trigger_check_agreement_extras_update on extra_condition;


-- Функция удаления договора
CREATE OR REPLACE FUNCTION delete_contract(p_contract_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM extra_condition WHERE contract_id = p_contract_id;
    DELETE FROM contract WHERE id = p_contract_id;
END;
$$ LANGUAGE plpgsql;


--Функция обновления договора для роли Агент
CREATE OR REPLACE FUNCTION update_contract_executor(
    p_contract_id INT,
	p_contract_name VARCHAR,
	p_contract_agr_obj TEXT,
    p_conclusion_date DATE,
    p_agreement_term DATE,
    p_document_scan TEXT,
    p_executor_full_name VARCHAR,
    p_executor_phone VARCHAR,
    p_executor_email VARCHAR,
    p_executor_position VARCHAR,
    p_company_name VARCHAR,
    p_agreement_extras TEXT
)
RETURNS VOID AS $$
BEGIN
    UPDATE contract
    SET 
		contract_num = p_contract_name,
		agreement_object = p_contract_agr_obj,
        conclusion_date = p_conclusion_date,
        agreement_term = p_agreement_term,
        document_scan = p_document_scan
    WHERE id = p_contract_id;

    UPDATE executor
    SET 
        full_name = p_executor_full_name,
        phone_number = p_executor_phone,
        email = p_executor_email,
        executor_position = p_executor_position,
        company_name = p_company_name
    WHERE id = (SELECT executor_id FROM contract WHERE id = p_contract_id);

    UPDATE extra_condition
    SET 
        agreement_extras = p_agreement_extras
    WHERE contract_id = p_contract_id;
END;
$$ LANGUAGE plpgsql;

--Функция обновления договора в роли Руководитель
CREATE OR REPLACE FUNCTION update_contract_head(
    p_contract_id INT,
    p_contract_num VARCHAR,
    p_status VARCHAR,
    p_agreement_object TEXT,
    p_conclusion_date DATE,
    p_agreement_term DATE,
    p_document_scan TEXT,
    p_executor_full_name VARCHAR,
    p_head_full_name VARCHAR,
    p_head_phone VARCHAR,
    p_head_email VARCHAR,
    p_agreement_extras TEXT
)
RETURNS VOID AS $$
BEGIN
    UPDATE contract
    SET 
        contract_num = p_contract_num,
        status = p_status,
        agreement_object = p_agreement_object,
        conclusion_date = p_conclusion_date,
        agreement_term = p_agreement_term,
        document_scan = p_document_scan,
        executor_id = (SELECT id FROM executor WHERE full_name = p_executor_full_name)
    WHERE id = p_contract_id;

    UPDATE head
    SET 
        full_name = p_head_full_name,
        phone_number = p_head_phone,
        email = p_head_email
    WHERE id = (SELECT head_id FROM contract WHERE id = p_contract_id);

    UPDATE extra_condition
    SET 
        agreement_extras = p_agreement_extras
    WHERE contract_id = p_contract_id;
END;
$$ LANGUAGE plpgsql;

SELECT h.full_name, h.phone_number, h.email FROM head h WHERE h.id = 1
select * from executor


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
