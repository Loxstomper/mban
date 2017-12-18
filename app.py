from flask import Flask, render_template, request, redirect, url_for
import pygal
import random
from generate_data import *
import sys
import json
import time
import statistics
import mysql.connector

db_user = "root"
db_password = "supersecretpassword"
db_host = "ban-db"
db_database = "ban"


app = Flask(__name__)


@app.route('/research')
def research():
    return render_template("research.html")
#### ANDROID APP ####

@app.route('/add', methods=["POST"])
def android_app():
    # convert data to JSON
    # check is patient exists
    # update data in database
    x = json.loads(request.data.decode())
    recieved_time = time.strftime("%Y-%m-%d %H:%M:%S") 

    # connect to db
    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database) 
    c = conn.cursor()

    # c.execute("SELECT COUNT(*) FROM Patients WHERE first_name = ? AND last_name = ?", [x['First_Name'], x['Last_Name']])
    c.execute(("SELECT COUNT(*) FROM ban.Patients WHERE first_name = %s AND last_name = %s"), (x['First_Name'], x['Last_Name']))


    # patient exists so update the values
    if c.fetchone()[0] != 0:
        # get the ID of the patient
        # c.execute("SELECT id FROM Patients WHERE first_name = ? AND last_name = ?", [x['First_Name'], x['Last_Name']])
        c.execute(("SELECT id FROM ban.Patients WHERE first_name = %s AND last_name = %s"), (x['First_Name'], x['Last_Name']))
        ID = c.fetchone()[0]

        # wont make sense if updating an existing patient that was created through the web app but its ok
        sensors = ["Mood", "Energy", "Appetite", "Stress", "Heart Rate", "Glucose Levels", "Blood Oxygen Saturation"]
        for sensor in sensors:
            # update db
            # c.execute("""INSERT INTO Readings VALUES(?, ?, ?, ?)""", [ID, recieved_time, sensor, x[sensor]])
            c.execute(("""INSERT INTO ban.Readings('ID', 'date', 'sensor', 'value') VALUES(%s, %s, %s, %s)"""), (ID, recieved_time, sensor, x[sensor]))

        # do BP here because 2 values per entry
        c.execute(("""INSERT INTO ban.Readings('ID', 'date', 'sensor', 'value') VALUES(%s, %s, %s, %s)"""), (ID, recieved_time, "Blood Pressure", x['BP_Sy'] + "|" + x["BP_Di"]))


        conn.commit()
        conn.close()

    # create the user
    else:
        print("PATIENT NOT IN DB")
        # return a message and app can have error message
    return "TEST"

