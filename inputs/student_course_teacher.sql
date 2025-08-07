create or replace trigger check_student_enrollment
before insert on student_course
for each row
declare
    v_teacher_count number;
    v_student_count number;

begin
    select count(*) into v_teacher_count
    from teacher_course
    where t_id = :new.t_id
    and course_id = :new.course_id;


    select count(*) into v_student_count
    from student_course
    where stud_id = :new.stud_id
    and course_id = :new.course_id;


    if v_teacher_count = 0 then
        raise_application_error(-20001, 'teacher is not linked with this course');

    elsif v_student_count > 0 then
        raise_application_error(-20002, 'student is already enrolled in this course');

    end if;
end;
