from flask import Flask, render_template, request, redirect, url_for,flash,session
import mysql.connector

app = Flask(__name__)
app.secret_key = '1234'
# MySQL database configuration
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="flask task"  # Replace with your database name
)


# Home route
@app.route('/')
def home():
    return render_template('dashboard.html')


# Admin login route
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate the username and password (you can customize this according to your needs)
        if username == 'admin' and password == 'pass':
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Invalid username or password'

    return render_template('admin_login.html')


# Admin dashboard route
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        job_name = request.form.get('job_name')
        vacancies = int(request.form.get('vacancies'))
        course_duration = request.form.get('course_duration')

        # Insert the new job into the database
        insert_job(job_name, vacancies,course_duration)

        return redirect(url_for('admin_dashboard'))

    jobs = get_jobs()
    return render_template('admin_dashboard.html', jobs=jobs)


def get_jobs():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    cursor.close()
    return jobs


def insert_job(name, vacancies, course_duration):
    cursor = db.cursor(dictionary=True)
    select_query = "SELECT * FROM jobs WHERE name = %s"
    select_values = (name,)
    cursor.execute(select_query, select_values)
    existing_job = cursor.fetchone()

    if existing_job:
        update_query = "UPDATE jobs SET vacancies = %s, course_duration = %s WHERE id = %s"
        update_values = (vacancies, course_duration, existing_job['id'])
        cursor.execute(update_query, update_values)
    else:
        insert_query = "INSERT INTO jobs (name, vacancies, course_duration) VALUES (%s, %s, %s)"
        insert_values = (name, vacancies, course_duration)
        cursor.execute(insert_query, insert_values)

    db.commit()
    cursor.close()




# User registration route
@app.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        # Handle the form submission and process the user registration data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        qualification = request.form.get('qualification')
        place = request.form.get('place')
        password = request.form.get('password')

        # Set username equal to email
        username = email

        # Perform the necessary actions for user registration
        insert_user(name, email, phone, qualification, place, username, password)

        # Redirect to the registration success page
        return redirect(url_for('registration_success'))

    return render_template('user_registration.html')


def insert_user(name, email, phone, qualification, place, username, password):
    cursor = db.cursor()
    query = "INSERT INTO user_registration (name, email, phone, qualification, place, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (name, email, phone, qualification, place, username, password)
    cursor.execute(query, values)
    db.commit()
    cursor.close()


@app.route('/registration/success')
def registration_success():
    # Render the registration success template
    return render_template('registration_success.html')




# User login route
@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        # Handle the form submission and process the user login data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists in the database
        if user_exists(username):
            # Perform the necessary actions for user login (e.g., authenticate the user)
            # Add your login logic here

            # Set the username in session
            session['username'] = username

            # Redirect to the user dashboard (welcome page)
            return redirect(url_for('user_dashboard'))
        else:
            # User does not exist or login failed
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('user_login'))

    return render_template('user_login.html')


# User dashboard route
@app.route('/user/dashboard')
def user_dashboard():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']

        # Fetch the user details from the database based on the username
        user_details = get_user_details(username)

        if user_details:
            name = user_details['name']
            email = user_details['email']
            phone = user_details['phone']
            qualification = user_details['qualification']
            place = user_details['place']

            jobs = get_jobs()  # Retrieve the list of jobs from the database

            # Render the user dashboard template with the user details and jobs
            return render_template('login.html', name=name, email=email, phone=phone, qualification=qualification, place=place, jobs=jobs)
        else:
            # User details not found in the database
            flash('User details not found!', 'danger')

            return redirect(url_for('user_login'))
    else:
        # User is not logged in
        flash('Please login to access the user dashboard!', 'danger')
        return redirect(url_for('user_login'))



def insert_user(name, email, phone, qualification, place, username, password):
    cursor = db.cursor()
    query = "INSERT INTO user_registration (name, email, phone, qualification, place, username, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (name, email, phone, qualification, place, username, password)
    cursor.execute(query, values)
    db.commit()
    cursor.close()


def user_exists(username):
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM user_registration WHERE username = %s"
    values = (username,)
    cursor.execute(query, values)
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def get_user_details(username):
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM user_registration WHERE username = %s"
    values = (username,)
    cursor.execute(query, values)
    user_details = cursor.fetchone()
    cursor.close()
    return user_details

# Apply for a job route
# Job application route
@app.route('/apply_job', methods=['POST'])
def apply_job():
    if 'username' in session:
        username = session['username']
        job_id = request.form.get('job_id')

        # Get the job name based on the job_id
        job_name = get_job_name(job_id)

        if job_name:
            # Save the job application to the XAMPP MySQL database
            save_job_application(username, job_name)

            flash('Job application submitted successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid job selected!', 'danger')
            return redirect(url_for('user_dashboard'))
    else:
        flash('Please login to apply for a job!', 'danger')
        return redirect(url_for('user_login'))



def save_job_application(username, job_name):
    cursor = db.cursor()
    insert_query = "INSERT INTO job_applications (username, job_name) VALUES (%s, %s)"
    values = (username, job_name)
    cursor.execute(insert_query, values)
    db.commit()
    cursor.close()

def get_job_name(job_id):
    cursor = db.cursor()
    query = "SELECT name FROM jobs WHERE id = %s"
    values = (job_id,)
    cursor.execute(query, values)
    job_name = cursor.fetchone()
    cursor.close()
    if job_name:
        return job_name[0]
    else:
        return None



@app.route('/registered_logins')
def registered_logins():
    # Perform the necessary actions to fetch registered logins and their applied jobs from the database
    # You can customize this logic according to your database schema and requirements
    logins = get_registered_logins()
    applied_jobs = get_applied_jobs()

    return render_template('registered_logins.html', logins=logins, applied_jobs=applied_jobs)
def get_registered_logins():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT username, email, phone, qualification, place FROM user_registration")
    rows = cursor.fetchall()
    cursor.close()

    registered_logins = []
    for row in rows:
        login = {
            'username': row['username'],
            'email': row['email'],
            'phone': row['phone'],
            'qualification': row['qualification'],
            'place': row['place']
        }
        registered_logins.append(login)

    return registered_logins

def get_applied_jobs():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT username, job_name FROM job_applications")
    rows = cursor.fetchall()
    cursor.close()

    applied_jobs = {}
    for row in rows:
        username = row['username']
        job_name = row['job_name']
        if username in applied_jobs:
            applied_jobs[username].append(job_name)
        else:
            applied_jobs[username] = [job_name]

    return applied_jobs



if __name__ == '__main__':
    app.run(debug=True)