################

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/patients/')
@app.route('/patients/<patient>')
def patient_page(patient=None):
    # if argument passed
    if patient and patient.isdigit():
        # checking if patient has record in table
        # conn = sqlite3.connect(db_location)
        conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database) 
        cursor = conn.cursor()

        # cursor.execute("""SELECT COUNT(*) FROM Patients WHERE ID = {0}""".format(patient))
        cursor.execute("""SELECT COUNT(*) FROM ban.Patients WHERE ID = {}""".format(patient))

        if cursor.fetchone()[0] != 0:
            # cursor.execute("""SELECT * FROM Patients WHERE ID = {0}""".format(patient))
            cursor.execute("""SELECT * FROM ban.Patients WHERE ID = {}""".format(patient))

            x       = cursor.fetchone()
            name    = x[1] + " " + x[2]
            age     = x[3]
            gender  = x[4]
            sensors = x[5]

            # major labels and hide minor labels
            # make major values every 4th, using MOD
            bp_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False, fill=True)
            bp_graph.title = "Blood Pressure"
            hr_graph = pygal.Line(interpolate="cubic", interpolation_precision=3, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            hr_graph.title = "Heart Rate"
            gl_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            gl_graph.title = "Glucose Levels"
            bo_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            bo_graph.title = "Blood Oxygen Saturation"
            mood_graph = pygal.Line(interpolate="cubic", interpolation_precision=3, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            mood_graph.title = "Mood"
            energy_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            energy_graph.title = "Energy"
            appetite_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            appetite_graph.title = "Appetite"
            stress_graph = pygal.Line(interpolate="cubic", interpolation_precision=100, legend_at_bottom=True, width=900, height=400, show_x_labels=False)
            stress_graph.title = "Stress"

            charts = {
                "Blood Pressure": bp_graph,
                "Heart Rate": hr_graph,
                "Glucose Levels": gl_graph,
                "Blood Oxygen Saturation": bo_graph,
                "Mood": mood_graph,
                "Energy": energy_graph,
                "Appetite": appetite_graph,
                "Stress": stress_graph
            }

            sensor_values = dict()

            for sensor in sensors.split(','):
                times = []
                if sensor == "Blood Pressure":
                    systolic   = []
                    diastolic  = []

                    # cursor.execute("""SELECT * FROM Readings WHERE ID = ? AND Sensor = ?""", (patient, sensor))
                    cursor.execute(("""SELECT * FROM ban.Readings WHERE ID = %s AND Sensor = %s"""), (patient, sensor))

                    for c in cursor:
                        times.append(c[1])
                        a, b = c[3].split('|')
                        systolic.append(int(a))
                        diastolic.append(int(b))

                    sensor_values[sensor] = (systolic, diastolic)
                    bp_graph.x_labels = times
                    bp_graph.add("Systolic", systolic)
                    bp_graph.add("diastolic", diastolic)
                else:
                    values = [] 
                    # cursor.execute("""SELECT * FROM Readings WHERE ID = ? AND Sensor = ?""", (patient, sensor))
                    cursor.execute(("""SELECT * FROM ban.Readings WHERE ID = %s AND Sensor = %s"""), (patient, sensor))

                    for c in cursor:
                        times.append(c[1])
                        if sensor in ["Heart Rate", "Blood Pressure", "Mood", "Energy", "Appetite", "Stress"]:
                            values.append(int(c[3]))
                        else:
                            values.append(float(c[3]))

                    sensor_values[sensor] = values
                    charts[sensor].x_labels = times
                    charts[sensor].add(sensor, values)

            conn.commit()
            conn.close()

            chart_data = {
                "bp":bp_graph.render_data_uri(),
                "hr":hr_graph.render_data_uri(),
                "gl":gl_graph.render_data_uri(),
                "bo":bo_graph.render_data_uri(),
                "mood": mood_graph.render_data_uri(),
                "energy": energy_graph.render_data_uri(),
                "appetite": appetite_graph.render_data_uri(),
                "stress": stress_graph.render_data_uri()
            }

            sensor_stats = dict()

            for sensor in sensor_values:
                if sensor == "Blood Pressure":
                    if len(sensor_values[sensor][0]) > 0:
                        sy = [min(sensor_values[sensor][0]), max(sensor_values[sensor][0]), round(sum(sensor_values[sensor][0]) / len(sensor_values[sensor][0]), 2), round(statistics.stdev(sensor_values[sensor][0]), 2), round(statistics.variance(sensor_values[sensor][0]), 2)]
                        di = [min(sensor_values[sensor][1]), max(sensor_values[sensor][1]), round(sum(sensor_values[sensor][1]) / len(sensor_values[sensor][1]), 2), round(statistics.stdev(sensor_values[sensor][1]), 2), round(statistics.variance(sensor_values[sensor][1]), 2)]
                        sensor_stats[sensor] = (sy, di)
                else:
                    if len(sensor_values[sensor]) > 0:
                        sensor_stats[sensor] = [min(sensor_values[sensor]), max(sensor_values[sensor]), round(sum(sensor_values[sensor]) / len(sensor_values[sensor]), 2), round(statistics.stdev(sensor_values[sensor]), 2), round(statistics.variance(sensor_values[sensor]), 2)]

            return render_template("patient-page.html", name=name, age=age, gender=gender, chart_data=chart_data, stats=sensor_stats)

        else:
            #return render_template("patient-home.html", error="Patient not in the database.")
            return redirect(url_for("patient_page"))
    else:
        # load all patient
        x = []

        # conn = sqlite3.connect(db_location)
        conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database) 
        cursor = conn.cursor()
        # cursor.execute("SELECT * FROM Patients")
        cursor.execute(("SELECT * FROM Patients"))

        for c in cursor:
            x.append(Patient(c[0], c[1], c[2], c[3], c[4], c[5]))

        conn.close()

        return render_template("patient-home.html", patients=x)

@app.route('/patients/add/', methods=["POST"])
def create_patient():
    first_name  = request.form['First Name']
    last_name   = request.form['Last Name']
    age         = request.form['Age']
    gender      = request.form['Gender']
    sensors     = request.form['Sensors']

    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database) 
    cursor = conn.cursor()
    # cursor.execute("""INSERT INTO Patients(first_name, last_name, age, gender, sensors) 
                      # VALUES (?, ?, ?, ?, ?)""", (first_name, last_name, age, gender, sensors))
    cursor.execute(("""INSERT INTO ban.Patients(first_name, last_name, age, gender, sensors) 
                      VALUES (%s, %s, %s, %s, %s)"""), (first_name, last_name, age, gender, sensors))

    conn.commit()
    conn.close()

    return redirect(url_for("patient_page"))

