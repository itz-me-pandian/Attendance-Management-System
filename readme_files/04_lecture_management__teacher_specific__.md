# Chapter 4: Lecture Management (Teacher-Specific)

Welcome back! In [Chapter 3: Attendance Management Core Logic](03_attendance_management_core_logic_.md), we explored the core of our system: how students mark their attendance and how both students and teachers can view those records. We saw the mechanisms that ensure only valid attendance is recorded, including location checks and enrollment verification.

Now, let's switch gears and look at the other side of the coin: **Lecture Management**. While students are busy marking attendance for existing lectures, who creates these lectures in the first place? Who decides when and where they happen? This is where teachers come in.

## What Problem Are We Solving? Organizing the Classroom!

Imagine you're a teacher. You need to schedule your classes for the semester. Without a system, this would involve a lot of manual planning, checking for double-bookings, and constantly informing students of changes.

Our Attendance Management System needs to provide teachers with tools to:
*   **Add new lectures**: Schedule future classes for their assigned courses.
*   **Update existing lectures**: Change the time, date, or location of a planned class if needed.
*   **Delete lectures**: Cancel a class if it's no longer happening.
*   **Prevent conflicts**: Crucially, the system must ensure that a teacher cannot accidentally schedule two classes at the same time, or update a lecture to conflict with another.
*   **Manage only their own lectures**: A teacher should only be able to add, update, or delete lectures for the courses they are assigned to teach.

Think of Lecture Management as the teacher's personal **scheduling assistant**. It helps them organize their teaching responsibilities efficiently and without errors.

## Key Concepts: Building Blocks for Lecture Management

Let's break down the main ideas that allow teachers to manage their lectures:

### 1. Adding New Lectures

Teachers need a simple way to create new lecture entries in the system. This involves providing details like the course, date, start time, end time, and location.

### 2. Updating Lecture Details

Sometimes schedules change. Teachers should be able to modify the details of upcoming lectures.

### 3. Deleting Lectures

If a lecture is cancelled, teachers need to remove it from the schedule. However, it's important not to delete lectures that have already happened or started.

### 4. Scheduling Conflict Checks

This is vital! Before any new lecture is added or an existing one is updated, the system must check if it clashes with any other lecture the *same teacher* has already scheduled.

### 5. Teacher-Specific Management

Only the assigned teacher can manage lectures for their courses. This links back to the [User Authentication & Authorization](02_user_authentication___authorization_.md) concepts we discussed earlier.

## Use Case: A Teacher Adds a New Lecture

Let's walk through a common use case: **Dr. Smith (a teacher with ID `T003`) wants to add a new "Database Systems" lecture for `C001` on 2025-03-10 from 10:00 AM to 11:00 AM at a specific location.**

**Input**: Dr. Smith logs in, navigates to "Add Lecture", and fills in the form with the course ID, date, start time, end time, and location coordinates.
**Output**: A success message if the lecture is added, or an error if there's a scheduling conflict or invalid data.

### Step 1: Teacher Fills the "Add Lecture" Form (`add_lecture.html`)

First, Dr. Smith needs a user-friendly form to input the lecture details.

```html
<!-- Project/atp/templates/atp/add_lecture.html (simplified) -->
<body>
    <h2>Add Lecture</h2>
    <form action="{% url 'insert_lecture' %}" method="post">
        {% csrf_token %}
        <label for="course_id">Course ID (COURSE_ID)</label>
        <input type="text" id="course_id" name="course_id">

        <label for="l_date">Lecture Date (L_DATE)</label>
        <input type="date" id="l_date" name="l_date">

        <label for="s_time">Start Time (S_TIME)</label>
        <input type="datetime-local" id="s_time" name="s_time">

        <label for="e_time">End Time (E_TIME)</label>
        <input type="datetime-local" id="e_time" name="e_time"> 

        <label for="lattitude">Latitude</label>
        <input type="number" step="0.000001" id="lattitude" value="12.971599" name="lattitude">

        <label for="longitude">Longitude</label>
        <input type="number" step="0.000001" id="longitude" value ="77.594566" name="longitude">

        <button type="submit">Add Lecture</button>
    </form>
    <a href="{% url 'teacher_courses' %}" class="back-link">← Back to My Courses</a>
</body>
```
**Explanation**:
*   The `form action="{% url 'insert_lecture' %}" method="post"` tells the browser to send the data to our `insert_lecture` function when the button is clicked.
*   Input fields collect all necessary details: `course_id`, `l_date` (lecture date), `s_time` (start time), `e_time` (end time), `lattitude`, and `longitude`. Notice `datetime-local` for combined date and time input.

