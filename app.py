from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from botocore.exceptions import ClientError
from pymysql import connections
import boto3
from config import *
import datetime
import socket
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io
import re

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

# @app.route('/')
# def index():
#     network_details = get_network_details()
#     return render_template('home.html', number=1, network_details=network_details)


# @app.route('/')
# def loadStudProfile():
#     network_details = get_network_details()
#     studID = 2
#     select_sql = f"SELECT * FROM students WHERE studentID = '{studID}'"

#     cursor = db_conn.cursor()
#     try:
#         cursor.execute(select_sql)
#         studInfo = cursor.fetchall()
#         stud_list = []
#         for studData in studInfo:

#             stud_data = {
#                 "studName": studData[1],
#                 "studIC": studData[2],
#                 "studEmail": studData[3],
#                 "studPhone": studData[4],
#                 "studBdate": studData[5],
#                 "studGender": studData[6],
#                 "studAddress": studData[7],
#                 "studPassword": studData[8],
#             }
#             stud_list.append(stud_data)
#             print(stud_list)
#     except Exception as e:
#         return str(e)

#     return render_template('applicationProfile.html', network_details=network_details, stud_data=stud_data)

# @app.route('/updateStudProfile')
# def updateStudProfile():
#     network_details = get_network_details()

#     return redirect(url_for('/', msg="Password updated successfully"))


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


# GWEE YONG SEAN
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
    application_date = datetime.now()
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

    pytesseract.pytesseract.tesseract_cmd = '"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"'

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
                if ic in words:
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

# N10 - Trace contact details
@app.route("/contactUs")
def contact_us():
    # Call the get_network_details function to retrieve network details
    # Retrieve student Id
    id = session.get('loggedInStudent')
    network_details = get_network_details()
    select_sql = "SELECT * FROM students WHERE studentID  = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (id,))
        student = cursor.fetchone()
        db_conn.commit()

        # Access student ID and name from the 'student' tuple
        student_name = student[1]

    except Exception as e:
        db_conn.rollback()
        return str(e)
    
    # # Pass the network_details and msg to the contactUs.html template
    # return render_template("contactUs.html", network_details=network_details, id=session.get('loggedInStudent'), student_name=student_name)
    print(id)
    print(student_name)

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
    student_id = request.form.get('student_id')
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

    except Exception as e:
        db_conn.rollback()
        return str(e)


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
