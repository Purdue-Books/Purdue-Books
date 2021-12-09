from flask import Blueprint, render_template, request, redirect, url_for
from flask.wrappers import Response
from .models import Course, Professor, User, Student, Author, School_Administrator, Book, Author_Book, Professor_Book, Book_Professor_Course, Book_Course, Image, Assigned_Professor_Course, Student_Course, Book_Course
from . import database
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
import mysql.connector as connector
from . import db
import uuid
import base64

db_connection = None
db_cursor = None

try:
    db_connection = connector.connect(user=db.user,
                                      password=db.password,
                                      host=db.host,
                                      database=db.name)
except connector.Error as err:
    print("ERROR")

db_cursor = db_connection.cursor(buffered=True)
db_cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
db_cursor.execute("USE Purdue_Books")


def book_table(data):
    if data == None:
        return ""
    table = "<table border = '1'>"
    table = table + "<tr><th>Name</th><th>Url</th><th>Image</th><th>Athor</th><th>Author Info</th><th>Book ID</th><th>Summary</th></tr>"
    for i in range(len(data)):
        table = table + "<tr>\n"
        table = table + "<td>" + str(data[i][0]) + "</td>"
        table = table + "<td>" + str(data[i][1]) + "</td>"
        table = table + "<td>" + "<img src ='" + \
            str(data[i][2]) + "' width=60 height=40>" + "</td>"
        table = table + "<td>" + str(data[i][3]) + "</td>"
        table = table + "<td>" + str(data[i][4]) + "</td>"
        table = table + "<td>" + str(data[i][5]) + "</td>"
        table = table + "<td>" + str(data[i][6]) + "</td>"
        table = table + "</tr>\n"
    table = table + "</table>"
    return table


def get_book(name):
    get_book_name_sql = "SELECT * FROM mytable WHERE name LIKE "
    get_book_sql = get_book_name_sql + "'%" + name + "%' "
    get_book_sql = get_book_sql + "OR author LIKE " + "'%" + name + "%' "
    get_book_sql = get_book_sql + "OR book_id LIKE " + "'%" + name + "%' "
    db_cursor.execute(get_book_sql)
    books = []
    for book in db_cursor.fetchall():
        books.append(
            {"name": book[0], "url": book[1], "image": book[2], "author": book[3],
             "author_url": book[4], "book_id": book[5], "summary": str(book[6])[0:50]})
    return books

def get_course(name):
    get_course_name_sql = "SELECT * FROM course WHERE name LIKE "
    get_course_sql = get_course_name_sql + "'%" + name + "%' "
    get_course_sql = get_course_sql + "OR subject LIKE " + "'%" + name + "%' "
    get_course_sql = get_course_sql + "OR course_id LIKE " + "'%" + name + "%' "
    db_cursor.execute(get_course_sql)
    courses = []
    ##for course in db_cursor.fetchall():
       ## courses.append(
          ##  {"name": course[0], "url": course[1], "image": course[2], "author": course[3],
           ##  "author_url": course[4], "book_id": course[5], "summary": str(course[6])[0:50]})
    return courses

def get_books_by_author(author_id):
    get_book_by_author_sql = "SELECT * FROM book b, author__book ab WHERE \"" + \
        author_id + "\" = ab.author_id AND ab.book_id = b.book_id;"
    db_cursor.execute(get_book_by_author_sql)
    books = []
    for book in db_cursor.fetchall():
        result = get_book_by_id(book[0])
        books.append({"book_id": book[0], "title": book[1], "published_year": book[2],
                     "summary": book[3], "genre": book[4], "image": result[0].get('image'), "author_id": book[6]})
    return books

def get_author_by_id(author_id): 
    get_author_by_id_sql = "SELECT * FROM author a WHERE a.author_id = \"" + author_id + "\";"
    db_cursor.execute(get_author_by_id_sql)
    authors = []
    for author in db_cursor.fetchall():
        authors.append({"author_id": author[0], "first_name": author[1], "last_name": author[2],
                     "biography": author[3], "email": author[4]})
    return authors    


