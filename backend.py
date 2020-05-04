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
@app.route('/', methods=['GET', 'POST'])

@app.route('/index', methods=['GET', 'POST'])
def index():
    
    # On form submission:
    if request.method == "POST":
        # Get data from JSON string
        data = request.get_json()

        # Set the two part of the data, subject (string) and ids (list of strings)
        subject = data['subject']
        ids = data['ids']
        
        try:
            # Iterate through each id to update each applicable row
            for idNum in ids:
                # Use double quotes for case-sensitive variables
                query = 'UPDATE assignments SET "{}" = false WHERE "ID" = {}'.format(subject, idNum)
                cursor.execute(query)
            # Commit changes to the database
            conn.commit()
            
            # Return true (there was no error)
            return json.dumps(True)
        except:
            return json.dumps(False)
    
    # On page load, render index.html
    return render_template('index.html')

# Render submitted page after form submission
@app.route('/submitted')
def submitThanks():
    return render_template("submitted.html")

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

# When program is run
if __name__ == '__main__':
    app.run()
    # Close cursor and connection once the program is done running
    cursor.close()
    conn.close()
