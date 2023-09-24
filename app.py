from flask import render_template, make_response, jsonify, flash
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
import socket
from config import *
import datetime
import difflib
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
import re
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
    network_details = get_network_details()
    return render_template('home.html', network_details=network_details)


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
        similarity = difflib.SequenceMatcher(
            None, searchObj, program_name).ratio()

        if similarity > 0.1:
            similarity_scores.append((program_id, program_name, similarity))

    # Sort the results by similarity in descending order
    sorted_similarity_scores = sorted(
        similarity_scores, key=lambda x: x[2], reverse=True)

    # Get the top 5 most relevant results
    top_5_results = sorted_similarity_scores[:5]

    relevantResults = []
    if not top_5_results:
        return render_template('relevantProgrammeSearchResult.html', relevantResults=relevantResults, network_details=network_details)
    else:
        for element in top_5_results:
            count = 0
            for url in url_set:
                count += 1
                if count == element[0]:
                    relevantResults.append(url_set.get(count))
        print(relevantResults)
        return render_template('relevantProgrammeSearchResult.html', relevantResults=relevantResults, network_details=network_details)

# N8 - Retrieve network details


def get_network_details():
    try:
        # Get the host name of the local machine
        host_name = socket.gethostname()

        # Get both IPv4 and IPv6 addresses associated with the host
        ipv4_address = socket.gethostbyname(host_name)
        ipv6_address = socket.getaddrinfo(
            host_name, None, socket.AF_INET6)[0][4][0]

        return {
            'Host Name': host_name,
            'IPv4 Address': ipv4_address,
            'IPv6 Address': ipv6_address
        }
    except Exception as e:
        return {'Error': str(e)}


# N10
@app.route('/contactUs')
def contactUs():
    # Call the get_network_details function to retrieve network details
    # Retrieve student Id
    apply_student_id = session.get('loggedInStudent')

    # Get the student's name based on their student ID
    student_name = get_student_name(apply_student_id)
    network_details = get_network_details()
    
    # # Pass the network_details and msg to the contactUs.html template
    return render_template("contactUs.html", network_details=network_details, apply_student_id=apply_student_id, student_name=student_name)

@app.route('/redirectProgrammeHome')
def redirectProgrammeHome():
    network_details = get_network_details()
    return render_template('programmeHome.html', network_details=network_details)

# Define individual routes for each program's landing page


@app.route('/redirectDiplomaCS')
def redirectDiplomaCS():
    network_details = get_network_details()
    return render_template('programmes/Diploma in Computer Science.html', network_details=network_details)


@app.route('/redirectDiplomaIS')
def redirectDiplomaIS():
    network_details = get_network_details()
    return render_template('programmes/Diploma in Information Systems.html', network_details=network_details)


@app.route('/redirectDiplomaIT')
def redirectDiplomaIT():
    network_details = get_network_details()
    return render_template('programmes/Diploma in Information Technology.html', network_details=network_details)


@app.route('/redirectDiplomaSE')
def redirectDiplomaSE():
    network_details = get_network_details()
    return render_template('programmes/Diploma in Software Engineering.html', network_details=network_details)


@app.route('/redirectMMwC')
def redirectMMwC():
    network_details = get_network_details()
    return render_template('programmes/Management Mathematics with Computing.html', network_details=network_details)


@app.route('/redirectIST')
def redirectIST():
    network_details = get_network_details()
    return render_template('programmes/Interactive Software Technology.html', network_details=network_details)


@app.route('/redirectDS')
def redirectDS():
    network_details = get_network_details()
    return render_template('programmes/Data Science.html', network_details=network_details)


@app.route('/redirectEIS')
def redirectEIS():
    network_details = get_network_details()
    return render_template('programmes/Enterprise Information Systems.html', network_details=network_details)


@app.route('/redirectISecurity')
def redirectISecurity():
    network_details = get_network_details()
    return render_template('programmes/Information Security.html', network_details=network_details)


@app.route('/redirectInternetT')
def redirectInternetT():
    network_details = get_network_details()
    return render_template('programmes/Internet Technology.html', network_details=network_details)


@app.route('/redirectSSD')
def redirectSSD():
    network_details = get_network_details()
    return render_template('programmes/Software Systems Development.html', network_details=network_details)


@app.route('/redirectSE')
def redirectSE():
    network_details = get_network_details()
    return render_template('programmes/Software Engineering.html', network_details=network_details)


@app.route('/redirectMasterCS')
def redirectMasterCS():
    network_details = get_network_details()
    return render_template('programmes/Master of Computer Science.html', network_details=network_details)


@app.route('/redirectMasterIT')
def redirectMasterIT():
    network_details = get_network_details()
    return render_template('programmes/Master of Information Technology.html', network_details=network_details)


@app.route('/redirectMasterSMS')
def redirectMasterSMS():
    network_details = get_network_details()
    return render_template('programmes/Master of Science in Mathematical Sciences.html', network_details=network_details)


@app.route('/redirectDoctorPCS')
def redirectDoctorPCS():
    network_details = get_network_details()
    return render_template('programmes/Doctor of Philosophy Computer Science.html', network_details=network_details)


@app.route('/redirectDoctorPIT')
def redirectDoctorPIT():
    network_details = get_network_details()
    return render_template('programmes/Doctor of Philosophy Information Technology.html', network_details=network_details)


@app.route('/redirectDoctorPMS')
def redirectDoctorPMS():
    network_details = get_network_details()
    return render_template('programmes/Doctor of Philosophy Mathematical Sciences.html', network_details=network_details)


######################################## STAFF #############################################
@app.route("/staffDirectory", methods=['GET', 'POST'])
def staffDirectory():

    division = request.args.get('division')
    campusName = request.args.get('campus')

    cursor = db_conn.cursor()
    # get all campuses
    selectCampus_sql = "SELECT campusName FROM campus"

    # get all divisions
    select_sql = "SELECT name FROM division d, campus c WHERE d.campusId = c.campusId AND campusName = %s"

    try:
        cursor.execute(selectCampus_sql)
        campuses = cursor.fetchall()

        cursor.execute(select_sql, (campuses[0],))
        divisions = cursor.fetchall()

        cursor.execute(select_sql, (campuses[1],))
        div = cursor.fetchone()

    except Exception as e:
        return str(e)

    try:
        select_sql = "SELECT campusId FROM campus WHERE campusName = %s"
        cursor.execute(select_sql, (campusName,))
        campusId = cursor.fetchone()

        if (division != "ALL"):
            select_sql = "SELECT divisionId FROM division WHERE name = %s AND campusId = %s"
            cursor.execute(select_sql, (division, campusId))
            division = cursor.fetchone()

        if (request.args.get('staffName')):
            if (division == "ALL"):
                select_sql = "SELECT D.Name AS divisionName, S.*, P.* FROM division D, staff S LEFT JOIN publication P ON S.staffID = P.staffID WHERE D.divisionID = S.divisionID AND campusId = %s AND UPPER(S.name) LIKE UPPER(%s) ORDER BY (CASE WHEN D.divisionID = 'FOCS' THEN 1 ELSE 0 END) DESC, D.divisionID DESC;"
                cursor.execute(select_sql, (campusId, '%' +
                               request.args.get('staffName') + '%'))
            else:
                select_sql = "SELECT D.Name AS divisionName, S.*, P.* FROM division D, staff S LEFT JOIN publication P ON S.staffID = P.staffID WHERE D.divisionID = S.divisionID AND campusId = %s AND S.divisionId = %s AND UPPER(S.name) LIKE UPPER(%s) ORDER BY (CASE WHEN D.divisionID = 'FOCS' THEN 1 ELSE 0 END) DESC, D.divisionID DESC;"
                cursor.execute(select_sql, (campusId, division,
                               '%' + request.args.get('staffName') + '%'))
            staffs = cursor.fetchall()
        else:
            cursor.callproc('sp_get_all_staffs', [division, campusId])
            staffs = cursor.fetchall()

        staff_images = []

        # Fetch the S3 image URL based on emp_id
        # for staff in staffs:
        #     staff_image_file_name_in_s3 = "staffImage/" + str(staff[1])
        #     s3 = boto3.client('s3')
        #     bucket_name = custombucket

        #     try:
        #         staff_images[staff[1]] = s3.generate_presigned_url('get_object',
        #                                     Params={'Bucket': bucket_name,
        #                                             'Key': staff_image_file_name_in_s3},
        #                                     ExpiresIn=1000)  # Adjust the expiration time as needed

        #     except Exception as e:
        #         return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    network_details = get_network_details()
    return render_template('staffDirectory.html', staffs=staffs, staff_images=staff_images, network_details=network_details, div=div, divisions=divisions, campuses=campuses)

@app.route('/staff', methods=['GET'])
def staff():
    staffId = request.args.get('staffId')

    cursor = db_conn.cursor()

    try:
        select_sql = "SELECT * FROM staff s, division d, campus c WHERE d.divisionId = s.divisionId AND c.campusId = d.campusId AND s.staffId = %s"
        cursor.execute(select_sql, (staffId,))
        staff = cursor.fetchone()
        print(staff)
        
        if staff:
            staff = {
                'staffId': staff[0],
                'name': staff[1],
                'prefix': staff[2],
                'position': staff[3],
                'role': staff[4],
                'email': staff[5],
                'qualification': staff[6],
                'specialization': staff[7],
                'interest': staff[8],
                'divisionName': staff[11],
                'campusName': staff[14],
                'publications': []
            }

            select_sql = "SELECT * FROM publication WHERE staffId = %s"
            cursor.execute(select_sql, (staffId,))
            publications = cursor.fetchall()

            if publications:
                for publication in publications:
                    staff['publications'].append(
                    {'title': publication[1], 'link': publication[2]})

        print(staff)

    except Exception as e:
        return str(e)
    
    finally:
        cursor.close()    

    network_details = get_network_details()
    return render_template('staff.html', staff=staff, network_details=network_details)

@app.route('/compare', methods=['GET', 'POST'])
def selectCompare():
    select_level = "SELECT DISTINCT level FROM availableProgramme"
    cursorLevel = db_conn.cursor()

    cursorLevel.execute(select_level)
    levels = cursorLevel.fetchall()

    level_list = []
    programmeList = []

    try:
        for level in levels:
            programmeLevel = level[0]

            try:
                level_date = {
                    "level": programmeLevel,
                }

                level_list.append(level_date)

            except Exception as e:
                return str(e)

            select_programme = "SELECT avProgrammeId,programmeName FROM availableProgramme WHERE level=%s"
            cursorProgramme = db_conn.cursor()

            cursorProgramme.execute(select_programme, (programmeLevel,))
            programmes = cursorProgramme.fetchall()

            for programme in programmes:
                progId = programme[0]
                progName = programme[1]

                try:
                    level_date = {
                        "level": programmeLevel,
                        "progId": progId,
                        "progName": progName
                    }

                    programmeList.append(level_date)

                except Exception as e:
                    return str(e)

    except Exception as e:
        return str(e)

    network_details = get_network_details()
    return render_template('selectCompare.html', number=1, network_details=network_details,
                           level_list=level_list,
                           programmeList=programmeList)


@app.route("/SelectError", methods=['GET', 'POST'])
def selectProgrammeError():
    network_details = get_network_details()
    return render_template('selectProgrammeError.html', network_details=network_details)

# N5 compare Programme Structure


@app.route('/compareProgramme', methods=['POST'])
def showAllProgramme():

    progId = request.form.getlist('progId[]')
    electiveCourse_list = []
    courseExits = []
    courseNotExits = []
    programmeList = []
    electiveExits = []
    electiveNotExits = []
    course_list = []
    progId = request.form.getlist('progId[]')

    # loop for check the programme
    if len(progId) > 1:
        for id in progId:
            select_programme = "SELECT avProgrammeId,programmeName,level FROM availableProgramme WHERE avProgrammeId=%s"
            cursorProgramme = db_conn.cursor()

            cursorProgramme.execute(select_programme, (id,))
            programmes = cursorProgramme.fetchall()

            for programme in programmes:
                progId = programme[0]
                progName = programme[1]

                course_list = findAllCourse(course_list, programme[2])
                electiveCourse_list = findAllElective(programme[2])
                try:
                    level_date = {
                        "progId": progId,
                        "progName": progName
                    }

                    programmeList.append(level_date)

                except Exception as e:
                    return str(e)

                # all not exits course in a particular programme
                notCourses_for_program = findNotExistsCourse(id, progName)
                courseNotExits.extend(notCourses_for_program)

                # all not exits elective in a particular programme
                notElective_for_program = findNotElectiveExists(id, progName)
                electiveNotExits.extend(notElective_for_program)

            # all exits course in a particular programme
            courses_for_program = findCourse(id)
            courseExits.extend(courses_for_program)

            # all exits elective course in a particular programme
            elective_for_program = findElectiveCourse(id)
            electiveExits.extend(elective_for_program)

            # Sort the course_list alphabetically by courseName
            courseExits = sorted(courseExits, key=lambda x: x['progName'])

    return render_template('compareProgramme.html',
                           course_list=course_list,
                           electiveCourse_list=electiveCourse_list,
                           programmeList=programmeList,
                           courseExits=courseExits,
                           courseNotExits=courseNotExits,
                           electiveExits=electiveExits,
                           electiveNotExits=electiveNotExits
                           )


