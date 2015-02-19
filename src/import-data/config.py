__author__ = 'cindylamm'

FORMAT = '%(asctime)-0s %(message)s'

# InfluxDB connection
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
USER = 'root'
PASSWORD = 'root'
DB_NAME = 'location_history'
TS_NAME = 'locations'

# Drop series before import?
CLEAN_SERIES = True

# Path to the location data from Google
DATA_PATH = '../../data/input/LocationHistory.json'

# Number of data points for every write operation to the InfluxDB
BUCKET_SIZE = 1000

# Limit of buckets to insert
# None - all buckets/points that are included in input data file
# 10   - only 10*BUCKET_SIZE points of input data file
MAX_NUM_BUCKETS = 10
