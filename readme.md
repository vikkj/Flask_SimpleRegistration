# Simple Login and Registration app using flask and sqlalchemy

## Python modules required:
1. flask_sqlalchemy
2. flask

## How to work inside data base
Refer this : [flask_sqlalchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)

1. Creating new entry in database : ``` user_1 = User(
    username=request.form['name'],
email=request.form['email'],
gender=request.form['gender'],
skill=request.form['skill'],
certification=request.form['cert'],
phoneno=request.form['ph'],
address=request.form['add'],
education=request.form['edu'],
profile_img=request.files['file'],
specialization=request.form['special'] ```
2. Adding the above created to the current db session: ``` db.session.add(user_1) ```
3. Commiting the above change: ``` db.session.commit() ```
4. Dropping all the models created in the db: ``` db.drop_all() ```
5. Deleting a single entry in the database: ``` 
db.session.delete(User.query.filter_by(username=='<something>').first())
db.session.commit() ```

Note: To run all the above commands in cmd you have to first open cmd in current directory where you have this python file. Then under python interpreter type this command: ``` from Controller import db,User,RegisteredUsers ``` then you can use database from interpreter