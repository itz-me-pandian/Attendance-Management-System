# Chapter 3: Attendance Management Core Logic

Welcome back! In [Chapter 2: User Authentication & Authorization](02_user_authentication___authorization_.md), we learned how our system acts as a gatekeeper, making sure only registered users can log in and access features appropriate for their role (student, teacher, or admin). We built the "lock" for our valuable data.

Now that we know *who* can access the system, let's dive into *what* they do once inside, specifically, the core function of our system: **Attendance Management**. This is the heart of our project, where students mark their presence and everyone can see who attended what.

## What Problem Are We Solving? Tracking Who's There!

Imagine a classroom where the teacher has to manually call out each student's name and mark it on a paper sheet. This is slow, prone to errors, and difficult to keep track of over many classes.

Our Attendance Management System needs a smart way to:
*   Allow students to **easily mark their attendance** for a specific class.
*   **Verify** if a student is actually *at* the lecture's location when they try to mark attendance (no marking from home!).
*   Let students **view their own attendance records**.
*   Let teachers **view attendance records** for their students in their courses.
*   **Calculate attendance percentages** to show how well a student is doing in a course.
*   Make sure a student can *only* mark attendance for courses they are actually **enrolled** in.

This chapter will guide you through how our system handles all these crucial tasks, making attendance tracking simple and reliable.

## Key Concepts: The Building Blocks of Attendance

Let's break down the core ideas that make attendance management work:

### 1. Marking Attendance (The Student's Job)

This is where a student records their presence for a specific lecture. They need to select the correct lecture and prove they are there.

### 2. Location-Based Validation (Proof of Presence)

To prevent cheating (like marking attendance from bed!), our system checks the student's current location against the lecture's registered location. If they are close enough, attendance is allowed.

### 3. Viewing Attendance Records (Transparency for All)

Students need to see their own attendance history, and teachers need to see attendance for their courses and students.

### 4. Calculating Attendance Percentage (Overall Picture)

For each course, the system automatically figures out how many lectures happened and how many the student attended, then calculates a percentage. This gives a quick overview of attendance performance.

### 5. Enrolled Courses Only (Fair Play)

Students should only be able to mark attendance for classes they are registered for. This prevents unauthorized attendance marking.

## Use Case: A Student Marks Attendance

Let's walk through the main use case: **Arjun (a student) wants to mark attendance for his "Introduction to Python" lecture today.**

**Input:** Arjun logs in (as we saw in Chapter 2), goes to the "Mark Attendance" page, selects his Python lecture, and allows the system to get his current location.
**Output:** A success message "Marked attendance successfully" or an error if he's not at the right place.

### Step 1: Student Sees Available Lectures (`mark_attendance.html`)

First, Arjun needs to see which of his enrolled lectures are scheduled for today and still need attendance. Our system displays these in a simple table.

```html
<!-- Project/atp/templates/atp/mark_attendance.html (simplified) -->
<body>
    <h2>Mark Attendance</h2>
    <div class="date">Date: {{ today }}</div>

    <table>
        <thead>
            <tr>
                <th>Course Name</th>
                <th>Lecturer</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for lecture in lectures %}
            <tr>
                <td>{{ lecture.course_name }}</td>
                <td>{{ lecture.lecturer }}</td>
                <td>{{ lecture.start_time }}</td>
                <td>{{ lecture.end_time }}</td>
                <td>
                    <form action="{% url 'give_attendance' %}" method="post">
                        {% csrf_token %}
                        <input type="hidden" name="lecture_id" value="{{ lecture.l_id }}">
                        <button type="submit" class="btn">Give Attendance</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
```
**Explanation:**
*   The `{% for lecture in lectures %}` part loops through all the lectures that Arjun is enrolled in and which are happening today.
*   For each lecture, it shows details like `course_name`, `lecturer`, `start_time`, `end_time`.
*   Crucially, there's a "Give Attendance" button. When Arjun clicks this, it sends the `lecture.l_id` (the unique ID for that lecture) to a new page `give_attendance` so the system knows which lecture he wants to mark attendance for.

### Step 2: Student Provides Location (`give_attendance.html`)

After clicking "Give Attendance", Arjun is taken to a new page where he's asked for his location. In a real web application, the browser would usually ask for permission to share location automatically. Here, for simplicity, we simulate it with text fields.

