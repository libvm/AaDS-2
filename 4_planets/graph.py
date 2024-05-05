#!/usr/bin/env python3

import sys
import random
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSpinBox, QMessageBox
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont


class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)
        self.graph = nx.Graph()
        self.nodes_positions = {}
        self.selected_node = None
        self.distance = 1
        self.highlighted_nodes = set()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        node_pen = QPen(Qt.black)
        node_brush = QColor(255, 255, 255)

        edge_pen = QPen(Qt.black)
        font = QFont("Arial", 8)

        # Рисуем узлы
        for u, v, data in self.graph.edges(data=True):
            x1, y1 = self.nodes_positions[u]
            x2, y2 = self.nodes_positions[v]
            painter.setPen(edge_pen)
            painter.drawLine(x1, y1, x2, y2)

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2

            # Рисуем ребра
            weight = data.get("weight", "")
            painter.setFont(font)
            painter.drawText(QPointF(mid_x, mid_y), str(weight))

        # Подсвечиваем узлы
        for node, pos in self.nodes_positions.items():
            painter.setPen(node_pen)
            painter.setBrush(node_brush)
            if node in self.highlighted_nodes:
                painter.setBrush(Qt.yellow)  #Подсвечиваем подходящие узлы
            painter.drawEllipse(pos[0] - 10, pos[1] - 10, 20, 20)
            painter.drawText(pos[0] - 5, pos[1] + 5, str(node))  #Пишем номер узла

        # Рисуем выбранный узел
        if self.selected_node:
            painter.setBrush(Qt.blue)
            painter.drawEllipse(self.nodes_positions[self.selected_node][0] - 10,
                                self.nodes_positions[self.selected_node][1] - 10, 20, 20)

    def generate_graph(self, num_nodes):
        self.graph.clear()
        self.nodes_positions = {}
        self.selected_node = None
        self.highlighted_nodes.clear()

        # Генерируем случайные узлы и ребра
        for i in range(num_nodes):
            self.graph.add_node(i)
            self.nodes_positions[i] = (random.randint(50, self.width() - 50), random.randint(50, self.height() - 50))

        for u in self.graph.nodes():
            for v in self.graph.nodes():
                if u != v and random.random() < 0.2:  # Вероятность создания узла
                    weight = random.randint(1, 10)
                    self.graph.add_edge(u, v, weight=weight)

        self.update()

    def find_nodes_within_distance(self, node, distance):
        if node not in self.graph.nodes():
            return []

        reachable_nodes = nx.single_source_dijkstra_path_length(self.graph, node, cutoff=distance)
        return list(reachable_nodes.keys())

    def mousePressEvent(self, event):
        pos = event.pos()
        for node, (x, y) in self.nodes_positions.items():
            if (x - pos.x()) ** 2 + (y - pos.y()) ** 2 <= 100:
                self.selected_node = node
                self.highlighted_nodes.clear()
                self.highlighted_nodes.update(self.find_nodes_within_distance(node, self.distance))
                self.update()
                break


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Нахождение планет на заданном расстоянии")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.graph_widget = GraphWidget()
        self.layout.addWidget(self.graph_widget)

        controls_layout = QHBoxLayout()
        self.layout.addLayout(controls_layout)

        self.num_nodes_label = QLabel("Количество планет (узлов):")
        controls_layout.addWidget(self.num_nodes_label)

        self.num_nodes_spinbox = QSpinBox()
        self.num_nodes_spinbox.setMinimum(1)
        self.num_nodes_spinbox.setMaximum(100)
        controls_layout.addWidget(self.num_nodes_spinbox)

        self.generate_button = QPushButton("Сгенерировать галактику (граф)")
        self.generate_button.clicked.connect(self.generate_graph)
        controls_layout.addWidget(self.generate_button)

        self.distance_label = QLabel("Расстояние:")
        controls_layout.addWidget(self.distance_label)

        self.distance_spinbox = QSpinBox()
        self.distance_spinbox.setMinimum(1)
        self.distance_spinbox.setMaximum(100)
        controls_layout.addWidget(self.distance_spinbox)

        self.find_button = QPushButton("Найти планеты (узлы)")
        self.find_button.clicked.connect(self.find_nodes_within_distance)
        controls_layout.addWidget(self.find_button)

    def generate_graph(self):
        num_nodes = self.num_nodes_spinbox.value()
        self.graph_widget.generate_graph(num_nodes)

    def find_nodes_within_distance(self):
        node = self.graph_widget.selected_node
        distance = self.distance_spinbox.value()

        if node is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите планету (узел)")
            return

        highlighted_nodes = self.graph_widget.find_nodes_within_distance(node, distance)
        self.graph_widget.highlighted_nodes.clear()
        self.graph_widget.highlighted_nodes.update(highlighted_nodes)
        self.graph_widget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec_())

