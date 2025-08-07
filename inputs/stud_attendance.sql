create or replace trigger stud_attendance_trigger
before insert on attendance
for each row
declare
v_count NUMBER;
c_count NUMBER;
c_id course.course_id%type;
begin
select count(*) into c_count from lecture where l_id=:NEW.l_id;
if c_count = 0 then
raise_application_error(-20001,'COURSE DOES NOT EXIST');
end if;

select course_id into c_id from lecture where l_id=:NEW.l_id;

select count(*) into v_count
from student_course where stud_id=:NEW.stud_id and course_id=c_id;

if v_count = 0 then
RAISE_APPLICATION_ERROR(-20001, 'STUDENT NOT ENROLLED IN THIS COURSE');
end if;
end;
/