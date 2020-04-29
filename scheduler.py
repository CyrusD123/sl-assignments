import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cursor = conn.cursor()

subject_arr = []


cursor.execute('UPDATE assignments SET * = true WHERE * = false')
conn.commit()

cursor.close()
conn.close()