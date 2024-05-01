import psycopg2

def connect(username, password):
    try:
        connection = psycopg2.connect(user=username, 
                                      password=password, 
                                      host="localhost", 
                                      port="5432", 
                                      database="sqlKurs")
        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
