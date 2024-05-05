#!/usr/bin/env python3

import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QTextEdit, QLineEdit, QMessageBox
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QRectF

class Node:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index

    def distance_to(self, node):
        return math.sqrt((self.x - node.x)**2 + (self.y - node.y)**2)

class TSPSolver:
    def __init__(self, nodes):
        self.nodes = nodes
        self.visited = [False] * len(nodes)

    def nearest_neighbor_hamiltonian_cycle(self):
        start_node = self.nodes[0]
        current_node = start_node
        self.visited[self.nodes.index(start_node)] = True
        path = [current_node]

        while len(path) < len(self.nodes):
            nearest_dist = float('inf')
            nearest_node = None
            for i, node in enumerate(self.nodes):
                if not self.visited[i]:
                    dist = current_node.distance_to(node)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest_node = node
            self.visited[self.nodes.index(nearest_node)] = True
            path.append(nearest_node)
            current_node = nearest_node

        path.append(start_node)
        return path

class TSPWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.nodes = []

        self.path = []

        self.initUI()
        self.draw_graph()

    def initUI(self):
        self.setWindowTitle('Решение задачи о коммивояжере методом ближайших соседей')

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

    def add_node(self):
        x_text = self.x_input.text()
        y_text = self.y_input.text()

        try:
            x = float(x_text)
            y = float(y_text)
            index = len(self.nodes) + 1
            self.nodes.append(Node(x, y, index))
            self.scene.addEllipse(x - 5, y - 5, 10, 10, QPen(Qt.blue))
            self.x_input.clear()
            self.y_input.clear()
        except ValueError:
            QMessageBox.warning(self, 'Ошибка ввода', 'Введите корректное значение координаты.')

    def solve_tsp(self):
        if len(self.nodes) < 2:
            self.label.setText('Добавьте как минимум 2 узла')
            return

        solver = TSPSolver(self.nodes)
        self.path = solver.nearest_neighbor_hamiltonian_cycle()

        self.display_info()
        self.draw_graph()

    def display_info(self):
        info = 'Информация:\n'
        for node in self.nodes:
            info += f'Узел {node.index}: ({node.x}, {node.y})\n'
        info += '\nРешение:\n'
        total_distance = 0
        for i in range(len(self.path) - 1):
            node1 = self.path[i]
            node2 = self.path[i + 1]
            distance = node1.distance_to(node2)
            total_distance += distance
            info += f'Ребро {i+1}: Узел {node1.index} -> Узел {node2.index}, Расстояние: {distance:.2f}\n'
        info += f'\nОбщее расстояние: {total_distance:.2f}'
        self.info_text.setPlainText(info)

    def draw_graph(self):
        self.scene.clear()

        pen = QPen(Qt.blue)
        for node in self.nodes:
            ellipse = QGraphicsEllipseItem(node.x - 5, node.y - 5, 10, 10)
            ellipse.setPen(pen)
            self.scene.addItem(ellipse)

        pen = QPen(Qt.red)
        for i in range(len(self.path) - 1):
            node1 = self.path[i]
            node2 = self.path[i + 1]
            line = QGraphicsLineItem(node1.x, node1.y, node2.x, node2.y)
            line.setPen(pen)
            self.scene.addItem(line)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPos()
            widget_pos = self.view.mapFromGlobal(global_pos)
            scene_pos = self.view.mapToScene(widget_pos)
            x = scene_pos.x()
            y = scene_pos.y()
            index = len(self.nodes) + 1
            self.nodes.append(Node(x, y, index))
            self.scene.addEllipse(x - 5, y - 5, 10, 10, QPen(Qt.blue))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TSPWindow()
    sys.exit(app.exec_())

