# Flask imports
from flask import (
    Flask, render_template,
    url_for, request, session,
    redirect, make_response,
    abort, flash
)
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
from flask_ipban import IpBan

# General python imports
import os
from datetime import timedelta, datetime
import json
import numpy as np
from passlib.hash import sha256_crypt
import shutil

# Import local files
import processData
import ocsvm

# Website configurations
# general
app = Flask(__name__)

# # csrf token (for valid form submission from client to server side)
csrf = CSRFProtect(app)

# database
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'us-cdbr-east-03.cleardb.com'
app.config['MYSQL_USER'] = 'baec853f4a9c2a'
app.config['MYSQL_PASSWORD'] = '9ab7b405'
app.config['MYSQL_DB'] = 'heroku_7033404f5c36b67'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15) # user only permitted to login for x amount of minutes

# sessions
app.secret_key = ">bnbJ#Rl_c)>zm>o':wC%!0MS2A&]*e{)9U)c,FI5s;>f1@Ol|cj4o?V;FwHpS+"

# ip ban (blacklisting). if security_try == 3, ip will be banned
ip_ban = IpBan(ban_seconds=60) # 1 minute
ip_ban.init_app(app)

# Variables
login_try = 3# if login_try == 3, website will be routed to security question
security_try = 3

# Routing & Page views
@app.route('/', methods=["GET"])
def index():
    if session.get("user", None) != None and session.get('verified_login', None) == True:
        return render_template('index.html', user=session['user'])
    else:
        return redirect(url_for("login"))

@app.route('/register', methods = ['POST', 'GET'])
def register():
    # so that user logging in halfway cannot choose 'register' button and skip the typing habit verification
    if "verified_login" not in session or session['verified_login'] == False:
        session.pop('user', None)
    # variables
    check_user_exist = False
    user_error = ''
    email_error = ''
    session['registering'] = False
    if request.method == "POST":
        '''
        Variables taken from the form.
        They will be filled as it is required from client side
        '''
        new_user = request.form.get('username', None)
        first_name = request.form.get('first_name', None)
        last_name = request.form.get('last_name', None)
        dob = request.form.get('dob', None)
        email = request.form.get('email', None)
        sec_qn = request.form.get('sec-qn', None)
        sec_ans = request.form.get('sec-ans', None)

        # Check if username/email is taken
        check_user_exist = checkIfUserExists(new_user)
        check_email_exist = checkIfEmailExists(email)
        if check_user_exist == True: # username exists in db
            user_error = "Username is taken!"

        if check_email_exist == True: # email exists in db
            email_error = "Email is taken!"

        if check_user_exist == False and check_email_exist == False:
            # temporarily store registration details
            session["new_user"] = new_user
            session['fname'] = first_name
            session['lname'] = last_name
            session['dob'] = dob
            session['email'] = email
            session['sec_qn'] = sec_qn
            session['sec_ans'] = sec_ans

            session['registering'] = True
            return redirect(url_for("register_habit")) # success. moving onto step 2 of registration

        # return the appropriate error messages
        return render_template('register.html', user_error=user_error, email_error=email_error)
    else:
            return render_template('register.html') # This returns register.html onload (REQUIREMENT: Not a logged in user)

