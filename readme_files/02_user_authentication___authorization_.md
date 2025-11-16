# Chapter 2: User Authentication & Authorization

Welcome back! In [Chapter 1: Database Schema (Entities & Relationships)](01_database_schema__entities___relationships__.md), we learned how to organize all our application's data, like student names, teacher details, and course information, using a blueprint called the Database Schema. We built the "rooms" and "storage cabinets" for our data.

Now, imagine our well-organized data is like a library full of valuable books. You wouldn't want just anyone walking in and taking any book they want, right? You'd want to know *who* is entering and *what* they are allowed to do. This is exactly the problem that **User Authentication & Authorization** solves for our Attendance Management System.

## What Problem Are We Solving? The Gatekeeper!

Our Attendance Management System has different types of users:
*   **Administrators (Admins)**: They can add new students, teachers, and courses. They have broad powers.
*   **Teachers**: They can view their courses, add new lectures, and check attendance for their students.
*   **Students**: They can view their profile, see their attendance, and mark attendance for lectures.

Each of these user types needs to access different parts of the system and perform specific actions. We need a way to:
1.  **Identify Users**: Make sure someone is who they say they are (e.g., "Is this really John Doe, a student?"). This is **Authentication**.
2.  **Control Access**: Determine what each identified user is allowed to do (e.g., "John Doe is a student, so he can't add new teachers"). This is **Authorization**.

Think of User Authentication & Authorization as the **gatekeeper** of our application. It makes sure only the right people get in, and once inside, they only go to the areas they're permitted to access.

## Key Concepts: Authentication vs. Authorization

Let's break down these two important terms:

### 1. Authentication: "Who are you?"

**Authentication** is the process of verifying a user's identity. It's like showing your ID card at a secure entrance. You provide a username (or ID) and a password, and the system checks if these match a record in its database.

**In our system**:
*   A student enters their name and student ID.
*   A teacher enters their name and teacher ID.
*   An admin enters their admin ID and password.

If the credentials match, the system confirms, "Okay, you are who you say you are!" and lets you in.

### 2. Authorization: "What can you do?"

**Authorization** is the process of deciding what an authenticated user is allowed to do within the system. It's like the security guard at the entrance, who, after checking your ID, tells you, "You can go to the student lounge, but you can't enter the faculty meeting room."

**In our system**:
*   An **admin** is authorized to add new courses.
*   A **teacher** is authorized to create a new lecture for their course.
*   A **student** is authorized to view their own attendance records.

Authorization happens *after* authentication. The system first needs to know *who you are* before it can decide *what you can do*.

## Solving Our Use Case: A Student Logs In

Let's walk through a common use case: a student wants to log into the system to view their attendance.

**Input**: The student goes to the login page and enters their name ("Arjun Kumar") and student ID ("2370001").
**Output**: If correct, Arjun gets redirected to his personal dashboard. If incorrect, he gets an error message.

### User Interface: The Login Form (`student_login.html`)

First, Arjun needs a way to provide his details. Our system provides a simple web form for this:

```html
<!-- Project/atp/templates/atp/student_login.html (simplified) -->
<form action="{% url 'student_check' %}" method="post">
    {% csrf_token %}
    <input type="text" name="name" placeholder="Student Name" required>
    <input type="password" name="stud_id" placeholder="Student ID (Password)" required>
    <button type="submit">Login</button>
</form>
```
**Explanation**:
*   `form action="{% url 'student_check' %}" method="post"`: This tells the browser to send the entered information to a specific part of our application (called `student_check`) when the "Login" button is clicked. The `method="post"` means the data is sent securely in the background.
*   `{% csrf_token %}`: This is a security feature in Django that helps protect against certain types of attacks. Don't worry about the details for now, just know it's important for forms.
*   `input type="text" name="name"`: This creates a text box for Arjun to type his full name.
*   `input type="password" name="stud_id"`: This creates a password-like box for Arjun to type his Student ID. It's `type="password"` so the text is hidden as he types.

### System Logic: Checking Credentials (`views.py`)

When Arjun clicks "Login", the information (`name` and `stud_id`) is sent to the `student_check` function in our `views.py` file. This function then interacts with the database to verify the identity.

