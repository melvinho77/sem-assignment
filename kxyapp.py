from flask import render_template, make_response
from flask import redirect
import mimetypes
from flask import Flask, render_template, request, redirect, url_for, session, send_file
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
app.secret_key = 'sem'

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
table = 'focsWebsite'

@app.route('/')
def index():
    network_details = get_network_details()
    return render_template('home.html', network_details=network_details)

######################################## STAFF #############################################
@app.route ("/staffDirectory", methods=['GET', 'POST'])
def staffDirectory():

    division = request.args.get('division')
    campusName = request.args.get('campus')

    cursor = db_conn.cursor()
    #get all campuses
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
            cursor.execute(select_sql, (division,campusId))
            division = cursor.fetchone()

        if (request.args.get('staffName')):
            if (division == "ALL"):
                select_sql = "SELECT D.Name AS divisionName, S.*, P.* FROM division D, staff S LEFT JOIN publication P ON S.staffID = P.staffID WHERE D.divisionID = S.divisionID AND campusId = %s AND UPPER(S.name) LIKE UPPER(%s) ORDER BY (CASE WHEN D.divisionID = 'FOCS' THEN 1 ELSE 0 END) DESC, D.divisionID DESC;"
                cursor.execute(select_sql, (campusId,'%' + request.args.get('staffName') + '%'))
            else:
                select_sql = "SELECT D.Name AS divisionName, S.*, P.* FROM division D, staff S LEFT JOIN publication P ON S.staffID = P.staffID WHERE D.divisionID = S.divisionID AND campusId = %s AND S.divisionId = %s AND UPPER(S.name) LIKE UPPER(%s) ORDER BY (CASE WHEN D.divisionID = 'FOCS' THEN 1 ELSE 0 END) DESC, D.divisionID DESC;"
                cursor.execute(select_sql, (campusId,division,'%' + request.args.get('staffName') + '%'))
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

@app.route('/go_back')
def go_back():
    return redirect(request.referrer)

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

@app.route('/goToQualification', methods=['GET', 'POST'])
def goToQualification():
    return render_template('verifyQualification.html')

