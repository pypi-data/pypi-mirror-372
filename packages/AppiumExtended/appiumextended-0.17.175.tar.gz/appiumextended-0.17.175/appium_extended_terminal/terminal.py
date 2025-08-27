import inspect
import logging
import base64
import os
import re
import subprocess
import sys
import time
import traceback
from typing import Dict, Any, Union, Tuple

from selenium.common import NoSuchDriverException, InvalidSessionIdException

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath( __file__))))  # The sys.path.append line adds the
# parent directory of the tests directory to the Python module search path, allowing you to import modules from the
# root folder.
from appium_extended_helpers.helpers_decorators import log_debug


class Terminal:
    base = None
    transport = None
    driver = None
    logger = None

    def __init__(self, base, logger: logging.Logger = None, log_level: int = logging.INFO, log_path: str = ''):
        self.base = base
        self.transport = base.transport
        self.driver = base.driver
        self.logger = base.logger
        if logger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(log_level)
        if bool(log_path):
            if not log_path.endswith('.log'):
                log_path = log_path + '.log'
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def __del__(self):
        if self.transport is not None:
            self.transport.ssh.close()

    @log_debug()
    def adb_shell(self, command: str, args: str = "", tries: int = 3) -> Any:
        for _ in range(tries):
            try:
                return self.driver.execute_script("mobile: shell", {'command': command, 'args': [args]})
            except NoSuchDriverException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()
            except InvalidSessionIdException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()
            except KeyError as e:
                self.logger.error(e)
                traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                self.logger.error(traceback_info)

    @log_debug()
    def push(self, source_path: str, remote_server_path: str, filename: str, destination: str, udid: str) -> bool:
        """
        Копирует файл или директорию на подключенное устройство через Appium сервер.

        Аргументы:
            driver: Appium WebDriver объект.
            source (str): Путь к копируемому файлу или директории на локальной машине.
            destination (str): Путь назначения на устройстве.

        Возвращает:
            bool: True, если файл или директория были успешно скопированы, False в противном случае.
        """
        if self.transport is None:
            raise AssertionError(
                f"Метод {inspect.currentframe().f_code.co_name} ssh_username, ssh_password в методе connect()")
        try:
            source_file_path = os.path.join(source_path, filename)
            remote_file_path = os.path.join(remote_server_path, filename)
            destination_file_path = f"{destination}/{filename}"
            self.transport.scp.put(files=source_file_path, remote_path=remote_file_path)
            stdin, stdout, stderr = self.transport.ssh.exec_command(
                f'adb -s {udid} push {remote_file_path} {destination_file_path}')
            stdout_exit_status = stdout.channel.recv_exit_status()
            lines = stdout.readlines()
            output = ''.join(lines)
            if stdout_exit_status != 0:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} {output=}")
                return False
            self.logger.debug(f"{inspect.currentframe().f_code.co_name} {output=}")
            return True
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except IOError as e:
            self.logger.error("appium_extended_terminal.push()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def pull(self, source: str, destination: str) -> bool:
        """Извлекает файл с устройства по пути `source` и сохраняет его по пути `destination` на компьютере.

        Аргументы:
            source (str): Путь к файлу на устройстве.
            destination (str): Путь, по которому файл должен быть сохранен на компьютере.

        Возвращает:
            bool: True, если файл успешно извлечен и сохранен, False в противном случае.
        """
        try:
            file_contents_base64 = self.driver.assert_extension_exists('mobile: pullFile'). \
                execute_script('mobile: pullFile', {'remotePath': source})
            if not file_contents_base64:
                return False
            decoded_contents = base64.b64decode(file_contents_base64)
            with open(destination, 'wb') as file:
                file.write(decoded_contents)
            return True
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except IOError as e:
            self.logger.error("appium_extended_terminal.pull")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def start_activity(self, package: str, activity: str) -> bool:
        """
        Запускает активити на подключенном устройстве.

        Аргументы:
            package (str): Название пакета.
            activity (str): Название запускаемой активити.

        Возвращает:
            bool: True, если активность была успешно запущена, False в противном случае.
        """
        try:
            self.adb_shell(command="am", args=f"start -n {package}/{activity}")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.start_activity()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def get_current_app_package(self) -> Union[str, None]:
        """
        Получает пакет текущего запущенного приложения на устройстве с помощью ADB.

        Возвращает:
            str: Название пакета текущего запущенного приложения, либо None, если произошла ошибка.
        """
        try:
            result = self.adb_shell(command="dumpsys", args="window windows")
            lines = result.split('\n')
            for line in lines:
                if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                    matches = re.search(r'(([A-Za-z]{1}[A-Za-z\d_]*\.)+([A-Za-z][A-Za-z\d_]*)/)', line)
                    if matches:
                        return matches.group(1)[:-1]  # removing trailing slash
            return None
        except KeyError as e:
            # Логируем ошибку, если возникло исключение
            self.logger.error("appium_extended_terminal.get_current_app_package()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return None

    @log_debug()
    def close_app(self, package: str) -> bool:
        """
        Принудительно останавливает указанный пакет с помощью ADB.

        Аргументы:
            package (str): Название пакета приложения для закрытия.

        Возвращает:
            bool: True, если приложение успешно закрыто, False в противном случае.
        """
        try:
            self.adb_shell(command="am", args=f"force-stop {package}")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.close_app()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def reboot_app(self, package: str, activity: str) -> bool:
        """
        Перезапускает приложение, закрывая его и затем запуская указанную активность.

        Аргументы:
            package (str): Название пакета приложения.
            activity (str): Название активности для запуска.

        Возвращает:
            bool: True, если перезапуск приложения выполнен успешно, False в противном случае.
        """
        # Закрытие приложения
        if not self.close_app(package=package):
            return False

        # Запуск указанной активности
        if not self.start_activity(package=package, activity=activity):
            return False

        return True

    @log_debug()
    def install_app(self, source: str, remote_server_path: str, filename: str, udid: str) -> bool:
        """
        Устанавливает указанный пакет с помощью Appium.
        Дублирует команду драйвера. Добавлено для интуитивности.

        Аргументы:
            package (str): Название пакета приложения для установки.

        Возвращает:
            bool: True, если приложение успешно удалено, False в противном случае.
        """
        if self.transport is None:
            raise AssertionError(
                f"Метод {inspect.currentframe().f_code.co_name} нельзя использовать, если не переданы server, port, username, password для обеспечения ssh соединения")
        try:
            source_filepath = os.path.join(source, filename)
            destination_filepath = os.path.join(remote_server_path, filename)
            self.transport.scp.put(files=source_filepath, remote_path=destination_filepath)
            stdin, stdout, stderr = self.transport.ssh.exec_command(
                f'adb -s {udid} install -r {destination_filepath}')
            stdout_exit_status = stdout.channel.recv_exit_status()
            lines = stdout.readlines()
            output = ''.join(lines)
            if stdout_exit_status != 0:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} {output=}")
                return False
            self.logger.debug(f"{inspect.currentframe().f_code.co_name} {output=}")
            return True
        except IOError as e:
            self.logger.error("appium_extended_terminal.push()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def is_app_installed(self, package) -> bool:
        """
        Проверяет, установлен ли пакет.
        """
        self.logger.debug(f"is_app_installed() < {package=}")

        try:
            result = self.adb_shell(command="pm", args="list packages")
            # Фильтруем пакеты
            if any([line.strip().endswith(package) for line in result.splitlines()]):
                self.logger.debug("is_app_installed() > True")
                return True
            self.logger.debug("is_app_installed() > False")
            return False
        except KeyError as e:
            self.logger.error("appium_extended_terminal.is_app_installed() > False")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def uninstall_app(self, package: str) -> bool:
        """
        Удаляет указанный пакет с помощью ADB.

        Аргументы:
            package (str): Название пакета приложения для удаления.

        Возвращает:
            bool: True, если приложение успешно удалено, False в противном случае.
        """
        try:
            self.driver.remove_app(app_id=package)
            return True
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except KeyError as e:
            self.logger.error("appium_extended_terminal.uninstall_app()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def press_home(self) -> bool:
        """
        Отправляет событие нажатия кнопки Home на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.input_keycode(keycode="KEYCODE_HOME")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.press_home()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def press_back(self) -> bool:
        """
        Отправляет событие нажатия кнопки Back на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.input_keycode(keycode="KEYCODE_BACK")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.press_back()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def press_menu(self) -> bool:
        """
        Отправляет событие нажатия кнопки Menu на устройство с помощью ADB.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.input_keycode(keycode="KEYCODE_MENU")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.press_menu()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def input_keycode_num_(self, num: int) -> bool:
        """
        Отправляет событие нажатия клавиши с числовым значением на устройство с помощью ADB.
        Допустимые значения: 0-9, ADD, COMMA, DIVIDE, DOT, ENTER, EQUALS

        Аргументы:
            num (int): Числовое значение клавиши для нажатия.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.adb_shell(command="input", args=f"keyevent KEYCODE_NUMPAD_{num}")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.input_keycode_num_()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def input_keycode(self, keycode: str) -> bool:
        """
        Вводит указанный код клавиши на устройстве с помощью ADB.

        Аргументы:
            keycode (str): Код клавиши для ввода.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.adb_shell(command="input", args=f"keyevent {keycode}")
            return True
        except KeyError as e:
            self.logger.error("appium_extended_terminal.input_keycode()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def input_by_virtual_keyboard(self, key: str, keyboard: Dict[str, tuple]) -> bool:
        """
        Вводит строку символов с помощью виртуальной клавиатуры.

        Аргументы:
            key (str): Строка символов для ввода.
            keyboard (dict): Словарь с маппингом символов на координаты нажатий.

        Возвращает:
            bool: True, если ввод выполнен успешно, False в противном случае.
        """
        try:
            for char in key:
                # Вызываем функцию tap с координатами, соответствующими символу char
                self.tap(x=keyboard[str(char)][0], y=keyboard[str(char)][1])
            return True
        except KeyError as e:
            # Логируем ошибку и возвращаем False в случае возникновения исключения
            self.logger.error("appium_extended_terminal.input_by_virtual_keyboard")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def input_text(self, text: str) -> bool:
        """
        Вводит указанный текст на устройстве с помощью ADB.

        Аргументы:
            text (str): Текст для ввода.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.adb_shell(command="input", args=f"text {text}")
            return True
        except KeyError as e:
            # Логируем ошибку, если возникло исключение
            self.logger.error("appium_extended_terminal.input_text()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def tap(self, x: int, y: int) -> bool:
        """
        Выполняет нажатие на указанные координаты на устройстве с помощью ADB.

        Аргументы:
            x: Координата X для нажатия.
            y: Координата Y для нажатия.

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.adb_shell(command="input", args=f"tap {str(x)} {str(y)}")
            return True
        except KeyError as e:
            # Логируем ошибку, если возникло исключение
            self.logger.error("appium_extended_terminal.tap()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def swipe(self, start_x: Union[str, int], start_y: Union[str, int],
              end_x: Union[str, int], end_y: Union[str, int], duration: int = 300) -> bool:
        """
        Выполняет свайп (перетаскивание) с одной точки на экране в другую на устройстве с помощью ADB.

        Аргументы:
            start_x: Координата X начальной точки свайпа.
            start_y: Координата Y начальной точки свайпа.
            end_x: Координата X конечной точки свайпа.
            end_y: Координата Y конечной точки свайпа.
            duration (int): Длительность свайпа в миллисекундах (по умолчанию 300).

        Возвращает:
            bool: True, если команда была успешно выполнена, False в противном случае.
        """
        try:
            self.adb_shell(command="input",
                           args=f"swipe {str(start_x)} {str(start_y)} {str(end_x)} {str(end_y)} {str(duration)}")
            return True
        except KeyError as e:
            # Логируем ошибку, если возникло исключение
            self.logger.error("appium_extended_terminal.swipe()")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def swipe_right_to_left(self, duration: int = 300) -> bool:
        window_size = self.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        return self.swipe(start_x=right,
                          start_y=height // 2,
                          end_x=left,
                          end_y=height // 2,
                          duration=duration)

    @log_debug()
    def swipe_left_to_right(self, duration: int = 300) -> bool:
        window_size = self.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        return self.swipe(start_x=left,
                          start_y=height // 2,
                          end_x=right,
                          end_y=height // 2,
                          duration=duration)

    @log_debug()
    def swipe_top_to_bottom(self, duration: int = 300) -> bool:
        window_size = self.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        return self.swipe(start_x=top,
                          start_y=height // 2,
                          end_x=bottom,
                          end_y=height // 2,
                          duration=duration)

    @log_debug()
    def swipe_bottom_to_top(self, duration: int = 300) -> bool:
        window_size = self.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        return self.swipe(start_x=bottom,
                          start_y=height // 2,
                          end_x=top,
                          end_y=height // 2,
                          duration=duration)

    @log_debug()
    def check_vpn(self, ip_address: str = '') -> bool:
        """
        Проверяет, активно ли VPN-соединение на устройстве с помощью ADB.

        Аргументы:
            ip (str): IP-адрес для проверки VPN-соединения. Если не указан, используется значение из конфигурации.

        Возвращает:
            bool: True, если VPN-соединение активно, False в противном случае.
        """
        try:
            output = self.adb_shell(command="netstat", args="")
            lines = output.split('\n')
            for line in lines:
                if ip_address in line and "ESTABLISHED" in line:
                    self.logger.debug("check_VPN() True")
                    return True
            self.logger.debug("check_VPN() False")
            return False
        except KeyError as e:
            # Логируем ошибку, если возникло исключение
            self.logger.error("appium_extended_terminal.check_VPN")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def stop_logcat(self) -> bool:
        """
        Останавливает выполнение logcat на устройстве с помощью ADB.

        Возвращает:
            bool: True, если выполнение logcat остановлено успешно, False в противном случае.
        """
        # Получаем список выполняющихся процессов logcat
        try:
            process_list = self.adb_shell(command="ps", args="")
        except KeyError as e:
            self.logger.error("appium_extended_terminal.stop_logcat")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        # Проходим по списку процессов и отправляем каждому сигнал SIGINT
        for process in process_list.splitlines():
            if "logcat" in process:
                pid = process.split()[1]
                try:
                    self.adb_shell(command="kill", args=f"-SIGINT {str(pid)}")
                except KeyError as e:
                    self.logger.error("appium_extended_terminal.stop_logcat")
                    self.logger.error(e)
                    traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
                    self.logger.error(traceback_info)
                    return False
        return True

    @log_debug()
    def know_pid(self, name: str) -> Union[int, None]:
        """
        Находит Process ID (PID) процесса по его имени, используя adb shell ps.

        Параметры:
            name (str): Имя процесса, PID которого нужно найти.

        Возвращает:
            Union[int, None]: PID процесса, если он найден, или None, если процесс не найден.
        """
        # Получение списка всех процессов с помощью adb shell ps
        processes = self.adb_shell(command="ps")
        if name not in processes:
            self.logger.error("know_pid() [Процесс не обнаружен]")
            return None
        # Разделение вывода на строки и удаление пустых строк
        lines = processes.strip().split('\n')
        # Проход по каждой строке вывода, начиная с 2-й строки, игнорируя заголовки
        for line in lines[1:]:
            # Разделение строки на столбцы по пробелам
            columns = line.split()
            # Проверка, что строка имеет не менее 9 столбцов
            if len(columns) >= 9:
                # Извлечение PID и имени процесса из соответствующих столбцов
                pid, process_name = columns[1], columns[8]
                # Сравнение имени процесса с искомым именем
                if name == process_name:
                    self.logger.debug(f"know_pid() > {str(pid)}")
                    return int(pid)
        self.logger.error("know_pid() [Процесс не обнаружен]")
        # Возврат None, если процесс с заданным именем не найден
        return None

    @log_debug()
    def is_process_exist(self, name) -> bool:
        """
        Проверяет, запущен ли процесс, используя adb shell ps.

        Параметры:
            name (str): Имя процесса.

        Возвращает:
            bool: True если процесс с указанным именем существует, False в ином случае.
        """
        # Получение списка всех процессов с помощью adb shell ps
        processes = self.adb_shell(command="ps")
        if name not in processes:
            self.logger.debug("is_process_exist() > False")
            return False
        # Разделение вывода на строки и удаление пустых строк
        lines = processes.strip().split('\n')
        # Проход по каждой строке вывода, начиная с 2-й строки, игнорируя заголовки
        for line in lines[1:]:
            # Разделение строки на столбцы по пробелам
            columns = line.split()
            # Проверка, что строка имеет не менее 9 столбцов
            if len(columns) >= 9:
                # Извлечение PID и имени процесса из соответствующих столбцов
                _, process_name = columns[1], columns[8]
                # Сравнение имени процесса с искомым именем
                if name == process_name:
                    self.logger.debug("is_process_exist() > True")
                    return True
        self.logger.debug("is_process_exist() > False")
        # Возврат None, если процесс с заданным именем не найден
        return False

    @log_debug()
    def run_background_process(self, command: str, args: str = "", process: str = "") -> bool:
        """
        Запускает процесс в фоновом режиме на устройстве Android.

        Аргументы:
            command (str): Команда для выполнения на устройстве.
            process (str): Название процесса, который будет запущен. По умолчанию "".
            Если process == "", то не будет проверяться его запуск в системе.

        Возвращает:
            bool: True, если процесс был успешно запущен, False в противном случае.
        """
        self.logger.debug(f"run_background_process() < {command=}")

        try:
            self.adb_shell(command=command, args=args + " nohup > /dev/null 2>&1 &")
            if process != "":
                time.sleep(1)
                if not self.is_process_exist(name=process):
                    return False
            return True
        except KeyError as e:
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False

    @log_debug()
    def kill_by_pid(self, pid: int) -> bool:
        """
        Отправляет сигнал SIGINT для остановки процесса по указанному идентификатору PID с помощью ADB.

        Аргументы:
            pid (str): Идентификатор PID процесса для остановки.

        Возвращает:
            bool: True, если процесс успешно остановлен, False в противном случае.
        """
        try:
            self.adb_shell(command="kill", args=f"-s SIGINT {str(pid)}")
        except KeyError as e:
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def kill_by_name(self, name: str) -> bool:
        """
        Останавливает все процессы с указанным именем на устройстве с помощью ADB.

        Аргументы:
            name (str): Имя процесса для остановки.

        Возвращает:
            bool: True, если все процессы успешно остановлены, False в противном случае.
        """
        self.logger.debug(f"kill_by_name() < {name=}")
        try:
            self.adb_shell(command="pkill", args=f"-l SIGINT {str(name)}")
        except KeyError as e:
            self.logger.error("kill_by_name() > False")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        self.logger.debug("kill_by_name() > True")
        return True

    @log_debug()
    def kill_all(self, name: str) -> bool:
        """
        Останавливает все процессы, соответствующие указанному имени, на устройстве с помощью ADB.

        Аргументы:
            name (str): Имя процесса или шаблон имени для остановки.

        Возвращает:
            bool: True, если все процессы успешно остановлены, False в противном случае.
        """
        try:
            self.adb_shell(command="pkill", args=f"-f {str(name)}")
        except KeyError as e:
            self.logger.error("appium_extended_terminal.kill_all")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def delete_files_from_internal_storage(self, path) -> bool:
        """
        Удаляет файлы из внутреннего хранилища устройства с помощью ADB.

        Аргументы:
            path (str): Путь к папке с файлами для удаления.

        Возвращает:
            bool: True, если файлы успешно удалены, False в противном случае.
        """
        try:
            self.adb_shell(command="rm", args=f"-rf {path}*")
        except KeyError as e:
            self.logger.error("appium_extended_terminal.delete_files_from_internal_storage")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def delete_file_from_internal_storage(self, path: str, filename: str) -> bool:
        """
        Удаляет файл из внутреннего хранилища устройства с помощью ADB.

        Аргументы:
            path (str): Путь к папке с файлами для удаления.
            filename (str): Наименование файла.

        Возвращает:
            bool: True, если файл успешно удален, False в противном случае.
        """
        try:
            if path.endswith('/'):
                path = path[:-1]
            self.adb_shell(command="rm", args=f"-rf {path}/{filename}")
        except KeyError as e:
            self.logger.error("appium_extended_terminal.delete_file_from_internal_storage")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def record_video(self, **options: Any) -> bool:
        """
        Начинает запись видео. 3 минуты максимум.

        Аргументы:
            filename (str): Имя файла для сохранения видео.

        Возвращает:
            bool: True, если запись видео успешно начата, False в противном случае.
        """
        try:
            self.driver.start_recording_screen(**options)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except KeyError as e:
            self.logger.error("appium_extended_terminal.record_video")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def stop_video(self, **options: Any) -> Union[bytes, None]:
        """
        Останавливает запись видео. Возвращает Base64 bytes

        Возвращает:
            bool: True, если запись видео успешно остановлена, False в противном случае.
        """
        try:
            str_based64_video = self.driver.stop_recording_screen(**options)
            # Декодируем base64-кодированную строку в бинарные данные видео
            return base64.b64decode(str_based64_video)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except KeyError as e:
            self.logger.error("appium_extended_terminal.stop_video")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return None

    @log_debug()
    def reboot(self) -> bool:
        """
        Перезагружает устройство с помощью ADB.

        Возвращает:
            bool: True, если перезагрузка успешно запущена, False в противном случае.
        """
        try:
            self.adb_shell(command='reboot')
        except KeyError as e:
            self.logger.error("appium_extended_terminal.reboot")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)
            return False
        return True

    @log_debug()
    def get_screen_resolution(self) -> Union[Tuple[int, int], None]:
        """
        Возвращает разрешение экрана устройства с помощью ADB.

        Возвращает:
            tuple[int, int] or None: Кортеж с шириной и высотой экрана в пикселях, или None в случае ошибки.
        """
        try:
            output = self.adb_shell(command='wm', args='size')
            if "Physical size" in output:
                resolution_str = output.split(":")[1].strip()
                width, height = resolution_str.split("x")
                return int(width), int(height)
        except KeyError as e:
            self.logger.error("appium_extended_terminal.get_screen_resolution")
            self.logger.error(e)
            traceback_info = "".join(traceback.format_tb(sys.exc_info()[2]))
            self.logger.error(traceback_info)

    @log_debug()
    def past_text(self, text: str, tries: int = 3) -> None:
        """
        Помещает в буфер обмена заданный текст, затем вставляет его
        """
        for _ in range(tries):
            try:
                self.driver.set_clipboard_text(text=text)
                self.input_keycode('279')
                return
            except NoSuchDriverException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()
            except InvalidSessionIdException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()

    @log_debug()
    def get_prop(self) -> dict:
        """
        Возвращает словарь атрибутов и их значений полученных командой getprop
        """
        raw_properties = self.adb_shell(command="getprop")

        # Разбиваем входную строку на строки
        lines = raw_properties.replace("\r", "").strip().split("\n")

        # Создаем пустой словарь для хранения пар ключ-значение
        result_dict = {}

        # Обрабатываем каждую строку
        for line in lines:
            try:
                # Разбиваем строку на две части, используя первое вхождение ":"
                key, value = line.strip().split(":", 1)

                # Убираем квадратные скобки вокруг ключа и значения
                key = key.strip()[1:-1]
                value = value.strip()[1:-1]
                # Добавляем пару ключ-значение в словарь
                result_dict[key] = value
            except ValueError:
                continue

        return result_dict

    def get_prop_hardware(self) -> str:
        """
        Возвращает значение атрибута 'ro.boot.hardware'
        """
        return self.get_prop()['ro.boot.hardware']

    def get_prop_model(self) -> str:
        """
        Возвращает значение атрибута 'ro.product.model'
        """
        return self.get_prop()['ro.product.model']

    def get_prop_serial(self) -> str:
        """
        Возвращает значение атрибута 'ro.serialno'
        """
        return self.get_prop()['ro.serialno']

    def get_prop_build(self) -> str:
        """
        Возвращает значение атрибута 'ro.build.description'
        """
        return self.get_prop()['ro.build.description']

    def get_prop_device(self) -> str:
        """
        Возвращает значение атрибута 'ro.product.device'
        """
        return self.get_prop()['ro.product.device']

    def get_prop_uin(self) -> str:
        """
        Вовзращает УИН устройства
        """
        return self.get_prop()['sys.atol.uin']

    def get_packages(self) -> list:
        """
        Возвращает список пакетов установленных на устройство
        """
        # Get the output from adb_shell command
        output = self.adb_shell(command='pm', args='list packages')

        # Split the output by newline to get each line separately
        lines = output.strip().split('\n')

        # Extract package names from each line and return as a list
        packages = [line.split(':')[-1].replace('\r', '') for line in lines]
        return packages

    def get_package_path(self, package: str) -> str:
        """
        Возвращает путь к пакету на устройстве.
        Args:
            package (str): Наименование пакета
        Returns:
            str: путь к пакету на устройстве
        """
        return self.adb_shell(command='pm', args=f'path {package}'). \
            replace('package:', ''). \
            replace('\r', ''). \
            replace('\n', '')

    def pull_package(self, package: str, path: str = '', filename: str = 'temp.apk'):
        """
        Скачивает с устройства указанный пакет.
        Args:
            package (str): Наименование пакета
            path (str): Путь к папке сохранения пакета на ПК
            filename (str): Имя файла сохраняемого на ПК
        """
        package_path = self.get_package_path(package=package)
        if not filename.endswith('.apk'):
            filename = f"{filename}.apk"
        self.pull(source=package_path, destination=os.path.join(path, filename))

    def get_package_manifest(self, package: str) -> dict:
        """
        Получает манифест с пакета на устройстве и возвращает его преобразованный в словарь.
        Args:
            package (str): наименование пакета
        Returns:
            dict: манифест в виде словаря
        """
        if not os.path.exists("test"):
            os.makedirs(name='test')

        self.pull_package(package=package, path="test",
                          filename="temp.apk")

        command = ["aapt", "dump", "badging", os.path.join("test", "temp.apk")]
        try:
            output: str = str(subprocess.check_output(command)).strip()
        except subprocess.CalledProcessError as error:
            # self.logger.error(f"get_package_manifest ошибка получения манифеста: {error}")
            return {}
        # Убираем лишние символы
        output = output.replace('\\r\\n', ' ').replace('b"', '').replace('"', '').replace(":'", ": '")

        # Строим список
        list_of_elements = output.split()
        result = {}
        current_key = None

        for element in list_of_elements:
            if element.endswith(':'):
                result[element] = []
                current_key = element
                continue
            result[current_key].append(element.replace("'", ""))

        os.remove(os.path.join('test', 'temp.apk'))

        return result