```python
# Project/atp/views.py (simplified)
from django.db import connection
from django.shortcuts import render, HttpResponse

def student_check(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        stud_id_as_password = request.POST.get('stud_id') # Treating stud_id as password here

        # Split full name into first and last name
        name_parts = full_name.strip().split()
        if len(name_parts) < 2:
            return HttpResponse("Please enter both first and last name.", status=400)
        fname = name_parts[0]
        lname = name_parts[1]

        with connection.cursor() as cursor:
            # Query the database to find a student with matching credentials
            cursor.execute("""
                SELECT * FROM student
                WHERE fname = %s AND lname = %s AND stud_id = %s
            """, [fname, lname, stud_id_as_password])
            student = cursor.fetchone() # Get the first matching student, if any

        if student:
            # If a student is found, they are authenticated!
            request.session['current_user'] = student[0] # Remember this user for later
            return render(request, 'atp/student_dashboard.html') # Grant authorization to dashboard
        else:
            # No matching student found
            return HttpResponse("Invalid Student Name or ID", status=401)
    return HttpResponse("Invalid Request Method", status=400)
```
**Explanation**:
1.  `if request.method == 'POST'`: Checks if the data was sent from the login form.
2.  `request.POST.get('name')` and `request.POST.get('stud_id')`: This is how our Django application gets the `name` and `stud_id` that Arjun typed into the form.
3.  **Name Parsing**: The `full_name` is split into `fname` (first name) and `lname` (last name).
4.  `with connection.cursor() as cursor:`: This opens a direct connection to our database.
5.  `cursor.execute(...)`: This runs a SQL query (like we saw in Chapter 1!) to search the `student` table. It looks for a row where the `fname`, `lname`, and `stud_id` (used as a password here) all match what Arjun entered.
6.  `student = cursor.fetchone()`: If a matching student is found, `student` will contain their details. If not, `student` will be empty (`None`).
7.  `if student:`: If a student record was found (meaning authentication was successful):
    *   `request.session['current_user'] = student[0]`: We store the student's ID (the first item in the `student` data) in something called `request.session`. This is like giving Arjun a temporary badge that the system remembers, so it knows he's logged in as `current_user` for future requests.
    *   `return render(request, 'atp/student_dashboard.html')`: Arjun is now **authorized** to see the `student_dashboard`.
8.  `else:`: If no student record was found, authentication failed, and Arjun gets an "Invalid Student Name or ID" message.

## Internal Implementation: The Login Flow

Let's visualize the step-by-step process when Arjun tries to log in:

```mermaid
sequenceDiagram
    participant User as Arjun (Student)
    participant WebBrowser
    participant AttendanceSystem as Attendance System
    participant Database

    User->>WebBrowser: 1. Enters Name and Student ID in login form
    WebBrowser->>AttendanceSystem: 2. Sends login request (Name, Student ID)
    Note over AttendanceSystem: 3. Extracts Name and Student ID from request.
                                 Splits Name into First Name and Last Name.
    AttendanceSystem->>Database: 4. "Check if (First Name, Last Name, Student ID) exists in 'student' table?"
    Database-->>AttendanceSystem: 5. Returns Student data (if found) or nothing
    alt Student Found (Authenticated)
        AttendanceSystem->>AttendanceSystem: 6. Stores Student ID in session (remembers Arjun)
        AttendanceSystem-->>WebBrowser: 7. Shows Student Dashboard (Authorized)
        WebBrowser->>User: 8. Arjun sees his dashboard
    else Student Not Found (Authentication Failed)
        AttendanceSystem-->>WebBrowser: 9. Shows "Invalid Credentials" message
        WebBrowser->>User: 10. Arjun sees error message
    end
```

### Deeper Dive into the Code

The same basic logic applies to Admin and Teacher logins. They all use a form to send credentials to a specific function in `views.py`, which then queries the appropriate table in the database.

Here are the relevant parts of the database schema for storing user credentials:

