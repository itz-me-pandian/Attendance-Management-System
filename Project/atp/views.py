from datetime import date,datetime,timedelta
import json
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.db import connection

def home(request):
    return render(request, 'atp/index.html')

def register(request):
    return render(request,"atp/reg.html")

def disp_det(request):
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

def del_student(request):
    return render(request, 'atp/del_student.html')

def add_teacher(request):
    return render(request, 'atp/add_teacher.html')

def add_course(request):
    return render(request, 'atp/add_course.html')

def add_department(request):
    return render(request, 'atp/add_department.html')



#------------------------------- Admin Functionalities -----------------------------

#Function for Verifying Admin Credentials for login
def admin_check(request):
    if request.method == 'POST':
        admin_name = request.POST.get('admin_name')
        admin_password = request.POST.get('password')
        
        with connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM admin_tab WHERE admin_id = :admin_name and admin_name = :admin_password""",{'admin_name': admin_name, 'admin_password': admin_password})
            admin = cursor.fetchone()
            print(admin)

        if admin:
            return render(request, 'atp/admin_dashboard.html')
        else:
            return HttpResponse("Invalid Admin ID or Password", status=401)

    return HttpResponse("Invalid Request Method", status=400)

#Function for adding course_teacher_Student
def add_teacher_course_student(request):
    if request.method == 'POST':
        t_id = request.POST.get('t_id')
        stud_id = request.POST.get('stud_id')
        course_id = request.POST.get('course_id')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""insert into student_course values( %s,%s,%s)""",[stud_id,course_id,t_id])
            cursor.execute("""commit""")
            return HttpResponse(f"Teacher with id {t_id} is allotted as teacher for student with id {stud_id} for course with id {course_id} Successfully !")

    except Exception as ex:
        return HttpResponse(ex)
    
#Function for deleting course_teacher_Student
def del_teacher_course_student(request):
    if request.method != 'POST':
        return HttpResponse("Invalid request method", status=400)

    t_id = request.POST.get('t_id')
    stud_id = request.POST.get('stud_id')
    course_id = request.POST.get('course_id')

    if not all([t_id, stud_id, course_id]):
        return HttpResponse("Missing required fields (t_id, stud_id, or course_id)", status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("""DELETE FROM student_course WHERE stud_id = %s AND course_id = %s AND t_id = %s""",[stud_id, course_id, t_id])
            
            if cursor.rowcount == 0:
                return HttpResponse(f"No matching record found for student_id={stud_id}, course_id={course_id}, teacher_id={t_id}",
                    status=404)
            
            return HttpResponse(f"Teacher (ID: {t_id}) unassigned from student (ID: {stud_id}) in course (ID: {course_id}) successfully!",status=200)

    except Exception as ex:
        return HttpResponse(f"Error: {str(ex)}", status=500)
    



#------------------------------- Student Functionalities -----------------------------------

def student_dashboard(request):
    return render(request, 'atp/student_dashboard.html')

def student_check(request):
    
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
        'barcode': student_row[6],
        'dept_id': student_row[5],
        
    }

    return render(request, 'atp/view_student_profile.html', student)

