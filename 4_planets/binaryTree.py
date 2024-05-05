#!/usr/bin/env python3

import sys
import random
from collections import deque
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QFont, QColor
from PyQt5.QtCore import Qt, QRectF, QPointF

class Node:
    def __init__(self, value, id):
        self.id = id
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value, id):
        new_node = Node(value, id)
        if self.root is None:
            self.root = new_node
        else:
            self._insert_rec(self.root, new_node)

    def _insert_rec(self, current, new_node):
        if new_node.value < current.value:
            if current.left is None:
                current.left = new_node
            else:
                self._insert_rec(current.left, new_node)
        else:
            if current.right is None:
                current.right = new_node
            else:
                self._insert_rec(current.right, new_node)

    def find_nodes_within_distance(self, start_node, distance):
        if self.root is None:
            return []

        distances = {}
        queue = deque([(start_node, 0)])  # (current_node, current_distance)
        distances[start_node] = 0
        result = []

        while queue:
            current_node, current_distance = queue.popleft()

            if current_distance == distance:
                result.append(current_node.id)

            if current_node.left and current_node.left not in distances:
                distances[current_node.left] = current_distance + 1
                queue.append((current_node.left, current_distance + 1))

            if current_node.right and current_node.right not in distances:
                distances[current_node.right] = current_distance + 1
                queue.append((current_node.right, current_distance + 1))

            parent_node = self._find_parent(self.root, current_node, start_node)
            if parent_node and parent_node not in distances:
                distances[parent_node] = current_distance + 1
                queue.append((parent_node, current_distance + 1))

        return result

    def _find_node(self, node, value):
        if node is None or node.value == value:
            return node
        elif value < node.value:
            return self._find_node(node.left, value)
        else:
            return self._find_node(node.right, value)

    def _find_parent(self, root, node, start_node):
        if root is None or root == start_node:
            return None
        
        if root.left == node or root.right == node:
            return root
        
        left_parent = self._find_parent(root.left, node, start_node)
        if left_parent:
            return left_parent
        
        return self._find_parent(root.right, node, start_node)

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.binary_tree = BinaryTree()
        self.selected_node = None
        self.distance = 0
        self.highlighted_nodes = set()

        self.setMinimumSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.binary_tree.root:
            self._draw_tree(painter, self.binary_tree.root, 400, 50, 200)

    def _draw_tree(self, painter, node, x, y, spacing):
        if not node:
            return

        x = int(x)
        y = int(y)
        x_left = int(x - spacing)
        y_left = int(y + 100)
        x_right = int(x + spacing)
        y_right = int(y + 100)

        # Draw left subtree
        if node.left:
            painter.drawLine(x, y, x_left, y_left)
            self._draw_tree(painter, node.left, x_left, y_left, spacing / 2)

        # Draw right subtree
        if node.right:
            painter.drawLine(x, y, x_right, y_right)
            self._draw_tree(painter, node.right, x_right, y_right, spacing / 2)

        # Draw node
        painter.setPen(QPen(Qt.black))
        if self.selected_node and node == self.selected_node:
            painter.setBrush(Qt.blue)  # подсвечиваем выбранный узел синим цветом
        elif node.id in self.highlighted_nodes:
            painter.setBrush(Qt.yellow)  # подсвечиваем узлы, удовлетворяющие условию, желтым цветом
        else:
            painter.setBrush(Qt.white)

        painter.drawEllipse(x - 20, y - 20, 40, 40)

        font = QFont("Arial", 10)
        painter.setFont(font)
        painter.drawText(QRectF(x - 20, y - 20, 40, 40), Qt.AlignCenter, str(node.value))

    def generate_random_tree(self, num_nodes):
        self.binary_tree = BinaryTree()
        self.selected_node = None
        self.highlighted_nodes.clear()

        for i in range(num_nodes):
            self.binary_tree.insert(random.randint(1, 100), i)

        self.update()

    def find_and_highlight_nodes(self):
        if self.selected_node is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите узел")
            return

        distance = self.distance
        highlighted_nodes = self.binary_tree.find_nodes_within_distance(self.selected_node, distance)
        self.highlighted_nodes = set(highlighted_nodes)
        self.update()

    def mousePressEvent(self, event):
        click_pos = event.pos()
        selected_node = self._find_node_at(self.binary_tree.root, click_pos, QPointF(400, 50), 200)
        if selected_node is not None:
            self.selected_node = selected_node
            self.find_and_highlight_nodes()
        else:
            self.selected_node = None
            self.highlighted_nodes.clear()
            self.update()

    def _find_node_at(self, node, click_pos, node_pos, spacing):
        if not node:
            return None

        node_center = QPointF(node_pos.x(), node_pos.y())
        click_point = QPointF(click_pos.x(), click_pos.y())

        # Check distance to node center
        if (click_point - node_center).manhattanLength() <= 20:
            return node

        # Recursively search in both directions
        left_result = self._find_node_at(node.left, click_pos, QPointF(node_pos.x() - spacing, node_pos.y() + 100), spacing / 2)
        if left_result is not None:
            return left_result

        right_result = self._find_node_at(node.right, click_pos, QPointF(node_pos.x() + spacing, node_pos.y() + 100), spacing / 2)
        if right_result is not None:
            return right_result

        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Отображение бинарного дерева")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.graph_widget = GraphWidget()
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.graph_widget)

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        num_nodes_label = QLabel("Количество узлов:")
        control_layout.addWidget(num_nodes_label)

        self.num_nodes_spinbox = QSpinBox()
        self.num_nodes_spinbox.setMinimum(1)
        self.num_nodes_spinbox.setMaximum(100)
        control_layout.addWidget(self.num_nodes_spinbox)

        generate_button = QPushButton("Сгенерировать дерево")
        generate_button.clicked.connect(self.generate_tree)
        control_layout.addWidget(generate_button)

        distance_label = QLabel("Расстояние:")
        control_layout.addWidget(distance_label)

        self.distance_spinbox = QSpinBox()
        self.distance_spinbox.setMinimum(0)
        self.distance_spinbox.setMaximum(100)
        control_layout.addWidget(self.distance_spinbox)

        find_button = QPushButton("Найти узлы")
        find_button.clicked.connect(self.find_nodes_within_distance)
        control_layout.addWidget(find_button)

    def generate_tree(self):
        num_nodes = self.num_nodes_spinbox.value()
        self.graph_widget.generate_random_tree(num_nodes)

    def find_nodes_within_distance(self):
        if self.graph_widget.selected_node is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите узел")
            return

        distance = self.distance_spinbox.value()
        self.graph_widget.distance = distance
        self.graph_widget.find_and_highlight_nodes()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.resize(800, 600)
    main_window.show()
    sys.exit(app.exec_())

