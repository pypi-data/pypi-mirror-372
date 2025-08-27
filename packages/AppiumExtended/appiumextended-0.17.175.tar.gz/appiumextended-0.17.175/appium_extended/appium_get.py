# coding: utf-8
import logging
import time
import typing
from typing import Union, Dict, List, Tuple, Optional, Any

import numpy as np
from PIL import Image
from selenium.types import WaitExcTypes

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from appium.webdriver import WebElement
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.appiumby import AppiumBy

from appium_extended.appium_base import AppiumBase


class AppiumGet(AppiumBase):
    """
    Класс расширяющий Appium.
    Обеспечивает получение чего-либо со страницы.
    """

    def __init__(self, logger: logging.Logger, secure_screenshot: bool = False):
        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def _get_element(self,
                     locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                     by: Union[MobileBy, AppiumBy, By, str] = None,
                     value: Union[str, Dict, None] = None,
                     timeout_elem: float = 10,
                     timeout_method: float = 600,
                     elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                     contains: bool = True,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: typing.Optional[WaitExcTypes] = None
                     ) -> \
            Union[WebElement, None]:
        """
        Метод обеспечивает поиск элемента в текущей DOM структуре.
        Должен принимать либо локатор, либо значения by и value.

        Args:
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str], optional):
                Определяет локатор элемента.
                Tuple - локатор в виде кортежа из двух строковых элементов,
                    где первый это стратегия поиска, а второй это селектор,
                    например ("id", "android.widget.ProgressBar").
                Dict - локатор в виде словаря атрибутов и их значений искомого элемента,
                    например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.

            by (Union[MobileBy, AppiumBy, By, str], optional):
                Тип локатора для поиска элемента (всегда в связке с value).
                Как в стандартном методе driver.find_element.
            value (Union[str, Dict, None], optional):
                Значение локатора или словарь аргументов, если используется AppiumBy.XPATH.
            timeout_elem (int, optional):
                Время ожидания элемента. По умолчанию 10 секунд.
            timeout_method (int, optional):
                Время ожидания метода поиска элемента. По умолчанию 600 секунд.
            elements_range (Union[Tuple, List[WebElement], Dict[str, str], None], optional):
                Ограничивает поиск элемента в указанном диапазоне (для поиска по изображению).
            contains (bool, optional):
                Для поиска по dict и атрибуту 'text',
                ищет элемент содержащий фрагмент значения если True
                и по строгому соответствию если False.
                По умолчанию True.

        Usages:
            element = app._get_element(locator=("id", "foo"))
            element = app._get_element(element)
            element = app._get_element(locator={'text': 'foo'}, contains=True)
            element = app._get_element(locator='/path/to/file/image.png')
            element = app._get_element(by="id", value="backButton")
            element = app._get_element(by=MobileBy.ID, value="backButton")

        Returns:
            Union[WebElement, None]: Возвращает WebElement, если элемент найден, иначе None.
        """
        # Проверка и подготовка аргументов
        if (not locator) and (not by or not value):
            self.logger.error(f"Некорректные аргументы!\n"
                              f"{locator=}\n"
                              f"{by=}\n"
                              f"{value=}\n"
                              f"{timeout_elem=}\n")
            return None
        if not locator and (by and value):
            locator = (by, value)
        if locator is None:
            return None

        # Объявление стратегии поиска элементов
        locator_handler = {
            # возвращает себя же
            WebElement: self.helpers.handle_webelement_locator,
            # возвращает себя же
            'WebElementExtended': self.helpers.handle_webelement_locator,
            # составляет локатор типа tuple из словаря с атрибутами искомого элемента
            dict: self.helpers.handle_dict_locator,
            # производит поиск элементов по фрагменту изображения, возвращает список элементов
            str: self.helpers.handle_string_locator,
        }

        # Цикл подготовки локатора и поиска элементов
        start_time = time.time()
        while not isinstance(locator, WebElement) and time.time() - start_time < timeout_method:
            # Выявление типа данных локатора для его подготовки
            locator_type = type(locator)
            # Если локатор типа tuple, то выполняется извлечение элементов
            if isinstance(locator, tuple):
                wait = WebDriverWait(driver=self.driver, timeout=timeout_elem,
                                     poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
                try:
                    element = wait.until(EC.presence_of_element_located(locator))
                    return element
                except NoSuchElementException:
                    return None
                except TimeoutException as error:
                    self.logger.debug(f"Элемент не обнаружен!\n"
                                      f"{locator=}\n"
                                      f"{timeout_elem=}\n\n" +
                                      "{}\n".format(error))
                    self.logger.debug("page source ", self.driver.page_source)
                    return None
                except WebDriverException as error:
                    self.logger.debug(f"Элемент не обнаружен!\n"
                                      f"{locator=}\n"
                                      f"{timeout_elem=}\n\n" +
                                      "{}\n".format(error))
                    self.logger.debug("page source ", self.driver.page_source)
                    return None
            # Выполнение подготовки локатора
            handler = locator_handler.get(locator_type)
            if locator is None:
                return None
            locator = handler(locator=locator, timeout=timeout_elem, elements_range=elements_range, contains=contains)
        # Подбирает результат после поиска по изображению
        if isinstance(locator, WebElement):
            return locator
        self.logger.error(f"Что-то пошло не так\n"
                          f"{locator=}\n"
                          f"{by=}\n"
                          f"{value=}\n"
                          f"{timeout_elem=}\n"
                          f"{timeout_method=}\n")
        return None

    def _get_elements(self,
                      locator: Union[Tuple, List[WebElement], Dict[str, str], str] = None,
                      by: Union[MobileBy, AppiumBy, By, str] = None,
                      value: Union[str, Dict, None] = None,
                      timeout_elements: int = 10,
                      timeout_method: int = 60,
                      elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                      contains: bool = True,
                      poll_frequency: float = 0.5,
                      ignored_exceptions: typing.Optional[WaitExcTypes] = None
                      ) -> \
            Union[List[WebElement], None]:
        """
        Метод обеспечивает поиск элементов в текущей DOM структуре.
        Должен принять либо локатор, либо by и value.

        Args:
            locator (Union[Tuple, List[WebElement], Dict[str, str], str], optional):
                Определяет локатор элементов.
                Tuple - локатор в виде кортежа из двух строковых элементов,
                    где первый это стратегия поиска, а второй это селектор,
                    например ("id", "android.widget.ProgressBar").
                Dict - локатор в виде словаря атрибутов и их значений искомого элемента,
                    например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.
            by (Union[MobileBy, AppiumBy, By, str], optional):
                Тип локатора для поиска элементов (всегда в связке с value).
                Как в стандартном методе driver.find_element.
            value (Union[str, Dict, None], optional):
                Значение локатора или словарь аргументов, если используется XPATH.
            timeout_elements (int, optional):
                Время ожидания элементов. По умолчанию 10 секунд.
            timeout_method (int, optional):
                Время ожидания метода поиска элементов. По умолчанию 600 секунд.
            elements_range (Union[Tuple, List[WebElement], Dict[str, str], None], optional):
                Ограничивает поиск элементов в указанном диапазоне.
            contains (bool, optional):
                Для поиска по dict и атрибуту 'text',
                True - ищет элемент содержащий фрагмент значения,
                False - по строгому соответствию.
                По умолчанию True.

        Usages:
            elements = app._get_elements(locator=("id", "foo"))
            elements = app._get_elements(locator={'text': 'foo'})
            elements = app._get_elements(locator='/path/to/file/pay_agent.png')
            elements = app._get_elements(by="id", value="ru.sigma.app.debug:id/backButton")
            elements = app._get_elements(by=MobileBy.ID, value="ru.sigma.app.debug:id/backButton")

        Raises:
            WebDriverException: Если произошла ошибка при взаимодействии с WebDriver.

        Returns:
            Union[List[WebElement], None]: Возвращает список WebElement'ов, если элементы найдены, иначе None.
        """
        # Проверка и подготовка аргументов
        if not locator and (not by or not value):
            self.logger.error(f"Некорректные аргументы!\n"
                              f"{locator=}\n"
                              f"{by=}\n"
                              f"{value=}\n"
                              f"{timeout_elements=}\n"
                              f"{timeout_method=}\n\n" +
                              f"{poll_frequency=}\n" +
                              f"{ignored_exceptions=}\n")
            return None
        if not locator and (by and value):
            locator = (by, value)
        if locator is None:
            return None

        # Объявление стратегии поиска элементов
        locator_handler = {
            # подразумевается список элементов, возвращает себя же
            list: self.helpers.handle_webelement_locator_elements,
            # составляет локатор типа tuple из словаря с атрибутами искомого элемента
            dict: self.helpers.handle_dict_locator_elements,
            # производит поиск элементов по фрагменту изображения, возвращает список элементов
            str: self.helpers.handle_string_locator_elements,
        }

        # Цикл подготовки локатора и поиска элементов
        start_time = time.time()
        while not isinstance(locator, list) and time.time() - start_time < timeout_method:
            # Выявление типа данных локатора для его подготовки
            locator_type = type(locator)
            # Если локатор типа tuple, то выполняется извлечение элементов
            if isinstance(locator, tuple):
                wait = WebDriverWait(driver=self.driver, timeout=timeout_elements,
                                     poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
                try:
                    element = wait.until(EC.presence_of_all_elements_located(locator))
                    return element
                except WebDriverException as error:
                    self.logger.debug(f"Элемент не обнаружен!\n"
                                      f"{locator=}\n"
                                      f"{by=}\n"
                                      f"{value=}\n"
                                      f"{timeout_elements=}\n"
                                      f"{timeout_method=}\n\n" +
                                      f"{poll_frequency=}\n" +
                                      f"{ignored_exceptions=}\n" +
                                      "{}\n".format(error))
                    return None
            # Выполнение подготовки локатора
            handler = locator_handler.get(locator_type)
            locator = handler(locator=locator,
                              timeout=timeout_elements,
                              elements_range=elements_range,
                              contains=contains)
        # Подбирает результат после поиска по изображению
        if isinstance(locator, list):
            return locator
        self.logger.debug(f"\nЧто-то пошло не так\n"
                          f"{locator=}\n"
                          f"{by=}\n"
                          f"{value=}\n"
                          f"{timeout_elements=}\n"
                          f"{timeout_method=}\n")
        return None

    def _get_image_coordinates(self,
                               image: Union[bytes, np.ndarray, Image.Image, str],
                               full_image: Union[bytes, np.ndarray, Image.Image, str] = None,
                               threshold: float = 0.7,
                               ) -> Union[Tuple[int, int, int, int], None]:
        return self.helpers.get_image_coordinates(image=image, full_image=full_image, threshold=threshold)

    def _get_inner_image_coordinates(self,
                                     outer_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                     inner_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                     threshold: float = 0.9) -> \
            Union[Tuple[int, int, int, int], None]:
        return self.helpers.get_inner_image_coordinates(outer_image_path=outer_image_path,
                                                       inner_image_path=inner_image_path,
                                                       threshold=threshold)

    def _get_text_coordinates(self,
                              text: str,
                              language: str = 'rus',
                              image: Union[bytes, str, Image.Image, np.ndarray] = None, ) -> Optional[tuple[int, ...]]:
        return self.helpers.get_text_coordinates(text=text, language=language, image=image)

    def _get_screenshot_as_base64_decoded(self):
        return self.helpers._get_screenshot_as_base64_decoded()
