# coding: utf-8
from collections import deque
from typing import Any, Optional, List

from appium_extended_exceptions.appium_extended_exceptions import AppiumExtendedError
from appium_extended_graph.appium_graph import AppiumGraph


class AppiumNavigator:
    def __init__(self, base):
        self.app = base
        self.driver = base.driver
        self.helpers = base.helpers
        self.graph_manager = AppiumGraph(self)
        self.logger = base.logger

    def add_page(self, page, edges):
        """
        Добавление вершины в граф навигации по приложению.
        Вершина - представляет собой страницу (экран / окно).
        """
        self.graph_manager.add_page(page=page, edges=edges)

    def navigate(self, current_page: Any, destination_page: Any, timeout: int = 55) -> bool:
        """
        Навигация от текущей страницы к целевой странице.

        Этот метод выполняет навигацию от текущей страницы к указанной целевой странице в вашем приложении.
        Он использует поиск пути и последовательное выполнение шагов навигации, чтобы достичь цели.

        Args:
            current_page (Type[YourPageClass]): Класс текущей страницы, на которой находится пользователь.
            destination_page (Type[YourPageClass]): Класс целевой страницы, на которую пользователь хочет перейти.
            timeout (int, optional): Максимальное время ожидания перехода, по умолчанию 55 секунд.

        Raises:
            ValueError: Если не удается найти путь от текущей страницы к целевой странице.
        """
        if current_page == destination_page:
            return True

        # Находим путь от текущей страницы к целевой странице
        path = self.find_path(current_page, destination_page)

        if not path:
            raise ValueError(f"No path found from {current_page} to {destination_page}")

        # Выполняем навигацию, следуя найденному пути
        try:
            self.perform_navigation(path, timeout)
            return True
        except AppiumExtendedError as error:
            self.logger.error(f"Не удалось совершить навигацию: {error}")
            return False

    def find_path(self, start_page: Any, target_page: Any) -> Optional[List[Any]]:
        """
        Находит путь от стартовой страницы до целевой страницы.

        Этот метод использует поиск в ширину (BFS) для нахождения пути от стартовой страницы до целевой.
        Он обходит граф переходов между страницами, сохраняя текущий путь и посещенные страницы.

        Args:
            start_page (Any): Начальная страница поиска пути.
            target_page (Any): Целевая страница, которую нужно достичь.

        Returns:
            Optional[List[Any]]: Список страниц, образующих путь от стартовой до целевой страницы.
                                 Если путь не найден, возвращает None.
        """
        # Создаем множество для отслеживания посещенных страниц
        visited = set()

        # Используем очередь для выполнения поиска в ширину
        queue = deque([(start_page, [])])

        # Пока очередь не пуста, выполняем поиск
        while queue:
            # Извлекаем текущую страницу и путь от стартовой страницы до нее
            current_window, path = queue.popleft()

            # Добавляем текущую страницу в список посещенных
            visited.add(current_window)

            # Получаем переходы (соседние страницы) для текущей страницы
            transitions = self.graph_manager.get_edges(page=current_window)

            # Проверяем каждую соседнюю страницу
            for next_window in transitions:
                # Если соседняя страница является целевой, возвращаем полный путь
                if next_window == target_page:
                    return path + [current_window, next_window]

                # Если соседняя страница не была посещена, добавляем ее в очередь для дальнейшего поиска
                if next_window not in visited:
                    queue.append((next_window, path + [current_window]))

        # Возвращаем None, если путь не найден
        return None

    def perform_navigation(self, path: List[Any], timeout: int = 55) -> None:
        """
        Выполняет навигацию по заданному пути.

        Этот метод принимает список страниц, который представляет собой путь для навигации.
        Он выполняет переходы между соседними страницами, чтобы достичь целевой страницы.

        Args:
            path (List[Any]): Список страниц, образующих путь для навигации.
                              Каждый элемент списка представляет страницу, а порядок элементов в списке
                              определяет последовательность переходов от одной страницы к другой.

        Returns:
            None
        """
        # Проходим по пути и выполняем переходы между соседними страницами
        for page in range(len(path) - 1):
            current_page = path[page]
            next_page = path[page + 1]
            try:
                # Получаем метод перехода между текущей и следующей страницами
                transition_method = current_page.edges[next_page]
                # Выполняем переход
                transition_method()
            except KeyError as e:
                # В случае ошибки выводим сообщение о неудачном переходе
                self.logger.error("perform_navigation() Не найден способ перехода")
                self.logger.exception(e)