def students_todays_lectures(request):
    student_id = request.session.get('current_user')
    today = date.today()  

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.course_name,
                l.s_time,
                l.e_time,
                (l.e_time - l.s_time) AS duration,
                CONCAT(t.fname, CONCAT(' ', t.lname)) AS lecturer,
                TO_CHAR(l.l_date, 'DD-Mon-YYYY') AS lecture_date
            FROM student_course sc
            JOIN lecture l ON sc.course_id = l.course_id AND sc.t_id = l.t_id
            JOIN course c ON c.course_id = l.course_id
            JOIN teacher t ON t.t_id = l.t_id
            WHERE sc.stud_id = %s
              AND l.l_date = %s
        """, [student_id, today])

        rows = cursor.fetchall()
    
    lectures = [
        {
            'course_name': row[0],
            'start_time': row[1],
            'end_time': row[2],
            'duration': row[3],
            'lecturer': row[4],
            'date': row[5]
        }
        for row in rows
    ]

    return render(request, 'atp/students_todays_lectures.html', {'lectures': lectures})

def mark_attendance(request):
    student_id = request.session.get('current_user') 
    today = date.today()  # Current date

    print(student_id,today)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT       
                c.course_name,
                CONCAT(t.fname, CONCAT(' ', t.lname)) AS lecturer,
                l.s_time,
                l.e_time,
                l.l_id
            FROM student_course sc
            JOIN lecture l ON sc.course_id = l.course_id AND sc.t_id = l.t_id
            JOIN course c ON c.course_id = l.course_id
            JOIN teacher t ON t.t_id = l.t_id
            WHERE sc.stud_id = %s
              AND l.l_date = trunc(sysdate)
              AND NOT EXISTS (
                  SELECT 1
                  FROM attendance a
                  WHERE a.stud_id = sc.stud_id
                    AND a.l_id = l.l_id
              )
        """, [student_id])  

        rows = cursor.fetchall()

    # Prepare the list of lectures
    lectures = [
        {
            'course_name': row[0],
            'lecturer': row[1],
            'start_time': row[2],
            'end_time': row[3],
            'l_id':row[4]
            
        }
        for row in rows
    ]

    return render(request, 'atp/mark_attendance.html', {'lectures': lectures,'today':today})

def give_attendance(request):
    lecture_id = request.POST.get('lecture_id')
    print(lecture_id)
    context = {'lecture': {'l_id': lecture_id}}
    return render(request, 'atp/give_attendance.html', context)

def add_attendance(request):
    
    student_id = request.session.get('current_user')
    print("Entered",student_id)

    if request.method == 'POST':
        lecture_id = request.POST.get('lecture_id')
        user_lat = float(request.POST.get('latitude'))
        user_long = float(request.POST.get('longitude'))

        if student_id and lecture_id:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT lattitude, longitude FROM lecture
                    WHERE l_id = %s """, [lecture_id])
                lecture = cursor.fetchone()
                
       
                if lecture:
                    lecture_lat, lecture_long = float(lecture[0]), float(lecture[1])

                    # Allow small margin of error (about 50 meters)
                    if abs(lecture_lat - user_lat) <= 0.0005 and abs(lecture_long - user_long) <= 0.0005:
                        
                        try:
                            cursor.execute("""
                                INSERT INTO attendance (stud_id, l_id, date_recorded, time_recorded, lattitude, longitude)
                                VALUES (%s, %s, CURRENT_DATE, SYSTIMESTAMP, %s, %s)
                                """, [student_id, lecture_id, user_lat, user_long])
                            
                            return HttpResponse("Marked attendance successfully")
                        
                        except Exception as ex:
                            return HttpResponse(ex)
                        
                    else:
                        return HttpResponse("You are not at the lecture location.")
                       
        return HttpResponse("sr")

def view_my_attendance(request):
    student_id = request.session.get('current_user')  # Logged-in student ID
    today = date.today().strftime('%Y-%m-%d')  # Format today's date

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                c.course_name,
                COUNT(DISTINCT l.l_id) AS total_lectures,
                COUNT(DISTINCT a.l_id) AS attended
            FROM student_course sc
            JOIN course c ON sc.course_id = c.course_id
            JOIN lecture l ON l.course_id = sc.course_id AND l.t_id = sc.t_id
            LEFT JOIN attendance a 
                ON a.l_id = l.l_id AND a.stud_id = sc.stud_id
            WHERE sc.stud_id = %s
              AND l.l_date <= TO_DATE(%s, 'YYYY-MM-DD')
            GROUP BY c.course_name
        """, [student_id, today])

        rows = cursor.fetchall()

    # Prepare final attendance data
    attendance_data = []
    for row in rows:
        course_name = row[0]
        total_lectures = row[1]
        attended = row[2]
        percentage = round((attended / total_lectures) * 100, 2) if total_lectures > 0 else 0

        attendance_data.append({
            'course_name': course_name,
            'total_lectures': total_lectures,
            'lectures_taken': total_lectures,
            'attended': attended,
            'percentage': percentage
        })

    return render(request, 'atp/view_my_attendance.html', {'attendance_data': attendance_data})