def findAllElective(level):
    electiveCourse_list = []
  # find all elective
    all_electiveCourse = "SELECT DISTINCT electiveTaken FROM programmeElectiveCourse p,  availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND LEVEL=%s ORDER BY electiveTaken"
    cursor_AllElectivecourse = db_conn.cursor()

    try:
        cursor_AllElectivecourse.execute(all_electiveCourse, (level,))
        allElectiveCourse = cursor_AllElectivecourse.fetchall()

        for elective in allElectiveCourse:
            courseName = elective[0]

            try:
                # Check if the course name already exists in course_list
                exists = any(
                    elective_data['courseName'] == courseName for elective_data in electiveCourse_list)

                # If the course name doesn't exist, add it to course_list
                if not exists:
                    elective_data = {
                        "courseName": courseName
                    }
                    electiveCourse_list.append(elective_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)
    # Sort course_list alphabetically by courseName
    electiveCourse_list = sorted(
        electiveCourse_list, key=lambda x: x['courseName'])

    return electiveCourse_list


def findAllCourse(course_list, level):
    # find main course
    all_course = "SELECT Distinct courseTaken FROM programmeMainCourse p , "  \
        "availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND level=%s ORDER BY courseTaken"
    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course, (level,))
        allCourse = cursor_Allcourse.fetchall()

        for course in allCourse:
            courseName = course[0]

            try:
                # Check if the course name already exists in course_list
                exists = any(course_data['courseName'] ==
                             courseName for course_data in course_list)

                # If the course name doesn't exist, add it to course_list
                if not exists:
                    course_data = {
                        "courseName": courseName
                    }
                    course_list.append(course_data)

            except Exception as e:
                return str(e)
    except Exception as e:
        return str(e)

     # Sort course_list alphabetically by courseName
    course_list = sorted(course_list, key=lambda x: x['courseName'])

    return course_list


def findNotExistsCourse(programmeId, progName):

    # Do something with progName

    # Find all courses that do not exist in the given programmeId
    all_course = "SELECT DISTINCT courseTaken " \
        "FROM programmeMainCourse " \
        "WHERE courseTaken NOT IN (" \
        "SELECT courseTaken " \
        "FROM programmeMainCourse " \
        "WHERE programmeId = %s ) " \
        "ORDER BY courseTaken;"

    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course, (programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "progName": progName,
                    "courseName": courseName
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    return course_list


def findCourse(programmeId):
    # find all course
    all_course = "SELECT programmeName,courseTaken FROM programmeMainCourse p , availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND programmeId = %s ORDER BY programmeName"
    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course, (programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            progName = course[0]
            courseName = course[1]

            try:
                course_data = {
                    "progName": progName,
                    "courseName": courseName
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    return course_list


def findElectiveCourse(programmeId):
    # find all course
    all_course = "SELECT programmeName,electiveTaken FROM programmeElectiveCourse p , availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND programmeId = %s ORDER BY electiveTaken"
    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course, (programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            progName = course[0]
            courseName = course[1]

            try:
                course_data = {
                    "progName": progName,
                    "courseName": courseName
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    return course_list


def findNotElectiveExists(programmeId, progName):

    # Do something with progName

    # Find all courses that do not exist in the given programmeId
    all_course = "SELECT DISTINCT electiveTaken FROM programmeElectiveCourse WHERE electiveTaken NOT IN (SELECT electiveTaken FROM programmeElectiveCourse WHERE programmeId = %s )ORDER BY electiveTaken"

    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course, (programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "progName": progName,
                    "courseName": courseName
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    return course_list


@app.route('/loadStudProfile')
def loadStudProfile():
    network_details = get_network_details()
    studID = session['loggedInStudent']
    select_sql = f"SELECT * FROM students WHERE studentID = '{studID}'"

    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql)
        studInfo = cursor.fetchall()
        stud_list = []
        for studData in studInfo:

            stud_data = {
                "studName": studData[1],
                "studIC": studData[2],
                "studEmail": studData[3],
                "studPhone": studData[4],
                "studBdate": studData[5],
                "studGender": studData[6],
                "studAddress": studData[7],
                "studPassword": studData[8],
            }
            stud_list.append(stud_data)
            print(stud_list)
    except Exception as e:
        return str(e)
    return render_template('applicationProfile.html', network_details=network_details, stud_data=stud_data)

# Gwee Yong Sean
@app.route('/login_application')
def login_application():
    return render_template('studentLogin.html')


@app.route('/regitser_student')
def regitser_student():
    return render_template('registerStudent.html')


@app.route('/regStudent', methods=['POST'])
def regStudent():
    try:
        name = request.form['register-name']
        ic = request.form['register-ic']
        email = request.form['register-email']
        phone = request.form['register-phone']
        birth_date = request.form['register-birth-date']
        gender = request.form['register-gender']
        address = request.form['register-address']
        password = request.form['register-password']

        insert_sql = "INSERT INTO students (studentName, studentIc, studentEmail,studentPhone,studentBirthDate,studentGender,studentAddress,studentPassword) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, (name, ic, email, phone,
                       birth_date, gender, address, password))
        db_conn.commit()
        return render_template('studentLogin.html')
    except Exception as e:
        db_conn.rollback()


@app.route('/verifyLogin', methods=['POST'])
def verifyLogin():
    if request.method == 'POST':
        loginEmail = request.form['login-email']
        loginPassword = request.form['login-password']

        # Query the database to check if the email and IC number match a record
        cursor = db_conn.cursor()
        query = "SELECT * FROM students WHERE studentEmail = %s AND studentPassword = %s"
        cursor.execute(query, (loginEmail, loginPassword))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['loggedInStudent'] = user[0]
            return redirect(url_for("applicationHomeContent"))
        else:
            return render_template('studentLogin.html', msg="Access Denied: Invalid Email or Password")


@app.route('/programmePage', methods=['POST'])
def programmePage():
    apply_student_id = session.get('loggedInStudent')

    # Get the student's name based on their student ID
    student_name = get_student_name(apply_student_id)
    return render_template('DisplayProgramme.html', student_name=student_name)


@app.route('/applyProgramme', methods=['POST'])
def applyProgramme():
    intake = request.form.get('intake', '')
    campus = request.form.get('campus', '')
    level = request.form.get('level', '')

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

    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql)
        programmes = cursor.fetchall()

        programme_objects = []
        for programme in programmes:
            programme_name = programme[0]
            level = programme[1]
            campus_name = programme[2]
            intake_date = programme[3]
            programme_Id = programme[4]

            programme_object = {
                "programme_name": programme_name,
                "level": level,
                "campus_name": campus_name,
                "intake_date": intake_date,
                "programme_Id": programme_Id
            }
            programme_objects.append(programme_object)
        return render_template('DisplayProgramme.html', programmes=programme_objects, student_name=student_name)

    except Exception as e:
        # Log the exception for debugging
        return render_template('DisplayProgramme.html', msg="Current does not have offer programme...")


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
    application_date = datetime.datetime.now()
    cursor = db_conn.cursor()
    choice = 0
    try:
        for program_id in selected_programs:
            choice += 1
            insert_sql = "INSERT INTO programmeApplications (applicationDate,applicationStatus,applicationProgramme,student,choice) VALUES (%s, %s,%s,%s,%s)"
            cursor.execute(insert_sql, (application_date,
                           'pending', program_id, apply_student_id, choice))

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

    select_sql = """
    SELECT pa.applicationId, pa.applicationDate, pa.applicationStatus, av.programmeName, p.intake,pa.choice
    FROM programmeApplications pa
    LEFT JOIN programme p ON p.programmeId = pa.applicationProgramme
    LEFT JOIN availableProgramme av ON av.avProgrammeId = p.programmeAvailable
    WHERE pa.student = %s

    """
    cursor.execute(select_sql, (apply_student_id,))
    application = cursor.fetchall()

    application_objects = []
    for row in application:
        application_id = row[0]
        application_date = row[1]
        application_status = row[2]
        application_programme = row[3]
        application_intake = row[4]
        application_choice = row[5]

        application_object = {
            "application_id": application_id,
            "application_date": application_date,
            "application_status": application_status,
            "application_programme": application_programme,
            "application_intake": application_intake,
            "application_choice": application_choice
        }

        application_objects.append(application_object)
    return render_template('applicationHome.html', applications=application_objects, student_name=student_name)


@app.route('/goToQualification', methods=['GET', 'POST'])
def goToQualification():
    return render_template('verifyQualification.html')


@app.route('/verifyApplication', methods=['GET', 'POST'])
def verifyApplication():

    cursor = db_conn.cursor()
    apply_student_id = session.get('loggedInStudent')
    
    qualification = request.form.get('qualification-diploma', '')
    year = request.form.get('qualification-diploma-year', '')
    subject1 = request.form.get('spm-subject-1', '')
    subject2 = request.form.get('spm-subject-2', '')
    subject3 = request.form.get('spm-subject-3', '')
    subject4 = request.form.get('spm-subject-4', '')
    subject5 = request.form.get('spm-subject-5', '')
    subject6 = request.form.get('spm-subject-6', '')
    subject7 = request.form.get('spm-subject-7', '')
    subject8 = request.form.get('spm-subject-8', '')
    subject9 = request.form.get('spm-subject-9', '')
    subject10 = request.form.get('spm-subject-10', '')

    grades = [
        request.form.get(f'spm-grades-{i}', '') for i in range(1, 11)
    ]

    #pytesseract.pytesseract.tesseract_cmd = '"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"'

    select_sql = "select studentIc from students where studentId = %s"
    cursor.execute(select_sql, (apply_student_id))
    ic = cursor.fetchone()

    student_grades = {
        request.form.get(f'spm-subject-{i}'): request.form.get(f'spm-grades-{i}', '')
        for i in range(1, 11)
    }

    # 'spm-file' is the name of the file input field in the form
    file = request.files['spm-file']

    # Read the file into a BytesIO object
    file_bytes = io.BytesIO(file.read())

    # Open the image with PIL
    imagefile = Image.open(file_bytes)

    # get spm result images
    # Convert the PIL Image to a numpy array
    imagefile = np.array(imagefile)
    imagefile = crop_image(imagefile)
    text = pytesseract.image_to_string(imagefile, config='--psm 6')
    print(text)

    if not check_year(text, year):
        return render_template('verifyQualification.html', err_msg="The year of SPM slip incorrect or your image is too blur, please try again")

    # Split the result text into lines
    lines = text.strip().split('\n')

    checkIc = False

    # Iterate over each line
    for line in lines:
        # Split the line into words
        words = line.split()

        # Check if the line contains at least 3 words (subject and grade)
        if words:
            if 'K/P' in words:
                if ic[0] in words:
                    print(f"The ic matched {words}.")
                    checkIc = True
                else:
                    print(f"The ic not match {words}.")
                    return render_template('verifyQualification.html', err_msg="The IC of SPM slip does not match or your image is too blur, please try again")

    if not checkIc:
        return render_template('verifyQualification.html', err_msg="SPM slip is not valid or your image is too blur, please try again")

    matchSubject = True
    gotSubject = False
    msg = ""
    # Check each grade in the dictionary against the list
    for subject, grade in student_grades.items():
        # Find the list that contains the subject
        for grades in lines:
            if subject in grades:
                # Check if the grade in the list matches the grade in the dictionary
                if grade not in grades:
                    matchSubject = False
                    msg += (f"The grade for {subject} does not match\n")
                    print(f"The grade for {subject} does not match.")
                else:
                    gotSubject = True
                    print(f"The grade for {subject} matched.")
                break

    if not gotSubject:
        return render_template('verifyQualification.html', err_msg="The SPM slip may not completed or your image is too blur")

    if not matchSubject:
        return render_template('verifyQualification.html', err_msg=msg+"Or you can try to reupload your SPM slip")

    # Count the number of subjects with a grade of "C" or better
    c_or_better_count = sum(
        grade in ['A', 'A+', 'A-', 'B', 'B+', 'C', 'C+'] for grade in grades)

    # GET know what student apply the programme with the first choice
    select_sql_fist_choice = """
    SELECT av.avProgrammeId AS programme_id
    FROM programmeApplications pa
    LEFT JOIN programme p ON p.programmeId=pa.applicationProgramme
    LEFT JOIN availableProgramme av ON p.programmeAvailable=av.avProgrammeId
    WHERE pa.student=%s AND pa.applicationStatus='pending' AND pa.choice=1
    """

    cursor.execute(select_sql_fist_choice, (apply_student_id,))
    application_programme = cursor.fetchone()

    grade_order = {
        'A+': 9,
        'A': 8,
        'A-': 7,
        'B+': 6,
        'B': 5,
        'C+': 4,
        'C': 3,
        'D': 2,
        'E': 1
    }

    # check whether the BAHASA MELAYU and  excced grades E
    compulsory_subjects = {
        'BAHASA MELAYU': 'E',
        'SEJARAH': 'E',
    }

    country_require = True
    for country_subject, country_required_grade in compulsory_subjects.items():
        if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
            # Find the index of the subject in the list
            subject_index = [subject1, subject2, subject3, subject4, subject5,
                             subject6, subject7, subject8, subject9, subject10].index(country_subject)

            # Check if the student's grade for that subject meets the required grade
            student_grade = grades[subject_index]

            # Compare the student's grade with the required grade
            if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                country_require = False
                break

    # compare compulsary subject has meet the requirements or not
    meet_first_choice_requirement = True
    # validate whether the application programme have reach the compulsary subject of minimum requirement
    if application_programme:
        sql_select_programme = """
            SELECT SUBJECT, grade
            FROM qualification
            WHERE programme=%s AND LEVEL=%s
        """
        cursor.execute(sql_select_programme,
                       (application_programme, qualification))
        validateSubject = cursor.fetchall()  # getting know first choice of subject

        # commpare student grades
        for subject, required_grade in validateSubject:
            # check if the validate subject in the manual subject from the student
            if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                # find the index of the student in the list
                # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5,
                                 subject6, subject7, subject8, subject9, subject10].index(subject)
                student_grade = grades[subject_index]
                if (grade_order.get(student_grade, 0) < grade_order.get(required_grade, 0)):
                    meet_first_choice_requirement = False
                    print(
                        f"For {subject}, the student's grade {student_grade} does not meet the required grade {required_grade}.")
                    break
            else:
                return ("Student does not have subject")

    if c_or_better_count >= 3 and country_require and meet_first_choice_requirement:
        update_sql_choice_1 = """
        UPDATE programmeApplications
        SET applicationStatus = 'approved'
        WHERE student = %s AND choice = 1 AND applicationStatus = 'pending'
         """
        cursor.execute(update_sql_choice_1, (apply_student_id,))

        # Update choice 2 and choice 3 application status to 'end' where the status is 'pending'
        update_sql_choice_2_3 = """
        UPDATE programmeApplications
        SET applicationStatus = 'end'
        WHERE student = %s AND (choice = 2 OR choice = 3) AND applicationStatus = 'pending'
        """
        cursor.execute(update_sql_choice_2_3, (apply_student_id,))

        # Commit the changes to the database
        db_conn.commit()
        return redirect(url_for("applicationHomeContent"))
    else:
        update_sql_choice_1_to_reject = """
        UPDATE programmeApplications
        SET applicationStatus = 'rejected'
        WHERE student = %s AND choice = 1 AND applicationStatus = 'pending'
         """
        cursor.execute(update_sql_choice_1_to_reject, (apply_student_id,))

        select_sql_second_choice = """
        SELECT av.avProgrammeId AS programme_id
        FROM programmeApplications pa
        LEFT JOIN programme p ON p.programmeId = pa.applicationProgramme
        LEFT JOIN availableProgramme av ON p.programmeAvailable = av.avProgrammeId
        WHERE pa.student = %s AND pa.applicationStatus = 'pending' AND pa.choice = 2
        """

        cursor.execute(select_sql_second_choice, (apply_student_id,))
        application_programme_second_choice = cursor.fetchone()

        second_country_require = True
        for country_subject, country_required_grade in compulsory_subjects.items():
            if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5,
                                 subject6, subject7, subject8, subject9, subject10].index(country_subject)

                # Check if the student's grade for that subject meets the required grade
                student_grade = grades[subject_index]

                # Compare the student's grade with the required grade
                if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                    second_country_require = False
                    print(
                        f"For {subject}, the student's grade {student_grade} does not meet the required grade {country_required_grade}.")
                    break

        # compare compulsary subject has meet the requirements or not
        meet_second_choice_requirement = True
        # validate whether the application programme have reach the compulsary subject of minimum requirement
        if application_programme:
            sql_select_programme = """
            SELECT SUBJECT, grade
            FROM qualification
            WHERE programme=%s AND LEVEL=%s
            """
        cursor.execute(sql_select_programme,
                       (application_programme_second_choice, qualification))
        validateSubject = cursor.fetchall()  # getting know first choice of subject

        # commpare student grades
        for subject, required_grade in validateSubject:
            # check if the validate subject in the manual subject from the student
            if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                # find the index of the student in the list
                # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5,
                                 subject6, subject7, subject8, subject9, subject10].index(subject)
                student_grade = grades[subject_index]
                if (grade_order.get(student_grade, 0) < grade_order.get(required_grade, 0)):
                    meet_first_choice_requirement = False
                    break
            else:
                return ("Student does not have subject")

        if c_or_better_count >= 3 and second_country_require and meet_second_choice_requirement:
            update_sql_choice_2_approved = """
            UPDATE programmeApplications
            SET applicationStatus = 'approved'
            WHERE student = %s AND choice = 2 AND applicationStatus = 'pending'
            """
            cursor.execute(update_sql_choice_2_approved, (apply_student_id,))

            # Update choice 2 and choice 3 application status to 'end' where the status is 'pending'
            update_sql_choice_3_end = """
            UPDATE programmeApplications
            SET applicationStatus = 'end'
            WHERE student = %s AND choice = 3 AND applicationStatus = 'pending'
            """
            cursor.execute(update_sql_choice_3_end, (apply_student_id,))
            db_conn.commit()
            return redirect(url_for("applicationHomeContent"))
        else:
            # update choice 2 to rejected
            update_sql_choice_2_rejected = """
            UPDATE programmeApplications
            SET applicationStatus = 'rejected'
            WHERE student = %s AND choice = 2 AND applicationStatus = 'pending'
            """
            cursor.execute(update_sql_choice_2_rejected, (apply_student_id,))

            select_sql_third_choice = """
            SELECT av.avProgrammeId AS programme_id
            FROM programmeApplications pa
            LEFT JOIN programme p ON p.programmeId = pa.applicationProgramme
            LEFT JOIN availableProgramme av ON p.programmeAvailable = av.avProgrammeId
            WHERE pa.student = %s AND pa.applicationStatus = 'pending' AND pa.choice = 3
            """
            cursor.execute(select_sql_third_choice, (apply_student_id,))
            application_programme_third_choice = cursor.fetchone()

            third_country_require = True
            for country_subject, country_required_grade in compulsory_subjects.items():
                if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                    # Find the index of the subject in the list
                    subject_index = [subject1, subject2, subject3, subject4, subject5,
                                     subject6, subject7, subject8, subject9, subject10].index(country_subject)

                    # Check if the student's grade for that subject meets the required grade
                    student_grade = grades[subject_index]

                    # Compare the student's grade with the required grade
                    if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                        third_country_require = False
                        break

                # compare compulsary subject has meet the requirements or not
                meet_third_choice_requirement = True
                # validate whether the application programme have reach the compulsary subject of minimum requirement
                if application_programme_third_choice:
                    sql_select_programme = """
                    SELECT SUBJECT, grade
                    FROM qualification
                    WHERE programme=%s AND LEVEL=%s
                    """
                    cursor.execute(
                        sql_select_programme, (application_programme_third_choice, qualification))
                    validateSubject = cursor.fetchall()  # getting know first choice of subject

                    # commpare student grades
                for subject, required_grade in validateSubject:
                    # check if the validate subject in the manual subject from the student
                    if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                        # Find the index of the subject in the list
                        subject_index = [subject1, subject2, subject3, subject4, subject5,
                                         subject6, subject7, subject8, subject9, subject10].index(subject)
                        student_grade = grades[subject_index]
                        if (grade_order.get(student_grade, 0) < grade_order.get(required_grade, 0)):
                            meet_third_choice_requirement = False
                            print(
                                f"For {subject}, the student's grade {student_grade} does not meet the required grade {required_grade}.")
                            break
                        else:
                            return ("Student does not have subject")
            if c_or_better_count >= 3 and third_country_require and meet_third_choice_requirement:
                update_sql_choice_3_approved = """
                UPDATE programmeApplications
                SET applicationStatus = 'approved'
                WHERE student = %s AND choice = 3 AND applicationStatus = 'pending'
                """
                cursor.execute(update_sql_choice_3_approved,
                               (apply_student_id,))
                db_conn.commit()
                return redirect(url_for("applicationHomeContent"))
            else:
                update_sql_choice_3_rejected = """
                UPDATE programmeApplications
                SET applicationStatus = 'rejected'
                WHERE student = %s AND choice = 3 AND applicationStatus = 'pending'
                """
                cursor.execute(update_sql_choice_3_rejected,
                               (apply_student_id,))
                db_conn.commit()
                return redirect(url_for("applicationHomeContent"))