@app.route('/register/verify-habits', methods = ['POST', 'GET'])
def register_habit():
    # variables
    print('register habit')
    sentence = generate_new_sentence()
    calculation_array = []
    if request.method == "POST":
        print('posting register habittt')
        new_user = session.get("new_user", None)
        # if request.form.get("reg-typing-habit", None) == None or request.form.get("RHabit-json", None) == None or \
        #     request.form.get("reg-typing-habit", None) == '' or request.form.get("RHabit-json", None) == '':
        #     return render_template('register-habit.html', sentence=sentence[0],  error="Please input something")
        # else:
        # STEP 1: javascript to post the array of variables here
        data = request.form.get('RHabit-json', None)
        reg_sentence = session.get('sentence',None)
        raw_data = json.loads(data)
        user_session = 1
        new_user = session.get("new_user", None)

        if 'null' in data: # Check if data has error
            return render_template('register-habit.html', sentence=sentence[0], error="Error! Could not register habit. Please try again.")
        # STEP 2: processing, encryption of data and writing into csv
        # Processing
        for x in raw_data:
            calculation_array = [] # create empty array
            csv_obj = np.empty # create an empty numpy array << more uses - can store string + number in 1 array
            reps = raw_data.index(x)+1
            accuracy = x['accuracy']
            wpm = x['wpm']
            flight = x['flight']
            dwell = x['dwell']
            calculation_array = processData.processRawTypingData(dwell, flight)

            # print('cssssssssvvvvvvvvvv')
            csv_obj = processData.packTypingDataIntoArray(new_user, user_session, reps, accuracy, wpm, calculation_array)
            processData.saveCSV(new_user, csv_obj)

        # STEP 3: ocsvm
        try:
            new_user_data = ocsvm.getData(new_user)
            ocsvm.create_model(new_user_data)
        except Exception as e:
            #remove local file
            shutil.rmtree('typing-habits/' + new_user)
            print(e)
            abort(500)

        # res = ocsvm.predict(new_user_data)
        # print(res[0])
        # STEP 4: encryption of key?? & store in db (new table: s/n, user_id (fk reference users), encrypted key)
        processData.encryptCSV(new_user)
        # STEP 5: Insert new user into db

        try:
            try_register = register_user(session.get("new_user", None), session.get('fname', None), session.get('lname', None), \
            session.get('dob', None), session.get('email', None), reg_sentence, session.get('sec_qn', None), session.get('sec_ans', None))
        except Exception as e:
            # to add delete csv
            shutil.rmtree('typing-habits/' + new_user)
            print(e)
            abort(500)
        finally:
            # because we are done with registering
            # pop session variables
            session.pop("new_user", None)
            session.pop("registering", None)
            session.pop('fname', None)
            session.pop('lname', None)
            session.pop('dob', None)
            session.pop('email', None)
            session.pop('sec_qn', None)
            session.pop('sec_ans', None)
            session.pop('sentence', None)
        return redirect(url_for("index"))  # actually will redirect to login page because if no user is logged in, index will redirect to login


    else:
        if session.get('registering', None) == None or \
        session.get('registering', None) == False:
            # auto log out
            session.clear()
            abort(400) # bad request
        else:
            session['sentence'] = sentence[0]
            return render_template('register-habit.html', sentence=sentence[0])

@app.route('/login', methods = ['POST', 'GET'])
def login():
    # variables
    checkExist = False
    error = None

    # Check for method
    if request.method == 'POST':
        # Variables
        user = request.form.get('username', None)

        # Validation
        if not user or not user.strip():
            # print('user', session.get('user', None))
            error = 'No input detected'
        else:
            # connect to MySQL db and check if user is found in DB
            checkExist = checkIfUserExists(user)

            if checkExist == False:
                # verified_user = False
                error = 'User not detected, please register an account.'
            else:
                # this else statement means user is verified
                # and moving onto verifying typing habits
                session['user'] = user
                session['verified_login'] = False

                return redirect(url_for('login_verify'))# load step 2 of login

        return render_template('login.html', error=error)

    else:
        if 'user' not in session or 'verified_login' not in session or session['verified_login'] == False:
            return render_template('login.html')
        else:
            if session['verified_login'] == True:
                # If user somehow made it here after logging in, they cannot reach the login page again.
                return 'You are logged in as ' + session["user"] + ' already. Click <a href="/">here</a> to return to homepage'

@app.route('/login/verify', methods = ['POST', 'GET'])
def login_verify():
    global login_try
    if 'user' not in session:
        abort(401)
    # variables
    sentence = generate_login_sentence(session['user'])
    calculation_array = []

    if request.method == "POST":
        if request.form.get('login-typing-habit', None) == None \
        or request.form.get('login-typing-habit', None) == '':
            return render_template('login-verify-habit.html', user=session['user'], sentence=sentence[0], error="Please input something")
        else:
            # Javascript to post the array of variables here
            data = request.form.get('LVerify-json', None) # process & save into .csv
            raw_data = json.loads(data)
            accuracy = raw_data['accuracy']
            wpm = raw_data['wpm']
            flight_time = raw_data['flight']
            dwell_time = raw_data['dwell']
            calculation_array = processData.processRawTypingData(dwell_time, flight_time)

            # Create a temporary data frame to store new data
            user = session.get('user', None) # get username
            session_num = int(processData.getLastSessionNumber(user)) + 1 # get new session number
            csv_obj = processData.packTypingDataIntoArray(user, session_num, 1, accuracy, wpm, calculation_array)

            processData.decryptCSV(user)

            # Use Model to verify habits
            user_df = ocsvm.convertNPArrayToDF(csv_obj)
            prediction = ocsvm.predict(user_df)

            if prediction == 1:
                # IF SUCCESS
                # STEP 1: encryption of data and writing into csv
                csv_obj = processData.packTypingDataIntoArray(user, session_num, 1, accuracy, wpm, calculation_array)
                processData.saveCSV(user, csv_obj) # save the record into csv
                # STEP 3: ocsvm
                try:
                    user_updated_data = ocsvm.getData(user)
                    ocsvm.create_model(user_updated_data)
                except Exception as e:
                    #remove local file
                    shutil.rmtree('typing-habits/' + user)
                    print(e)
                    abort(500)

                processData.encryptCSV(user)
                # Step 2: return all the success/page all these
                #session.permanent = True # if successfully verified
                session['verified_login'] = True
                login_try = 3
                return redirect(url_for('index'))
            else:
                login_try -= 1
                if login_try == 0:
                    login_try = 3
                    shutil.rmtree('typing-habits/' + user)
                    return redirect(url_for('security_login'))
                else:
                    error_msg = str(login_try) + " out of 3 attempt(s) left."
                    # Step 1: Return error msg and try again

            shutil.rmtree('typing-habits/' + user)

        return render_template('login-verify-habit.html', error=error_msg, user=session['user'], sentence=sentence[0])

    else:
        if 'verified_login' in session and session.get('verified_login', None) == True:
            #If user somehow made it here after logging in, they cannot reach the login page again.
            return 'You are logged in as ' + session["user"] + ' already. Click <a href="/">here</a> to return to homepage'
        else:
            login_try = 3
            return render_template('login-verify-habit.html', user=session['user'], sentence=sentence[0])


