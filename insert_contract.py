import psycopg2
import random
from faker import Faker

# Установите соединение с вашей базой данных PostgreSQL
def connect():
    try:
        connection = psycopg2.connect(user='postgres', 
                                      password='211229082206', 
                                      host="localhost", 
                                      port="5432", 
                                      database="sqlKurs")
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


# Генерация данных и вставка в таблицу contract
def insert_contracts():
    connection = connect()
    if connection:
        cursor = connection.cursor()
        fake = Faker()

        try:
            for _ in range(10000):
                contract_num = fake.unique.bothify(text='????-#####')
                conclusion_date = fake.date_between(start_date='-2y', end_date='today')
                agreement_term = fake.date_between(start_date=conclusion_date, end_date='+1y')
                agreement_object = fake.sentence(nb_words=4)
                document_scan = fake.file_name(extension="pdf")
                agreement_extras = fake.text(max_nb_chars=200)
                
                cursor.execute("SELECT id FROM head ORDER BY RANDOM() LIMIT 1")
                head_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM executor ORDER BY RANDOM() LIMIT 1")
                executor_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO contract (
                        contract_num, conclusion_date, agreement_term, agreement_object, status, document_scan, executor_id, head_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    contract_num, conclusion_date, agreement_term, agreement_object, 'Создан', document_scan, executor_id, head_id
                ))

                # Получение id последнего вставленного договора
                cursor.execute("SELECT currval(pg_get_serial_sequence('contract','id'))")
                contract_id = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO extra_condition (
                        agreement_extras, contract_id
                    ) VALUES (%s, %s)
                """, (agreement_extras, contract_id))

            connection.commit()
            print("10000 договоров успешно добавлены.")
        except Exception as error:
            print("Ошибка при вставке данных в PostgreSQL:", error)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    insert_contracts()