def check_year(text, year):
    # Use a regular expression to find four-digit numbers in the text
    years = re.findall(r'\b\d{4}\b', text)

    # Check if the desired year is in the list of years
    return str(year) in years


def crop_image(img):
    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # invert gray image
    gray = 255 - gray

    # threshold
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]

    # apply close and open morphology to fill tiny black and white holes and save as mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # get contours (presumably just one around the nonzero pixels)
    contours = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    cntr = contours[0]
    x, y, w, h = cv2.boundingRect(cntr)

    # make background transparent by placing the mask into the alpha channel
    new_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    new_img[:, :, 3] = mask

    # then crop it to bounding rectangle
    crop = new_img[y:y+h, x:x+w]

    cv2.imshow('crop', crop)

    return crop

# Ho hong meng
@app.route("/trackContactUs")
def trackContactUs():
    # Change to session data
    id = session.get('loggedInStudent')
    network_details = get_network_details()

    # Retrieve all contact data based on this student
    select_sql = "SELECT * FROM contact WHERE student = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id,))
        contact_data = cursor.fetchall()
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    return render_template("studentContactUs.html", contact_data=contact_data, student=session['loggedInStudent'], network_details=network_details)


@app.route('/submitContactUs', methods=['POST'])
def submitContactUs():
    # After log in, then only can ask question
    student_id = request.form.get('apply_student_id')
    student_name = request.form.get('student_name')
    category = request.form.get('category')
    inquiries = request.form.get('inquiries')

    try:
        insert_sql = "INSERT INTO contact (`status`, category, question, reply, repliedBy, student) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, ('pending', category,
                       inquiries, None, None, student_id))
        db_conn.commit()

        # Flash a success message
        flash('Question submitted successfully', 'success')

        # Redirect back to the contactUs page
        return redirect('/contactUs')

    except Exception as e:
        db_conn.rollback()
        return str(e)


@app.route('/adminLogin')
def adminLogin():
    network_details = get_network_details()
    return render_template('adminLogin.html', network_details=network_details)


@app.route('/adminContactUs', methods=['POST', 'GET'])
def adminContactUs():
    network_details = get_network_details()
    # Handle the form submission with email and password
    email = request.form['email']
    password = request.form['password']

    try:
        cursor = db_conn.cursor()
        # Retrieve contact details for the current page
        cursor.execute("SELECT * FROM contact")
        contactDetails = cursor.fetchall()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if email == 'hhm@gmail.com' and password == '123':
        session['name'] = 'Ho Hong Meng'
        session['loggedIn'] = 'hhm'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    elif email == 'css@gmail.com' and password == '456':
        session['name'] = 'Cheong Soo Siew'
        session['loggedIn'] = 'css'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    else:
        error_msg = 'Invalid email or password. Please try again.'
        return render_template('adminLogin.html', msg=error_msg, network_details=network_details)


@app.route('/adminRedirect', methods=['POST', 'GET'])
def adminRedirect():
    network_details = get_network_details()
    contactDetails = []

    try:
        cursor = db_conn.cursor()
        # Retrieve contact details for the current page
        cursor.execute("SELECT * FROM contact")
        contactDetails = cursor.fetchall()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    # Check the session for authentication
    user = session.get('loggedIn')

    if user == 'hhm':
        session['name'] = 'Ho Hong Meng'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    elif user == 'css':
        session['name'] = 'Cheong Soo Siew'
        return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

    else:
        error_msg = 'You are not logged in. Please log in to access this page.'
        return render_template('adminLogin.html', msg=error_msg, network_details=network_details)


