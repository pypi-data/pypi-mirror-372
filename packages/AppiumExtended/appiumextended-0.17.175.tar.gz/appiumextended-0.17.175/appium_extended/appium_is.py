# coding: utf-8
import logging
import typing
from typing import Union, Dict, Tuple

from appium.webdriver import WebElement
from selenium.common import WebDriverException
from selenium.types import WaitExcTypes

from appium_extended.appium_get import AppiumGet


class AppiumIs(AppiumGet):
    """
    Класс расширяющий Appium.
    Обеспечивает ....
    """

    def __init__(self, logger: logging.Logger, secure_screenshot: bool = False):
        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def _is_element_within_screen(
            self,
            locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
            timeout_elem: float = 10,
            timeout_method: float = 600,
            elements_range: Union[Tuple, typing.List[WebElement], Dict[str, str], None] = None,
            contains: bool = True,
            poll_frequency: float = 0.5,
            ignored_exceptions: typing.Optional[WaitExcTypes] = None
    ) -> bool:
        """
        Метод проверяет, находится ли заданный элемент на видимом экране.

        Args:
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str]):
                    Определяет локатор элемента.
                    Tuple - локатор в виде кортежа из двух строковых элементов,
                        где первый это стратегия поиска, а второй это селектор,
                        например ("id", "android.widget.ProgressBar").
                    Dict - локатор в виде словаря атрибутов и их значений искомого элемента,
                        например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.
                    str - путь до изображения
            timeout (int): Время ожидания элемента. Значение по умолчанию: 10.
            contains (bool): Искать строгое соответствие или вхождение текста.
                Только для поиска по словарю с аргументом 'text'

        Returns:
            bool: True, если элемент находится на экране, False, если нет.

        Note:
            Проверяет атрибут: 'displayed'.
        """
        screen_size = self.terminal.get_screen_resolution()  # Получаем размеры экрана
        screen_width = screen_size[0]  # Ширина экрана
        screen_height = screen_size[1]  # Высота экрана
        element = self._get_element(locator=locator,
                                    timeout_elem=timeout_elem,
                                    timeout_method=timeout_method,
                                    elements_range=elements_range,
                                    contains=contains,
                                    poll_frequency=poll_frequency,
                                    ignored_exceptions=ignored_exceptions)
        if element is None:
            return False
        try:
            if not element.get_attribute('displayed') == 'true':
                # Если элемент не отображается на экране
                return False
            element_location = element.location  # Получаем координаты элемента
            element_size = element.size  # Получаем размеры элемента
            if (
                    element_location['y'] + element_size['height'] > screen_height or
                    element_location['x'] + element_size['width'] > screen_width or
                    element_location['y'] < 0 or
                    element_location['x'] < 0
            ):
                # Если элемент находится за пределами экрана
                return False
        except WebDriverException:
            return False
        # Если элемент находится на экране
        return True
