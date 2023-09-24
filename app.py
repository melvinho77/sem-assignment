from flask import render_template, make_response, jsonify
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

# N10
@app.route('/contactUs')
def contact_us():
    # Call the get_network_details function to retrieve network details
    network_details = get_network_details()
    
    # Pass the network_details to the contactUs.html template
    return render_template('contactUs.html', network_details=network_details)

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

@app.route('/compare', methods=['GET', 'POST'])
def selectCompare():
    select_level="SELECT DISTINCT level FROM availableProgramme"
    cursorLevel = db_conn.cursor()

    cursorLevel.execute(select_level)
    levels=cursorLevel.fetchall()

    level_list=[]
    programmeList=[]

    try:
        for level in levels:
            programmeLevel=level[0]
        
            try:
                level_date={
                "level" :programmeLevel,                  
                }

                level_list.append(level_date)
                    
            except Exception as e:
                return str(e) 
            
            select_programme="SELECT avProgrammeId,programmeName FROM availableProgramme WHERE level=%s"
            cursorProgramme= db_conn.cursor()

            cursorProgramme.execute(select_programme,(programmeLevel,))
            programmes=cursorProgramme.fetchall()

            for programme in programmes:
                progId=programme[0]
                progName=programme[1]

                try:
                    level_date={
                    "level" :programmeLevel,
                    "progId" :progId,
                    "progName":progName                    
                    }

                    programmeList.append(level_date)
                    
                except Exception as e:
                    return str(e) 
                
    except Exception as e:
        return str(e)
    
    network_details = get_network_details()
    return render_template('selectCompare.html',number=1, network_details=network_details,
                           level_list=level_list,
                           programmeList=programmeList)



@app.route("/SelectError", methods=['GET', 'POST'])
def selectProgrammeError():
    network_details = get_network_details()
    return render_template('selectProgrammeError.html', network_details=network_details)

# N5 compare Programme Structure
@app.route('/compareProgramme', methods=['POST'])
def showAllProgramme():

    progId=request.form.getlist('progId[]')    
    electiveCourse_list = []
    courseExits=[]
    courseNotExits=[]
    programmeList=[]
    electiveExits=[]
    electiveNotExits=[]
    course_list=[]
    network_details = get_network_details()
    #loop for check the programme
    for id in progId:
            select_programme="SELECT avProgrammeId,programmeName,level FROM availableProgramme WHERE avProgrammeId=%s"
            cursorProgramme= db_conn.cursor()

            cursorProgramme.execute(select_programme,(id,))
            programmes=cursorProgramme.fetchall()                        

            for programme in programmes:
                progId=programme[0]
                progName=programme[1]
                
                course_list=findAllCourse(course_list,programme[2])
                electiveCourse_list=findAllElective(programme[2])
                try:
                    level_date={
                    "progId" :progId,
                    "progName":progName                    
                    }

                    programmeList.append(level_date)
                    
                except Exception as e:
                    return str(e) 

                #all not exits course in a particular programme
                notCourses_for_program = findNotExistsCourse(id,progName)
                courseNotExits.extend(notCourses_for_program)     

                #all not exits elective in a particular programme
                notElective_for_program = findNotElectiveExists(id,progName)
                electiveNotExits.extend(notElective_for_program) 


            #all exits course in a particular programme
            courses_for_program = findCourse(id)
            courseExits.extend(courses_for_program)

            #all exits elective course in a particular programme
            elective_for_program = findElectiveCourse(id)
            electiveExits.extend(elective_for_program)           
                 
            
        #Sort the course_list alphabetically by courseName
            courseExits = sorted(courseExits, key=lambda x: x['progName'])
              
    return render_template('compareProgramme.html', 
                           course_list=course_list,
                           electiveCourse_list=electiveCourse_list,
                           programmeList=programmeList,
                           courseExits=courseExits,
                           courseNotExits=courseNotExits,
                           electiveExits=electiveExits,
                           electiveNotExits=electiveNotExits, 
                           network_details = network_details                                              
                           )


def findAllElective(level):
        electiveCourse_list=[]
  #find all elective
        all_electiveCourse = "SELECT DISTINCT electiveTaken FROM programmeElectiveCourse p,  availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND LEVEL=%s ORDER BY electiveTaken"
        cursor_AllElectivecourse = db_conn.cursor()
        
        try:
            cursor_AllElectivecourse.execute(all_electiveCourse,(level,))
            allElectiveCourse = cursor_AllElectivecourse.fetchall()

            

            for elective in allElectiveCourse:
                courseName = elective[0]

                try:
                    # Check if the course name already exists in course_list
                    exists = any(elective_data['courseName'] == courseName for elective_data in electiveCourse_list)
                    
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
        electiveCourse_list = sorted(electiveCourse_list, key=lambda x: x['courseName']) 

        return electiveCourse_list

