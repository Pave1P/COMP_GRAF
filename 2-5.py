import tkinter as tk
from tkinter import ttk
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SplineCurve:
    def __init__(self, color="red"):
        self.control_points = []
        self.color = color
        self.show_control_lines = True
        self.show_points = True
        self.line_width = 3
        self.tension = 0.5
        self.additional_points = []  # Дополнительные промежуточные точки

    def add_control_point(self, point):
        self.control_points.append(point)
        self.generate_additional_points()

    def remove_last_control_point(self):
        if self.control_points:
            point = self.control_points.pop()
            self.generate_additional_points()
            return point
        return None

    def clear_control_points(self):
        self.control_points.clear()
        self.additional_points.clear()

    def set_tension(self, value):
        self.tension = max(0.1, min(0.9, float(value)))
        self.generate_additional_points()

    def generate_additional_points(self):
        """Генерирует 2 промежуточные точки на каждом сегменте между контрольными точками"""
        self.additional_points = []

        if len(self.control_points) < 2:
            return

        for i in range(len(self.control_points) - 1):
            p1 = self.control_points[i]
            p2 = self.control_points[i + 1]

            # Вычисляем вектор направления
            dx = p2.x - p1.x
            dy = p2.y - p1.y

            # Две промежуточные точки на расстоянии 1/3 и 2/3 от p1 до p2
            add_point1 = Point(
                p1.x + dx * 0.33,
                p1.y + dy * 0.33
            )

            add_point2 = Point(
                p1.x + dx * 0.67,
                p1.y + dy * 0.67
            )

            self.additional_points.extend([add_point1, add_point2])

    def catmull_rom_point(self, t, p0, p1, p2, p3):
        """Катмулл-Ром сплайн для плавной интерполяции"""
        t2 = t * t
        t3 = t2 * t

        return Point(
            0.5 * ((2 * p1.x) +
                   (-p0.x + p2.x) * t +
                   (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
                   (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3),

            0.5 * ((2 * p1.y) +
                   (-p0.y + p2.y) * t +
                   (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
                   (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3)
        )

    def draw_control_lines(self, canvas):
        if len(self.control_points) < 2:
            return

        points_coords = []
        for point in self.control_points:
            points_coords.extend([point.x, point.y])

        canvas.create_line(points_coords, fill="lightgray", width=1, dash=(2, 2))

    def draw_additional_points_lines(self, canvas):
        """Рисует линии к дополнительным точкам"""
        if len(self.additional_points) == 0:
            return

        # Соединяем дополнительные точки с ближайшими контрольными точками
        for i, add_point in enumerate(self.additional_points):
            control_point_index = i // 2  # Каждые 2 доп. точки относятся к одному сегменту
            if control_point_index < len(self.control_points) - 1:
                p1 = self.control_points[control_point_index]
                p2 = self.control_points[control_point_index + 1]

                # Рисуем пунктирные линии к обоим контрольным точкам сегмента
                canvas.create_line(add_point.x, add_point.y, p1.x, p1.y,
                                   fill="#FFA000", width=1, dash=(1, 2))
                canvas.create_line(add_point.x, add_point.y, p2.x, p2.y,
                                   fill="#FFA000", width=1, dash=(1, 2))

    def draw_control_points(self, canvas):
        for i, point in enumerate(self.control_points):
            # Рисуем контрольные точки
            canvas.create_oval(point.x - 4, point.y - 4, point.x + 4, point.y + 4,
                               fill="#4CAF50", outline="#2E7D32", width=2)

            # Номера точек
            canvas.create_text(point.x, point.y - 15, text=str(i + 1),
                               fill="#2E7D32", font=("Arial", 9, "bold"))

    def draw_additional_points(self, canvas):
        """Рисует дополнительные промежуточные точки"""
        for i, point in enumerate(self.additional_points):
            # Рисуем дополнительные точки (оранжевые)
            canvas.create_oval(point.x - 3, point.y - 3, point.x + 3, point.y + 3,
                               fill="#FF9800", outline="#F57C00", width=1)

            # Подписываем дополнительные точки буквами
            segment_num = i // 2 + 1  # Номер сегмента
            point_in_segment = i % 2 + 1  # 1 или 2 точка в сегменте
            label = f"{segment_num}.{point_in_segment}"
            canvas.create_text(point.x, point.y - 12, text=label,
                               fill="#E65100", font=("Arial", 8))

    def draw_curve(self, canvas):
        if len(self.control_points) < 2:
            return

        # Для Catmull-Rom сплайна нужно минимум 4 точки
        if len(self.control_points) >= 4:
            curve_points = []

            # Добавляем первую точку
            curve_points.append(self.control_points[0].x)
            curve_points.append(self.control_points[0].y)

            # Генерируем кривую между точками
            for i in range(len(self.control_points) - 3):
                p0 = self.control_points[i]
                p1 = self.control_points[i + 1]
                p2 = self.control_points[i + 2]
                p3 = self.control_points[i + 3]

                segments = 20  # Количество сегментов между точками
                for j in range(segments + 1):
                    t = j / segments
                    point = self.catmull_rom_point(t, p0, p1, p2, p3)
                    curve_points.extend([point.x, point.y])

            # Добавляем последнюю точку
            last_point = self.control_points[-1]
            curve_points.extend([last_point.x, last_point.y])

            # Рисуем сглаженную кривую
            canvas.create_line(curve_points, fill=self.color, width=self.line_width, smooth=True)
        else:
            # Для 2-3 точек рисуем простую кривую Безье
            if len(self.control_points) == 2:
                p1, p2 = self.control_points
                canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                   fill=self.color, width=self.line_width)
            elif len(self.control_points) == 3:
                p1, p2, p3 = self.control_points
                canvas.create_line(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y,
                                   fill=self.color, width=self.line_width, smooth=True)

    def draw(self, canvas):
        if not self.control_points:
            return

        # Рисуем контрольные линии
        if self.show_control_lines and len(self.control_points) >= 2:
            self.draw_control_lines(canvas)

        # Рисуем линии к дополнительным точкам
        self.draw_additional_points_lines(canvas)

        # Рисуем саму кривую
        self.draw_curve(canvas)

        # Рисуем контрольные точки
        if self.show_points:
            self.draw_control_points(canvas)

        # Рисуем дополнительные точки
        self.draw_additional_points(canvas)


class SplineManager:
    def __init__(self):
        self.splines = []
        self.current_spline = None
        self.spline_colors = [
            "#E91E63", "#9C27B0", "#2196F3", "#009688",
            "#FF9800", "#795548", "#607D8B"
        ]
        self.color_index = 0

    def start_new_spline(self):
        color = self.spline_colors[self.color_index % len(self.spline_colors)]
        self.color_index += 1
        self.current_spline = SplineCurve(color=color)
        return self.current_spline

    def finish_current_spline(self):
        if self.current_spline and len(self.current_spline.control_points) >= 2:
            self.splines.append(self.current_spline)
            finished = self.current_spline
            self.current_spline = None
            return finished
        return None

    def get_current_spline(self):
        return self.current_spline

    def clear_all_splines(self):
        self.splines.clear()
        self.current_spline = None

    def remove_last_spline(self):
        if self.splines:
            return self.splines.pop()
        return None

    def get_spline_count(self):
        return len(self.splines)

    def get_total_point_count(self):
        total = 0
        for spline in self.splines:
            total += len(spline.control_points)
        if self.current_spline:
            total += len(self.current_spline.control_points)
        return total

    def get_total_additional_point_count(self):
        total = 0
        for spline in self.splines:
            total += len(spline.additional_points)
        if self.current_spline:
            total += len(self.current_spline.additional_points)
        return total


class SplineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №3 - Сплайновые кривые с промежуточными точками")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f5f5f5')

        self.spline_manager = SplineManager()
        self.is_adding_points = False

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Управление сплайнами", padding=15)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        ttk.Button(control_frame, text="Новый сплайн",
                   command=self.start_spline, width=20).pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Добавить точки",
                   command=self.enable_point_adding, width=20).pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Завершить сплайн",
                   command=self.finish_spline, width=20).pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Удалить последнюю точку",
                   command=self.remove_last_point, width=20).pack(fill=tk.X, pady=5)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Tension control
        tension_frame = ttk.Frame(control_frame)
        tension_frame.pack(fill=tk.X, pady=5)

        ttk.Label(tension_frame, text="Натяжение:").pack(anchor=tk.W)
        self.tension_var = tk.DoubleVar(value=0.5)
        tension_scale = ttk.Scale(tension_frame, from_=0.1, to=0.9,
                                  variable=self.tension_var, orient=tk.HORIZONTAL,
                                  command=self.update_tension)
        tension_scale.pack(fill=tk.X, pady=5)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Display options
        display_frame = ttk.Frame(control_frame)
        display_frame.pack(fill=tk.X, pady=5)

        ttk.Button(display_frame, text="Вкл/Выкл контрольные линии",
                   command=self.toggle_control_lines, width=20).pack(fill=tk.X, pady=2)

        ttk.Button(display_frame, text="Вкл/Выкл точки",
                   command=self.toggle_points, width=20).pack(fill=tk.X, pady=2)

        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Spline management
        ttk.Button(control_frame, text="Удалить последний сплайн",
                   command=self.remove_last_spline, width=20).pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Очистить все",
                   command=self.clear_all, width=20).pack(fill=tk.X, pady=5)

        # Info panel
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=10)

        self.info_var = tk.StringVar(value="Сплайны: 0, Контрольные: 0, Промежуточные: 0")
        ttk.Label(info_frame, textvariable=self.info_var,
                  font=("Arial", 10), background="#e8f5e8",
                  relief=tk.SUNKEN, padding=5).pack(fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(control_frame, textvariable=self.status_var,
                  font=("Arial", 9), foreground="#666",
                  background="#f0f0f0", relief=tk.SUNKEN,
                  padding=3).pack(side=tk.BOTTOM, fill=tk.X)

        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

    def start_spline(self):
        self.spline_manager.start_new_spline()
        self.is_adding_points = True
        self.update_info()
        self.status_var.set("Режим создания сплайна - кликайте по холсту")

    def enable_point_adding(self):
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            self.is_adding_points = True
            self.status_var.set("Режим добавления точек - кликайте по холсту")
        else:
            self.status_var.set("Сначала создайте новый сплайн")

    def finish_spline(self):
        finished_spline = self.spline_manager.finish_current_spline()
        if finished_spline:
            self.is_adding_points = False
            self.redraw_canvas()
            point_count = len(finished_spline.control_points)
            additional_count = len(finished_spline.additional_points)
            self.update_info()
            self.status_var.set(f"Сплайн завершен: {point_count} контрольных, {additional_count} промежуточных точек")
        else:
            self.status_var.set("Нужно как минимум 2 точки для сплайна")

    def remove_last_point(self):
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            removed_point = current_spline.remove_last_control_point()
            if removed_point:
                self.redraw_canvas()
                point_count = len(current_spline.control_points)
                additional_count = len(current_spline.additional_points)
                self.update_info()
                self.status_var.set(f"Удалена точка. Контрольных: {point_count}, промежуточных: {additional_count}")
            else:
                self.status_var.set("Нет точек для удаления")
        else:
            self.status_var.set("Нет активного сплайна")

    def remove_last_spline(self):
        removed_spline = self.spline_manager.remove_last_spline()
        if removed_spline:
            self.redraw_canvas()
            self.update_info()
            self.status_var.set("Удален последний сплайн")
        else:
            self.status_var.set("Нет сплайнов для удаления")

    def update_tension(self, value):
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.set_tension(value)
            self.redraw_canvas()
            self.status_var.set(f"Натяжение: {float(value):.1f}")

    def toggle_control_lines(self):
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.show_control_lines = not current_spline.show_control_lines
            self.redraw_canvas()
            state = "включены" if current_spline.show_control_lines else "выключены"
            self.status_var.set(f"Контрольные линии {state}")

    def toggle_points(self):
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.show_points = not current_spline.show_points
            self.redraw_canvas()
            state = "включены" if current_spline.show_points else "выключены"
            self.status_var.set(f"Контрольные точки {state}")

    def clear_all(self):
        self.spline_manager.clear_all_splines()
        self.is_adding_points = False
        self.redraw_canvas()
        self.update_info()
        self.status_var.set("Все сплайны удалены")

    def on_canvas_click(self, event):
        if self.is_adding_points:
            current_spline = self.spline_manager.get_current_spline()
            if current_spline:
                point = Point(event.x, event.y)
                current_spline.add_control_point(point)
                point_count = len(current_spline.control_points)
                additional_count = len(current_spline.additional_points)
                self.redraw_canvas()
                self.update_info()
                self.status_var.set(
                    f"Добавлена точка {point_count}. Контрольных: {point_count}, промежуточных: {additional_count}")

    def on_canvas_motion(self, event):
        # Можно добавить предпросмотр следующей точки
        pass

    def redraw_canvas(self):
        self.canvas.delete("all")

        # Рисуем сетку для удобства
        self.draw_grid()

        # Рисуем все завершенные сплайны
        for spline in self.spline_manager.splines:
            spline.draw(self.canvas)

        # Рисуем текущий сплайн
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.draw(self.canvas)

    def draw_grid(self):
        """Рисует сетку на холсте для удобства позиционирования"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width > 1 and height > 1:
            # Вертикальные линии
            for x in range(0, width, 50):
                self.canvas.create_line(x, 0, x, height, fill="#f0f0f0", width=1)

            # Горизонтальные линии
            for y in range(0, height, 50):
                self.canvas.create_line(0, y, width, y, fill="#f0f0f0", width=1)

    def update_info(self):
        spline_count = self.spline_manager.get_spline_count()
        total_control_points = self.spline_manager.get_total_point_count()
        total_additional_points = self.spline_manager.get_total_additional_point_count()
        current_spline = self.spline_manager.get_current_spline()

        if current_spline:
            current_control = len(current_spline.control_points)
            current_additional = len(current_spline.additional_points)
            info_text = f"Сплайны: {spline_count}, Контрольные: {total_control_points}, Промежуточные: {total_additional_points} (текущий: {current_control}+{current_additional})"
        else:
            info_text = f"Сплайны: {spline_count}, Контрольные: {total_control_points}, Промежуточные: {total_additional_points}"

        self.info_var.set(info_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = SplineApp(root)
    root.mainloop()
