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