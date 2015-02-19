__author__ = 'cindylamm'

import time
import logging

import config as conf
from tsdbquery import tsdbquery
from sparkprocess import sparkprocess




# ###############################################################################
# Defaults
#

if conf.DEBUG:
    FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
    FORMAT = '%(asctime)-0s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')

# requests_log = logging.getLogger("requests")
# requests_log.setLevel(logging.ERROR)


# ###############################################################################
# Main script
#
if __name__ == '__main__':
    dbConnector = tsdbquery.InfluxDbConnector()
    request = dbConnector.do_GET()
    pointsJsonList = dbConnector.getJsonlistFromRequest(request)
    sparkProcessor = sparkprocess.SparkProcessor()

    if conf.DEBUG:
        sparkProcessor.write_json_to_file(conf.IN_FILE, pointsJsonList)

    startProcessingTime = time.time()
    startDate, endDate, size = sparkProcessor.process(pointsJsonList)
    endProcessingTime = time.time()
    processing_time = endProcessingTime - startProcessingTime

    info = {
        "startDate": startDate,
        "endDate": endDate,
        "aggregationInputSize": conf.BATCH_SIZE,
        "aggregationOutputSize": size,
        "processingTimeInSeconds": round(processing_time, 3)
    }
    sparkProcessor.write_json_to_file(conf.INFO_FILE, info)