#--------------------- Teacher Functionalites ----------------------

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
                    cursor.execute("""select course_name from course where course_id = %s""",[i])
                    course_name = cursor.fetchone()

                    cursor.execute("""select count(*) from lecture where t_id = %s and course_id = %s""",[t_id,i])
                    total_lecture = cursor.fetchone()[0]
                    
                    current_time = datetime.now()

                    cursor.execute("""select count(*) from lecture where t_id = %s and course_id = %s and e_time <= %s""", [t_id,i,'2025-01-10 12:53:21.350762']) #current_time])
                    lecture_taken = cursor.fetchone()[0]
                    #print(lecture_taken)

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

def add_lecture(request):
    return render(request, 'atp/add_lecture.html')

# Function for checking conflicts for adding new Lecture
def check_lecture_conflict(t_id, l_date, s_time, e_time):

    try:
        
        def parse_time(time_str):
            if time_str.startswith("T"):
                time_str = time_str[1:]
            if "T" in time_str:  
                return datetime.strptime(time_str, "%Y-%m-%dT%H:%M").time()
            else: 
                return datetime.strptime(time_str, "%H:%M").time()
        
        start_time = parse_time(s_time)
        end_time = parse_time(e_time)
        
        
        start_datetime = f"{l_date} {start_time.strftime('%H:%M')}"
        end_datetime   = f"{l_date} {end_time.strftime('%H:%M')}"

        with connection.cursor() as cursor:
            
            cursor.execute("""select l_id, to_char(s_time, 'HH24:MI') as start_time, to_char(e_time, 'HH24:MI') as end_time
                          from lecture where t_id = %s and l_date = %s and not (e_time <= %s OR s_time >= %s)""",
                          [t_id, l_date, start_datetime, end_datetime])
            
            conflicting_lectures = cursor.fetchall()
            
            if conflicting_lectures:
                conflict_msg = "Lecture conflicts with existing:\n"

                for lecture in conflicting_lectures:
                    conflict_msg += f"- Lecture {lecture[0]} ({lecture[1]} to {lecture[2]})\n"

                return HttpResponse(conflict_msg, status=400)
            
            return None

    except ValueError as e:
        return HttpResponse(f"Invalid time format: {str(e)}", status=400)
    
    except Exception as e:
        return HttpResponse(f"Validation error: {str(e)}", status=500)