```html
<!-- Project/atp/templates/atp/give_attendance.html (simplified) -->
<body>
    <div class="form-container">
        <h2>Give Attendance</h2>
        <form method="post" action="{% url 'add_attendance' %}">
            {% csrf_token %}
            <input type="hidden" name="lecture_id" value="{{ lecture.l_id }}">
            <label for="latitude">Latitude</label>
            <input type="text" name="latitude" id="latitude" required>
            <label for="longitude">Longitude</label>
            <input type="text" name="longitude" id="longitude" required>
            <button type="submit" class="button-link">Submit Attendance</button>
        </form>
    </div>
</body>
```
**Explanation:**
*   `input type="hidden" name="lecture_id" value="{{ lecture.l_id }}"`: This hidden field still carries the lecture ID so the system knows which lecture the attendance is for.
*   `input type="text" name="latitude" ...` and `longitude`: These are where Arjun (or the browser automatically) would input his current location coordinates.
*   `Submit Attendance`: Clicking this sends the `lecture_id`, `latitude`, and `longitude` to the `add_attendance` function.

### Step 3: System Validates and Records Attendance (`views.py`)

When the location data is submitted, our Django application's `add_attendance` function takes over. This is where the core logic lives.

```python
# Project/atp/views.py (simplified - add_attendance function)
from django.db import connection
from django.http import HttpResponse

def add_attendance(request):
    student_id = request.session.get('current_user') # Get logged-in student's ID
    if request.method == 'POST':
        lecture_id = request.POST.get('lecture_id')
        user_lat = float(request.POST.get('latitude'))
        user_long = float(request.POST.get('longitude'))

        if student_id and lecture_id:
            with connection.cursor() as cursor:
                # 1. Get lecture's actual location from the database
                cursor.execute("""
                    SELECT lattitude, longitude FROM lecture
                    WHERE l_id = %s """, [lecture_id])
                lecture = cursor.fetchone()

                if lecture:
                    lecture_lat, lecture_long = float(lecture[0]), float(lecture[1])

                    # 2. Perform location-based validation
                    # Allow a small margin of error (e.g., 0.0005 degrees, approx 50 meters)
                    if abs(lecture_lat - user_lat) <= 0.0005 and abs(lecture_long - user_long) <= 0.0005:
                        try:
                            # 3. Record attendance in the database
                            cursor.execute("""
                                INSERT INTO attendance (stud_id, l_id, date_recorded, time_recorded, lattitude, longitude)
                                VALUES (%s, %s, CURRENT_DATE, SYSTIMESTAMP, %s, %s)
                                """, [student_id, lecture_id, user_lat, user_long])
                            # No explicit commit here, but Django's autocommit or transaction management would handle it.
                            return HttpResponse("Marked attendance successfully")
                        except Exception as ex:
                            # This catches errors like the trigger preventing duplicate attendance
                            return HttpResponse(f"Error marking attendance: {str(ex)}")
                    else:
                        return HttpResponse("You are not at the lecture location.")
                else:
                    return HttpResponse("Lecture not found.", status=404)
        return HttpResponse("Invalid request data.", status=400)
    return HttpResponse("Invalid Request Method", status=400)
```
**Explanation:**
1.  **Get Student ID:** It first retrieves the `student_id` from the user's session, which was set during [login in Chapter 2](02_user_authentication___authorization_.md).
2.  **Get User Location:** It gets the `lecture_id`, `latitude`, and `longitude` from the submitted form.
3.  **Fetch Lecture Location:** It queries the `lecture` table to find the *actual* latitude and longitude registered for that `lecture_id`.
4.  **Location Validation:** It then compares the student's reported location (`user_lat`, `user_long`) with the `lecture_lat` and `lecture_long`. We allow a small difference (`0.0005` degrees) to account for GPS inaccuracies.
5.  **Record Attendance:** If the locations match, it inserts a new record into the `attendance` table, linking the `student_id` to the `l_id` (lecture ID), along with the date, time, and location recorded.
6.  **Error Handling:** If the locations don't match or the lecture isn't found, an appropriate error message is returned.

## Internal Implementation: Under the Hood

Let's trace what happens when Arjun marks his attendance.

