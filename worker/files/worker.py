import csv
import math
from datetime import datetime, timedelta
#instead of datetime use https://arrow.readthedocs.io/en/latest/
from influxdb import InfluxDBClient

def read_CSV(filename):
	data = []
	with open(filename) as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		#data = list(reader)
		for row in reader:
			if(not row[0]): 
				continue
			#skip PPD42NS sensor cause they're not acurat
			if(row[2]=="PPD42NS"):
					return None
			data.append(parse_CSV_row(row))
	return data		

def parse_CSV_row(row):
#,sensor_id,sensor_type,location,lat,lon,timestamp,P1,durP1,ratioP1,P2,durP2,ratioP2
	(row_id,sensor_id,sensor_type,location,lat,lon,timestamp,P1,durP1,ratioP1,P2,durP2,ratioP2) = tuple(map(lambda x: x, range(13)))
	return {
		#"row_id" : row[row_id],
		"sensor_id" : row[sensor_id],
		"sensor_type" : row[sensor_type],
		"location" : row[location],
		"lat" : row[lat],
		"lon" : row[lon],
		"timestamp" : parse_timestamp(row[timestamp]),
		"P1" : row[P1],
		#"durP1" : row[durP1],
		#"ratioP1" : row[ratioP1],
		"P2" : row[P2],
		#"durP2" : row[durP2],
		#"ratioP2" : row[ratioP2]
	}
	
def parse_timestamp(_timestamp):
	areas = list(map(lambda x: x*2.5*60, range(24)))
	"""
	[0.0, 150.0, 300.0, 450.0, 600.0, 750.0, 900.0, 1050.0, 1200.0, 1350.0, 
	1500.0, 1650.0, 1800.0, 1950.0, 2100.0, 2250.0, 2400.0, 2550.0, 2700.0, 
	2850.0, 3000.0, 3150.0, 3300.0, 3450.0]
	"""
	filtered_time = ''.join(_timestamp.rsplit(':', 1))
	sorted_time = datetime.strptime(filtered_time,'%Y-%m-%dT%H:%M:%S.%f%z')
	parsed_time = datetime(
		year=sorted_time.year,month=sorted_time.month,
		day=sorted_time.day, hour=sorted_time.hour, 
		minute=sorted_time.minute, second=sorted_time.second
	)
	

	seconds_timestamp = timedelta(minutes=parsed_time.minute,seconds=parsed_time.second).total_seconds()	
	#print(seconds_timestamp)
	for i in range(len(areas)):
		if(seconds_timestamp < areas[i]):
			# set minutes and seconds to 0 and add the minutes f.e 2:30 to datetime object
			return parsed_time.replace(minute=0,second=0) + timedelta(seconds=areas[i-1])
	return parsed_time.replace(minute=0,second=0) + timedelta(seconds=areas[-1])

def filter_data(data):
	filtered_data = []
	aritmethric_vals = {
		"P1" : 0,
		"P2" : 0
	}
	#check timestamp of current object
	low_bound,high_bound = 0,0

	for i in range(len(data)):
		if i+1 >= len(data):
			break
		if(data[i]["timestamp"] != data[i+1]["timestamp"]):
			#print("compared timestamps: %s and %s" % (str(data[i]["timestamp"]),str(data[i+1]["timestamp"])))
			aritmethric_vals = {
				"P1" : 0,
				"P2" : 0
			}
			high_bound = i+1
			for index in range(low_bound,high_bound):
				aritmethric_vals["P1"] += float(data[index]["P1"])
				aritmethric_vals["P2"] += float(data[index]["P2"])
			
			distance = high_bound-low_bound
			aritmethric_vals["P1"] /= distance
			aritmethric_vals["P2"] /= distance

			data[i]["P1"] = aritmethric_vals["P1"]
			data[i]["P2"] = aritmethric_vals["P2"]
			filtered_data.append(data[i])

			low_bound = high_bound
	return filtered_data

def prepare_data(data):
	"""
	FROM:
	{
		'sensor_id': '219', 'sensor_type': 'SDS011', 'location': '94', 
		'lat': '48.765', 'lon': '9.168', 'timestamp': datetime.datetime(2016, 10, 29, 9, 30), 
		'P1': 32.63, 'P2': 20.78
	}

	TO:
	    {
        "measurement": "brushEvents",
        "tags": {
            "user": "Carol",
            "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
        },
        "time": "2018-03-28T8:01:00Z",
        "fields": {
            "duration": 127
        }
    """
	prepared_data = []
	counter = 0
	for row in data:
		#print(row)
		#order of attributes is important!!
		pointValues = {
            "measurement": "feinstaub",
            "tags": {
	            "sensor_id": row["sensor_id"],
	            "sensor_type": row["sensor_type"],
	            "location" : row["location"],
	            "lat" : row["lat"],
	            "lon" : row["lon"],
	            #temp type,
	            #eine spalte mit tag und eine mit stunden

            },
            "time": row["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                "P1": row["P1"],
                "P2": row["P2"],

                #von dwd
	            #PP_10 / Luftdruck
	            #RF_10 / rel feuchte / in %
	            "RWS_10" : 0 ,#Niederschlagsmenge in mm
	            #windgeschwindigkeit ff_10
	            #windrichtung dd_10

	            #TMS_10 / - kann man weglassen
	            "PP_10" : 0, 
	            
	            #TT_10 / temp in 2m höhe -> temp
	            #TT_5 / temp in 5 cm höhe
	            
	            # wenn keine temp daten vorhanden dann dwd
	            
	            #windrichtung
	            #

            },
		}
		if(counter > 50):
			break
		counter+=1
		prepared_data.append(pointValues)
	#print(prepared_data)
	return prepared_data

def write_data(data):
	client = InfluxDBClient(host='localhost', port=8086)
	try:
		client.create_database('feinstaub')
	except:
		print("db already exists")
	client.switch_database('feinstaub')
	prepared_data = prepare_data(data)
	print(prepared_data)
	return client.write_points(prepared_data)

def run():
	filename = 'data/archive.luftdaten.info_2016-10-29_2016-10-29_sds011_sensor_219.csv'
	data = read_CSV(filename)
	cleaned_data = filter_data(data)
	result = write_data(cleaned_data)
	print(result)

def getDownloadedFiles():
	
if __name__ == "__main__":
    # execute only if run as a script
    #print(parse_timestamp("2016-10-29T15:57:54.636904+00:00"))
    run()