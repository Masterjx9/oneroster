from flask import Blueprint

from app.routes.oauth import (
    ROSTER_CORE_READONLY_SCOPE,
    ROSTER_DEMOGRAPHICS_READONLY_SCOPE,
    ROSTER_READONLY_SCOPE,
    bearer_token_required,
)
from app.models.AcademicSessions import AcademicSession
from app.models.Class import Class
from app.models.Course import Course
from app.models.Demographics import Demographics
from app.models.Enrollment import Enrollment
from app.models.Org import Org
from app.models.User import User
from app.utils.collection_response import collection_response

rostering = Blueprint('rostering', __name__)

# Return collection of all academic sessions.
@rostering.route('/academicSessions', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllAcademicSessions():
    return collection_response("academicSessions", [session.to_dict() for session in AcademicSession.query.all()])

# Return specific Academic Session.
@rostering.route('/academicSessions/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAcademicSession(id) -> dict:
    session = AcademicSession.get_by_sourced_id(id)
    if not session:
        print(f"Academic Session not found: {id}")
        return {"error": "Not found"}, 404
    return {"academicSession": session.to_dict()}

# Return collection of classes.
@rostering.route('/classes', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllClasses() -> dict:
    classes = Class.query.all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return specific class.
@rostering.route('/classes/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getClass(id) -> dict:
    cls = Class.get_by_sourced_id(id)
    if not cls:
        return {"error": "Not found"}, 404
    return {"class": cls.to_dict()}

# Return collection of courses.
@rostering.route('/courses', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllCourses() -> dict:
    courses = Course.query.all()
    return collection_response("courses", [course.to_dict() for course in courses])

# Return specific course.
@rostering.route('/courses/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getCourse(id) -> dict:
    course = Course.get_by_sourced_id(id)
    if not course:
        return {"error": "Not found"}, 404
    return {"course": course.to_dict()}

# Return collection of grading periods. A Grading Period is an instance of an AcademicSession.
@rostering.route('/gradingPeriods', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllGradingPeriods() -> dict:
    grading_periods = AcademicSession.query.filter_by(type="gradingPeriod").all()
    return collection_response("gradingPeriods", [period.to_dict() for period in grading_periods])

# Return specific Grading Period. A Grading Period is an instance of an AcademicSession.
@rostering.route('/gradingPeriods/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getGradingPeriod(id) -> dict:
    period = AcademicSession.get_by_sourced_id(id)
    if not period or period.type != "gradingPeriod":
        return {"error": "Not found"}, 404
    return {"gradingPeriod": period.to_dict()}

# Return collection of demographics.
@rostering.route('/demographics', methods=['GET'])
@bearer_token_required(ROSTER_DEMOGRAPHICS_READONLY_SCOPE)
def getAllDemographics() -> dict:
    demographics = Demographics.query.all()
    return collection_response("demographics", [demo.to_dict() for demo in demographics])

# Return specific demographics.
@rostering.route('/demographics/<id>', methods=['GET'])
@bearer_token_required(ROSTER_DEMOGRAPHICS_READONLY_SCOPE)
def getDemographics(id) -> dict:
    demo = Demographics.get_by_sourced_id(id)
    if not demo:
        return {"error": "Not found"}, 404
    return {"demographic": demo.to_dict()}

# Return collection of all enrollments.
@rostering.route('/enrollments', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllEnrollments() -> dict:
    enrollments = Enrollment.query.all()
    return collection_response("enrollments", [enrollment.to_dict() for enrollment in enrollments])

# Return specific enrollment.
@rostering.route('/enrollments/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getEnrollment(id) -> dict:
    enrollment = Enrollment.get_by_sourced_id(id)
    if not enrollment:
        return {"error": "Not found"}, 404
    return {"enrollment": enrollment.to_dict()}

# Return collection of Orgs.
@rostering.route('/orgs', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllOrgs() -> dict:
    orgs = Org.query.all()
    return collection_response("orgs", [org.to_dict() for org in orgs])

# Return Specific Org.
@rostering.route('/orgs/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getOrg(id) -> dict:
    org = Org.get_by_sourced_id(id)
    if not org:
        return {"error": "Not found"}, 404
    return {"org": org.to_dict()}

# Return collection of students. A Student is an instance of a User.
@rostering.route('/students', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllStudents() -> dict:
    students = User.query.filter_by(role="student").all()
    return collection_response("students", [student.to_dict() for student in students])

# Return specific student. A Student is an instance of a User.
@rostering.route('/students/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getStudent(id) -> dict:
    student = User.query.filter_by(sourcedId=id, role="student").first()
    if not student:
        return {"error": "Not found"}, 404
    return {"student": student.to_dict()}

# Return collection of teachers. A Teacher is an instance of a User.
@rostering.route('/teachers', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllTeachers() -> dict:
    teachers = User.query.filter_by(role="teacher").all()
    return collection_response("teachers", [teacher.to_dict() for teacher in teachers])

# Return specific teacher.
@rostering.route('/teachers/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getTeacher(id) -> dict:
    teacher = User.query.filter_by(sourcedId=id, role="teacher").first()
    if not teacher:
        return {"error": "Not found"}, 404
    return {"teacher": teacher.to_dict()}

# Return collection of terms. A Term is an instance of an AcademicSession.
@rostering.route('/terms', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getAllTerms() -> dict:
    terms = AcademicSession.query.filter_by(type="term").all()
    return collection_response("terms", [term.to_dict() for term in terms])

# Return specific term.
@rostering.route('/terms/<id>', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getTerm(id) -> dict:
    term = AcademicSession.get_by_sourced_id(id)
    if not term or term.type != "term":
        return {"error": "Not found"}, 404
    return {"term": term.to_dict()}

# Return collection of users
@rostering.route('/users', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllUsers() -> dict:
    users = User.query.all()
    return collection_response("users", [user.to_dict() for user in users])

# Return specific user
@rostering.route('/users/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getUser(id) -> dict:
    user = User.get_by_sourced_id(id)
    if not user:
        return {"error": "Not found"}, 404
    return {"user": user.to_dict()}

# Return collection of schools. A School is an instance of an Org.
@rostering.route('/schools', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getAllSchools() -> dict:
    schools = Org.query.filter_by(type="school").all()
    return collection_response("schools", [school.to_dict() for school in schools])

# Return specific school. A School is an instance of an Org.
@rostering.route('/schools/<id>', methods=['GET'])
@bearer_token_required(ROSTER_CORE_READONLY_SCOPE)
def getSchool(id) -> dict:
    school = Org.get_by_sourced_id(id)
    if not school or school.type != "school":
        return {"error": "Not found"}, 404
    return {"school": school.to_dict()}

# Return the collection of courses taught by this school.
@rostering.route('/schools/<id>/courses', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getCoursesForSchool(id) -> dict:
    school = Org.get_by_sourced_id(id)
    if not school:
        return {"error": "Not found"}, 404
    courses = Course.query.filter_by(orgSourcedId=id).all()
    return collection_response("courses", [course.to_dict() for course in courses])

# Return the collection of all enrollments into this class.
@rostering.route('/schools/<school_id>/classes/<class_id>/enrollments', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getEnrollmentsForClassInSchool(school_id, class_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Class not found"}, 404
    enrollments = Enrollment.query.filter_by(classSourcedId=class_id).all()
    return collection_response("enrollments", [enrollment.to_dict() for enrollment in enrollments])

# Return the collection of students taking this class in this school.
@rostering.route('/schools/<school_id>/classes/<class_id>/students', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getStudentsForClassInSchool(school_id, class_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Class not found"}, 404
    enrollments = Enrollment.query.filter_by(
        classSourcedId=class_id,
        schoolSourcedId=school_id,
        role="student",
    ).all()
    student_ids = [enrollment.userSourcedId for enrollment in enrollments]
    students = User.query.filter(
        User.sourcedId.in_(student_ids),
        User.role == "student",
    ).all()
    return collection_response("students", [student.to_dict() for student in students])

# Return the collection of teachers taking this class in this school.
@rostering.route('/schools/<school_id>/classes/<class_id>/teachers', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getTeachersForClassInSchool(school_id, class_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Class not found"}, 404
    enrollments = Enrollment.query.filter_by(classSourcedId=class_id, schoolSourcedId=school_id, role="teacher").all()
    teacher_ids = [enrollment.userSourcedId for enrollment in enrollments]
    teachers = User.query.filter(User.sourcedId.in_(teacher_ids)).all()
    return collection_response("teachers", [{**teacher.to_dict(), "role": "teacher"} for teacher in teachers])

# Return the collection of all enrollments for this school.
@rostering.route('/schools/<school_id>/enrollments', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getEnrollmentsForSchool(school_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    enrollments = Enrollment.query.filter_by(schoolSourcedId=school_id).all()
    return collection_response("enrollments", [enrollment.to_dict() for enrollment in enrollments])

# Return the collection of students attending this school.
@rostering.route('/schools/<school_id>/students', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getStudentsForSchool(school_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    enrollments = Enrollment.query.filter_by(schoolSourcedId=school_id, role="student").all()
    student_ids = [enrollment.userSourcedId for enrollment in enrollments]
    students = User.query.filter(
        User.sourcedId.in_(student_ids),
        User.role == "student",
    ).all()
    return collection_response("students", [student.to_dict() for student in students])

# Return the collection of teachers teaching at this school.
@rostering.route('/schools/<school_id>/teachers', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getTeachersForSchool(school_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    enrollments = Enrollment.query.filter_by(schoolSourcedId=school_id, role="teacher").all()
    teacher_ids = [enrollment.userSourcedId for enrollment in enrollments]
    teachers = User.query.filter(User.sourcedId.in_(teacher_ids)).all()
    return collection_response("teachers", [{**teacher.to_dict(), "role": "teacher"} for teacher in teachers])

# Return the collection of terms that are used by this school.
@rostering.route('/schools/<school_id>/terms', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getTermsForSchool(school_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    school_classes = Class.query.filter_by(schoolSourcedId=school_id).all()
    term_ids = {
        term_id
        for cls in school_classes
        for term_id in (cls.termSourcedIds or [])
    }
    terms = AcademicSession.query.filter(
        AcademicSession.sourcedId.in_(term_ids),
        AcademicSession.type == "term",
    ).all()
    return collection_response("terms", [term.to_dict() for term in terms])

# Return the collection of classes that are taught in this term.
@rostering.route('/terms/<term_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForTerm(term_id) -> dict:
    term = AcademicSession.get_by_sourced_id(term_id)
    if not term:
        return {"error": "Term not found"}, 404
    classes = [cls for cls in Class.query.all() if term_id in (cls.termSourcedIds or [])]
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of Grading Periods that are part of this term.
@rostering.route('/terms/<term_id>/gradingPeriods', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getGradingPeriodsForTerm(term_id) -> dict:
    term = AcademicSession.get_by_sourced_id(term_id)
    if not term:
        return {"error": "Term not found"}, 404
    grading_periods = AcademicSession.query.filter_by(parentSourcedId=term_id, type="gradingPeriod").all()
    return collection_response("gradingPeriods", [period.to_dict() for period in grading_periods])

# Return the collection of classes that are teaching this course.
@rostering.route('/courses/<course_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForCourse(course_id) -> dict:
    course = Course.get_by_sourced_id(course_id)
    if not course:
        return {"error": "Course not found"}, 404
    classes = Class.query.filter_by(courseSourcedId=course_id).all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of classes that this student is taking.
@rostering.route('/students/<student_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForStudent(student_id) -> dict:
    student = User.query.filter_by(sourcedId=student_id, role="student").first()
    if not student:
        return {"error": "Student not found"}, 404
    enrollments = Enrollment.query.filter_by(userSourcedId=student_id, role="student").all()
    class_ids = [enrollment.classSourcedId for enrollment in enrollments]
    classes = Class.query.filter(Class.sourcedId.in_(class_ids)).all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of classes that this teacher is teaching.
@rostering.route('/teachers/<teacher_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForTeacher(teacher_id) -> dict:
    teacher = User.query.filter_by(sourcedId=teacher_id, role="teacher").first()
    if not teacher:
        return {"error": "Teacher not found"}, 404
    enrollments = Enrollment.query.filter_by(userSourcedId=teacher_id, role="teacher").all()
    class_ids = [enrollment.classSourcedId for enrollment in enrollments]
    classes = Class.query.filter(Class.sourcedId.in_(class_ids)).all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of classes taught by this school.
@rostering.route('/schools/<school_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForSchool(school_id) -> dict:
    school = Org.get_by_sourced_id(school_id)
    if not school:
        return {"error": "School not found"}, 404
    classes = Class.query.filter_by(schoolSourcedId=school_id).all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of classes attended by this user.
@rostering.route('/users/<user_id>/classes', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getClassesForUser(user_id) -> dict:
    user = User.get_by_sourced_id(user_id)
    if not user:
        return {"error": "User not found"}, 404
    enrollments = Enrollment.query.filter_by(userSourcedId=user_id).all()
    class_ids = [enrollment.classSourcedId for enrollment in enrollments]
    classes = Class.query.filter(Class.sourcedId.in_(class_ids)).all()
    return collection_response("classes", [cls.to_dict() for cls in classes])

# Return the collection of students that are taking this class.
@rostering.route('/classes/<class_id>/students', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getStudentsForClass(class_id) -> dict:
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Class not found"}, 404
    enrollments = Enrollment.query.filter_by(classSourcedId=class_id, role="student").all()
    student_ids = [enrollment.userSourcedId for enrollment in enrollments]
    students = User.query.filter(
        User.sourcedId.in_(student_ids),
        User.role == "student",
    ).all()
    return collection_response("students", [student.to_dict() for student in students])

# Return the collection of teachers that are teaching this class.
@rostering.route('/classes/<class_id>/teachers', methods=['GET'])
@bearer_token_required(ROSTER_READONLY_SCOPE)
def getTeachersForClass(class_id) -> dict:
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Class not found"}, 404
    enrollments = Enrollment.query.filter_by(classSourcedId=class_id, role="teacher").all()
    teacher_ids = [enrollment.userSourcedId for enrollment in enrollments]
    teachers = User.query.filter(User.sourcedId.in_(teacher_ids)).all()
    return collection_response("teachers", [{**teacher.to_dict(), "role": "teacher"} for teacher in teachers])
