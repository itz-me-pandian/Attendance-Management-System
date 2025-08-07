set echo on;

drop table attendance;
drop table on_duty;
drop table student_course;
drop table teacher_course;
drop table teacher_phno;
drop table lecture;
drop table course;
drop table teacher;
drop table student;
drop table department;
drop table admin_tab;

create table department (
	dep_id varchar(10) constraint dep_pk primary key,
	dep_name varchar(50)
);


create table student (
	stud_id varchar(10) constraint stpk primary key,
	fname varchar(30),
	lname varchar(30),
	minit varchar(10),
	dob date,
	dep_id varchar(10) constraint sd_fk references department(dep_id),
	barcode varchar(15)
);

create table teacher (
	t_id varchar(10) constraint t_pk primary key,
	fname varchar(30),
	lname varchar(30),
	email varchar(50),
	dep_id varchar(10) constraint td_fk references department(dep_id),
	hod_id varchar(20) constraint th_fk references teacher(t_id)
);

create table course (
	course_id varchar(20) constraint co_pk primary key,
	course_name varchar(50),
	dep_id varchar(10) constraint cd_fk references department(dep_id)
);

create table lecture (
	l_id varchar(10) constraint lpk primary key,
	s_time TIMESTAMP,
	e_time TIMESTAMP,
	l_date date,
	t_id varchar(20) constraint tfk references teacher(t_id),
	course_id varchar(20) constraint cfk references course(course_id),
	lattitude number(9,6),
	longitude number(9,6)
);

create table teacher_phno (
	t_id varchar(10) constraint tpt_fk references teacher(t_id),
	ph_no number(10),
	constraint tpno_pk primary key(t_id,ph_no)
);

create table teacher_course (
	t_id varchar(10) constraint tct_fk references teacher(t_id),
	course_id varchar(20) constraint tcc_fk references course(course_id),
	constraint tc_pk primary key(t_id,course_id)
);

create table student_course (
	stud_id varchar(10) constraint scs_fk references student(stud_id),
	course_id varchar(20) constraint scc_fk references course(course_id),
	t_id varchar(10) constraint sct_fk references teacher(t_id),
	constraint sc_pk primary key(stud_id,course_id)
);

create table on_duty (
	stud_id varchar(10) constraint ods_fk references student(stud_id),
	l_id varchar(10) constraint odl references lecture(l_id),
	reason varchar(50),
	constraint od_pk primary key(stud_id,l_id)
);

create table attendance (
	stud_id varchar(10) constraint as_fk references student(stud_id),
	l_id varchar(10) constraint al_fk references lecture(l_id) on delete cascade,
	date_recorded date,
	time_recorded timestamp,
	lattitude number(9,6),
	longitude number(9,6),
	constraint a_pk primary key(stud_id,l_id)
);	

create table admin_tab
(admin_id varchar2(20) constraint admin_pk primary key, 
 admin_name varchar2(20));
 
insert into admin_tab values('DBMS','SSN');