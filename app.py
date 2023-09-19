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
    return render_template('home.html')

@app.route('/')
def index():
    
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
    return render_template('home.html', number=1, network_details=network_details,
                           level_list=level_list,
                           programmeList=programmeList)

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

# N5 compare Programme Structure
@app.route('/compareProgramme', methods=['POST'])
def showAllProgramme():

    progId=request.form.getlist('progId[]')    
    programmeList=[]
    course_list = []
    electiveCourse_list = []
    courseExits=[]
    courseNotExits=[]
    
    for id in progId:  
        courses_for_program = findCourse(id)
        courseExits.extend(courses_for_program)

        notCourses_for_program = findNotExitsCourse(id)
        courseNotExits.extend(notCourses_for_program)
    
        return courseNotExits
    
        #find selected programme
        select_programme="SELECT avProgrammeId,programmeName FROM availableProgramme WHERE avProgrammeId=%s"
        cursorProgramme= db_conn.cursor()

        cursorProgramme.execute(select_programme,(id,))
        programmes=cursorProgramme.fetchall()

        for programme in programmes:
            progId=programme[0]
            progName=programme[1]

            try:
                level_date={
                "progId" :progId,
                "progName":progName                    
                }

                programmeList.append(level_date)
                
            except Exception as e:
                return str(e)   
    #find all course

        all_course = "SELECT Distinct courseTaken FROM programmeMainCourse p , "  \
                     "availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND LEVEL='diploma' ORDER BY courseTaken"
        cursor_Allcourse = db_conn.cursor()

        try:
            cursor_Allcourse.execute(all_course)
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

    #find all elective
        all_electiveCourse = "SELECT DISTINCT electiveTaken FROM programmeElectiveCourse WHERE programmeId=%s ORDER BY electiveTaken"
        cursor_AllElectivecourse = db_conn.cursor()
        
        try:
            cursor_AllElectivecourse.execute(all_electiveCourse,(id,))
            allElectiveCourse = cursor_AllElectivecourse.fetchall()

            

            for elective in allElectiveCourse:
                courseName = elective[0]

                try:
                    # Check if the course name already exists in course_list
                    exists = any(elective_data['courseName'] == courseName for elective_data in course_list)
                    
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
        
    #Sort the course_list alphabetically by courseName
    courseExits = sorted(courseExits, key=lambda x: x['progName'])
        

    return render_template('compareProgramme.html', 
                           course_list=course_list,
                           electiveCourse_list=electiveCourse_list,
                           programmeList=programmeList,
                           courseExits=courseExits,
                           courseNotExits=courseNotExits                                              
                           )


def findSelectedProgramme(progId):
    programmeList=[]
    for id in progId:
        select_programme="SELECT avProgrammeId,programmeName FROM availableProgramme WHERE avProgrammeId=%s"
        cursorProgramme= db_conn.cursor()

        cursorProgramme.execute(select_programme,(id,))
        programmes=cursorProgramme.fetchall()

        for programme in programmes:
            progId=programme[0]
            progName=programme[1]

            try:
                level_date={
                "progId" :progId,
                "progName":progName                    
                }

                programmeList.append(level_date)
                
            except Exception as e:
                return str(e) 
def findSameCourse():
    #find all course
    all_course = "SELECT DISTINCT courseTaken FROM programmeMainCourse WHERE programmeId = 1 AND courseTaken IN ( SELECT courseTaken FROM programmeMainCourse WHERE programmeId = 2) ORDER BY courseTaken;"
    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course)
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "courseName": courseName              
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list

def findNotExitsCourse(programmeId):
      #find all course
    all_course = "SELECT distinct courseTaken FROM programmeMainCourse p , availableProgramme a WHERE  p.programmeId=a.avProgrammeId AND programmeId != 1 ORDER BY courseTaken"
    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "courseName":courseName           
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

def findCourseNoInclude(programmeId):
      #find all course
    all_course = "SELECT DISTINCT courseName FROM course WHERE courseName NOT IN " \
                "(SELECT courseTaken FROM programmeMainCourse WHERE programmeId = %s) " \
                "ORDER BY courseName"


    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "courseName": courseName              
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list

def findElectiveCourse(programmeId):
      #find all course
    all_course = "SELECT DISTINCT electiveTaken FROM programmeElectiveCourse WHERE programmeId = %s ORDER BY electiveTaken"
    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "courseName": courseName              
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list

def findElectiveCourseNoInclude(programmeId):
      #find all course
    all_course = "SELECT DISTINCT  electiveTaken FROM programmeElectiveCourse WHERE electiveTaken NOT IN  " \
                "(SELECT electiveTaken FROM programmeElectiveCourse WHERE programmeId = %s) " \
                "ORDER BY electiveTaken"


    cursor_Allcourse = db_conn.cursor()
    
    try:
        cursor_Allcourse.execute(all_course,(programmeId,))
        allCourse = cursor_Allcourse.fetchall()

        course_list = []

        for course in allCourse:
            courseName = course[0]

            try:
                course_data = {
                    "courseName": courseName              
                }

                course_list.append(course_data)

            except Exception as e:
                return str(e)
    
    except Exception as e:
        return str(e)
    
    return course_list


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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)