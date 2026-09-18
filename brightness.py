#!/usr/bin/env python3

import subprocess
import sys
import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider
)

def get_current_brightness():
    """Получает текущую яркость в процентах через brightnessctl."""
    try:
        result = subprocess.run(
            ["brightnessctl", "m"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        max_b = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 100

        result = subprocess.run(
            ["brightnessctl", "g"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        curr_b = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 50
        
        # Переводим в проценты
        return round((curr_b / max_b) * 100)
    except Exception:
        return 50

class HugeBrightnessMenu(QWidget):
    def __init__(self):
        super().__init__()

        # --- Настройки Окна ---
        self.setWindowTitle("Управление яркостью")
        
        # Флаги: делаем окно всплывающим (Popup), убираем рамки
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Главный вертикальный слой с большими отступами
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        # Считываем реальное значение яркости из системы
        current_brightness = get_current_brightness()

        # --- Секция яркости ---
        self.label = QLabel(f"Яркость: {current_brightness}%")
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Горизонтальный ряд для слайдера
        row = QHBoxLayout()
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimumWidth(700)  # Огромная длина слайдера
        self.slider.setRange(0, 100)
        self.slider.setSingleStep(5)
        self.slider.setPageStep(5)
        self.slider.setValue(current_brightness)
        self.slider.setStyleSheet("height: 40px;")  # Делаем сам слайдер крупнее
        
        # Чтобы слайдер перемещался строго по шагам в 5% при клике мыши
        self.slider.setTracking(True)
        
        row.addWidget(self.slider)

        # Собираем всё в главный слой
        main_layout.addWidget(self.label)
        main_layout.addLayout(row)

        # --- Подключение сигналов ---
        self.slider.valueChanged.connect(self.set_brightness)

        # Позиционируем окно на экране
        self.center_on_screen()

    def center_on_screen(self):
        """Размещает окно в правом нижнем углу экрана (над панелью LXQt)."""
        screen = QApplication.primaryScreen().geometry()
        self.adjustSize()  # Даем Qt посчитать реальный размер гигантского окна
        
        # Вычисляем координаты: правый край минус ширина окна, нижний край минус высота окна
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 60  # Оставляем место под панель задач
        
        self.move(x, y)

    def set_brightness(self, value):
        # Округляем до ближайшего кратного 5 для строгого шага в 5%
        value = round(value / 5) * 5
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)

        # Выполняем команду изменения яркости
        subprocess.run(
            ["brightnessctl", "set", f"{value}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.label.setText(f"Яркость: {value}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HugeBrightnessMenu()
    window.show()
    sys.exit(app.exec_())
