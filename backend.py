#TODO Use heroku scheduler to clear table monday at 9 am
#TODO Add an about page
#TODO get better css
    #TODO add a sidebar with "SLSD Assignment Completion Database" next to it on non-home pages
    #TODO change form styling (radios, text spacing, submit button, will omit results button once sidebar is in)
    #TODO add a favicon

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
    cursor.execute('SELECT * FROM assignments ORDER BY "ID" ASC')
    passResult = cursor.fetchall()
    return render_template('results.html', result = passResult)

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run()
    cursor.close()
    conn.close()