# Function inserting new Lecture in Lecture table
def insert_lecture(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]
    #print(t_id)

    if request.method == 'POST':
        l_id = request.POST.get('l_id')
        s_time = request.POST.get('s_time')
        e_time = request.POST.get('e_time')
        l_date = request.POST.get('l_date')
        course_id = request.POST.get('course_id')
        lattitude = request.POST.get('lattitude')
        longitude = request.POST.get('longitude')

        conflict = check_lecture_conflict(t_id, l_date, s_time, e_time)

        if conflict:
            return conflict
        
        try:
            l_date_obj = datetime.strptime(l_date, "%Y-%m-%d").date()
            s_time_obj = datetime.strptime(s_time, "%Y-%m-%dT%H:%M")
            e_time_obj = datetime.strptime(e_time, "%Y-%m-%dT%H:%M")
            
            if (s_time_obj.date() != l_date_obj) or (e_time_obj.date() != l_date_obj):
                return JsonResponse({'error': 'Date mismatch: Lecture date must match start/end time dates'}, status=400)
                
        except ValueError as e:
            return JsonResponse({'error': f'Invalid date/time format: {str(e)}'}, status=400)

        with connection.cursor() as cursor:

            cursor.execute("""select sysdate from dual""")
            current_date = cursor.fetchone()[0].date()

            cursor.execute("""select to_char(systimestamp, 'YYYY-MM-DD HH24:MI') from dual""")
            current_date_time = cursor.fetchone()[0]

            cursor.execute("""select max(l_id) from lecture""")
            max_lid = cursor.fetchone()[0]

            l_id = int(max_lid[1:])+1
            l_id = 'L0'+str(l_id)

    
        l_date = datetime.strptime(l_date, "%Y-%m-%d").date()
        current_date_time = datetime.strptime(current_date_time, "%Y-%m-%d %H:%M")
        s_time = datetime.strptime(s_time, "%Y-%m-%dT%H:%M")
        e_time = datetime.strptime(e_time, "%Y-%m-%dT%H:%M")

        if l_date<current_date:
            return HttpResponse("Error !!! Your are trying to create lecture in Past", status=400)
        
        if current_date_time>s_time:
            return HttpResponse("Error ! Your are trying to create lecture in Past !! You can create lectures with start time as this second or more", status=400)
        
        time_diff = e_time-s_time

        if time_diff <= timedelta(0) or time_diff > timedelta(hours=5):
            return HttpResponse("Error in start time  and end time !!!", status=400)
        
        s_time = s_time.strftime("%Y-%m-%d %H:%M:%S")
        e_time = e_time.strftime("%Y-%m-%d %H:%M:%S")
        l_date = l_date.strftime("%Y-%m-%d")

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO lecture (L_ID, S_TIME, E_TIME, L_DATE, T_ID, COURSE_ID, LATTITUDE, LONGITUDE) 
                           VALUES (%s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'),TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'),TO_DATE(%s, 'YYYY-MM-DD'), %s, %s, %s, %s)"""
                           , (l_id, s_time, e_time, l_date, t_id, course_id,lattitude,longitude))

            cursor.execute("""commit""")
            return HttpResponse(f"Success ! Lecture created with Lecture id {l_id}", status=400)
        
def delete_lecture(request):
    return render(request, 'atp/delete_lecture.html')

# Function to check whether a lecture can be deleted or cannot
def check_lecture(l_id):
    try:
        current_time = datetime.now()
        
        with connection.cursor() as cursor:

            cursor.execute("""select to_char
                           (l_date + NUMTODSINTERVAL(EXTRACT(HOUR FROM s_time), 'HOUR') 
                            + NUMTODSINTERVAL(EXTRACT(MINUTE FROM s_time), 'MINUTE'),
                            'YYYY-MM-DD HH24:MI:SS') as start_datetime FROM lecture WHERE l_id = %s""", [l_id])
            
            lecture_data = cursor.fetchone()
            
            if not lecture_data:
                return JsonResponse({'can_change': False,'message': 'Lecture not found'}, status=404)
            
            try:
                lecture_start = datetime.strptime(lecture_data[0], '%Y-%m-%d %H:%M:%S')

            except ValueError as e:
                return JsonResponse({'can_change': False,'message': f'Invalid datetime format: {str(e)}'}, status=500)
            
            can_delete = current_time < lecture_start

            return JsonResponse({'can_change': can_delete,'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),'lecture_start': lecture_start.strftime('%Y-%m-%d %H:%M:%S'),
                                 'message': ('Lecture can be deleted (has not started)' if can_delete else 'Lecture cannot be deleted (already started or completed)')})
    
    except Exception as e:
        return JsonResponse({'can_change': False,'message': f'Error checking lecture status: {str(e)}'}, status=500)

# Functio to delete already existing Lectures
def delete_existing_lecture(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]

    if request.method == 'POST':
        try:
            
            l_date = request.POST.get('l_date')
            l_date_obj = datetime.strptime(l_date, "%Y-%m-%d").date()
            formatted_date = l_date_obj.strftime("%Y-%m-%d")  
            
            s_time = request.POST.get('s_time')
            if s_time.startswith("T"):
                s_time = s_time[1:]
            
            
            timestamp_str = f"{formatted_date} {s_time}:00"  
            
            print(f"Executing query with t_id: {t_id}, date: {formatted_date}, timestamp: {timestamp_str}")

            with connection.cursor() as cursor:
                
                cursor.execute("""SELECT l_id FROM lecture 
                    WHERE t_id = %s 
                    AND l_date = TO_DATE(%s, 'YYYY-MM-DD') 
                    AND s_time = TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')""", [t_id, formatted_date, timestamp_str])
                
                result = cursor.fetchone()
                if result:
                    l_id = result[0]
                    
                    with connection.cursor() as cursor:
                        status_check = check_lecture(l_id)
                        data = json.loads(status_check.content)
        
                        if not data['can_change']:
                            return status_check 

                        cursor.execute("""delete from lecture where l_id = %s""",[l_id])
                        cursor.execute("""commit""")

                        return HttpResponse("Lecture Deleted Succesfully !")
                
                else:
                    return HttpResponse("Lecture not found", status=404)
                    
        except ValueError as e:
            return HttpResponse(f"Invalid date/time format: {str(e)}", status=400)
        except Exception as e:
            return HttpResponse(f"Database error: {str(e)}", status=500)