```mermaid
sequenceDiagram
    participant Arjun
    participant Web Browser
    participant Attendance System
    participant Database

    Arjun->>Web Browser: 1. Clicks "Mark Attendance"
    Web Browser->>Attendance System: 2. Requests list of today's lectures for Arjun
    Note over Attendance System: 3. Retrieves Arjun's ID from session.
                                 Queries Database for enrolled lectures today.
    Attendance System->>Database: 4. "SELECT lectures for student X for today not yet attended"
    Database-->>Attendance System: 5. Returns list of available lectures
    Attendance System-->>Web Browser: 6. Displays lectures in a table
    Arjun->>Web Browser: 7. Selects a lecture, provides location (or allows browser to get it), clicks "Submit Attendance"
    Web Browser->>Attendance System: 8. Sends (Lecture ID, Student Location)
    Note over Attendance System: 9. Retrieves Lecture ID.
                                 Gets lecture's registered location from Database.
    Attendance System->>Database: 10. "SELECT location FROM lecture WHERE l_id = Y"
    Database-->>Attendance System: 11. Returns lecture's (Latitude, Longitude)
    Note over Attendance System: 12. Compares student location with lecture location.
    alt Location Matches
        Attendance System->>Database: 13. "INSERT INTO attendance (stud_id, l_id, ...) VALUES (Arjun's ID, Y, ...)"
        Note over Database: 14. Runs 'stud_attendance_trigger' to ensure enrollment.
        Database-->>Attendance System: 15. Confirmation (Attendance recorded)
        Attendance System-->>Web Browser: 16. "Attendance marked successfully"
        Web Browser->>Arjun: 17. Sees success message
    else Location Does NOT Match
        Attendance System-->>Web Browser: 18. "You are not at the lecture location."
        Web Browser->>Arjun: 19. Sees error message
    end
```

### Database Interaction: The `attendance` Table

As seen in [Chapter 1: Database Schema (Entities & Relationships)](01_database_schema__entities___relationships__.md), the `attendance` table is where the records are actually stored.

```sql
-- inputs/table.sql (simplified)
create table attendance (
	stud_id varchar(10) constraint ad_fk1 references student(stud_id),
	l_id varchar(10) constraint ad_fk2 references lecture(l_id),
	date_recorded date,
	time_recorded timestamp,
	lattitude number(10,8),
	longitude number(11,8),
	constraint att_pk primary key(stud_id,l_id)
);

create table lecture (
	l_id varchar(10) constraint lpk primary key,
	s_time timestamp,
	e_time timestamp,
	l_date date,
	t_id varchar(10) constraint l_fk1 references teacher(t_id),
	course_id varchar(10) constraint l_fk2 references course(course_id),
	lattitude number(10,8),
	longitude number(11,8)
);
```
**Explanation:**
*   The `attendance` table has `stud_id` and `l_id` as foreign keys, linking each attendance record to a specific student and a specific lecture.
*   It also stores `date_recorded`, `time_recorded`, and the `lattitude` and `longitude` where attendance was marked.
*   The `lecture` table stores the `lattitude` and `longitude` where the lecture is *supposed* to happen.

### Ensuring Enrollment: The `stud_attendance_trigger`

When an `INSERT` command tries to add a new attendance record, a special database feature called a **trigger** automatically runs before the data is actually saved. This trigger (`stud_attendance_trigger`) ensures that the student is actually enrolled in the course for which the lecture is being held.

```sql
-- inputs/trigger_for_inserting_attendance_row.sql (simplified)
create or replace trigger stud_attendance_trigger
before insert on attendance
for each row
declare
    v_count NUMBER;
    c_count NUMBER;
    c_id course.course_id%type;
begin
    -- Check if the lecture exists
    select count(*) into c_count from lecture where l_id=:NEW.l_id;
    if c_count = 0 then
        raise_application_error(-20001,'LECTURE DOES NOT EXIST');
    end if;

    -- Get the course ID for the lecture
    select course_id into c_id from lecture where l_id=:NEW.l_id;

    -- Check if the student is enrolled in that course
    select count(*) into v_count from student_course where stud_id=:NEW.stud_id and course_id=c_id;

    if v_count = 0 then
        RAISE_APPLICATION_ERROR(-20001, 'STUDENT NOT ENROLLED IN THIS COURSE');
    end if;
end;
/
```
**Explanation:**
1.  `before insert on attendance`: This means the trigger runs *before* any new data is inserted into the `attendance` table.
2.  `select count(*) into c_count from lecture where l_id=:NEW.l_id;`: It checks if the `l_id` (lecture ID) provided in the new attendance record actually exists in the `lecture` table. If not, it stops the insertion with an error.
3.  `select course_id into c_id from lecture where l_id=:NEW.l_id;`: It gets the `course_id` associated with the lecture.
4.  `select count(*) into v_count from student_course where stud_id=:NEW.stud_id and course_id=c_id;`: It checks the `student_course` table (from [Chapter 1](01_database_schema__entities___relationships__.md)) to see if the student (`:NEW.stud_id`) is enrolled in that `course_id`.
5.  `if v_count = 0 then RAISE_APPLICATION_ERROR(...)`: If the student is not enrolled, it stops the attendance record from being created with an error.

This trigger adds an important layer of data integrity, ensuring that only valid attendance records are ever saved.

### Viewing My Attendance (Student View)

Students can view their attendance records, including a summary of how many lectures they've attended versus the total.