### Step 2: System Validates and Adds Lecture (`views.py`)

When Dr. Smith submits the form, the `insert_lecture` function in `views.py` processes the request. This is where the core logic for adding a lecture, including conflict checks, resides.

```python
# Project/atp/views.py (simplified - insert_lecture function)
from datetime import date, datetime, timedelta
from django.db import connection
from django.http import HttpResponse

# Helper function to check for scheduling conflicts
def check_lecture_conflict(t_id, l_date, s_time_str, e_time_str):
    # This helper function converts string times to datetime objects for comparison
    # It queries the database to see if the teacher (t_id) has any existing lecture on l_date that overlaps with the proposed s_time_str and e_time_str.
    # If conflicts are found, it returns an HttpResponse with an error, otherwise None.
    # ... (Actual implementation details would be here) ...
    pass # We'll see the full implementation shortly!

def insert_lecture(request):
    teacher_info = request.session.get('teacher_info') # Get logged-in teacher's ID
    t_id = teacher_info[0]

    if request.method == 'POST':
        # 1. Get data from the form
        course_id = request.POST.get('course_id')
        l_date_str = request.POST.get('l_date')
        s_time_str = request.POST.get('s_time')
        e_time_str = request.POST.get('e_time')
        lattitude = request.POST.get('lattitude')
        longitude = request.POST.get('longitude')

        # 2. Check for scheduling conflicts
        conflict_response = check_lecture_conflict(t_id, l_date_str, s_time_str, e_time_str)
        if conflict_response:
            return conflict_response # If there's a conflict, return the error message

        try:
            # 3. Convert string inputs to proper date/time objects for validation
            l_date_obj = datetime.strptime(l_date_str, "%Y-%m-%d").date()
            s_datetime_obj = datetime.strptime(s_time_str, "%Y-%m-%dT%H:%M")
            e_datetime_obj = datetime.strptime(e_time_str, "%Y-%m-%dT%H:%M")

            # Basic validations: Lecture date cannot be in the past, start/end times must be on same day
            if l_date_obj < date.today():
                return HttpResponse("Error! You are trying to create a lecture in the Past", status=400)
            if s_datetime_obj < datetime.now():
                return HttpResponse("Error! Lecture start time cannot be in the past.", status=400)
            if (s_datetime_obj.date() != l_date_obj) or \
               (e_datetime_obj.date() != l_date_obj) or \
               (e_datetime_obj <= s_datetime_obj) or \
               (e_datetime_obj - s_datetime_obj > timedelta(hours=5)):
                return HttpResponse("Error in lecture times or dates. Ensure end time is after start time (max 5 hours) and dates match.", status=400)

        except ValueError as e:
            return HttpResponse(f"Invalid date/time format: {str(e)}", status=400)

        # 4. Generate a unique lecture ID (l_id)
        # Simplified for tutorial: In reality, use a sequence or auto-increment.
        # Original code used: max_lid = cursor.fetchone()[0]; l_id = 'L0'+str(int(max_lid[1:])+1)
        # For simplicity, let's assume `get_next_lecture_id` handles this.
        l_id = get_next_lecture_id() # Placeholder for ID generation

        # 5. Insert the new lecture into the database
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO lecture (L_ID, S_TIME, E_TIME, L_DATE, T_ID, COURSE_ID, LATTITUDE, LONGITUDE)
                VALUES (%s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'),
                        TO_DATE(%s, 'YYYY-MM-DD'), %s, %s, %s, %s)
            """, [l_id, s_datetime_obj.strftime("%Y-%m-%d %H:%M:%S"),
                   e_datetime_obj.strftime("%Y-%m-%d %H:%M:%S"),
                   l_date_obj.strftime("%Y-%m-%d"),
                   t_id, course_id, float(lattitude), float(longitude)])
            # Django's default behavior or transaction management would commit this.
            return HttpResponse(f"Success! Lecture created with ID {l_id}", status=200)

    return HttpResponse("Invalid Request Method", status=400)

# Dummy for tutorial to replace complex ID generation logic
def get_next_lecture_id():
    # In a real system, this would query the database for the max ID
    # and generate a new one, or use a database sequence.
    # For this tutorial, we'll return a simple incremented ID.
    import random
    return 'L' + str(random.randint(10000, 99999))
```
**Explanation**:
1.  **Teacher Identity**: The `t_id` of the logged-in teacher is retrieved from `request.session` (as established in [Chapter 2: User Authentication & Authorization](02_user_authentication___authorization_.md)). This ensures only the correct teacher can add lectures.
2.  **Form Data**: The function collects all lecture details submitted through the form.
3.  **Conflict Check**: It calls a helper function `check_lecture_conflict` (explained next) to see if this new lecture overlaps with any existing lectures for this teacher. If it does, an error is returned.
4.  **Date/Time Validation**: The system parses the date and time strings into Python `datetime` objects. It then performs crucial checks:
    *   The lecture date cannot be in the past.
    *   The start time cannot be in the past (relative to the *current* time).
    *   The start and end times must fall on the specified lecture date.
    *   The end time must be *after* the start time.
    *   The lecture duration cannot exceed 5 hours.
