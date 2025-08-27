# coding: utf-8
import logging

from appium.webdriver import WebElement

from appium_extended_web_element.web_element_get import WebElementGet
from appium_extended_helpers import helpers_decorators
from appium_extended_utils.utils import find_coordinates_by_vector


class WebElementTerminalActions(WebElementGet):
    """
    Класс для выполнения adb-действий с элементами.
    Наследуется от класса WebElementGet.
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

    def _terminal_tap(self,
                      decorator_args: dict = None,
                      wait: bool = False) -> bool:
        """
        Выполняет нажатие на элемент с помощью adb.

        Аргументы:
            decorator_args (dict): Дополнительные аргументы для использования в декораторе.
                timeout_window (int): Время ожидания нового окна (умножается на количество попыток).
                tries (int): Количество попыток нажатия (по умолчанию 3).
            wait (bool): Флаг, указывающий, нужно ли ожидать изменения окна.

        Возвращает:
            bool: True, если нажатие выполнено успешно; False в противном случае.
        """
        if wait:
            # Если нужно ожидать изменения окна.
            if not decorator_args:
                decorator_args = {"timeout_window": 5,
                                  "tries": 5}
            return self._terminal_tap_to_element_and_wait(decorator_args=decorator_args)
        # Если не нужно ожидать изменения окна.
        return self._terminal_tap_to_element()

    def _terminal_tap_to_element(self) -> bool:
        return self.__terminal_tap()

    @helpers_decorators.wait_for_window_change()
    def _terminal_tap_to_element_and_wait(self,
                                          decorator_args: dict = None) -> bool:
        return self.__terminal_tap()

    def __terminal_tap(self) -> bool:
        """
        Выполняет нажатие на элемент с помощью adb.

        Возвращает:
            bool: True, если нажатие выполнено успешно, False в противном случае.
        """
        try:
            x, y = self._get_center()
            return self.terminal.tap(x=x, y=y)
        except Exception as e:
            return False

    def _terminal_swipe(self,
                        root,
                        element: WebElement = None,
                        x: int = None,
                        y: int = None,
                        direction: int = None,
                        distance: int = None,
                        duration: int = 1) -> bool:
        """
        Выполняет прокрутку с помощью adb.

        Аргументы:
            root: Корневой элемент на странице.
            element (WebElement): Целевой элемент.
            x (int): Координата X целевой позиции прокрутки.
            y (int): Координата Y целевой позиции прокрутки.
            direction (int): Направление прокрутки в градусах (от 0 до 360).
            distance (int): Расстояние прокрутки в пикселях.
            duration (int): Длительность прокрутки в секундах.

        Возвращает:
            bool: True, если прокрутка выполнена успешно; False в противном случае.
        """
        # Проверка наличия входных данных
        if element is None and (x is None or y is None) and (direction is None or distance is None):
            return False

        # Получение координат центра начальной позиции прокрутки
        x1, y1 = self._get_center()
        x2, y2 = self._get_center()

        # Расчет целевой позиции прокрутки на основе предоставленных входных данных
        if element is not None:
            # Если предоставлен локатор, получаем координаты центра целевого элемента
            x2, y2 = self._get_center(element)
        elif x is not None and y is not None:
            # Если предоставлены координаты x и y, используем их в качестве целевой позиции прокрутки
            x2, y2 = x, y
        elif direction is not None and distance is not None:
            # Если предоставлены направление и расстояние, вычисляем целевую позицию прокрутки
            window_size = self.terminal.get_screen_resolution()
            width = window_size[0]
            height = window_size[1]
            x2, y2 = find_coordinates_by_vector(width=width, height=height,
                                                direction=direction, distance=distance,
                                                start_x=x1, start_y=y1)

        # Выполнение adb-команды прокрутки с заданными координатами и длительностью
        self.terminal.swipe(start_x=str(x1),
                            start_y=str(y1),
                            end_x=str(x2),
                            end_y=str(y2),
                            duration=str(duration * 1000))

        return True
