from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Replace with your MongoDB Atlas connection URI
client = MongoClient('mongodb+srv://rithika:rithika@cluster0.fqbkkve.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = client.get_database('demo')
collection = db.demo_collection

print("MongoDB connected successfully")

# Index route to render the form for adding tasks
@app.route('/')
def index():
    return render_template('form.html')

# Route to handle adding a new task
@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        task_date = request.form.get('task_date')
        task_description = request.form.get('task_description')
        task_assignee = request.form.get('task_assignee')

        task = {
            'date': task_date,
            'description': task_description,
            'assignee': task_assignee,
            'completed': False
        }

        collection.insert_one(task)
        return redirect(url_for('view_tasks'))

    except Exception as e:
        app.logger.error(f"Error adding task: {e}")
        return "Error adding task."

# Route to display all tasks
@app.route('/tasks')
def view_tasks():
    try:
        tasks = list(collection.find())
        return render_template('tasks.html', tasks=tasks)
    except Exception as e:
        app.logger.error(f"Error retrieving tasks: {e}")
        return "Error retrieving tasks. Please check server logs for more details."


# Route to edit a task
@app.route('/edit_task/<string:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    try:
        if request.method == 'GET':
            task = collection.find_one({'_id': ObjectId(task_id)})
            if task:
                return render_template('edit_task.html', task=task)
            else:
                return "Task not found."
        elif request.method == 'POST':
            task_description = request.form.get('task_description')
            task_assignee = request.form.get('task_assignee')

            collection.update_one({'_id': ObjectId(task_id)}, {'$set': {
                'description': task_description,
                'assignee': task_assignee
            }})
            return redirect(url_for('view_tasks'))

    except Exception as e:
        app.logger.error(f"Error editing task: {e}")
        return "Error editing task."

# Route to delete a task
@app.route('/delete_task/<string:task_id>', methods=['POST'])
def delete_task(task_id):
    try:
        collection.delete_one({'_id': ObjectId(task_id)})
        return redirect(url_for('view_tasks'))

    except Exception as e:
        app.logger.error(f"Error deleting task: {e}")
        return "Error deleting task."

# Route to update the completion status of a task
@app.route('/update_completed/<string:task_id>', methods=['POST'])
def update_completed(task_id):
    try:
        completed = 'completed' in request.form
        collection.update_one({'_id': ObjectId(task_id)}, {'$set': {'completed': completed}})
        return redirect(url_for('view_tasks'))

    except Exception as e:
        app.logger.error(f"Error updating task status: {e}")
        return "Error updating task status."

if __name__ == '__main__':
    app.run(debug=True)
