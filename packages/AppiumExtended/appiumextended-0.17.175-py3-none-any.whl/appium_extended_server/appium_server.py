# coding: utf-8
import subprocess
import time
import logging
import requests


class AppiumServer:
    def __init__(self, server_ip: str = "127.0.0.1", server_port: int = 4723, logger: logging.Logger = None,
                 remote_log_level: str = 'error'):
        self.server_ip = server_ip
        self.server_port = server_port
        self.remote_log_level = remote_log_level
        self.logger = logger

    def start(self) -> bool:
        """
        Запускает Appium сервер согласно указанным параметрам.
        'appium server -ka 800 --log-level {self.log_level} --log logs/appium_log.txt --log-timestamp
        --use-plugins=device-farm,appium-dashboard -p {self.port} -a {self.ip} -pa /wd/hub
        --plugin-device-farm-platform=android --allow-insecure=adb_shell'
        """
        self.logger.info("Start Appium server")
        cmd = f'appium server -ka 800 --log-level {self.remote_log_level} --log logs/appium_log.txt --log-timestamp ' \
              f'--use-plugins=device-farm,appium-dashboard -p {self.server_port} -a {self.server_ip} -pa /wd/hub ' \
              f'--plugin-device-farm-platform=android --allow-insecure=adb_shell'
        try:
            subprocess.Popen(cmd, shell=True)  # don't use with
            return True
        except subprocess.CalledProcessError:
            self.logger.error("Error starting Appium server: subprocess.CalledProcessError")
            return False
        except OSError:
            self.logger.error("Error starting Appium server: OSError")
            return False

    def is_alive(self) -> bool:
        """
        Отправляет на сервер команду sessions и проверяет код ответа.
        Если 200 возвращает True, в ином случае False.
        """
        self.logger.info("Checking Appium server status")
        try:
            response = requests.get(f"http://{self.server_ip}:{self.server_port}/wd/hub/sessions", timeout=180)
            if response.status_code == 200:
                self.logger.info("Appium server ready")
                return True
            self.logger.warning(f"Appium server responded with status code {response.status_code}")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error checking Appium server status: {e}")
            return False

    def stop(self) -> bool:
        """
        Останавливает сервер
        Только при запуске на столе!
        """
        self.logger.info("Stop Appium server")
        try:
            cmd = 'taskkill /F /IM node.exe'
            subprocess.check_output(cmd, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def wait_until_alive(self, timeout: int = 600, poll: int = 2):
        """
        Ожидает пока сервер не вернет код 200
        """
        self.logger.info("Wait for Appium server")
        start_time = time.time()
        while time.time() < start_time + timeout:
            if self.is_alive():
                return True
            time.sleep(poll)
        return False
