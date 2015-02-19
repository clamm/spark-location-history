__author__ = 'cindylamm'

DEBUG = False   # True or False

IN_FILE = '../../data/output/spark_in.json'
INFO_FILE = '../../data/output/info.json'


# parameter for query of InfluxDB
INFLUXDB_HOST = 'localhost'  # InfluxDB server IP
DATABASE = 'location_history'  # InfluxDB event target database
TIME_SERIES = 'locations'  # the global time series for the event
DB_API_CALL = 'http://%s:8086/db/%s/series?u=root&p=root' % (INFLUXDB_HOST, DATABASE)
BATCH_SIZE = 10000  # number of points to get from the db
DB_QUERY = '&q=SELECT lat, lng FROM ' + TIME_SERIES + ' LIMIT ' + str(BATCH_SIZE)


# parameter for Spark processing
OUT_FILE_DATA = '../../data/output/spark_out_data.json'     # file that is read from front-end
OUT_FILE_EXTREMA = '../../data/output/spark_out_extrema.json'    # file that is read from front-end
INTERMEDIATE_FILE = '../../data/output/spark_intermediate.json'   # file with intermediate results for debugging
GEOHASH_PRECISION = 10  # for 10 the geohash boundary boxes are approximately 1 sqm
