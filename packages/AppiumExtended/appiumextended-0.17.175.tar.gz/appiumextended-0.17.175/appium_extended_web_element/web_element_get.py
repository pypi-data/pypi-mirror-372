# coding: utf-8
import logging
import math
import time
import typing
from typing import Union, Dict, List, Tuple

import xml.etree.ElementTree as ET

from appium.webdriver import WebElement
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.appiumby import AppiumBy
from selenium.types import WaitExcTypes
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from appium_extended_helpers.appium_helpers import AppiumHelpers
from appium_extended_terminal.terminal import Terminal


class WebElementGet(WebElement):
    """
    Класс расширяющий Appium WebElement.
    Обеспечивает получение сущностей из элемента.
    """

    def __init__(self, base, element_id):
        super().__init__(parent=base.driver, id_=element_id)
        self.base = base
        self.element_id = element_id
        self.driver = base.driver
        self.logger = base.logger
        self.terminal = base.terminal
        self.helpers = base.helpers

    def _get_element(self,
                     locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                     by: Union[MobileBy, AppiumBy, By, str] = None,
                     value: Union[str, Dict, None] = None,
                     timeout_elem: float = 10,
                     timeout_method: float = 600,
                     elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                     contains: bool = True,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                     ) -> \
            Union[WebElement, None]:
        """
        Извлекает элемент из элемента.
        Должен принимать как минимум либо локатор, либо значения by и value.

        Usage:
            inner_element = element.get_element(locator=("id", "foo")).
            inner_element = element.get_element(element).
            inner_element = element.get_element(locator={'text': 'foo'}).
            inner_element = element.get_element(locator='/path/to/file/pay_agent.png').
            inner_element = element.get_element(locator=part_image,
                                       elements_range={'class':'android.widget.FrameLayout', 'package':'ru.app.debug'}).
            inner_element = element.get_element(by="id", value="ru.sigma.app.debug:id/backButton").
            inner_element = element.get_element(by=MobileBy.ID, value="ru.sigma.app.debug:id/backButton").
            inner_element = element.get_element(by=AppiumBy.ID, value="ru.sigma.app.debug:id/backButton").
            inner_element = element.get_element(by=By.ID, value="ru.sigma.app.debug:id/backButton").

        Args:
            locator: tuple / WebElement / dict / str, определяет локатор элемента.
                tuple - локатор в виде ('стратегия', 'значение'), например ('xpath', '//*'), ('id', 'elem_id') и т.д.
                WebElement / WebElementExtended - объект веб элемента
                dict - словарь, содержащий пары атрибут: значение (элемента), например {'text':'foo', 'enabled':'true'}
                str - путь до файла с изображением элемента.
            by: MobileBy, AppiumBy, By, str, тип локатора для поиска элемента (всегда в связке с value)
            value: str, dict, None, значение локатора или словарь аргументов, если используется AppiumBy.XPATH.
            timeout_elem: int, время ожидания элемента.
            timeout_method: int, время ожидания метода поиска элемента.
            elements_range: tuple, list, dict, None, ограничивает поиск элемента в указанном диапазоне
            (для поиска по изображению). По умолчанию - все элементы внутри текущего элемента

        Returns:
            WebElement или None, если элемент не был найден.
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

        # Поиск по изображению в пределах текущего элемента
        if elements_range is None:
            elements_range = self.find_elements("xpath", ".//*")

        # Объявление стратегии поиска элементов
        locator_handler = {
            # составляет локатор типа tuple из словаря с атрибутами искомого элемента
            dict: self.helpers.handle_dict_locator,
            # производит поиск элементов по фрагменту изображения, возвращает список элементов
            str: self.helpers.handle_string_locator,
        }

        # Цикл подготовки локатора и поиска элементов
        start_time = time.time()
        while time.time() - start_time < timeout_method:
            # Выявление типа данных локатора для его подготовки
            if isinstance(locator, WebElement):
                return locator
            locator_type = type(locator)
            # Если локатор типа tuple, то выполняется извлечение элементов
            if isinstance(locator, tuple):
                try:
                    # wait = WebDriverWait(driver=self.driver, timeout=timeout_elem,
                    #                      poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
                    # wait.until(EC.presence_of_element_located(locator))
                    element = self.find_element(*locator)
                    return element
                except WebDriverException:
                    # self.logger.error(f"Элемент не обнаружен!\n"
                    #                   f"{locator=}\n"
                    #                   f"{timeout_elem=}\n\n" +
                    #                   "{}\n".format(e))
                    # self.logger.error(self.driver.page_source)
                    return None
            # Выполнение подготовки локатора
            handler = locator_handler.get(locator_type)
            if locator is None:
                return None
            locator = handler(locator=locator,
                              timeout=int(timeout_elem),
                              elements_range=elements_range,
                              contains=contains)
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
                      timeout_elements: float = 10.0,
                      timeout_method: float = 60.0,
                      elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                      contains: bool = True,
                      poll_frequency: float = 0.5,
                      ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                      ) -> \
            Union[List[WebElement], None]:
        """
        Метод обеспечивает поиск элементов в текущей DOM структуре.
        Должен принять либо локатор, либо by и value.

        Usage:
            elements = app.get_elements(locator=("id", "foo")).
            elements = app.get_elements(locator={'text': 'foo'}).
            elements = app.get_elements(locator='/path/to/file/pay_agent.png').
            elements = app.get_elements(by="id", value="ru.sigma.app.debug:id/backButton").
            elements = app.get_elements(by=MobileBy.ID, value="ru.sigma.app.debug:id/backButton").
            elements = app.get_elements(by=AppiumBy.ID, value="ru.sigma.app.debug:id/backButton").
            elements = app.get_elements(by=By.ID, value="ru.sigma.app.debug:id/backButton").

        Args:
            locator: tuple or WebElement or Dict[str, str], str, локатор tuple или Веб Элемент или словарь {'атрибут': 'значение'} или str как путь до файла с изображением элемента.
            by:[MobileBy, AppiumBy, By, str], тип локатора для поиска элемента (всегда в связке с value)
            value: Union[str, Dict, None], значение локатора или словарь аргументов, если используется AppiumBy.XPATH
            timeout_elements:
            timeout_method:
            elements_range:

        Returns:
            Список WebElement'ов, или пустой список в случае их отсутствия.
        """
        # Проверка и подготовка аргументов
        if not locator and (not by or not value):
            self.logger.error(f"Некорректные аргументы!\n"
                              f"{locator=}\n"
                              f"{by=}\n"
                              f"{value=}\n"
                              f"{timeout_elements=}\n"
                              f"{timeout_method=}\n"
                              f"{contains=}")
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
            # Если локатор типа tuple, то выполняется извлечение элементов
            if isinstance(locator, tuple):
                try:
                    wait = WebDriverWait(driver=self.driver, timeout=timeout_elements,
                                         poll_frequency=poll_frequency, ignored_exceptions=ignored_exceptions)
                    wait.until(EC.presence_of_element_located(locator))
                    elements = self.find_elements(*locator)
                    return elements
                except WebDriverException:
                    # self.logger.error(f"Элемент не обнаружен!\n"
                    #                   f"{locator=}\n"
                    #                   f"{by=}\n"
                    #                   f"{value=}\n"
                    #                   f"{timeout_elements=}\n"
                    #                   f"{timeout_method=}\n"
                    #                   f"{contains=}" +
                    #                   "{}\n".format(e))
                    return None
            # Выявление типа данных локатора для его подготовки
            locator_type = type(locator)
            # Выполнение подготовки локатора
            handler = locator_handler.get(locator_type)
            locator = handler(locator=locator,
                              timeout=int(timeout_elements),
                              elements_range=elements_range,
                              contains=contains)
        # Подбирает результат после поиска по изображению
        if isinstance(locator, list):
            return locator
        self.logger.error(f"Что-то пошло не так\n"
                          f"{locator=}\n"
                          f"{by=}\n"
                          f"{value=}\n"
                          f"{timeout_elements=}\n"
                          f"{timeout_method=}\n"
                          f"{contains=}")
        return None

    def _get_attributes(self,
                        desired_attributes: List[str] = None,
                        tries: int = 3) -> Dict[str, str]:
        """
        Получает атрибуты элемента.
        Если хотя бы один запрашиваемый атрибут не найден, возвращает все атрибуты.

        Usage:
            element._get_attributes(['text', 'bounds', 'class'])
            element._get_attributes()

         Args:
            desired_attributes: список имен атрибутов для получения.
            Если не указан, будут возвращены все атрибуты элемента.

        Returns:
            Если указан desired_attributes и найдены в атрибутах элемента, возвращает словарь с требуемыми атрибутами
            и их значениями.
            Если desired_attributes не указан или атрибут не найден у элемента, возвращает словарь со всеми атрибутами.
        """
        for _ in range(tries):
            try:
                # Инициализация пустого словаря для хранения атрибутов
                result = {}

                # Если desired_attributes не указан, установка значения 'all'
                if not desired_attributes:
                    desired_attributes = 'all'

                # Если desired_attributes не указан, установка значения 'all'
                root = ET.fromstring(self.parent.page_source)

                # Поиск требуемого элемента по критериям атрибутов
                found_element = None
                for element in root.iter():
                    if 'bounds' in element.attrib and 'class' in element.attrib:
                        if self.get_attribute('bounds') == element.attrib['bounds'] and self.get_attribute('class') == \
                                element.attrib['class']:
                            found_element = element
                            break

                # Если элемент найден, получение его атрибутов
                if found_element is not None:
                    attributes = found_element.attrib
                    # Сохранение атрибутов в словаре result
                    for attribute_name, attribute_value in attributes.items():
                        result[attribute_name] = attribute_value

                # Если desired_attributes указан, фильтрация словаря result
                if desired_attributes:
                    new_result = {}
                    for attribute in desired_attributes:
                        if attribute not in result:
                            # Возврат всех атрибутов если не найден искомый
                            return result
                        new_result[attribute] = result[attribute]
                    # Возврат отфильтрованных атрибутов
                    return new_result
                # Возврат всех атрибутов
                return result
            except StaleElementReferenceException:
                continue

    def _get_xpath(self) -> Union[str, None]:
        """
        Подбирает атрибуты элемента и на их основе составляет XPath элемента.

        Returns:
            str: XPath элемента.
        """
        try:
            # Инициализация переменных
            element = self
            xpath = "//"
            attrs = element._get_attributes()
            element_type = attrs.get('class')
            except_attrs = ['hint',
                            'content-desc',
                            'selection-start',
                            'selection-end',
                            'extras',
                            ]

            # Формирование начальной части XPath в зависимости от наличия типа (класса) элемента
            if element_type:
                xpath += element_type
            else:
                xpath += "*"

            # Перебор атрибутов элемента для формирования остальной части XPath
            for key, value in attrs.items():
                if key in except_attrs:
                    continue

                # Добавление атрибута в XPath с соответствующим значением или без него, если значение равно None
                if value is None:
                    xpath += "[@{}]".format(key)
                else:
                    xpath += "[@{}='{}']".format(key, value)
            return xpath
        except (AttributeError, KeyError) as e:
            self.logger.error("Ошибка при формировании XPath: {}".format(str(e)))
        except WebDriverException as e:
            self.logger.error("Неизвестная ошибка при формировании XPath: {}".format(str(e)))
        return None

    def _get_center(self, element: WebElement = None) -> Union[Tuple[int, int], None]:
        """
        Получение координат центра элемента.

        Returns:
            tuple: Координаты x и y центра элемента.
        """
        try:
            if element:
                # Получение границ элемента
                left, top, right, bottom = self._get_coordinates()
            else:
                # Получение границ элемента
                left, top, right, bottom = self._get_coordinates()
            # Расчет координат центра элемента
            x = (left + right) / 2
            y = (top + bottom) / 2

            return x, y
        except WebDriverException as e:
            self.logger.error("exception with _get_center(): {}".format(e))
            return None

    def _get_coordinates(self) -> Union[Tuple[int, int, int, int], None]:
        """
        fill me
        """
        try:
            left, top, right, bottom = map(int, self.get_attribute('bounds').strip("[]").replace("][", ",").split(","))
            return left, top, right, bottom
        except WebDriverException as e:
            self.logger.error("Ошибка в методе _get_coordinates()")
            self.logger.exception(e)

    def _get_first_child_class(self, tries: int = 3) -> str:
        """
        Возвращает класс первого дочернего элемента, отличный от родительского
        """
        for _ in range(tries):
            try:
                parent_element = self
                parent_class = parent_element.get_attribute('class')
                child_elements = parent_element.find_elements("xpath", "//*[1]")
                for i, child_element in enumerate(child_elements):
                    child_class = child_element.get_attribute('class')
                    if parent_class != child_class:
                        return str(child_class)
            except StaleElementReferenceException:
                continue

    def _get_top_child_from_parent(self,
                                   locator: Union[Tuple[str, str], WebElement, Dict[str, str]] = None,
                                   timeout_elements: float = 10.0,
                                   timeout_method: float = 60.0,
                                   elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                                   contains: bool = True,
                                   poll_frequency: float = 0.5,
                                   ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                                   tries: int = 3,
                                   ) -> \
            Union[WebElement, None]:
        """
        Возвращает самый верхний дочерний элемент родительского элемента.
        Если дочерний элемент только один, ищет внутри.

        Args:
            locator: Кортеж / объект WebElement / словарь, представляющий локатор для дочернего элемента.

        Returns:
            Самый верхний дочерний элемент родительского элемента, указанному в локаторе дочерних элементов,
            или None, если соответствующий дочерний элемент не найден.
        """
        for _ in range(tries):
            try:
                if locator is None:
                    locator = {'class': self._get_first_child_class()}
                children = self._get_elements(locator=locator,
                                              timeout_elements=timeout_elements,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains,
                                              poll_frequency=poll_frequency,
                                              ignored_exceptions=ignored_exceptions, )
                if len(children) <= 1:
                    while not len(children) > 1:
                        if len(children) == 0:
                            return None
                        children = children[0].find_elements(by='xpath', value=f'//*')
                top_child = sorted(children, key=lambda x: x.location['y'])[0]
                return top_child
            except StaleElementReferenceException:
                continue

    def _get_bottom_child_from_parent(self,
                                      locator: Union[Tuple[str, str], WebElement, Dict[str, str]] = None,
                                      timeout_elements: float = 10.0,
                                      timeout_method: float = 60.0,
                                      elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                                      contains: bool = True,
                                      poll_frequency: float = 0.5,
                                      ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                                      tries: int = 3
                                      ) -> \
            Union[WebElement, None]:
        """
        Метод возвращает нижний дочерний элемент родительского элемента с заданным классом.
        Если дочерний элемент только один, ищет внутри.

        Args:
            locator: Union[Tuple[str, str], WebElement, Dict[str, str]], локатор дочернего элемента.
        Returns:
            Найденный элемент или None, в случае его отсутствия.
        """
        for _ in range(tries):
            try:
                if locator is None:
                    locator = {'class': self._get_first_child_class()}
                children = self._get_elements(locator=locator,
                                              timeout_elements=timeout_elements,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains,
                                              poll_frequency=poll_frequency,
                                              ignored_exceptions=ignored_exceptions,
                                              )
                if len(children) == 0:
                    return None
                if len(children) <= 1:
                    while not len(children) > 1:
                        if len(children) == 0:
                            return None
                        children = children[0].find_elements(by='xpath', value=f'//*')
                bottom_child = sorted(children, key=lambda x: x.location['y'] + x.size['height'])[-1]
                return bottom_child
            except StaleElementReferenceException:
                continue

    def _get_center_child_from_parent(self,
                                      locator: Union[Tuple[str, str], WebElement, Dict[str, str]] = None,
                                      timeout_elements: float = 10.0,
                                      timeout_method: float = 60.0,
                                      elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                                      contains: bool = True,
                                      poll_frequency: float = 0.5,
                                      ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                                      tries: int = 3
                                      ) -> \
            Union[WebElement, None]:
        """
        Возвращает центральный дочерний элемент родительского элемента.
        Если дочерний элемент только один, ищет внутри.

        Args:
            locator: Кортеж / объект WebElement / словарь, представляющий локатор для дочернего элемента.

        Returns:
            Центральный дочерний элемент родительского элемента, указанному в локаторе дочерних элементов,
            или None, если соответствующий дочерний элемент не найден.
        """
        for _ in range(tries):
            try:
                if locator is None:
                    locator = {'class': self._get_first_child_class()}
                children = self._get_elements(locator=locator,
                                              timeout_elements=timeout_elements,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains,
                                              poll_frequency=poll_frequency,
                                              ignored_exceptions=ignored_exceptions,
                                              )
                if len(children) <= 1:
                    while not len(children) > 1:
                        if len(children) == 0:
                            return None
                        children = children[0].find_elements(by='xpath', value=f'//*')
                center_child = sorted(children, key=lambda x: x.location['y'])[len(children) // 2]
                return center_child
            except StaleElementReferenceException:
                continue

    def _get_top_center_child_from_parent(self,
                                          locator: Union[Tuple[str, str], WebElement, Dict[str, str]] = None,
                                          timeout_elements: float = 10.0,
                                          timeout_method: float = 60.0,
                                          elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                                          contains: bool = True,
                                          poll_frequency: float = 0.5,
                                          ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                                          tries: int = 3
                                          ) -> \
            Union[WebElement, None]:
        """
        Возвращает дочерний элемент родительского элемента расположенный между центральным и верхним.
        Если дочерний элемент только один, ищет внутри.

        Args:
            locator: Кортеж / объект WebElement / словарь, представляющий локатор для дочернего элемента.

        Returns:
            Дочерний элемент родительского элемента расположенный между центральным и верхним,
            указанному в локаторе дочерних элементов,
            или None, если соответствующий дочерний элемент не найден.
        """
        for _ in range(tries):
            try:
                if locator is None:
                    locator = {'class': self._get_first_child_class()}
                children = self._get_elements(locator=locator,
                                              timeout_elements=timeout_elements,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains,
                                              poll_frequency=poll_frequency,
                                              ignored_exceptions=ignored_exceptions,
                                              )
                if len(children) <= 1:
                    while not len(children) > 1:
                        if len(children) == 0:
                            return None
                        children = children[0].find_elements(by='xpath', value=f'//*')
                top_center_child = sorted(children, key=lambda x: x.location['y'])[math.ceil(len(children) / 2 / 2)]
                return top_center_child
            except StaleElementReferenceException:
                continue

    def _get_bottom_center_child_from_parent(self,
                                             locator: Union[Tuple[str, str], WebElement, Dict[str, str]] = None,
                                             timeout_elements: float = 10.0,
                                             timeout_method: float = 60.0,
                                             elements_range: Union[
                                                 Tuple, List[WebElement], Dict[str, str], None] = None,
                                             contains: bool = True,
                                             poll_frequency: float = 0.5,
                                             ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                                             tries: int = 3
                                             ) -> \
            Union[WebElement, None]:
        """
        Возвращает дочерний элемент родительского элемента расположенный между центральным и нижним.
        Если дочерний элемент только один, ищет внутри.

        Args:
            locator: Кортеж / объект WebElement / словарь, представляющий локатор для дочернего элемента.

        Returns:
            Дочерний элемент родительского элемента расположенный между центральным и нижним,
            указанному в локаторе дочерних элементов,
            или None, если соответствующий дочерний элемент не найден.
        """
        for _ in range(tries):
            try:
                if locator is None:
                    locator = {'class': self._get_first_child_class()}
                children = self._get_elements(locator=locator,
                                              timeout_elements=timeout_elements,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains,
                                              poll_frequency=poll_frequency,
                                              ignored_exceptions=ignored_exceptions,
                                              )
                if len(children) <= 1:
                    while not len(children) > 1:
                        if len(children) == 0:
                            return None
                        children = children[0].find_elements(by='xpath', value=f'//*')
                # sorted, 0 - верхний элемент
                bottom_center_child = sorted(children, key=lambda x: x.location['y'])[
                    math.floor(len(children) / 2 + len(children) / 2 / 2)]
                return bottom_center_child
            except StaleElementReferenceException:
                continue