@app.route('/replyQuestion', methods=['POST', 'GET'])
def replyQuestion():
    contactId = request.form.get('contactId')
    reply = request.form.get('reply')
    repliedBy = session['name']

    # Update the contact us details
    update_sql = "UPDATE contact SET reply = %s, repliedBy = %s, status=%s WHERE contactId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (reply, repliedBy, 'completed', contactId))
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if 'name' in session and 'email' in session:
        name = session['name']
        email = session['email']
        if email == 'hhm@gmail.com' and name == 'Ho Hong Meng':
            session['loggedIn'] = 'hhm'
            session['name'] = 'Ho Hong Meng'
        elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
            session['loggedIn'] = 'css'
            session['name'] = 'Cheong Soo Siew'

    # Flash a success message
    flash('Question submitted successfully', 'success')

    # Redirect back to the contactUs page
    return redirect('/adminRedirect')


<<<<<<< HEAD
@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
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

    # Get the newly updated input fields
    newStudentName = request.form['studentName']
    newGender = request.form['gender']
    newMobileNumber = request.form['mobileNumber']
    newAddress = request.form['address']

    # Compare with the old fields
    # Student name
    if student[1] != newStudentName:
        # Insert into request table
        insert_sql = "INSERT INTO request (attribute, newData, status, reason, studentId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, ('studentName', newStudentName,
                                    'pending', None, session['loggedInStudent']))
        db_conn.commit()

    # Gender
    if student[4] != newGender:
        # Insert into request table
        insert_sql = "INSERT INTO request (attribute, newData, status, reason, studentId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, ('gender', newGender, 'pending',
                                    None, session['loggedInStudent']))
        db_conn.commit()

    # Mobile number
    if student[3] != newMobileNumber:
        # Insert into request table
        insert_sql = "INSERT INTO request (attribute, newData, status, reason, studentId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, ('mobileNumber', newMobileNumber,
                                    'pending', None, session['loggedInStudent']))
        db_conn.commit()

    # Address
    if student[5] != newAddress:
        # Insert into request table
        insert_sql = "INSERT INTO request (attribute, newData, status, reason, studentId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, ('address', newAddress,
                                    'pending', None, session['loggedInStudent']))
        db_conn.commit()

    return redirect('/edit_student')

# Navigate to Upload Resume Page


@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
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

    return render_template('UploadResume.html', studentId=student[0],
                           studentName=student[1],
                           IC=student[2],
                           mobileNumber=student[3],
                           gender=student[4],
                           address=student[5],
                           email=student[6],
                           level=student[7],
                           programme=student[8],
                           supervisor=student[9],
                           cohort=student[10],)

# Upload Resume into S3


@app.route('/uploadResume', methods=['GET', 'POST'])
def uploadResume():
    id = session['loggedInStudent']

    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cursor = db_conn.cursor()
    stud_resume_file_name_in_s3 = 'resume/' + id + "_resume"
    student_resume_file = request.files['resume']

    # Create the folder if not exist
    s3_client = boto3.client('s3')
    folder_name = 'resume/'

    # Check if the folder (prefix) already exists
    response = s3_client.list_objects_v2(
        Bucket=custombucket, Prefix=folder_name)

    # If the folder (prefix) doesn't exist, you can create it
    if 'Contents' not in response:
        s3_client.put_object(Bucket=custombucket, Key=(folder_name + '/'))

    s3 = boto3.resource('s3')

    try:
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()
        db_conn.commit()

        print("Data inserted in MySQL RDS... uploading resume to S3...")

        # Set the content type to 'application/pdf' when uploading to S3
        s3.Object(custombucket, stud_resume_file_name_in_s3).put(
            Body=student_resume_file,
            ContentType='application/pdf'
        )

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])

        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

    except Exception as e:
        db_conn.rollback()
        return str(e)

    print("Resume uploaded complete.")
    return render_template('UploadResumeOutput.html', studentName=student[1], id=session['loggedInStudent'])


# Download resume from S3 (based on Student Id)
@app.route('/viewResume', methods=['GET', 'POST'])
def view_resume():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')
    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"resume/{student_id}_resume"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the resume does not exist, return a page with a message
            return render_template('no_resume_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)

# Navigate to Student View Report


@app.route('/view_progress_report', methods=['GET', 'POST'])
def view_progress_report():
    # Retrieve student's ID
    id = session.get('loggedInStudent')
    if not id:
        return "Student not logged in."

    # Retrieve the cohort where student belongs to
    select_sql = "SELECT startDate, endDate FROM cohort c, student s WHERE studentId = %s AND c.cohortId = s.cohort"
    cursor = db_conn.cursor()

    # Retrieve all the submission details based on student
    report_sql = "SELECT * from report WHERE student = %s"
    report_cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id))
        cohort = cursor.fetchone()

        report_cursor.execute(report_sql, (id))
        report_details = report_cursor.fetchall()

        if not cohort:
            return "No such cohort or report details exists."

    except Exception as e:
        return str(e)

    # Create a list to store report details
    report_list = []

    # Iterate over the fetched report rows and append them to the list
    for row in report_details:
        report_list.append({
            # Adjust this to match your database structure
            'reportId': row[0],
            'submissionDate': row[1],
            'reportType': row[2],
            'status': row[3],
            'late': row[4],
            'remark': row[5],
            'student': row[6],
        })

    # Convert start_date_str and end_date_str into datetime.date objects
    start_date_str = str(cohort[0])
    end_date_str = str(cohort[1])

    start_date = datetime.date.fromisoformat(start_date_str)
    end_date = datetime.date.fromisoformat(end_date_str)

    # Calculate submission dates and report names
    submission_info = calculate_submission_date(start_date, end_date)

    # Format submission dates as "year-month-day"
    submission_dates = [date.strftime('%Y-%m-%d')
                        for date, _ in submission_info]
    report_names = [report_name for _, report_name in submission_info]

    combined_data = list(zip(submission_dates, report_names))

    return render_template('StudentViewReport.html', student_id=session.get('loggedInStudent'), combined_data=combined_data, start_date=cohort[0], end_date=cohort[1], report_list=report_list)

# Calculate the submission dates and return in a list


def calculate_submission_date(start_date, end_date):
    # Calculate the number of months between the start date and end date.
    months_between_dates = (end_date.year - start_date.year) * \
        12 + (end_date.month - start_date.month) + 1

    # Initialize a list to store submission dates and report names as tuples.
    submission_info = []

    for i in range(1, months_between_dates + 1):
        # Calculate the target month and year for this report
        target_month = (start_date.month + i - 1) % 12
        target_year = start_date.year + (start_date.month + i - 1) // 12

        # Calculate the 4th day of the target month as a datetime.date object
        submission_date = datetime.date(target_year, target_month + 1, 4)

        # If the start date is before the 4th day of the current month,
        # adjust the submission date to the 4th day of the next month
        if start_date.day < 4 and submission_date > start_date:
            submission_date = datetime.date(
                target_year, target_month + 1, 4)

        report_name = f'Progress Report {i}'
        submission_info.append((submission_date, report_name))

    # Calculate the final report submission date, which is 1 week before the end date.
    final_report_date = end_date - datetime.timedelta(days=7)
    submission_info.append((final_report_date, 'Final Report'))

    return submission_info

# Calculate the submission counts (INSERT AFTER REGISTER)


def calculate_submission_count(start_date, end_date):
    # Calculate the number of months between the start date and end date.
    months_between_dates = (end_date.year - start_date.year) * \
        12 + (end_date.month - start_date.month) + 1

    # Calculate the count of submission reports including the final report
    report_count = months_between_dates + 1  # +1 for the final report

    return report_count

# Upload progress report function


@app.route('/uploadProgressReport', methods=['GET', 'POST'])
def uploadProgressReport():
    # Retrieve all required data from forms / session
    id = session['loggedInStudent']
    report_type = request.form.get('report_type')
    # Remove spaces and concatenate words
    report_type = report_type.replace(" ", "")
    submission_date = request.form.get('submission_date')
    student_progress_report = request.files['progress_report']

    # Change submission date into datetime obj
    submission_date_obj = datetime.date.fromisoformat(submission_date)

    s3_client = boto3.client('s3')
    folder_name = 'progressReport/' + id  # Replace 'id' with your folder name

    # Check if the folder (prefix) already exists
    response = s3_client.list_objects_v2(
        Bucket=custombucket, Prefix=folder_name)

    # If the folder (prefix) doesn't exist, you can create it
    if 'Contents' not in response:
        s3_client.put_object(Bucket=custombucket, Key=(folder_name + '/'))

    # UPLOAD PROGRESS FOLDER OPERATION
    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cursor = db_conn.cursor()
    object_key = 'progressReport/' + id + '/' + id + "_" + report_type

    s3 = boto3.resource('s3')

    # Update the Report Table
    update_sql = "UPDATE report SET submissionDate = %s, status = %s, late = %s WHERE student = %s AND reportType = %s"
    request_cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()

        # Compare submission dates
        if datetime.date.today() > submission_date_obj:
            request_cursor.execute(
                update_sql, (datetime.date.today(), 'submitted', 1, id, report_type))
        else:
            request_cursor.execute(
                update_sql, (datetime.date.today(), 'submitted', 0, id, report_type))

        db_conn.commit()

        print("Data inserted in MySQL RDS... uploading resume to S3...")

        # Set the content type to 'application/pdf' when uploading to S3
        s3.Object(custombucket, object_key).put(
            Body=student_progress_report,
            ContentType='application/pdf'
        )

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])

        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

    except Exception as e:
        db_conn.rollback()
        return str(e)

    print("Progress Report sucessfully submitted.")
    return render_template('UploadProgressReportOutput.html', studentName=student[1], id=session['loggedInStudent'])

# View progress report


@app.route('/viewProgressReport', methods=['GET', 'POST'])
def viewProgressReport():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')
    # Use request.args to get query parameters
    report_type = request.args.get('report_type')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"progressReport/{student_id}/{student_id}_{report_type}"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)

# Upload supporting documents


@app.route('/uploadSupportingDocuments', methods=['GET', 'POST'])
def uploadSupportingDocuments():
    id = session['loggedInStudent']

    # Retrieve the necessary documents
    acceptanceForm = request.files['acceptanceForm']
    acknowledgementForm = request.files['acknowledgementForm']
    indemnityLetter = request.files['indemnityLetter']
    supportLetter = request.files['supportLetter']
    hiredEvidence = request.files['hiredEvidence']

    objKey_acceptanceForm = 'supportingDocument/' + id + '/' + id + "_acceptanceForm"
    objKey_acknowledgementForm = 'supportingDocument/' + \
        id + '/' + id + "_acknowledgementForm"
    objKey_indemnityLetter = 'supportingDocument/' + \
        id + '/' + id + "_indemnityLetter"
    objKey_supportLetter = 'supportingDocument/' + id + '/' + id + "_supportLetter"
    objKey_hiredEvidence = 'supportingDocument/' + id + '/' + id + "_hiredEvidence"

    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cursor = db_conn.cursor()

    # Create the folder if not exist
    s3_client = boto3.client('s3')
    folder_name = 'supportingDocument/' + id  # Replace 'id' with your folder name

    # Check if the folder (prefix) already exists
    response = s3_client.list_objects_v2(
        Bucket=custombucket, Prefix=folder_name)

    # If the folder (prefix) doesn't exist, you can create it
    if 'Contents' not in response:
        s3_client.put_object(Bucket=custombucket, Key=(folder_name + '/'))

    s3 = boto3.resource('s3')

    try:
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()

        # Set the content type to 'application/pdf' when uploading to S3
        # Upload acceptance form
        s3.Object(custombucket, objKey_acceptanceForm).put(
            Body=acceptanceForm,
            ContentType='application/pdf'
        )

        # Upload acknowledgement form
        s3.Object(custombucket, objKey_acknowledgementForm).put(
            Body=acknowledgementForm,
            ContentType='application/pdf'
        )

        # Upload indemnity letter
        s3.Object(custombucket, objKey_indemnityLetter).put(
            Body=indemnityLetter,
            ContentType='application/pdf'
        )

        # Upload support letter
        s3.Object(custombucket, objKey_supportLetter).put(
            Body=supportLetter,
            ContentType='application/pdf'
        )

        # Upload hired evidence
        s3.Object(custombucket, objKey_hiredEvidence).put(
            Body=hiredEvidence,
            ContentType='application/pdf'
        )

        bucket_location = boto3.client(
            's3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])

        if s3_location is None:
            s3_location = ''
        else:
            s3_location = '-' + s3_location

    except Exception as e:
        db_conn.rollback()
        return str(e)

    print("Supporting documents sucessfully submitted.")
    return render_template('UploadSupportingDocumentsOutput.html', studentName=student[1], id=session['loggedInStudent'])

# View supporting documents
# View acceptance form
@app.route('/viewAcceptanceForm')
def viewAcceptanceForm():
  # Retrieve student's ID
    student_id = session.get('loggedInStudent')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"supportingDocument/{student_id}/{student_id}_acceptanceForm"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route('/viewAcknowledgementForm')
def viewAcknowledgementForm():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"supportingDocument/{student_id}/{student_id}_acknowledgementForm"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route('/viewIndemnityLetter')
def viewIndemnityLetter():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"supportingDocument/{student_id}/{student_id}_indemnityLetter"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route('/viewSupportLetter')
def viewSupportLetter():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"supportingDocument/{student_id}/{student_id}_supportLetter"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route('/viewHiredEvidence')
def viewHiredEvidence():
    # Retrieve student's ID
    student_id = session.get('loggedInStudent')

    if not student_id:
        return "Student not logged in."

    # Construct the S3 object key
    object_key = f"supportingDocument/{student_id}/{student_id}_hiredEvidence"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the report does not exist, return a page with a message
            return render_template('no_report_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)

# Navigate to Student Registration


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    return render_template("RegisterStudent.html")
# Register a student


@app.route("/addstud", methods=['POST'])
def add_student():
    try:
        level = request.form['level']
        cohort = request.form['cohort']
        programme = request.form['programme']
        student_id = request.form['studentId']
        email = request.form['email']
        name = request.form['name']
        ic = request.form['ic']
        mobile = request.form['mobile']
        gender = request.form['gender']
        address = request.form['address']

        insert_sql = "INSERT INTO student (studentId, studentName, IC, mobileNumber, gender, address, email, level, programme, cohort) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        cursor.execute(insert_sql, (student_id, name, ic, mobile,
                                    gender, address, email, level, programme, cohort))
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()

    # Retrieve the cohort where student belongs to
    select_sql = "SELECT startDate, endDate FROM cohort WHERE cohortId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (cohort))
        cohort = cursor.fetchone()

        if not cohort:
            return "No such cohort details exists."

    except Exception as e:
        return str(e)

    # Retrieve start date and end date
    # Convert start_date_str and end_date_str into datetime objects
    start_date_str = str(cohort[0])
    end_date_str = str(cohort[1])

    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

    # Calculate the report count for the student
    report_count = calculate_submission_count(start_date, end_date)

    # Loop and insert the details into the report table
    for i in range(1, report_count + 1):
        report_type = f'ProgressReport{i}' if i != report_count else 'FinalReport'

        # You can customize this insert SQL query based on your database schema
        insert_report_sql = "INSERT INTO report (submissionDate, reportType, status, late, remark, student) VALUES (%s, %s, %s, %s, %s, %s)"

        try:
            cursor.execute(insert_report_sql, (None, report_type,
                           'pending', 0, None, student_id))
            db_conn.commit()
        except Exception as e:
            db_conn.rollback()

    # Redirect back to the registration page with a success message
    return render_template("home.html")


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')

