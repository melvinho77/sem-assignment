from flask import render_template, make_response, jsonify
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
import socket
from config import *
import difflib
from datetime import datetime
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
    return render_template('home.html')

@app.route('/')
def index():
    network_details = get_network_details()
    return render_template('home.html', number=1, network_details=network_details)

@app.route("/", methods=['GET', 'POST'])
def home():
    network_details = get_network_details()
    return render_template('home.html', network_details=network_details)

# req1
@app.route('/relevantResult_display', methods=['POST'])
def relevantResult_display():
    result = request.form['result']
    network_details = get_network_details()
    return render_template(result, network_details=network_details)

# req1
@app.route('/homeSearchProgramme', methods=['POST'])
def homeSearchProgramme():
    searchObj = request.form['textInput']
    network_details = get_network_details()

    select_sql = f"SELECT * FROM availableProgramme"
    cursor = db_conn.cursor()
    cursor.execute(select_sql)
    searchRange = cursor.fetchall()

    url_set = {
        1: "programmes/Diploma in Computer Science.html",
        2: "programmes/Diploma in Information Systems.html",
        3: "programmes/Diploma in Information Technology.html",
        4: "programmes/Diploma in Software Engineering.html",
        5: "programmes/Management Mathematics with Computing.html",
        6: "programmes/Interactive Software Technology.html",
        7: "programmes/Data Science.html",
        8: "programmes/Enterprise Information Systems.html",
        9: "programmes/Information Security.html",
        10: "programmes/Internet Technology.html",
        11: "programmes/Software Systems Development.html",
        12: "programmes/Software Engineering.html",
        13: "programmes/Master of Computer Science.html",
        14: "programmes/Master of Information Technology.html",
        15: "programmes/Master of Science in Mathematical Sciences.html",
        16: "programmes/Doctor of Philosophy Computer Science.html",
        17: "programmes/Doctor of Philosophy Information Technology.html",
        18: "programmes/Doctor of Philosophy Mathematical Sciences.html"
    }

    similarity_scores = []

    # Iterate through the program names in 'searchRange'
    for program in searchRange:
        program_id = program[0]
        program_name = program[1]
        similarity = difflib.SequenceMatcher(None, searchObj, program_name).ratio()

        if similarity > 0.1:
            similarity_scores.append((program_id, program_name, similarity))

    # Sort the results by similarity in descending order
    sorted_similarity_scores = sorted(similarity_scores, key=lambda x: x[2], reverse=True)

    # Get the top 5 most relevant results
    top_5_results = sorted_similarity_scores[:5]

    relevantResults = []
    if not top_5_results:
        return render_template('relevantProgrammeSearchResult.html', relevantResults = relevantResults, network_details=network_details)
    else:
        for element in top_5_results:
            count = 0
            for url in url_set:
                count += 1
                if count == element[0]:
                    relevantResults.append(url_set.get(count))
        print(relevantResults)
        return render_template('relevantProgrammeSearchResult.html', relevantResults = relevantResults, network_details=network_details)

# N8 - Retrieve network details
def get_network_details():
    try:
        # Get the host name of the local machine
        host_name = socket.gethostname()

        # Get both IPv4 and IPv6 addresses associated with the host
        ipv4_address = socket.gethostbyname(host_name)
        ipv6_address = socket.getaddrinfo(host_name, None, socket.AF_INET6)[0][4][0]

        return {
            'Host Name': host_name,
            'IPv4 Address': ipv4_address,
            'IPv6 Address': ipv6_address
        }
    except Exception as e:
        return {'Error': str(e)}


#GWEE YONG SEAN
@app.route('/login_application')
def login_application():
    return render_template('studentLogin.html')

@app.route('/regitser_student')
def regitser_student():
    return render_template('registerStudent.html')

@app.route('/regStudent',methods=['POST'])
def regStudent():
    try:
        name = request.form['register-name']
        ic=request.form['register-ic']
        email = request.form['register-email']
        phone = request.form['register-phone']
        birth_date = request.form['register-birth-date']
        gender = request.form['register-gender']
        address = request.form['register-address']
        password = request.form['register-password']

        insert_sql = "INSERT INTO students (studentName, studentIc, studentEmail,studentPhone,studentBirthDate,studentGender,studentAddress,studentPassword) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor=db_conn.cursor()
    
        cursor.execute(insert_sql,(name,ic,email,phone,birth_date,gender,address,password))
        db_conn.commit()
        return render_template('studentLogin.html')
    except Exception as e:
        db_conn.rollback()

@app.route('/verifyLogin',methods=['POST'])
def verifyLogin():
    if request.method=='POST':
        loginEmail=request.form['login-email']
        loginPassword=request.form['login-password']

        # Query the database to check if the email and IC number match a record
        cursor = db_conn.cursor()
        query = "SELECT * FROM students WHERE studentEmail = %s AND studentPassword = %s"
        cursor.execute(query, (loginEmail, loginPassword))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['loggedInStudent']=user[0]
            return redirect(url_for("applicationHomeContent"))
        else:
            return render_template('studentLogin.html', msg="Access Denied: Invalid Email or Password")
        
