"""
Модуль исключений для класса AppiumExtended
"""
import traceback
import typing
from typing import Optional, Union, Tuple, List, Dict

import numpy as np
from PIL import Image
from appium.webdriver import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from selenium.types import WaitExcTypes
from selenium.webdriver.common.by import By


class AppiumExtendedError(Exception):
    def __init__(self, message=''):
        super().__init__(message)
        self.message = message


class GetElementError(AppiumExtendedError):
    """
    Возникает, когда попытка получить элемент не удалась.
    """

    def __init__(self,
                 message='',
                 locator=None,
                 by=None,
                 value=None,
                 timeout_elem=None,
                 timeout_method=None,
                 elements_range=None,
                 contains=None,
                 original_exception: Optional[Exception] = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None
                 ):
        message = f"{message}. Args: {locator=}, {by=}, {value=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.by = by
        self.value = value
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.contains = contains
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class GetElementsError(AppiumExtendedError):
    """
    Возникает, когда попытка получить элементы не удалась.
    """

    def __init__(self,
                 message: str = '',
                 locator: Union[Tuple, List[WebElement], Dict[str, str], str] = None,
                 by: Union[MobileBy, AppiumBy, By, str] = None,
                 value: Union[str, Dict, None] = None,
                 timeout_elements: int = None,
                 timeout_method: int = None,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 contains: bool = None,
                 original_exception: Optional[Exception] = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None
                 ):
        message = f"{message}. Args: {locator=}, {by=}, {value=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.by = by
        self.value = value
        self.timeout_elements = timeout_elements
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.contains = contains
        self.poll_frequency = poll_frequency,
        self.ignored_exceptions = ignored_exceptions,
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class GetImageCoordinatesError(AppiumExtendedError):
    """
    Возникает когда попытка найти изображение не удалась
    """

    def __init__(self,
                 message='',
                 image=None,
                 full_image=None,
                 threshold=None,
                 original_exception: Optional[Exception] = None
                 ):
        super().__init__(message)
        self.full_image = full_image,
        self.image = image,
        self.threshold = threshold
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class GetManyCoordinatesOfImageError(AppiumExtendedError):
    """
    Возникает, когда попытка найти все вхождения частичного изображения внутри полного изображения не удалась.
    """

    def __init__(self,
                 message: str = '',
                 image: Union[bytes, str] = None,
                 full_image: Union[bytes, str] = None,
                 cv_threshold: Optional[float] = None,
                 coord_threshold: Optional[int] = None,
                 original_exception: Optional[Exception] = None
                 ):
        super().__init__(message)
        self.image = image
        self.full_image = full_image
        self.cv_threshold = cv_threshold
        self.coord_threshold = coord_threshold
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class GetInnerImageCoordinatesError(AppiumExtendedError):
    """
    Возникает, когда попытка извлечь внутреннее изображение из изображения не удалась.
    """

    def __init__(self,
                 message='',
                 outer_image_path=None,
                 inner_image_path=None,
                 threshold=None,
                 original_exception: Optional[Exception] = None
                 ):
        super().__init__(message)
        self.outer_image_path = outer_image_path,
        self.inner_image_path = inner_image_path,
        self.threshold = threshold
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class GetTextCoordinatesError(AppiumExtendedError):
    """
    Возникает, когда попытка найти координаты текста на изображении или экране не удалась.
    """

    def __init__(self,
                 message: str = '',
                 text: str = None,
                 language: Optional[str] = None,
                 image: Union[bytes, str] = None,
                 ocr: Optional[bool] = None,
                 contains: bool = None,
                 original_exception: Optional[Exception] = None
                 ):
        message = f"{message}. Args: {text=}, {language=}, {ocr=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.text = text
        self.language = language
        self.image = image
        self.ocr = ocr
        self.contains = contains
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class FindAndGetElementError(AppiumExtendedError):
    """
    Возникает, когда попытка найти и извлечь элемент не удалась.
    """

    def __init__(self,
                 message: str = '',
                 locator: Union[Tuple[str, str], 'WebElement', 'WebElementExtended', Dict[str, str], str] = None,
                 tries: int = None,
                 contains: bool = None,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None
                 ):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.tries = tries
        self.contains = contains
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception


class IsElementWithinScreenError(AppiumExtendedError):
    """
    Возникает, когда происходит ошибка при проверке, находится ли элемент на видимом экране.
    """

    def __init__(self,
                 message: str = '',
                 locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 contains: bool = True,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Exception = None
                 ):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.contains = contains
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class IsTextOnScreenError(AppiumExtendedError):
    """
    Возникает, когда происходит ошибка при проверке, присутствует ли заданный текст на экране.
    """

    def __init__(self,
                 message: str = '',
                 text: str = None,
                 language: str = None,
                 ocr: bool = None,
                 contains: bool = None,
                 original_exception: Exception = None
                 ):
        message = f"{message}. Args: {text=}, {language=}, {ocr=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.text = text
        self.language = language
        self.ocr = ocr
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class IsImageOnScreenError(AppiumExtendedError):
    """
    Возникает, когда происходит ошибка при проверке, присутствует ли заданное изображение на экране.
    """

    def __init__(self,
                 message: str = '',
                 image: Union[bytes, str] = None,
                 threshold: float = None,
                 original_exception: Exception = None
                 ):
        super().__init__(message)
        self.image = image
        self.threshold = threshold
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class TapError(AppiumExtendedError):
    """
    Возникает, когда происходит ошибка при выполнении тапа.
    """

    def __init__(self,
                 message: str = '',
                 locator: Union[Tuple[str, str], 'WebElementExtended', 'WebElement', Dict[str, str], str] = None,
                 x: int = None,
                 y: int = None,
                 image: Union[bytes, str] = None,
                 duration: Optional[int] = None,
                 timeout: float = 5,
                 original_exception: Optional[Exception] = None
                 ):
        message = f"{message}. Args: {locator=}, {x=}, {y=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.x = x
        self.y = y
        self.image = image
        self.duration = duration
        self.timeout = timeout
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class SwipeError(AppiumExtendedError):
    """
    Возникает, если свайп не может быть выполнен.
    """

    def __init__(self,
                 message: str = '',
                 start_position=None,
                 end_position=None,
                 direction=None,
                 distance=None,
                 duration=None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {start_position=}, {end_position=}, {direction=}, {distance=}, {duration=}" if "Args:" not in message else message
        super().__init__(message)
        self.start_position = start_position
        self.end_position = end_position
        self.direction = direction
        self.distance = distance
        self.duration = duration
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class WaitForError(AppiumExtendedError):
    """
    Возникает, когда элемент или изображение не появляются на экране в течение заданного времени.
    """

    def __init__(self,
                 message: str = '',
                 locator: Union[Tuple[str, str], WebElement, 'WebElementExtended', Dict[str, str], str,
                 List[Tuple[str, str]], List[WebElement], List['WebElementExtended'], List[Dict[str, str]], List[
                     str]] = None,
                 image: Union[bytes, np.ndarray, Image.Image, str,
                 List[bytes], List[np.ndarray], List[Image.Image], List[str]] = None,
                 contains: bool = True,
                 sleep: int = 1,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.image = image
        self.sleep = sleep
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class WaitForNotError(AppiumExtendedError):
    """
    Возникает, когда элемент или изображение не исчезают с экрана в течение заданного времени.
    """

    def __init__(self,
                 message: str = '',
                 locator=None,
                 image=None,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 contains: bool = True,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.image = image
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class IsWaitForError(AppiumExtendedError):
    def __init__(self,
                 message: str = '',
                 locator=None,
                 image=None,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 contains: bool = True,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.image = image
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class IsWaitForNotError(AppiumExtendedError):

    def __init__(self,
                 message: str = '',
                 locator=None,
                 image=None,
                 timeout_elem: float = 10.0,
                 timeout_method: float = 60.0,
                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                 contains: bool = True,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {locator=}, {contains=}" if "Args:" not in message else message
        super().__init__(message)
        self.locator = locator
        self.image = image
        self.timeout_elem = timeout_elem
        self.timeout_method = timeout_method
        self.elements_range = elements_range
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.contains = contains
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class WaitReturnTrueError(AppiumExtendedError):
    """
    Возникает, когда метод не возвращает True в течение заданного времени.
    """

    def __init__(self,
                 message: str = '',
                 method=None,
                 timeout: int = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {str(method)=}, {timeout=}" if "Args:" not in message else message
        super().__init__(message)
        self.method = method
        self.timeout = timeout
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class DrawByCoordinatesError(AppiumExtendedError):
    """
    Возникает, когда не удается нарисовать прямоугольник на изображении.
    """

    def __init__(self,
                 message: str = '',
                 coordinates: Tuple[int, int, int, int] = None,
                 top_left: Tuple[int, int] = None,
                 bottom_right: Tuple[int, int] = None,
                 path: str = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {coordinates=}, {top_left=}, {bottom_right=}, {path=}" if "Args:" not in message else message
        super().__init__(message)
        self.coordinates = coordinates
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.path = path
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ExtractPointCoordinatesByTypingError(AppiumExtendedError):
    """
    Возникает, когда не удается извлечь координаты точки на основе типа переданной позиции.
    """

    def __init__(self,
                 message: str = '',
                 position: Union[Tuple[int, int], str, bytes, 'np.ndarray', 'Image.Image',
                 Tuple[str, str], Dict, WebElement, 'WebElementExtended'] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {position=}" if "Args:" not in message else message
        super().__init__(message)
        self.position = position
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class ExtractPointCoordinatesError(AppiumExtendedError):
    """
    Возникает, когда не удается извлечь координаты точки на основе заданных параметров.
    """

    def __init__(self,
                 message: str = '',
                 direction: int = None,
                 distance: int = None,
                 start_x: int = None,
                 start_y: int = None,
                 screen_resolution: Tuple[int, int] = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {direction=}, {distance=}, {start_x=}, {start_y=}, {screen_resolution=}" if "Args:" not in message else message
        super().__init__(message)
        self.direction = direction
        self.distance = distance
        self.start_x = start_x
        self.start_y = start_y
        self.screen_resolution = screen_resolution
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class GetScreenshotError(AppiumExtendedError):
    """
    Возникает, когда не удается получить скриншот экрана.
    """

    def __init__(self,
                 message: str = '',
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class SaveScreenshotError(AppiumExtendedError):
    """
    Возникает, когда не удается сохранить скриншот.
    """

    def __init__(self,
                 message: str = '',
                 path: str = None,
                 filename: str = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {path=}, {filename=}" if "Args:" not in message else message
        super().__init__(message)
        self.path = path
        self.filename = filename
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class SaveSourceError(AppiumExtendedError):
    """
    Возникает, когда не удается сохранить исходный код страницы.
    """

    def __init__(self,
                 message: str = '',
                 path: str = None,
                 filename: str = None,
                 original_exception: Optional[Exception] = None):
        message = f"{message}. Args: {path=}, {filename=}" if "Args:" not in message else message
        super().__init__(message)
        self.path = path
        self.filename = filename
        self.original_exception = original_exception
        self.traceback = traceback.format_exc()


class WebElementExtendedError(AppiumExtendedError):
    """
    Возникает, когда выбрасывается исключение из класса WebElementExtended
    """

    def __init__(self,
                 message='',
                 original_exception: Optional[Exception] = None,
                 poll_frequency: float = 0.5,
                 ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                 *args, **kwargs,
                 ):
        super().__init__(message)
        self.poll_frequency = poll_frequency
        self.ignored_exceptions = ignored_exceptions
        self.traceback = traceback.format_exc()
        self.original_exception = original_exception
        self.args = args
        self.kwargs = kwargs


