# coding: utf-8
import logging
from typing import Union, Tuple, Dict

from appium.webdriver import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException, \
    InvalidElementStateException

from appium_extended_exceptions.appium_extended_exceptions import WebElementExtendedError
from appium_extended_web_element.web_element_get import WebElementGet
from appium_extended_helpers.helpers_decorators import wait_for_window_change
from appium_extended_utils.utils import find_coordinates_by_vector


class WebElementClick(WebElementGet):
    """
    Класс для выполнения действий клика на элементе, двойного клика и клика с зажатием и перемещением курсора.
    Наследуется от класса WebElementGet.
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

    def _click(self,
               duration: int = 0,
               decorator_args: dict = None,
               wait: bool = False) -> bool:
        """
        Нажимает на элемент.

        Аргументы:
            duration (int): Время в секундах для продолжительности нажатия (по умолчанию 0).
            decorator_args (dict): Параметры для декоратора.
                timeout_window (int): Время ожидания нового окна (умножается на количество попыток).
                tries (int): Количество попыток нажатия (по умолчанию 3).
            wait (bool): Флаг, указывающий, нужно ли ожидать изменения окна.

        Использование:
            decorator_args = {"timeout_window": 5,
                              "tries": 5}
            element._click(duration=0, wait=True, decorator_args=decorator_args)

        Возвращает:
            bool: True, если нажатие выполнено успешно; False в противном случае.
        """
        if wait:
            # Если нужно ожидать изменения окна после нажатия
            if not decorator_args:
                # Декоратор по умолчанию
                decorator_args = {"timeout_window": 5,
                                  "tries": 5}
            return self._click_to_element_and_wait(duration=duration, decorator_args=decorator_args)
        else:
            # Если не нужно ожидать результата после нажатия
            return self._click_to_element(duration=duration)

    def _click_to_element(self,
                          duration: int = 0) -> bool:
        return self.__click(duration=duration)

    @wait_for_window_change()
    def _click_to_element_and_wait(self,
                                   duration: int = 0,
                                   decorator_args: dict = None) -> bool:
        return self.__click(duration=duration)

    def __click(self,
                duration: int = 0) -> bool:
        """
        Выполняет клик на элементе.

        Аргументы:
            duration (int): Длительность удержания клика в секундах.

        Возвращает:
            bool: True, если клик выполнен успешно; False в противном случае.
        """
        try:
            action = ActionChains(self.driver)
            element = self

            if duration > 0:
                # Если указана длительность клика, выполняется клик с удержанием на заданную длительность
                action.click_and_hold(element).pause(duration / 1000).release()
                action.perform()
            else:
                # Если не указана длительность клика, выполняется обычный клик
                action.click(element).perform()

        except (ElementNotInteractableException, StaleElementReferenceException, InvalidElementStateException) as e:
            self.logger.error(f"Не удалось кликнуть по элементу")
            self.logger.error("{}".format(e))
            return False
        return True

    def _double_click(self,
                      decorator_args: dict = None,
                      wait: bool = False) -> bool:
        """
        Выполняет двойное нажатие (double click) на элементе.

        Аргументы:
            decorator_args (dict): Дополнительные аргументы для использования в декораторе.
                Например:
                    decorator_args = {"timeout_window": 5,
                                      "tries": 5}, где
                    timeout_window (int): время ожидания изменения окна
                    tries (int): количество попыток для изменения окна
            wait (bool): Флаг, указывающий, нужно ли ожидать выполнения двойного нажатия.

        Возвращает:
        - True, если двойное нажатие выполнено успешно; False в противном случае.
        """
        decorator_args = {"timeout_window": 5,
                          "tries": 5}
        if wait:
            return self._double_click_to_element_and_wait(decorator_args=decorator_args)
        else:
            return self._double_click_to_element()

    def _double_click_to_element(self) -> bool:
        return self.__double_click()

    @wait_for_window_change()
    def _double_click_to_element_and_wait(self, decorator_args: dict = None) -> bool:
        return self.__double_click()

    def __double_click(self):
        """
        Выполняет двойное нажатие (double click) на элементе.
        Возвращает:
        - True, если двойное нажатие выполнено успешно; False в противном случае.
        """
        try:
            action = ActionChains(self.driver)
            action.click(self).click(self).perform()
            return True
        except WebElementExtendedError:
            return False
        except InvalidElementStateException:
            return True
        except (ElementNotInteractableException, StaleElementReferenceException) as e:
            self.logger.error(f"Не удалось тапнуть по элементу")
            self.logger.error("{}".format(e))
            return False

    def _click_and_move(self,
                        root=None,
                        locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                        x: int = None,
                        y: int = None,
                        direction: int = None,
                        distance: int = None,
                        ) -> bool:
        """
        Нажимает левую кнопку мыши, перемещает курсор к указанной цели и отпускает кнопку.

        Целью может быть WebElement, абсолютные координаты (x, y) или направление и расстояние.
        Если предоставлены направление и расстояние, функция вычисляет целевую позицию
        на основе вектора, определенного этими значениями.
        Если предоставлены абсолютные координаты (x, y), курсор перемещается в указанные позиции.
        Если предоставлен локатор, функция перемещается к найденному элементу на веб-странице.

        Параметры:
        - root: Первый элемент на странице.
        - locator: Локатор для поиска целевого элемента на веб-странице.
        - x: Абсолютная координата по оси X для перемещения курсора.
        - y: Абсолютная координата по оси Y для перемещения курсора.
        - direction: Направление в градусах для перемещения курсора, где 0/360 - вверх, 90 - вправо, 180 - вниз, 270 - влево.
        - distance: Расстояние в пикселях для перемещения курсора.

        Возвращает:
        - True, если действие было успешно выполнено, в противном случае False.

        Примечание: Если не предоставлены аргументы, функция возвращает False и регистрирует ошибку.
        """
        element = self
        action = ActionChains(self.driver)
        action.click_and_hold(element)

        # Получение координат центра начальной позиции прокрутки
        x1, y1 = self._get_center()

        if (x is None and y is None) and locator is None and (direction is None and distance is None):
            # Если не предоставлены аргументы
            self.logger.error(f"_click_and_move(): Нет аргументов")
            return False
        elif x is not None and y is not None:
            # Если указаны абсолютные координаты (x, y) для перемещения курсора
            action.move_by_offset(x-x1, y-y1)
            action.release().perform()
            return True
        elif locator is not None and root is not None:
            try:
                # Если указан локатор элемента и корневой элемент
                target_element = root.get_element(locator)
                action.move_to_element(target_element)
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
            action.move_by_offset(x2-x1, y2-y1)
            action.release().perform()
            return True

        return False