# Verify login


@app.route("/verifyLogin", methods=['POST', 'GET'])
def verifyLogin():
    if request.method == 'POST':
        StudentIc = request.form['StudentIc']
        Email = request.form['Email']

        # Query the database to check if the email and IC number match a record
        cursor = db_conn.cursor()
        query = "SELECT * FROM student WHERE IC = %s AND email = %s"
        cursor.execute(query, (StudentIc, Email))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # User found in the database, login successful

            # Retrieve the cohort where student belongs to
            select_sql = "SELECT startDate, endDate FROM cohort c WHERE cohortId = %s"
            cursor = db_conn.cursor()
            cursor.execute(select_sql, (user[10]))
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
            cursor.execute(supervisor_query, (user[0]))
            supervisor = cursor.fetchone()
            cursor.close()

            # Retrieve the company details
            company_query = "SELECT c.name, j.jobLocation, salary, jobPosition, jobDesc FROM company c, job j, companyApplication ca, student s WHERE c.companyId = j.company AND ca.student = s.studentId AND ca.job = j.jobId AND s.studentId = %s AND ca.`status` = 'approved'"
            cursor = db_conn.cursor()
            cursor.execute(company_query, (user[0]))
            companyDetails = cursor.fetchone()
            cursor.close()
            #######################################################################

            # Create a list to store all the retrieved data
            user_data = {
                'studentId': user[0],
                'studentName': user[1],
                'IC': user[2],
                'mobileNumber': user[3],
                'gender': user[4],
                'address': user[5],
                'email': user[6],
                'level': user[7],
                'programme': user[8],
                'cohort': user[10],
                'start_date': start_date,
                'end_date': end_date,
                # Default values if supervisor is not found
                'supervisor': supervisor if supervisor else ("N/A", "N/A"),
                # Default values if company details are not found
                'companyDetails': companyDetails if companyDetails else ("N/A", "N/A", "N/A", "N/A", "N/A")
            }

            # Set the loggedInStudent session
            session['loggedInStudent'] = user[0]

            # Redirect to the student home page with the user_data
            return render_template('studentHome.html', data=user_data)

        else:
            # User not found, login failed
            return render_template('LoginStudent.html', msg="Access Denied: Invalid Email or Ic Number")

# GWEE YONG SEAN
# Function to create a database connection context


def get_db_connection():
    customhost = 'employee.cgtpcksgf7rv.us-east-1.rds.amazonaws.com'
    customuser = 'aws_user'
    custompass = 'Bait3273'
    customdb = 'employee'

    return connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )


@app.route("/displayJobFind", methods=['POST', 'GET'])
def displayAllJobs():
    # Get filter values from the form
    search_company = request.form.get('search-company', '')
    search_title = request.form.get('search-title', '')
    search_state = request.form.get('search-state', 'All')
    search_allowance = request.form.get('search-allowance', '1800')

    # Construct the base SQL query with a JOIN between the job and company tables
    select_sql = """
        SELECT j.*, c.name AS company_name
        FROM job j
        LEFT JOIN company c ON j.company = c.companyId
        WHERE 1
    """

    # Add filter conditions based on form inputs
    if search_company:
        select_sql += f" AND c.name LIKE '%{search_company}%'"

    if search_title:
        select_sql += f" AND j.jobPosition LIKE '%{search_title}%'"

    if search_state != 'All':
        select_sql += f" AND j.jobLocation LIKE '%{search_state}%'"

    if search_allowance:
        select_sql += f" AND j.salary <= {search_allowance}"

    # Add the condition to check the company's status
    select_sql += " AND c.status = 'activated'"

    # Add the condition to check numOfOperating greater than 0
    select_sql += " AND j.numOfOperating > 0"

    try:
        with get_db_connection() as db_conn:
            with db_conn.cursor() as cursor:
                cursor.execute(select_sql)
                jobs = cursor.fetchall()

                job_objects = []
                for job in jobs:
                    job_id = job[0]
                    publish_date = job[1]
                    job_type = job[2]
                    job_position = job[3]
                    qualification_level = job[4]
                    job_requirement = job[6]
                    job_location = job[7]
                    salary = job[8]
                    company_id = job[10]
                    company_name = job[12]  # Extracted from the JOINed column

                    # Generate the S3 image URL using custombucket and customregion
                    company_image_file_name_in_s3 = "comp-id-" + \
                        str(company_id)+"_image_file"
                    s3 = boto3.client('s3', region_name=customregion)
                    bucket_name = custombucket

                    response = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': bucket_name,
                                'Key': company_image_file_name_in_s3},
                        ExpiresIn=1000  # Adjust the expiration time as needed
                    )
                    job_object = {
                        "job_id": job_id,
                        "publish_date": publish_date,
                        "job_type": job_type,
                        "job_position": job_position,
                        "qualification_level": qualification_level,
                        "job_requirement": job_requirement,
                        "job_location": job_location,
                        "salary": salary,
                        "company_name": company_name,
                        "company_id": company_id,
                        "image_url": response
                    }

                    job_objects.append(job_object)

        return render_template('SearchCompany.html', jobs=job_objects)

    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {str(e)}")
        return "An error occurred while fetching job data."


@app.route("/displayJobDetails", methods=['POST', 'GET'])
def display_job_details():
    if request.method == 'POST':
        # Get the selected job_id from the form
        selected_job_id = request.form.get('transfer-id')

        apply_student_id = session.get('loggedInStudent')

        select_sql = """
        SELECT j.*, c.name AS company_name, i.name AS industry_name, c.email AS company_email, c.phone AS company_phone
        FROM job j
        LEFT JOIN company c ON j.company = c.companyId
        LEFT JOIN industry i on j.industry = i.industryId
        WHERE jobId =%s
        """
        cursor = db_conn.cursor()
        try:
            cursor.execute(select_sql, (selected_job_id,))
            job = cursor.fetchone()

            if not job:
                return "No such job exists."
        except Exception as e:
            return str(e)

        # Initialize job_objects as an empty list
        job_objects = []

        # Append job details to job_objects
        job_id = job[0]
        publish_date = job[1]
        job_type = job[2]
        job_position = job[3]
        qualification_level = job[4]
        job_description = job[5]
        job_requirement = job[6]
        job_location = job[7]
        salary = job[8]
        num_of_operate = job[9]
        company_id = job[10]
        company_name = job[12]  # Extracted from the JOINed column
        industry_name = job[13]
        company_email = job[14]
        company_phone = job[15]

        # Generate the S3 image URL using custombucket and customregion
        company_image_file_name_in_s3 = "comp-id-" + \
            str(company_id) + "_image_file"
        s3 = boto3.client('s3', region_name=customregion)
        bucket_name = custombucket

        response = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name,
                    'Key': company_image_file_name_in_s3},
            ExpiresIn=1000  # Adjust the expiration time as needed
        )

        job_object = {
            "job_id": job_id,
            "publish_date": publish_date,
            "job_type": job_type,
            "job_position": job_position,
            "qualification_level": qualification_level,
            "job_description": job_description,
            "job_requirement": job_requirement,
            "job_location": job_location,
            "salary": salary,
            "company_name": company_name,
            "company_id": company_id,
            "num_of_operate": num_of_operate,
            "industry_name": industry_name,
            "company_email": company_email,
            "company_phone": company_phone,
            "image_url": response
        }

        job_objects.append(job_object)

        job_applied = False  # Initialize as False by default

        # Check if the student has applied for this job
        check_application_sql = """
        SELECT COUNT(*) as total
        FROM companyApplication
        WHERE student = %s AND job = %s
        """

        cursor.execute(check_application_sql,
                       (apply_student_id, selected_job_id))
        application_count = cursor.fetchone()

        if application_count and application_count[0] > 0:
            job_applied = True

        return render_template('JobDetail.html', jobs=job_objects, job_applied=job_applied)

    return render_template('SearchCompany.html', jobs=job_objects)


@app.template_filter('replace_and_keep_hyphen')
def replace_and_keep_hyphen(s):
    return s.replace('-', '<br>-').replace('<br>-', '-', 1)


@app.route("/studentApplyCompany", methods=['POST', 'GET'])
def studentApplyCompany():

    id = session['loggedInStudent']

    # Create a cursor
    cursor = db_conn.cursor()

    try:
        # Get the search query from the request (if provided)
        search_query = request.args.get('search', '')

        # Get the total number of applications
        total_applications = get_total_applications(cursor, search_query)

        # Define the number of applications per page
        per_page = 6  # Adjust as needed

        # Get the current page from the request or default to 1
        current_page = request.args.get('page', default=1, type=int)

        # Calculate the total number of pages
        num_pages = (total_applications + per_page - 1) // per_page

        # Calculate the start and end indices for the current page
        start_index = (current_page - 1) * per_page
        end_index = start_index + per_page

        # Get the applications for the current page
        applications = get_applications(
            cursor, session['loggedInStudent'], per_page, start_index, search_query)

        return render_template("trackApplication.html", applications=applications, current_page=current_page, num_pages=num_pages, id=id)

    except Exception as e:
        # Handle exceptions here
        return "An error occurred: " + str(e)

    finally:
        cursor.close()


def get_total_applications(cursor, search_query):
    # Execute the SELECT COUNT(*) query to get the total row count
    select_sql = """
    SELECT COUNT(*) as total
    FROM companyApplication ca
    LEFT JOIN job j ON ca.job = j.jobId
    LEFT JOIN company c ON j.company = c.companyId
    WHERE ca.student=%s
    """

    if search_query:
        select_sql += " AND c.name LIKE %s"
        cursor.execute(
            select_sql, (session['loggedInStudent'], f"%{search_query}%"))
    else:
        cursor.execute(select_sql, (session['loggedInStudent'],))

    apply_result = cursor.fetchone()
    return apply_result[0]


def calculate_pagination(total, per_page):
    num_pages = (total + per_page - 1) // per_page
    current_page = request.args.get('page', 1, type=int)
    start_index = (current_page - 1) * per_page
    end_index = start_index + per_page
    return num_pages, current_page, start_index, end_index


