#!/usr/bin/env python3

import subprocess
import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


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


class HugeBrightnessMenu(Gtk.Window):
    def __init__(self):
        super().__init__(title="Управление яркостью")

        # Всплывающее окно без рамки
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.set_border_width(30)

        # Главный вертикальный слой
        main_layout = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=25
        )
        self.add(main_layout)

        # Считываем реальное значение яркости из системы
        current_brightness = get_current_brightness()

        # --- Секция яркости ---
        self.label = Gtk.Label(label=f"Яркость: {current_brightness}%")

        # Немного увеличиваем шрифт через CSS
        css = Gtk.CssProvider()
        css.load_from_data(b"""
        label.brightness-label {
            font-size: 16px;
            font-weight: bold;
        }
        scale.brightness-scale {
            min-height: 40px;
        }
        """)

        self.label.get_style_context().add_class("brightness-label")
        self.label.get_style_context().add_provider(
            css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Горизонтальный слайдер
        self.slider = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 1
        )
        self.slider.set_size_request(700, 40)
        self.slider.set_draw_value(False)
        self.slider.set_value(current_brightness)
        self.slider.set_has_origin(True)
        self.slider.get_style_context().add_class("brightness-scale")
        self.slider.get_style_context().add_provider(
            css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Шаг клавишами/колесом
        self.slider.set_increments(5, 5)
        self.slider.set_digits(0)

        main_layout.pack_start(self.label, False, False, 0)
        main_layout.pack_start(self.slider, False, False, 0)

        # Изменение яркости
        self.slider.connect("value-changed", self.set_brightness)

        # Закрытие окна
        self.connect("key-press-event", self.on_key_press)


        self.set_accept_focus(True)
        self.connect("focus-out-event", self.on_focus_out)

        # Позиционируем окно
        self.center_on_screen()

    def center_on_screen(self):
        """Размещает окно в правом нижнем углу экрана."""
        self.show_all()

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()

        if monitor is None:
            monitor = display.get_monitor(0)

        geometry = monitor.get_geometry()

        self.get_window().move(
            geometry.x + geometry.width - self.get_allocated_width() - 20,
            geometry.y + geometry.height - self.get_allocated_height() - 60
        )

    def set_brightness(self, scale):
        # Округляем до ближайшего кратного 5
        value = round(scale.get_value() / 5) * 5

        # Не допускаем выхода за пределы
        value = max(0, min(100, value))

        if abs(scale.get_value() - value) > 0.01:
            scale.handler_block_by_func(self.set_brightness)
            scale.set_value(value)
            scale.handler_unblock_by_func(self.set_brightness)

        # Выполняем команду изменения яркости
        subprocess.run(
            ["brightnessctl", "set", f"{value}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.label.set_text(f"Яркость: {value}%")
        
        
    def on_focus_out(self, window, event):
        self.destroy()
        return False


    def on_key_press(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        return False


if __name__ == "__main__":
    app = Gtk.Application(
        application_id="local.brightness.gtk",
        flags=0
    )

        
    def on_activate(application):
        window = HugeBrightnessMenu()
        window.set_application(application)
        window.show_all()



    app.connect("activate", on_activate)
    sys.exit(app.run(sys.argv))
