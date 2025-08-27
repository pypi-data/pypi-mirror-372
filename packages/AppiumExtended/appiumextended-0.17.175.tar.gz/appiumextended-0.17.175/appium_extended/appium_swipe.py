# coding: utf-8
import logging

from selenium.common.exceptions import WebDriverException
from appium_extended.appium_get import AppiumGet


class AppiumSwipe(AppiumGet):
    """
    Класс работы с Appium.
    Обеспечивает swipe
    """

    def __init__(self, logger: logging.Logger, secure_screenshot: bool = False):
        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def _swipe(self,    # TODO +direction and distance
               start_x: int,
               start_y: int,
               end_x: int,
               end_y: int,
               duration: int = 0) -> bool:
        """
        Выполняет свайп на элементе.

        Аргументы:
        - start_x (int): Координата x начальной точки свайпа.
        - start_y (int): Координата y начальной точки свайпа.
        - end_x (int): Координата x конечной точки свайпа.
        - end_y (int): Координата y конечной точки свайпа.
        - duration (int, optional): Продолжительность свайпа в миллисекундах.

        Возвращает:
        - bool: True, если свайп выполнен успешно, False в случае исключения.

        Исключения:
        - WebDriverException: Если происходит ошибка при выполнении свайпа.

        Примечание:
        - Метод использует экземпляр драйвера self.driver для выполнения свайпа.
        """
        try:
            self.driver.swipe(start_x=start_x, start_y=start_y,
                              end_x=end_x, end_y=end_y,
                              duration=duration)
        except WebDriverException as e:
            self.logger.error(f"Исключение в методе _swipe(). Аргументы:\n"
                              f"start_x={start_x}\n"
                              f"start_y={start_y}\n"
                              f"end_x={end_x}\n"
                              f"end_y={end_y}\n"
                              f"duration={duration}")
            self.logger.exception(e)
            return False

        return True