5.  **Unique Lecture ID**: A unique `l_id` is generated for the new lecture.
6.  **Database Insertion**: If all checks pass, an SQL `INSERT` statement adds the new lecture record to the `lecture` table in the database.

#### The `check_lecture_conflict` Function (Detail)

This helper function is crucial for preventing double-bookings.

```python
# Project/atp/views.py (simplified - check_lecture_conflict function)
# ... (imports from above) ...

def check_lecture_conflict(t_id, l_date_str, s_time_str, e_time_str):
    try:
        # 1. Parse input strings into time objects
        # The 'datetime-local' input provides format like "YYYY-MM-DDTHH:MM"
        # We need to combine date and time for database comparison
        s_datetime_obj = datetime.strptime(f"{l_date_str}T{s_time_str.split('T')[1]}", "%Y-%m-%dT%H:%M")
        e_datetime_obj = datetime.strptime(f"{l_date_str}T{e_time_str.split('T')[1]}", "%Y-%m-%dT%H:%M")

        # 2. Query the database for overlapping lectures
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT l_id, to_char(s_time, 'HH24:MI') as start_time, to_char(e_time, 'HH24:MI') as end_time
                FROM lecture
                WHERE t_id = %s
                  AND l_date = TO_DATE(%s, 'YYYY-MM-DD')
                  AND NOT (e_time <= TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS') OR s_time >= TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'))
            """, [t_id, l_date_str, s_datetime_obj.strftime("%Y-%m-%d %H:%M:%S"),
                   e_datetime_obj.strftime("%Y-%M-%d %H:%M:%S")])

            conflicting_lectures = cursor.fetchall()

            # 3. If conflicts are found, build an error message
            if conflicting_lectures:
                conflict_msg = "Lecture conflicts with existing lectures:\n"
                for lecture in conflicting_lectures:
                    conflict_msg += f"- Lecture {lecture[0]} ({lecture[1]} to {lecture[2]})\n"
                return HttpResponse(conflict_msg, status=400)

            return None # No conflicts found
    except ValueError as e:
        return HttpResponse(f"Invalid time format in conflict check: {str(e)}", status=400)
    except Exception as e:
        return HttpResponse(f"Validation error in conflict check: {str(e)}", status=500)
```
**Explanation**:
1.  **Time Parsing**: It takes the new lecture's proposed `l_date_str`, `s_time_str`, and `e_time_str` and converts them into comparable `datetime` objects.
2.  **SQL Query**: The heart of the conflict check is this SQL query. It looks in the `lecture` table for any lectures by the *same teacher* (`t_id`) on the *same date* (`l_date`) where the existing lecture's time range `(s_time, e_time)` *overlaps* with the new lecture's proposed time range.
    *   The `NOT (e_time <= new_s_time OR s_time >= new_e_time)` condition is a standard way to check for overlap. It means: "It's a conflict if the existing lecture *doesn't end before* the new one starts AND the existing lecture *doesn't start after* the new one ends."
