#TODO add a favicon

from flask import Flask, jsonify, request, render_template
import json
import os
import psycopg2

# Connect to database using heroku environment variable DATABASE_URL
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')# Heroku requires SSL

# Create a cursor to execute queries
cursor = conn.cursor()

# Initialize flask app
app = Flask(__name__)

# / and /index lead to same page
@app.route('/', methods=['GET', 'POST', 'GETPASSWORD'])

@app.route('/index', methods=['GET', 'POST', 'GETPASSWORD'])
def index():
    
    # On form submission:
    if request.method == "POST":
        # Get data from JSON string
        data = request.get_json()

        # Set the two part of the data, subject (string) and ids (list of strings)
        subject = data['subject']
        ids = data['ids']
        
        # Iterate through each id to update each applicable row
        for idNum in ids:
            # Use double quotes for case-sensitive variables
            query = 'UPDATE assignments SET "{}" = false WHERE "ID" = {}'.format(subject, idNum)
            cursor.execute(query)
        # Commit changes to the database
        conn.commit()
        
        # Return true (there was no error)
        return json.dumps(True)
    
    elif request.method == "GETPASSWORD":
        toPass = os.environ['PASS']
        return toPass

    elif request.method == "GET":
        # On page load, render index.html
        return render_template('index.html')

# Render submitted page after form submission
@app.route('/submitted')
def submitThanks():
    return render_template("submitted.html")

@app.route('/edit', methods=['GET', 'POST', 'GETPASSWORD'])
def edit():
    
    # On form submission:
    if request.method == "POST":
        # Get data from JSON string
        data = request.get_json()

        # Set the two part of the data, subject (string) and ids (list of strings)
        subject = data['subject']
        ids = data['ids']
        
        print(subject)
        print(ids)

        # Iterate through each id to update each applicable row
        for idNum in ids:
            # Use double quotes for case-sensitive variables
            query = """UPDATE assignments SET "{}" = 'true' WHERE "ID" = {}""".format(subject, idNum)
            cursor.execute(query)
        # Commit changes to the database
        conn.commit()
        
        # Return true (there was no error)
        return json.dumps(True)
    
    elif request.method == "GETPASSWORD":
        toPass = os.environ['PASS']
        return toPass

    elif request.method == "GET":
        # On page load, render edit.html
        return render_template('edit.html')

# Results page
@app.route('/results')
def view():
    # Get everything from database
    cursor.execute('SELECT * FROM assignments ORDER BY "ID" ASC')
    # Save each row as an element in a list
    passResult = cursor.fetchall()
    # Render results.html with result variable passed
    return render_template('results.html', result = passResult)

# Display about page
@app.route('/about')
def about():
    return render_template("about.html")

# Display emails
@app.route('/email')
def email():
    # Arrays to hold emails by number of incomplete
    one = []
    two = []
    three = []
    four = []
    five = []
    sixPlus = []

    # Counter for incomplete assignments
    incCount = 0

    # Get everything from database
    cursor.execute('SELECT * FROM assignments')
    # Save each row in list
    table = cursor.fetchall()
    for row in table:
        incCount = 0
        for i in range (3, (len(row)-1)):
            if row[i] == False:
                incCount += 1
        if (incCount == 1):
            one.append(row[len(row)-1])
        elif (incCount == 2):
            two.append(row[len(row)-1])
        elif (incCount == 3):
            three.append(row[len(row)-1])
        elif (incCount == 4):
            four.append(row[len(row)-1])
        elif (incCount == 5):
            five.append(row[len(row)-1])
        elif (incCount >= 6):
            sixPlus.append(row[len(row)-1])
        
        
    return render_template("email.html", oneArr = one, twoArr = two, threeArr = three, fourArr = four, fiveArr = five, sixArr = sixPlus)

# When program is run
if __name__ == '__main__':
    app.run()
    # Close cursor and connection once the program is done running
    cursor.close()
    conn.close()