```sql
-- inputs/table.sql (simplified)
create table student (
	stud_id varchar(10) constraint stpk primary key,
	fname varchar(30),
	lname varchar(30),
	-- ... other student details
);

create table teacher (
	t_id varchar(10) constraint t_pk primary key,
	fname varchar(30),
	lname varchar(30),
	-- ... other teacher details
);

create table admin_tab (
    admin_id varchar2(20) constraint admin_pk primary key,
    admin_name varchar2(20) -- This is effectively the password for admin login
);
```
**Explanation**:
*   The `student` table stores `fname`, `lname`, and `stud_id`. When a student logs in, we verify these three pieces of information.
*   The `teacher` table stores `fname`, `lname`, and `t_id`.
*   The `admin_tab` table stores `admin_id` and `admin_name`. For the admin login, `admin_id` acts as the username and `admin_name` acts as the password.

And here's how the other login checks in `views.py` use these tables:

**Admin Login Check**:

```python
# Project/atp/views.py (simplified)
def admin_check(request):
    if request.method == 'POST':
        admin_id_input = request.POST.get('admin_id')
        admin_password_input = request.POST.get('password')

        with connection.cursor() as cursor:
            # Check admin_tab for matching admin_id and admin_name (as password)
            cursor.execute("""
                SELECT * FROM admin_tab
                WHERE admin_id = :admin_id AND admin_name = :admin_password
            """, {'admin_id': admin_id_input, 'admin_password': admin_password_input})
            admin = cursor.fetchone()

        if admin:
            # Admin authenticated, grant authorization to admin dashboard
            return render(request, 'atp/admin_dashboard.html')
        else:
            return HttpResponse("Invalid Admin ID or Password", status=401)
    # ... handle other request methods
```

**Teacher Login Check**:

```python
# Project/atp/views.py (simplified)
def teacher_check(request):
    if request.method == 'POST':
        teacher_full_name = request.POST.get('teacher_name')
        teacher_id_as_password = request.POST.get('teacher_id')

        # Split full name into first and last name
        name_parts = teacher_full_name.strip().split()
        if len(name_parts) < 2:
            return HttpResponse("Please enter both first and last name.", status=400)
        fname = name_parts[0]
        lname = name_parts[1]

        with connection.cursor() as cursor:
            # Check teacher table for matching credentials
            cursor.execute("""
                SELECT * FROM teacher
                WHERE fname = :fname AND lname = :lname AND t_id = :tid
            """, {'fname': fname, 'lname': lname, 'tid': teacher_id_as_password})
            teacher = cursor.fetchone()

        if teacher:
            # Teacher authenticated, store info and grant authorization to dashboard
            request.session['teacher_info'] = teacher
            return render(request, 'atp/teacher_dashboard.html')
        else:
            return HttpResponse("Invalid Teacher Name or ID", status=401)
    # ... handle other request methods
```

**How Authorization Continues**:
After a user successfully logs in, their identity is stored in the `request.session`. This "session" acts like their badge. Whenever they try to access another page (like a student viewing their attendance), the system can check their badge (`request.session['current_user']` for students, `request.session['teacher_info']` for teachers) to confirm they are indeed logged in and authorized for that specific action or page. If a page requires an admin, the system would typically check if an admin user is logged in.

## Conclusion

In this chapter, we've explored the crucial concepts of **User Authentication** and **Authorization**.
*   **Authentication** is about verifying *who you are* (like checking your ID).
*   **Authorization** is about determining *what you can do* once your identity is confirmed.

These mechanisms are the gatekeepers of our Attendance Management System, ensuring that only authenticated users can enter and that they only access functionalities appropriate for their role (Admin, Teacher, or Student). We saw how simple login forms (`.html` files) interact with our application logic (`views.py`) and the database (`table.sql`) to perform these checks.

Now that we know who can access the system and what they can do, the next step is to understand the heart of the system: how attendance is actually managed. In the next chapter, we'll dive into [Attendance Management Core Logic](03_attendance_management_core_logic_.md).

---

<sub><sup>**References**: [[1]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/admin_login.html), [[2]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/student_login.html), [[3]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/templates/atp/teacher_login.html), [[4]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/Project/atp/views.py), [[5]](https://github.com/itz-me-pandian/Attendance-Management-System/blob/904ec3a6902ecfc89889f8f4ac3dfbb2dcd8e182/inputs/table.sql)</sup></sub>