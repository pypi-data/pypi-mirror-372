from appium_extended_web_element.web_element_get import WebElementGet


class WebElementIs(WebElementGet):
    """
    Класс для выполнения действий нажатия (Tap), а также нажатия и перемещения с использованием элементов веб-страницы.
    Наследуется от класса WebElementGet.
    """

    def __init__(self, base, element_id):
        super().__init__(base=base, element_id=element_id)

    def _is_within_screen(self, element):
        screen_size = self.terminal.get_screen_resolution()  # Получаем размеры экрана
        screen_width = screen_size[0]  # Ширина экрана
        screen_height = screen_size[1]  # Высота экрана
        element_location = element.location  # Получаем координаты элемента
        element_size = element.size  # Получаем размеры элемента
        if (
                element_location['y'] + element_size['height'] > screen_height or
                element_location['x'] + element_size['width'] > screen_width or
                element_location['y'] < 0 or
                element_location['x'] < 0
        ):
            # Если элемент находится за пределами экрана
            return False
        # Если элемент находится на экране
        return True
