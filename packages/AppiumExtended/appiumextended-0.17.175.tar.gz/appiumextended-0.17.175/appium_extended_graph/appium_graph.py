# coding: utf-8


class AppiumGraph:
    def __init__(self, base):
        self.app = base
        self.graph = {}

    def add_page(self, page, edges):
        self.graph[page] = edges

    def get_edges(self, page):
        return self.graph.get(page, [])

    def is_valid_edge(self, from_page, to_page):
        transitions = self.get_edges(from_page)
        return to_page in transitions

