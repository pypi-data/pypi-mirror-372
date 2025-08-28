# -*- coding: utf-8 -*-
import urllib3.exceptions

from ecotrust_smiddleware.aws import get_scan_data_from_s3_bucket, upload_log_dump
from ecotrust_smiddleware.abstract import Sensor
from pathlib import Path
from typing import NoReturn, AnyStr, Dict, Union
from requests_toolbelt.sessions import BaseUrlSession
from requests import Session as HTTPSession, Response
from requests.adapters import HTTPAdapter, Retry
from rich import print # noqa
from http import HTTPStatus
from enum import IntEnum
try:
    from gevent import sleep as gevent_sleep # non-blocking
except (ModuleNotFoundError, ImportError):
    from time import sleep as gevent_sleep # blocking

try:
    from typing import Final, Tuple
except ImportError:
    from typing_extensions import Final, Tuple

import requests.exceptions
import configparser
import os
import json
import secrets
import io

DEBUG = os.getenv('DEBUG', False)


# URL That should be called back when the scan finishes or some error occurs
# AUTOMATICALLY INJECTED BY ECS FARGATE
SCAN_CALLBACK_URL = os.getenv('SCAN_CALLBACK_URL')
FILES_BY_SENSOR_TYPE = {
    'WEBAPP': [
        '/root/.ZAP/zap.log',
        '/opt/access.log',
        '/opt/error.log',
    ]
}

DEFAULT_FILES = [
    '/opt/error.log',
    '/opt/access.lgo'
]