def update_lecture(request):
    return render(request, 'atp/update_lecture.html')

# Function to check conflicts for updating existing Lectures
def check_lecture_conflict_update(t_id, l_date, s_time, e_time,l_id):
    try:
        
        def parse_time(time_str):
            if time_str.startswith("T"):
                time_str = time_str[1:]
            if "T" in time_str:  
                return datetime.strptime(time_str, "%Y-%m-%dT%H:%M").time()
            else: 
                return datetime.strptime(time_str, "%H:%M").time()
        
        start_time = parse_time(s_time)
        end_time = parse_time(e_time)
        
        
        start_datetime = f"{l_date} {start_time.strftime('%H:%M')}"
        end_datetime   = f"{l_date} {end_time.strftime('%H:%M')}"

        with connection.cursor() as cursor:
            
            cursor.execute("""select l_id, to_char(s_time, 'HH24:MI') as start_time, to_char(e_time, 'HH24:MI') as end_time
                          from lecture where t_id = %s and l_date = %s and not (e_time <= %s OR s_time >= %s)""",
                          [t_id, l_date, start_datetime, end_datetime])
            
            conflicting_lectures = cursor.fetchall()

            con = True
            
            if conflicting_lectures:
                conflict_msg = "Lecture conflicts with existing:\n"

                for lecture in conflicting_lectures:
                    if l_id == lecture[0]:
                        con = False

                    else:
                        conflict_msg += f"- Lecture {lecture[0]} ({lecture[1]} to {lecture[2]})\n"
                        con = True

                if con :
                    return HttpResponse(conflict_msg, status=400)
            
            return None

    except ValueError as e:
        return HttpResponse(f"Invalid time format: {str(e)}", status=400)
    
    except Exception as e:
        return HttpResponse(f"Validation error: {str(e)}", status=500)

