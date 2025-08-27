"""
Корневой класс AppiumExtended. Обеспечивает соединение с сервером и инициализацию драйвера.
"""

# coding: utf-8
import logging
import json
import time

from appium import webdriver

from appium_extended_helpers.appium_helpers import AppiumHelpers
from appium_extended_helpers.appium_image import AppiumImage
from appium_extended_navigator.appium_navigator import AppiumNavigator
from appium_extended_terminal.terminal import Terminal
from appium_extended_terminal.aapt import Aapt
from appium_extended_terminal.adb import Adb
from appium.webdriver.webdriver import WebDriver

from appium_extended_terminal.transport import Transport


class AppiumBase:
    """
    Класс работы с Appium.
    Обеспечивает подключение к устройству
    """

    def __init__(self, logger: logging.Logger = None, log_level=logging.CRITICAL, secure_screenshot: bool = False):
        self.navigator = None
        self.options = None
        self.transport = None
        self.server_log_level: str = None
        self.server_port: int = None
        self.server_ip: str = None
        self.command_executor: str = None
        self.logger = logger
        self.driver: WebDriver = None
        self.terminal: Terminal = None
        self.image: AppiumImage = None
        self.helpers = None
        self.session_id: str = None
        self.capabilities = None
        self.keep_alive_server: bool = True
        self.aapt = Aapt()
        self.adb = Adb()
        self.logger.setLevel(log_level)
        self.secure_screenshot = secure_screenshot

    def connect(self,
                capabilities: dict = None,
                server_ip: str = '127.0.0.1',
                server_port: int = 4723,
                command_executor: str = "",
                server_log_level: str = 'error',
                remote: bool = False,
                keep_alive_server: bool = True,
                ssh_username: str = None,
                ssh_password: str = None,
                timeout_connect: float = 60.0,
                options=None) -> None:
        """
        Подключение к устройству через сервер Appium.

        Args:
            capabilities (dict): Словарь с возможностями для подключения к устройству.
            command_executor (str): example: 'http://{server_ip}:{str(server_port)}/wd/hub'
            server_ip (str, optional): IP-адрес сервера Appium. По умолчанию '127.0.0.1'.
            server_port (int, optional): Порт сервера Appium. По умолчанию 4723.
            server_log_level (str, optional): Уровень логирования сервера. По умолчанию 'error'.
            remote (bool, optional): Флаг для удаленного подключения. По умолчанию False.
            keep_alive_server (bool, optional): Флаг, оставлять ли сервер работающим после отключения
                (только при remote=False). По умолчанию True.

        Usages:
            app = AppiumExtended(logger=logger, log_level=logging.INFO)

            capabilities = {
                "platformName": "android",
                "appium:automationName": "uiautomator2",
                "appium:deviceName": app.adb.get_device_model(),
                "appium:udid": app.adb.get_device_uuid(),
                }

            app.connect(capabilities=capabilities,
                        server_ip='127.0.0.1',
                        server_port=4723,
                        server_log_level='info',
                        remote=False,
                        keep_alive_server=True)

            # ИЛИ ЕСЛИ СЕРВЕР УДАЛЕННЫЙ:
            app.connect(capabilities=capabilities,
                        server_ip='15.78.145.11',
                        server_port=4723,
                        server_log_level='error',
                        remote=True,
                        keep_alive_server=True)

        Raises:
            AppiumServerNotAliveException: Если сервер Appium не запущен или не отвечает.
            WebDriverException: Если не удается установить соединение с WebDriver.

        Returns:
            None: Функция не возвращает ничего, но инициализирует драйвер и другие компоненты.
        """
        if remote:
            DeprecationWarning("remote arg is deprecated")

        self.server_ip = server_ip
        self.server_port = server_port
        self.command_executor = command_executor
        self.server_log_level = server_log_level
        self.keep_alive_server = keep_alive_server
        self.capabilities = capabilities
        self.options = options
        self.logger.debug(
            f"connect(capabilities {capabilities}")

        url = command_executor
        if not any(url):
            url = f'http://{server_ip}:{str(server_port)}/wd/hub'
        self.logger.info(f"Подключение к серверу: {url}")
        self.driver = webdriver.Remote(command_executor=url,
                                       desired_capabilities=capabilities,
                                       keep_alive=True,
                                       options=options)
        # self.driver.update_settings(settings={'enableMultiWindows': True})
        self.session_id = self.driver.session_id
        # Инициализация объектов требующих драйвер
        if ssh_username is not None and ssh_password is not None:
            self.transport = Transport(server=self.server_ip, port=22, user=ssh_username, password=ssh_password)
        self.terminal = Terminal(base=self)
        self.helpers = AppiumHelpers(base=self)
        self.image = self.helpers
        self.navigator = AppiumNavigator(base=self)
        app_capabilities = json.dumps(capabilities)
        self.logger.info(f'Подключение установлено с  параметрами: {str(app_capabilities)}, {url}')
        self.logger.info(f'Сессия №: {self.driver.session_id}')

    def disconnect(self) -> None:
        """
        Отключение от устройства.
        А также остановка сервера Appium, если флаг `keep_alive_server` установлен в False.

        Usages:
            app.disconnect()

        Raises:
            AppiumServerNotAliveException: Если сервер Appium не запущен или не отвечает.
            WebDriverException: Если не удается завершить соединение с WebDriver.

        Returns:
            None: Функция не возвращает ничего, но завершает текущую сессию и останавливает сервер, если необходимо.
        """
        if self.driver:
            self.logger.debug(f"Отключение от сессии №: {self.driver.session_id}")
            try:
                self.driver.quit()
            except Exception as error:
                self.logger.error(error)
            finally:
                self.driver = None

    def is_running(self) -> bool:
        """
        Проверяет, запущен ли сервер Appium и активна ли текущая сессия.

        Usages:
            app.is_running()

        Raises:
            WebDriverException: Если не удается проверить статус сервера или сессии.

        Returns:
            bool: Возвращает True, если сервер и сессия активны, иначе False.
        """
        status = self.driver.get_status()
        print(f'{status=}')
        if 'build' in status:
            return True
        return False

    def reconnect(self):
        self.logger.error("RECONNECT")
        self.disconnect()
        self.connect(capabilities=self.capabilities,
                     server_ip=self.server_ip,
                     server_port=self.server_port,
                     command_executor=self.command_executor,
                     server_log_level=self.server_log_level,
                     keep_alive_server=self.keep_alive_server)