class NonCommomHTTPStatuses(IntEnum):
    def __new__(cls, value, phrase, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    WEB_SERVER_IS_DOWN = 521, 'Web Server Is Down'
    CONNECTION_TIMED_OUT = 522, 'Connection Timed Out'
    SSL_HANDSHAKE_FAILED = 525, 'SSL Handshake Failed'
    SITE_FROZEN = 530, 'Site Frozen'
    NETWORK_CONNECTION_TIMED_OUT = 599, 'Network Connect Timeout Error'


class BadManifestSyntax(SyntaxError):
    """
        Raised when manifest.ini is not with the proper syntax/sections.
    """
    pass


class CannotReadScanData(Exception):
    """
        Raised when the scan data cannot be read from envvar/...
    """
    pass


class Super:
    """
        Non-canonical class to refer to the super within the upper class
    """
    pass


class SensorControler(Sensor):
    _session: Union[HTTPSession, None] = None
    SENSOR_MANIFEST_PATH	= Path('/opt/manifest.ini') # noqa

    # Keys to get in the manifest.ini
    SENSOR_PATH_CNF_NAME    = 'sensor_path' # noqa
    SENSOR_TYPE_CNF_NAME    = 'sensor_type' # noqa
    SENSOR_PORT_CNF_NAME    = 'default_port' # noqa
    SENSOR_ENGINE_CNF_NAME  = 'engine_proc_name' # noqa

    ENGINE_READY_STATUS 	= 'READY' # noqa
    ENGINE_ERROR_STATUS 	= 'ERROR' # noqa
    SCAN_RUNNING_STATUS 	= ['STARTED', 'SCANNING', 'PAUSING', 'STOPING', 'UNKNOWN'] # noqa
    SCAN_ERROR_STATUS       = ['ERROR', 'INEXISTENT-SCAN'] # noqa
    SCAN_FINISHED_STATUS    = ['FINISHED', 'STOPPED'] # noqa
    SCAN_FINISHED           = 'FINISHED' # noqa

    def __init__(self, manifest=None, scan_data=None, full_api_url=None, check_if_engine_is_running=True):
        self.scan_data: 	  Union[Dict, None] = None
        self.sensor_manifest: Union[Dict, None] = None
        self._sensor_api:	  Union[SensorControler.SensorAPIControler, None] = None # noqa
        self.full_api_url = full_api_url
        self.check_if_engine_is_runnin = check_if_engine_is_running

        if scan_data is not None:
            # GET SCAN DATA VIA STRING
            self.scan_data = scan_data
        else:
            # GET SCAN DATA FROM S3 BUCKET
            self._get_scan_from_s3_and_settovar()

        if manifest is not None:
            # GET MANIFEST DATA VIA STRING
            config = configparser.ConfigParser()
            config.read_file(io.StringIO(manifest))
            self.sensor_manifest = dict(config['sensor_info'])
        else:
            # GET MANIFEST DATA FROM HOST MACHINE
            self._read_sensor_manifest_and_settovar()

        # Normalize some data
        self.scan_data['options'] = self.scan_data.pop('engine_policy', {})
        self.scan_data['scan_id'] = self.scan_data.pop('id', '4747')

        # Get engine name and scan id from readed scan data / manifest
        self.engine_name = self.sensor_manifest[SensorControler.SENSOR_ENGINE_CNF_NAME]  # noqa
        self.sensor_type = self.sensor_manifest[SensorControler.SENSOR_TYPE_CNF_NAME] # noqa
        self.scan_id     = self.scan_data['scan_id']  # noqa

    @property
    def sensor_api(self):
        if self._sensor_api is None:
            # Initialize
            try:
                sensor_api_url_path = self.sensor_manifest[SensorControler.SENSOR_PATH_CNF_NAME]
                sensor_api_url_port = self.sensor_manifest[SensorControler.SENSOR_PORT_CNF_NAME]
            except KeyError:
                raise NameError('sensor_manifest is not initialized yet !')
            else:
                self._sensor_api = SensorControler._SensorAPIControler(
                    sensor_api_url_path,
                    sensor_api_url_port,
                    self.scan_id, full_api_url=self.full_api_url)

        return self._sensor_api

    @classmethod
    def get_session(cls, total_=None) -> requests.sessions.Session:
        if cls._session is None:
            cls._session = HTTPSession()
            http_adapter = HTTPAdapter(max_retries=Retry(
                total=total_, # noqa
                status_forcelist=[
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    HTTPStatus.BAD_GATEWAY,
                    HTTPStatus.GATEWAY_TIMEOUT,
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    NonCommomHTTPStatuses.WEB_SERVER_IS_DOWN,
                    NonCommomHTTPStatuses.SITE_FROZEN,
                    NonCommomHTTPStatuses.CONNECTION_TIMED_OUT,
                    NonCommomHTTPStatuses.SSL_HANDSHAKE_FAILED,
                    NonCommomHTTPStatuses.NETWORK_CONNECTION_TIMED_OUT
                ]
            ))

            cls._session.mount('http://', http_adapter)
            cls._session.mount('https://', http_adapter)

        return cls._session

    @staticmethod
    def fail_scan(error_message: str, scontroler=None) -> NoReturn:
        if SCAN_CALLBACK_URL is None:
            print('[bold red] CRITICAL ERROR: SCAN_CALLBACK_URL is NULL [/bold red]')
            return

        callback_response = None
        try:
            callback_response = SensorControler.get_session().get(SCAN_CALLBACK_URL, params={
                'errmsg': error_message,
                'status': 'error'
            })
        except: # noqa
            pass

        # upload fail dump
        upload_log_dump(FILES_BY_SENSOR_TYPE.get(scontroler.sensor_type, DEFAULT_FILES), scontroler.scan_id)

        if DEBUG:
            print(f'[bold green] Callback repsonse:'
                  f'Status code: {callback_response.status_code}'
                  f'Text Response: {callback_response.text}')

    @staticmethod
    def finish_scan(scontroler) -> NoReturn:
        if SCAN_CALLBACK_URL is None:
            print('[bold red] CRITICAL ERROR: SCAN_CALLBACK_URL is NULL [/bold red]')
            return

        callback_response = None
        try:
            callback_response = SensorControler.get_session().get(SCAN_CALLBACK_URL, params={
                'errmsg': None,
                'status': 'finished'
            })
        except: # noqa
            pass

        # upload log dump
        upload_log_dump(FILES_BY_SENSOR_TYPE.get(scontroler.sensor_type, DEFAULT_FILES), scontroler.scan_id)

        if DEBUG:
            print(f'[bold green] Callback repsonse:'
                  f'Status code: {callback_response.status_code} '
                  f'Text Response: {callback_response.text}')

    def is_engine_process_running(self, __=None):
        return super().is_engine_process_running(self.engine_name)

    class _SensorAPIControler(Super):
        DEFAULT_PROTO = 'http'
        DEFAULT_ADDR  = '127.0.0.1' # noqa
        SCAN_STARTED_STATUS = ['accepted']
        SCAN_STOPPED_STATUS = ['SUCCESS', 'success']

        def __init__(self, base_api_path, base_api_port, scan_id, full_api_url=None):
            if full_api_url is None:
                self.session = BaseUrlSession(f'{self.DEFAULT_PROTO}://{self.DEFAULT_ADDR}:{base_api_port}')
            else:
                self.session = BaseUrlSession(full_api_url)

            #self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=5)) # noqa
            self.base_path = base_api_path
            self.scan_id = scan_id
            self.is_scan_started = False

        def _make_request(self, method, *args, **kwargs) -> Dict:
            """
            Method that concats base_api_path to the middle of the URL and set some default values to the request.

            :param method: HTTP method
            :param args: Args to pass to the request method
            :param kwargs: Kwargs to pass to the request method
            :return: <Response> object
            """

            # response json
            rjson: Union[Dict, None] = None # noqa

            # Get req object
            do_request = getattr(self.session, method)

            # Do some changes
            kwargs['url'] = f'{self.base_path}{kwargs["url"][1:]}'
            kwargs['allow_redirects'] = False
            kwargs['verify'] = False

            # Do the request
            try:
                response: Response = do_request(*args, timeout=30, **kwargs)
                response.raise_for_status()
            except (
                    requests.exceptions.HTTPError,
                    requests.exceptions.RequestException,
                    ConnectionError,
                    ConnectionRefusedError,
                    ConnectionResetError,
                    ConnectionError,
                    urllib3.exceptions.NewConnectionError, OSError, Exception) as neterr:
                rjson = {
                    'status': 'network-error',
                    'details': {
                        'reason': f'(_make_request): {str(neterr)}'
                    }
                }
            else:
                if DEBUG:
                    print(f'[bold green] '
                          f'{method} -> {kwargs["url"]} RET: {response.status_code} '
                          f'TEXT: {response.text} [/bold green]')

                # Parse response (JSON)
                try:
                    raw_text = response.content.replace(b'', b'', -1).replace(b'\x00', b'', -1)
                    rjson = json.loads(raw_text)
                except Exception as decode_error: # noqa
                    if DEBUG:
                        import traceback
                        print(f'[bold red] Got Exception: {traceback.format_exc()}')

                    rjson = {
                        'status': 'decode-error',
                        'details': {
                            'reason': f'(_make_request): {str(decode_error)}'
                        }
                    }

            return rjson

        def _get_reason(self, json_response: Union[None, Dict]) -> Union[str, None]:
            # null safety
            jresponse = json_response or {}
            reason = (jresponse
                      .get('details', {})
                      .get('reason', None) or
                      jresponse.get('reason'))

            # fallback to the raw response
            if reason is None:
                reason = f'Raw: {str(jresponse)}'

            return reason

        class _Decorators:
            @classmethod
            def after_scan_starts(cls, fn):
                """
                Decorator that checks if the scan is started before calling the function.
                :param fn:
                :return: wrapper
                """
                def wrapper(self, *args):
                    if not self.is_scan_started:
                        raise RuntimeError('Scan not started yet !')

                    return fn(self, *args)

                return wrapper

        def call_enginestatus(self) -> AnyStr:
            """
            Get engine status
            :return:
            """
            rjson = self._make_request(method='get', url='/status')
            return rjson.get('status', 'WAIT')

        def call_startscan(self, scan_data: Dict) -> Tuple[bool, AnyStr]:
            """
            Starts a scan with the given data

            :param
            :return: (is_scan_started, refused_reason)
            """
            if DEBUG:
                print(f'[bold green] Calling /startscan with: {str(scan_data)} [/bold green]')

            rjson = self._make_request(method='post', url='/startscan', json=scan_data)
            is_accepeted = rjson.get('status', 'error') in self.SCAN_STARTED_STATUS
            self.is_scan_started = is_accepeted

            if is_accepeted:
                refused_reason = ''
            else:
                # refused
                refused_reason = self._get_reason(rjson)

            return is_accepeted, refused_reason

        def call_stopscan(self) -> Tuple[bool, AnyStr]:
            """
            Stop a scan with the given scan_id

            :param:
            :return: (is_scan_stopped, reason of error)
            """

            rjson = self._make_request(method='get', url=f'/stop/{str(self.scan_id)}')

            # Assume stopped when no response is given
            is_stopped = rjson.get('status', 'success') in self.SCAN_STOPPED_STATUS
            if is_stopped:
                errmsg = ''
            else:
                # error
                errmsg = self._get_reason(rjson)

            return is_stopped, errmsg

        def call_scanstatus(self) -> (str, str):
            """
            :param:
            :return: status, reason
            """
            rjson = self._make_request(method='get', url=f'/status/{str(self.scan_id)}')

            # get status and reason
            status = str(rjson.get('status', 'UNKNOWN')).strip().upper()
            reason = self._get_reason(rjson)

            return status, reason

        def call_getfindings(self) -> (bool, Dict, AnyStr):
            """
            Get findings from a scan
            :param:
            :return: (got the findings, findings, reason of error)
            """

            rjson = self._make_request(method='get', url=f'/getfindings/{str(self.scan_id)}')
            got_findings = rjson.get('status', 'ERROR') == 'success'

            if not got_findings:
                err_reason = self._get_reason(rjson)
            else:
                err_reason = ''

            return got_findings, rjson, err_reason

    def _get_scan_from_s3_and_settovar(self) -> NoReturn:
        """
            Get data about the scan we're going to run.
        :return:
        """
        self.scan_data = get_scan_data_from_s3_bucket()

    def _read_sensor_manifest_and_settovar(self) -> NoReturn:
        """
            Reads and parses manifest.ini of the sensor, to get some important fields like:
                * sensor_path
                * default_dir
                .
        :return:
        """
        if not os.path.exists(SensorControler.SENSOR_MANIFEST_PATH):
            raise FileNotFoundError(f'Sensor Manifest file not Found in {SensorControler.SENSOR_MANIFEST_PATH.__str__()}!')

        config = configparser.ConfigParser()
        config.read(SensorControler.SENSOR_MANIFEST_PATH)

        try:
            # Read sensor info section
            self.sensor_manifest = dict(config['sensor_info'])

            # Assert if all the mandatory keys are present (Dev)
            assert SensorControler.SENSOR_PATH_CNF_NAME in self.sensor_manifest, 'key not found'
            assert SensorControler.SENSOR_PORT_CNF_NAME in self.sensor_manifest, 'key not found'
            assert SensorControler.SENSOR_ENGINE_CNF_NAME in self.sensor_manifest, 'key not found'

            # Assert if the mandatory keys are present, if no, raise a KeyError
            for mandatory_key in [
                SensorControler.SENSOR_PATH_CNF_NAME,
                SensorControler.SENSOR_PORT_CNF_NAME,
                SensorControler.SENSOR_ENGINE_CNF_NAME]: # noqa
                if mandatory_key not in self.sensor_manifest:
                    raise KeyError(f'Key {mandatory_key} not found in {SensorControler.SENSOR_MANIFEST_PATH} !')

        except KeyError:
            raise BadManifestSyntax(f'Section \"sensor_info\" not found in {SensorControler.SENSOR_MANIFEST_PATH} !')

    def start_scan(self) -> Tuple[bool, AnyStr]:
        is_scan_started, refusal_msg = self.sensor_api.call_startscan(self.scan_data)
        return is_scan_started, refusal_msg

    def stop_scan(self) ->  Tuple[bool, AnyStr]: # noqa
        is_stopped, errmsg = self.sensor_api.call_stopscan()
        return is_stopped, errmsg

    def wait_scan(self) -> (bool, str):
        """
            Async if SensorMiddleare[gevent]
            Blocking otherwise.
            :return: is_report_available, errmsg
        """

        # WAIT ENGINE
#        _MAX_WAIT_ENGINE: Final = 35
#        _ENGINE_WAIT_TIME: Final = 2
#        wait_engine_time = 0
#        while self.check_if_engine_is_runnin and (not self.is_engine_process_running()):
#            if DEBUG:
#                print('[bold green] Waiting engine proc to init.. [/bold green]')
#
#            gevent_sleep(_ENGINE_WAIT_TIME)
#            wait_engine_time += _ENGINE_WAIT_TIME
#
#            if wait_engine_time >= _MAX_WAIT_ENGINE:
#                return False, "Engine not started yet"

        # WAIT SCAN
        STATUS_POOLING_TIME: Final[int] = secrets.choice(range(14, 31))
        MAX_ERROR: Final[int] = 40
        is_scanning = True
        errnow = 0
        errmsg = 'n/a'
        scan_status = ''

        # Wait before entering the loop (give the scan time to begin logically)
        gevent_sleep(STATUS_POOLING_TIME)
        while is_scanning:
            # Get new status from the API
            scan_status, errmsg = self.sensor_api.call_scanstatus()

            if scan_status not in ['SCANNING', 'FINISHED']:
                errnow += 1
            else:
                # Update if not error
                is_scanning = scan_status == 'SCANNING'
                errnow = 0

            if errnow >= MAX_ERROR:
                errmsg = f'Error waiting for scan: {errmsg}'
                break

            if DEBUG:
                print(f'[bold green] Got scan status: {scan_status} [/bold green]')

            gevent_sleep(STATUS_POOLING_TIME)

        return scan_status == 'FINISHED', errmsg

    def wait_report(self):
        """
            No need to be implemented.
        :return:
        """
        raise NotImplementedError

    def wait_engine(self) -> NoReturn:
        ST_POOLING_TIME: Final[int] = 2
        engine_status:   AnyStr     = self.sensor_api.call_enginestatus() # noqa

        if DEBUG:
            print(f'[bold green] Got first engine status: {engine_status}')

        # Wait for the engine to be ready
        while engine_status != self.ENGINE_READY_STATUS:
            # Check for errors
            if engine_status == self.ENGINE_ERROR_STATUS:
                raise RuntimeError('Engine hang with error!')

            gevent_sleep(ST_POOLING_TIME)
            engine_status = self.sensor_api.call_enginestatus()
            if DEBUG:
                print(f'[bold green] Got new status: {engine_status}')

    def get_report(self) -> Tuple[bool, Dict, AnyStr]:
        """
        Get the report of the scan
        :return: Dict with the report
        """
        return self.sensor_api.call_getfindings()