def findAllCourse(course_list,level):

    

    #find main course
    all_course = "SELECT Distinct courseTaken FROM programmeMainCourse p , "  \
                "availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND level=%s ORDER BY courseTaken"
    cursor_Allcourse = db_conn.cursor()

    try:
        cursor_Allcourse.execute(all_course,(level,))
        allCourse = cursor_Allcourse.fetchall()

        for course in allCourse:
            courseName = course[0]

            try:
                # Check if the course name already exists in course_list
                exists = any(course_data['courseName'] == courseName for course_data in course_list)
                
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

def findNotExistsCourse(programmeId,progName):
    
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
                    "progName":progName,
                    "courseName": courseName
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)

    except Exception as e:
        return str(e)

    return course_list

def findCourse(programmeId):
      #find all course
    all_course = "SELECT programmeName,courseTaken FROM programmeMainCourse p , availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND programmeId = %s ORDER BY programmeName"
    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            progName = course[0]
            courseName = course[1]

            try:
                course_data = {
                    "progName": progName, 
                    "courseName":courseName           
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list

def findElectiveCourse(programmeId):
      #find all course
    all_course = "SELECT programmeName,electiveTaken FROM programmeElectiveCourse p , availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND programmeId = %s ORDER BY electiveTaken"
    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            progName = course[0]
            courseName = course[1]

            try:
                course_data = {
                    "progName": progName, 
                    "courseName":courseName           
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list

def findNotElectiveExists(programmeId,progName):
    
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
                    "progName":progName,
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
    studID = 2  # modify
    select_sql = f"SELECT * FROM students WHERE studentID = '{studID}'"

    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql)
        studInfo = cursor.fetchall() 
        stud_list = []
        for studData in studInfo:
            
            stud_data = {
                "studName" : studData[1],
                "studIC" : studData[2],
                "studEmail" : studData[3],
                "studPhone" : studData[4],
                "studBdate" : studData[5],
                "studGender" : studData[6],
                "studAddress" : studData[7],
                "studPassword" : studData[8],
                }           
            stud_list.append(stud_data)  
            print(stud_list)
    except Exception as e:
            return str(e)
    return render_template('applicationProfile.html', network_details=network_details, stud_data = stud_data)



# Ho hong meng
@app.route("/trackContactUs")
def trackContactUs():
    # Change to session data
    student = '2'
    session['loggedInStudent'] = '2'
    network_details = get_network_details()

    # Retrieve all contact data based on this student
    select_sql = "SELECT * FROM contact WHERE student = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (student))
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
    # Handle the form submission with email and password
    email = request.form.get('email')
    password = request.form.get('password')

    if email == 'hhm@gmail.com' and password == '123':
        session['name'] = 'Ho Hong Meng'
        session['loggedIn'] = 'hhm'

    elif email == 'css@gmail.com' and password == '456':
        session['name'] = 'Cheong Soo Siew'
        session['loggedIn'] = 'css'

    network_details = get_network_details()

    try:
        cursor = db_conn.cursor()
        # Retrieve contact details for the current page
        cursor.execute("SELECT * FROM contact")
        contactDetails = cursor.fetchall()

    except Exception as e:
        db_conn.rollback()
        return str(e)

    if request.method == 'POST':

        if email == 'hhm@gmail.com' and password == '123':
            return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

        elif email == 'css@gmail.com' and password == '456':
            return render_template('adminContactUs.html', name=session['name'], contact_details=contactDetails, network_details=network_details)

        else:
            error_msg = 'Invalid email or password. Please try again.'
            return render_template('adminLogin.html', msg=error_msg, network_details=network_details)

    return render_template(
        'adminContactUs.html',
        name=session['name'],
        contact_details=contactDetails,
        network_details=network_details
    )


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
        elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
            session['loggedIn'] = 'css'

    # Flash a success message
    flash('Question submitted successfully', 'success')

    # Redirect back to the contactUs page
    return redirect('/adminContactUs')


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
                session['loggedInName'] = 'Ho Hong Meng'
            elif email == 'css@gmail.com' and name == 'Cheong Soo Siew':
                session['loggedIn'] = 'css'
                session['loggedInName'] = 'Cheong Soo Siew'

        return render_template('adminContactUs.html', contact_details=contact_details, network_details=network_details, name=session['loggedInName'])

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



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
