CREATE ROLE head;
CREATE ROLE executor;

-- Роль head может видеть и управлять всеми таблицами
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO head;

-- Роль executor может управлять только таблицами contract и extra_condition, но видеть все таблицы
GRANT SELECT, INSERT, UPDATE, DELETE ON contract TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON extra_condition TO executor;
GRANT SELECT, INSERT, UPDATE, DELETE ON executor TO executor;
GRANT SELECT ON head TO executor;

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
	document_scan BYTEA,
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

-- Данные для таблицы "contract"
INSERT INTO contract (contract_num, conclusion_date, agreement_term, agreement_object, status, executor_id, head_id) VALUES ('КТ-005', '2000-02-10', '2025-08-10', 'без доп условий', 'Закрыт', 1, 3);

('КТ-001', '2024-04-15', '2024-10-15', 'Строительство жилого комплекса', 'Действующий', 1, 1),
('КТ-002', '2024-03-20', '2024-09-20', 'Разработка программного обеспечения', 'В ожидании', 2, 2),
('КТ-003', '2024-02-10', '2024-08-10', 'Поставка оборудования', 'Закрыт', 3, 3);
('КТ-004', '2000-02-10', '2025-08-10', 'Проверка удаления', 'Закрыт', 1, 3);


-- Данные для таблицы "extra_condition"
INSERT INTO extra_condition (agreement_extras, contract_id) VALUES 
('Дополнительные работы по благоустройству прилегающей территории', 1),
('Обязательное обучение сотрудников', 2),
('Гарантийное обслуживание на 2 года', 3);

SELECT * FROM head
SELECT * FROM executor
SELECT * FROM contract
SELECT * FROM extra_condition

DELETE from extra_condition where contract_id=(select id from contract where contract_num='апдейт')
DELETE from contract where id'апдейт'

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