def get_applications(cursor, student_id, per_page, start_index, search_query):
    select_application = """
    SELECT ca.*, c.name AS company_name, j.jobPosition AS job_position, j.jobLocation AS job_location
    FROM companyApplication ca
    LEFT JOIN job j ON ca.job = j.jobId
    LEFT JOIN company c ON j.company = c.companyId
    WHERE ca.student=%s
    """

    if search_query:
        select_application += " AND c.name LIKE %s"

    select_application += " LIMIT %s OFFSET %s"

    if search_query:
        cursor.execute(select_application, (student_id,
                       f"%{search_query}%", per_page, start_index))
    else:
        cursor.execute(select_application, (student_id, per_page, start_index))

    application_track = cursor.fetchall()

    application_objects = []
    for row in application_track:
        application_id = row[0]
        applyDateTime = row[1]
        status = row[2]
        student = row[3]
        job = row[4]
        company_name = row[5]
        job_position = row[6]
        job_location = row[7]

        application_object = {
            "application_id": application_id,
            "applyDateTime": applyDateTime,
            "status": status,
            "student": student,
            "job": job,
            "company_name": company_name,
            "job_position": job_position,
            "job_location": job_location
        }
        application_objects.append(application_object)

    return application_objects


@app.route("/applyCompany", methods=['POST'])
def applyCompany():
    try:
        # Get the selected job_id from the form
        apply_job_id = request.form.get('apply-job-id')
        apply_student_id = session['loggedInStudent']
        now = datetime.datetime.now()

        # Create a cursor
        cursor = db_conn.cursor()

        # Get the next available application ID (you may need to adjust this logic)
        cursor.execute("SELECT MAX(applicationId) FROM companyApplication")
        max_id = cursor.fetchone()[0]
        company_id = max_id + 1 if max_id is not None else 1

        # Insert the application record into the database
        insert_application_sql = """
        INSERT INTO companyApplication (applicationId, applyDateTime, status, student, job)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_application_sql, (company_id, now,
                       'pending', apply_student_id, apply_job_id))
        db_conn.commit()

    except Exception as e:
        db_conn.rollback()
    # Handle the exception if needed

    finally:
        cursor.close()

    # This line is outside the try-except block
    return redirect(url_for("studentApplyCompany"))


@app.route('/downloadStudF04', methods=['GET'])
def download_StudF04():
    # Construct the S3 object key
    object_key = f"forms/FOCS_StudF04.docx"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the resume does not exist, return a page with a message
            return render_template('no_resume_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)

# DOWNLOAD FOCS_StudF05.docx


@app.route('/downloadStudF05', methods=['GET'])
def download_StudF05():
    # Construct the S3 object key
    object_key = f"forms/FOCS_StudF05.docx"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the resume does not exist, return a page with a message
            return render_template('no_resume_found.html')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)

# DOWNLOAD FOCS_StudF06.pdf (Student Support Letter)


@app.route('/downloadStudF06', methods=['GET'])
def download_StudF06():
    id = session.get('loggedInStudent')

    select_sql = "SELECT * FROM student WHERE studentId = %s"
    cohort_sql = "SELECT startDate, endDate FROM cohort c WHERE cohortId = %s"
    cursor = db_conn.cursor()

    try:
        # Retrieve student data
        cursor.execute(select_sql, (id))
        student = cursor.fetchone()

        # Retrieve cohort data
        cursor.execute(cohort_sql, (student[10]))
        cohort = cursor.fetchone()

        db_conn.commit()

        # Format dates
        todayDate = datetime.datetime.now().strftime('%d-%B-%Y')
        startDate = cohort[0].strftime('%d-%B-%Y')
        endDate = cohort[1].strftime('%d-%B-%Y')

        # Prepare the data as a list
        data = {
            'todayDate': todayDate,
            'startDate': startDate,
            'endDate': endDate,
            'studentId': student[0],
            'studentName': student[1],
            'programme': student[8]
        }
=======
@app.route('/applyFilter', methods=['POST', 'GET'])
def applyFilter():
    # Extract filter criteria from the form
    category = request.form.get('category')
    status = request.form.get('status')
    network_details = get_network_details()

    try:
        # Create a cursor
        cursor = db_conn.cursor()

        # Construct the SQL query based on the selected filters
        sql = "SELECT * FROM contact WHERE 1=1"

        if category != '*':
            sql += f" AND category = '{category}'"
        if status != '*':
            sql += f" AND status = '{status}'"

        cursor.execute(sql)

        # Fetch the filtered data
        contact_details = cursor.fetchall()

        if 'name' in session and 'email' in session:
            name = session['name']
            email = session['email']
            if email == 'hhm@gmail.com' and name == 'Ho Hong Meng':
                session['loggedIn'] = 'hhm'
                session['name'] = 'Ho Hong Meng'
            elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
                session['loggedIn'] = 'css'
                session['name'] = 'Cheong Soo Siew'

        return render_template('adminContactUs.html', contact_details=contact_details, network_details=network_details, name=session['name'])
>>>>>>> 1e5970868ab72e6bdaeb6feb8088c2323e7d8284

    except Exception as e:
        db_conn.rollback()
        return str(e)

<<<<<<< HEAD
    # Render the HTML template with the data
    rendered_template = render_template('StudentSupportLetter.html', data=data)

    # Use pdfkit to generate the PDF
    html = HTML(string=rendered_template, base_url=request.url)
    pdf = html.write_pdf(presentational_hints=True)

    # Create a response object with the PDF data
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline;filename={id}_SupportLetter.pdf'

    return response


# KU XIN YAU AND LOKE KOK LAM :))))))))) LU ZHONG <333
@app.route("/leclogin")
def LecLoginPage():
    return render_template('LecturerLogin.html')


@app.route("/loginlec", methods=['GET', 'POST'])
def LoginLec():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        select_sql = "SELECT * FROM lecturer WHERE email = %s AND password = %s"
        cursor = db_conn.cursor()

        try:
            cursor.execute(select_sql, (email, password,))
            lecturer = cursor.fetchone()

            if lecturer:
                session['loginLecturer'] = lecturer[0]

                # Fetch the S3 image URL based on emp_id
                lec_image_file_name_in_s3 = "lec-id-" + \
                    str(lecturer[0]) + "_image_file"
                s3 = boto3.client('s3')
                bucket_name = custombucket

                try:
                    response = s3.generate_presigned_url('get_object',
                                                         Params={'Bucket': bucket_name,
                                                                 'Key': lec_image_file_name_in_s3},
                                                         ExpiresIn=1000)  # Adjust the expiration time as needed

                except Exception as e:
                    return str(e)

                select_sql = "SELECT s.*, c.name, ca.status, co.startDate, co.endDate, r.* FROM student s LEFT JOIN companyApplication ca ON s.studentId = ca.student LEFT JOIN job j ON ca.job = j.jobId LEFT JOIN company c ON j.company = c.companyId LEFT JOIN cohort co ON s.cohort = co.cohortId LEFT JOIN report r ON s.studentId = r.student WHERE s.supervisor = %s ORDER BY s.level, co.startDate DESC, s.studentId, r.reportId"

                cursor.execute(select_sql, (lecturer[0],))
                raw_students = cursor.fetchall()

                if raw_students:
                    # Process the raw data
                    students = {}
                    for row in raw_students:
                        studId = row[0]
                        if studId not in students:
                            students[studId] = {
                                'studentId': studId,
                                'name': row[1],
                                'programme': row[8],
                                'email': row[6],
                                'gender': row[4],
                                'hp': row[3],
                                'level': row[7],
                                'cohortId': row[10],
                                'company': row[11],
                                'compStatus': row[12],
                                'startDate': row[13],
                                'endDate': row[14],
                                'reports': []
                            }
                        students[studId]['reports'].append(
                            {'reportType': row[17], 'reportStatus': row[18], 'reportLate': row[19]})

                    return render_template('LecturerHome.html', lecturer=lecturer, students=students, noReport=len(students[raw_students[0][0]]['reports']), image_url=response)

                else:
                    return render_template('LecturerHome.html', lecturer=lecturer, students=raw_students, image_url=response)

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

    return render_template('LecturerLogin.html', msg="Access Denied : Invalid email or password")


@app.route("/logoutlec")
def LogoutLec():
    if 'loginLecturer' in session:
        session.pop('loginLecturer', None)
    return render_template('home.html')


@app.route("/lecHome")
def LecHome():
    if 'loginLecturer' in session:
        lectId = session['loginLecturer']

        select_sql = "SELECT * FROM lecturer WHERE lectId = %s"
        cursor = db_conn.cursor()

        try:
            cursor.execute(select_sql, (lectId,))
            lecturer = cursor.fetchone()

            if lecturer:
                # Fetch the S3 image URL based on emp_id
                lec_image_file_name_in_s3 = "lec-id-" + \
                    str(lecturer[0]) + "_image_file"
                s3 = boto3.client('s3')
                bucket_name = custombucket

                try:
                    response = s3.generate_presigned_url('get_object',
                                                         Params={'Bucket': bucket_name,
                                                                 'Key': lec_image_file_name_in_s3},
                                                         ExpiresIn=1000)  # Adjust the expiration time as needed

                except Exception as e:
                    return str(e)

                select_sql = "SELECT s.*, c.name, ca.status, co.startDate, co.endDate, r.* FROM student s LEFT JOIN companyApplication ca ON s.studentId = ca.student LEFT JOIN job j ON ca.job = j.jobId LEFT JOIN company c ON j.company = c.companyId LEFT JOIN cohort co ON s.cohort = co.cohortId LEFT JOIN report r ON s.studentId = r.student WHERE s.supervisor = %s ORDER BY s.level, co.startDate DESC, s.studentId, r.reportId"

                cursor.execute(select_sql, (lecturer[0],))
                raw_students = cursor.fetchall()

                # Process the raw data
                if raw_students:
                    students = {}
                    for row in raw_students:
                        studId = row[0]
                        if studId not in students:
                            students[studId] = {
                                'studentId': studId,
                                'name': row[1],
                                'programme': row[8],
                                'email': row[6],
                                'gender': row[4],
                                'hp': row[3],
                                'level': row[7],
                                'cohortId': row[10],
                                'company': row[11],
                                'compStatus': row[12],
                                'startDate': row[13],
                                'endDate': row[14],
                                'reports': []
                            }
                        students[studId]['reports'].append(
                            {'reportType': row[17], 'reportStatus': row[18], 'reportLate': row[19]})
                else:
                    return render_template('LecturerHome.html', lecturer=lecturer, students=raw_students, image_url=response)
        except Exception as e:
            return str(e)

        finally:
            cursor.close()

        return render_template('LecturerHome.html', lecturer=lecturer, students=students, noReport=len(students[raw_students[0][0]]['reports']), image_url=response)

    else:
        return render_template('LecturerLogin.html')


@app.route("/lecStudentDetails", methods=['GET'])
def LecStudentDetails():
    if 'loginLecturer' in session and request.args.get('studentId') is not None and request.args.get('studentId') != '':
        lectId = session['loginLecturer']
        studId = request.args.get('studentId')

        select_sql = "SELECT * FROM student WHERE supervisor = %s AND studentID = %s"
        cursor = db_conn.cursor()

        try:
            cursor.execute(select_sql, (lectId, studId,))
            student = cursor.fetchone()

            if student:
                select_sql = "SELECT * FROM report WHERE student = %s"

                cursor.execute(select_sql, (studId,))
                reports = cursor.fetchall()

                return render_template('LecStudDetails.html', student=student, reports=reports)

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

    return render_template('/lecHome')


@app.route("/updateReportStatus", methods=['POST'])
def LecUpdateReportStatus():
    if request.method == 'POST':
        studId = request.form['studentId']
        reportType = request.form['reportType']
        remark = request.form['remark']
        if request.form['status'] == 'Approve':
            status = 'approved'
        elif request.form['status'] == 'Reject':
            status = 'rejected'

        if remark.strip():
            update_sql = "UPDATE report SET status = %s, remark = %s WHERE student = %s AND reportType = %s"
        else:
            update_sql = "UPDATE report SET status = %s WHERE student = %s AND reportType = %s"
        cursor = db_conn.cursor()

        try:
            if remark.strip():
                cursor.execute(
                    update_sql, (status, remark, studId, reportType,))
            else:
                cursor.execute(update_sql, (status, studId, reportType,))
            db_conn.commit()

        except Exception as e:
            db_conn.rollback()
            return str(e)

        finally:
            cursor.close()

    if 'loginLecturer' in session:
        lectId = session['loginLecturer']

        select_sql = "SELECT * FROM student WHERE supervisor = %s AND studentID = %s"
        cursor = db_conn.cursor()

        try:
            cursor.execute(select_sql, (lectId, studId,))
            student = cursor.fetchone()

            if student:
                select_sql = "SELECT * FROM report WHERE student = %s"

                cursor.execute(select_sql, (studId,))
                reports = cursor.fetchall()

                return render_template('LecStudDetails.html', student=student, reports=reports)

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

    return render_template('LecturerLogin.html')

# Download resume from S3 (based on Student Id)


@app.route('/lecViewDoc', methods=['GET', 'POST'])
def LecViewDoc():
    # Retrieve student's ID
    studId = request.args.get('studentId')
    type = request.args.get('type')

    if not studId and not type:
        return "Student undefined or Document error"

    # Construct the S3 object key
    if (type == 'resume'):
        object_key = f"resume/{studId}_resume"
    elif (type == 'comAcc'):
        object_key = f"supportingDocument/{studId}/{studId}_acceptanceForm"
    elif (type == 'parentAck'):
        object_key = f"supportingDocument/{studId}/{studId}_acknowledgementForm"
    elif (type == 'indemnity'):
        object_key = f"supportingDocument/{studId}/{studId}_indemnityLetter"
    elif (type == 'hiredEvi'):
        object_key = f"supportingDocument/{studId}/{studId}_hiredEvidence"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the resume does not exist, return a page with a message
            return render_template('LecStudDetails.html', msg='not found')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route('/lecViewReport', methods=['GET', 'POST'])
def LecViewReport():
    # Retrieve student's ID
    studId = request.args.get('studentId')
    type = request.args.get('reportType')

    if not studId and not type:
        return "Student undefined or Document error"

    # Construct the S3 object key
    object_key = f"progressReport/{studId}/{studId}_{type}"

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': custombucket,
                'Key': object_key,
                'ResponseContentDisposition': 'inline',
            },
            ExpiresIn=3600  # Set the expiration time (in seconds) as needed
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            # If the resume does not exist, return a page with a message
            return render_template('LecStudDetails.html', msg='no found')
        else:
            return str(e)

    # Redirect the user to the URL of the PDF file
    return redirect(response)


@app.route("/fetchdata", methods=['POST'])
def GetEmp():
    lec_id = session['loginLecturer']
    select_sql = "SELECT * FROM lecturer WHERE lectId = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (lec_id,))
        lecturer = cursor.fetchone()

        if not lecturer:
            return "Lecturer not found"

        lec_id = lecturer[0]
        passowrd = lecturer[1]
        name = lecturer[2]
        gender = lecturer[3]
        email = lecturer[4]
        expertis = lecturer[5]

        # Fetch the S3 image URL based on emp_id
        lec_image_file_name_in_s3 = "lec-id-" + str(lec_id) + "_image_file"
        s3 = boto3.client('s3')
        bucket_name = custombucket

        try:
            response = s3.generate_presigned_url('get_object',
                                                 Params={'Bucket': bucket_name,
                                                         'Key': lec_image_file_name_in_s3},
                                                 ExpiresIn=1000)  # Adjust the expiration time as needed

            # You can return the employee details along with the image URL
            lec_details = {
                "lec_id": lec_id,
                "passowrd": passowrd,
                "name": name,
                "gender": gender,
                "email": email,
                "expertis": expertis,
                "image_url": response
            }

            return render_template('GetLecOutput.html', image_url=response, id=lec_id, psw=passowrd, name=name, email=email, expertise=expertis, gender=gender)

        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


@app.route("/editlec", methods=['POST'])
def UpdateEmp():
    lec_id = request.form['lec_id']
    password = request.form['password']
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    expertise = request.form['expertise']
    lec_image_file = request.files['lec_image_file']

    update_sql = "UPDATE lecturer SET password=%s, name=%s, gender=%s, email=%s, expertise=%s WHERE lectId=%s"
    cursor = db_conn.cursor()

    try:
        # Check if the employee exists
        check_sql = "SELECT * FROM lecturer WHERE lectId = %s"
        cursor.execute(check_sql, (lec_id,))
        existing_lecturer = cursor.fetchone()

        if not existing_lecturer:
            return "Lecturer not found"

        cursor.execute(update_sql, (password, name,
                       gender, email, expertise, lec_id))
        db_conn.commit()
        lec_name = "" + name

        if lec_image_file.filename != "":
            # Update image file in S3
            lec_image_file_name_in_s3 = "lec-id-" + str(lec_id) + "_image_file"
            s3 = boto3.resource('s3')

            try:
                print("Data updated in MySQL RDS... updating image in S3...")
                s3.Bucket(custombucket).put_object(
                    Key=lec_image_file_name_in_s3, Body=lec_image_file)
                bucket_location = boto3.client(
                    's3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location.get('LocationConstraint'))

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' + s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    lec_image_file_name_in_s3)

            except Exception as e:
                return str(e)

    finally:
        cursor.close()
    return render_template('UpdateLecOutput.html', name=name)


@app.route("/displayStudent", methods=['GET', 'POST'])
def GetStudent():

    action = request.form['action']
    id = session['loginLecturer']

    if action == 'drop':
        select_sql = f"SELECT * FROM student WHERE supervisor LIKE '%{id}%'"
        cursor = db_conn.cursor()

    if action == 'pickUp':
        select_sql = f"SELECT * FROM student WHERE supervisor IS NULL"
        cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql)
        students = cursor.fetchall()  # Fetch all students

        student_list = []

        for student in students:
            student_id = student[0]
            name = student[1]
            gender = student[4]
            email = student[6]
            level = student[7]
            programme = student[8]
            cohort = student[10]

            try:
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "gender": gender,
                    "email": email,
                    "level": level,
                    "programme": programme,
                    "cohort": cohort,
                }

                # Append the student's dictionary to the student_list
                student_list.append(student_data)

            except Exception as e:
                return str(e)

        if action == 'drop':
            return render_template('DropStudent.html', student_list=student_list, id=id, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())

        if action == 'pickUp':
            return render_template('PickUpStudent.html', id=id, student_list=student_list, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


@app.route("/pickUp", methods=['GET', 'POST'])
def PickStudent():
    selected_student_ids = request.form.getlist('selected_students[]')
    # selected_student_name = request.form.getlist('selected_studentsNames[]')
    lec_id = session['loginLecturer']
    # student_id = request.form['student_id']
    # name = request.form['name']
    # gender = request.form['gender']
    # email = request.form['email']
    # level = request.form['level']
    # programme = request.form['programme']
    # cohort = request.files['cohort']

    update_sql = "UPDATE student SET supervisor=%s WHERE studentId=%s"
    cursor = db_conn.cursor()

    student_list = []

    try:
        # Check if the employee exists
        for student_id in selected_student_ids:
            update_sql = "UPDATE student SET supervisor=%s WHERE studentId=%s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (lec_id, student_id))
            db_conn.commit()

    finally:
        cursor.close()

    cursor = db_conn.cursor()
    student_list = []

    try:

        for student_id in selected_student_ids:
            select_sql = "SELECT * FROM student WHERE supervisor= %s and studentId = %s "
            cursor.execute(select_sql, (lec_id, student_id))
            students = cursor.fetchall()  # Fetch all students

            for student in students:
                student_id = student[0]
                name = student[1]
                gender = student[4]
                email = student[6]
                level = student[7]
                programme = student[8]
                cohort = student[10]
                try:
                    student_data = {
                        "student_id": student_id,
                        "name": name,
                        "gender": gender,
                        "email": email,
                        "level": level,
                        "programme": programme,
                        "cohort": cohort,
                    }

                    # Append the student's dictionary to the student_list
                    student_list.append(student_data)

                except Exception as e:
                    return str(e)

    except Exception as e:
        return str(e)
    return render_template('PickedUpOutput.html', student_list=student_list)


@app.route("/drop", methods=['GET', 'POST'])
def DropStudent():
    selected_student_ids = request.form.getlist('selected_students[]')
    selected_student_name = request.form.getlist('selected_students[]')
    # student_id = request.form['student_id']
    # name = request.form['name']
    # gender = request.form['gender']
    # email = request.form['email']
    # level = request.form['level']
    # programme = request.form['programme']
    # cohort = request.files['cohort']

    update_sql = "UPDATE student SET supervisor='' WHERE studentId=%s"
    cursor = db_conn.cursor()
    student_list = []

    try:
        for student_id in selected_student_ids:
            update_sql = "UPDATE student SET supervisor = NULL WHERE studentId=%s"
            cursor = db_conn.cursor()
            cursor.execute(update_sql, (student_id))
            db_conn.commit()

    finally:
        cursor.close()

    cursor = db_conn.cursor()
    try:

        for student_id in selected_student_ids:
            select_sql = "SELECT * FROM student WHERE studentId = %s "
            cursor.execute(select_sql, (student_id))
            students = cursor.fetchall()  # Fetch all students

            for student in students:
                student_id = student[0]
                name = student[1]
                gender = student[4]
                email = student[6]
                level = student[7]
                programme = student[8]
                cohort = student[10]
                try:
                    student_data = {
                        "student_id": student_id,
                        "name": name,
                        "gender": gender,
                        "email": email,
                        "level": level,
                        "programme": programme,
                        "cohort": cohort,
                    }

                    # Append the student's dictionary to the student_list
                    student_list.append(student_data)

                except Exception as e:
                    return str(e)

    except Exception as e:
        return str(e)
    return render_template('DropOutput.html', student_list=student_list)


@app.route("/filterStudent", methods=['GET', 'POST'])
def FilterStudent():

    level = request.form['search-level']
    programme = request.form['search-programme']
    cohort = request.form['search-cohort']

    select_sql = "SELECT * FROM student WHERE supervisor IS NULL"
    cursor = db_conn.cursor()

    if level != 'All':
        select_sql += f" AND level LIKE '%{level}%'"
    if programme != 'All':
        select_sql += f" AND programme LIKE '%{programme}%'"
    if cohort != 'All':
        select_sql += f" AND cohort LIKE '%{cohort}%'"

    try:
        cursor.execute(select_sql)
        students = cursor.fetchall()  # Fetch all students

        stu = []
        student_list = []

        for student in students:
            student_id = student[0]
            name = student[1]
            gender = student[4]
            email = student[6]
            level = student[7]
            programme = student[8]
            cohort = student[10]

            # Fetch the S3 image URL based on student_id
            stu_image_file_name_in_s3 = "stu-id-" + \
                str(student_id) + "_image_file"
            s3 = boto3.client('s3')
            bucket_name = custombucket

            try:
                response = s3.generate_presigned_url('get_object',
                                                     Params={'Bucket': bucket_name,
                                                             'Key': stu_image_file_name_in_s3},
                                                     ExpiresIn=1000)  # Adjust the expiration time as needed

                # Create a dictionary for each student with their details and image URL
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "gender": gender,
                    "email": email,
                    "level": level,
                    "programme": programme,
                    "cohort": cohort,
                }

                # Append the student's dictionary to the student_list
                student_list.append(student_data)

            except Exception as e:
                return str(e)

        return render_template('PickUpStudent.html', id=id, student_list=student_list, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


@app.route("/filterPickedStudent", methods=['GET', 'POST'])
def FilterPickedStudent():

    level = request.form['search-level']
    programme = request.form['search-programme']
    cohort = request.form['search-cohort']
    id = session['loginLecturer']

    select_sql = f"SELECT * FROM student WHERE supervisor = '{id}'"
    cursor = db_conn.cursor()

    if level != 'All':
        select_sql += f" AND level LIKE '%{level}%'"
    if programme != 'All':
        select_sql += f" AND programme LIKE '%{programme}%'"
    if cohort != 'All':
        select_sql += f" AND cohort LIKE '%{cohort}%'"

    try:
        cursor.execute(select_sql)
        students = cursor.fetchall()  # Fetch all students

        stu = []
        student_list = []

        for student in students:
            student_id = student[0]
            name = student[1]
            gender = student[4]
            email = student[6]
            level = student[7]
            programme = student[8]
            cohort = student[10]

            # Fetch the S3 image URL based on student_id
            stu_image_file_name_in_s3 = "stu-id-" + \
                str(student_id) + "_image_file"
            s3 = boto3.client('s3')
            bucket_name = custombucket

            try:
                response = s3.generate_presigned_url('get_object',
                                                     Params={'Bucket': bucket_name,
                                                             'Key': stu_image_file_name_in_s3},
                                                     ExpiresIn=1000)  # Adjust the expiration time as needed

                # Create a dictionary for each student with their details and image URL
                student_data = {
                    "student_id": student_id,
                    "name": name,
                    "gender": gender,
                    "email": email,
                    "level": level,
                    "programme": programme,
                    "cohort": cohort,
                }

                # Append the student's dictionary to the student_list
                student_list.append(student_data)

            except Exception as e:
                return str(e)

        return render_template('DropStudent.html', id=id, student_list=student_list, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())

    except Exception as e:
        return str(e)

    finally:
        cursor.close()


####################### ADMIN #########################
@app.route('/login_admin')
def login_admin():
    return render_template('LoginAdmin.html')


@app.route("/logoutAdmin")
def logoutAdmin():
    return render_template('home.html')


@app.route("/loginAdmin", methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        admin_id = request.form['admin_ID']
        password = request.form['password']

        if admin_id != "a" or password != "1":
            return render_template('LoginAdmin.html')
        # session['logedInAdmin'] = str(admin_id)

    return displayRequest()


@app.route("/displayRequest", methods=['GET', 'POST'])
def displayRequest():
    select_sql = "SELECT * FROM request WHERE status ='pending'"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql)
        requests = cursor.fetchall()  # Fetch all request

        request_list = []

        for requestEdit in requests:
            req_id = requestEdit[0]
            req_attribute = requestEdit[1]
            req_change = requestEdit[2]
            req_reason = requestEdit[4]
            req_studentId = requestEdit[5]

            try:
                request_data = {
                    "id": req_id,
                    "attribute": req_attribute,
                    "change": req_change,
                    "reason": req_reason,
                    "studentId": req_studentId,
                }

                # Append the student's dictionary to the student_list
                request_list.append(request_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('AdminDashboard.html', request_list=request_list, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())


@app.route("/approveReq", methods=['GET', 'POST'])
def approveReq():
    selected_request_ids = request.form.getlist('selected_requests[]')
    action = request.form['action']

    resultAttributes = []  # Store the result attributes here
    resultChange = []
    resultStudentId = []
    resultOri = []
    request_list = []

    if action == 'approve':
        try:
            cursor = db_conn.cursor()

            for request_id in selected_request_ids:
                get_attribute = "SELECT attribute FROM request WHERE requestId=%s"
                cursor.execute(get_attribute, (request_id,))
                attribute_result = cursor.fetchone()  # Fetch the result for this request_id

                get_change = "SELECT newData FROM request WHERE requestId=%s"
                cursor.execute(get_change, (request_id,))
                change_result = cursor.fetchone()  # Fetch the result for this request_id

                get_studentId = "SELECT studentId FROM request WHERE requestId=%s"
                cursor.execute(get_studentId, (request_id,))
                studentId_result = cursor.fetchone()  # Fetch the result for this request_id

                if attribute_result:
                    # Append the attribute value to the list
                    resultAttributes.append(attribute_result[0])

                if change_result:
                    # Append the change value to the list
                    resultChange.append(change_result[0])

                if studentId_result:
                    # Append the change value to the list
                    resultStudentId.append(studentId_result[0])

                # get ori data
                get_ori = f"SELECT `{attribute_result[0]}` FROM student WHERE studentId=%s"
                cursor.execute(get_ori, (studentId_result,))
                ori_result = cursor.fetchone()  # Fetch the result for this request_id

                if ori_result:
                    # Append the change value to the list
                    resultOri.append(ori_result[0])

                # Use string formatting to create the SQL query
                update_sql = f"UPDATE student SET `{attribute_result[0]}` = %s WHERE studentId=%s"
                cursor.execute(
                    update_sql, (change_result[0], studentId_result[0]))
                db_conn.commit()

            db_conn.commit()

        finally:
            cursor.close()

        # update the status of the request
        try:
            for request_id in selected_request_ids:
                update_sql = "UPDATE request SET status = 'approved' WHERE requestId=%s"
                cursor = db_conn.cursor()
                cursor.execute(update_sql, (request_id,))
                db_conn.commit()

        finally:
            cursor.close()

        return render_template('requestOutput.html', resultAttributes=resultAttributes, resultChange=resultChange, resultStudentId=resultStudentId, resultOri=resultOri)

    if action == 'reject':
        try:
            cursor = db_conn.cursor()

            for request_id in selected_request_ids:
                update_sql = "UPDATE request SET status = 'rejected' WHERE requestId=%s"
                cursor.execute(update_sql, (request_id,))
                db_conn.commit()
        finally:
            cursor.close()

        for request_id in selected_request_ids:
            select_sql = "SELECT * FROM request WHERE status ='rejected' AND requestId=%s"
            cursor = db_conn.cursor()

            try:
                cursor.execute(select_sql, (request_id,))
                requests = cursor.fetchall()  # Fetch all request

                for requestEdit in requests:
                    req_id = requestEdit[0]
                    req_attribute = requestEdit[1]
                    req_change = requestEdit[2]
                    req_reason = requestEdit[4]
                    req_studentId = requestEdit[5]

                    try:
                        request_data = {
                            "id": req_id,
                            "attribute": req_attribute,
                            "change": req_change,
                            "reason": req_reason,
                            "studentId": req_studentId,
                        }

                        # Append the student's dictionary to the student_list
                        request_list.append(request_data)

                    except Exception as e:
                        return str(e)

            except Exception as e:
                return str(e)

            finally:
                cursor.close()

        return render_template('requestRejectOutput.html', request_list=request_list)


@app.route("/filterRequest", methods=['GET', 'POST'])
def FilterRequest():

    level = request.form['search-level']
    programme = request.form['search-programme']  # Check if the field exists
    cohort = request.form['search-cohort']
    attribute = request.form['search-attribute']

    select_sql = "SELECT * FROM request r ,student s WHERE status ='pending' AND r.studentId = s.studentId "
    cursor = db_conn.cursor()

    if level != 'All':
        select_sql += f" AND s.level LIKE '%{level}%'"
    if programme != 'All':
        select_sql += f" AND s.programme LIKE '%{programme}%'"
    if cohort != 'All':
        select_sql += f" AND s.cohort LIKE '%{cohort}%'"
    if attribute != 'All':
        select_sql += f" AND r.attribute LIKE '%{attribute}%'"

    select_sql += " Order by r.requestId,r.studentId"

    try:
        cursor.execute(select_sql)
        requests = cursor.fetchall()  # Fetch all request

        request_list = []

        for requestEdit in requests:
            req_id = requestEdit[0]
            req_attribute = requestEdit[1]
            req_change = requestEdit[2]
            req_reason = requestEdit[4]
            req_studentId = requestEdit[5]

            try:
                request_data = {
                    "id": req_id,
                    "attribute": req_attribute,
                    "change": req_change,
                    "reason": req_reason,
                    "studentId": req_studentId,
                }

                # Append the student's dictionary to the student_list
                request_list.append(request_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('AdminDashboard.html', request_list=request_list, programme_list=filterProgramme(), cohort_list=filterCohort(), level_list=filterLevel())


def filterProgramme():
    selectProgram_sql = "SELECT DISTINCT programme FROM student;"
    cursorProgramme = db_conn.cursor()
    try:
        cursorProgramme.execute(selectProgram_sql)
        programmes = cursorProgramme.fetchall()  # Fetch all request

        programme_list = []

        for programmeExits in programmes:
            programme = programmeExits[0]

            try:
                programme_data = {
                    "programme": programme,
                }

                # Append the student's dictionary to the student_list
                programme_list.append(programme_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursorProgramme.close()

    selectCohort_sql = "SELECT * FROM cohort;"
    cursorCohort = db_conn.cursor()
    try:
        cursorCohort.execute(selectCohort_sql)
        cohorts = cursorCohort.fetchall()  # Fetch all request

        cohort_list = []

        for cohortExits in cohorts:
            cohort = cohortExits[0]

            try:
                cohort_data = {
                    "cohort": cohort,
                }

                # Append the student's dictionary to the student_list
                cohort_list.append(cohort_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursorCohort.close()

    return programme_list


def filterCohort():
    selectCohort_sql = "SELECT * FROM cohort;"
    cursorCohort = db_conn.cursor()
    try:
        cursorCohort.execute(selectCohort_sql)
        cohorts = cursorCohort.fetchall()  # Fetch all request

        cohort_list = []

        for cohortExits in cohorts:
            cohort = cohortExits[0]

            try:
                cohort_data = {
                    "cohort": cohort,
                }

                # Append the student's dictionary to the student_list
                cohort_list.append(cohort_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursorCohort.close()

    return cohort_list


def filterLevel():
    selectLevel_sql = "SELECT DISTINCT level FROM student;"
    cursorLevel = db_conn.cursor()
    try:
        cursorLevel.execute(selectLevel_sql)
        levels = cursorLevel.fetchall()  # Fetch all request

        level_list = []

        for levelExits in levels:
            level = levelExits[0]

            try:
                level_data = {
                    "level": level,
                }

                # Append the student's dictionary to the student_list
                level_list.append(level_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursorLevel.close()

    return level_list


@app.route("/displayCompany", methods=['GET', 'POST'])
def displayCompany():

    select_sql = "SELECT * FROM company WHERE status ='pending'"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql)
        companys = cursor.fetchall()  # Fetch all request

        company_list = []

        for companyExits in companys:
            company_id = companyExits[0]
            company_password = companyExits[1]
            company_name = companyExits[2]
            company_about = companyExits[3]
            company_address = companyExits[4]
            company_email = companyExits[5]
            company_phone = companyExits[6]

            try:
                company_data = {
                    "id": company_id,
                    "password": company_password,
                    "name": company_name,
                    "about": company_about,
                    "address": company_address,
                    "email": company_email,
                    "phone": company_phone,

                }

                # Append the student's dictionary to the student_list
                company_list.append(company_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('displayCompany.html', company_list=company_list)


@app.route("/filterCompany", methods=['GET', 'POST'])
def FilterCompany():

    name = request.form['search-name']
    address = request.form['search-address']  # Check if the field exists

    select_sql = "SELECT * FROM company WHERE status ='pending'"
    cursor = db_conn.cursor()

    if name:
        select_sql += f" AND name LIKE '%{name}%'"
    if address:
        select_sql += f" AND address LIKE '%{address}%'"

    try:
        cursor.execute(select_sql)
        companys = cursor.fetchall()  # Fetch all request

        company_list = []

        for companyExits in companys:
            company_id = companyExits[0]
            company_password = companyExits[1]
            company_name = companyExits[2]
            company_about = companyExits[3]
            company_address = companyExits[4]
            company_email = companyExits[5]
            company_phone = companyExits[6]

            try:
                company_data = {
                    "id": company_id,
                    "password": company_password,
                    "name": company_name,
                    "about": company_about,
                    "address": company_address,
                    "email": company_email,
                    "phone": company_phone,

                }

                # Append the student's dictionary to the student_list
                company_list.append(company_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    return render_template('displayCompany.html', company_list=company_list)


@app.route("/approveCompany", methods=['GET', 'POST'])
def approveCompany():
    selected_selected_companys = request.form.getlist('selected_companys[]')
    selected_company_name = request.form.getlist('selected_name[]')
    action = request.form['action']

    cursorApprove = db_conn.cursor()
    cursorName = db_conn.cursor()
    cursorReject = db_conn.cursor()
    name_list = []

    if action == 'approve':
        try:
            for conpanyId in selected_selected_companys:
                update_sql = "UPDATE company SET status ='activeted' WHERE companyId=%s"
                cursorApprove.execute(update_sql, (conpanyId))
                db_conn.commit()

                selectName_sql = "SELECT name FROM company WHERE companyId=%s;"
                cursorName.execute(selectName_sql, (conpanyId))
                names = cursorName.fetchall()  # Fetch all request

                for nameExits in names:
                    name = nameExits[0]

                try:
                    name_data = {
                        "name": name,
                    }
                    name_list.append(name_data)
                except Exception as e:
                    return str(e)
        finally:
            cursorApprove.close()
            cursorName.close()

        return render_template('companyOutput.html', company_list=name_list)

    if action == 'reject':
        try:
            for conpanyId in selected_selected_companys:
                update_sql = "UPDATE company SET status ='rejected' WHERE companyId=%s"
                cursorReject.execute(update_sql, (conpanyId))
                db_conn.commit()

                selectName_sql = "SELECT name FROM company WHERE companyId=%s and status='rejected';"
                cursorName.execute(selectName_sql, (conpanyId))
                names = cursorName.fetchall()  # Fetch all request

                for nameExits in names:
                    name = nameExits[0]

                try:
                    name_data = {
                        "name": name,
                    }
                    name_list.append(name_data)
                except Exception as e:
                    return str(e)

        finally:
            cursorReject.close()

        return render_template('companyRejectOutput.html', company_list=name_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
=======

@app.route('/studentApplyFilter', methods=['POST', 'GET'])
def studentApplyFilter():
    # Extract filter criteria from the form
    category = request.form.get('category')
    status = request.form.get('status')
    network_details = get_network_details()

    try:
        # Create a cursor
        cursor = db_conn.cursor()

        # Construct the SQL query based on the selected filters
        sql = "SELECT * FROM contact WHERE 1=1 AND student = %s"

        if category != '*':
            sql += f" AND category = '{category}'"
        if status != '*':
            sql += f" AND status = '{status}'"

        cursor.execute(sql, ('2'))

        # Fetch the filtered data
        contact_details = cursor.fetchall()

        return render_template('studentContactUs.html', contact_data=contact_details, network_details=network_details)

    except Exception as e:
        db_conn.rollback()
        return str(e)


@app.route('/logout')
def admin_logout():
    # Clear session data
    session.pop('name', None)
    session.pop('loggedIn', None)

    return redirect(url_for('adminLogin'))
# N10 - Trace contact details


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
>>>>>>> 1e5970868ab72e6bdaeb6feb8088c2323e7d8284
