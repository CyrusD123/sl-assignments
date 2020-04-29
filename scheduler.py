import datetime

if (datetime.datetime.today().weekday() == 0):
    import os
    import psycopg2

    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')

    cursor = conn.cursor()

    subject_arr = ["Science", "Math", "English", "Social Studies", "World Language", "PE/Health/DE", "Special Education", "Music", "Art", "Family Consumer Science", "Technology Education", "Business", "Guidance Notes", "LCTI", "Supports"]
    for subject in subject_arr:
        cursor.execute('UPDATE assignments SET "{}" = true'.format(subject))


    conn.commit()

    cursor.close()
    conn.close()