# bulk add from admin generate-patients
@app.route('/patients/add-bulk/', methods=["POST"])
def add_patients():
    number = int(request.form['Amount'])
    male = float(request.form['Male Ratio'])
    female = float(request.form['Female Ratio'])

    patients = generate_patients(number, male, female)

    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
    cursor = conn.cursor()

    for patient in patients:
        # cursor.execute("""INSERT INTO Patients(first_name, last_name, age, gender, sensors) 
                          # VALUES (?, ?, ?, ?, ?)""", (patient.first_name, patient.last_name, patient.age, patient.gender, patient.sensors))
        cursor.execute(("""INSERT INTO ban.Patients(first_name, last_name, age, gender, sensors) 
                          VALUES (%s, %s, %s, %s, %s)"""), (patient.first_name, patient.last_name, patient.age, patient.gender, patient.sensors))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route('/patients/remove')
@app.route('/patients/remove/<ID>')
def remove_patient(ID=None):
    if ID:
        # conn = sqlite3.connect(db_location)
        conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
        cursor = conn.cursor()

        # cursor.execute("""DELETE FROM Patients WHERE ID = {0}""".format(ID))
        cursor.execute("""DELETE FROM ban.Patients WHERE ID = {}""".format(ID))
        conn.commit()
        conn.close()

    return redirect(url_for("patient_page"))


@app.route('/patients/remove-all', methods=["POST"])
def remove_all_patient():
    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)

    cursor = conn.cursor()
    # cursor.execute("""DELETE FROM Patients""")
    cursor.execute(("""DELETE FROM ban.Patients"""))
    # shouldnt need this but cant get cascade delete working
    # cursor.execute("""DELETE FROM Readings""") 
    cursor.execute(("""DELETE FROM ban.Readings"""))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route('/sensors/add', methods=["POST"])
def sensor_data():

    bp = [float(request.form['BP RATE']), int(request.form['BP MIN']), int(request.form['BP MAX'])]
    hr = [float(request.form['HR RATE']), int(request.form['HR MIN']), int(request.form['HR MAX'])]
    gl = [float(request.form['GL RATE']), int(request.form['GL MIN']), int(request.form['GL MAX'])]
    bo = [float(request.form['BO RATE']), int(request.form['BO MIN']), int(request.form['BO MAX'])]
    days = int(request.form['Days'])


    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)

    cursor = conn.cursor()
    # cursor.execute("""SELECT * FROM Patients""")
    cursor.execute(("""SELECT * FROM ban.Patients"""))

    patients = []
    for c in cursor:
        patients.append(Patient(c[0], c[1], c[2], c[3], c[4], c[5]))

    # cursor.execute("""DELETE FROM Readings""")
    cursor.execute(("""DELETE FROM ban.Readings"""))

    data = generate_sensor_data(patients, bp, hr, gl, bo, days)

    for record in data:
        #print(record)
        record = (record[0], record[1], record[2], record[3])
        # cursor.execute("""INSERT INTO Readings VALUES(?, ?, ?, ?)""", record)
        cursor.execute(("""INSERT INTO ban.Readings VALUES(%s, %s, %s, %s)"""), (record))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route('/sensors/remove-all', methods=["POST"])
