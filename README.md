# CRYPTO-STOCKS

## CS50

>This was my final project for conclude the CS50 Introduction to Computer Sciense course.
>CS, python, flask, flask web framework, web development, CS50
## Features
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/index.html)

I've used Flask web framework based in Python
its was necessary flask-sqlalchemy for manage SQL database with sqlite and flask-wtf for upload Password, Username, Key and secret Key.

## Explaining the project and the database
My web App is a crypto-stocks exchange that use real data from ALPACA. You can train yourself in order to understand the market and improve your skills as a broker.
In order to be able to use the app, you need to register yourself into ALPACA website, confirm your email and then on paper account press the yellow button (GENERATE KEY),
copy your KEY and your SECRET KEY on some text editor like NOTEPAD++. once you have done this you can register yourself.
Be sure to use a correct username and correct password. When you will be registered You would be able to trade stocks and crypto asset, without worrying of lose any money.
YES! you won't lose any money, as the app will provide you a total free envorioment that by default will charge on your account 100.000$.
If you will lose this money then you will need to reset your account. To reset your account, go to alpaca website, login and on the dashborad click RESET ACCOUNT your KEY.
PAY ATTENTION: everynow and then ALPACA requir to regenerate the KEY, when this happen you need to recreate another account.
FILE: app.py and config.py are the heart of the programm, here is written all the python code. ; clienti.db is the database where all the clients will register theirself
with password-confirmation password- username- Key and secret Key, in order to have the correct dashborad and to store correctly all the data.;
requirments.txt is the file where are named all the programs needed for app.py and flask to run. ; templates folder: here there are all the files for html code.
static folder: there is an image of my favicon and the CSS files which is the heart of my design web application.


I used sqlalchemy extension for connect the database to application and sqlite3 to manager her.

### Sqlachemy and sqlite3:
I needed 1 table for my database:

- First, table client. Where I put, id, username, hash (for password) key and secret key.

finalproject\assethistory .jpg" width="400"> | <img src="C:\Users\HOME\Desktop\cs50finalproject\dashborad.jpg" width = "400">

#### Video Demo:  https://youtu.be/CQpLY7QdzuY

#### Description: My web App is a crypto-stocks exchange that use real data from ALPACA. You can train yourself in order to understand the market and improve your skills as a broker.
In order to be able to use the app, you need to register yourself into ALPACA website, confirm your email and then on paper account press the yellow button (GENERATE KEY),
copy your KEY and your SECRET KEY on some text editor like NOTEPAD++. once you have done this you can register yourself. Be sure to use a correct username and correct password. When you will be registered You would be able to trade stocks and crypto asset, without worrying of lose any money. YES! you won't lose any money, as the app will provide you a total free envorioment that by default will charge on your account 100.000$. If you will lose this money then you will need to reset your account. To reset your account, go to alpaca website, login and on the dashborad click RESET ACCOUNT your KEY. PAY ATTENTION: everynow and then ALPACA requir to regenerate the KEY, when this happen you need to recreate another account. FILE: app.py and config.py are the heart of the programm, here is written all the python code. ; clienti.db is the database where all the clients will register theirself with password-confirmation password- username- Key and secret Key, in order to have the correct dashborad and to store correctly all the data. ; requirments.txt is the file where are named all the programs needed for app.py and flask to run. ; templates folder: here there are all the files for html code. ;
static folder: there is an image of my favicon and the CSS files which is the heart of my design web application.

## About CS50
CS50 is a openware course from Havard University and taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.

- Where I get CS50 course?
https://cs50.harvard.edu/x/2020/

[LinkedIn Anthony Contu](https://www.linkedin.com/in/anthony-contu-49505416a/)