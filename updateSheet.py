import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import psycopg2

# Connect to database using heroku environment variable DATABASE_URL
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')# Heroku requires SSL

# Create a cursor to execute queries
cursor = conn.cursor()

# Output data (currently a dict) to file so that you can use a python environment variable
data = {
    "type": "service_account",
    "project_id": "assignmentssheet",
    "private_key_id": "821db85dfa53172a71eedcb3ab591699f2f3e693",
    "private_key": os.environ['DRIVE_PRIVATE_KEY'].replace('\\n', '\n'),
    "client_email": "sheeteditor@assignmentssheet.iam.gserviceaccount.com",
    "client_id": "107375601430696559484",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheeteditor%40assignmentssheet.iam.gserviceaccount.com"
}
# Convert dict to JSON string
data = json.dumps(data, indent=2)

# Don't need to change the file if it already exists
if os.path.exists("assignmentssheet-821db85dfa53.json") == False:
    # Opening file automatically deletes contents and will create it if it doesn't exits
    outJSON = open("assignmentssheet-821db85dfa53.json", "w")
    outJSON.write(data)
    outJSON.close()

# Connect to api service account
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('assignmentssheet-821db85dfa53.json', scope)
client = gspread.authorize(creds)
# Open sheet
sheet = client.open('SLSD Assignment Completion Database - Google Sheets').sheet1

# Delete all from sheet except headers
sheet.resize(rows=1)
sheet.resize(rows=sheet.row_count)

cursor.execute('SELECT * FROM assignments ORDER BY "ID" ASC')
table = cursor.fetchall()

# Run it a bunch of times for testing purposes
for x in range(54):
    for i in range(len(table)):
        #List comprehension to replace booleans with strings
        table[i] = [ "Completed" if cell==True else "Incomplete" if cell==False else cell for cell in table[i] ]

        # Insert row into sheet
        sheet.insert_row(table[i], (i+2))
