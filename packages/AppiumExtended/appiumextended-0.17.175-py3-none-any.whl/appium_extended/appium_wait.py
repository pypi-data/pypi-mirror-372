# coding: utf-8
import logging
import time
import typing
from typing import Union, Dict, List, Tuple

import numpy as np
from PIL import Image
from appium.webdriver import WebElement
from selenium.types import WaitExcTypes

from appium_extended.appium_get import AppiumGet


class AppiumWait(AppiumGet):
    """
    Класс расширяющий Appium.
    Обеспечивает ....
    """

    def __init__(self, logger: logging.Logger, secure_screenshot: bool = False):
        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def _wait_for(self,
                  locator: Union[Tuple[str, str], WebElement, 'WebElementExtended', Dict[str, str], str,
                  List[Tuple[str, str]], List[WebElement], List['WebElementExtended'], List[Dict[str, str]], List[
                      str]] = None,
                  image: Union[bytes, np.ndarray, Image.Image, str,
                  List[bytes], List[np.ndarray], List[Image.Image], List[str]] = None,
                  timeout_elem: float = 10.0,
                  timeout_method: float = 60.0,
                  elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                  contains: bool = True,
                  sleep: float = 1.0,
                  poll_frequency: float = 0.5,
                  ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                  threshold: float = 0.9,
                  ):
        """
        Ожидает появления на экране указанного локатора или изображения.

        Args:
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict, str, List], optional):
                - Tuple: локатор в виде кортежа из двух строковых элементов, где первый это стратегия поиска, а второй это селектор, например ("id", "android.widget.ProgressBar").
                - Dict: локатор в виде словаря {'text': 'foo', 'displayed': 'true', 'enabled': 'true'}.
                - str: путь до изображения.
                - List: список из локаторов. Будет ожидание всех элементов из списка.
                По умолчанию None.

            image (Union[bytes, np.ndarray, Image.Image, str, List], optional):
                - bytes: изображение в формате байтов.
                - np.ndarray: изображение в формате массива NumPy.
                - Image.Image: изображение в формате Image (PIL/Pillow).
                - str: путь до файла с изображением.
                По умолчанию None.

            timeout (int, optional): Максимальное время ожидания в секундах. По умолчанию 10.

            contains (bool, optional): Если True, проверяет, содержит ли элемент указанный локатор.
                                       По умолчанию True.

            sleep (int): время ожидания перед новым запросом в процессе поллинга.

        Usages:
            - _wait_for(locator=("id", "android.widget.ProgressBar"), timeout=5)
            - _wait_for(image="path/to/image.png", timeout=10)
            - _wait_for(locator=[("id", "element1"), ("name", "element2")], timeout=5)
            - _wait_for(image=["path/to/image1.png", "path/to/image2.png"], timeout=10)


        Returns:
            bool: True, если элементы или изображения найдены в течение заданного времени, иначе False.

        Raises:
            None: Метод не вызывает исключений.

        Notes:
            - Метод использует внутренние функции для поиска элементов и изображений.
            - Параметр `contains` используется только при поиске по локатору.
        """
        if locator is not None:
            if not isinstance(locator, List):
                locator = [locator]

            # Loop through each locator
            for i in locator:
                # Check if the element is present
                if self._get_element(locator=i,
                                     timeout_elem=timeout_elem,
                                     timeout_method=timeout_method,
                                     elements_range=elements_range,
                                     contains=contains,
                                     poll_frequency=poll_frequency,
                                     ignored_exceptions=ignored_exceptions,) is None:
                    return False

        if image is not None:
            start_time = time.time()
            if not isinstance(image, List):
                image = [image]

            # Loop through each image
            for i in image:
                # Check if the image is on the screen within the timeout period
                while not self.helpers._is_image_on_the_screen(image=i, threshold=threshold) and time.time() - start_time < timeout_method:
                    time.sleep(sleep)
                if not self.helpers._is_image_on_the_screen(image=i, threshold=threshold):
                    return False

        # Return True if all conditions are met
        return True

    def _wait_for_not(self,
                      locator: Union[Tuple[str, str], WebElement, 'WebElementExtended', Dict[str, str], str,
                      List[Tuple[str, str]], List[WebElement], List['WebElementExtended'], List[Dict[str, str]], List[
                          str]] = None,
                      image: Union[bytes, np.ndarray, Image.Image, str,
                      List[bytes], List[np.ndarray], List[Image.Image], List[str]] = None,
                      timeout_elem: float = 10.0,
                      timeout_method: float = 60.0,
                      elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                      contains: bool = True,
                      poll_frequency: float = 0.5,
                      ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                      sleep: float = 1.0,
                      threshold: float = 0.9,
                      ):
        """
        Ожидает пока указанный локатор или изображение исчезнет с экрана или DOM.

        Args:
            locator (Union[Tuple[str, str], WebElement, 'WebElementExtended', Dict[str, str], str,
                           List[Tuple[str, str]], List[WebElement], List['WebElementExtended'],
                           List[Dict[str, str]], List[str]], optional): The locator(s) to wait for.
                           Can be a single locator or a list of locators. Defaults to None.

            image (Union[bytes, np.ndarray, Image.Image, str,
                         List[bytes], List[np.ndarray], List[Image.Image], List[str]], optional):
                         The image(s) to wait for. Can be a single image or a list of images.
                         Defaults to None.

            timeout (float, optional): The maximum time to wait in seconds. Defaults to 10.0.

            contains (bool, optional): If True, checks if the element contains the specified locator.
                                       If False, checks if the element exactly matches the specified locator.
                                       Defaults to True.

            sleep (int): время ожидания перед новым запросом в процессе поллинга.

        Returns:
            bool: True if the element(s) are found within the timeout period, False otherwise.
        """
        if locator is not None:
            if not isinstance(locator, List):
                locator = [locator]

            # Loop through each locator
            start_time = time.time()
            while time.time() - start_time < timeout_method:
                locators_present = False
                for i in locator:
                    # Check if the element is present
                    if not self._get_element(locator=i,
                                             timeout_elem=timeout_elem,
                                             timeout_method=timeout_method,
                                             elements_range=elements_range,
                                             contains=contains,
                                             poll_frequency=poll_frequency,
                                             ignored_exceptions=ignored_exceptions,) is None:
                        locators_present = True
                if not locators_present:
                    return True
                time.sleep(sleep)
            raise TimeoutError

        if image is not None:
            if not isinstance(image, List):
                image = [image]

            # Loop through each image
            start_time = time.time()
            while time.time() - start_time < timeout_method:
                images_present = False
                for i in image:
                    # Check if the image is on the screen within the timeout period
                    if self.helpers._is_image_on_the_screen(image=i, threshold=threshold):
                        images_present = True
                if not images_present:
                    return True
                time.sleep(sleep)
            raise TimeoutError
        return False

    @staticmethod
    def _wait_return_true(method, timeout: float = 10.0, sleep: float = 1.0, *args, **kwargs):
        """
        Ожидает пока метод не вернет True.
        Args:
            method: ссылка на метод
            timeout (float): таймаут на ожидание
            sleep (int): время ожидания перед новым запросом в процессе поллинга.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if method(*args, **kwargs):
                return
            time.sleep(sleep)
        raise TimeoutError


