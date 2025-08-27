import inspect
import logging
import os
import time
import typing
from typing import Union, Tuple, Dict, List, Optional, cast, Any
import numpy as np
from PIL import Image

from selenium.common.exceptions import NoSuchDriverException, WebDriverException, StaleElementReferenceException, \
    InvalidSessionIdException
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver import WebElement
from selenium.types import WaitExcTypes

from selenium.webdriver.common.by import By

from appium_extended.appium_swipe import AppiumSwipe
from appium_extended.appium_wait import AppiumWait
from appium_extended.appium_tap import AppiumTap
from appium_extended.appium_is import AppiumIs
from appium_extended_exceptions.appium_extended_exceptions import TapError, GetElementError, GetElementsError, \
    GetImageCoordinatesError, GetInnerImageCoordinatesError, GetManyCoordinatesOfImageError, GetTextCoordinatesError, \
    FindAndGetElementError, IsElementWithinScreenError, IsTextOnScreenError, IsImageOnScreenError, SaveSourceError, \
    GetScreenshotError, ExtractPointCoordinatesError, ExtractPointCoordinatesByTypingError, SaveScreenshotError, \
    DrawByCoordinatesError, WaitReturnTrueError, WaitForNotError, WaitForError, SwipeError, AppiumExtendedError, \
    IsWaitForError, IsWaitForNotError, WebElementExtendedError

from appium_extended_web_element.web_element_extended import WebElementExtended

from appium_extended_utils import utils


