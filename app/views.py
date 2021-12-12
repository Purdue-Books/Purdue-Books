from flask import Blueprint, render_template, request, redirect, url_for
from flask.scaffold import F
from flask.wrappers import Response
from .models import Course, Professor, User, Student, Author, School_Administrator, Book, Author_Book, Professor_Book, Book_Professor_Course, Image, Assigned_Professor_Course, Student_Course, Rating
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
prep_cursor = db_connection.cursor(prepared=True)
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


def get_books_by_author(author_id):
    get_book_by_author_sql = "SELECT * FROM book b, author__book ab WHERE %s = ab.author_id AND ab.book_id = b.book_id;"
    prep_cursor.execute(get_book_by_author_sql, (author_id, ))
    books = []
    for book in prep_cursor.fetchall():
        result = get_book_by_id(book[0])
        books.append({"book_id": book[0], "title": book[1], "published_year": book[2],
                     "summary": book[3], "genre": book[4], "image": result[0].get('image'), "author_id": book[6]})
    return books

def get_author_by_id(author_id): 
    get_author_by_id_sql = "SELECT * FROM author a WHERE a.author_id = %s;"
    prep_cursor.execute(get_author_by_id_sql, (author_id, ))
    authors = []
    for author in prep_cursor.fetchall():
        authors.append({"author_id": author[0], "first_name": author[1], "last_name": author[2],
                     "biography": author[3], "email": author[4]})
    return authors    


def get_author_by_book_id(book_id):
    get_author_by_book_id_sql = "SELECT * FROM author__book ab WHERE %s = ab.book_id;"
    prep_cursor.execute(get_author_by_book_id_sql, (book_id, ))
    author_books = []
    for author_book in prep_cursor.fetchall():
        author = get_author_by_id(author_book[0])
        book = get_book_by_id(author_book[1])
        #image = Image.query.filter_by(image_id=book[5]).first()
        author_books.append({"author_id": author_book[0], "book_id": author_book[1], "book_title": book[0]['title'],
                     "author_name": author[0]['first_name'] + author[0]['last_name'], "image": book[0]['image']})
    return author_books

def get_book_by_id(book_id):
    get_book_by_id_sql = "SELECT * FROM book b WHERE b.book_id = %s";
    prep_cursor.execute(get_book_by_id_sql, (book_id, ))
    books = []
    for book in prep_cursor.fetchall():
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
    get_course_by_id_sql = "SELECT * FROM course c WHERE c.course_id = %s;"
    prep_cursor.execute(get_course_by_id_sql, (course_id, ))
    courses = []
    for course in prep_cursor.fetchall():
        courses.append({"course_id": course[0], "name": course[1], "summary": course[2],
                     "subject": course[3], "semester": course[4], "year": course[5]})
    return courses

def get_professor_by_course_id(course_id):
    get_professor_by_course_id_sql = "SELECT * FROM professor p, assigned__professor__course apc WHERE %s = apc.course_id AND apc.prof_id = p.prof_id;"
    prep_cursor.execute(get_professor_by_course_id_sql, (course_id, ))
    professors = []
    for prof in prep_cursor.fetchall():
        professors.append({"prof_id": prof[0], "first_name": prof[2], "last_name": prof[3], "biography": prof[4], "email": prof[5]})
    return professors

def get_courses():
    get_courses = "SELECT * FROM course c;"
    db_cursor.execute(get_courses)
    courses = []
    for course in db_cursor.fetchall():
        courses.append({"course_id": course[0], "name": course[1], "summary": course[2],
                     "subject": course[3], "semester": course[4], "year": course[5]})
    return courses

def get_professor_by_id(prof_id):
    get_professor_by_id_sql = "SELECT * FROM professor p WHERE p.prof_id = %s;"
    prep_cursor.execute(get_professor_by_id_sql, (prof_id, ))
    professors = []
    for professor in prep_cursor.fetchall():
        image = Image.query.filter_by(image_id=professor[1]).first()
        professors.append({"prof_id": professor[0], "first_name": professor[2],
                     "last_name": professor[3], "biography": professor[4], "email": professor[5], "image": image})
    return professors

