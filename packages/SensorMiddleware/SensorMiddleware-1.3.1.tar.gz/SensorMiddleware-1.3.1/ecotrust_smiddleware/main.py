#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ecotrust_smiddleware.aws import upload_report_to_s3_bucket
from ecotrust_smiddleware.core import SensorControler
from ecotrust_smiddleware import VERSION
from rich import print # noqa
from typing import NoReturn, Union

import typer
import os
import sys
import signal
import datetime
import traceback

DEBUG = os.getenv('DEBUG', False)

GUNICORN_PID_PATH = '/var/run/gunicorn.pid'
GUNICORN_ACCESS_LOG = '/opt/access.log'
GUNICORN_ERROR_LOG = '/opt/error.log'
DEFAULT_ROOT_PID_PATH = '/var/run/root_process.pid'

HELP = f"""
    Sensor Middleware {VERSION} \n
    Ferramenta CLI para interagir e gerenciar os scans dos sensores EcoTrust. \n 
    
"""
app = typer.Typer(pretty_exceptions_show_locals=False, no_args_is_help=True, add_completion=False, help=HELP)
sensor_controler: Union[None, SensorControler] = None


def full_exit():
    """
        Kill main container process
    :return:
    """
    if os.path.exists(GUNICORN_PID_PATH):
        proc_pid_path = GUNICORN_PID_PATH
    else:
        proc_pid_path = DEFAULT_ROOT_PID_PATH

    try:
        with open(proc_pid_path, 'r', newline='\n') as pid:
            pid_str = pid.read()

            try:
                pid_int = int(pid_str)
            except ValueError:
                pass
            else:
                if not os.getenv('DEBUG', False):
                    os.kill(pid_int, signal.SIGKILL)

    except (FileNotFoundError, ValueError):
        pass

    sys.exit()


def crash_dump(format_exc: str, raw_except: str):
    """
        Dump logs and important data for post-analysis after a critical traceback and upload to S3 Bucket.
    :return:
    """
    # read gunicorn error log
    from aws import get_scan_data_from_s3_bucket

    try:
        scan_data = get_scan_data_from_s3_bucket()
    except: # noqa
        scan_data = {}

    scan_id = scan_data.get('scan_id', 0)
    try:
        gunicorn_err_message_fd = open(GUNICORN_ERROR_LOG, 'r')
        gunicorn_err: str = gunicorn_err_message_fd.read()
        gunicorn_err_message_fd.close()
    except FileNotFoundError:
        gunicorn_err = 'NOT FOUND'

    crash_dump_str = f"""
        ------------ SENSOR CRASH DUMP ---------------
        Date of failure: {datetime.datetime.now()}        
        Exception: 
         - format_exc():
            {format_exc}
         - str(exception):
            {raw_except}
            
        Gunicorn /opt/error.log: 
        {gunicorn_err}
    """

    print('[bold red] Uploaded crash dump to s3 bucket. [/bold red]')
    upload_report_to_s3_bucket(report=crash_dump_str, scan_id=scan_id, is_crash_dump=True)


class MiddlewareException(Exception):
    pass


@app.command(short_help="Run cloud scan, specify where the scan data is stored (envvar/...)")
def runscan() -> NoReturn:
    print('[bold green] Starting scan ... [/bold green]')
    scontrol = None
    try:
        scontrol = SensorControler()
    except Exception as e:
        print('[bold red] Error: [/bold red]', e)
        SensorControler.fail_scan(str(e))
        full_exit() # noqa

    print('[bold green] Waiting engine to start ... [/bold green]')
    try:
        scontrol.wait_engine()
    except Exception as e:
        print(f'[bold red] Error waiting for the engine, error: {str(e)} [/bold red]')
        SensorControler.fail_scan(str(e), scontrol)
        full_exit() # noqa

    # Todo: Retry ?
    try:
        is_scan_started, errmsg = scontrol.start_scan()
        if not is_scan_started:
            print(f'[bold red] Error: [/bold red] Scan could not be started. Reason: {errmsg}')
            SensorControler.fail_scan(str(errmsg), scontrol)
            full_exit() # noqa
    except Exception as e:
        print('[bold red] Error: [/bold red]', e)
        SensorControler.fail_scan(str(e), scontrol)
        full_exit() # noqa

    print('[bold green] Scan started')
    print('[bold green] Waiting for scan to finish ... [/bold green]')
    try:
        is_report_ready, errmsg = scontrol.wait_scan()
        if not is_report_ready:
            print(f'[bold red] Scan finished with error:  {errmsg}[/bold red]')
            SensorControler.fail_scan(str(errmsg), scontrol)
            full_exit() # noqa
    except Exception as e:
        print(f'[bold red] Error waiting for the scan, error: {str(e)} [/bold red]')
        SensorControler.fail_scan(str(e), scontrol)
        full_exit() # noqa

    print('[bold green] Scan finished successfully. [/bold green]')
    print('[bold green] Getting scan results ... [/bold green]')

    try:
        gotfindings, scan_report, errmsg = scontrol.get_report()
        if not gotfindings:
            print(f'[bold red] Error: [/bold red] Could not get scan findings. Error: {errmsg}')
            SensorControler.fail_scan(str(errmsg), scontrol)
            full_exit() # noqa
    except Exception as e:
        print(f'[bold red] Error getting findings, error: {str(e)} [/bold red]')
        SensorControler.fail_scan(str(e), scontrol)
        full_exit() # noqa

    # UPLOAD REPORT TO S3 BUCKET
    try:
        upload_report_to_s3_bucket(scan_report)
    except Exception as e:
        SensorControler.fail_scan(str(e), scontrol)
        full_exit() # noqa

    print('[bold green] Scan findings uploaded to s3 bucket. [/bold green]') # noqa
    SensorControler.finish_scan(scontroler=scontrol)
    full_exit() # noqa


@app.command(short_help="Stop the current running scan.")
def stopscan() -> NoReturn:
    raise NotImplementedError


@app.command(short_help="Show info about the CLI.")
def info():
    print(f'[bold green] Version: {VERSION}')
    print('Author: Pablo Skubert <pablo1920@protonmail.com>')


def scontroler_main():
    if not DEBUG:
        try:
            app()
        except MiddlewareException as middleware_error:
            raw_except = str(middleware_error)

            print(f'[bold red] Middleware error: {raw_except} [/bold red]')
            SensorControler.fail_scan(f'Critical middleware error') # noqa
            crash_dump(traceback.format_exc(), raw_except) # noqa
            full_exit() # noqa
    else:
        # Show full traceback
        app()

