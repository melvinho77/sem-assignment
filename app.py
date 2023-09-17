from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
from weasyprint import HTML

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


@app.route('/')
def index():
    return render_template('home.html', number=1)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/register_company')
def register_company():
    return render_template('RegisterCompany.html')


@app.route('/login_company', methods=['GET', 'POST'])
def login_company():
    return render_template('LoginCompany.html')


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    return render_template('LoginStudent.html')

# Navigation to Student Home Page


@app.route('/student_home', methods=['GET', 'POST'])
def student_home():
    id = session['loggedInStudent']

    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()

        # Retrieve cohort

        if not student:
            return "No such student exist."

    except Exception as e:
        return str(e)

    if student:
        # Student found in the database, login successful

        # Retrieve the cohort where student belongs to
        select_sql = "SELECT startDate, endDate FROM cohort c WHERE cohortId = %s"
        cursor = db_conn.cursor()
        cursor.execute(select_sql, (student[10]))
        cohort = cursor.fetchone()
        cursor.close()

        # Convert start_date_str and end_date_str into datetime.date objects
        start_date_str = str(cohort[0])
        end_date_str = str(cohort[1])
        start_date = datetime.date.fromisoformat(start_date_str)
        end_date = datetime.date.fromisoformat(end_date_str)

        #######################################################################
        # Retrieve supervisor details
        supervisor_query = "SELECT l.name, l.email FROM lecturer l, student s WHERE s.supervisor = l.lectId AND studentId = %s"
        cursor = db_conn.cursor()
        cursor.execute(supervisor_query, (student[0]))
        supervisor = cursor.fetchone()
        cursor.close()

        # Retrieve the company details
        company_query = "SELECT c.name, j.jobLocation, salary, jobPosition, jobDesc FROM company c, job j, companyApplication ca, student s WHERE c.companyId = j.company AND ca.student = s.studentId AND ca.job = j.jobId AND s.studentId = %s AND ca.`status` = 'approved'"
        cursor = db_conn.cursor()
        cursor.execute(company_query, (student[0]))
        companyDetails = cursor.fetchone()
        cursor.close()
        #######################################################################

        # Create a list to store all the retrieved data
        user_data = {
            'studentId': student[0],
            'studentName': student[1],
            'IC': student[2],
            'mobileNumber': student[3],
            'gender': student[4],
            'address': student[5],
            'email': student[6],
            'level': student[7],
            'programme': student[8],
            'cohort': student[10],
            'start_date': start_date,
            'end_date': end_date,
            # Default values if supervisor is not found
            'supervisor': supervisor if supervisor else ("N/A", "N/A"),
            # Default values if company details are not found
            'companyDetails': companyDetails if companyDetails else ("N/A", "N/A", "N/A", "N/A", "N/A")
        }

        # Set the loggedInStudent session
        session['loggedInStudent'] = student[0]

        # Redirect to the student home page with the user_data
        return render_template('studentHome.html', data=user_data)

# Navigation to Edit Student Page


@app.route('/edit_student', methods=['GET', 'POST'])
def edit_student():
    id = session['loggedInStudent']

    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()

        if not student:
            return "No such student exist."

    except Exception as e:
        return str(e)

    pendingRequestCount = check_pending_requests(id)

    return render_template('EditStudentProfile.html', studentId=student[0],
                           studentName=student[1],
                           IC=student[2],
                           mobileNumber=student[3],
                           gender=student[4],
                           address=student[5],
                           email=student[6],
                           level=student[7],
                           programme=student[8],
                           supervisor=student[9],
                           cohort=student[10],
                           pendingRequestCount=pendingRequestCount)

# CHECK REQUEST EDIT PENDING


def check_pending_requests(id):
    pending_request_sql = "SELECT COUNT(*) FROM request WHERE studentId = %s AND status = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(pending_request_sql, (id, 'pending'))
        foundRecords = cursor.fetchall()

        if not foundRecords:
            return 0

        return foundRecords[0][0]

    except Exception as e:
        return str(e)

# Update student profile (Function)


sddsdsdsdsdsdvsdvsdvsdvsdvv
sdv
send_filevsd
varssdv
vsd
vs
dv
sdv