#TODO Use heroku scheduler to clear table monday at 9 am
#TODO update sql queries
#TODO update results.html
#TODO get better css

from flask import Flask, jsonify, request, render_template
import json
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cursor = conn.cursor()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

@app.route('/index', methods=['GET', 'POST'])
def index():
    
    if request.method == "POST":
        data = request.get_json()

        subject = data['subject']
        ids = data['ids']
        
        for idNum in ids:
            query = 'UPDATE assignments SET "{}" = false WHERE "ID" = {}'.format(subject, idNum)
            cursor.execute(query)
        conn.commit()
        
        return json.dumps(True)
    
    return render_template('index.html')


@app.route('/submitted')
def submitThanks():
    return render_template("submitted.html")

@app.route('/results')
def view():
    cursor.execute("SELECT * FROM assignments")
    passResult = cursor.fetchall()
    return render_template('results.html', result = passResult)

if __name__ == '__main__':
    app.run()
    cursor.close()
    conn.close()
