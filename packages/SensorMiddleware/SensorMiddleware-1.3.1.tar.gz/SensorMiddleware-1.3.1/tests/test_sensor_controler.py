import unittest
import logging
import requests

from http import HTTPStatus
from ecotrust_smiddleware.core import SensorControler, NonCommomHTTPStatuses
from requests.exceptions import ConnectionError

log = logging.getLogger(__name__)


class TestSensorControler(unittest.TestCase):
    def setUp(self):
        # Total used to break the loop of retries
        self.session = SensorControler.get_session(total_=2)

    def test_sensor_controler_session(self):
        # Test raise
        self.assertRaises(ConnectionError, self.session.get, "http://not_exists")

        # Test (Bad Gateway retry)
        log.warning('The server should be listenning on localhost:8080 for the test.')
        log.info('Testing bad gateway retry...')
        self.assertRaises(requests.exceptions.RetryError, self.session.get, 'http://localhost:8080')

        # Test (Service Unavailable retry)
        log.info('Testing service unavailable retry...')
        self.assertRaises(requests.exceptions.RetryError, self.session.get,
                          f'http://localhost:8080/{HTTPStatus.SERVICE_UNAVAILABLE}')

        # Test Site Frozen
        log.info('Testing site frozen retr ...')
        self.assertRaises(requests.exceptions.RetryError, self.session.get,
                          f'http://localhost:8080/{NonCommomHTTPStatuses.SITE_FROZEN}')


    def test_sensor_controler_parameter(self):
        scan_data = {}
        scontroler = SensorControler(
            manifest="[sensor_info]\n"+
                     f"sensor_path=/engines/netscan/\n"+
                     "default_port=foo\n"+
                     "engine_proc_name=python",
            scan_data=scan_data,
            full_api_url='http://admin:admin@127.0.0.1:8080/engines/netscan/'
        )

        scontroler.start_scan()