@app.route('/verifyApplication', methods=['GET', 'POST'])
def verifyApplication():

    cursor = db_conn.cursor()
    apply_student_id = session.get('loggedInStudent')

    qualification=request.form.get('qualification-diploma','')
    year=request.form.get('qualification-diploma-year','')
    subject1=request.form.get('spm-subject-1','')
    subject2=request.form.get('spm-subject-2','')
    subject3=request.form.get('spm-subject-3','')
    subject4=request.form.get('spm-subject-4','')
    subject5=request.form.get('spm-subject-5','')
    subject6=request.form.get('spm-subject-6','')
    subject7=request.form.get('spm-subject-7','')
    subject8=request.form.get('spm-subject-8','')
    subject9=request.form.get('spm-subject-9','')
    subject10=request.form.get('spm-subject-10','')

    grades = [
        request.form.get(f'spm-grades-{i}', '') for i in range(1, 11)
    ]

    select_sql = "select studentIc from students where studentId = %s"
    cursor.execute(select_sql,(apply_student_id))
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
    c_or_better_count = sum(grade in ['A', 'A+', 'A-', 'B', 'B+', 'C', 'C+'] for grade in grades)


    #GET know what student apply the programme with the first choice
    select_sql_fist_choice="""
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

    #check whether the BAHASA MELAYU and  excced grades E
    compulsory_subjects = {
    'BAHASA MELAYU': 'E',
    'SEJARAH': 'E',
    }

    country_require=True
    for country_subject, country_required_grade in compulsory_subjects.items():
        if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
        # Find the index of the subject in the list
            subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(country_subject)

            # Check if the student's grade for that subject meets the required grade
            student_grade = grades[subject_index]

            # Compare the student's grade with the required grade
            if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                country_require = False
                break


    #compare compulsary subject has meet the requirements or not
    meet_first_choice_requirement= True
    #validate whether the application programme have reach the compulsary subject of minimum requirement
    if application_programme:
        sql_select_programme="""
            SELECT SUBJECT, grade
            FROM qualification
            WHERE programme=%s AND LEVEL=%s
        """
        cursor.execute(sql_select_programme, (application_programme,qualification))
        validateSubject = cursor.fetchall() #getting know first choice of subject

        #commpare student grades
        for subject, required_grade in validateSubject:
        #check if the validate subject in the manual subject from the student
            if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
            #find the index of the student in the list
            # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(subject)
                student_grade=grades[subject_index]
                if(grade_order.get(student_grade,0)<grade_order.get(required_grade,0)):
                    meet_first_choice_requirement=False
                    print(f"For {subject}, the student's grade {student_grade} does not meet the required grade {required_grade}.")
                    break
            else:
                return("Student does not have subject")
            
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
        update_sql_choice_1_to_reject="""
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

        second_country_require=True
        for country_subject, country_required_grade in compulsory_subjects.items():
            if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
            # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(country_subject)

                # Check if the student's grade for that subject meets the required grade
                student_grade = grades[subject_index]

                # Compare the student's grade with the required grade
                if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                    second_country_require = False
                    print(f"For {subject}, the student's grade {student_grade} does not meet the required grade {country_required_grade}.")
                    break

        #compare compulsary subject has meet the requirements or not
        meet_second_choice_requirement= True
        #validate whether the application programme have reach the compulsary subject of minimum requirement
        if application_programme:
            sql_select_programme="""
            SELECT SUBJECT, grade
            FROM qualification
            WHERE programme=%s AND LEVEL=%s
            """
        cursor.execute(sql_select_programme, (application_programme_second_choice,qualification))
        validateSubject = cursor.fetchall() #getting know first choice of subject

        #commpare student grades
        for subject, required_grade in validateSubject:
        #check if the validate subject in the manual subject from the student
            if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
            #find the index of the student in the list
            # Find the index of the subject in the list
                subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(subject)
                student_grade=grades[subject_index]
                if(grade_order.get(student_grade,0)<grade_order.get(required_grade,0)):
                    meet_first_choice_requirement=False
                    break
            else:
                return("Student does not have subject")
            
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
            #update choice 2 to rejected
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

            third_country_require=True
            for country_subject, country_required_grade in compulsory_subjects.items():
                if country_subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                # Find the index of the subject in the list
                    subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(country_subject)

                    # Check if the student's grade for that subject meets the required grade
                    student_grade = grades[subject_index]

                    # Compare the student's grade with the required grade
                    if grade_order.get(student_grade, 0) < grade_order.get(country_required_grade, 0):
                        third_country_require = False
                        break
            
                #compare compulsary subject has meet the requirements or not
                meet_third_choice_requirement= True
                #validate whether the application programme have reach the compulsary subject of minimum requirement
                if application_programme_third_choice:
                    sql_select_programme="""
                    SELECT SUBJECT, grade
                    FROM qualification
                    WHERE programme=%s AND LEVEL=%s
                    """
                    cursor.execute(sql_select_programme, (application_programme_third_choice,qualification))
                    validateSubject = cursor.fetchall() #getting know first choice of subject

                    #commpare student grades
                for subject, required_grade in validateSubject:
                #check if the validate subject in the manual subject from the student
                    if subject in [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10]:
                # Find the index of the subject in the list
                        subject_index = [subject1, subject2, subject3, subject4, subject5, subject6, subject7, subject8, subject9, subject10].index(subject)
                        student_grade=grades[subject_index]
                        if(grade_order.get(student_grade,0)<grade_order.get(required_grade,0)):
                            meet_third_choice_requirement=False
                            print(f"For {subject}, the student's grade {student_grade} does not meet the required grade {required_grade}.")
                            break
                        else:
                            return("Student does not have subject")
            if c_or_better_count >= 3 and third_country_require and meet_third_choice_requirement:
                update_sql_choice_3_approved = """
                UPDATE programmeApplications
                SET applicationStatus = 'approved'
                WHERE student = %s AND choice = 3 AND applicationStatus = 'pending'
                """
                cursor.execute(update_sql_choice_3_approved, (apply_student_id,))
                db_conn.commit()
                return redirect(url_for("applicationHomeContent"))
            else:
                update_sql_choice_3_rejected = """
                UPDATE programmeApplications
                SET applicationStatus = 'rejected'
                WHERE student = %s AND choice = 3 AND applicationStatus = 'pending'
                """
                cursor.execute(update_sql_choice_3_rejected, (apply_student_id,))
                db_conn.commit()
                return redirect(url_for("applicationHomeContent"))

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    try:
        if request.method == 'POST':
            img = Image.open(request.files.get('imagefile'))
        
        ic = '020401-01-2124'

        # Define the dictionary with subjects and grades filled by the student
        student_grades = {
            'BAHASA MELAYU': 'A',
            'BAHASA INGGERIS': 'A-',
            'PENDIDIKAN MORAL': 'A-',
            'SEJARAH': 'A',
            'MATHEMATICS': 'A+',
            'ADDITIONAL MATHEMATICS': 'A',
            'PHYSICS': 'A+',
            'CHEMISTRY': 'A',
            'BIOLOGY': 'B',
            'BAHASA CINA': 'A-'
        }

        # read image
        # img = cv2.imread('C:\\Users\\kuxinyau\\Desktop\\RSF TARUC\\Year 3\\Sem 1\\BACS3003 SEM\\Assignment (AWS)\\sem-assignment\\static\\images\\spmslip3.jpg')

        img = crop_image(img)

        text = pytesseract.image_to_string(img, config='--psm 6')
        print(text)

        # Split the result text into lines
        lines = text.strip().split('\n')

        # Iterate over each line
        for line in lines:
             # Split the line into words
            words = line.split()

            # Check if the line contains at least 3 words (subject and grade)
            if words:
                if 'K/P' in words:
                    if ic in words:
                        print(f"The ic matched {words}.")
                    else:
                        print(f"The ic not match {words}.")

        # Check each grade in the dictionary against the list
        for subject, grade in student_grades.items():
            # Find the list that contains the subject
            for grades in lines:
                if subject in grades:
                    # Check if the grade in the list matches the grade in the dictionary
                    if grade not in grades:
                        print(f"The grade for {subject} {grade} does not match.")
                    else:
                        print(f"The grade for {subject} {grade} matched.")
                    break

        return render_template('image.html', var=text)
            #else:
            #    return render_template('image.html', var='No image file uploaded')
        #else:
        #    return render_template('image.html', var='')  # Render an empty form for GET requests
    except Exception as e:
        return render_template('image.html', var=f'Error: {str(e)}')

def check_year(text, year):
    # Use a regular expression to find four-digit numbers in the text
    years = re.findall(r'\b\d{4}\b', text)

    # Check if the desired year is in the list of years
    return str(year) in years

def crop_image(img):    
        # convert to grayscale
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # invert gray image
        gray = 255 - gray

        # threshold
        thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY)[1]

        # apply close and open morphology to fill tiny black and white holes and save as mask
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # get contours (presumably just one around the nonzero pixels) 
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        cntr = contours[0]
        x,y,w,h = cv2.boundingRect(cntr)

        # make background transparent by placing the mask into the alpha channel
        new_img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        new_img[:, :, 3] = mask

        # then crop it to bounding rectangle
        crop = new_img[y:y+h, x:x+w]
        
        cv2.imshow('crop', crop)
        
        return crop

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)