# Function for Updating already existing lectures
def update_existing_lecture(request):
    teacher_info = request.session.get('teacher_info')
    teacher_id = teacher_info[0]

    if request.method == 'POST':
        l_id = request.POST.get('l_id')
        s_time = request.POST.get('s_time')
        e_time = request.POST.get('e_time')
        l_date = request.POST.get('l_date')
        lattitude = request.POST.get('lattitude')
        longitude = request.POST.get('longitude')

        status_check = check_lecture(l_id)
        data = json.loads(status_check.content)
        
        if not data['can_change']:
            return status_check 
        
        conflict = check_lecture_conflict_update(teacher_id,l_date,s_time,e_time,l_id)

        if conflict:
            return conflict
        
        try:
            l_date_obj = datetime.strptime(l_date, "%Y-%m-%d").date()
            s_time_obj = datetime.strptime(s_time, "%Y-%m-%dT%H:%M")
            e_time_obj = datetime.strptime(e_time, "%Y-%m-%dT%H:%M")
            
            if (s_time_obj.date() != l_date_obj) or (e_time_obj.date() != l_date_obj):
                return JsonResponse({'error': 'Date mismatch: Lecture date must match start/end time dates'}, status=400)
                
        except ValueError as e:
            return JsonResponse({'error': f'Invalid date/time format: {str(e)}'}, status=400)
        
        #print(s_time,e_time,l_date)
        s_time = datetime.strptime(s_time, '%Y-%m-%dT%H:%M')
        s_time = s_time.strftime('%Y-%m-%d %H:%M:%S')
            
        e_time = datetime.strptime(e_time, '%Y-%m-%dT%H:%M')
        e_time = e_time.strftime('%Y-%m-%d %H:%M:%S')
            
        l_date = datetime.strptime(l_date, '%Y-%m-%d')
        l_date = l_date.strftime('%Y-%m-%d')
        
        with connection.cursor() as cursor:
            cursor.execute("""update lecture set s_time =  to_timestamp(%s, 'YYYY-MM-DD HH24:MI:SS'),
                           e_time = to_timestamp(%s, 'YYYY-MM-DD HH24:MI:SS'),
                           l_date = to_date(%s, 'YYYY-MM-DD'),
                           lattitude = %s , longitude = %s where t_id = %s""",[s_time,e_time,l_date,lattitude,longitude,teacher_id])
            
            cursor.execute("""commit""")

            return HttpResponse("Updated Successfully !")


#Function for displaying Today's lecture of a particular Teacher 
def teacher_lectures(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]
    lectures = []
    past = []
    future = []
    today_str = date.today().strftime('%Y-%m-%d')

    with connection.cursor() as cursor:
        cursor.execute("""select * from lecture where t_id = %s and l_date = to_date(%s,'YYYY-MM-DD')""",[t_id,'2025-01-10']) #today_str]) # '2023-09-13'])
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                temp = {}

                lec_id, start_time, end_time, lec_date, t_id, course_id, lat, lon = row

                cursor.execute("""select course_name from course where course_id = %s""",[course_id])
                course_name = cursor.fetchone()
                
                # Calculate duration
                duration = end_time - start_time  # returns a timedelta object
        
                # get total minutes or HH:MM
                duration_minutes = int(duration.total_seconds() / 60)
                duration_str = f"{duration.seconds // 3600:02}:{(duration.seconds % 3600) // 60:02}"

                #print(f"Course ID : {course_id} Lecture ID: {lec_id}")

                #print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
                start_time = start_time.strftime('%Y-%m-%d @ %H:%M')

                #print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M')}")
                end_time = end_time.strftime('%Y-%m-%d @ %H:%M')
            
                duration = str(duration_str)+' (i.e. '+str(duration_minutes)+' minutes )'
                
                temp['course_name'] = course_name[0]
                temp['course_id']   = course_id
                temp['start_time']  = start_time
                temp['end_time']    = end_time
                temp['duration']    = duration

                lectures.append(temp)

        cursor.execute("""select * from lecture where t_id = %s and l_date < to_date(%s,'YYYY-MM-DD')""",[t_id,'2025-01-10']) #today_str]) # '2023-09-13'])
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                temp = {}

                lec_id, start_time, end_time, lec_date, t_id, course_id, lat, lon = row

                cursor.execute("""select course_name from course where course_id = %s""",[course_id])
                course_name = cursor.fetchone()
                
                # Calculate duration
                duration = end_time - start_time  # returns a timedelta object
        
                # get total minutes or HH:MM
                duration_minutes = int(duration.total_seconds() / 60)
                duration_str = f"{duration.seconds // 3600:02}:{(duration.seconds % 3600) // 60:02}"

                #print(f"Course ID : {course_id} Lecture ID: {lec_id}")

                #print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M')}")
                start_time = start_time.strftime('%Y-%m-%d @ %H:%M')

                #print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M')}")
                end_time = end_time.strftime('%Y-%m-%d @ %H:%M')
            
                duration = str(duration_str)+' (i.e. '+str(duration_minutes)+' minutes )'
                
                temp['course_name'] = course_name[0]
                temp['course_id']   = course_id
                temp['start_time']  = start_time
                temp['end_time']    = end_time
                temp['duration']    = duration

                past.append(temp)

        cursor.execute("""select * from lecture where t_id = %s and l_date > to_date(%s,'YYYY-MM-DD')""",[t_id,'2025-01-10']) #today_str]) # '2023-09-13'])
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                temp = {}

                lec_id, start_time, end_time, lec_date, t_id, course_id, lat, lon = row

                cursor.execute("""select course_name from course where course_id = %s""",[course_id])
                course_name = cursor.fetchone()
                
                # Calculate duration
                duration = end_time - start_time  # returns a timedelta object
        
                # get total minutes or HH:MM
                duration_minutes = int(duration.total_seconds() / 60)
                duration_str = f"{duration.seconds // 3600:02}:{(duration.seconds % 3600) // 60:02}"

                start_time = start_time.strftime('%Y-%m-%d @ %H:%M')
                end_time = end_time.strftime('%Y-%m-%d @ %H:%M')
            
                duration = str(duration_str)+' (i.e. '+str(duration_minutes)+' minutes )'
                
                temp['course_name'] = course_name[0]
                temp['course_id']   = course_id
                temp['start_time']  = start_time
                temp['end_time']    = end_time
                temp['duration']    = duration

                future.append(temp)
            
        return render(request, 'atp/teacher_lectures.html',{'past':past,'lectures' : lectures,'future':future})
    

