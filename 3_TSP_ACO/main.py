#!/usr/bin/env python3

import sys
import math
import random
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QTextEdit, QLineEdit, QMessageBox
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRectF

# Класс для представления узла (города)
class Node:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index

    # Метод для вычисления расстояния между текущим узлом и другим узлом
    def distance_to(self, node):
        return math.sqrt((self.x - node.x) ** 2 + (self.y - node.y) ** 2)

# Класс для алгоритма муравьиной колонии
class AntColony:
    def __init__(self, nodes, ant_count=10, generations=100, alpha=0.9, beta=3, evaporation_rate=0.5, q0=0.9):
        self.nodes = nodes
        self.ant_count = ant_count
        self.generations = generations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.q0 = q0
        self.pheromones = np.ones((len(nodes), len(nodes)))  # Инициализация феромонов

    # Метод оптимизации для поиска оптимального маршрута
    def optimize(self):
        best_cycle = None
        best_distance = float('inf')

        for gen in range(self.generations):
            for ant_index in range(self.ant_count):
                cycle = self.ant_tour()
                distance = self.calculate_cycle_distance(cycle)
                if distance < best_distance:
                    best_distance = distance
                    best_cycle = cycle
            self.update_pheromones(best_cycle)

        return best_cycle

    # Метод для прохождения муравья по графу (поиск маршрута)
    def ant_tour(self):
        cycle = [random.choice(self.nodes)]  # Начальный узел
        remaining_nodes = set(self.nodes) - set(cycle)

        while remaining_nodes:
            next_node = self.select_next_node(cycle[-1], remaining_nodes)
            cycle.append(next_node)
            remaining_nodes.remove(next_node)

        return cycle

    # Выбор следующего узла для муравья
    def select_next_node(self, current_node, remaining_nodes):
        probabilities = self.calculate_probabilities(current_node, remaining_nodes)
        if random.random() < self.q0:
            next_node_index = np.argmax(probabilities)  # Использование q0 для жадного выбора
        else:
            next_node_index = random.choices(range(len(probabilities)), probabilities)[0]
        return list(remaining_nodes)[next_node_index]

    # Вычисление вероятностей перехода к следующему узлу
    def calculate_probabilities(self, current_node, remaining_nodes):
        probabilities = []
        total = 0

        for node in remaining_nodes:
            pheromone = self.pheromones[current_node.index][node.index]
            distance = current_node.distance_to(node)
            attractiveness = pheromone ** self.alpha * (1 / distance) ** self.beta
            probabilities.append(attractiveness)
            total += attractiveness

        probabilities = [p / total for p in probabilities]
        return probabilities

    # Обновление уровня феромонов после прохождения муравьев
    def update_pheromones(self, cycle):
        delta_pheromones = np.zeros((len(self.nodes), len(self.nodes)))

        for i in range(len(cycle) - 1):
            node1 = cycle[i]
            node2 = cycle[i + 1]
            delta_pheromones[node1.index][node2.index] += 1 / self.calculate_cycle_distance(cycle)

        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                self.pheromones[i][j] = (1 - self.evaporation_rate) * self.pheromones[i][j] + delta_pheromones[i][j]

    # Вычисление полной длины цикла
    def calculate_cycle_distance(self, cycle):
        total_distance = sum(cycle[i].distance_to(cycle[i + 1]) for i in range(len(cycle) - 1))
        total_distance += cycle[-1].distance_to(cycle[0])
        return total_distance

# Оконный класс для отображения и взаимодействия
class TSPWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Инициализация узлов (городов)
        self.nodes = [Node(10, 50, 0),
                      Node(50, 50, 1),
                      Node(30, 40, 2),
                      Node(-50, 66, 3),
                      Node(100, 110, 4),
                      Node(80, -12, 5),
                      Node(120, 100, 6),
                      Node(110, 0, 7),
                      Node(112, 44, 8),
                      Node(-15, -10, 9),
                      Node(90, 150, 10),
                      Node(35, 11, 11),
                      Node(150, 150, 12)]
        self.cycle = []  # Цикл (маршрут)

        self.initUI()
        self.draw_graph()

    def initUI(self):
        self.setWindowTitle('Решение задачи о коммивояжере методом муравьиной колонии')

        scene_width = 700
        scene_height = 180
        scene_rect = QRectF(0, 0, scene_width, scene_height)

        self.view = QGraphicsView()
        self.scene = QGraphicsScene(scene_rect)
        self.view.setScene(self.scene)

        self.label = QLabel('Кликните по полю, чтобы добавить узел, либо введите координаты узла вручную.')
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.add_button = QPushButton('Добавить узел')
        self.add_button.clicked.connect(self.add_node)
        self.solve_button = QPushButton('Найти кратчайший путь обхода')
        self.solve_button.clicked.connect(self.solve_tsp)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.view)
        layout.addWidget(QLabel('X координата:'))
        layout.addWidget(self.x_input)
        layout.addWidget(QLabel('Y координата:'))
        layout.addWidget(self.y_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.solve_button)
        layout.addWidget(self.info_text)

        self.setLayout(layout)

        self.setGeometry(100, 100, 800, 600)
        self.show()

    # Метод для добавления нового узла по координатам
    def add_node(self):
        x_text = self.x_input.text()
        y_text = self.y_input.text()

        try:
            x = float(x_text)
            y = float(y_text)
            index = len(self.nodes)
            self.nodes.append(Node(x, y, index))
            self.scene.addEllipse(x - 5, y - 5, 10, 10, QPen(Qt.blue))
            self.x_input.clear()
            self.y_input.clear()
        except ValueError:
            QMessageBox.warning(self, 'Ошибка ввода', 'Введите корректное значение координаты.')

    # Метод для решения задачи коммивояжера
    def solve_tsp(self):
        if len(self.nodes) < 3:
            self.label.setText('Добавьте как минимум 3 узла')
            return

        ant_colony = AntColony(self.nodes)
        self.cycle = ant_colony.optimize()

        self.display_info()
        self.draw_graph()

    # Вывод информации о решении задачи
    def display_info(self):
        info = 'Информация:\n'
        for node in self.nodes:
            info += f'Узел {node.index}: ({node.x}, {node.y})\n'
        info += '\nРешение (Гамильтонов цикл):\n'
        total_distance = sum(node.distance_to(self.cycle[i + 1]) for i, node in enumerate(self.cycle[:-1]))
        total_distance += self.cycle[-1].distance_to(self.cycle[0])
        for i in range(len(self.cycle) - 1):
            node1 = self.cycle[i]
            node2 = self.cycle[i + 1]
            distance = node1.distance_to(node2)
            info += f'Ребро {i + 1}: Узел {node1.index} -> Узел {node2.index}, Расстояние: {distance:.2f}\n'
        info += f'\nОбщее расстояние: {total_distance:.2f}'
        self.info_text.setPlainText(info)

    # Отрисовка графа с узлами и маршрутом
    def draw_graph(self):
        self.scene.clear()

        pen = QPen(Qt.blue)
        for node in self.nodes:
            ellipse = QGraphicsEllipseItem(node.x - 5, node.y - 5, 10, 10)
            ellipse.setPen(pen)
            self.scene.addItem(ellipse)

        pen = QPen(Qt.red)
        for i in range(len(self.cycle)):
            node1 = self.cycle[i]
            node2 = self.cycle[(i + 1) % len(self.cycle)]
            line = QGraphicsLineItem(node1.x, node1.y, node2.x, node2.y)
            line.setPen(pen)
            self.scene.addItem(line)

# Основная часть программы: создание приложения и окна для решения TSP
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TSPWindow()
    sys.exit(app.exec_())

