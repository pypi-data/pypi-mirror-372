# coding: utf-8
import inspect
import logging
import time
from typing import Union, Tuple, Dict, List, cast

from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from selenium.common import StaleElementReferenceException, NoSuchDriverException, InvalidSessionIdException
from selenium.webdriver.common.by import By

from appium_extended_exceptions.appium_extended_exceptions import WebElementExtendedError
from appium_extended_web_element.web_element_click import WebElementClick
from appium_extended_web_element.web_element_dom import WebElementDOM
from appium_extended_web_element.web_element_scroll import WebElementScroll
from appium_extended_web_element.web_element_tap import WebElementTap
from appium_extended_web_element.web_element_adb_actions import WebElementTerminalActions


class WebElementExtended(WebElementClick,
                         WebElementTerminalActions,
                         WebElementDOM,
                         WebElementTap,
                         WebElementScroll):
    """
    Основной интерфейс для работы с WebElementExtended
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

    # GET
    def get_element(self,
                    locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                    by: Union[MobileBy, AppiumBy, By, str] = None,
                    value: Union[str, Dict, None] = None,
                    timeout_elem: int = 10,
                    timeout_method: int = 60,
                    elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                    contains: bool = True,
                    ) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        try:
            inner_element = self._get_element(locator=locator,
                                              by=by,
                                              value=value,
                                              timeout_elem=timeout_elem,
                                              timeout_method=timeout_method,
                                              elements_range=elements_range,
                                              contains=contains)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        if inner_element is not None:
            return WebElementExtended(base=self.base, element_id=inner_element.id)

        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"check exception attributes",
                                      locator=locator,
                                      by=by,
                                      value=value,
                                      timeout_elem=timeout_elem,
                                      timeout_method=timeout_method,
                                      elements_range=elements_range,
                                      contains=contains)

    def get_attributes(self,
                       desired_attributes: Union[str, List[str]] = None,
                       ) -> Union[str, Dict[str, str], None]:
        """
        # TODO fill
        """
        try:
            attributes = self._get_attributes(desired_attributes=desired_attributes)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        if attributes is not None:
            return attributes
        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"check exception attributes",
                                      desired_attributes=desired_attributes)

    # CLICK
    def click(self,
              duration: int = 0,
              decorator_args: dict = None,
              wait: bool = False,
              ) -> 'WebElementExtended':
        """
        Нажимает на элемент.
        Args:
            duration: время в секундах продолжительности нажатия (по умолчанию 0)
            wait: ожидать изменение окна или нет
            decorator_args: параметры для декоратора.
                timeout_window: int время ожидания нового окна (умножается на количество попыток)
                tries: int количество попыток нажатия (по умолчанию 3)
        Usage:
            decorator_args = {"timeout_window": 5,
                              "tries": 5}
            element._tap(duration=0, wait=True, decorator_args=decorator_args)

        Returns:
            True если удалось нажать на элемент, иначе False
        """
        try:
            self._click(duration=duration,
                        wait=wait,
                        decorator_args=decorator_args)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          duration=duration,
                                          decorator_args=decorator_args,
                                          wait=wait,
                                          original_exception=error) from error

    def double_click(self,
                     decorator_args: dict = None,
                     wait: bool = False,
                     ) -> 'WebElementExtended':
        """
        fill me
        # TODO fill
        """
        try:
            self._double_click(decorator_args=decorator_args,
                               wait=wait)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          decorator_args=decorator_args,
                                          wait=wait,
                                          original_exception=error) from error

    def click_and_move(self,
                       locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                       x: int = None,
                       y: int = None,
                       direction: int = None,
                       distance: int = None,
                       ) -> 'WebElementExtended':
        """
        fill me
        # TODO fill
        """
        try:
            root = self.driver.find_element('xpath', '//*')
            root = WebElementExtended(base=self.base, element_id=root.id)
            super()._click_and_move(root=root, locator=locator, x=x, y=y, direction=direction, distance=distance)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          x=x,
                                          y=y,
                                          direction=direction,
                                          distance=distance,
                                          original_exception=error) from error

    # ADB TAP
    def adb_tap(self,
                decorator_args: dict = None,
                wait: bool = False,
                ) -> 'WebElementExtended':
        """
        tap by adb
        # TODO fill
        """
        try:
            self._terminal_tap(wait=wait,
                               decorator_args=decorator_args)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          decorator_args=decorator_args,
                                          wait=wait,
                                          original_exception=error) from error

    def adb_swipe(self,
                  locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                  x: int = None,
                  y: int = None,
                  direction: int = None,
                  distance: int = None,
                  duration: int = 1,
                  contains: bool = True,
                  ) -> 'WebElementExtended':
        """
        swipe by adb
        # TODO fill
        """
        try:
            root = self.driver.find_element('xpath', '//*')
            root = WebElementExtended(base=self.base, element_id=root.id)
            element = None
            if locator is not None:
                element = root.get_element(locator=locator, contains=contains)
            self._terminal_swipe(root=root, element=element,
                                 x=x, y=y,
                                 direction=direction, distance=distance,
                                 duration=duration)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          x=x,
                                          y=y,
                                          direction=direction,
                                          distance=distance,
                                          duration=duration,
                                          contains=contains,
                                          original_exception=error) from error

    # TAP
    def tap(self,
            duration: int = 0,
            decorator_args: dict = None,
            wait: bool = False,
            ) -> 'WebElementExtended':
        """
        # TODO fill
        """
        try:
            positions = self.get_center()
            self._tap(positions=[positions],
                      duration=duration,
                      decorator_args=decorator_args,
                      wait=wait)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          duration=duration,
                                          decorator_args=decorator_args,
                                          wait=wait,
                                          original_exception=error) from error

    def double_tap(self,
                   decorator_args: dict = None,
                   wait: bool = False,
                   pause: float = 0.2,
                   ) -> 'WebElementExtended':
        """
        # TODO fill
        """
        try:
            positions = self.get_center()
            self._double_tap(positions=positions,
                             decorator_args=decorator_args,
                             wait=wait,
                             pause=pause)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          decorator_args=decorator_args,
                                          wait=wait,
                                          pause=pause,
                                          original_exception=error) from error

    def tap_and_move(self,
                     locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                     x: int = None,
                     y: int = None,
                     direction: int = None,
                     distance: int = None,
                     ) -> 'WebElementExtended':
        """
        # TODO fill
        """
        try:
            root = self.driver.find_element('xpath', '//*')
            root = WebElementExtended(base=self.base, element_id=root.id)
            self._tap_and_move(root=root, locator=locator, x=x, y=y, direction=direction, distance=distance)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          x=x,
                                          y=y,
                                          direction=direction,
                                          distance=distance,
                                          original_exception=error) from error

    # ELEMENTS
    def get_elements(self,
                     locator: Union[Tuple, List[WebElement], Dict[str, str], str] = None,
                     by: Union[MobileBy, AppiumBy, By, str] = None,
                     value: Union[str, Dict, None] = None,
                     timeout_elements: int = 10,
                     timeout_method: int = 60,
                     elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                     contains: bool = True,
                     ) -> Union[List[WebElement], None]:
        """
        # TODO fill
        """
        try:
            elements = self._get_elements(locator=locator,
                                          by=by,
                                          value=value,
                                          timeout_elements=timeout_elements,
                                          timeout_method=timeout_method,
                                          elements_range=elements_range,
                                          contains=contains)
            result = []
            if elements is not None or elements != []:
                for element in elements:
                    result.append(WebElementExtended(base=self.base,
                                                     element_id=element.id))
                return result
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
            return None
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          original_exception=error,
                                          locator=locator,
                                          by=by,
                                          value=value,
                                          timeout_elements=timeout_elements,
                                          timeout_method=timeout_method,
                                          elements_range=elements_range,
                                          contains=contains) from error

    # SCROLL
    def scroll_down(self,
                    locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str] = None,
                    duration: int = None,
                    ) -> 'WebElementExtended':
        """
        Скроллит элемент вниз от нижнего до верхнего элемента.
        :param child_locator: str, имя класса дочернего элемента.
        :param timeout: int, время ожидания элемента, по умолчанию 10 секунд.
        :return: bool, True, если скроллинг выполнен успешно.
        # TODO fill
        """
        try:
            self._scroll_down(locator=locator,
                              duration=duration)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          duration=duration,
                                          original_exception=error) from error

    def scroll_up(self,
                  locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str] = None,
                  duration: int = None,
                  ) -> 'WebElementExtended':
        """
        Скроллит элемент вверх от верхнего дочернего элемента до нижнего дочернего элемента родительского элемента.
        :param locator: Union[tuple, WebElement], локатор или элемент, который нужно проскроллить.
        :param child_locator: str, имя класса дочернего элемента.
        :param timeout: int, время ожидания элемента, по умолчанию 10 секунд.
        :return: bool, True, если скроллинг выполнен успешно.
        # TODO fill
        """
        try:
            self._scroll_up(locator=locator,
                            duration=duration)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          duration=duration,
                                          original_exception=error) from error

    def scroll_to_bottom(self,
                         locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str] = None,
                         timeout_method: int = 120,
                         ) -> 'WebElementExtended':
        """
        # TODO fill
        """
        try:
            self._scroll_to_bottom(locator=locator,
                                   timeout_method=timeout_method)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          timeout_method=timeout_method,
                                          original_exception=error) from error

    def scroll_to_top(self,
                      locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str] = None,
                      timeout_method: int = 120,
                      ) -> 'WebElementExtended':
        """
        # TODO fill
        """
        try:
            self._scroll_to_top(locator=locator,
                                timeout_method=timeout_method)
            return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          timeout_method=timeout_method,
                                          original_exception=error) from error

    def scroll_until_find(self,
                          locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str],
                          timeout_method: float = 120.0,
                          contains: bool = True,
                          check_image: bool = False,
                          ) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        try:
            if self._scroll_until_find(locator=locator,
                                       timeout_method=timeout_method,
                                       contains=contains,
                                       check_image=check_image):
                return cast('WebElementExtended', self)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          locator=locator,
                                          timeout_method=timeout_method,
                                          contains=contains,
                                          original_exception=error) from error

    def scroll_and_get(self,
                       locator: Union[Tuple, 'WebElementExtended', Dict[str, str], str],
                       timeout_method: int = 120,
                       tries: int = 3,
                       check_image: bool = False
                       ) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        for i in range(tries):
            try:
                element = self._scroll_and_get(locator=locator,
                                               timeout_method=timeout_method,
                                               tries=tries,
                                               check_image=check_image)
                if element is not None:
                    return WebElementExtended(base=self.base, element_id=element.id)
            except StaleElementReferenceException:
                time.sleep(3)
                continue
            except NoSuchDriverException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()
            except InvalidSessionIdException:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.base.reconnect()
        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"element is None",
                                      locator=locator,
                                      timeout_method=timeout_method,
                                      tries=tries)

    # DOM
    def get_parent(self) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        try:
            element = self._get_parent()
            if element is not None:
                return WebElementExtended(base=self.base, element_id=element.id)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"element is None")

    def get_parents(self) -> Union[List['WebElementExtended'], None]:
        """
        # TODO fill
        """
        try:
            elements = self._get_parents()
            elements_ext = []
            if elements is None or elements == []:
                return None
            for element in elements:
                elements_ext.append(
                    WebElementExtended(base=self.base, element_id=element.id))
            return elements_ext
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          original_exception=error) from error

    def get_sibling(self,
                    attributes: Dict[str, str],
                    contains: bool = True,
                    ) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        try:
            element = self._get_sibling(attributes=attributes, contains=contains)
            if element is None:
                return None
            return WebElementExtended(base=self.base, element_id=element.id)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          attributes=attributes,
                                          contains=contains,
                                          original_exception=error) from error

    def get_siblings(self) -> Union[List['WebElementExtended'], None]:
        """
        # TODO fill
        """
        try:
            elements = self._get_siblings()
            elements_ext = []
            for element in elements:
                elements_ext.append(
                    WebElementExtended(base=self.base, element_id=element.id))
            return elements_ext
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          original_exception=error) from error

    def get_cousin(self,
                   ancestor: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str],
                   cousin: Dict[str, str],
                   contains: bool = True,
                   ) -> Union['WebElementExtended', None]:
        """
        # TODO fill
        """
        try:
            root = self.driver.find_element('xpath', '//*')
            root = WebElementExtended(base=self.base, element_id=root.id)
            ancestor = root.get_element(ancestor)
            ancestor = WebElement(ancestor.parent, ancestor.id)
            element = self._get_cousin(ancestor=ancestor, cousin=cousin, contains=contains)
            if element is None:
                return None
            return WebElementExtended(base=self.base, element_id=element.id)
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          ancestor=ancestor,
                                          cousin=cousin,
                                          contains=contains,
                                          original_exception=error) from error

    def get_cousins(self,
                    ancestor: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str],
                    cousin: Dict[str, str],
                    contains: bool = True,
                    ) -> Union[List['WebElementExtended'], None]:
        """
        # TODO fill
        """
        try:
            root = self.driver.find_element('xpath', '//*')
            root = WebElementExtended(base=self.base, element_id=root.id)
            ancestor = root.get_element(ancestor)
            ancestor = WebElement(ancestor.parent, ancestor.id)
            elements = self._get_cousins(ancestor=ancestor, cousin=cousin, contains=contains)
            elements_ext = []
            if elements is None or elements == []:
                return None
            for element in elements:
                elements_ext.append(
                    WebElementExtended(base=self.base, element_id=element.id))
            return elements_ext
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except Exception as error:
            raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                                  f"check exception attributes",
                                          ancestor=ancestor,
                                          cousin=cousin,
                                          contains=contains,
                                          original_exception=error) from error

    def is_contains(self,
                    locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str],
                    contains: bool = True,
                    ) -> bool:
        """
        # TODO fill
        """
        try:
            child_element = self._get_element(locator=locator, contains=contains)
            if child_element is not None:
                return True
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        return False

    # ACTIONS
    def zoom(self, hold: bool) -> 'WebElementExtended':
        """
        # TODO fill
        """
        raise NotImplementedError  # TODO implement

    def unzoom(self, hold: bool) -> 'WebElementExtended':
        """
        # TODO fill
        """
        raise NotImplementedError  # TODO implement

    def get_center(self) -> Union[Tuple[int, int], None]:
        """
        Вычисляет координаты центра заданного элемента.

        Аргументы:
            element (WebElement): Веб-элемент.

        Возвращает:
            tuple: Координаты центра в виде (x, y). Возвращает None, если произошла ошибка.
        """
        try:
            center = self._get_center()
            if center is not None:
                return center
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"check exception attributes",
                                      )

    def get_coordinates(self) -> Union[Tuple[int, int, int, int], None]:
        """
        # TODO fill
        """
        try:
            coordinates = self._get_coordinates()
            if coordinates is not None:
                return coordinates
        except NoSuchDriverException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        except InvalidSessionIdException:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.base.reconnect()
        raise WebElementExtendedError(message=f"Ошибка при выполнении {inspect.currentframe().f_code.co_name}. "
                                              f"check exception attributes",
                                      )
