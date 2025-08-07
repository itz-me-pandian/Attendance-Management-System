from datetime import date,datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.db import connection

def home(request):
    return render(request, 'atp/index.html')

def register(request):
    return render(request,"atp/reg.html")

def disp_det(request):
    '''
    if request.method == 'POST':
        det = {}
        det["fname"] = request.POST.get('fname')
        det["lname"] = request.POST.get('lname')
        det["sid"] = request.POST.get('sid')
        det["dob"] = request.POST.get('dob')
 

        return render(request, 'atp/disp_det.html',det)
    else:
        return HttpResponse('Dont worry we will fix the error :)')
    '''
    return render(request, 'atp/disp_det.html')  

def student_login(request):
    return render(request, 'atp/student_login.html')

def teacher_login(request):
    return render(request, 'atp/teacher_login.html')

def admin_login(request):
    return render(request, 'atp/admin_login.html')

def admin_dashboard(request):
    return render(request, 'atp/admin_dashboard.html')

def add_student(request):
    return render(request, 'atp/add_student.html')

def add_teacher(request):
    return render(request, 'atp/add_teacher.html')

def add_course(request):
    return render(request, 'atp/add_course.html')

def add_department(request):
    return render(request, 'atp/add_department.html')

def student_dashboard(request):
    return render(request, 'atp/student_dashboard.html')

def student_check(request):
    print("Sankara Narayanan V")
    if request.method == 'POST':
        full_name = request.POST.get('name')  # full name entered here
        name_parts = full_name.strip().split()
        print(name_parts)
        

        if len(name_parts) < 2:
            return HttpResponse("Please enter both first and last name.", status=400)

        fname = name_parts[0]
        lname = name_parts[1]
        password = request.POST.get('stud_id')  # assuming actual ID/password is entered in this field

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM student
                WHERE fname = %s AND lname = %s AND stud_id = %s
            """, [fname, lname, password])
            student = cursor.fetchone()
            print(fname, lname, password)
            print("C: ",student)
            print(type(student))

        if student:
            request.session['current_user'] = student[0]
            return render(request, 'atp/student_dashboard.html')
        else:
            return HttpResponse("Invalid Student ID or Password", status=401)

    return HttpResponse("Invalid Request Method", status=400)
    print("Sankara Narayanan V")
    if request.method == 'POST':
        full_name = request.POST.get('name')  # full name entered here
        name_parts = full_name.strip().split()
        print(name_parts)
        

        if len(name_parts) < 2:
            return HttpResponse("Please enter both first and last name.", status=400)

        fname = name_parts[0]
        lname = name_parts[1]
        password = request.POST.get('stud_id')  # assuming actual ID/password is entered in this field

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM student
                WHERE fname = %s AND lname = %s AND stud_id = %s
            """, [fname, lname, password])
            student = cursor.fetchone()
            print(fname, lname, password)
            print("C: ",student)
            print(type(student))

        if student:
            request.session['current_user'] = student[0]
            return render(request, 'atp/student_dashboard.html')
        else:
            return HttpResponse("Invalid Student ID or Password", status=401)

    return HttpResponse("Invalid Request Method", status=400)

def view_student_profile(request):

    '''
    id = request.session.get('current_user')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM student
            WHERE stud_id = %s            """, [id])
        student_row = cursor.fetchone()
   
    # Map the tuple to a dictionary based on column order
    student = {
        'stud_id': student_row[0],
        'fname': student_row[1],
        'lname': student_row[2],
        'minit': student_row[3],
        'dob': student_row[4],
        'age': student_row[6],
        'barcode': student_row[5],
        
    }
    '''
    id = request.session.get('current_user')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM student
            WHERE stud_id = %s            """, [id])
        student_row = cursor.fetchone()
   
    # Map the tuple to a dictionary based on column order
    student = {
        'stud_id': student_row[0],
        'fname': student_row[1],
        'lname': student_row[2],
        'minit': student_row[3],
        'dob': student_row[4],
        'age': student_row[6],
        'barcode': student_row[5],
        
    }

    return render(request, 'atp/view_student_profile.html', student)
    #return render(request, 'atp/view_student_profile.html')

def students_todays_lectures(request):

    student_id = request.session.get('current_user')
    print(student_id,"AAAAAAAAAAAAAAAAAAAAAAA")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.course_name, 
                TO_CHAR(l.s_time, 'HH:MI AM') AS start_time, 
                TO_CHAR(l.s_time + (l.duration/24), 'HH:MI AM') AS end_time,
                l.duration || ' hour' AS duration,
                t.fname || ' ' || t.lname AS lecturer,
                TO_CHAR(l.l_date, 'Month DD, YYYY') AS lecture_date
            FROM student s        
            join department d on s.dep_id = d.dep_id
            join course c on d.dep_id = c.dep_id
            JOIN lecture l ON c.course_id = l.course_id
            JOIN teachers t ON l.t_id = t.t_id
            WHERE s.stud_id = %s
              AND TRUNC(l.l_date) = TRUNC(SYSDATE)
           
        """, [student_id])
        
        rows = cursor.fetchall()

    columns = ['course_name', 'start_time', 'end_time', 'duration', 'lecturer', 'date']
    lectures = [dict(zip(columns, row)) for row in rows]

    #return render(request, 'atp/students_todays_lectures.html', {'lectures': lectures})




    return render(request, 'atp/students_todays_lectures.html')

