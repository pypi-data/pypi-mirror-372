# coding: utf-8
import logging
from typing import Union, Tuple, Dict, List, Optional

from appium.webdriver import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput

from appium_extended_exceptions.appium_extended_exceptions import WebElementExtendedError
from appium_extended_web_element.web_element_get import WebElementGet

from appium_extended_helpers.helpers_decorators import wait_for_window_change
from appium_extended_utils.utils import find_coordinates_by_vector


class WebElementTap(WebElementGet):
    """
    Класс для выполнения действий нажатия (Tap), а также нажатия и перемещения с использованием элементов веб-страницы.
    Наследуется от класса WebElementGet.
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

    def _tap(self,
             positions: List[Tuple[int, int]],
             duration: int = 0,
             decorator_args: dict = None,
             wait: bool = False) -> bool:
        """
        Выполняет нажатие на указанные координаты.

        Аргументы:
            positions (List[Tuple[int, int]]): Список координат X и Y для нажатия.
            duration (int): Длительность нажатия в миллисекундах.
            decorator_args (dict): Дополнительные аргументы для использования в декораторе.
                    Например:
                        decorator_args = {"timeout_window": 5,
                                          "tries": 5}, где
                        timeout_window (int): время ожидания изменения окна
                        tries (int): количество попыток для изменения окна
            wait (bool): Флаг, указывающий, нужно ли ожидать результата после нажатия.

        Возвращает:
            bool: True, если нажатие выполнено успешно; False в противном случае.
        """

        if wait:
            # Если нужно ожидать результата после нажатия

            if not decorator_args:
                # Декоратор по умолчанию
                decorator_args = {"timeout_window": 5,
                                  "tries": 5}

            return self._tap_to_element_and_wait(positions=positions, duration=duration, decorator_args=decorator_args)
        else:
            # Если не нужно ожидать результата после нажатия
            return self._tap_to_element(positions=positions, duration=duration)

    @wait_for_window_change()
    def _tap_to_element_and_wait(self,
                                 positions: List[Tuple[int, int]],
                                 duration: int = 0,
                                 decorator_args: dict = None, ):
        return self.__tap(positions=positions, duration=duration)

    def _tap_to_element(self,
                        positions: List[Tuple[int, int]],
                        duration: int = 0, ):
        return self.__tap(positions=positions, duration=duration)

    def __tap(self, positions: List[Tuple[int, int]], duration: Optional[int] = None):
        """
        Выполняет нажатие по указанным координатам.

        Аргументы:
            positions (List[Tuple[int, int]]): Список координат X и Y для нажатия.
            duration (Optional[int]): Длительность нажатия в миллисекундах.

        Возвращает:
            bool: True, если нажатие выполнено успешно; False в противном случае.
        """

        try:
            self.driver.tap(positions=positions, duration=duration)
            return True
        except Exception as e:
            self.logger.error("some exception with __tap(): {}".format(e))
            return False

    def _double_tap(self,
                    positions: Tuple[int, int],
                    decorator_args: dict = None,
                    wait: bool = False,
                    pause: float = 0.2) -> bool:
        """
        Выполняет двойное нажатие (double tap) на указанных координатах.

        Аргументы:
            positions (Tuple[int, int]): Координаты X и Y для двойного нажатия.
            decorator_args (dict): Дополнительные аргументы для использования в декораторе.
                Например:
                    decorator_args = {"timeout_window": 5,
                                      "tries": 5}, где
                    timeout_window (int): время ожидания изменения окна
                    tries (int): количество попыток для изменения окна
            wait (bool): Флаг, указывающий, нужно ли ожидать изменения окна после двойного нажатия.
            pause (float): Пауза между двумя нажатиями в секундах.

        Возвращает:
            bool: True, если двойное нажатие выполнено успешно; False в противном случае.
        """

        # Декоратор по умолчанию
        decorator_args = {"timeout_window": 5,
                          "tries": 5}

        if wait:
            # Если нужно ожидать результата после двойного нажатия
            return self._double_tap_to_element_and_wait(positions=positions, decorator_args=decorator_args, pause=pause)
        else:
            # Если не нужно ожидать результата после двойного нажатия
            return self._double_tap_to_element(positions=positions, pause=pause)

    @wait_for_window_change()
    def _double_tap_to_element_and_wait(self, positions: Tuple[int, int], decorator_args: dict = None,
                                        pause: float = 0.2) -> bool:
        return self.__double_tap(positions=positions, pause=pause)

    def _double_tap_to_element(self, positions: Tuple[int, int], pause: float = 0.2) -> bool:
        return self.__double_tap(positions=positions, pause=pause)

    def __double_tap(self, positions: Tuple[int, int], pause: float = 0.2) -> bool:
        """
        Выполняет двойное нажатие (double tap) по указанным координатам.

        Аргументы:
            positions (Tuple[int, int]): Координаты X и Y для двойного нажатия.
            pause (float): Пауза между двумя нажатиями в секундах.

        Возвращает:
            bool: True, если двойное нажатие выполнено успешно; False в противном случае.
        """
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        x = positions[0]
        y = positions[1]

        # Первое нажатие
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.pointer_up()
        actions.w3c_actions.pointer_action.pause(pause)

        # Второе нажатие
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(0.1)
        actions.w3c_actions.pointer_action.release()

        try:
            actions.perform()
            return True
        except Exception as e:
            self.logger.error("some exception with __double_tap(): {}".format(e))
            return False

    def _tap_and_move(self,
                      root=None,
                      locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                      x: int = None,
                      y: int = None,
                      direction: int = None,
                      distance: int = None,
                      ) -> bool:
        """
        Выполняет операцию "нажать и переместить" на веб-элементе или на указанных координатах.

        Аргументы:
            root (WebElementExtended): Корневой элемент, относительно которого будет выполнено нажатие и перемещение.
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str]): Локатор элемента,
                на который будет выполнено нажатие и перемещение.
            x (int): Координата X для нажатия и перемещения.
            y (int): Координата Y для нажатия и перемещения.
            direction (int): Направление прокрутки в градусах (0 - вверх, 90 - вправо, 180 - вниз, 270 - влево).
            distance (int): Расстояние прокрутки в пикселях.

        Возвращает:
            bool: True, если операция успешно выполнена; False в противном случае.
        """
        # Получение координат центра начальной позиции прокрутки
        x1, y1 = self._get_center()

        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x1, y1)
        actions.w3c_actions.pointer_action.pointer_down()

        # Проверка аргументов для определения типа операции
        if (x is None and y is None) and locator is None and (direction is None and distance is None):
            # Если не предоставлены аргументы
            self.logger.error(f"_tap_and_move(): Нет аргументов")
            return False
        elif x is not None and y is not None:
            # Если указаны координаты для нажатия и перемещения
            actions.w3c_actions.pointer_action.move_to_location(x, y)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            return True
        elif locator is not None and root is not None:
            try:
                # Если указан локатор элемента и корневой элемент
                target_element = root.get_element(locator)
                x, y = target_element._get_center()
                actions.w3c_actions.pointer_action.move_to_location(x, y)
                actions.w3c_actions.pointer_action.release()
                actions.perform()
                return True
            except WebElementExtendedError:
                return False
        elif direction is not None and distance is not None:
            # Если предоставлены направление и расстояние, вычисляем целевую позицию прокрутки
            window_size = self.terminal.get_screen_resolution()
            width = window_size[0]
            height = window_size[1]

            x2, y2 = find_coordinates_by_vector(width=width, height=height,
                                                direction=direction, distance=distance,
                                                start_x=x1, start_y=y1)
            actions.w3c_actions.pointer_action.move_to_location(x2, y2)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            return True

        return False