def get_professors():
    get_professors = "SELECT * FROM professor p;"
    db_cursor.execute(get_professors)
    professors = []
    for professor in db_cursor.fetchall():
        image = Image.query.filter_by(image_id=professor[1]).first()
        professors.append({"prof_id": professor[0], "image": image, "first_name": professor[2],
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
    assigned_professor_course = "SELECT * FROM assigned__professor__course a WHERE a.course_id = %s;"
    prep_cursor.execute(assigned_professor_course, (course_id, ))
    professors_courses = []
    for professor_course in prep_cursor.fetchall():
        professors_courses.append({"sch_id": professor_course[0], "prof_id": professor_course[1],
                     "course_id": professor_course[2]})
    return professors_courses

def get_book_professor_course(course_id, prof_id):
    book_professor_course = "SELECT * FROM book__professor__course b WHERE b.course_id = %s AND b.prof_id = %s;"
    prep_cursor.execute(book_professor_course, (course_id, prof_id))
    book_professor_courses = []
    for book_professor_course in prep_cursor.fetchall():
        book_professor_courses.append({"prof_id": book_professor_course[0], "course_id": book_professor_course[1],
                     "book_id": book_professor_course[2]})
    return book_professor_courses

def get_administrator_by_id(sch_id):
    get_administrator_by_id_sql = "SELECT * FROM school__administrator sa WHERE sa.sch_id = %s;"
    prep_cursor.execute(get_administrator_by_id_sql, (sch_id, ))
    administrators = []
    for admin in prep_cursor.fetchall():
        administrators.append({"sch_id": admin[0], "first_name": admin[1], "last_name": admin[2], "email": admin[3]})
    return administrators

def get_author_by_id(author_id):
    get_author_by_id_sql = "SELECT * FROM author a WHERE a.author_id = %s;"
    prep_cursor.execute(get_author_by_id_sql, (author_id, ))
    authors = []
    for author in prep_cursor.fetchall():
        image = Image.query.filter_by(image_id=author[5]).first()
        authors.append({"author_id": author[0], "first_name": author[1], "last_name": author[2], "email": author[3], "biography": author[4], "image": image})
    return authors

def get_course_by_student_id(stud_id):
    get_course_by_student_id_sql = "SELECT course_id FROM student__course sc WHERE sc.stud_id =  %s;"
    prep_cursor.execute(get_course_by_student_id_sql, (stud_id, ))
    courses = []
    for course in prep_cursor.fetchall():
        courses.append({"course_id": course[0]})
    return courses

def get_values_course_student(stud_id, course_id):
    get_values_course_student = "SELECT stud_id, course_id AS count FROM student__course sc WHERE sc.stud_id = %s AND sc.course_id = %s;"
    prep_cursor.execute(get_values_course_student, (stud_id, course_id))
    checker = []
    for check in prep_cursor.fetchall():
        checker.append({"stud_id": check[0], "course_id": check[1]})
    return checker

def get_check_course_student(stud_id, course_id):
    get_check_course_student_sql = "SELECT COUNT(*) AS count FROM student__course sc WHERE sc.stud_id = %s AND sc.course_id = %s;"
    prep_cursor.execute(get_check_course_student_sql, (stud_id, course_id))
    checker = []
    for check in prep_cursor.fetchall():
        checker.append({"count": check[0]})
    return checker

def get_course_by_genre(genre):
    get_course_id_and_prof_id_by_genre_sql = "(SELECT course_id, prof_id FROM book bk INNER JOIN book__professor__course bpc ON bk.book_id = bpc.book_id WHERE bk.genre = %s)"
    get_course_info = "(SELECT c.course_id, t1.prof_id, c.name, c.semester, c.year FROM course c INNER JOIN" + get_course_id_and_prof_id_by_genre_sql + "t1 ON c.course_id = t1.course_id)"
    get_prof_course_info = "(SELECT t2.course_id, p.prof_id, p.first_name, p.last_name FROM professor p INNER JOIN" + get_course_id_and_prof_id_by_genre_sql + "t2 ON p.prof_id = t2.prof_id)"
    get_combo_prof_course_info = "SELECT pci.first_name, pci.last_name, gci.name, gci.semester, gci.year, gci.course_id FROM " + get_course_info + "gci INNER JOIN " + get_prof_course_info + " pci ON gci.course_id = pci.course_id;"

    prep_cursor.execute(get_combo_prof_course_info, (genre, genre))
    checker = []
    for check in prep_cursor.fetchall():
        checker.append({"first_name": check[0], "last_name": check[1], "course_name": check[2], "course_semester": check[3], "course_year": check[4], "course_id": check[5]})
    return checker

def get_professor_by_genre_and_semester(genre, semester):
    if genre != '' and semester == '':
        get_course_by_genre = "(SELECT bpc.course_id, bpc.prof_id FROM book bk INNER JOIN book__professor__course bpc ON bk.book_id = bpc.book_id WHERE bk.genre = %s)"
        get_course_info = "(SELECT cbg.prof_id FROM course c INNER JOIN" + get_course_by_genre + "cbg ON c.course_id = cbg.course_id)"
        get_prof_course_info = "SELECT p.image, p.first_name, p.last_name FROM professor p INNER JOIN" + get_course_info + "t2 ON p.prof_id = t2.prof_id;"
        prep_cursor.execute(get_prof_course_info, (genre, ))
        
    elif genre == '' and semester != '':
        get_course_by_genre = "(SELECT bpc.course_id, bpc.prof_id FROM book bk INNER JOIN book__professor__course bpc ON bk.book_id = bpc.book_id)"
        get_course_info = "(SELECT cbg.prof_id FROM course c INNER JOIN" + get_course_by_genre + "cbg ON c.course_id = cbg.course_id WHERE c.semester = %s)"
        get_prof_course_info = "SELECT p.image, p.first_name, p.last_name FROM professor p INNER JOIN" + get_course_info + "t2 ON p.prof_id = t2.prof_id;"
        prep_cursor.execute(get_prof_course_info, (semester, ))
        
    else:
        get_course_by_genre = "(SELECT bpc.course_id, bpc.prof_id FROM book bk INNER JOIN book__professor__course bpc ON bk.book_id = bpc.book_id WHERE bk.genre = %s)"
        get_course_info = "(SELECT cbg.prof_id FROM course c INNER JOIN" + get_course_by_genre + "cbg ON c.course_id = cbg.course_id WHERE c.semester = %s)"
        get_prof_course_info = "SELECT p.image, p.first_name, p.last_name FROM professor p INNER JOIN" + get_course_info + "t2 ON p.prof_id = t2.prof_id;"
        prep_cursor.execute(get_prof_course_info, (genre, semester))

    # db_cursor.execute(get_prof_course_info)
    checker = []
    for check in prep_cursor.fetchall():
        image = Image.query.filter_by(image_id=check[0]).first()
        checker.append({"image": image, "first_name": check[1], "last_name": check[2]})
    return checker



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
        new_course = Course(course_id=course_id, name=name, summary=summary, subject=subject, semester=semester, year=year)
        database.session.add(new_course)
        database.session.commit()
        prof_course = Assigned_Professor_Course(prof_id = professor, sch_id = current_user.get_id(), course_id=course_id)
        database.session.add(prof_course)
        database.session.commit()
        professors_courses = get_assigned_professor_course()
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
    return render_template('/administratorCourseCreation.html', Data=professors)

@views.route('/administratorBooks.html/', methods=['POST', 'GET'])
def administrator_books():
    author_books_info = []
    books = get_books()
    for book in books:
        author_book = get_author_by_book_id(book['book_id'])
        author_books_info.append({"author_books_info": author_book})
    return render_template('administratorBooks.html', Author_book_info=author_books_info)

@views.route('/administratorCourse.html/<string:id>', methods=['POST', 'GET'])
def administrator_course(id):
    professors_courses = get_assigned_professor_course_by_course_id(id)
    professors_courses_info = []
    author_books_info = []
    books = get_book_professor_course(id, professors_courses[0]['prof_id'])
    for book in books:
        author_book = get_author_by_book_id(book['book_id'])
        author_books_info.append({"author_books_info": author_book})
    for professor_course in professors_courses:
        professor = get_professor_by_id(prof_id=professor_course['prof_id'])
        course = get_course_by_id(course_id=professor_course['course_id'])
        professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], "image": professor[0]['image'],
         "course_id": course[0]['course_id'], "course_name": course[0]['name'], "course_summary": course[0]['summary'], 
         "course_semester": course[0]['semester'], "course_year": course[0]['year']}) 
    return render_template('/administratorCourse.html', Data=professors_courses_info, Author_book_info=author_books_info)

