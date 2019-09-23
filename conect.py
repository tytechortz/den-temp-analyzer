import psycopg2
from psycopg2 import pool
# import app1.py

try:

    postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20,user = "postgres",
                                                password = "1234",
                                                host = "localhost",
                                                database = "denver_temps")

    if(postgreSQL_pool):
            print("Connection pool created successfully")


 # Use getconn() to Get Connection from connection pool
    norms_connection  = postgreSQL_pool.getconn()
    temps_connection = postgreSQL_pool.getconn()

    if(norms_connection):
        print("successfully recived connection from connection pool ")
        norms_cursor = norms_connection.cursor()
        norms_cursor.execute("select * from dly_max_norm")
        norm_records = norms_cursor.fetchall()
        norms_cursor.close()

        temps_cursor = temps_connection.cursor()
        temps_cursor.execute('SELECT min(ALL "TMIN") AS rec_low, to_char("DATE"::TIMESTAMP,\'MM-DD\') AS day FROM temps GROUP BY day ORDER BY day ASC')
        temp_records = temps_cursor.fetchall()
        temps_cursor.close()  

        #Use this method to release the connection object and send back to connection pool
        print("Put away a PostgreSQL connection")
        postgreSQL_pool.putconn(norms_connection)
        postgreSQL_pool.putconn(temps_connection)

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while connecting to PostgreSQL", error)

finally:
    #closing database connection.
    # use closeall method to close all the active connection if you want to turn of the application
    if (postgreSQL_pool):
        postgreSQL_pool.closeall
    print("PostgreSQL connection pool is closed")