def remove_all_sensors():
    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
    cursor = conn.cursor()
    #cursor.execute("""DELETE FROM Readings""") 
    cursor.execute(("""DELETE FROM ban.Readings"""))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


@app.route('/admin/')
def admin():
    # conn = sqlite3.connect(db_location)
    conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
    cursor = conn.cursor()


    # GET ALL THE PATIENTS AND PUT THE SENSORS INTO A LIST AND SPLIT AT ',' and sum the sensors
    # cursor.execute("""SELECT COUNT(*) FROM Patients""")
    cursor.execute(("""SELECT COUNT(*) FROM ban.Patients"""))
    num_patients = cursor.fetchone()[0]

	# cursor.execute("""SELECT COUNT(*) FROM Patients WHERE Gender = 'Male'""")
    cursor.execute(("""SELECT COUNT(*) FROM ban.Patients WHERE Gender = 'Male'"""))
    num_males = cursor.fetchone()
    # cursor.execute("""SELECT COUNT(*) FROM Patients WHERE Gender = 'Female'""")
    cursor.execute(("""SELECT COUNT(*) FROM ban.Patients WHERE Gender = 'Female'"""))
    num_females = cursor.fetchone()

    # i dont like this, but couldnt get SQL TO WORK
    # cursor.execute("""SELECT Sensors FROM Patients""")
    cursor.execute(("""SELECT Sensors FROM ban.Patients"""))

    sensors = []
    for c in cursor:
        sensors += c[0].split(",")

    bp = sensors.count("Blood Pressure")
    hr = sensors.count("Heart Rate")
    gl = sensors.count("Glucose Levels")
    bo = sensors.count("Blood Oxygen Saturation")

    # cursor.execute("""SELECT COUNT(*) FROM Readings""")
    cursor.execute(("""SELECT COUNT(*) FROM ban.Readings"""))
    n_records = cursor.fetchone()[0]

    # cursor.execute("""SELECT COUNT(*) FROM Readings""")
    # n_records = cursor.fetchone()[0]
    
    # cursor.execute("""SELECT AVG(Age) FROM Patients""")
    cursor.execute(("""SELECT AVG(Age) FROM ban.Patients"""))
    x = cursor.fetchone()[0]
    if x:
        avg_age = round(x, 2)
    else:
        avg_age = "Na"

    conn.close()

    pie_chart = pygal.Pie(inner_radius=0.4, legend_at_bottom=True, half_pie=True)
    pie_chart.title = "Gender Distribution"
    pie_chart.add("Male", num_males)
    pie_chart.add("Female", num_females)
    pie_chart_data = pie_chart.render_data_uri()

    bar = pygal.Bar(legend_at_bottom=True, show_x_guides=True, show_y_guides=True)
    bar.title = "Sensor Distribution"
    bar.add("Blood Pressure", [bp])
    bar.add("Heart Rate", [hr])
    bar.add("Glucose Levels", [gl])
    bar.add("Blood Oxygen Saturation", [bo])
    bar_data = bar.render_data_uri()

    return render_template("admin.html", num_patients=num_patients, gender_chart=pie_chart_data, sensors_chart=bar_data, avg_age=avg_age, n_sensors=len(sensors), n_records=n_records, server_name=sys.argv[1])


def setup_db():
	conn = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database=db_database)
	cursor = conn.cursor()

	cursor.execute("""CREATE TABLE IF NOT EXISTS ban.Patients
	(
	ID          INTEGER PRIMARY KEY auto_increment,
	first_name  TEXT    NOT NULL,
	last_name   TEXT    NOT NULL,
	age         INTEGER NOT NULL,
	gender      TEXT    NOT NULL,
	sensors     TEXT
	)
    """)


	cursor.execute("""CREATE TABLE IF NOT EXISTS ban.Readings
	(
	ID      INTEGER auto_increment,
	date    TEXT,
	sensor  TEXT,
	value   TEXT,
	FOREIGN KEY(ID) REFERENCES Patients(ID) ON DELETE CASCADE
	)
    """)

	conn.commit()
	conn.close()


if __name__ == "__main__":
    try:
        setup_db()
    except:
        pass
    app.run(debug=True, host="0.0.0.0")
