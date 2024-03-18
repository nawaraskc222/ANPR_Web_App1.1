


# from flask import Flask, render_template, request, url_for, flash, session
# from werkzeug.utils import redirect
# from flask_mysqldb import MySQL
# import os


from flask import Flask, render_template, request, url_for,session,flash
import smtplib
from werkzeug.utils import redirect
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mysqldb import MySQL
import os
from deeplearning import OCR
from datetime import datetime





BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH, 'static/upload/')

users = {
    'nawaras': 'root',
    'bibek': 'root',
    'manish': 'root'
}



app = Flask(__name__)
app.secret_key = 'many random bytes'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydb'
mysql = MySQL(app)


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['logged_in'] = True
            flash('Login Successful', 'success')
            return redirect(url_for('Index'))
        
    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    # flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# Index route
@app.route('/')
def Index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return render_template('Index.html', students=data)


# Insert route
@app.route('/insert', methods=['POST'])
def insert():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        print(request.form)
        flash("Data Inserted Successfully")
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        # photo = request.form['photo']
          # # see 2
        checkin = request.form['checkin']
        checkout = request.form['checkout']

         # Calculate hours parked
        cost_str = calculate_hours_parked(checkin, checkout)

         # Convert check-in and check-out times to datetime objects
        

        
        upload_file = request.files['photo']
        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH,filename)
        upload_file.save(path_save)
        photo = OCR(path_save,filename)


        cur = mysql.connection.cursor()

        # cur.execute("INSERT INTO students (name, email, phone,photo) VALUES (%s, %s, %s,%s)", (name, email, phone, photo))

        cur.execute("INSERT INTO students (name, email, phone,photo,cost_str) VALUES (%s, %s, %s,%s,%s)", (name, email, phone,photo,cost_str))
        
        mysql.connection.commit()
        return redirect(url_for('Index'))



def calculate_hours_parked(checkin, checkout):
    
    checkin_time = datetime.strptime(checkin, '%Y-%m-%dT%H:%M')
    checkout_time = datetime.strptime(checkout, '%Y-%m-%dT%H:%M')

    # Calculate the time difference in hours
    time_diff = (checkout_time - checkin_time).total_seconds() / 3600

    # Calculate the total cost
    total_cost = time_diff * 10

   

    return total_cost 

# Delete route
@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('Index'))


# Update route
@app.route('/update', methods=['POST'])
def update():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        photo = request.form['photo']

        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE students SET name=%s, email=%s, phone=%s,photo=%s
        WHERE id=%s
        """, (name, email, phone, photo, id_data))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))





@app.route('/send_email', methods=['POST'])
def send_email():
    receiver_email = request.form['emailTo']
    subject = request.form['emailSubject']
    body = request.form['emailBody']

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
        return redirect(url_for('Index'))
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    app.run(debug=True)
