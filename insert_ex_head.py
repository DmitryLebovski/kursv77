import psycopg2
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

# Генерация данных и вставка в таблицу executor
def insert_executors():
    connection = connect()
    if connection:
        cursor = connection.cursor()
        fake = Faker('ru_RU')  # Установка локали на русский язык
        
        try:
            for i in range(3000):
                full_name = fake.name()
                phone_number = f"+7(9{fake.numerify('##')}){fake.numerify('###-##-##')}"
                email = fake.email()
                executor_username = fake.user_name() + f'test{i}'
                position = 'Агент'
                company_name = fake.company()
                cursor.execute("SELECT id FROM head ORDER BY RANDOM() LIMIT 1")
                head_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO executor (full_name, phone_number, email, executor_username, company_name, executor_position, head_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                    (full_name, phone_number, email, executor_username, company_name, position, head_id))
                    
            
            # for _ in range(3000):
            #     full_name = fake.name()
            #     phone_number = f"+7(9{fake.numerify('##')}){fake.numerify('###-##-##')}"
            #     email = fake.email()
            #     head_username = fake.user_name()
                
            #     cursor.execute("INSERT INTO head (full_name, phone_number, email, head_username) VALUES (%s, %s, %s, %s)",
            #                         (full_name, phone_number, email, head_username))

            connection.commit()
            print("записи успешно добавлены в таблицу head.")
        except Exception as error:
            print("Ошибка при вставке данных в PostgreSQL:", error)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    insert_executors()
