# -*- coding: utf-8 -*-
from typing import AnyStr, NoReturn, Union, Dict
from abc import ABC, abstractmethod
from rich import print # noqa

import psutil
import os

DEBUG = os.getenv('DEBUG', False)


class Sensor(ABC):
    """
        Basic class defining the fundamental behavior of a EcoTrust Sensor.
    """

    @abstractmethod
    def start_scan(self) -> bool:
        """
            Call /startscan on Sensor API
        :return: true|false: Is the scan accepeted ?
        """
        pass

    @abstractmethod
    def stop_scan(self) -> bool:
        """
            Call /stop/<scan_id> on Sensor API
        :return: true|false: Is the scan stopped ?
        """
        pass

    @abstractmethod
    def wait_scan(self) -> bool:
        """
            Call /status/<scan_id> periodically on Sensor API to check if the Scan is finished and/or with error.
        :return: Is scan finished ? (without error)
        """
        pass

    @abstractmethod
    def wait_engine(self) -> NoReturn:
        """
            Normaly called when the container is started, to check if the engine is ready for Scans.
        :return:
        """
        pass

    # noinspection PyMethodMayBeStatic
    def is_engine_process_running(self, engine_proc_name: Union[AnyStr, None]) -> bool:
        """
            Checks if the engine process of the Sensor is still running in background.
        :return: True|False
        """
        current_proc_pid = os.getpid()

        for proc in psutil.process_iter():
            proc_pid  = proc.pid # noqa
            proc_name = proc.name()

            # Jump self (this python interpreter proc)
            if proc_pid == current_proc_pid:
                continue

            # Check if it matches
            if proc_name == engine_proc_name or engine_proc_name in proc_name:
                if DEBUG:
                    print(f'[bold green] Proc: {proc_name} mathes {engine_proc_name} [/bold green]') # noqa
                break

        else:
            # Iteration completed without breaking
            return False

        # Process found
        return True

    @abstractmethod
    def wait_report(self) -> NoReturn:
        """
            Wait json/xml/csv Scan report to be available to be sent.
        :return:
        """
        pass

    @abstractmethod
    def get_report(self) -> (bool, Dict):
        """
            Gets the CSV/JSON... report from the Sensor after the scan finishes (or should be called after it).
        :return:
        """
        pass
