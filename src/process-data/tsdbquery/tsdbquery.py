__author__ = 'cindylamm'

import requests

import config as conf


class InfluxDbConnector:
    def do_GET(self):
        r = requests.get(conf.DB_API_CALL + conf.DB_QUERY)
        return r

    def getJsonlistFromRequest(self, request):
        pointsJsonList = []
        pointsDict = {}
        columnNames = request.json()[0]['columns']
        for point in request.json()[0]['points']:
            for i in range(len(columnNames)):
                pointsDict[columnNames[i]] = point[i]
            pointsJsonList.append(dict(pointsDict))
        return pointsJsonList