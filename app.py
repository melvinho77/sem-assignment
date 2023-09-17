from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
import difflib
# from weasyprint import HTML

app = Flask(__name__)
app.static_folder = 'static'  # The name of your static folder
app.static_url_path = '/static'  # The URL path to serve static files
app.secret_key = 'cc'

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

@app.route('/home_page')
def home_page():
    # Add any logic here if needed
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('programmes/Doctor of Philosophy Mathematical Sciences.html', number=1)

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/homeSearchProgramme', methods=['POST'])
def homeSearchProgramme():
    searchObj = request.form['textInput']
    
    select_sql = f"SELECT * FROM availableProgramme"
    cursor = db_conn.cursor()
    cursor.execute(select_sql)
    searchRange = cursor.fetchall()

    url_set = {"programmes/Diploma in Computer Science.html"}
    similarity_scores = []

    # Iterate through the program names in 'searchRange'
    for program in searchRange:
        print(program)
        program_name = program[1]
        similarity = difflib.SequenceMatcher(None, searchObj, program_name).ratio()

        if similarity > 0.1:
            similarity_scores.append((program_name, similarity))

    # Sort the results by similarity in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # Get the top 5 most relevant results
    top_5_results = similarity_scores[:5]

    if not top_5_results:
        return("no relevant result")
    else:







        return top_5_results






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
