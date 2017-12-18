from elizabeth import Personal
import random
from datetime import datetime, timedelta


class Patient():
    def __init__(self, ID, first_name, last_name, age, gender, sensors):
        self.ID = ID
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.sensors = sensors

    def __str__(self):
    	return "{0} {1} {2} {3} {4} {5}".format(self.ID, self.first_name, self.last_name, self.age, self.gender, self.sensors)


def generate_patients(number, male, female):
	patients = []
	person = Personal('en')
	sensors = ["Blood Pressure", "Heart Rate", "Glucose Levels", "Blood Oxygen Saturation"]

	# males
	for i in range(int(number * male)):
		first_name = person.name(gender="male")
		last_name = person.surname()
		age = person.age(18)

		# creates a copy of sensors
		x = sensors
		# shuffles the sensors
		random.shuffle(x)
		# picks a random number of sensors
		sens = ",".join(x[:random.randrange(1, len(sensors))])

		# sql query here
		patients.append(Patient(
			ID=0, #not important for this step as sql will auto increment
			first_name=first_name,
			last_name=last_name,
			age=age,
			gender="Male",
			sensors=sens
			))

	# females
	for i in range(int(number * female)):
		first_name = person.name(gender="female")
		last_name = person.surname()
		age = person.age(18)
		gender = "famale"

		# creates a copy of sensors
		x = sensors
		# shuffles the sensors
		random.shuffle(x)
		# picks a random number of sensors
		sens = ",".join(x[:random.randrange(1, len(sensors))])

		# sql query here
		patients.append(Patient(
			ID=0, #not important for this step as sql will auto increment
			first_name=first_name,
			last_name=last_name,
			age=age,
			gender="Female",
			sensors=sens
			))

	return patients 



def generate_sensor_data(patients, bp, hr, gl, bo, days):
	time_frame = days

	# could of used a disctionary here between string and rate which would remove all the ifs

	# [sample per hour, min, max]
	sensor_sample = {
		"Blood Pressure"			: [bp[0], bp[1], bp[2]],
		"Heart Rate"				: [hr[0], hr[1], hr[2]],
		"Glucose Levels"			: [gl[0], gl[1], gl[2]],
		"Blood Oxygen Saturation"	: [bo[0], bo[1], bo[2]]
	}
	# bp_rate = 0.083	# every 12 hours
	# hr_rate = 360 	# every 10 seconds
	# gl_rate = 0.25 	# every 4 hours
	# bo_rate = 2 	# every 30 mins


	# sampling rate of minutes per sample
	sensor_data = []
	for patient in patients:
		for sensor in patient.sensors.split(','):
			time = datetime.today() - timedelta(days=time_frame)

			# this will allways be true in this controlled enviroment
			if sensor in sensor_sample:
				for _ in range(int(sensor_sample[sensor][0] * time_frame * 24)):
					# need dystolic and stuff just do it a string maybe?
					time += timedelta(hours= 1 / sensor_sample[sensor][0])

					if sensor == "Blood Pressure":
						systolic = random.randrange(sensor_sample[sensor][1], sensor_sample[sensor][2] + 1)
						diastolic = 0
						try:
							diastolic = random.randrange(0, systolic - 40)
						except:
							diastolic = 0

						record = (patient.ID, time.strftime("%Y-%m-%d %H:%M:%S"), sensor, str(systolic) + "|" + str(diastolic)) # MAKE THIS A DOUBLE LINE graph, need to detect if blood pressure and if it is make another datapoint
					
					elif sensor == "Glucose Levels":
						record = (patient.ID, time.strftime("%Y-%m-%d %H:%M:%S"), sensor, round(random.uniform(sensor_sample[sensor][1], sensor_sample[sensor][2] + 1), 2))
					
					else:
						record = (patient.ID, time.strftime("%Y-%m-%d %H:%M:%S"), sensor, random.randrange(sensor_sample[sensor][1], sensor_sample[sensor][2] + 1))

					sensor_data.append(record)

	return sensor_data

		

	# # samples per hour
	# bp_rate = 0.083	# every 12 hours
	# hr_rate = 360 	# every 10 seconds
	# gl_rate = 0.25 	# every 4 hours
	# bo_rate = 2 	# every 30 mins


	# # sampling rate of minutes per sample
	# for patient in patients:
	# 	for sensor in patient.sensors.split(','):
	# 		sensor_data = []
	# 		# want to go 1 week in the past till current
	# 		# time = datetime.today() - timedelta(days= time_frame / 7)
	# 		time = datetime.today() - timedelta(days=7)

	# 		if sensor == "Blood Pressure":
	# 			for _ in range(int(bp_rate * time_frame)):
	# 				# need dystolic and stuff just do it a string maybe?
	# 				time += timedelta(hours= 1 / bp_rate)
	# 				record = (patient.ID, time, "Blood Pressure", random.randrange(40, 200)) # MAKE THIS A DOUBLE LINE
	# 				sensor_data.append(record)

	# 		if sensor == "Heart Rate":
	# 			for _ in range(int(hr_rate * time_frame)):
	# 				# need dystolic and stuff just do it a string maybe?
	# 				time += timedelta(hours= 1 / hr_rate)
	# 				record = (patient.ID, time, "Heart Rate", random.randrange(200))
	# 				sensor_data.append(record)

	# 		if sensor == "Glucose Levels":
	# 			for _ in range(int(gl_rate * time_frame)):
	# 				# need dystolic and stuff just do it a string maybe?
	# 				time += timedelta(hours= 1 / gl_rate)
	# 				record = (patient.ID, time, "Glucose Levels", random.randrange(200))
	# 				sensor_data.append(record)

	# 		if sensor == "Blood Oxygen Saturation":
	# 			for _ in range(int(bo_rate * time_frame)):
	# 				# need dystolic and stuff just do it a string maybe?
	# 				time += timedelta(hours= 1 / gl_rate)
	# 				record = (patient.ID, time, "Blood Oxygen Saturation", random.randrange(200))
	# 				sensor_data.append(record)

	# 		for data in sensor_data:
	# 			print(data)
