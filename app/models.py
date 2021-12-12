from . import database
from flask_login import UserMixin


class School_Administrator(database.Model):
    sch_id = database.Column(database.String(
        256), database.ForeignKey('user.username'), primary_key=True)
    first_name = database.Column(database.String(256))
    last_name = database.Column(database.String(256))
    email = database.Column(database.String(256))


class Author(database.Model):
    author_id = database.Column(database.String(
        256), database.ForeignKey('user.username'), primary_key=True)
    image = database.Column(database.String(256))
    first_name = database.Column(database.String(256))
    last_name = database.Column(database.String(256))
    biography = database.Column(database.String(256))
    email = database.Column(database.String(256))


class Professor(database.Model):
    prof_id = database.Column(database.String(
        256), database.ForeignKey('user.username'), primary_key=True)
    image = database.Column(database.String(256))
    first_name = database.Column(database.String(256))
    last_name = database.Column(database.String(256))
    biography = database.Column(database.String(256))
    email = database.Column(database.String(256))


class Student(database.Model):
    stud_id = database.Column(database.String(
        256), database.ForeignKey('user.username'), primary_key=True)
    first_name = database.Column(database.String(256))
    last_name = database.Column(database.String(256))
    major = database.Column(database.String(256))
    email = database.Column(database.String(256))
    grade_year = database.Column(database.String(256))


class User(database.Model, UserMixin):
    username = database.Column(database.String(256), primary_key=True)
    pwd = database.Column(database.String(256))
    role = database.Column(database.String(256))

    def get_id(self):
        return (self.username)


class Book(database.Model):
    book_id = database.Column(database.String(256), primary_key=True)
    title = database.Column(database.String(256))
    published_year = database.Column(database.Integer)
    summary = database.Column(database.String(256))
    genre = database.Column(database.String(256))
    image = database.Column(database.String(256))

class Course(database.Model):
    course_id = database.Column(database.String(256), primary_key=True)
    name = database.Column(database.String(256))
    summary = database.Column(database.String(256))
    subject = database.Column(database.String(256))
    semester = database.Column(database.String(256))
    year = database.Column(database.String(256))

class Author_Book(database.Model):
    author_id = database.Column(database.String(
        256), database.ForeignKey('author.author_id'), primary_key=True)
    book_id = database.Column(database.String(
        256), database.ForeignKey('book.book_id'), primary_key=True)


class Professor_Book(database.Model):
    prof_id = database.Column(database.String(256), database.ForeignKey(
        'professor.prof_id'), primary_key=True)
    book_id = database.Column(database.String(
        256), database.ForeignKey('book.book_id'), primary_key=True)


class Book_Professor_Course(database.Model):
    prof_id = database.Column(database.String(256), database.ForeignKey(
        'professor.prof_id'), primary_key=True)
    book_id = database.Column(database.String(
        256), database.ForeignKey('book.book_id'), primary_key=True)
    course_id = database.Column(database.String(
        256), database.ForeignKey('course.course_id'), primary_key=True)


class Assigned_Professor_Course(database.Model):
    prof_id = database.Column(database.String(256), database.ForeignKey(
        'professor.prof_id'), primary_key=True)
    sch_id = database.Column(database.String(256), database.ForeignKey(
        'school__administrator.sch_id'), primary_key=True)
    course_id = database.Column(database.String(
        256), database.ForeignKey('course.course_id'), primary_key=True)


class Student_Course(database.Model):
    stud_id = database.Column(database.String(
        256), database.ForeignKey('student.stud_id'), primary_key=True)
    course_id = database.Column(database.String(
        256), database.ForeignKey('course.course_id'), primary_key=True)


class Book_Course(database.Model):
    book_id = database.Column(database.String(
        256), database.ForeignKey('book.book_id'), primary_key=True)
    course_id = database.Column(database.String(
        256), database.ForeignKey('course.course_id'), primary_key=True)


class Image(database.Model):
    image_id = database.Column(database.String(256), primary_key=True)
    image = database.Column(database.Text, nullable=False)
    name = database.Column(database.Text, nullable=False)
    mimetype = database.Column(database.Text, nullable=False)

class Rating(database.Model):
    stud_id = database.Column(database.String(
        256), database.ForeignKey('user.username'), primary_key=True)
    book_id = database.Column(database.String(
        256), database.ForeignKey('book.book_id'), primary_key=True)
    rating = database.Column(database.Integer)