@views.route('/administratorBookProfile.html/<string:id>', methods=['POST', 'GET'])
def administrator_book_profile(id):
    result = get_book_by_id(book_id=id)
    return render_template('/administratorBookProfile.html', Data=result)

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
    result = get_book_by_id(id)
    Image.query.filter_by(image_id=result[0].get('image').image_id).delete()
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
        return administrator_course(id)
    result = get_course_by_id(id)
    professors = get_professors()
    selected_prof = get_professor_by_course_id(id)
    return render_template('/administratorCourseEdit.html', Course=result[0], Professor=professors, Selected_prof=selected_prof[0])

@views.route('/deleteCourse/<string:id>', methods=['POST', 'GET'])
@login_required
def delete_course(id):
    Assigned_Professor_Course.query.filter_by(course_id=id).delete()
    Book_Professor_Course.query.filter_by(course_id=id).delete()
    Student_Course.query.filter_by(course_id=id).delete()
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


@views.route('/studentHome.html/', methods=['POST', 'GET'])
@login_required
def student_home():
    genre = ''
    if request.method == 'POST':
        genre = request.form.get("genre")

    if genre == '' and len(genre) == 0:
        results = get_courses()
        professors_courses_info = []
        for result in results:
            professors_courses = get_assigned_professor_course_by_course_id(result['course_id'])
            for professor_course in professors_courses:
                professor = get_professor_by_id(prof_id=professor_course['prof_id'])
                course = get_course_by_id(course_id=professor_course['course_id'])
                professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], "course_name": course[0]['name'], "course_semester": course[0]['semester'], "course_year": course[0]['year'], "course_id": course[0]['course_id']})
    else:
        results = get_course_by_genre(genre)
        professors_courses_info = []
        for result in results:     
            professors_courses_info.append({"prof_name": result['first_name'] + " " + result['last_name'], "course_name": result['course_name'], "course_semester": result['course_semester'], "course_year": result['course_year'], "course_id": result['course_id']})
   
        
    return render_template('studentHome.html', Data=professors_courses_info)