from django.db import connection
from django.shortcuts import render
from django.contrib import messages

def mark_attendance(request):
    student_id = request.session.get('current_user')

    if request.method == 'POST':
        # Your existing logic for handling POST requests
        with connection.cursor() as cursor:
            # Query to get lectures that the student has not marked attendance for
            cursor.execute("""
                SELECT 
                    c.course_name,
                    t.fname || ' ' || t.lname AS lecturer,
                    TO_CHAR(l.s_time, 'HH24:MI') AS start_time,
                    TO_CHAR(l.e_time, 'HH24:MI') AS end_time,
                    l.l_id
                FROM student_course sc
                JOIN lecture l ON sc.course_id = l.course_id AND sc.t_id = l.t_id
                JOIN course c ON sc.course_id = c.course_id
                JOIN teacher t ON sc.t_id = t.t_id
                WHERE sc.stud_id = %s
                AND TRUNC(l.l_date) = TRUNC(SYSDATE)
                AND NOT EXISTS (
                    SELECT 1 FROM attendance a
                    WHERE a.stud_id = %s AND a.l_id = l.l_id
                );
            """, [student_id, student_id])

            # Fetch all results (lectures without marked attendance)
            columns = [col[0].lower() for col in cursor.description]
            rows = cursor.fetchall()
            lectures = [dict(zip(columns, row)) for row in rows]

            if lectures:
                # Pass the results to the template
                return render(request, 'atp/mark_attendance.html', {'lectures': lectures, 'today': date.today()})
            else:
                return HttpResponse("No lectures available to mark attendance", status=401)

    # If the method is not POST, respond accordingly (this could be a GET or another method)
    elif request.method == 'GET':
        # You might want to handle GET requests (e.g., show the form or something else)
        return render(request, 'atp/mark_attendance.html', {'today': date.today()})

    return HttpResponse("Method Not Allowed", status=405)

def give_attendance(request):
    return render(request, 'atp/give_attendance.html')

