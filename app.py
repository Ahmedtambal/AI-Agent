import flask
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

print("Current Flask version:", flask.__version__)

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    def __repr__(self):
        return f"<Task {self.title}>"

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Routes for Task Management
@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'POST':
        data = request.form
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            deadline=datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M'),
            status='Pending'
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully!'}), 201

    tasks = Task.query.all()
    tasks_list = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'deadline': task.deadline.strftime('%Y-%m-%d %H:%M'),
        'status': task.status
    } for task in tasks]
    return jsonify(tasks_list), 200

@app.route('/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'GET':
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'deadline': task.deadline.strftime('%Y-%m-%d %H:%M'),
            'status': task.status
        }
        return jsonify(task_data), 200

    elif request.method == 'PUT':
        data = request.form
        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        if 'deadline' in data:
            task.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d %H:%M')
        task.status = data.get('status', task.status)
        db.session.commit()
        return jsonify({'message': 'Task updated successfully!'}), 200

    elif request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