@views.route('/studentBookmarks.html/')
@login_required
def student_bookmarks():
    courses = get_course_by_student_id(current_user.get_id())
    professors_courses_info = []
    for course in courses:
        course_info = get_course_by_id(course['course_id'])
        prof_info = get_professor_by_course_id(course['course_id'])
        professors_courses_info.append({"prof_name": prof_info[0]['first_name'] + " " + prof_info[0]['last_name'], "course_name": course_info[0]['name'], "course_semester": course_info[0]['semester'], "course_year": course_info[0]['year'], "course_id": course_info[0]['course_id']})
    return render_template('studentBookmarks.html', Data=professors_courses_info)

@views.route('/studentBookProfile.html/<string:id>', methods=['POST', 'GET'])
@login_required
def student_book_profile(id):
    bookResult = get_book_by_id(book_id=id)
    authorId = get_author_by_book_id(book_id=id)
    authorResult = get_author_by_id(authorId[0]['author_id'])
    test = ''
    '''
    if request.method == 'GET':
        amount = request.form.get("rating")
        test = type(int(amount))
        rates = Rating(stud_id = current_user.get_id(), book_id = id, rating = amount)
        database.session.add(rates)
        database.session.commit()
    '''
    return render_template('studentBookProfile.html', Book=bookResult, Author=authorResult, rating = test)

