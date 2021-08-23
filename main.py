from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, BooleanField, RadioField
from wtforms.validators import DataRequired, URL
from wtforms.widgets import TextArea
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

now = datetime.now()
current_year = now.strftime("%Y")

app = Flask(__name__)
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Wtforms
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(500), unique=False, nullable=False)
    status = db.Column(db.String(10), unique=False, nullable=False)


# db.create_all()


class ToDoForm(FlaskForm):
    task = StringField('Add a new To-Do', validators=[DataRequired()], widget=TextArea())
    submit = SubmitField('Add to List')


@app.route("/", methods=['POST', 'GET'])
def home():
    form = ToDoForm()
    task_list = []
    # If form is posted, create new task in db and redirect
    if form.validate_on_submit():
        new_task = Task(
            task=form.task.data,
            status="to-do"
        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("home"))
    # If get request, retrieve all tasks, append to list and render page
    all_tasks = Task.query.all()
    for task in all_tasks:
        task_list.append(task)
    return render_template("index.html", form=form, task_list=task_list, current_year=current_year)


# Deletes a task from db by id
@app.route("/delete/<id>", methods=["GET"])
def delete(id):
    task_to_delete = Task.query.get(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# Logic for moving status of task rightwards on page
@app.route("/move-right/<id>", methods=["GET"])
def moveRight(id):
    task_to_move = Task.query.get(id)
    if task_to_move.status == "to-do":
        task_to_move.status = "doing"
    elif task_to_move.status == "doing":
        task_to_move.status = "done"
    db.session.commit()
    return redirect(url_for('home'))


# Logic for moving status of task leftwards on page
@app.route("/move-left/<id>", methods=["GET"])
def moveLeft(id):
    task_to_move = Task.query.get(id)
    if task_to_move.status == "doing":
        task_to_move.status = "to-do"
    elif task_to_move.status == "done":
        task_to_move.status = "doing"
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
