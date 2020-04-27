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

        cursor.execute("UPDATE votes SET votenum = (votenum + 1) WHERE name = '{}'".format(data))
        
        return json.dumps(True)
    
    return render_template('index.html')


@app.route('/submitted')
def submitThanks():
    return render_template("submitted.html")

@app.route('/results')
def view():
    cursor.execute("SELECT * FROM votes")
    return render_template('results.html', result = cursor.fetchall())

if __name__ == '__main__':
    app.run()
    cursor.close()
    conn.close()
