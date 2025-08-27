# coding: utf-8
import logging
from typing import Optional

from selenium.common.exceptions import WebDriverException

from appium_extended.appium_get import AppiumGet


class AppiumTap(AppiumGet):
    """
    Класс работы с Appium.
    Обеспечивает tap
    """

    def __init__(self, logger: logging.Logger, secure_screenshot: bool = False):
        super().__init__(logger=logger, secure_screenshot=secure_screenshot)

    def _tap(self,
             x: int,
             y: int,
             duration: Optional[int] = None,
             ) -> bool:
        """
        Выполняет касание на экране устройства в указанных координатах (x, y) или на основе изображения.

        Аргументы:
        - x (int): Горизонтальная координата X точки касания на экране устройства.
        - y (int): Вертикальная координата Y точки касания на экране устройства.
        - duration (Optional[int]): Длительность касания в миллисекундах (по умолчанию None).

        Возвращает:
        - True, если касание выполнено успешно.
        - False, если произошла ошибка при выполнении касания.
        """
        position = (x, y)  # Координаты для касания

        try:
            self.driver.tap(positions=[position], duration=duration)  # Выполняем касание на указанных координатах
        except WebDriverException as e:
            self.logger.error("_tap() WebDriverException "
                              f"{x=}, {y=} "
                              f"{duration=}")
            self.logger.error(e)
            return False
        return True