3.  **Conflict Detected**: If `conflicting_lectures` is not empty, it means one or more overlaps were found, and an error message is generated. Otherwise, `None` is returned, indicating no conflicts.

## Internal Implementation: Adding a Lecture Flow

Let's visualize the step-by-step process when Dr. Smith adds a new lecture:

```mermaid
sequenceDiagram
    participant Teacher as Dr. Smith
    participant WebBrowser
    participant AttendanceSystem
    participant Database

    Teacher->>WebBrowser: 1. Fills "Add Lecture" form
    WebBrowser->>AttendanceSystem: 2. Sends lecture details (POST request)
    Note over AttendanceSystem: 3. Extracts teacher ID from session.
                                 Parses lecture details.
    AttendanceSystem->>AttendanceSystem: 4. Calls check_lecture_conflict()
    AttendanceSystem->>Database: 5. "SELECT lectures for T_ID on L_DATE that overlap with new S_TIME, E_TIME?"
    Database-->>AttendanceSystem: 6. Returns conflicting lectures (if any)
    alt No Conflicts
        AttendanceSystem->>AttendanceSystem: 7. Performs date/time validations (past check, duration)
        AttendanceSystem->>AttendanceSystem: 8. Generates new unique Lecture ID
        AttendanceSystem->>Database: 9. "INSERT INTO lecture VALUES (new L_ID, S_TIME, E_TIME, ...)"
        Note over Database: 10. Runs 'teacher_lecture' trigger to check teacher-course assignment.
        Database-->>AttendanceSystem: 11. Confirmation (Lecture added)
        AttendanceSystem-->>WebBrowser: 12. "Success! Lecture created with ID X."
        WebBrowser->>Teacher: 13. Sees success message
    else Conflicts or Validation Failed
        AttendanceSystem-->>WebBrowser: 7. Returns error message (e.g., "Time conflict" or "Past date")
        WebBrowser->>Teacher: 8. Sees error message
    end
```

### Database Interaction: The `lecture` Table

The `lecture` table, first introduced in [Chapter 1: Database Schema (Entities & Relationships)](01_database_schema__entities___relationships__.md), is where all lecture information is stored.

```sql
-- inputs/table.sql (simplified)
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
**Explanation**:
*   `l_id`: Unique identifier for each lecture (Primary Key).
*   `s_time` and `e_time`: Start and end timestamps of the lecture.
*   `l_date`: Date of the lecture.
*   `t_id`: Foreign Key linking to the `teacher` table, indicating which teacher is giving the lecture.
*   `course_id`: Foreign Key linking to the `course` table, indicating which course the lecture is for.
*   `lattitude`, `longitude`: Location coordinates for the lecture, used for [attendance validation (Chapter 3)](03_attendance_management_core_logic_.md).

### Ensuring Teacher-Course Assignment: The `teacher_lecture` Trigger

Just like the `stud_attendance_trigger` in Chapter 3, a database **trigger** helps maintain data integrity. The `teacher_lecture` trigger ensures that a teacher can only add lectures for courses they are actually assigned to teach.

```sql
-- inputs/trigger_for_creating_lecture.sql (simplified)
CREATE OR REPLACE TRIGGER teacher_lecture
BEFORE INSERT ON lecture
FOR EACH ROW
DECLARE
    v_count NUMBER := 0;