```python
# Project/atp/views.py (simplified - view_my_attendance function)
def view_my_attendance(request):
    student_id = request.session.get('current_user') # Get logged-in student's ID
    today = date.today().strftime('%Y-%m-%d')

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
            WHERE sc.stud_id = %s AND l.l_date <= TO_DATE(%s, 'YYYY-MM-DD')
            GROUP BY c.course_name
        """, [student_id, today])

        rows = cursor.fetchall()

    attendance_data = []
    for row in rows:
        course_name = row[0]
        total_lectures = row[1]
        attended = row[2]
        percentage = round((attended / total_lectures) * 100, 2) if total_lectures > 0 else 0

        attendance_data.append({
            'course_name': course_name,
            'total_lectures': total_lectures, # This is actually lectures held so far
            'lectures_taken': total_lectures, # Redundant name but included from original
            'attended': attended,
            'percentage': percentage
        })

    return render(request, 'atp/view_my_attendance.html', {'attendance_data': attendance_data})
```
**Explanation:**
*   This SQL query is more complex, using `JOIN` statements to link `student_course`, `course`, `lecture`, and `attendance` tables.
*   It counts `total_lectures` (lectures held *up to today* for the courses the student is enrolled in).
*   It counts `attended` lectures by checking the `attendance` table for entries from the `current_user`.
*   `GROUP BY c.course_name` ensures that the counts are grouped per course.
*   Finally, it calculates the `percentage` and passes this `attendance_data` to a template for display.

### Viewing Student Attendance (Teacher View)

Teachers also have a way to see the attendance summary for students in their courses.

```python
# Project/atp/views.py (simplified - find_attendance function, used by student_attendance_details)
def find_attendance(t_id, students_in_courses):
    data = []
    current_time = datetime.now() # Use current time to count lectures held so far

    for item in students_in_courses: # item is like {'CS101': ['2370001', '2370002']}
        for course_id, student_ids_in_course in item.items():
            if student_ids_in_course:
                for stud_id in student_ids_in_course:
                    temp = {}
                    with connection.cursor() as cursor:
                        # Count total lectures held for this course by this teacher up to now
                        cursor.execute("""
                            SELECT COUNT(*) FROM lecture
                            WHERE t_id = %s AND course_id = %s AND e_time <= %s
                        """, [t_id, course_id, current_time])
                        total_lectures_held = cursor.fetchone()[0]

                        # Count lectures attended by this specific student for this course and teacher
                        cursor.execute("""
                            SELECT count(*) FROM lecture l
                            JOIN attendance a ON l.l_id = a.l_id
                            WHERE a.stud_id = %s AND l.t_id = %s AND l.course_id = %s AND l.e_time <= %s
                        """, [stud_id, t_id, course_id, current_time])
                        lectures_attended = cursor.fetchone()[0]

                        # Get student's name
                        cursor.execute("""SELECT fname, lname FROM student WHERE stud_id = %s""", [stud_id])
                        row = cursor.fetchone()
                        student_name = f"{row[0]} {row[1]}" if row else "Unknown"

                        temp['name'] = student_name
                        temp['id'] = stud_id
                        temp['course_id'] = course_id
                        temp['total_lectures'] = total_lectures_held
                        temp['lectures_attended'] = lectures_attended
                        # No 'on_duty' calculation shown here for simplicity, but it would be similar
                        data.append(temp)
    return data
```
**Explanation:**
*   This `find_attendance` function is designed to be called by a teacher's view (`student_attendance_details`).
*   It takes the `t_id` (teacher ID) and a list of students in their courses.
*   For each student and course, it performs two main queries:
    *   One to count the `total_lectures_held` for that course by that teacher up to the current time.
    *   Another to count `lectures_attended` by that specific student for that specific course and teacher.
*   It then collects this information, including the student's name, and returns it. This data is then rendered in the `student_attendance_details.html` template.

## Conclusion

In this chapter, we've explored the core logic behind our Attendance Management System. We learned how students mark attendance with location validation, and how both students and teachers can view attendance records and percentages. We also saw how database triggers and enrollment checks ensure that attendance is fair and accurate, only allowing students to mark attendance for courses they are properly registered for.

Understanding this core logic is key, as it's the main function of our application. Next, we'll dive deeper into how teachers specifically manage the creation and modification of lectures in [Chapter 4: Lecture Management (Teacher-Specific)](04_lecture_management__teacher_specific__.md).

---

<sub><sup>**References**: [[1]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/give_attendance.html), [[2]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/mark_attendance.html), [[3]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/view_my_attendance.html), [[4]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/views.py), [[5]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/inputs/att.sql), [[6]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/inputs/trigger_for_inserting_attendance_row.sql)</sup></sub>