from flask import Blueprint, render_template, request, redirect, url_for
from .models import Professor, User, Student, Author, School_Administrator, Book
from . import database
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import mysql.connector as connector
from . import db
import uuid

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


views = Blueprint('views', __name__)


@views.route('/authorBookCreation.html', methods=['POST', 'GET'])
def create_book():
    if request.method == 'POST':
        book_id = uuid.uuid1()
        title = request.form.get("title")
        published_year = request.form.get("published_year")
        summary = request.form.get("summary")
        genre = request.form.get("genre")
        image = request.form.get("fileToUpload")
        new_book = Book(book_id=book_id, title=title, published_year=published_year, summary=summary, genre=genre, image=image)
        database.session.add(new_book)
        database.session.commit()
        return render_template('authorHome.html')
    return render_template('authorBookCreation.html')


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
    return render_template('administratorHome.html')


@views.route('/authorHome.html')
@login_required
def author_home():
    return render_template('authorHome.html')


@views.route('/professorHome.html')
@login_required
def professor_home():
    return render_template('professorHome.html')


@views.route('/studentHome.html')
@login_required
def student_home():
    return render_template('studentHome.html')


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
        image = request.form.get('fileToUpload')

        new_auth = Author(author_id=prof_id, first_name=firstname,
                          last_name=lastname, biography=biography, email=email, image=image)
        database.session.add(new_auth)
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
        image = request.form.get('fileToUpload')

        new_prof = Professor(prof_id=prof_id, first_name=firstname,
                             last_name=lastname, biography=biography, email=email, image=image)
        database.session.add(new_prof)
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