# Function to find attendance of the Students involved in Teacher teaching course
def find_attendance(t_id, students):
    if not students:
        return None

    data = []
    current_time = datetime.now()

    for item in students:
        for key, value in item.items(): 
            if value:
                for stud_id in value:
                    temp = {}
                    with connection.cursor() as cursor:

                       
                        cursor.execute("""SELECT COUNT(*) FROM lecture WHERE t_id = %s AND course_id = %s AND e_time <= %s""",
                                        [t_id, key, '2025-01-10 12:53:21.350762']) #current_time])
                        total_lecture = cursor.fetchone()[0]

                        cursor.execute("""select count(*) from lecture l
                            join attendance a on l.l_id = a.l_id 
                            where a.stud_id = %s and l.t_id = %s and l.course_id = %s and l.e_time <= %s""", 
                            [stud_id, t_id, key, '2025-01-10 12:53:21.350762']) #current_time])
                        lectures_attended = cursor.fetchone()[0]

                        cursor.execute("""SELECT fname, lname FROM student WHERE stud_id = %s""", [stud_id])
                        row = cursor.fetchone()
                        if row:
                            fname, lname = row
                            name = f"{fname} {lname}"
                        else:
                            name = "Unknown"

                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM on_duty o 
                            JOIN lecture l ON o.l_id = l.l_id
                            WHERE o.stud_id = %s AND l.t_id = %s AND l.course_id = %s AND l.e_time <= %s
                        """, [stud_id, t_id, key, '2025-01-10 12:53:21.350762']) #current_time])
                        on_duty_count = cursor.fetchone()[0]

                        temp['name'] = name
                        temp['total_lectures'] = total_lecture
                        temp['course_id'] = key
                        temp['id'] = stud_id
                        temp['lectures_attended'] = lectures_attended
                        temp['on_duty'] = on_duty_count

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