def get_author_by_book_id(book_id):
    get_author_by_book_id_sql = "SELECT * FROM author__book ab WHERE \"" + \
        book_id + "\" = ab.book_id;"
    db_cursor.execute(get_author_by_book_id_sql)
    author_books = []
    for author_book in db_cursor.fetchall():
        author = get_author_by_id(author_book[0])
        book = get_book_by_id(author_book[1])
        author_books.append({"author_id": author_book[0], "book_id": author_book[1], "book_title": book['title'],
                     "author_name": author['first_name'] + author['last_name'], "image": book[0].get('image')})
    return author_books

def get_book_by_id(book_id):
    get_book_by_id_sql = "SELECT * FROM book b WHERE b.book_id = \"" + book_id + "\";"
    db_cursor.execute(get_book_by_id_sql)
    books = []
    for book in db_cursor.fetchall():
        image = Image.query.filter_by(image_id=book[5]).first()
        books.append({"book_id": book[0], "title": book[1], "published_year": book[2],
                     "summary": book[3], "genre": book[4], "image": image})
    return books

def get_books():
    get_books = "SELECT * FROM book b;"
    db_cursor.execute(get_books)
    books = []
    for book in db_cursor.fetchall():
        image = Image.query.filter_by(image_id=book[5]).first()
        books.append({"book_id": book[0], "title": book[1], "published_year": book[2],
                     "summary": book[3], "genre": book[4], "image": image})
    return books

def get_course_by_id(course_id):
    get_course_by_id_sql = "SELECT * FROM course c WHERE c.course_id = \"" + course_id + "\";"
    db_cursor.execute(get_course_by_id_sql)
    courses = []
    for course in db_cursor.fetchall():
        courses.append({"course_id": course[0], "name": course[1], "summary": course[2],
                     "subject": course[3], "semester": course[4], "year": course[5]})
    return courses

def get_courses():
    get_courses = "SELECT * FROM course c;"
    db_cursor.execute(get_courses)
    courses = []
    for course in db_cursor.fetchall():
        courses.append({"course_id": course[0], "name": course[1], "summary": course[2],
                     "subject": course[3], "semester": course[4], "year": course[5]})
    return courses

def get_professor_by_id(prof_id):
    get_professor_by_id_sql = "SELECT * FROM professor p WHERE p.prof_id = \"" + prof_id + "\";"
    db_cursor.execute(get_professor_by_id_sql)
    professors = []
    for professor in db_cursor.fetchall():
        professors.append({"prof_id": professor[0], "first_name": professor[2],
                     "last_name": professor[3], "biography": professor[4], "professor": professor[5]})
    return professors

def get_professors():
    get_professors = "SELECT * FROM professor p;"
    db_cursor.execute(get_professors)
    professors = []
    for professor in db_cursor.fetchall():
        professors.append({"prof_id": professor[0], "first_name": professor[2],
                     "last_name": professor[3], "biography": professor[4], "email": professor[5]})
    return professors

def get_assigned_professor_course():
    assigned_professor_course = "SELECT * FROM assigned__professor__course a;"
    db_cursor.execute(assigned_professor_course)
    professors_courses = []
    for professor_course in db_cursor.fetchall():
        professors_courses.append({"sch_id": professor_course[0], "prof_id": professor_course[1],
                     "course_id": professor_course[2]})
    return professors_courses

def get_assigned_professor_course_by_course_id(course_id):
    assigned_professor_course = "SELECT * FROM assigned__professor__course a WHERE a.course_id = \"" + course_id + "\";"
    db_cursor.execute(assigned_professor_course)
    professors_courses = []
    for professor_course in db_cursor.fetchall():
        professors_courses.append({"sch_id": professor_course[0], "prof_id": professor_course[1],
                     "course_id": professor_course[2]})
    return professors_courses

def get_book_professor_course(course_id, prof_id):
    book_professor_course = "SELECT * FROM book__professor__course b WHERE b.course_id = \"" + course_id + "\" AND b.prof_id = \"" + prof_id + "\";"
    db_cursor.execute(book_professor_course)
    book_professor_courses = []
    for book_professor_course in db_cursor.fetchall():
        book_professor_courses.append({"prof_id": book_professor_course[0], "course_id": book_professor_course[1],
                     "book_id": book_professor_course[2]})
    return book_professor_courses

views = Blueprint('views', __name__)