BEGIN
    -- Check if teacher is assigned to this course
    SELECT COUNT(*) INTO v_count
    FROM teacher_course
    WHERE t_id = :NEW.t_id
      AND course_id = :NEW.course_id;

    IF v_count = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'TEACHER NOT ASSIGNED TO THIS COURSE');
    END IF;
END;
/
```
**Explanation**:
1.  `BEFORE INSERT ON lecture`: This trigger automatically runs *before* any new record is inserted into the `lecture` table.
2.  `SELECT COUNT(*) INTO v_count FROM teacher_course WHERE t_id = :NEW.t_id AND course_id = :NEW.course_id;`: It checks the `teacher_course` table (which defines which teacher teaches which course) to see if the teacher (`:NEW.t_id` refers to the `t_id` of the new lecture being inserted) is assigned to the specified course (`:NEW.course_id`).
3.  `IF v_count = 0 THEN RAISE_APPLICATION_ERROR(...)`: If `v_count` is 0, it means the teacher is *not* assigned to that course, and the insertion is stopped with an error message. This prevents teachers from scheduling classes for courses they don't teach.

## Other Teacher Management Features: Update and Delete Lectures

Besides adding new lectures, teachers also need to modify or remove existing ones.

### Updating an Existing Lecture

A teacher might need to change the time, date, or location of an upcoming lecture.

**User Interface (`update_lecture.html`)**:

```html
<!-- Project/atp/templates/atp/update_lecture.html (simplified) -->
<body>
    <h2>Update Lecture</h2>
    <form action="{% url 'update_existing_lecture' %}" method="post">
        {% csrf_token %}
        <label for="l_id">Lecture ID (L_ID)</label>
        <input type="text" id="l_id" name="l_id" required>

        <label for="s_time">New Start Time (S_TIME)</label>
        <input type="datetime-local" id="s_time" name="s_time">

        <label for="e_time">New End Time (E_TIME)</label>
        <input type="datetime-local" id="e_time" name="e_time">

        <label for="l_date">New Lecture Date (L_DATE)</label>
        <input type="date" id="l_date" name="l_date">

        <label for="lattitude">New Latitude</label>
        <input type="number" step="0.000001" id="lattitude" value="12.971599" name="lattitude">

        <label for="longitude">New Longitude</label>
        <input type="number" step="0.000001" id="longitude" value ="77.594566" name="longitude">

        <button type="submit">Update Lecture</button>
    </form>
    <a href="{% url 'teacher_courses' %}" class="back-link">← Back to My Courses</a>
</body>
```

**System Logic (`views.py` - simplified `update_existing_lecture` function)**:

```python
# Project/atp/views.py (simplified - update_existing_lecture function)
# ... (imports and other functions like check_lecture_conflict_update, check_lecture) ...

# Helper function: Checks if a lecture can be changed (i.e., has not started yet)
def check_lecture(l_id):
    # This function queries the lecture table for a given l_id.
    # It compares the current time with the lecture's start time.
    # If the lecture has already started or completed, it returns a message
    # indicating it cannot be changed. Otherwise, it indicates it can.
    # ... (Actual implementation details would be here) ...
    pass # We'll see the full implementation shortly!

