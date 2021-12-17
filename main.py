from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from app import create_app

app = create_app()

app.secret_key = 'Purdue Books Secret Key'

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')