@login_required
@views.route('/authorBookCreation.html', methods=['POST', 'GET'])
def create_book():
    if request.method == 'POST':
        book_id = uuid.uuid1()
        title = request.form.get("title")
        published_year = request.form.get("published_year")
        summary = request.form.get("summary")
        genre = request.form.get("genre")
        image_id = uuid.uuid1()
        new_book = Book(book_id=book_id, title=title, published_year=published_year,
                        summary=summary, genre=genre, image=image_id)
        author_book = Author_Book(
            author_id=current_user.get_id(), book_id=book_id)
        database.session.add(new_book)
        database.session.commit()
        database.session.add(author_book)
        database.session.commit()

        file = request.files["fileToUpload"]
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        image = Image(image_id=image_id, image=base64.b64encode(file.read()), mimetype=mimetype, name=filename)
        database.session.add(image)
        database.session.commit()

        result = get_books_by_author(author_id=current_user.get_id())
        return render_template('authorHome.html', Data=result)
    return render_template('authorBookCreation.html')

@views.route('/administratorCourseCreation.html', methods=['POST', 'GET'])
def create_course():
    if request.method == 'POST':
        course_id = uuid.uuid1()
        name = request.form.get("name")
        summary = request.form.get("summary")
        subject = request.form.get("subject")
        semester = request.form.get("semester")
        year = request.form.get("year")
        professor = request.form.get("professor")
        print("professor:"+ professor)
        new_course = Course(course_id=course_id, name=name, summary=summary, subject=subject, semester=semester, year=year)
        database.session.add(new_course)
        database.session.commit()
        prof_course = Assigned_Professor_Course(prof_id = professor, sch_id = current_user.get_id(), course_id=course_id)
        database.session.add(prof_course)
        database.session.commit()
        professors_courses = get_assigned_professor_course()
        print("professors_courses")
        print(*professors_courses)
        professors_courses_info = []
        for professor_course in professors_courses:
            professor = get_professor_by_id(prof_id=professor_course['prof_id'])
            course = get_course_by_id(course_id=professor_course['course_id'])
            books = get_book_professor_course(course[0]['course_id'], professor[0]['prof_id'])
            professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], 
            "course_name": course[0]['name'], "course_semester": course[0]['semester'], "course_year": course[0]['year'], 
            "course_id": course[0]['course_id'], "books": books})
        return render_template('/administratorHome.html', Data=professors_courses_info, Books=books)
        #return render_template('administratorHome.html')
    professors = get_professors();   
    return render_template('administratorCourseCreation.html', Data=professors)

@views.route('/administratorBooks.html/', methods=['POST', 'GET'])
def administrator_books():
    return render_template('administratorBooks.html')

@views.route('/administratorCourse.html/<string:id>', methods=['POST', 'GET'])
def administrator_course(id):
    professors_courses = get_assigned_professor_course_by_course_id(id)
    print("professors_courses")
    print(professors_courses)
    professors_courses_info = []
    author_books_info = []
    for professor_course in professors_courses:
        professor = get_professor_by_id(prof_id=professor_course['prof_id'])
        course = get_course_by_id(course_id=professor_course['course_id'])
        book = get_book_professor_course(course[0]['course_id'], professor[0]['prof_id'])
        author_book = get_author_by_book_id(book['book_id'])
        author_books_info.append({"author_book": author_book})
        professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], 
         "course_id": course[0]['course_id'], "course_name": course[0]['name'], "course_summary": course[0]['summary'], 
         "course_semester": course[0]['semester'], "course_year": course[0]['year']}) 
        professor = get_professor_by_id(prof_id=professor_course['prof_id'])
    return render_template('/administratorCourse.html', Data=professors_courses_info, Author_book_info = author_books_info)

@views.route('/administratorBookProfile.html', methods=['POST', 'GET'])
def administrator_book_profile():
    return render_template('administratorBookProfile.html')

@views.route('/professorBookProfile.html', methods=['POST', 'GET'])
def professor_book_profile():
    return render_template('professorBookProfile.html')

@views.route('/professorBooks.html', methods=['POST', 'GET'])
def professor_books():
    return render_template('professorBooks.html')