def update_existing_lecture(request):
    teacher_info = request.session.get('teacher_info')
    teacher_id = teacher_info[0]

    if request.method == 'POST':
        l_id = request.POST.get('l_id')
        # ... (get other updated details like s_time, e_time, l_date, lattitude, longitude) ...

        # 1. First, check if the lecture is eligible for update (hasn't started yet)
        status_check = check_lecture(l_id)
        data = json.loads(status_check.content) # Convert JsonResponse to Python dict
        if not data['can_change']:
            return status_check # Cannot update, return the error from check_lecture

        # 2. Perform a conflict check with the NEW proposed times, excluding the lecture itself
        # check_lecture_conflict_update is similar to check_lecture_conflict but ignores the l_id being updated
        # conflict_response = check_lecture_conflict_update(teacher_id, new_l_date, new_s_time, new_e_time, l_id)
        # if conflict_response:
        #     return conflict_response

        # 3. Perform similar date/time validations as in insert_lecture
        # ... (past date/time, duration checks) ...

        # 4. Update the lecture in the database
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE lecture
                SET s_time = TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'),
                    e_time = TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS'),
                    l_date = TO_DATE(%s, 'YYYY-MM-DD'),
                    lattitude = %s, longitude = %s
                WHERE l_id = %s AND t_id = %s
            """, [new_s_time_formatted, new_e_time_formatted, new_l_date_formatted,
                   float(lattitude), float(longitude), l_id, teacher_id])
            # ... (commit, etc.) ...
            return HttpResponse("Updated Successfully!")
    return HttpResponse("Invalid Request Method", status=400)
```
**Explanation**:
1.  **Eligibility Check**: Before allowing any update, `check_lecture(l_id)` is called to ensure the lecture hasn't already started. If it has, the update is rejected.
2.  **Conflict Check for Update**: A specialized conflict check, `check_lecture_conflict_update`, is used. It's almost identical to `check_lecture_conflict` but smartly ignores the `l_id` *being updated*. This way, a lecture doesn't "conflict with itself" if its time range doesn't change, but it still prevents conflicts with *other* lectures.
3.  **Date/Time Validation**: Similar validations as for adding a lecture (past date, duration) are performed.
4.  **Database Update**: An SQL `UPDATE` statement modifies the `lecture` record for the specified `l_id` and `t_id` (ensuring only the correct teacher can modify their lecture).

### Deleting an Existing Lecture

Teachers can also cancel lectures.

**User Interface (`delete_lecture.html`)**:

```html
<!-- Project/atp/templates/atp/delete_lecture.html (simplified) -->
<body>
    <h2>Delete Lecture</h2>
    <form action="{% url 'delete_existing_lecture' %}" method="post">
        {% csrf_token %}
        <label for="l_date">Lecture Date (L_DATE)</label>
        <input type="date" id="l_date" name="l_date" required>

        <label for="s_time">Start Time (S_TIME)</label>
        <input type="time" id="s_time" name="s_time" required>

        <button type="submit">Delete Lecture</button>
    </form>
    <a href="{% url 'teacher_courses' %}" class="back-link">← Back to My Courses</a>
</body>
```

**System Logic (`views.py` - simplified `delete_existing_lecture` function)**:

```python
# Project/atp/views.py (simplified - delete_existing_lecture function)
# ... (imports and check_lecture function from above) ...

def delete_existing_lecture(request):
    teacher_info = request.session.get('teacher_info')
    t_id = teacher_info[0]

    if request.method == 'POST':
        # 1. Get lecture identification details
        l_date_str = request.POST.get('l_date')
        s_time_str = request.POST.get('s_time') # This is just time, need to combine with date

        try:
            # 2. Find the l_id based on teacher, date, and start time
            # Combine date and time for precise lookup
            s_datetime_lookup_str = f"{l_date_str} {s_time_str}:00"
            
            with connection.cursor() as cursor:
                cursor.execute("""SELECT l_id FROM lecture
                    WHERE t_id = %s
                    AND l_date = TO_DATE(%s, 'YYYY-MM-DD')
                    AND s_time = TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS')
                """, [t_id, l_date_str, s_datetime_lookup_str])
                result = cursor.fetchone()

                if not result:
                    return HttpResponse("Lecture not found or you are not the assigned teacher.", status=404)

                l_id_to_delete = result[0]

                # 3. Check if the lecture can be deleted (has not started yet)
                status_check_response = check_lecture(l_id_to_delete)
                data = json.loads(status_check_response.content)
                if not data['can_change']: # check_lecture returns 'can_change': True/False
                    return status_check_response # Cannot delete, return the error from check_lecture

                # 4. Delete the lecture from the database
                cursor.execute("""DELETE FROM lecture WHERE l_id = %s""", [l_id_to_delete])
                # ... (commit, etc.) ...
                return HttpResponse("Lecture Deleted Successfully!")

        except ValueError as e:
            return HttpResponse(f"Invalid date/time format: {str(e)}", status=400)
        except Exception as e:
            return HttpResponse(f"Database error: {str(e)}", status=500)
    return HttpResponse("Invalid Request Method", status=400)
```
**Explanation**:
1.  **Identify Lecture**: The teacher provides the lecture date and start time. The system then queries the `lecture` table to find the specific `l_id` associated with that teacher, date, and start time. This is important to ensure the correct lecture is targeted for deletion and that the teacher has permission.
2.  **Eligibility Check**: Similar to updating, `check_lecture(l_id)` is called. A lecture can only be deleted if it *has not started yet*.
3.  **Database Deletion**: If the lecture is found and is eligible for deletion, an SQL `DELETE` statement removes the record from the `lecture` table.

## Internal Implementation: `check_lecture` in Detail

Let's look at the actual `check_lecture` helper function, used by both update and delete operations.

```python
# Project/atp/views.py (simplified - check_lecture function)
# ... (imports from above) ...

def check_lecture(l_id):
    try:
        current_time = datetime.now()

        with connection.cursor() as cursor:
            # Fetch the lecture's start time from the database
            cursor.execute("""
                SELECT
                    TO_CHAR(s_time, 'YYYY-MM-DD HH24:MI:SS') as start_datetime
                FROM lecture
                WHERE l_id = %s
            """, [l_id])

            lecture_data = cursor.fetchone()

            if not lecture_data:
                # Return a JSON response for consistency with other parts of the system
                return JsonResponse({'can_change': False, 'message': 'Lecture not found'}, status=404)

            # Convert the fetched start time string back to a datetime object
            lecture_start = datetime.strptime(lecture_data[0], '%Y-%m-%d %H:%M:%S')

            # Compare current time with lecture start time
            can_change = current_time < lecture_start

            message = 'Lecture can be changed/deleted (has not started)' if can_change else 'Lecture cannot be changed/deleted (already started or completed)'
            return JsonResponse({
                'can_change': can_change,
                'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'lecture_start': lecture_start.strftime('%Y-%m-%d %H:%M:%S'),
                'message': message
            })
    except Exception as e:
        return JsonResponse({'can_change': False, 'message': f'Error checking lecture status: {str(e)}'}, status=500)
```
**Explanation**:
1.  **Current Time**: Gets the exact current date and time.
2.  **Fetch Lecture Start Time**: Queries the `lecture` table to get the `s_time` for the given `l_id`.
3.  **Comparison**: Compares `current_time` with `lecture_start`. If the current time is *before* the lecture's start time, `can_change` is `True`, meaning it's still possible to modify or delete the lecture. Otherwise, `can_change` is `False`.
4.  **Response**: Returns a `JsonResponse` with `can_change` status and a descriptive message.

## Conclusion

In this chapter, we explored the important capabilities teachers have for managing their courses: **Lecture Management**. We learned how teachers can **add new lectures**, **update existing lecture details**, and **delete lectures** through simple web forms. Crucially, we delved into the **scheduling conflict checks** that prevent double-bookings and ensure smooth operation, as well as the important checks to prevent modifications of lectures that have already started. We also saw how database triggers contribute to data integrity by enforcing that teachers only manage courses they are assigned to.

Understanding how lectures are managed by teachers sets the stage for how the entire system functions. Next, we'll broaden our perspective to understand the overall structure of how different parts of our application connect and display information to users in [Chapter 5: Application Logic (Views)](05_application_logic__views__.md).

---


<sub><sup>**References**: [[1]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/add_lecture.html), [[2]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/delete_lecture.html), [[3]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/update_lecture.html), [[4]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/views.py), [[5]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/inputs/insert_lectures.sql), [[6]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/inputs/trigger_for_creating_lecture.sql)</sup></sub>