def view_my_attendance(request):
    student_id = request.session.get('current_user')
    attendance_data = []

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    c.course_name,
                    COUNT(DISTINCT l.l_id) AS total_lectures,
                    COUNT(DISTINCT CASE WHEN a.stud_id IS NOT NULL THEN l.l_id END) AS lectures_taken,
                    COUNT(DISTINCT a.l_id) AS attended,
                    ROUND(
                        (COUNT(DISTINCT a.l_id) * 100.0) / 
                        NULLIF(COUNT(DISTINCT CASE WHEN a.stud_id IS NOT NULL THEN l.l_id END), 0), 
                        2
                    ) AS percentage
                FROM 
                    student s
                JOIN 
                    student_course sc ON s.stud_id = sc.stud_id
                JOIN 
                    course c ON sc.course_id = c.course_id
                JOIN 
                    lecture l ON l.course_id = c.course_id AND l.t_id = sc.t_id
                LEFT JOIN 
                    attendance a ON a.stud_id = s.stud_id AND a.l_id = l.l_id
                WHERE 
                    s.stud_id = %s
                GROUP BY 
                    c.course_name
            """, [student_id])

            rows = cursor.fetchall()
            for row in rows:
                attendance_data.append({
                    'course_name': row[0],
                    'total_lectures': row[1],
                    'lectures_taken': row[2],
                    'attended': row[3],
                    'percentage': float(row[4]) if row[4] is not None else 0.0
                })

    return render(request, 'atp/view_my_attendance.html', {'attendance_data': attendance_data})
'''
    attendance_data = [
        {
            'course_name': 'Data Structures',
            'total_lectures': 20,
            'lectures_taken': 18,
            'attended': 17,
            'percentage': round((17 / 18) * 100, 2)
        },
        {
            'course_name': 'Operating Systems',
            'total_lectures': 22,
            'lectures_taken': 20,
            'attended': 19,
            'percentage': round((19 / 20) * 100, 2)
        },
        {
            'course_name': 'DBMS',
            'total_lectures': 25,
            'lectures_taken': 23,
            'attended': 20,
            'percentage': round((20 / 23) * 100, 2)
        },
        {
            'course_name': 'Computer Networks',
            'total_lectures': 21,
            'lectures_taken': 21,
            'attended': 18,
            'percentage': round((18 / 21) * 100, 2)
        },
        {
            'course_name': 'Machine Learning',
            'total_lectures': 24,
            'lectures_taken': 22,
            'attended': 21,
            'percentage': round((21 / 22) * 100, 2)
        },
        {
            'course_name': 'Compiler Design',
            'total_lectures': 20,
            'lectures_taken': 19,
            'attended': 15,
            'percentage': round((15 / 19) * 100, 2)
        },
        {
            'course_name': 'Artificial Intelligence',
            'total_lectures': 22,
            'lectures_taken': 20,
            'attended': 18,
            'percentage': round((18 / 20) * 100, 2)
        },
        {
            'course_name': 'Web Technologies',
            'total_lectures': 20,
            'lectures_taken': 18,
            'attended': 16,
            'percentage': round((16 / 18) * 100, 2)
        }
    ]
    return render(request, 'atp/view_my_attendance.html',{'attendance_data':attendance_data})'''

#Function for Verifying Teacher Credentials for login
def teacher_check(request):
    if request.method == 'POST':
        teacher_full_name = request.POST.get('teacher_name')
        teacher_password = request.POST.get('teacher_id')
        name_parts = teacher_full_name.strip().split()

        if len(name_parts) < 2:
            return HttpResponse("Please enter both first and last name.", status=400)

        fname = name_parts[0]
        lname = name_parts[1]

        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM teacher WHERE fname = :fname AND lname = :lname AND t_id = :tid""",{'fname': fname, 'lname': lname, 'tid': teacher_password})
            teacher = cursor.fetchone()

        if teacher:
            #print(teacher)
            request.session['teacher_info'] = teacher
            return render(request, 'atp/teacher_dashboard.html')
        else:
            return HttpResponse("Invalid Student ID or Password", status=401)

    return HttpResponse("Invalid Request Method", status=400)

#Function for redirecting to Teacher dashboard
def teacher_dashboard(request):
    return render(request, 'atp/teacher_dashboard.html')

#Function for displaying details of the teacher
def teacher_profile(request):
    teacher_info = request.session.get('teacher_info')
    phone=[]

    with connection.cursor() as cursor:
        cursor.execute("""select * from teacher_phno where t_id = %s""",[teacher_info[0]])
        teacher_phone = cursor.fetchall()

        if teacher_phone:
            for i in teacher_phone:
                phone.append(i[1])

    if not teacher_info:
        return redirect('teacher_login')
    
    print(teacher_info,phone)

    return render(request, 'atp/teacher_profile.html', {'teacher_info': teacher_info,'teacher_phone': phone})

# Function for finding courses taken by a particular Teacher
def teacher_courses(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]
    c_id = []

    with connection.cursor() as cursor:
        cursor.execute("""select course_id from teacher_course where t_id = %s""",[t_id])
        course_id = cursor.fetchall()

        if course_id :
            for i in course_id:
                temp={}
                with connection.cursor() as cursor:
                    i=i[0]
                    print(i[0])
                    cursor.execute("""select course_name from course where course_id = %s""",[i])
                    course_name = cursor.fetchone()

                    cursor.execute("""select count(*) from lecture where t_id = %s and course_id = %s""",[t_id,i])
                    total_lecture = cursor.fetchone()[0]
                    
                    current_time = datetime.now()

                    cursor.execute("""select count(*) from lecture where t_id = %s and course_id = %s and e_time <= %s""", [t_id,i,'2025-01-10 12:53:21.350762']) #current_time])
                    lecture_taken = cursor.fetchone()[0]
                    print(lecture_taken)

                    lecture_left = total_lecture - lecture_taken

                    temp['name']= course_name[0]
                    temp['id']  = i
                    temp['total_lectures'] = total_lecture
                    temp['lectures_taken'] = lecture_taken
                    temp['lectures_left']  = lecture_left

                c_id.append(temp)

            #print(c_id)
           
            return render(request, 'atp/teacher_courses.html',{'courses':c_id})
        return HttpResponse("No course Available", status=400)

