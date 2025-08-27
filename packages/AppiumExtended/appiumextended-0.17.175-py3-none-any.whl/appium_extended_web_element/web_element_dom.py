# coding: utf-8
import logging
import time
from typing import Union, List, Dict

from appium.webdriver import WebElement
from selenium.common.exceptions import NoSuchElementException

from appium_extended_web_element.web_element_get import WebElementGet


class WebElementDOM(WebElementGet):
    """
    Класс поиска элементов по DOM структуре относительно текущего элемента.
    Наследуется от класса WebElementGet.
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

        self.stable_attributes = ['bounds', 'enabled', 'displayed', 'focused', 'focusable', 'class', 'resource-id',
                                  'text']

    def _get_parent(self) -> WebElement:
        """
        Возвращает родительский элемент
        """
        # Формирование XPath для поиска всех родительского элемента
        xpath = self._get_xpath() + "/.."

        # Поиск всех родительского элемента по XPath
        parent = self.driver.find_element(by='xpath', value=xpath)

        return parent

    def _get_parents(self) -> List[WebElement]:
        """
        Возвращает всех родителей элемента.

        Возвращает:
            List[WebElement]: Список всех родительских элементов, начиная от ближайшего и до корневого элемента.
        """
        # Формирование XPath для поиска всех родительских элементов
        xpath = self._get_xpath() + "/ancestor::*"

        # Поиск всех родительских элементов по XPath
        parents = self.driver.find_elements(by='xpath', value=xpath)

        return parents

    def _get_sibling(self, attributes: Dict[str, str], contains: bool = True) -> Union[WebElement, None]:
        """
        Возвращает брата элемента по указанным атрибутам.
        То есть соседнего элемента в пределах первого предка.

        Аргументы:
            attributes (dict): Словарь с атрибутами и их значениями для поиска брата или сестры.
            contains (bool): Флаг, указывающий, использовать ли функцию contains для атрибутов (по умолчанию: True).

        Возвращает:
            WebElement or None: Брат или сестра элемента, соответствующие указанным атрибутам, или None, если не найдено.

        Примечание:
            В случае, если используется contains=True и не найдено ни брата, ни сестры, возвращается None.

        """
        xpath_attributes = ""

        # Формирование XPath атрибутов в зависимости от значения contains
        if contains:
            # Для поиска по фрагменту значения атрибута
            for attr, value in attributes.items():
                xpath_attributes += f"[contains(@{attr}, '{value}')]"
        else:
            # Для поиска по полному совпадению значения атрибута
            for attr, value in attributes.items():
                xpath_attributes += f"[(@{attr}='{value}')]"
        try:
            # Поиск брата перед текущим элементом с указанными атрибутами
            xpath = self._get_xpath() + "/preceding-sibling::*" + xpath_attributes
            sibling_before = self.driver.find_element(by='xpath', value=xpath)
            return sibling_before
        except NoSuchElementException:
            try:
                # Поиск брата после текущего элемента с указанными атрибутами
                xpath = self._get_xpath() + "/following-sibling::*" + xpath_attributes
                sibling_after = self.driver.find_element(by='xpath', value=xpath)
                return sibling_after
            except NoSuchElementException:
                return None

    def _get_siblings(self) -> Union[List[WebElement], List]:
        """
        Возвращает всех братьев элемента.
        То есть соседних элементов в пределах первого предка.

        Возвращает:
            List[WebElement]: Список всех братьев и сестер элемента.
        """
        try:
            # Получение XPath текущего элемента
            xpath = self._get_xpath() + "/preceding-sibling::*"
            # Поиск всех предшествующих братьев
            siblings_before = self.driver.find_elements(by='xpath', value=xpath)
            # Формирование XPath для последующих братьев
            xpath = self._get_xpath() + "/following-sibling::*"
            # Поиск всех последующих братьев
            siblings_after = self.driver.find_elements(by='xpath', value=xpath)
            # Объединение предшествующих и последующих братьев
            siblings = siblings_before + siblings_after
            return siblings
        except NoSuchElementException as e:
            self.logger.error("Ошибка при _get_siblings: {}".format(e))
            return []

    def _get_cousin(self,
                    ancestor: WebElement,
                    cousin: Dict[str, str],
                    contains: bool = True) -> Union[WebElement, None]:
        """
        Поиск одного кузена элемента.
        То есть элемента находящегося на аналогичной глубине относительно указанного предка.

        Аргументы:
            ancestor (WebElement): Элемент-предок.
            cousin (Dict[str, str]): Атрибуты кузина для поиска.
            contains (bool): Флаг, указывающий на использование функции contains при формировании XPath (по умолчанию: True).

        Возвращает:
            WebElement: Кузин элемента или None, если кузин не найден.
        """
        # Получение количество поколений между предком и текущим элементом
        generation_len = self._generation_counter(ancestor=ancestor, descendant=self)

        # Проверка наличия атрибута 'class' в словаре cousin и получение его значения из текущего элемента,
        # если отсутствует
        if 'class' not in cousin:
            cousin['class'] = self.get_attribute('class')

        # Формирование начального XPath с использованием класса кузина
        xpath = "//" + cousin['class']

        # Формирование XPath с использованием остальных атрибутов кузина
        if contains:
            # Для поиска по фрагменту значения атрибута
            for attr, value in cousin.items():
                xpath += f"[contains(@{attr}, '{value}')]"
        else:
            # Для поиска по полному совпадению значения атрибута
            for attr, value in cousin.items():
                xpath += f"[@{attr}='{value}']"

        # Поиск потенциальных кузенов с помощью XPath
        possible_cousins = ancestor.find_elements('xpath', xpath)

        # Проверка поколения между предком и каждым потенциальным кузеном и возврат первого подходящего элемента
        for element in possible_cousins:
            if self._generation_counter(ancestor=ancestor, descendant=element) == generation_len:
                return element

        return None

    def _get_cousins(self, ancestor: WebElement, cousin: Dict[str, str], contains: bool = True) -> \
            Union[List[WebElement], List]:
        """
        Возвращает список кузенов элемента.
        То есть элементов находящихся на аналогичной глубине относительно указанного предка.

        Аргументы:
            ancestor (WebElement): Элемент-предок.
            cousin (dict): Атрибуты кузина для поиска.
            contains (bool): Флаг, указывающий на использование функции contains при формировании XPath (по умолчанию: True).

        Возвращает:
            list: Список элементов-кузенов.
        """
        # Получение количество поколений между предком и текущим элементом
        generation_len = self._generation_counter(ancestor=ancestor, descendant=self, )

        # Проверка наличия атрибута 'class' в словаре cousin и получение его значения из текущего элемента,
        # если отсутствует
        if 'class' not in cousin:
            cousin['class'] = self.get_attribute('class')

        # Формирование начального XPath с использованием класса кузена
        xpath = "//" + cousin['class']

        # Формирование начального XPath с использованием класса кузина
        if contains:
            # Для поиска по фрагменту значения атрибута
            for attr, value in cousin.items():
                xpath += f"[contains(@{attr}, '{value}')]"
        else:
            # Для поиска по полному совпадению значения атрибута
            for attr, value in cousin.items():
                xpath += f"[@{attr}='{value}']"

        # Поиск потенциальных кузенов с помощью XPath
        possible_cousins = ancestor.find_elements('xpath', xpath)
        result = []

        # Проверка поколения между предком и каждым потенциальным кузеном и добавление их в список результатов
        for element in possible_cousins:
            if self._generation_counter(ancestor=ancestor, descendant=element) == generation_len:
                result.append(element)

        return result

    def _generation_counter(self,
                            ancestor: WebElement,
                            descendant: WebElement,
                            timeout: int = 90) -> int:
        """
        Подсчитывает количество поколений между элементами предком и потомком.

        Аргументы:
            ancestor (WebElement): элемент-предок.
            descendant (WebElement): элемент-потомок.
            timeout (int): время ожидания в секундах (по умолчанию: 90).
        Возвращает:
            int: количество поколений между элементами.
        """
        # Инициализация
        start_time = time.time()
        generation_count = 0
        current_element = descendant

        # Цикл выполняется, пока текущий элемент не станет None, не будет равен предку или не будет превышено время ожидания.
        while current_element is not None and current_element != ancestor and time.time() - start_time < timeout:
            attributes = {}
            # Цикл проходит по всем стабильным атрибутам и получает их значения для текущего элемента.
            for attribute in self.stable_attributes:
                attributes[attribute] = current_element.get_attribute(attribute)

            # Удаление атрибутов со значением None
            attributes = {k: v for k, v in attributes.items() if v is not None}
            # Создание начального xpath с использованием класса текущего элемента.
            xpath = "//" + attributes['class']

            # Цикл проходит по всем оставшимся атрибутам и добавляет их в xpath.
            for attr, value in attributes.items():
                xpath += f"[@{attr}='{value}']"

            # Добавление "/.." в конец xpath для перехода к родительскому элементу.
            xpath += "/.."
            try:
                # Поиск предка элемента по xpath
                current_element = self.driver.find_element(by='xpath', value=xpath)
                generation_count += 1
            except NoSuchElementException:
                # Если не удалось найти элемент-предка, возвращаем 0 и выводим сообщение об ошибке
                self.logger.error("Элементы не связаны связью предок-потомок")
                return 0

        return generation_count
