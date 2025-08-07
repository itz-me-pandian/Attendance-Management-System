@"C:\Users\pandi\Downloads\dbms\inputs\table.sql"


REM inserting department records

insert into department values('CS001','Computer Science');


REM inserting student records

INSERT INTO student VALUES ('2370001', 'arjun', 'kumar', 'R', TO_DATE('2004-06-15', 'YYYY-MM-DD'), 'CS001', '9876543210');
INSERT INTO student VALUES ('2370002', 'divya', 'shree', 'A', TO_DATE('2005-01-24', 'YYYY-MM-DD'), 'CS001', '7894561230');
INSERT INTO student VALUES ('2370003', 'karthik', 'reddy', 'V', TO_DATE('2004-03-30', 'YYYY-MM-DD'), 'CS001', '9568741205');
INSERT INTO student VALUES ('2370004', 'meena', 'kumari', 'S', TO_DATE('2004-12-11', 'YYYY-MM-DD'), 'CS001', '8459631258');
INSERT INTO student VALUES ('2370005', 'vishal', 'raj', 'T', TO_DATE('2005-07-19', 'YYYY-MM-DD'), 'CS001', '7788996655');
INSERT INTO student VALUES ('2370006', 'sneha', 'patel', 'B', TO_DATE('2004-05-09', 'YYYY-MM-DD'), 'CS001', '8987654312');
INSERT INTO student VALUES ('2370007', 'rohit', 'sharma', 'M', TO_DATE('2005-08-22', 'YYYY-MM-DD'), 'CS001', '8123456790');
INSERT INTO student VALUES ('2370008', 'lavanya', 'krishna', 'K', TO_DATE('2004-09-17', 'YYYY-MM-DD'), 'CS001', '9876549876');
INSERT INTO student VALUES ('2370009', 'naveen', 'singh', 'N', TO_DATE('2005-03-14', 'YYYY-MM-DD'), 'CS001', '9547863210');
INSERT INTO student VALUES ('2370010', 'isha', 'gupta', 'G', TO_DATE('2005-02-12', 'YYYY-MM-DD'), 'CS001', '7854123698');


REM inserting teacher records

INSERT INTO teacher VALUES('T001','mani','maran','mani@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T002','deepa','shree','deepa@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T003','ravi','kumar','ravi.kumar@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T004','priya','das','priya.das@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T005','suresh','reddy','suresh.reddy@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T006','kavitha','ram','kavitha.ram@gmail.com','CS001','T001');
INSERT INTO teacher VALUES('T007','arun','kumar','arun.kumar@gmail.com','CS001','T001');


REM inserting course records

INSERT INTO course VALUES ('C001', 'DBMS', 'CS001');
INSERT INTO course VALUES ('C002', 'Operating Systems', 'CS001');
INSERT INTO course VALUES ('C003', 'Computer Networks', 'CS001');
INSERT INTO course VALUES ('C004', 'Machine Learning', 'CS001');
INSERT INTO course VALUES ('C005', 'Artificial Intelligence', 'CS001');
INSERT INTO course VALUES ('C006', 'Compiler Design', 'CS001');

REM  inserting lecture records

@"C:\Users\pandi\Downloads\dbms\inputs\insert_lectures.sql";
@"C:\Users\pandi\Downloads\dbms\inputs\lect_up.sql";


REM inserting teacher phnorecords

INSERT INTO teacher_phno VALUES('T001', 9876543210);
INSERT INTO teacher_phno VALUES('T002', 9812345678);
INSERT INTO teacher_phno VALUES('T003', 9789456123);
INSERT INTO teacher_phno VALUES('T004', 9345678901);
INSERT INTO teacher_phno VALUES('T005', 9887766554);
INSERT INTO teacher_phno VALUES('T006', 9871234560);
INSERT INTO teacher_phno VALUES('T007', 9367812345);




REM inserting teacher course records

INSERT INTO teacher_course VALUES('T002', 'C001');
INSERT INTO teacher_course VALUES('T003', 'C002');
INSERT INTO teacher_course VALUES('T004', 'C003');
INSERT INTO teacher_course VALUES('T005', 'C004');
INSERT INTO teacher_course VALUES('T006', 'C005');
INSERT INTO teacher_course VALUES('T007', 'C006');

REM inserting student_course records

@"C:\Users\pandi\Downloads\dbms\inputs\stc_input.sql";


REM inserting data for attendance

@"C:\Users\pandi\Downloads\dbms\inputs\att.sql";

REM Triggers

@"C:\Users\pandi\Downloads\dbms\inputs\trigger_for_inserting_attendance_row.sql"
@"C:\Users\pandi\Downloads\dbms\inputs\trigger_for_teacher_student_link.sql"
@"C:\Users\pandi\Downloads\dbms\inputs\trigger_for_creating_lecture.sql"