#Function for displaying Today's lecture of a particular Teacher 
def teacher_lectures(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]
    lectures = []
    today_str = date.today().strftime('%Y-%m-%d')

    with connection.cursor() as cursor:
        cursor.execute("""select * from lecture where t_id = %s and l_date = to_date(%s,'YYYY-MM-DD')""",[t_id,'2025-01-02']) #today_str]) # '2023-09-13'])
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                temp = {}

                lec_id, start_time, end_time, lec_date, t_id, course_id, lat, lon = row

                cursor.execute("""select course_name from course where course_id = %s""",[course_id])
                course_name = cursor.fetchone()
                
                # Calculate duration
                duration = end_time - start_time  # returns a timedelta object
        
                # Optional: get total minutes or HH:MM
                duration_minutes = int(duration.total_seconds() / 60)
                duration_str = f"{duration.seconds // 3600:02}:{(duration.seconds % 3600) // 60:02}"

                print(f"Course ID : {course_id} Lecture ID: {lec_id}")

                print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
                start_time = start_time.strftime('%Y-%m-%d @ %H:%M')

                print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M')}")
                end_time = end_time.strftime('%Y-%m-%d @ %H:%M')
            
                duration = str(duration_str)+' (i.e. '+str(duration_minutes)+' minutes )'
                
                temp['course_name'] = course_name[0]
                temp['course_id']   = course_id
                temp['start_time']  = start_time
                temp['end_time']    = end_time
                temp['duration']    = duration

                lectures.append(temp)
            
            return render(request, 'atp/teacher_lectures.html',{'lectures' : lectures})
        
        return HttpResponse("No Lectures Available Today !!!", status=400)

def find_attendance(t_id, students):
    if not students:
        return None

    data = []
    current_time = datetime.now()

    for item in students:
        for key, value in item.items():  # key = course_id, value = list of student ids
            if value:
                for stud_id in value:
                    temp = {}
                    with connection.cursor() as cursor:

                        # Total lectures
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM lecture 
                            WHERE t_id = %s AND course_id = %s AND e_time <= %s
                        """, [t_id, key, current_time])
                        total_lecture = cursor.fetchone()[0]

                        print(total_lecture)

                        cursor.execute("""select count(*) from lecture l
                            join attendance a on l.l_id = a.l_id 
                            where a.stud_id = %s and l.t_id = %s and l.course_id = %s and l.e_time <= %s
                        """, [stud_id, t_id, key, current_time])
                        lectures_attended = cursor.fetchone()[0]

                        # Student name
                        cursor.execute("""
                            SELECT fname, lname 
                            FROM student 
                            WHERE stud_id = %s
                        """, [stud_id])
                        row = cursor.fetchone()
                        if row:
                            fname, lname = row
                            name = f"{fname} {lname}"
                        else:
                            name = "Unknown"

                        # On-duty count
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM on_duty o 
                            JOIN lecture l ON o.l_id = l.l_id
                            WHERE o.stud_id = %s AND l.t_id = %s AND l.course_id = %s AND l.e_time <= %s
                        """, [stud_id, t_id, key, current_time])
                        on_duty_count = cursor.fetchone()[0]

                        # Compile result
                        temp['name'] = name
                        temp['total_lectures'] = total_lecture
                        temp['course_id'] = key
                        temp['id'] = stud_id
                        temp['lectures_attended'] = lectures_attended
                        temp['on_duty'] = on_duty_count

                        print(temp)

                        data.append(temp)

    return data


# Function for displaying Attendance details of Students involved with a particular Teacher
def student_attendance_details(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]
    c_id = []
    students = []

    with connection.cursor() as cursor:
        cursor.execute("""select course_id from teacher_course where t_id = %s""",[t_id])
        course_id = cursor.fetchall()
        
        if course_id:
            for i in course_id:
                temp={}
                c_id.append(i[0])
                cursor.execute("""select stud_id from student_course where t_id = %s and course_id = %s""",[t_id,i[0]])
                stu_id = cursor.fetchall()
                
                s_id=[]

                if(stu_id):
                    for j in stu_id :
                        s_id.append(j[0])

                    #print(s_id)
                    temp[i[0]] = s_id

                else:
                    temp[i[0]] = None

                students.append(temp)

        print(students)

        data = find_attendance(t_id,students)
        print(data)

    return render(request, 'atp/student_attendance_details.html',{'students':data})

def test_git(request):
    return HttpResponse("Testing git hub")