@views.route('/authorBookEdit.html/<string:id>', methods=['POST', 'GET'])
@login_required
def edit_book(id):
    if request.method == 'POST':
        result = get_book_by_id(id)
        title = request.form.get("title")
        published_year = request.form.get("published_year")
        summary = request.form.get("summary")
        genre = request.form.get("genre")
        book = Book.query.filter_by(book_id=result[0].get('book_id')).first()
        book.title = title
        book.published_year = published_year
        book.summary = summary
        book.genre = genre
        database.session.commit() 
        database.session.flush()
        return author_book_profile(id)
    result = get_book_by_id(id)
    return render_template('authorBookEdit.html', Book=result[0])


@views.route('/deleteBook/<string:id>', methods=['POST', 'GET'])
@login_required
def delete_book(id):
    Book_Course.query.filter_by(book_id=id).delete()
    Book_Professor_Course.query.filter_by(book_id=id).delete()
    Professor_Book.query.filter_by(book_id=id).delete()
    Author_Book.query.filter_by(book_id=id).delete()
    Book.query.filter_by(book_id=id).delete()
    database.session.commit()
    database.session.flush()
    return redirect(url_for('views.author_home'))

@views.route('/administratorCourseEdit.html/<string:id>', methods=['POST', 'GET'])
@login_required
def edit_course(id):
    if request.method == 'POST':
        result = get_course_by_id(id)
        name = request.form.get("name")
        summary = request.form.get("summary")
        subject = request.form.get("subject")
        semester = request.form.get("semester")
        year = request.form.get("year")
        selected_prof = request.form.get("professor")
        course = Course.query.filter_by(course_id=result[0].get('course_id')).first()
        course.name = name
        course.summary = summary
        course.subject = subject
        course.semester = semester
        course.year = year
        database.session.commit() 
        database.session.flush()
        prof_course = Assigned_Professor_Course.query.filter_by(course_id=result[0].get('course_id')).first()
        prof_course.sch_id = current_user.get_id()
        prof_course.prof_id = selected_prof
        prof_course.course_id = id
        database.session.commit() 
        database.session.flush()
        return redirect(url_for('views.admin_home'))
    result = get_course_by_id(id)
    professors = get_professors()
    prof_id = request.form.get("professor")
    selected_prof = get_professor_by_id(str(prof_id))
    return render_template('administratorCourseEdit.html', Course=result[0], Professor=professors, Selected_prof=selected_prof)

@views.route('/deleteCourse/<string:id>', methods=['POST', 'GET'])
@login_required
def delete_course(id):
    Assigned_Professor_Course.query.filter_by(course_id=id).delete()
    Book_Professor_Course.query.filter_by(course_id=id).delete()
    Student_Course.query.filter_by(course_id=id).delete()
    Book_Course.query.filter_by(course_id=id).delete()
    Course.query.filter_by(course_id=id).delete()
    database.session.commit()
    database.session.flush()
    return redirect(url_for('views.admin_home'))
    

@views.route('/result.html', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        res = request.form['re']
        result = get_book(res)
        print("result is : " + str(result))
        return render_template('results.html', Data=result)
    else:
        return render_template('search.html')


@views.route('/administratorHome.html')
@login_required
def admin_home():
    professors_courses = get_assigned_professor_course()
    professors_courses_info = []
    for professor_course in professors_courses:
        professor = get_professor_by_id(prof_id=professor_course['prof_id'])
        course = get_course_by_id(course_id=professor_course['course_id'])
        professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], 
        "course_name": course[0]['name'], "course_semester": course[0]['semester'], "course_year": course[0]['year'], "course_id": course[0]['course_id']})
    return render_template('/administratorHome.html', Data=professors_courses_info)


@views.route('/authorHome.html')
@login_required
def author_home():
    result = get_books_by_author(author_id=current_user.get_id())
    return render_template('authorHome.html', Data=result)

@views.route('/authorBookProfile.html/<string:id>')
@login_required
def author_book_profile(id):
    result = get_book_by_id(book_id=id)
    return render_template('/authorBookProfile.html', Data=result)

@views.route('/professorHome.html')
@login_required
def professor_home():
    return render_template('professorHome.html')