@app.route('/login/security-attempt', methods=['POST', 'GET'])
def security_login():
    global security_try
    user = session.get('user', None)
    security_qn = getSecurityQn(user)
    if request.method == "POST":
        ans = request.form.get("security-ans", None)
        if ans == None or ans == '':
            return render_template('security-login.html', security_qn=security_qn[0], error='Please enter something')
        else:
            check = checkSecurityAns(user, ans)
            # print(check)
            if check == True:
                session['verified_login'] = True
                security_try = 3
                return redirect(url_for('index'))
            else:
                security_try -= 1
                if security_try == 0:
                    security_try = 3
                    session.clear()
                    ip_ban.block(request.remote_addr, permanent=False)
                    # return render_template('login.html', error='Too many attempts. Redirected to login page.')
                else:
                    error_msg = 'Security answer is incorrect. ' + str(security_try) + ' attempts left.'
                    return render_template('security-login.html', security_qn=security_qn[0], error=error_msg)
    else:
        if session.get('user', None) != None:
            security_try = 3
            return render_template('security-login.html', security_qn=security_qn[0])
        else:
            abort(401)

@app.route('/recalibrate', methods = ['POST', 'GET'])
def recalibrate():
    sentence = generate_new_sentence()
    calculation_array = []
    if request.method == "POST":
        user = session.get('user', None)
        if request.form.get("Recal-habit-json", None) == None or \
           request.form.get("Recal-habit-json", None) == '':
            return render_template('recalibrate.html', sentence=sentence[0], error="Error! Could not recalibrate habit. Please try again.")
        else:
            # step 1: javascript to post the array of variables here & Process
            data = request.form.get('Recal-habit-json', None)
            if 'null' in data:
                return render_template('recalibrate.html', sentence=sentence[0], error="Error! Could not recalibrate habit. Please try again.")
            recal_sentence = session.get('sentence',None)
            raw_data = json.loads(data)
            user = session.get("user", None)
            # STEP 2: remove of original habit file, processing, encryption of data and writing into csv
            # remove
            # folder_path = os.path.dirname(os.path.realpath('typing-habits\\' + user))
            # remove_filename = folder_path + '\\' + user + '\\' + user + ".csv"
            # os.remove(remove_filename)

            # Processing
            for x in raw_data:
                calculation_array = [] # create empty array
                csv_obj = np.empty # create an empty numpy array << more uses - can store string + number in 1 array
                reps = raw_data.index(x)+1
                accuracy = x['accuracy']
                wpm = x['wpm']
                flight = x['flight']
                dwell = x['dwell']
                calculation_array = processData.processRawTypingData(dwell, flight)

                csv_obj = processData.packTypingDataIntoArray(user, 1, reps, accuracy, wpm, calculation_array)
                processData.saveCSV(user, csv_obj)

            # STEP 3: ocsvm
            try:
                user_data = ocsvm.getData(user)
                ocsvm.create_model(user_data)
            except Exception as e:
                shutil.rmtree('typing-habits/' + user)
                # print(e)
                abort(500)

            # Encrypt csv
            processData.encryptCSV(user)

            # STEP 4: update sentence
            update = update_sentence(session['sentence'], user)
            if update == True:
                # give some success message
                session.pop('sentence', None)
                return render_template('recalibrate.html', \
                recalibrated="Success!!")
            else:
                abort(500)

    else:
        if 'verified_login' not in session or session.get('verified_login', None) == False:
            #If a guest somehow made it here before logging in, they will be thrown a bad request
            # clear session
            session.clear()
            abort(401) # unauthorized
        else:
            session['sentence'] = sentence[0]
            return render_template('recalibrate.html', sentence=sentence[0])


