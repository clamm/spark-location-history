import time

__author__ = 'cindylamm'

import json

from operator import add

from geohash import *

import config as conf
from pyspark import SparkConf, SparkContext


class SparkProcessor(object):
    def process(self, jsonList):
        # initiate spark
        sparkConf = SparkConf().setMaster("local").setAppName("geo-processor")
        sc = SparkContext(conf=sparkConf)

        # parallelize our input data into an RDD
        pointsRDD = sc.parallelize(jsonList)

        # find start and end date
        startEpoch = pointsRDD.map(lambda x: x['time']).min()
        startDate = self.convertEpochToDate(startEpoch)
        endEpoch = pointsRDD.map(lambda x: x['time']).max()
        endDate = self.convertEpochToDate(endEpoch)

        # aggregate checkins
        # (geohash, 1) -> reduceByKey with add totals -> map to reverse geohash
        geohashCountsRDD = pointsRDD.map(self.getGeohashFromLatLng).reduceByKey(add)

        if conf.DEBUG:
            self.write_json_to_file(conf.INTERMEDIATE_FILE, geohashCountsRDD.take(100))

        latLngCountsRDD = geohashCountsRDD.map(self.getLatLngFromGeohash)
        nbPoints = geohashCountsRDD.map(self.getLatLngFromGeohash).count()

        minimumCount = geohashCountsRDD.map(lambda x: x[1]).min()
        maximumCount = geohashCountsRDD.map(lambda x: x[1]).max()
        extrema = {
            "minCount": minimumCount,
            "maxCount": maximumCount
        }
        self.write_json_to_file(conf.OUT_FILE_EXTREMA, extrema)

        result = latLngCountsRDD.collect()
        self.write_json_to_file(conf.OUT_FILE_DATA, result)

        # shutdown spark
        sc.stop()

        return startDate, endDate, nbPoints


    def distinct(self, l):
        return len(set(l))


    def convertEpochToDate(self, epochMicroseconds):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epochMicroseconds / 1000))


    def getGeohashFromLatLng(self, entry):
        geohash = encode(entry['lat'], entry['lng'], conf.GEOHASH_PRECISION)
        return (geohash, 1)


    def getGeohashWithUserFromLatLng(self, entry):
        geohash = encode(entry['lat'], entry['lng'], conf.GEOHASH_PRECISION)
        return (geohash, entry['user_id'])


    def getLatLngFromGeohash(self, entry):
        coord = decode(entry[0])
        return {
            'lat': coord[0],
            'lng': coord[1],
            'count': entry[1]
        }


    def write_json_to_file(self, filename, result):
        self.write_to_file(filename, json.dumps(result, indent=2))


    def write_to_file(self, filename, result):
        f = open(filename, "w")
        f.write(result)
        f.close()