@views.route('/studentHome.html')
@login_required
def student_home():
    return render_template('studentHome.html')


@views.route('/studentBookmarks.html')
@login_required
def student_bookmarks():
    return render_template('studentBookmarks.html')


@views.route('/administratorProfile.html', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if request.method == 'POST':
        sch_id = current_user.get_id()
        firstname = request.form.get("firstname")
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        new_admin = School_Administrator(
            sch_id=sch_id, first_name=firstname, last_name=lastname, email=email)
        database.session.add(new_admin)
        database.session.commit()
        return redirect(url_for('views.admin_home'))

    return render_template('administratorProfile.html')


@views.route('/authorProfile.html', methods=['GET', 'POST'])
@login_required
def author_profile():
    if request.method == 'POST':
        prof_id = current_user.get_id()
        firstname = request.form.get("firstname")
        lastname = request.form.get('lastname')
        biography = request.form.get('biography')
        email = request.form.get('email')
        image_id = uuid.uuid1();

        new_auth = Author(author_id=prof_id, first_name=firstname,
                          last_name=lastname, biography=biography, email=email, image=image_id)
        database.session.add(new_auth)
        database.session.commit()

        file = request.files["fileToUpload"]
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        image = Image(image_id=image_id, image=file.read(), mimetype=mimetype, name=filename)
        database.session.add(image)
        database.session.commit()

        return redirect(url_for('views.author_home'))

    return render_template('authorProfile.html')


@views.route('/professorProfile.html', methods=['GET', 'POST'])
@login_required
def professor_profile():
    if request.method == 'POST':
        prof_id = current_user.get_id()
        firstname = request.form.get("firstname")
        lastname = request.form.get('lastname')
        biography = request.form.get('biography')
        email = request.form.get('email')
        image_id = uuid.uuid1();

        new_prof = Professor(prof_id=prof_id, first_name=firstname,
                             last_name=lastname, biography=biography, email=email, image=image_id)
        database.session.add(new_prof)
        database.session.commit()

        file = request.files['fileToUpload']
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        image = Image(image_id=image_id, image=file.read(), mimetype=mimetype, name=filename)
        database.session.add(image)
        database.session.commit()

        return redirect(url_for('views.professor_home'))

    return render_template('professorProfile.html')


@views.route('/studentProfile.html', methods=['GET', 'POST'])
@login_required
def student_profile():
    if request.method == 'POST':
        stud_id = current_user.get_id()
        firstname = request.form.get("firstname")
        lastname = request.form.get('lastname')
        major = request.form.get('major')
        email = request.form.get('email')
        gradeyear = request.form.get('gradeyear')

        new_stud = Student(stud_id=stud_id, first_name=firstname,
                           last_name=lastname, major=major, email=email, grade_year=gradeyear)
        database.session.add(new_stud)
        database.session.commit()
        return redirect(url_for('views.student_home'))

    return render_template('studentProfile.html')


@views.route('/', methods=['GET', 'POST'])
@views.route('/index.html', methods=['GET', 'POST'])
def login():
    logout_user()
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.pwd, pwd):
                print("SUCCESS")
                login_user(user, remember=True)
                if user.role == "student":
                    return redirect(url_for('views.student_home'))
                if user.role == "professor":
                    return redirect(url_for('views.professor_home'))
                if user.role == "author":
                    return redirect(url_for('views.author_home'))
                else:
                    return redirect(url_for('views.admin_home'))
            else:
                print("FAILED TO LOGIN")
        else:
            print("FAILURE")

    return render_template('index.html')


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))


@views.route('/signUp.html', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        role_type = request.form.get('role_type')

        user = User.query.filter_by(username=username).first()
        if user:
            print("USERNAME EXISTS")

        else:
            new_user = User(username=username, pwd=generate_password_hash(
                pwd, method='sha256'), role=role_type)
            database.session.add(new_user)
            database.session.commit()
            login_user(new_user, remember=True)
            if role_type == "student":
                return redirect(url_for('views.student_profile'))
            if role_type == "professor":
                return redirect(url_for('views.professor_profile'))
            if role_type == "author":
                return redirect(url_for('views.author_profile'))
            else:
                return redirect(url_for('views.admin_profile'))

    return render_template('signUp.html')