@app.route('/programmePage',methods=['POST'])
def programmePage():
    apply_student_id = session.get('loggedInStudent')

    # Get the student's name based on their student ID
    student_name = get_student_name(apply_student_id)
    return render_template('DisplayProgramme.html',student_name=student_name)

@app.route('/applyProgramme',methods=['POST'])
def applyProgramme():
    intake=request.form.get('intake','')
    campus = request.form.get('campus','')
    level = request.form.get('level','')
    
        # Get the student ID from the session
    apply_student_id = session.get('loggedInStudent')

    # Get the student's name based on their student ID
    student_name = get_student_name(apply_student_id)

    select_sql = """
    SELECT ap.programmeName, ap.level, c.campusName, ch.intakeDate,p.programmeId
    FROM programme p
    LEFT JOIN availableProgramme ap ON p.programmeAvailable = ap.avProgrammeId
    LEFT JOIN campus c ON c.campusId = p.campus
    LEFT JOIN cohort ch ON ch.cohortId = p.intake
    WHERE 1
    """

    if intake:
        select_sql += f" AND p.intake = '{intake}'"
    if campus:
        select_sql += f" AND p.campus = '{campus}'"
    if level:
        select_sql += f" AND ap.level = '{level}'"


    cursor=db_conn.cursor()
    try:
        cursor.execute(select_sql)
        programmes=cursor.fetchall()

        programme_objects=[]
        for programme in programmes:
            programme_name=programme[0]
            level=programme[1]
            campus_name=programme[2]
            intake_date=programme[3]
            programme_Id=programme[4]

            programme_object ={
                "programme_name": programme_name,
                "level":level,
                "campus_name":campus_name,
                "intake_date":intake_date,
                "programme_Id":programme_Id
            }
            programme_objects.append(programme_object)
        return render_template('DisplayProgramme.html',programmes=programme_objects,student_name=student_name)

    except Exception as e:
        # Log the exception for debugging
        return render_template('DisplayProgramme.html',msg="Current does not have offer programme...")
        
def get_student_name(student_id):
    cursor = db_conn.cursor()
    select_sql = "SELECT studentName FROM students WHERE studentID = %s"
    cursor.execute(select_sql, (student_id,))
    student = cursor.fetchone()
    if student:
        return student[0]
    else:
        return "Unknown"

@app.route('/storeProgramme', methods=['POST'])
def storeProgramme():
    selected_programs = request.form.getlist('selected_programs')
    apply_student_id = session.get('loggedInStudent')
    application_date=datetime.now()
    cursor = db_conn.cursor()
    choice=0
    try:
        for program_id in selected_programs:
            choice+=1
            insert_sql = "INSERT INTO programmeApplications (applicationDate,applicationStatus,applicationProgramme,student,choice) VALUES (%s, %s,%s,%s,%s)"
            cursor.execute(insert_sql, (application_date,'pending',program_id,apply_student_id,choice))

        db_conn.commit()  # Commit the changes after the loop completes successfully

        return redirect(url_for("applicationHomeContent"))
    
    except Exception as e:
        # Handle any errors that may occur
        db_conn.rollback()
        # Log the error for debugging
        print(f"An error occurred: {str(e)}")

    finally:
        cursor.close()

    # Add a return statement here to return a valid response
    return redirect(url_for("applicationHomeContent"))

@app.route('/applicationHomeContent', methods=['GET', 'POST'])
def applicationHomeContent():
    apply_student_id = session.get('loggedInStudent')
    cursor = db_conn.cursor()

        # Get the student's name based on their student ID
    student_name = get_student_name(apply_student_id)

    select_sql="""
    SELECT pa.applicationId, pa.applicationDate, pa.applicationStatus, av.programmeName, p.intake
    FROM programmeApplications pa
    LEFT JOIN programme p ON p.programmeId = pa.applicationProgramme
    LEFT JOIN availableProgramme av ON av.avProgrammeId = p.programmeAvailable
    WHERE pa.student = %s AND pa.choice = 1;

    """
    cursor.execute(select_sql, (apply_student_id,))
    application=cursor.fetchall()
    
    application_objects = []
    for row in application:
        application_id=row[0]
        application_date=row[1]
        application_status=row[2]
        application_programme=row[3]
        application_intake=row[4]

        application_object ={
            "application_id":application_id,
            "application_date":application_date,
            "application_status": application_status,
            "application_programme": application_programme,
            "application_intake":application_intake
        }

        application_objects.append(application_object)
    return render_template('applicationHome.html',applications=application_objects,student_name=student_name)







        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)