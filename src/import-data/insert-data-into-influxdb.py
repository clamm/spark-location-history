# !/usr/bin/python

import json
import logging

from influxdb import client as influxdb

import config as conf


logging.basicConfig(level=logging.DEBUG, format=conf.FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')


def get_db_connection(host, port, user, password, db_name):
    return influxdb.InfluxDBClient(host, port, user, password, db_name)


def create_db(conn, db_name):
    if db_name not in [el['name'] for el in conn.get_database_list()]:
        conn.create_database(db_name)


def drop_series_from_db(conn, ts_name):
    logging.info('Drop series %s before import' % ts_name)
    conn.delete_series(ts_name)


def load_data_file(file_name):
    logging.info('Start loading %s file' % file_name)
    json_data = open(file_name)
    data = json.load(json_data)
    json_data.close()
    logging.info('Done loading %s file' % file_name)
    return data


def get_locations_from_data(data):
    if 'locations' in data.keys():
        return data['locations']


def adapt_bucket_size(locations, bucket_size):
    num_locations = len(locations)
    if num_locations < bucket_size:
        bucket_size = num_locations
        logging.info('Updated bucket_size to %s due to small input data' % num_locations)
    return bucket_size


def prepare_point(location):
    return [int(location['timestampMs']) / 1000,
            location['latitudeE7'] / 10000000.0,
            location['longitudeE7'] / 10000000.0]


def create_bucket(points, ts_name):
    return [
        {
            'points': points,
            'name': ts_name,
            'columns': ['time', 'lat', 'lng']
        }
    ]


def write_bucket_to_db(db, bucket):
    db.write_points(bucket)


def get_number_of_points_in_db(ts_name):
    return db.query('SELECT COUNT(lat) FROM ' + ts_name)[0].get('points')[0][1]


if __name__ == '__main__':
    # Connection to the influxdb
    db = get_db_connection(conf.INFLUXDB_HOST, conf.INFLUXDB_PORT, conf.USER, conf.PASSWORD, conf.DB_NAME)

    # Create a db within the connection
    create_db(db, conf.DB_NAME)

    if conf.CLEAN_SERIES:
        drop_series_from_db(db, conf.TS_NAME)

    data = load_data_file(conf.DATA_PATH)
    logging.info('Start inserting bucketed data into the db')
    locations = get_locations_from_data(data)
    bucket_size = adapt_bucket_size(locations, conf.BUCKET_SIZE)

    num_points = 0
    points = []
    num_buckets = 0

    for location in locations:
        point = prepare_point(location)
        points.append(point)
        num_points += 1
        # When we have a BUCKET_SIZE number of points we proceed to store the data in the db
        if num_points >= bucket_size:
            bucket = create_bucket(points, conf.TS_NAME)
            num_buckets += 1
            write_bucket_to_db(db, bucket)
            # Reset points
            points = []
            num_points = 0
            # Debugging info
            logging.debug('Last point written in bucket {0} was: {1}'.format(num_buckets, point))
            if conf.MAX_NUM_BUCKETS is not None and conf.MAX_NUM_BUCKETS == num_buckets:
                break

    num_points_in_db = get_number_of_points_in_db(conf.TS_NAME)
    logging.info('There are now {0} points in the series "{1}"'.format(num_points_in_db, conf.TS_NAME))
    logging.info('Done!')
