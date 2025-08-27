# coding: utf-8
import base64
import io
import logging
import os
import time
from typing import Union, List, Tuple, Optional, Dict

import cv2
import numpy as np
from PIL import Image
from pytesseract import pytesseract

from appium_extended_helpers import helpers_decorators
from appium_extended_terminal.terminal import Terminal
from appium_extended_utils import utils


class AppiumImage:
    """
    Класс работы с Appium.
    Обеспечивает работу с изображениями
    """

    def __init__(self, base):
        self.logger = base.logger
        self.driver = base.driver
        self.terminal = base.terminal
        self.transport = base.transport
        self.secure_screenshot = base.secure_screenshot

    def find_and_tap_in_drop_down_menu(self, item: str, items: List[str], drop_down_locator=None, timeout: int = 390):
        swipe_direction_down = True
        while True:
            try:
                item = item.lower()
                coord = self.get_text_coordinates(text=items)
                if item in coord.keys():
                    element_coord = utils.calculate_center_of_coordinates(coord[item])
                    self.terminal.tap(x=element_coord[0], y=element_coord[1])
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

                # top_value = utils.calculate_center_of_coordinates(top_value)
                # bottom_value = utils.calculate_center_of_coordinates(bottom_value)

                if swipe_direction_down:
                    self.terminal.swipe(*bottom_value)
                else:
                    self.terminal.swipe(*top_value)
                time.sleep(2)
                last_coord = self.get_text_coordinates(text=items)
                if last_coord == coord:
                    swipe_direction_down = not swipe_direction_down

            except IndexError as error:
                self.logger.error(f"IndexError {error}")
                if drop_down_locator is not None:
                    self.terminal.tap(drop_down_locator)
                continue
            except Exception as error:
                self.logger.error(f"Exception {error}")
                continue

    @helpers_decorators.retry
    def get_image_coordinates(self,
                              image: Union[bytes, np.ndarray, Image.Image, str],
                              full_image: Union[bytes, np.ndarray, Image.Image, str] = None,
                              threshold: Optional[float] = 0.7,
                              ) -> Union[Tuple[int, int, int, int], None]:
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
        """
        if full_image is None:
            screenshot = self._get_screenshot_as_base64_decoded()
            big_image = self._to_ndarray(image=screenshot, grayscale=True)
        else:
            big_image = self._to_ndarray(image=full_image, grayscale=True)  # Загрузка полного изображения

        small_image = self._to_ndarray(image=image, grayscale=True)  # Загрузка частичного изображения

        # Сопоставление частичного изображения и снимка экрана
        max_val_loc = self._multi_scale_matching(full_image=big_image, template_image=small_image,
                                                 threshold=threshold)
        if max_val_loc is None:
            return None

        max_val, max_loc = max_val_loc

        if not max_val >= threshold:  # Если наибольшее значение совпадения не превышает порога, возвращаем None
            self.logger.error("find_coordinates_by_image(): Совпадений не найдено")
            return None

        # Вычисляем координаты левого верхнего и правого нижнего углов найденного совпадения
        left = int(max_loc[0])
        top = int(max_loc[1])
        width = small_image.shape[1]
        height = small_image.shape[0]
        right = left + width
        bottom = top + height

        return int(left), int(top), int(right), int(bottom)  # Возвращаем координаты наиболее вероятного совпадения

    @helpers_decorators.retry
    def get_inner_image_coordinates(self,
                                    outer_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                    inner_image_path: Union[bytes, np.ndarray, Image.Image, str],
                                    threshold: float = 0.9) -> Union[Tuple[int, int, int, int], None]:
        """
        Находит изображение на экране и внутри него находит другое изображение (внутреннее).

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
            Повторяет выполнение 3 раза при неудаче.
        """
        # Получаем разрешение экрана
        screen_width, screen_height = self.terminal.get_screen_resolution()

        # Захватываем скриншот
        screenshot = base64.b64decode(self.driver.get_screenshot_as_base64())

        # Читаем скриншот
        full_image = self._to_ndarray(image=screenshot, grayscale=True)

        # Прочитать внешнее изображение
        outer_image = self._to_ndarray(image=outer_image_path, grayscale=True)

        # Прочитать внутреннее изображение
        inner_image = self._to_ndarray(image=inner_image_path, grayscale=True)

        # Вычисляем коэффициенты масштабирования
        width_ratio = screen_width / full_image.shape[1]
        height_ratio = screen_height / full_image.shape[0]

        # ...
        inner_image = cv2.resize(inner_image, None, fx=width_ratio, fy=height_ratio)
        outer_image = cv2.resize(outer_image, None, fx=width_ratio, fy=height_ratio)

        outer_max_val, outer_max_loc = self._multi_scale_matching(full_image=full_image, template_image=outer_image,
                                                                  threshold=threshold)

        # Проверить, превышает ли максимальное значение сходства для внешнего изображения пороговое значение
        if outer_max_val >= threshold:
            # Получить размеры внешнего изображения
            outer_height, outer_width = outer_image.shape

            # Вычислить координаты внешнего изображения на экране
            outer_top_left = outer_max_loc
            outer_bottom_right = (outer_top_left[0] + outer_width, outer_top_left[1] + outer_height)

            # Извлечь область интереса (ROI), содержащую внешнее изображение
            outer_roi = full_image[outer_top_left[1]:outer_bottom_right[1], outer_top_left[0]:outer_bottom_right[0]]

            inner_max_val, inner_max_loc = self._multi_scale_matching(full_image=outer_roi, template_image=inner_image,
                                                                      threshold=threshold)

            # Проверить, превышает ли максимальное значение сходства для внутреннего изображения пороговое значение
            if inner_max_val >= threshold:
                # Получить размеры внутреннего изображения
                inner_height, inner_width = inner_image.shape

                # Вычислить координаты внутреннего изображения относительно экрана
                inner_top_left = (outer_top_left[0] + inner_max_loc[0], outer_top_left[1] + inner_max_loc[1])
                inner_bottom_right = (inner_top_left[0] + inner_width, inner_top_left[1] + inner_height)

                # Вернуть координаты внутреннего изображения относительно экрана
                return inner_top_left + inner_bottom_right

        # Вернуть None, если внутреннее изображение не найдено
        return None

    def _is_image_on_the_screen(self,
                                image: Union[bytes, np.ndarray, Image.Image, str],
                                threshold: float = 0.9) -> bool:
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
            screenshot = self._get_screenshot_as_base64_decoded()

            # Чтение снимка экрана и частичного изображения
            full_image = self._to_ndarray(image=screenshot, grayscale=True)
            small_image = self._to_ndarray(image=image, grayscale=True)

            # Проверка размеров изображений
            if small_image.shape[0] > full_image.shape[0] or small_image.shape[1] > full_image.shape[1]:
                self.logger.error("Частичное изображение больше снимка экрана.")
                return False

            # Сопоставление частичного изображения и снимка экрана
            max_val, max_loc = self._multi_scale_matching(full_image=full_image, template_image=small_image,
                                                          threshold=threshold)

            return max_val > threshold
        except cv2.error as e:
            self.logger.error(f"is_image_on_the_screen(): {e}")
            return False
        except AssertionError as e:
            self.logger.error(f"is_image_on_the_screen(): {e}")
            return False

    @staticmethod
    def _multi_scale_matching(full_image: np.ndarray,
                              template_image: np.ndarray,
                              threshold: float = 0.8,
                              return_raw: bool = False):
        origin_width, origin_height = template_image.shape[::-1]  # Исходный размер шаблона

        # Цикл по различным масштабам, включая масштабы больше 1.0 для "растягивания"
        for scale in np.concatenate([np.linspace(0.2, 1.0, 10)[::-1], np.linspace(1.1, 2.0, 10)]):

            # Изменение размера изображения и сохранение масштаба
            resized = cv2.resize(full_image, (int(full_image.shape[1] * scale), int(full_image.shape[0] * scale)))

            # Если измененный размер становится меньше шаблона, прерываем цикл
            if resized.shape[0] < origin_height or resized.shape[1] < origin_width:
                continue

            # Сопоставление шаблона
            result = cv2.matchTemplate(resized, template_image, cv2.TM_CCOEFF_NORMED)

            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > threshold:
                if return_raw:
                    return result
                # Преобразование координат обратно к оригинальному масштабу
                max_loc_original = (int(max_loc[0] / scale), int(max_loc[1] / scale))
                return max_val, max_loc_original

        if return_raw:
            return None
        return 0, (0, 0)

    def is_text_on_ocr_screen(self,
                              text: str,
                              screen: Union[bytes, np.ndarray, Image.Image, str] = None,
                              language: str = 'rus') -> bool:
        """
        Проверяет, присутствует ли заданный текст на экране.
        Распознавание текста производит с помощью библиотеки pytesseract.

        Аргументы:
        - text (str): Текст, который нужно найти на экране.
        - screen (bytes, optional): Скриншот в формате bytes. Если не указан, будет захвачен скриншот с помощью `self.driver`.
        - language (str): Язык распознавания текста. Значение по умолчанию: 'rus'.

        Возвращает:
        - bool: True, если заданный текст найден на экране. False в противном случае.
        """
        try:
            if screen is None:
                screenshot = self._get_screenshot_as_base64_decoded()
                image = self._to_ndarray(screenshot)
            else:
                image = self._to_ndarray(screen)

            # Адаптивная бинаризация
            threshold = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            # Преобразование двоичного изображения в текст
            custom_config = r'--oem 3 --psm 6'

            ocr_text = pytesseract.image_to_string(threshold, lang=language, config=custom_config)

            # Проверка наличия заданного текста в распознанном тексте
            return text.lower() in ocr_text.lower()
        except cv2.error as e:
            self.logger.error(f"is_text_on_ocr_screen(): {e}")
            return False
        except pytesseract.TesseractError as e:
            self.logger.error(f"is_text_on_ocr_screen(): {e}")
            return False
        except AssertionError as e:
            self.logger.error(f"is_text_on_ocr_screen(): {e}")
            return False

    @helpers_decorators.retry
    def get_many_coordinates_of_image(self,
                                      image: Union[bytes, np.ndarray, Image.Image, str],
                                      full_image: Union[bytes, np.ndarray, Image.Image, str] = None,
                                      cv_threshold: float = 0.7,
                                      coord_threshold: int = 5) -> Union[List[Tuple], None]:
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
                Максимальное различие между значениями x и y двух кортежей, чтобы они считались слишком близкими друг к другу.
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

        if full_image is None:
            screenshot = self._get_screenshot_as_base64_decoded()
            big_image = self._to_ndarray(image=screenshot, grayscale=True)
        else:
            big_image = self._to_ndarray(image=full_image, grayscale=True)  # Загрузка полного изображения

        small_image = self._to_ndarray(image=image, grayscale=True)  # Загрузка частичного изображения

        result = self._multi_scale_matching(full_image=big_image, template_image=small_image,
                                            return_raw=True, threshold=cv_threshold)

        # Получить все совпадения выше порога
        locations = np.where(result >= cv_threshold)  # Нахождение всех совпадений выше порога
        matches = list(zip(*locations[::-1]))  # Преобразование координат в список кортежей

        # Фильтрация слишком близких совпадений
        unique_list = []  # Создаем пустой список для хранения уникальных кортежей
        for (x1_coordinate, y1_coordinate) in matches:  # Итерируемся по списку кортежей
            exclude = False  # Инициализируем флаг exclude значением False
            for (x2_coordinate, y2_coordinate) in unique_list:  # Итерируемся по уникальным кортежам
                if abs(x1_coordinate - x2_coordinate) <= coord_threshold and abs(
                        y1_coordinate - y2_coordinate) <= coord_threshold:
                    # Если различие между значениями x и y двух кортежей меньше или равно порогу,
                    # помечаем exclude как True и выходим из цикла
                    exclude = True
                    break
            if not exclude:  # Если exclude равно False, добавляем кортеж в unique_list
                unique_list.append((x1_coordinate, y1_coordinate))
        matches = unique_list

        if not matches:
            self.logger.error(f"_find_many_coordinates_by_image() NO MATCHES, {image=}")
            return None

        # Добавляем правый нижний угол к каждому найденному совпадению
        matches_with_corners = []
        for match in matches:
            x_coordinate, y_coordinate = match
            width, height = small_image.shape[::-1]
            top_left = (x_coordinate, y_coordinate)
            bottom_right = (x_coordinate + width, y_coordinate + height)
            matches_with_corners.append((top_left + bottom_right))

        return matches_with_corners

    @helpers_decorators.retry
    def get_text_coordinates(self,
                             text: Union[str, List[str]],
                             image: Union[bytes, str, Image.Image, np.ndarray] = None,
                             language: str = 'rus'
                             ) -> Union[tuple[int, ...], Dict[str, tuple], None]:
        """
        Возвращает координаты области с указанным текстом на предоставленном изображении или снимке экрана.

        Args:
        - text (str): Искомый текст.
        - image (bytes, str, Image.Image, np.ndarray, опционально): Изображение, на котором осуществляется поиск текста.
          Если не указано, будет использован снимок экрана. По умолчанию None.
        - language (str, опционально): Язык для распознавания текста. По умолчанию 'rus'.

        Usages:
            app.get_text_coordinates("Hello, world!")
            app.get_text_coordinates("Привет, мир!", language='rus')
            app.get_text_coordinates("Hello, world!", image='path/to/image.png')

        Returns:
        - Union[Tuple[int, int, int, int], None]: Координаты области с текстом или None, если текст не найден.
        """
        if not image:
            # Получаем снимок экрана, если изображение не предоставлено
            screenshot = self._get_screenshot_as_base64_decoded()  # Получение снимка экрана в формате base64
            image = self._to_ndarray(image=screenshot,
                                     grayscale=True)  # Преобразование снимка экрана в массив numpy и преобразование в оттенки серого
        else:
            # Если предоставлено, то преобразуем
            image = self._to_ndarray(image=image,
                                     grayscale=True)  # Преобразование изображения в массив numpy и преобразование в оттенки серого
        image = cv2.medianBlur(image, 3)  # + устранение шума
        image = cv2.convertScaleAbs(image, alpha=1.5, beta=30)

        # Адаптивная бинаризация
        threshold = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        oem_config = r'--oem 3 --psm 6'
        # Выполнение OCR с помощью PyTesseract
        data = pytesseract.image_to_data(threshold,
                                         lang=language,
                                         output_type=pytesseract.Output.DICT,
                                         config=oem_config)  # Использование PyTesseract для распознавания текста и получения информации о распознанных словах

        formatted_data = {}

        for i in range(len(data['text'])):
            word_text = data['text'][i]  # Текст слова
            left = int(data['left'][i])  # Координата левой границы слова
            top = int(data['top'][i])  # Координата верхней границы слова
            width = int(data['width'][i])  # Ширина слова
            height = int(data['height'][i])  # Высота слова
            coordinates = [left, top, left + width, top + height]  # Координаты рамки слова

            if word_text:
                if i not in formatted_data:
                    formatted_data[i] = {}
                formatted_data[i] = {'text': word_text,
                                     'coordinates': coordinates}  # Сохранение информации о слове и его координатах
        # Инициализировать переменные для последовательности слов и соответствующих координат
        current_sequence = []  # Текущая последовательность слов
        result_coordinates = []  # Координаты текущей последовательности слов
        result_dict = {}
        flag_return_list = False

        if isinstance(text, str):
            text = [text]
            flag_return_list = True
        for element in text:
            # Разбить искомый текст на отдельные слова
            words = element.lower().split(' ')  # Разделение искомого текста на отдельные слова
            for word_data in formatted_data.values():
                word = word_data['text'].lower()  # Текущее слово
                coordinates = word_data['coordinates']  # Координаты слова

                if word in words:
                    current_sequence.append(word)  # Добавление слова в текущую последовательность
                    result_coordinates.append(coordinates)  # Добавление координат слова в результат

            if utils.is_list_in_list(small_list=words, big_list=current_sequence):
                # Обрезка списка координат до размерности заданной последовательности слов
                if len(current_sequence) > len(words):
                    result_coordinates = result_coordinates[-len(words):]

                # Если найдена последовательность слов, вернуть соответствующие координаты
                top_left = tuple(map(int, result_coordinates[0][:2]))  # Верхний левый угол рамки
                bottom_right = tuple(map(int, result_coordinates[-1][2:]))  # Нижний правый угол рамки
                if flag_return_list:
                    return top_left + bottom_right
                words = ' '.join(words)
                result_dict[words] = top_left + bottom_right
            current_sequence = []  # Сброс текущей последовательности слов
            result_coordinates = []  # Сброс координат последовательности слов
        return result_dict

    def draw_by_coordinates(self,
                            image: Union[bytes, str, Image.Image, np.ndarray] = None,
                            coordinates: Tuple[int, int, int, int] = None,
                            top_left: Tuple[int, int] = None,
                            bottom_right: Tuple[int, int] = None,
                            path: str = None) -> bool:
        """
        Рисует прямоугольник на предоставленном изображении или снимке экрана с помощью драйвера.

        Args:
            image (Union[bytes, str, Image.Image, np.ndarray], optional): Изображение для рисования. По умолчанию None.
            coordinates (Tuple[int, int, int, int], optional): Координаты прямоугольника (x1, y1, x2, y2). По умолчанию None.
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
            if image is None:
                # Если изображение не предоставлено, получаем снимок экрана с помощью драйвера
                screenshot = self._get_screenshot_as_base64_decoded()
                image = self._to_ndarray(screenshot)
            else:
                image = self._to_ndarray(image)

            # Если верхняя левая и нижняя правая точки не предоставлены, используем координаты для определения
            # прямоугольника
            if not top_left and not bottom_right:
                top_left = (coordinates[0], coordinates[1])
                bottom_right = (coordinates[2], coordinates[3])

            # Сохраняем снимок экрана с нарисованным прямоугольником
            if path is None:
                path = "screenshot_with_text_coordinates.png"
            path = os.path.join(path)
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.imwrite(path, image)

            return True
        except cv2.error as e:
            # Обработка исключения cv2.error
            self.logger.error(f'draw_by_coordinates() cv2.error: {e}')
            return False

    @staticmethod
    def is_rgb(image: np.ndarray) -> bool:
        """
        Проверяет, является ли изображение цветным (RGB).

        Аргументы:
        - image: np.ndarray - Входное изображение в формате NumPy ndarray.

        Возвращает:
        - bool - True, если изображение является цветным (RGB), False - в противном случае.
        """
        return len(image.shape) == 3 and image.shape[2] == 3 or image.ndim == 3 or image.ndim == '3'

    @staticmethod
    def is_grayscale(image: np.ndarray) -> bool:
        """
        Проверяет, является ли изображение оттенков серого.

        Аргументы:
        - image: np.ndarray - Входное изображение в формате NumPy ndarray.

        Возвращает:
        - bool - True, если изображение является оттенков серого, False - в противном случае.
        """
        return len(image.shape) == 2 or (
                len(image.shape) == 3 and image.shape[2] == 1) or image.ndim == 2 or image.ndim == '2'

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Преобразует изображение в оттенки серого.

        Аргументы:
        - image: np.ndarray - Входное изображение в формате ndarray.

        Возвращает:
        - np.ndarray - Преобразованное изображение в оттенках серого.
        """
        # Проверяем, является ли изображение в формате RGB
        if self.is_rgb(image):
            # Если да, то преобразуем его в оттенки серого
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Приводим значения пикселей к диапазону от 0 до 255
            gray_image = cv2.convertScaleAbs(gray_image)
            return gray_image
        # Иначе, возвращаем изображение без изменений
        return image

    def _to_ndarray(self, image: Union[bytes, np.ndarray, Image.Image, str], grayscale: bool = True) -> np.ndarray:
        """
        Преобразует входные данные из различных типов в ndarray (NumPy array).

        Аргументы:
        - image: Union[bytes, np.ndarray, Image.Image, str] - Входные данные,
          представляющие изображение. Может быть типами bytes, np.ndarray, PIL Image или str.

        Возвращает:
        - np.ndarray - Преобразованный массив NumPy (ndarray) представляющий изображение.
        """
        # Если входные данные являются массивом байтов, преобразовать их в массив NumPy
        if isinstance(image, bytes):
            image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)

        # Если входные данные являются строкой с путем к файлу, открыть изображение и преобразовать в массив NumPy
        if isinstance(image, str):
            # image = np.array(Image.open(image))
            image = cv2.imread(image, cv2.IMREAD_COLOR)

        # Если входные данные являются объектом PIL Image, преобразовать его в массив NumPy
        if isinstance(image, Image.Image):
            image = np.array(image)

        # Вернуть преобразованный массив NumPy
        if grayscale:
            return self.to_grayscale(image=image)
        return image

    def _save_screenshot(self, path: str = '', filename: str = 'screenshot.png') -> bool:
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
            bool: True, если скриншот успешно сохранен, иначе False.

        Raises:
            Exception: В случае, если возникают проблемы при сохранении скриншота.

        Notes:
            - Если путь не указан, скриншот будет сохранен в текущей директории.
            - Если имя файла не указано, будет использовано имя 'screenshot.png'.
        """
        screenshot = self._get_screenshot_as_base64_decoded()
        path_to_file = os.path.join(path, filename)
        with open(path_to_file, "wb") as f:
            f.write(screenshot)
        return True

    def show_screen(self):
        """
        Выводит на экран теста скриншот текущего экрана устройства.
        Код не будет продолжать выполнятся, пока изображение не закрыть.
        Метод для отладки.
        """
        cv2.imshow('screen', self._to_ndarray(self._get_screenshot_as_base64_decoded()))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _get_screenshot_by_scrcpy(self) -> bytes:
        try:
            remote_path = "/home/sigma/temp/file.mp4"  # fix it
            command = f"timeout 2s scrcpy -s {self.driver.caps['udid']} --no-control --no-display --record {remote_path}"
            self.logger.debug(f"{command=}")
            stdin, stdout, stderr = self.transport.ssh.exec_command(command)
            output = stdout.read().decode() + stderr.read().decode()
            self.logger.debug(output)
            if "Recording started to mp4 file" not in output:
                self.logger.error(output)
            time.sleep(3)

            # Проверка файла на удалённой машине
            file_exists_command = f"test -f {remote_path} && echo 'File exists' || echo 'File not found'"

            # Цикл проверки
            for _ in range(5):  # проверим 5 раз с интервалом в 3 секунды
                stdin, stdout, stderr = self.transport.ssh.exec_command(file_exists_command)
                file_check_output = stdout.read().decode().strip()
                self.logger.info(f"File check result: {file_check_output}")
                time.sleep(3)
                if "File exists" in file_check_output:
                    self.logger.debug("Файл найден.")
                    break
            else:
                self.logger.error("Файл не был создан.")

            # Забираем лог через SCP
            self.transport.scp.get(remote_path=remote_path)

            # Очищаем временный файл на сервере
            # self.transport.ssh.exec_command(f'rm {remote_path}')

            # Параметры
            video_file = 'file.mp4'  # Путь к видеофайлу
            time_to_extract = 0  # Время в секундах, на котором нужно сделать скриншот
            output_image = 'screenshot.png'  # Путь для сохранения скриншота

            # Извлекаем кадр
            self.extract_frame(video_file, time_to_extract, output_image)
            with open(output_image, 'rb') as image_file:
                return image_file.read()  # Возвращаем изображение в виде байтов
        except Exception as error:
            self.logger.error(f"_get_screenshot_by_scrcpy Failed to capture screenshot: {error}")
            return b''

    def _get_screenshot_as_base64_decoded(self) -> bytes:
        """
        Получает скриншот экрана, кодирует его в формате Base64, а затем декодирует в байты.

        Args:
            Метод не принимает аргументов.

        Usages:
            screenshot_bytes = self._get_screenshot_as_base64_decoded()

        Returns:
            bytes: Декодированные байты скриншота, обычно в формате PNG.

        Raises:
            WebDriverException: Если не удается получить скриншот.

        Notes:
            - Этот метод предназначен для внутреннего использования и может быть вызван другими методами класса.
            - Скриншот возвращается в формате PNG.
            - Исходный скриншот получается в формате Base64, который затем кодируется в UTF-8 и декодируется обратно в байты.
        """
        try:
            screenshot = self.driver.get_screenshot_as_base64().encode('utf-8')
            screenshot = base64.b64decode(screenshot)
            return screenshot
        except Exception as error:
            self.logger.error(error)
            return self._get_screenshot_by_scrcpy()

    def extract_frame(self, video_path: str, time_sec: int, output_image: str) -> bool:
        """
        Извлекает кадр из видеофайла на указанной временной метке и сохраняет его как изображение.

        Параметры:
            video_path (str): Путь к видеофайлу, из которого нужно извлечь кадр.
            time_sec (int): Время в секундах, на котором нужно извлечь кадр.
            output_image (str): Путь для сохранения извлечённого кадра в формате изображения.

        Возвращает:
            bool: Возвращает True, если кадр успешно извлечён и сохранён. False — в случае ошибки (например, если видео не удалось открыть или не удалось прочитать кадр).
        """
        # Открываем видео файл
        cap = cv2.VideoCapture(video_path)

        # Проверяем, что видео открылось
        if not cap.isOpened():
            self.logger.error(f"Не удалось открыть видео {video_path}")
            return False

        # Устанавливаем время, на котором нужно взять кадр (в секундах)
        cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)

        # Читаем кадр
        success, frame = cap.read()

        if success:
            # Сохраняем кадр как изображение
            cv2.imwrite(output_image, frame)
            self.logger.debug(f"Кадр успешно сохранен в {output_image}")
            cap.release()
            return True
        else:
            self.logger.error("Не удалось извлечь кадр")
            cap.release()
            return False