@views.route('/studentClassesPage.html/<string:id>', methods=['GET', 'POST'])
@login_required
def student_classes_page(id):
    professors_courses = get_assigned_professor_course_by_course_id(id)
    professors_courses_info = []
    for professor_course in professors_courses:
        professor = get_professor_by_id(prof_id=professor_course['prof_id'])
        course = get_course_by_id(course_id=professor_course['course_id'])

        professors_courses_info.append({"prof_name": professor[0]['first_name'] + " " + professor[0]['last_name'], "image": professor[0]['image'], "prof_biography": professor[0]['biography'], "prof_email": professor[0]['email'],"course_id": course[0]['course_id'], "course_name": course[0]['name'], "course_summary": course[0]['summary'], "course_semester": course[0]['semester'], "course_year": course[0]['year'], "course_subject": course[0]['subject']})
        bookList_info = []
        bookList = get_book_professor_course(professor_course['course_id'], professor_course['prof_id'])
        for book in bookList:
            bookInfo = get_book_by_id(book['book_id'])
            authorInfo = get_author_by_book_id(book['book_id'])
            bookList_info.append({"book_id": bookInfo[0]['book_id'], "book_title": bookInfo[0]['title'], "author_name": authorInfo[0]['author_name'], "image": bookInfo[0]['image']})

    checker = get_check_course_student(current_user.get_id(), id)

    if request.method == 'POST':
        formResult = request.form.get('submit')
        if formResult == 'accept':
            new_student_course = Student_Course(stud_id = current_user.get_id(), course_id = id)
            database.session.add(new_student_course)
            database.session.commit()
            return redirect(url_for('views.student_bookmarks'))
        elif formResult == 'reject':
            Student_Course.query.filter_by(stud_id = current_user.get_id(), course_id = id).delete()
            database.session.commit()
            database.session.flush()
            return redirect(url_for('views.student_bookmarks'))
            
    return render_template('studentClassesPage.html', Prof=professors_courses_info, Book=bookList_info, check = checker[0])

@views.route('/studentProfessors.html/', methods=['POST', 'GET'])
@login_required
def student_professors():
    result = get_professors()
    if request.method == 'POST':
        genre = request.form.get("genre")
        semester = request.form.get("semester")
        if genre != '' or semester != '':
            result = get_professor_by_genre_and_semester(genre, semester)
        
    return render_template('studentProfessors.html', Data=result)


@views.route('/studentProfessorProfile.html/<string:id>')
@login_required
def student_professors_profile(id):
    result = get_professor_by_id(id)
    return render_template('studentProfessorProfile.html', Data=result)


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
    result = get_administrator_by_id(current_user.get_id())
    if len(result) == 0:
        result.append({"sch_id": "", "first_name": "", "last_name": "", "email": ""})
    return render_template('administratorProfile.html', Administrator=result[0])


@views.route('/authorProfile.html', methods=['GET', 'POST'])
@login_required
def author_profile():
    none = 1
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
        image = Image(image_id=image_id, image=base64.b64encode(file.read()), mimetype=mimetype, name=filename)
        database.session.add(image)
        database.session.commit()

        return redirect(url_for('views.author_home'))
    result = get_author_by_id(current_user.get_id())
    if len(result) == 0:
        result.append({"author_id": "", "first_name": "", "last_name": "", "email": "", "biography": "", "image": ""})
        none = 0
    return render_template('authorProfile.html', Author=result[0], test = none)


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
        image = Image(image_id=image_id, image=base64.b64encode(file.read()), mimetype=mimetype, name=filename)
        database.session.add(image)
        database.session.commit()

        return redirect(url_for('views.professor_home'))
    result = get_professor_by_id(current_user.get_id())
    if len(result) == 0:
        result.append({"prof_id": "", "first_name": "", "last_name": "", "biography": "", "email": ""})
    return render_template('professorProfile.html', Professor=result[0])


@views.route('/studentProfile.html/', methods=['GET', 'POST'])
@login_required
def student_profile():
    none = 0
    result = get_student_by_id(current_user.get_id())
    if request.method == 'POST' and len(result) == 0:
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
    if len(result) == 0:
        return render_template('studentProfile.html', studentData = '', test = none)
    if request.method == 'POST' and len(result) == 1:
        stud_id = current_user.get_id()
        firstname = request.form.get("firstname")
        lastname = request.form.get('lastname')
        major = request.form.get('major')
        email = request.form.get('email')
        gradeyear = request.form.get('gradeyear')
        student = Student.query.filter_by(stud_id=result[0].get('stud_id')).first()
        student.first_name = firstname
        student.last_name = lastname
        student.major = major
        student.email = email
        student.grade_year = gradeyear
        database.session.commit() 
        database.session.flush()
        return redirect(url_for('views.student_home'))
    
    none = 1
    return render_template('studentProfile.html', studentData = result[0], test = none)

def get_student_by_id(student_id):
    get_student_by_id_sql = "SELECT * FROM student b WHERE b.stud_id = \"" + student_id + "\";"
    db_cursor.execute(get_student_by_id_sql)
    students = []
    for student in db_cursor.fetchall():
        students.append({"stud_id": student[0], "first_name": student[1], "last_name": student[2],
                     "major": student[3], "email": student[4], "grade_year": student[5]})
    return students


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