@app.route('/logout')
def logout():
    session.clear()
    ip_ban.remove(request.remote_addr)
    return render_template('logout.html')

# error handling (404, 400, 401, 500)
@app.errorhandler(404)
def not_found(self):
    return make_response(render_template("error.html", error="Page not found :(", e_type="404"), 404)

@app.errorhandler(400)
def bad_req(self):
    return make_response(render_template("error.html", error="Bad request :(", e_type="400"), 400)

@app.errorhandler(401)
def unauthorized(self):
    return make_response(render_template("error.html", error="Unauthorized. Please log in first.", e_type="401"), 401)

@app.errorhandler(500)
def internal_server_error(self):
    return make_response(render_template("error.html", error="Internal server error :(", e_type="500"), 500)

@app.route('/privatepolicy')
def pp():
    return render_template("private_policy.html")



# functions/methods
def checkIfUserExists(user):
    # connect to MySQL db and check if user is found in DB
    cursor = mysql.connection.cursor()
    cursor.execute('select * from users where username = %s', [user])
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        return True

def checkIfEmailExists(email):
    # connect to MySQL db and check if email is found in DB
    cursor = mysql.connection.cursor()
    cursor.execute('select * from users where email = %s', [email])
    result = cursor.fetchone()
    cursor.close()
    if result == None:
        return False
    else:
        return True

def generate_new_sentence():
    cursor = mysql.connection.cursor()
    cursor.execute("select sentence from sentence_bank order by rand() limit 1")
    result = cursor.fetchone()
    cursor.close()
    return result

def generate_login_sentence(user):
    cursor = mysql.connection.cursor()
    cursor.execute("select sentence from users where username = %s", [user])
    result = cursor.fetchone()
    cursor.close()
    return result

def update_sentence(sentence, user):
    parameter = ([sentence], [user])
    cursor = mysql.connection.cursor()
    success = False
    try:
        update_statement = cursor.execute("UPDATE `users` SET `sentence` = %s WHERE `users`.`username` = %s", parameter)
        mysql.connection.commit()
        success = True
    except Exception as e:
        # print(e)
        success = False
    finally:
        cursor.close()
        return success

def register_user(user, first_name, last_name, dob, email, sentence, security_qn, security_ans):
    date_of_birth = dob.split('-')
    new_dob = datetime(int(date_of_birth[0]), int(date_of_birth[1]), int(date_of_birth[2]))
    formatted_dob = new_dob.strftime('%Y-%m-%d')
    security_ans_hash = sha256_crypt.hash(security_ans)
    # parameterized_dob = "'" + "{formatted_dob}".format(formatted_dobformatted_dob=formatted_dob) + "'"
    cursor = mysql.connection.cursor()
    query = "INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`, `date_of_birth`, `email`, `sentence`, `security_qn`, `security_ans`) \
    VALUES (NULL, %s, %s, %s, STR_TO_DATE(%s, '%%Y-%%m-%%d'), %s, %s, %s, %s)"
    parameter =  ([user], [first_name], [last_name], [formatted_dob], [email], [sentence], [security_qn], [security_ans_hash])

    success = False
    try:
        register = cursor.execute(query, parameter)
        mysql.connection.commit()
        success = True
    except Exception as e:
        # print(e)
        success = False
    finally:
        cursor.close()
        return success

def getSecurityQn(user):
    cursor = mysql.connection.cursor()
    cursor.execute("select security_qn from users where username = %s", [user])
    result = cursor.fetchone()
    cursor.close()
    return result

def checkSecurityAns(user, ans):
    cursor = mysql.connection.cursor()
    cursor.execute("select security_ans from users where username = %s", [user])
    result = cursor.fetchone()
    result = result[0]
    cursor.close()
    return sha256_crypt.verify(ans, result)
    # if result == ans:
    #     return True
    # else:
    #     return False

if __name__ == "__main__":
    app.run()
    # ensure css/js will auto update each time I save
    if (os.environ.get('FLASK_ENV') == 'development'):
        SEND_FILE_MAX_AGE_DEFAULT=0