class AppiumExtended(AppiumIs, AppiumTap, AppiumSwipe, AppiumWait):
    """
    Класс работы с Appium.
    Обеспечивает работу с устройством
    """

    def __init__(self, logger: logging.Logger = None, log_level: int = logging.INFO,
                 log_path: str = '', secure_screenshot: bool = False):
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(log_level)
        if bool(log_path):
            if not log_path.endswith('.log'):
                log_path = log_path + '.log'
            file_handler = logging.FileHandler(log_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def get_element(self,
                    locator: Union[Tuple, WebElementExtended, Dict[str, str], str] = None,
                    by: Union[MobileBy, AppiumBy, By, str] = None,
                    value: Union[str, Dict, None] = None,
                    timeout_elem: float = 10.0,
                    timeout_method: float = 60.0,
                    elements_range: Union[Tuple, List[WebElementExtended], Dict[str, str], None] = None,
                    contains: bool = True,
                    poll_frequency: float = 0.5,
                    tries: int = 3,
                    ignored_exceptions: typing.Optional[WaitExcTypes] = None
                    ) -> Union[WebElementExtended, None]:
        """
        Метод обеспечивает поиск элемента в текущей DOM структуре.
        Должен принимать либо локатор, либо значения by и value.

        Args:
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str], optional):
                Определяет локатор элемента.
                Tuple - локатор в виде кортежа из двух строковых элементов,
                    где первый это стратегия поиска, а второй это селектор, например ("id", "android.widget.ProgressBar").
                Dict - локатор в виде словаря атрибутов и их значений искомого элемента,
                    например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.
                str - путь до изображения. Будет искать изображение, вычислять координаты и
                      искать в DOM ближайший к этим координатам элемент

            by (Union[MobileBy, AppiumBy, By, str], optional):
                Тип локатора для поиска элемента (всегда в связке с value).
                Как в стандартном методе driver.find_element.
            value (Union[str, Dict, None], optional):
                Значение локатора или словарь аргументов, если используется XPATH.
            timeout_elem (int, optional):
                Время ожидания элемента. По умолчанию 10 секунд.
            timeout_method (int, optional):
                Время ожидания метода поиска элемента. По умолчанию 600 секунд.
            elements_range (Union[Tuple, List[WebElement], Dict[str, str], None], optional):
                Ограничивает поиск элемента в указанном диапазоне (для поиска по изображению).
            contains (bool, optional):
                Для поиска по dict и атрибуту 'text',
                True - ищет элемент содержащий фрагмент значения
                False - по строгому соответствию.
                По умолчанию True.

        Usages:
            element = app._get_element(locator=("id", "foo"))
            element = app._get_element(element)
            element = app._get_element(locator={'text': 'foo'}, contains=True)
            element = app._get_element(locator='/path/to/file/image.png')
            element = app._get_element(by="id", value="backButton")
            element = app._get_element(by=MobileBy.ID, value="backButton")

        Returns:
            Union[WebElementExtended, None]: Возвращает WebElementExtended, если элемент найден, иначе None.
        """
        element = None
        try:
            for i in range(tries):
                try:
                    element = self._get_element(locator=locator,
                                                by=by,
                                                value=value,
                                                timeout_elem=timeout_elem,
                                                timeout_method=timeout_method,
                                                elements_range=elements_range,
                                                contains=contains,
                                                poll_frequency=poll_frequency,
                                                ignored_exceptions=ignored_exceptions)
                except StaleElementReferenceException:
                    time.sleep(3)
                    continue
                if element is None:
                    time.sleep(1)
                    continue
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetElementError(message=f"Ошибка при попытке извлечь элемент {error}",
                                  locator=locator,
                                  by=by,
                                  value=value,
                                  timeout_elem=timeout_elem,
                                  timeout_method=timeout_method,
                                  elements_range=elements_range,
                                  contains=contains,
                                  original_exception=error,
                                  poll_frequency=poll_frequency,
                                  ignored_exceptions=ignored_exceptions
                                  ) from error
        if element is None:
            raise GetElementError(message="Элемент не найден",
                                  locator=locator,
                                  by=by,
                                  value=value,
                                  timeout_elem=timeout_elem,
                                  timeout_method=timeout_method,
                                  elements_range=elements_range,
                                  contains=contains,
                                  poll_frequency=poll_frequency,
                                  ignored_exceptions=ignored_exceptions
                                  )
        return WebElementExtended(base=self, element_id=element.id)

    def get_elements(self,
                     locator: Union[Tuple, List[WebElement], Dict[str, str], str] = None,
                     by: Union[MobileBy, AppiumBy, By, str] = None,
                     value: Union[str, Dict, None] = None,
                     timeout_elements: int = 10,
                     timeout_method: int = 60,
                     elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                     contains: bool = True,
                     poll_frequency: float = 0.5,
                     ignored_exceptions: typing.Optional[WaitExcTypes] = None
                     ) -> Union[List[WebElementExtended], List]:
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

        Returns:
            Union[List[WebElementExtended], List]: Возвращает список объектов WebElementExtended,
            если элементы найдены, иначе пустой список.
        """
        elements = None
        try:
            elements = super()._get_elements(locator=locator,
                                             by=by,
                                             value=value,
                                             timeout_elements=timeout_elements,
                                             timeout_method=timeout_method,
                                             elements_range=elements_range,
                                             contains=contains,
                                             poll_frequency=poll_frequency,
                                             ignored_exceptions=ignored_exceptions
                                             )
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetElementsError(message=f"Ошибка при попытке извлечь элементы: {error}",
                                   by=by,
                                   value=value,
                                   timeout_elements=timeout_elements,
                                   timeout_method=timeout_method,
                                   elements_range=elements_range,
                                   contains=contains,
                                   original_exception=error,
                                   poll_frequency=poll_frequency,
                                   ignored_exceptions=ignored_exceptions
                                   ) from error
        if elements is None:
            raise GetElementsError(message="Элементы не найдены",
                                   by=by,
                                   value=value,
                                   timeout_elements=timeout_elements,
                                   timeout_method=timeout_method,
                                   elements_range=elements_range,
                                   contains=contains,
                                   poll_frequency=poll_frequency,
                                   ignored_exceptions=ignored_exceptions
                                   )
        elements_ext = []
        for element in elements:
            elements_ext.append(
                WebElementExtended(base=self, element_id=element.id))
        return elements_ext

    def get_image_coordinates(self,
                              image: Union[bytes, np.ndarray, Image.Image, str],
                              full_image: Union[bytes, np.ndarray, Image.Image, str] = None,
                              threshold: float = 0.7,
                              ) -> Union[Tuple, None]:
        """
        Находит координаты наиболее вероятного совпадения частичного изображения в полном изображении.

        Args:
            image (Union[bytes, np.ndarray, Image.Image, str]):
                Частичное изображение или путь к файлу, которое нужно найти внутри полного изображения.
            full_image (Union[bytes, np.ndarray, Image.Image, str], optional):
                Полное изображение или путь к файлу. По умолчанию None, в этом случае используется скриншот экрана.
            threshold (float, optional):
                Минимальный порог совпадения для считывания совпадения допустимым. По умолчанию 0.7.

        Usages:
            app.get_image_coordinates('path/to/partial_image.png', 'path/to/full_image.png')
            app.get_image_coordinates('path/to/partial_image.png', threshold=0.8)

        Returns:
            Union[Tuple[int, int, int, int], None]:
                Кортеж с координатами наиболее вероятного совпадения (x1, y1, x2, y2)
                или None, если совпадение не найдено.

        Note:
            При неудаче повторяет выполнение, до трёх раз.
        """
        coordinates = None
        try:
            coordinates = self._get_image_coordinates(full_image=full_image,
                                                      image=image,
                                                      threshold=threshold)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetImageCoordinatesError(message=f"Ошибка при попытке извлечения координат изображения: {error}",
                                           full_image=full_image,
                                           image=image,
                                           threshold=threshold,
                                           original_exception=error
                                           ) from error
        if coordinates is None:
            raise GetImageCoordinatesError(message="Изображение не найдено",
                                           full_image=full_image,
                                           image=image,
                                           threshold=threshold
                                           )
        return coordinates

    def get_inner_image_coordinates(self,
                                    outer_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                    inner_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                    threshold: Optional[float] = 0.9
                                    ) -> Union[Tuple[int, int, int, int], None]:
        """
        Сначала находит изображение на экране,
        затем внутри него находит внутреннее изображение.

        Args:
            outer_image_path (Union[bytes, np.ndarray, Image.Image, str]):
                Внешнее изображение или путь к файлу, которое нужно найти на экране.
            inner_image_path (Union[bytes, np.ndarray, Image.Image, str]):
                Внутреннее изображение или путь к файлу, которое нужно найти внутри внешнего изображения.
            threshold (float, optional):
                Пороговое значение сходства для шаблонного сопоставления. По умолчанию 0.9.

        Usages:
            app.get_inner_image_coordinates('path/to/outer_image.png', 'path/to/inner_image.png')
            app.get_inner_image_coordinates('path/to/outer_image.png', 'path/to/inner_image.png', threshold=0.8)

        Returns:
            Union[Tuple[int, int, int, int], None]:
                Координаты внутреннего изображения относительно экрана в формате (x1, y1, x2, y2).
                Если внутреннее изображение не найдено, возвращает None.

        Note:
            При неудаче повторяет выполнение, до трёх раз.
        """
        inner_image_coordinates = None
        try:
            inner_image_coordinates = self._get_inner_image_coordinates(outer_image_path=outer_image_path,
                                                                        inner_image_path=inner_image_path,
                                                                        threshold=threshold)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetInnerImageCoordinatesError(message=f"Ошибка при попытке извлечь внутреннее изображение: {error}",
                                                outer_image_path=outer_image_path,
                                                inner_image_path=inner_image_path,
                                                threshold=threshold,
                                                original_exception=error
                                                ) from error
        if inner_image_coordinates is None:
            raise GetInnerImageCoordinatesError(message="Внутреннее изображение не найдено",
                                                outer_image_path=outer_image_path,
                                                inner_image_path=inner_image_path,
                                                threshold=threshold
                                                )
        return inner_image_coordinates

    def get_many_coordinates_of_image(self,
                                      image: Union[bytes, np.ndarray, Image.Image, str],
                                      full_image: Union[bytes, np.ndarray, Image.Image, str] = None,
                                      cv_threshold: Optional[float] = 0.7,
                                      coord_threshold: Optional[int] = 5,
                                      ) -> Union[List[Tuple], None]:
        """
        Находит все вхождения частичного изображения внутри полного изображения.

        Args:
            image (Union[bytes, np.ndarray, Image.Image, str]):
                Частичное изображение или путь к файлу, которое нужно найти внутри полного изображения.
            full_image (Union[bytes, np.ndarray, Image.Image, str], optional):
                Полное изображение или путь к файлу. По умолчанию None, в этом случае используется скриншот экрана.
            cv_threshold (float, optional):
                Минимальный порог совпадения для считывания совпадения допустимым. По умолчанию 0.7.
            coord_threshold (int, optional):
                Максимальное различие между значениями x и y двух кортежей,
                чтобы они считались слишком близкими друг к другу.
                По умолчанию 5 пикселей.

        Usages:
            app.et_many_coordinates_of_image('path/to/partial_image.png', 'path/to/full_image.png')
            app.get_many_coordinates_of_image('path/to/partial_image.png', cv_threshold=0.8, coord_threshold=10)

        Returns:
            Union[List[Tuple], None]:
                Список кортежей, содержащий расположение каждого найденного совпадения в формате (x1, y1, x2, y2).
                Если совпадений не найдено, возвращает None.

        Note:
            При неудаче повторяет выполнение, до трёх раз.
        """
        coordinates = None
        try:
            coordinates = self.get_many_coordinates_of_image(full_image=full_image,
                                                             image=image,
                                                             cv_threshold=cv_threshold,
                                                             coord_threshold=coord_threshold)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetManyCoordinatesOfImageError(
                message=f"Ошибка при попытке извлечения координат изображений: {error}",
                image=image,
                full_image=full_image,
                cv_threshold=cv_threshold,
                coord_threshold=coord_threshold,
                original_exception=error) from error
        if coordinates is None:
            raise GetManyCoordinatesOfImageError(message="Совпадения не найдены",
                                                 image=image,
                                                 full_image=full_image,
                                                 cv_threshold=cv_threshold,
                                                 coord_threshold=coord_threshold)
        return coordinates

    def get_text_coordinates(self,
                             text: str,
                             language: Optional[str] = 'rus',
                             image: Union[bytes, str, Image.Image, np.ndarray] = None,
                             ocr: Optional[bool] = True,
                             timeout_elem: float = 10.0,
                             timeout_method: float = 60.0,
                             elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                             contains: bool = True,
                             poll_frequency: float = 0.5,
                             ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                             ) -> Union[tuple[int, ...], tuple[int, int, int, int], None]:
        """
        Возвращает координаты области с указанным текстом на предоставленном изображении или снимке экрана.
        Метод может работать в двух режимах: с использованием OCR (оптического распознавания символов) или
        с использованием метода get_element для поиска элемента по тексту.

        Args:
            - text (str): Искомый текст.
            - image (bytes, str, Image.Image, np.ndarray, опционально): Изображение, на котором
                осуществляется поиск текста. Для OCR поиска.
                Если не указано, будет использован снимок экрана. По умолчанию None.
            - language (str, опционально): Язык для распознавания текста. По умолчанию 'rus'.
                Для OCR поиска.
            - ocr (bool, опционально): Использовать ли OCR для поиска текста. По умолчанию True.
            - contains (bool): Искать строгое соответствие текста или вхождение. Для поиска по DOM.

        Usages:
            app.get_text_coordinates("Hello, world!")
            app.get_text_coordinates("Привет, мир!", language='rus')
            app.get_text_coordinates("Hello, world!", image='path/to/image.png')
            app.get_text_coordinates("Hello, world!", ocr=False, contains=False)

        Returns:
        - Union[Tuple[int, int, int, int], None]: Координаты области с текстом или None, если текст не найден.
          Если ocr=False, возвращаются координаты, полученные с помощью метода get_element.
        """
        coordinates = None
        if ocr:
            try:
                coordinates = self._get_text_coordinates(text=text, language=language, image=image)
            except NoSuchDriverException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except InvalidSessionIdException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except WebElementExtendedError as error:
                raise GetTextCoordinatesError(message=f"""
                                Ошибка при попытке найти координаты изображения с использованием OCR: {error}""",
                                              text=text,
                                              language=language,
                                              image=image,
                                              ocr=True,
                                              original_exception=error) from error
            except Exception as error:
                raise GetTextCoordinatesError(message=f"""
                Ошибка при попытке найти координаты изображения с использованием OCR: {error}""",
                                              text=text,
                                              language=language,
                                              image=image,
                                              ocr=True,
                                              original_exception=error) from error
            if coordinates is None:
                raise GetTextCoordinatesError(message="Текст не найден при использовании OCR",
                                              text=text,
                                              language=language,
                                              image=image,
                                              ocr=True)
            return coordinates
        else:
            try:
                return self.get_element(locator={'text': text, 'displayed': 'true', 'enabled': 'true'},
                                        timeout_elem=timeout_elem,
                                        timeout_method=timeout_method,
                                        elements_range=elements_range,
                                        contains=contains,
                                        poll_frequency=poll_frequency,
                                        ignored_exceptions=ignored_exceptions, ).get_coordinates()
            except NoSuchDriverException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except InvalidSessionIdException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except Exception as error:
                raise GetTextCoordinatesError(message=f"""
                Ошибка при попытке найти координаты изображения с использованием поиска по DOM: {error}""",
                                              text=text,
                                              contains=contains,
                                              ocr=False,
                                              original_exception=error) from error

    # DOM

    def get_element_contains(self,
                             ) -> Any:
        """
        Возвращает элемент содержащий определенный элемент.
        Не реализован.
        """
        raise NotImplementedError("Метод еще не реализован.")  # TODO implement

    def get_elements_contains(self,
                              ) -> Any:
        """
        Возвращает элементы содержащие определенный(е) элемент(ы).
        Не реализован.
        """
        raise NotImplementedError("Метод еще не реализован.")  # TODO implement

    def find_and_get_element(self,
                             locator: Union[Tuple[str, str], WebElement, 'WebElementExtended', Dict[str, str], str],
                             timeout_elem: float = 10.0,
                             timeout_method: float = 60.0,
                             elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                             contains: bool = True,
                             poll_frequency: float = 0.5,
                             ignored_exceptions: typing.Optional[WaitExcTypes] = None,
                             tries: int = 3,
                             ) -> Union[WebElementExtended, None]:
        """
        Ищет элемент на странице и возвращает его. Если элемент не найден, метод прокручивает
        все прокручиваемые элементы и повторяет попытку поиска указанное количество попыток.

        Args:
            locator (Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str]):
                Определяет локатор элемента.
                Tuple - локатор в виде кортежа из двух строковых элементов,
                    где первый это стратегия поиска, а второй это селектор,
                    например ("id", "android.widget.ProgressBar").
                Dict - локатор в виде словаря атрибутов и их значений искомого элемента,
                    например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.
                str - путь до изображения. Будет искать изображение, вычислять координаты и
                      искать в DOM ближайший к этим координатам элемент
            timeout (int): Максимальное время ожидания для поиска элемента в секундах. По умолчанию 10 секунд.
            tries (int): Количество попыток прокрутки и поиска элемента. По умолчанию 3 попытки.
            contains (bool): Искать строгое соответствие или вхождение текста.
                Только для поиска по словарю с аргументом 'text'

        Returns:
            WebElementExtended или None: Возвращает найденный элемент или None, если элемент не найден
            после всех попыток.

        Raises:
            ValueError: Возникает, если элемент не найден. Исключение вызывается внутренним методом get_element.
        """
        try:
            element = self.get_element(locator=locator,
                                       timeout_elem=timeout_elem,
                                       timeout_method=timeout_method,
                                       elements_range=elements_range,
                                       contains=contains,
                                       poll_frequency=poll_frequency,
                                       tries=tries,
                                       ignored_exceptions=ignored_exceptions)
            return element
        except GetElementError:
            pass
        for i in range(tries):
            try:
                recyclers = self.get_elements(
                    locator={'scrollable': 'true', 'enabled': 'true', 'displayed': 'true'})
                if recyclers is None:
                    raise FindAndGetElementError(message="Не удалось обнаружить прокручиваемые элементы на экране",
                                                 locator=locator,
                                                 timeout_elem=timeout_elem,
                                                 timeout_method=timeout_method,
                                                 elements_range=elements_range,
                                                 contains=contains,
                                                 poll_frequency=poll_frequency,
                                                 ignored_exceptions=ignored_exceptions,
                                                 tries=tries, )
                for recycler in recyclers:
                    recycler.scroll_until_find(locator=locator, timeout_method=timeout_method, contains=contains)
                    return self.get_element(locator=locator,
                                            timeout_elem=timeout_elem,
                                            timeout_method=timeout_method,
                                            elements_range=elements_range,
                                            contains=contains,
                                            poll_frequency=poll_frequency,
                                            ignored_exceptions=ignored_exceptions, )
            except NoSuchDriverException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except InvalidSessionIdException as error:
                self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
                self.logger.error(error)
                self.reconnect()
            except StaleElementReferenceException:
                continue
            except WebElementExtendedError:
                continue
            except GetElementsError:
                continue
            except GetElementError as error:
                continue
        raise FindAndGetElementError(message="Не удалось извлечь элемент",
                                     locator=locator,
                                     timeout_elem=timeout_elem,
                                     timeout_method=timeout_method,
                                     elements_range=elements_range,
                                     contains=contains,
                                     poll_frequency=poll_frequency,
                                     ignored_exceptions=ignored_exceptions,
                                     tries=tries)

    def is_element_within_screen(self,
                                 locator: Union[Tuple, WebElement, 'WebElementExtended', Dict[str, str], str] = None,
                                 timeout_elem: float = 10.0,
                                 timeout_method: float = 60.0,
                                 elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
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
                    str - путь до изображения. Будет искать изображение, вычислять координаты и
                      искать в DOM ближайший к этим координатам элемент
            timeout (int): Время ожидания элемента. Значение по умолчанию: 10.
            contains (bool): Искать строгое соответствие или вхождение текста.
                Только для поиска по словарю с аргументом 'text'

        Returns:
            bool: True, если элемент находится на экране, False, если нет.

        Note:
            Проверяет атрибут: 'displayed'.
        """
        try:
            return self._is_element_within_screen(locator=locator,
                                                  timeout_elem=timeout_elem,
                                                  timeout_method=timeout_method,
                                                  elements_range=elements_range,
                                                  contains=contains,
                                                  poll_frequency=poll_frequency,
                                                  ignored_exceptions=ignored_exceptions, )
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise IsElementWithinScreenError(message=f"""
            Ошибка при проверке, находится ли элемент на видимом экране: {error}""",
                                             locator=locator,
                                             timeout_elem=timeout_elem,
                                             timeout_method=timeout_method,
                                             elements_range=elements_range,
                                             contains=contains,
                                             poll_frequency=poll_frequency,
                                             ignored_exceptions=ignored_exceptions,
                                             original_exception=error) from error

    def is_text_on_screen(self,
                          text: str,
                          language: str = 'rus',
                          ocr: bool = True,
                          timeout_elem: float = 10.0,
                          timeout_method: float = 60.0,
                          elements_range: Union[Tuple, List[WebElement], Dict[str, str], None] = None,
                          contains: bool = True,
                          poll_frequency: float = 0.5,
                          ignored_exceptions: typing.Optional[WaitExcTypes] = None
                          ) -> bool:
        """
        Проверяет, присутствует ли заданный текст на экране.
        Если ocr=True:
            Распознавание текста производит с помощью библиотеки pytesseract.
        Если ocr=False:
            Производится поиск элемента по xpath.

        Аргументы:
        - text (str): Текст, который нужно найти на экране.
        - ocr (bool): Производить поиск по изображению или DOM.
        - language (str): Язык распознавания текста. Значение по умолчанию: 'rus'.
        - contains (bool): Только для ocr=False. Допускает фрагмент текста

        Возвращает:
        - bool: True, если заданный текст найден на экране. False в противном случае.
        """
        try:
            if ocr:
                return self.helpers.is_text_on_ocr_screen(text=text, language=language)
            return self._is_element_within_screen(locator={'text': text},
                                                  timeout_elem=timeout_elem,
                                                  timeout_method=timeout_method,
                                                  elements_range=elements_range,
                                                  contains=contains,
                                                  poll_frequency=poll_frequency,
                                                  ignored_exceptions=ignored_exceptions,
                                                  )
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise IsTextOnScreenError(message=f"""
            Ошибка при проверке, присутствует ли заданный текст на экране: {error}""",
                                      text=text,
                                      language=language,
                                      ocr=ocr,
                                      contains=contains,
                                      original_exception=error) from error

    def is_image_on_the_screen(self,
                               image: Union[bytes, np.ndarray, Image.Image, str],
                               threshold: float = 0.9,
                               ) -> bool:
        """
        Сравнивает, присутствует ли заданное изображение на экране.

        Args:
            image (Union[bytes, np.ndarray, Image.Image, str]): Изображение для поиска на экране.
                Может быть в формате байтов, массива numpy, объекта Image.Image или строки с путем до файла.
            threshold (float): Пороговое значение схожести части изображения со снимком экрана.

        Returns:
            bool: Возвращает `True`, если изображение найдено на экране, иначе `False`.

        Raises:
            cv2.error: Ошибки, связанные с OpenCV.
            AssertionError: Ошибки, связанные с неверными размерами изображений.
            Exception: Остальные исключения.
        """
        try:
            return self.helpers._is_image_on_the_screen(image=image, threshold=threshold)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise IsImageOnScreenError(message=f"""
            Ошибка при проверке, присутствует ли заданное изображение на экране: {error}""",
                                       image=image,
                                       threshold=threshold,
                                       original_exception=error) from error

    def to_ndarray(self, image: Union[bytes, np.ndarray, Image.Image, str], grayscale: bool = True) -> np.ndarray:
        """
        Преобразует входные данные из различных типов в ndarray (NumPy array).

        Аргументы:
        - image: Union[bytes, np.ndarray, Image.Image, str] - Входные данные,
          представляющие изображение. Может быть типами bytes, np.ndarray, PIL Image или str.

        Возвращает:
        - np.ndarray - Преобразованный массив NumPy (ndarray) представляющий изображение.
        """
        try:
            return self.helpers._to_ndarray(image=image, grayscale=grayscale)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()

    def tap(self,
            locator: Union[Tuple[str, str], WebElementExtended, WebElement, Dict[str, str], str] = None,
            x: int = None,
            y: int = None,
            image: Union[bytes, np.ndarray, Image.Image, str] = None,
            duration: Optional[int] = None,
            timeout: float = 5.0,
            threshold: float = 0.9
            ) -> 'AppiumExtended':
        """
        Выполняет тап по заданным координатам, элементу или изображению на экране.

        Args:
            locator (Union[Tuple[str, str], WebElementExtended, WebElement, Dict[str, str], str], optional):
                Определяет локатор элемента.
                -Tuple: - локатор в виде кортежа из двух строковых элементов,
                где первый это стратегия поиска, а второй это селектор, например ("id", "android.widget.ProgressBar").
                -Dict: - локатор в виде словаря атрибутов и их значений искомого элемента,
                например {'text': 'foo', 'displayed' : 'true', 'enabled': 'true'}.
                -str: - путь до изображения. Будет искать изображение, вычислять координаты и
                искать в DOM ближайший к этим координатам элемент
                Применяется, если image = None.
            x (int, optional): Координата X для тапа. Используется, если `locator` не указан.
            y (int, optional): Координата Y для тапа. Используется, если `locator` не указан.
            image (Union[bytes, np.ndarray, Image.Image, str], optional):
            Изображение, по которому нужно тапнуть (в центр). Используется, если `locator` и координаты не указаны.
            duration (int, optional): Длительность тапа в миллисекундах.
            timeout (int): Максимальное время ожидания для поиска элемента или изображения.

        Usages:
            tap(locator=("id", "some_id"))
            tap(x=50, y=50)
            tap(image="path/to/image.png", duration=3)

        Returns:
            AppiumExtended: Возвращает экземпляр класса AppiumExtended (self).

        Raises:
            AssertionError: Если тап не удался.
        """
        try:
            if locator is not None:
                # Извлечение координат
                x, y = self._extract_point_coordinates_by_typing(locator)
            if image is not None:
                start_time = time.time()
                while not self.helpers._is_image_on_the_screen(image=image, threshold=threshold) \
                        and time.time() - start_time < timeout:
                    time.sleep(1)
                # Извлечение координат
                x, y = self._extract_point_coordinates_by_typing(image)
            if not self._tap(x=x, y=y, duration=duration):
                raise TapError(message="Tap не удался",
                               locator=locator,
                               x=x, y=y,
                               image=image,
                               duration=duration,
                               timeout=timeout)
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise TapError(message=f"Ошибка при выполнении tap: {error}",
                           locator=locator,
                           x=x,
                           y=y,
                           image=image,
                           duration=duration,
                           timeout=timeout,
                           original_exception=error) from error

    # SWIPE
    def swipe(self,
              start_position: Union[
                  Tuple[int, int], str, bytes, np.ndarray, Image.Image, WebElement, WebElementExtended, Tuple[str, str],
                  Dict[str, str]],
              end_position: Optional[Union[
                  Tuple[int, int], str, bytes, np.ndarray, Image.Image, WebElement, WebElementExtended, Tuple[str, str],
                  Dict[str, str]]] = None,
              direction: Optional[int] = None,
              distance: Optional[int] = None,
              duration: Optional[int] = 0,
              ) -> 'AppiumExtended':
        """
        Выполняет свайп (перетаскивание) элемента или изображения на экране.

        Args:
            start_position: Позиция начала свайпа. Может быть задана в различных форматах:
                - Если start_position является кортежем и оба его элемента являются строками, то он представляет собой
                  локатор элемента. Например ('id', 'elementId'). В этом случае будет выполнен поиск элемента и используется его позиция.
                - Если start_position является словарем, то считается, что это локатор элемента, основанный на атрибутах.
                  Например, {'text': 'some text'} или {'class': 'SomeClass', 'visible': 'true'}. В этом случае будет
                  выполнен поиск элемента по указанным атрибутам, и используется его позиция.
                - Если start_position является экземпляром класса WebElement или WebElementExtended, то используется его
                  позиция.
                - Если start_position является строкой, массивом байтов (bytes), массивом NumPy (np.ndarray) или объектом
                  класса Image.Image, то считается, что это изображение. В этом случае будет вычислен центр изображения и
                  используется его позиция.
                - Если start_position является кортежем, и оба его элемента являются целыми числами, то считается, что это
                  координаты в формате (x_coordinate, y_coordinate).

            end_position: (Optional) Позиция конца свайпа. Принимает те же форматы, что и start_position.
            direction: (Optional) Направление свайпа, в градусах.
            distance: (Optional) Расстояние свайпа, в пикселях.
            duration: (Optional) Продолжительность свайпа, в миллисекундах.

        Usages:
            - swipe(start_position=(100, 100), end_position=(200, 200))
            - swipe(start_position=('id', 'elementId'), direction=90, distance=100)

        Returns:
            Возвращает экземпляр класса AppiumExtended (self).

        Notes:
            - В качестве конечной позиции свайпа должен быть указан end_position или пара direction, distance.
            - str принимается как путь к изображению на экране и вычисляется его центр, а не как локатор элемента.
        """
        try:
            # Извлечение координат начальной точки свайпа
            start_x, start_y = self._extract_point_coordinates_by_typing(start_position)

            if end_position is not None:
                # Извлечение координат конечной точки свайпа
                end_x, end_y = self._extract_point_coordinates_by_typing(end_position)
            else:
                # Извлечение координат конечной точки свайпа на основе направления и расстояния
                end_x, end_y = self._extract_point_coordinates_by_direction(direction, distance, start_x, start_y,
                                                                            screen_resolution=self.terminal.get_screen_resolution())

            # Выполнение свайпа
            if not self._swipe(start_x=start_x, start_y=start_y,
                               end_x=end_x, end_y=end_y,
                               duration=duration):
                raise SwipeError(message=f"Не удалось выполнить свайп",
                                 start_position=start_position,
                                 end_position=end_position,
                                 direction=duration,
                                 distance=distance,
                                 duration=duration)

            # Возвращаем экземпляр класса appium_extended
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise SwipeError(message=f"Ошибка при попытке выполнения свайпа: {error}",
                             start_position=start_position,
                             end_position=end_position,
                             direction=duration,
                             distance=distance,
                             duration=duration,
                             original_exception=error) from error

    def swipe_right_to_left(self) -> 'AppiumExtended':
        """
        Выполняет свайп (нажать, провести, отпустить) справа налево по горизонтальной оси экрана.

        Args:
            Метод не принимает аргументов.

        Usages:
            app.swipe_right_to_left()

        Returns:
            AppiumExtended: Возвращает экземпляр текущего объекта для возможности цепочного вызова методов.

        Raises:
            None: Метод не вызывает исключений, но внутренние методы (см. swipe), которые он вызывает, могут вызывать исключения.

        Notes:
            Этот метод использует текущее разрешение экрана для определения начальной и конечной точек свайпа.
            Свайп начинается с 90% ширины экрана и заканчивается на 10% ширины экрана, сохраняя при этом
            вертикальную координату на уровне 50% от высоты экрана.
        """
        window_size = self.terminal.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        self.swipe(start_position=(right, height // 2),
                   end_position=(left, height // 2))
        # Возвращаем экземпляр класса appium_extended
        return cast('AppiumExtended', self)

    def swipe_left_to_right(self) -> 'AppiumExtended':
        """
        Выполняет свайп с левой стороны экрана на правую по горизонтальной оси.

        Args:
            Метод не принимает аргументов.

        Usages:
            app.swipe_left_to_right()

        Returns:
            AppiumExtended: Возвращает экземпляр текущего объекта для возможности цепочного вызова методов.

        Raises:
            None: Метод не вызывает исключений, но внутренние методы, которые он вызывает, могут вызывать исключения.

        Notes:
            Свайп начинается с 10% ширины экрана и заканчивается на 90% ширины экрана, сохраняя вертикальную координату на уровне 50% от высоты экрана.
        """
        window_size = self.terminal.get_screen_resolution()
        width = window_size[0]
        height = window_size[1]
        left = int(width * 0.1)
        right = int(width * 0.9)
        self.swipe(start_position=(left, height // 2),
                   end_position=(right, height // 2))
        # Возвращаем экземпляр класса appium_extended
        return cast('AppiumExtended', self)

    def swipe_top_to_bottom(self) -> 'AppiumExtended':
        """
        Выполняет свайп сверху вниз по вертикальной оси экрана.

        Args:
            Метод не принимает аргументов.

        Usages:
            app.swipe_top_to_bottom()

        Returns:
            AppiumExtended: Возвращает экземпляр текущего объекта для возможности цепочного вызова методов.

        Raises:
            None: Метод не вызывает исключений, но внутренние методы, которые он вызывает, могут вызывать исключения.

        Notes:
            Свайп начинается с 10% высоты экрана и заканчивается на 90% высоты экрана, сохраняя горизонтальную координату на уровне 50% от ширины экрана.
        """
        window_size = self.terminal.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        self.swipe(start_position=(top, height // 2),
                   end_position=(bottom, height // 2))
        # Возвращаем экземпляр класса appium_extended
        return cast('AppiumExtended', self)

    def swipe_bottom_to_top(self) -> 'AppiumExtended':
        """
        Выполняет свайп снизу вверх по вертикальной оси экрана.

        Args:
            Метод не принимает аргументов.

        Usages:
            app.swipe_bottom_to_top()

        Returns:
            AppiumExtended: Возвращает экземпляр текущего объекта для возможности цепочного вызова методов.

        Raises:
            None: Метод не вызывает исключений, но внутренние методы, которые он вызывает, могут вызывать исключения.

        Notes:
            Свайп начинается с 90% высоты экрана и заканчивается на 10% высоты экрана, сохраняя горизонтальную координату на уровне 50% от ширины экрана.
        """
        window_size = self.terminal.get_screen_resolution()
        height = window_size[1]
        top = int(height * 0.1)
        bottom = int(height * 0.9)
        self.swipe(start_position=(bottom, height // 2),
                   end_position=(top, height // 2))
        # Возвращаем экземпляр класса appium_extended
        return cast('AppiumExtended', self)

    # WAIT
    def wait_for(self,
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
                 ) -> 'AppiumExtended':
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

        Usages:
            app.wait_for(locator=("id", "android.widget.ProgressBar"), timeout=5)
            app.wait_for(locator={'text': 'foo', 'displayed': 'true', 'enabled': 'true'})
            app.wait_for(image="path/to/image.png", timeout=10)
            app.wait_for(locator=[("id", "element1"), ("name", "element2")], timeout=5)
            app.wait_for(image=["path/to/image1.png", "path/to/image2.png"], timeout=10)

        Returns:
            bool: True, если элементы или изображения найдены в течение заданного времени, иначе False.

        Raises:
            None: Метод не вызывает исключений.

        Notes:
            - Метод использует внутренние функции для поиска элементов и изображений.
            - Параметр `contains` используется только при поиске по локатору.
        """
        try:
            if not self._wait_for(locator=locator,
                                  image=image,
                                  sleep=sleep,
                                  timeout_elem=timeout_elem,
                                  timeout_method=timeout_method,
                                  elements_range=elements_range,
                                  contains=contains,
                                  poll_frequency=poll_frequency,
                                  ignored_exceptions=ignored_exceptions, ):
                raise WaitForError(message="Элемент или изображение не появились на экране в течение заданного времени",
                                   locator=locator,
                                   image=image,
                                   sleep=sleep,
                                   timeout_elem=timeout_elem,
                                   timeout_method=timeout_method,
                                   elements_range=elements_range,
                                   contains=contains,
                                   poll_frequency=poll_frequency,
                                   ignored_exceptions=ignored_exceptions, )
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise WaitForError(message=f"""
            Ошибка ожидания элемента или изображения на экране в течение заданного времени {locator=}, {image=}""",
                               locator=locator,
                               image=image,
                               sleep=sleep,
                               timeout_elem=timeout_elem,
                               timeout_method=timeout_method,
                               elements_range=elements_range,
                               contains=contains,
                               poll_frequency=poll_frequency,
                               ignored_exceptions=ignored_exceptions, ) from error

    def wait_for_not(self,
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
                     sleep: int = 1
                     ) -> 'AppiumExtended':
        """
        Ожидает исчезновения указанного локатора или изображения с экрана.

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

        Usages:
            app.wait_for_not(locator=("id", "android.widget.ProgressBar"), timeout=5)
            app.wait_for_not(locator={'text': 'foo', 'displayed': 'true', 'enabled': 'true'})
            app.wait_for_not(image="path/to/image.png", timeout=10)
            app.wait_for_not(locator=[("id", "element1"), ("name", "element2")], timeout=5)
            app.wait_for_not(image=["path/to/image1.png", "path/to/image2.png"], timeout=10)

        Returns:
            AppiumExtended: Возвращает экземпляр текущего объекта для возможности цепочного вызова методов.

        Raises:
            Метод не вызывает исключений.

        Notes:
            - Метод использует внутренние функции для поиска элементов и изображений.
            - Параметр `contains` используется только при поиске по локатору.
        """
        try:
            if not self._wait_for_not(locator=locator,
                                      image=image,
                                      timeout_elem=timeout_elem,
                                      timeout_method=timeout_method,
                                      elements_range=elements_range,
                                      contains=contains,
                                      poll_frequency=poll_frequency,
                                      ignored_exceptions=ignored_exceptions,
                                      sleep=sleep):
                raise WaitForNotError(message="Элемент или изображение не исчезли в течение заданного времени",
                                      locator=locator,
                                      image=image,
                                      timeout_elem=timeout_elem,
                                      timeout_method=timeout_method,
                                      elements_range=elements_range,
                                      contains=contains,
                                      poll_frequency=poll_frequency,
                                      ignored_exceptions=ignored_exceptions, )
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise WaitForNotError(message=f"Ошибка при ожидании wait_for_not(): {error}",
                                  locator=locator,
                                  image=image,
                                  timeout_elem=timeout_elem,
                                  timeout_method=timeout_method,
                                  elements_range=elements_range,
                                  contains=contains,
                                  poll_frequency=poll_frequency,
                                  ignored_exceptions=ignored_exceptions,
                                  original_exception=error) from error

    def is_wait_for(self,
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
                    sleep: int = 1,
                    ) -> bool:
        try:
            if self._wait_for(locator=locator,
                              timeout_elem=timeout_elem,
                              timeout_method=timeout_method,
                              elements_range=elements_range,
                              contains=contains,
                              poll_frequency=poll_frequency,
                              ignored_exceptions=ignored_exceptions,
                              sleep=sleep,
                              image=image, ):
                return True
            return False
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise IsWaitForError(message=f"""
           Неизвестная ошибка в методе is_wait_for {error=}, {locator=}, {image=}""",
                                 locator=locator,
                                 image=image,
                                 timeout_elem=timeout_elem,
                                 timeout_method=timeout_method,
                                 elements_range=elements_range,
                                 contains=contains,
                                 poll_frequency=poll_frequency,
                                 ignored_exceptions=ignored_exceptions,
                                 original_exception=error) from error

    def is_wait_for_not(self,
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
                        sleep: int = 1
                        ) -> bool:
        try:
            if self._wait_for_not(locator=locator,
                                  image=image,
                                  timeout_elem=timeout_elem,
                                  timeout_method=timeout_method,
                                  elements_range=elements_range,
                                  contains=contains,
                                  poll_frequency=poll_frequency,
                                  ignored_exceptions=ignored_exceptions,
                                  sleep=sleep):
                return True
            return False
        except TimeoutError:
            return False
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise IsWaitForNotError(message=f"""Неизвестная ошибка в методе is_wait_for_not(): 
                                              {error}, {locator=}, {image=}""",
                                    locator=locator,
                                    image=image,
                                    timeout_elem=timeout_elem,
                                    timeout_method=timeout_method,
                                    elements_range=elements_range,
                                    contains=contains,
                                    poll_frequency=poll_frequency,
                                    ignored_exceptions=ignored_exceptions,
                                    original_exception=error) from error

    def wait_return_true(self, method, timeout: int = 10, sleep: int = 1) -> 'AppiumExtended':
        try:
            self._wait_return_true(method=method, timeout=timeout, sleep=sleep)
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise WaitReturnTrueError(message=f"Ошибка ожидания возврата True от метода: {error}",
                                      method=method,
                                      timeout=timeout,
                                      original_exception=error) from error

    # OTHER

    def draw_by_coordinates(self,
                            image: Union[bytes, str, Image.Image, np.ndarray] = None,
                            coordinates: Tuple[int, int, int, int] = None,
                            top_left: Tuple[int, int] = None,
                            bottom_right: Tuple[int, int] = None,
                            path: str = None,
                            ) -> 'AppiumExtended':
        """
        Рисует прямоугольник на предоставленном изображении или снимке экрана с помощью драйвера.

        Args:
            image (Union[bytes, str, Image.Image, np.ndarray], optional): Изображение для рисования. По умолчанию None.
            coordinates (Tuple[int, int, int, int], optional): Координаты прямоугольника (x1, y1, x2, y2).
                                                               По умолчанию None.
            top_left (Tuple[int, int], optional): Верхняя левая точка прямоугольника. По умолчанию None.
            bottom_right (Tuple[int, int], optional): Нижняя правая точка прямоугольника. По умолчанию None.
            path (str, optional): Путь для сохранения изображения. По умолчанию None.

        Usages:
            draw_by_coordinates(image=image_bytes, coordinates=(10, 20, 30, 40), path='path/to/save/image.png')
            draw_by_coordinates(top_left=(10, 20), bottom_right=(30, 40))

        Returns:
            bool: True, если операция выполнена успешно, иначе False.

        Raises:
            WebDriverException: Если возникают проблемы с WebDriver.
            cv2.error: Если возникают проблемы с OpenCV.

        Notes:
            - Если изображение не предоставлено, будет использован текущий снимок экрана.
            - Если не указаны верхняя левая и нижняя правая точки, будут использованы координаты.
        """
        try:
            assert self.draw_by_coordinates(image=image,
                                            coordinates=coordinates,
                                            top_left=top_left,
                                            bottom_right=bottom_right,
                                            path=path)
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise DrawByCoordinatesError(message=f"Не удалось нарисовать прямоугольник на изображении: {error}",
                                         coordinates=coordinates,
                                         top_left=top_left,
                                         bottom_right=bottom_right,
                                         path=path,
                                         original_exception=error) from error

    def save_screenshot(self, path: str = '', filename: str = 'screenshot.png') -> 'AppiumExtended':
        """
        Сохраняет скриншот экрана в указанный файл.

        Args:
            path (str, optional): Путь к директории, где будет сохранен скриншот. По умолчанию пустая строка, что означает текущую директорию.
            filename (str, optional): Имя файла, в который будет сохранен скриншот. По умолчанию 'screenshot.png'.

        Usages:
            save_screenshot(path='/path/to/save', filename='my_screenshot.png')
            save_screenshot(filename='another_screenshot.png')
            save_screenshot()

        Returns:
            AppiumExtended (self).

        Raises:
            Exception: В случае, если возникают проблемы при сохранении скриншота.

        Notes:
            - Если путь не указан, скриншот будет сохранен в текущей директории.
            - Если имя файла не указано, будет использовано имя 'screenshot.png'.
        """
        try:
            self.image._save_screenshot(path=path, filename=filename)
            return cast('AppiumExtended', self)
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise SaveScreenshotError(message=f"Не удалось сохранить скриншот: {error}",
                                      path=path,
                                      filename=filename,
                                      original_exception=error) from error

    # PRIVATE

    def _extract_point_coordinates_by_typing(self,
                                             position:
                                             Union[Tuple[int, int], str, bytes, np.ndarray, Image.Image,
                                             Tuple[str, str], Dict, WebElement, WebElementExtended]
                                             ) -> Tuple[int, int]:
        """
        Извлекает координаты точки на основе типа переданной позиции.
    
        Args:
            position (Union[Tuple[int, int], str, bytes, np.ndarray, Image.Image, Tuple[str, str], 
                      Dict, WebElement, WebElementExtended]):
                - Позиция, для которой нужно извлечь координаты.
                - Либо локатор элемента, либо изображение, либо кортеж из координат.
    
        Usages:
            _extract_point_coordinates_by_typing((100, 200))
            _extract_point_coordinates_by_typing("path/to/image.png")
            _extract_point_coordinates_by_typing({"id": "some_id"})
            _extract_point_coordinates_by_typing(WebElement)
    
        Returns:
            Tuple[int, int]: Кортеж координат точки, в формате (x, y).
        
        Notes:
            - Метод использует различные внутренние функции для вычисления координат в 
              зависимости от типа входного параметра.
        """
        try:
            x, y = 0, 0
            # Вычисление позиции начала свайпа
            if (isinstance(position, Tuple) and
                    isinstance(position[0], int) and
                    isinstance(position[1], int)):
                # Если position является кортежем с двумя целыми числами, то считаем, что это координаты
                x, y = position
            elif (isinstance(position, Tuple) and
                  isinstance(position[0], str) and
                  isinstance(position[1], str)) or \
                    isinstance(position, WebElement) or \
                    isinstance(position, WebElementExtended) or \
                    isinstance(position, Dict):
                # Если position является кортежем с двумя строковыми элементами или экземпляром WebElement,
                # WebElementExtended или словарем, то получаем координаты центра элемента
                x, y = utils.calculate_center_of_coordinates(
                    self.get_element(locator=position).get_coordinates())
            elif isinstance(position, (bytes, np.ndarray, Image.Image, str)):
                # Если position является строкой, байтами, массивом NumPy или объектом Image.Image,
                # то получаем координаты центра изображения
                x, y = utils.calculate_center_of_coordinates(
                    self.get_image_coordinates(image=position))
            return x, y
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except WebElementExtendedError as error:
            raise ExtractPointCoordinatesByTypingError(
                message=f"Не удалось извлечь координаты точки на основе типа переданной позиции: {error}",
                position=position,
                original_exception=error) from error
        except Exception as error:
            raise ExtractPointCoordinatesByTypingError(
                message=f"Не удалось извлечь координаты точки на основе типа переданной позиции: {error}",
                position=position,
                original_exception=error) from error

    @staticmethod
    def _extract_point_coordinates_by_direction(direction: int, distance: int,
                                                start_x: int, start_y: int,
                                                screen_resolution: tuple
                                                ) -> Tuple[int, int]:
        """
        Извлекает координаты точки на заданном расстоянии и в заданном направлении относительно начальных координат.

        Параметры:
            direction (str): Направление движения в пределах 360 градусов.
            distance (int): Расстояние, на которое нужно переместиться относительно начальных координат в пикселях.
            start_x (int): Начальная координата X.
            start_y (int): Начальная координата Y.

        Возвращает:
            Tuple[int, int]: Координаты конечной точки в формате (x, y).
        """
        try:
            width = screen_resolution[0]
            height = screen_resolution[1]
            end_x, end_y = utils.find_coordinates_by_vector(width=width, height=height,
                                                            direction=direction, distance=distance,
                                                            start_x=start_x, start_y=start_y)
            return end_x, end_y
        except Exception as error:
            raise ExtractPointCoordinatesError(message=f"Не удалось извлечь координаты точки: {error}",
                                               direction=direction,
                                               distance=distance,
                                               start_x=start_x,
                                               start_y=start_y,
                                               screen_resolution=screen_resolution,
                                               original_exception=error) from error

    def get_screenshot_as_base64_decoded(self) -> bytes:
        """
        Получает скриншот экрана, кодирует его в формате Base64, а затем декодирует в байты.

        Args:
            Метод не принимает аргументов.

        Usages:
            screenshot_bytes = self._get_screenshot_as_base64_decoded()

        Returns:
            bytes: Декодированные байты скриншота.

        Notes:
            - Этот метод предназначен для внутреннего использования и может быть вызван другими методами класса.
            - Скриншот возвращается в формате PNG.
            - Исходный скриншот получается в формате Base64, который затем кодируется в UTF-8 и декодируется обратно в байты.
        """
        try:
            return self._get_screenshot_as_base64_decoded()
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise GetScreenshotError(message=f"Не удалось получить скриншот: {error}",
                                     original_exception=error) from error

    def save_source(self, path: str = '', filename: str = 'source.xml'):
        """
        Сохраняет исходный код страницы в указанной директории с указанным именем файла.

        Args:
            path (str, optional): Путь к директории, в которой будет сохранен файл. По умолчанию пустая строка, что означает текущую директорию.
            filename (str, optional): Имя файла, в котором будет сохранен исходный код. По умолчанию 'source.xml'.

        Usages:
            save_source()
            save_source(path='some/directory')
            save_source(filename='another_name.xml')
            save_source(path='some/directory', filename='another_name.xml')

        Returns:
            bool: True, если исходный код успешно сохранен. False, если произошла ошибка.

        Notes:
            - Метод использует встроенный метод драйвера `page_source` для получения исходного кода страницы.
            - Исходный код сохраняется в формате XML.
        """
        try:
            source = self.driver.page_source
            path_to_file = os.path.join(path, filename)
            with open(path_to_file, "wb") as f:
                f.write(source.encode('utf-8'))
        except NoSuchDriverException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except InvalidSessionIdException as error:
            self.logger.error(f"{inspect.currentframe().f_code.co_name} RECONNECT")
            self.logger.error(error)
            self.reconnect()
        except Exception as error:
            raise SaveSourceError(message="Не удалось сохранить исходный код страницы",
                                  path=path,
                                  filename=filename,
                                  original_exception=error) from error

    def find_and_tap_in_drop_down_menu(self, item: str, items: List[str],
                                       drop_down_locator=None, timeout: int = 390, drop_sleep: int = 3):
        swipe_direction_down = True
        start_time = time.time()
        time.sleep(drop_sleep)

        # Прокрутка вниз до упора
        while time.time() - start_time < timeout:
            try:
                item = item.lower()
                coord = self.get_text_coordinates(text=items)
                if item in coord.keys():
                    element_coord = self.utils.calculate_center_of_coordinates(coord[item])
                    self.tap(x=element_coord[0], y=element_coord[1])
                    return True

                # сортировка по последнему значению координат
                sorted_list = [item for item in sorted(coord.items(), key=lambda x: x[1][-1])]
                sorted_dicts = [dict({key: value}) for key, value in sorted_list]

                top_dict = sorted_dicts[1]  # Верхний словарь в списке
                bottom_dict = sorted_dicts[3]  # Нижний словарь в списке

                top_key = list(top_dict.keys())[0]  # Ключ первого словаря
                top_value = coord[top_key]  # Значение первого словаря
                bottom_key = list(bottom_dict.keys())[0]  # Ключ последнего словаря
                bottom_value = coord[bottom_key]  # Значение последнего словаря

                top_value = utils.calculate_center_of_coordinates(top_value)
                bottom_value = utils.calculate_center_of_coordinates(bottom_value)

                if swipe_direction_down:
                    self.swipe(start_position=bottom_value, end_position=top_value)
                else:
                    self.swipe(start_position=top_value, end_position=bottom_value)
                time.sleep(2)
                last_coord = self.get_text_coordinates(text=items)
                if last_coord == coord:
                    swipe_direction_down = not swipe_direction_down

            except IndexError as error:
                self.logger.error(f"IndexError {error}")
                if drop_down_locator is not None:
                    self.tap(drop_down_locator)
                continue
            except Exception as error:
                self.logger.error(f"Exception {error}")
                continue

