import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import struct
from PIL import Image, ImageTk, ImageDraw
import os


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №2 - Алгоритмы двумерных преобразований
# =============================================================================

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def transform(self, dx=0, dy=0, angle=0, pivot=None):
        """Преобразование точки (перенос + поворот)"""
        # Перенос
        x_new = self.x + dx
        y_new = self.y + dy

        # Поворот относительно pivot точки
        if angle != 0 and pivot:
            # Смещаем точку относительно центра поворота
            x_rel = x_new - pivot.x
            y_rel = y_new - pivot.y

            # Поворачиваем
            rad = math.radians(angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            x_rot = x_rel * cos_a - y_rel * sin_a
            y_rot = x_rel * sin_a + y_rel * cos_a

            # Возвращаем обратно
            x_new = x_rot + pivot.x
            y_new = y_rot + pivot.y

        return Point(x_new, y_new)

    def __str__(self):
        return f"({self.x}, {self.y})"


class Polygon:
    def __init__(self, points=None, color="black"):
        self.points = points if points else []
        self.color = color

    def add_point(self, point):
        self.points.append(point)

    def draw(self, canvas):
        """Рисование полигона на canvas"""
        if len(self.points) < 2:
            return

        points_coords = []
        for point in self.points:
            points_coords.extend([point.x, point.y])

        canvas.create_polygon(points_coords, outline=self.color, fill="", width=2)

    def transform(self, dx=0, dy=0, angle=0):
        """Преобразование полигона (перенос + поворот)"""
        if not self.points:
            return

        # Используем первую точку как центр поворота
        pivot = self.points[0]

        # Применяем преобразование ко всем точкам
        new_points = []
        for point in self.points:
            new_point = point.transform(dx, dy, angle, pivot)
            new_points.append(new_point)

        self.points = new_points

    def get_bounds(self):
        """Получить границы полигона"""
        if not self.points:
            return 0, 0, 0, 0

        x_coords = [p.x for p in self.points]
        y_coords = [p.y for p in self.points]

        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


class ShapeFactory:
    """Фабрика для создания фигур варианта 16 - два соединенных треугольника"""

    @staticmethod
    def create_double_triangle(center_x, center_y, size=50):
        """Создать два соединенных треугольника (вариант 16)"""
        points = []

        # Первый треугольник (верхний/правый)
        points.append(Point(center_x + size, center_y))  # Правая вершина
        points.append(Point(center_x, center_y - size))  # Верхняя вершина
        points.append(Point(center_x - size // 2, center_y))  # Левая вершина

        # Второй треугольник (нижний/левый)
        points.append(Point(center_x - size, center_y))  # Левая вершина
        points.append(Point(center_x, center_y + size))  # Нижняя вершина
        points.append(Point(center_x + size // 2, center_y))  # Правая вершина

        return Polygon(points, "blue")


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №3 - Сплайновые кривые (УЛУЧШЕННАЯ ВЕРСИЯ)
# =============================================================================

class SplineCurve:
    def __init__(self, control_points=None, color="red", segments=100):
        self.control_points = control_points if control_points else []
        self.color = color
        self.segments = segments
        self.show_control_lines = True
        self.show_points = True
        self.line_width = 3

    def add_control_point(self, point):
        """Добавить контрольную точку"""
        self.control_points.append(point)

    def clear_control_points(self):
        """Очистить все контрольные точки"""
        self.control_points.clear()

    def remove_last_control_point(self):
        """Удалить последнюю контрольную точку"""
        if self.control_points:
            return self.control_points.pop()
        return None

    def insert_control_point(self, index, point):
        """Вставить контрольную точку в указанную позицию"""
        if 0 <= index <= len(self.control_points):
            self.control_points.insert(index, point)
            return True
        return False

    def bezier_point(self, t, points):
        """Вычисление точки на кривой Безье для параметра t"""
        n = len(points) - 1
        x = 0.0
        y = 0.0

        for i, point in enumerate(points):
            # Биномиальный коэффициент
            binom = math.comb(n, i) if hasattr(math, 'comb') else self.comb(n, i)
            # Полином Бернштейна
            bernstein = binom * (t ** i) * ((1 - t) ** (n - i))

            x += point.x * bernstein
            y += point.y * bernstein

        return Point(x, y)

    def comb(self, n, k):
        """Вычисление биномиального коэффициента (для старых версий Python)"""
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        k = min(k, n - k)
        numerator = 1
        denominator = 1
        for i in range(1, k + 1):
            numerator *= n - i + 1
            denominator *= i
        return numerator // denominator

    def draw_control_lines(self, canvas):
        """Рисование контрольных линий между точками"""
        if len(self.control_points) < 2:
            return

        points_coords = []
        for point in self.control_points:
            points_coords.extend([point.x, point.y])

        # Рисуем пунктирные контрольные линии
        canvas.create_line(points_coords, fill="gray", width=1, dash=(4, 2))

    def draw_control_points(self, canvas):
        """Рисование контрольных точек с номерами"""
        for i, point in enumerate(self.control_points):
            # Рисуем точку
            canvas.create_oval(point.x - 5, point.y - 5, point.x + 5, point.y + 5,
                               fill="green", outline="darkgreen", width=2)

            # Подписываем точку номером
            canvas.create_text(point.x, point.y - 18, text=str(i + 1),
                               fill="darkgreen", font=("Arial", 10, "bold"))

    def draw_composite_bezier(self, canvas):
        """Рисование составной кривой Безье из множества контрольных точек"""
        if len(self.control_points) < 2:
            return

        # Для составной кривой Безье используем все точки
        curve_points = []

        # Генерируем точки для всей кривой
        total_segments = len(self.control_points) - 1
        if total_segments > 0:
            for seg in range(total_segments):
                for j in range(self.segments // total_segments + 1):
                    t = j / (self.segments // total_segments)
                    # Используем текущую и следующую точки для линейной интерполяции
                    if seg < len(self.control_points) - 1:
                        p1 = self.control_points[seg]
                        p2 = self.control_points[seg + 1]
                        x = p1.x + (p2.x - p1.x) * t
                        y = p1.y + (p2.y - p1.y) * t
                        curve_points.append((x, y))

        # Рисуем сглаженную кривую
        if len(curve_points) > 1:
            canvas.create_line(curve_points, fill=self.color, width=self.line_width, smooth=True)

    def draw_cubic_bezier_segments(self, canvas):
        """Рисование кубических кривых Безье сегментами по 4 точки"""
        if len(self.control_points) < 4:
            return self.draw_composite_bezier(canvas)

        colors = ["red", "blue", "green", "purple", "orange", "cyan", "magenta"]
        color_index = 0

        # Разбиваем на сегменты по 4 точки с перекрытием
        for i in range(0, len(self.control_points) - 3, 3):
            segment_points = self.control_points[i:i + 4]
            color = colors[color_index % len(colors)]
            color_index += 1

            # Генерируем точки для этого сегмента
            segment_curve = []
            for j in range(self.segments + 1):
                t = j / self.segments
                point = self.bezier_point(t, segment_points)
                segment_curve.append((point.x, point.y))

            # Рисуем сегмент
            if len(segment_curve) > 1:
                canvas.create_line(segment_curve, fill=color, width=self.line_width - 1, smooth=True)

    def draw(self, canvas):
        """Рисование сплайновой кривой с контрольными точками и линиями"""
        if len(self.control_points) < 2:
            return

        # Рисуем контрольные линии (если включено)
        if self.show_control_lines and len(self.control_points) >= 2:
            self.draw_control_lines(canvas)

        # Рисуем кривую Безье
        if len(self.control_points) >= 4:
            self.draw_cubic_bezier_segments(canvas)
        else:
            self.draw_composite_bezier(canvas)

        # Рисуем контрольные точки (если включено)
        if self.show_points:
            self.draw_control_points(canvas)

    def toggle_control_lines(self):
        """Переключение отображения контрольных линий"""
        self.show_control_lines = not self.show_control_lines

    def toggle_points(self):
        """Переключение отображения контрольных точек"""
        self.show_points = not self.show_points

    def set_line_width(self, width):
        """Установить толщину линии"""
        self.line_width = max(1, min(width, 10))

    def get_point_count(self):
        """Получить количество контрольных точек"""
        return len(self.control_points)

    def get_bounds(self):
        """Получить границы сплайна"""
        if not self.control_points:
            return 0, 0, 0, 0

        x_coords = [p.x for p in self.control_points]
        y_coords = [p.y for p in self.control_points]

        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)


class SplineManager:
    """Менеджер для управления несколькими сплайнами"""

    def __init__(self):
        self.splines = []
        self.current_spline = None
        self.spline_colors = ["red", "blue", "green", "purple", "orange", "brown", "pink"]
        self.color_index = 0

    def start_new_spline(self, color=None):
        """Начать новый сплайн"""
        if color is None:
            color = self.spline_colors[self.color_index % len(self.spline_colors)]
            self.color_index += 1

        self.current_spline = SplineCurve(color=color)
        return self.current_spline

    def finish_current_spline(self):
        """Завершить текущий сплайн"""
        if self.current_spline and self.current_spline.get_point_count() >= 2:
            self.splines.append(self.current_spline)
            finished_spline = self.current_spline
            self.current_spline = None
            return finished_spline
        return None

    def cancel_current_spline(self):
        """Отменить текущий сплайн"""
        cancelled_spline = self.current_spline
        self.current_spline = None
        return cancelled_spline

    def get_current_spline(self):
        """Получить текущий сплайн"""
        return self.current_spline

    def clear_all_splines(self):
        """Очистить все сплайны"""
        self.splines.clear()
        self.current_spline = None

    def remove_last_spline(self):
        """Удалить последний завершенный сплайн"""
        if self.splines:
            return self.splines.pop()
        return None

    def get_spline_count(self):
        """Получить количество завершенных сплайнов"""
        return len(self.splines)

    def get_total_point_count(self):
        """Получить общее количество контрольных точек"""
        total = 0
        for spline in self.splines:
            total += spline.get_point_count()
        if self.current_spline:
            total += self.current_spline.get_point_count()
        return total


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №4 - Растровые ресурсы и кисти
# =============================================================================

class BitmapResource:
    def __init__(self, width=32, height=32):
        self.width = width
        self.height = height
        self.pixels = [[(255, 255, 255) for _ in range(width)] for _ in range(height)]
        self.photo_image = None

    def create_double_triangle_pattern(self):
        """Создание растрового шаблона двойного треугольника (вариант 16)"""
        center_x = self.width // 2
        center_y = self.height // 2
        size = min(center_x, center_y) - 2

        # Создаем PIL изображение для рисования
        pil_image = Image.new('RGB', (self.width, self.height), (240, 240, 240))
        draw = ImageDraw.Draw(pil_image)

        # Координаты для двойного треугольника
        triangle1 = [
            (center_x + size, center_y),
            (center_x, center_y - size),
            (center_x - size // 2, center_y)
        ]

        triangle2 = [
            (center_x - size, center_y),
            (center_x, center_y + size),
            (center_x + size // 2, center_y)
        ]

        # Рисуем треугольники
        draw.polygon(triangle1, fill=(0, 100, 200), outline=(0, 50, 150))
        draw.polygon(triangle2, fill=(200, 100, 0), outline=(150, 50, 0))

        # Конвертируем обратно в пиксели
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = pil_image.getpixel((x, y))

    def get_photo_image(self):
        """Получить PhotoImage для Tkinter"""
        if self.photo_image is None:
            pil_image = Image.new('RGB', (self.width, self.height))
            for y in range(self.height):
                for x in range(self.width):
                    pil_image.putpixel((x, y), self.pixels[y][x])

            self.photo_image = ImageTk.PhotoImage(pil_image)

        return self.photo_image


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №5 - Загрузка BMP и масштабирование
# =============================================================================

class EnhancedBMPLoader:
    def __init__(self):
        self.image_data = None
        self.width = 0
        self.height = 0
        self.bits_per_pixel = 0

    def create_test_image(self):
        """Создание тестового изображения с деталями для демонстрации"""
        width, height = 200, 200
        self.width = width
        self.height = height
        self.image_data = []

        # Создаем сложное тестовое изображение
        for y in range(height):
            row = []
            for x in range(width):
                # Вертикальные полосы
                if x % 20 < 10:
                    r, g, b = 255, 0, 0  # Красный
                else:
                    r, g, b = 0, 0, 255  # Синий

                # Горизонтальные полосы
                if y % 20 < 10:
                    r = min(r + 50, 255)
                    b = max(b - 50, 0)

                # Диагональная линия
                if abs(x - y) < 3:
                    r, g, b = 255, 255, 0  # Желтый

                # Текст или мелкие детали
                if 80 <= x <= 120 and 80 <= y <= 120:
                    if (x - 100) ** 2 + (y - 100) ** 2 < 400:  # Круг
                        r, g, b = 0, 255, 0  # Зеленый

                row.append((r, g, b))
            self.image_data.append(row)

        return True

    def scale_image(self, scale_factor, mode="nearest"):
        """Масштабирование изображения с заданным коэффициентом"""
        if not self.image_data:
            return None, 0, 0

        new_width = max(1, int(self.width * scale_factor))
        new_height = max(1, int(self.height * scale_factor))

        scaled_data = [[(0, 0, 0) for _ in range(new_width)] for _ in range(new_height)]

        for y in range(new_height):
            for x in range(new_width):
                # Вычисляем координаты в исходном изображении
                src_x = x * (self.width - 1) / (new_width - 1) if new_width > 1 else 0
                src_y = y * (self.height - 1) / (new_height - 1) if new_height > 1 else 0

                if mode == "nearest":
                    # Ближайший сосед
                    nearest_x = min(int(round(src_x)), self.width - 1)
                    nearest_y = min(int(round(src_y)), self.height - 1)
                    scaled_data[y][x] = self.image_data[nearest_y][nearest_x]

        return scaled_data, new_width, new_height

    def get_photo_image(self, data=None, width=None, height=None):
        """Получить PhotoImage для отображения"""
        data_to_use = data if data else self.image_data
        if not data_to_use:
            return None

        h = len(data_to_use)
        w = len(data_to_use[0]) if h > 0 else 0

        pil_image = Image.new('RGB', (w, h))
        for y in range(h):
            for x in range(w):
                pil_image.putpixel((x, y), data_to_use[y][x])

        # Масштабируем для отображения
        if width and height:
            pil_image = pil_image.resize((width, height), Image.NEAREST)

        return ImageTk.PhotoImage(pil_image)


# =============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# =============================================================================

class PainterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painter - Лабораторные работы 2-5 (Улучшенные сплайны)")
        self.root.geometry("1200x800")

        # Данные приложения
        self.current_polygon = None
        self.polygons = []
        self.spline_manager = SplineManager()  # Используем менеджер сплайнов
        self.bitmap_resources = []
        self.bmp_loader = EnhancedBMPLoader()
        self.current_scaling_mode = "nearest"
        self.is_adding_points = False

        # Создание интерфейса
        self.create_interface()

        # Создание тестового растрового ресурса
        self.create_test_bitmap()

    def create_interface(self):
        """Создание интерфейса пользователя"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - controls
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)

        # Canvas
        self.canvas = tk.Canvas(main_frame, bg="white", width=600, height=500)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Bottom panel for bitmap display
        self.bitmap_frame = ttk.Frame(main_frame)
        self.bitmap_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5, 0))

        # ===== LAB 2 Controls =====
        lab2_frame = ttk.LabelFrame(control_frame, text="Лаб. 2: Полигоны", padding=5)
        lab2_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab2_frame, text="Создать двойной треугольник",
                   command=self.create_double_triangle).pack(fill=tk.X, pady=2)

        # Transform controls
        transform_frame = ttk.Frame(lab2_frame)
        transform_frame.pack(fill=tk.X, pady=5)

        ttk.Label(transform_frame, text="Перенос:").grid(row=0, column=0, sticky="w")
        self.dx_var = tk.StringVar(value="10")
        self.dy_var = tk.StringVar(value="10")
        ttk.Entry(transform_frame, textvariable=self.dx_var, width=5).grid(row=0, column=1, padx=2)
        ttk.Entry(transform_frame, textvariable=self.dy_var, width=5).grid(row=0, column=2, padx=2)

        ttk.Label(transform_frame, text="Поворот:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self.angle_var = tk.StringVar(value="45")
        ttk.Entry(transform_frame, textvariable=self.angle_var, width=5).grid(row=1, column=1, padx=2, pady=(5, 0))
        ttk.Label(transform_frame, text="°").grid(row=1, column=2, sticky="w", pady=(5, 0))

        ttk.Button(lab2_frame, text="Применить преобразования",
                   command=self.apply_transformations).pack(fill=tk.X, pady=2)

        # ===== LAB 3 Controls (УЛУЧШЕННЫЕ) =====
        lab3_frame = ttk.LabelFrame(control_frame, text="Лаб. 3: Сплайны (Улучшенные)", padding=5)
        lab3_frame.pack(fill=tk.X, pady=(0, 5))

        # Основные операции со сплайнами
        ttk.Button(lab3_frame, text="Начать новый сплайн",
                   command=self.start_spline).pack(fill=tk.X, pady=2)

        ttk.Button(lab3_frame, text="Добавить точку к сплайну",
                   command=self.enable_point_adding).pack(fill=tk.X, pady=2)

        ttk.Button(lab3_frame, text="Завершить сплайн",
                   command=self.finish_spline).pack(fill=tk.X, pady=2)

        # Управление точками текущего сплайна
        points_frame = ttk.Frame(lab3_frame)
        points_frame.pack(fill=tk.X, pady=5)

        ttk.Button(points_frame, text="Удалить последнюю точку",
                   command=self.remove_last_spline_point).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        ttk.Button(points_frame, text="Очистить сплайн",
                   command=self.clear_current_spline).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Настройки отображения
        display_frame = ttk.Frame(lab3_frame)
        display_frame.pack(fill=tk.X, pady=5)

        ttk.Button(display_frame, text="Вкл/Выкл контрольные линии",
                   command=self.toggle_control_lines).pack(fill=tk.X, pady=2)

        ttk.Button(display_frame, text="Вкл/Выкл точки",
                   command=self.toggle_points).pack(fill=tk.X, pady=2)

        # Управление всеми сплайнами
        splines_frame = ttk.Frame(lab3_frame)
        splines_frame.pack(fill=tk.X, pady=5)

        ttk.Button(splines_frame, text="Удалить последний сплайн",
                   command=self.remove_last_spline).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        ttk.Button(splines_frame, text="Очистить все сплайны",
                   command=self.clear_all_splines).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Информация о сплайнах
        info_frame = ttk.Frame(lab3_frame)
        info_frame.pack(fill=tk.X, pady=5)

        self.spline_info_var = tk.StringVar(value="Сплайны: 0, Точки: 0")
        ttk.Label(info_frame, textvariable=self.spline_info_var,
                  font=("Arial", 9), background="#f0f0f0").pack(fill=tk.X)

        # ===== LAB 4 Controls =====
        lab4_frame = ttk.LabelFrame(control_frame, text="Лаб. 4: Растры", padding=5)
        lab4_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab4_frame, text="Показать растровый шаблон",
                   command=self.show_bitmap_pattern).pack(fill=tk.X, pady=2)

        # ===== LAB 5 Controls =====
        lab5_frame = ttk.LabelFrame(control_frame, text="Лаб. 5: BMP + Масштабирование", padding=5)
        lab5_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab5_frame, text="Создать тестовое изображение",
                   command=self.create_test_bmp_image).pack(fill=tk.X, pady=2)

        # Масштабирование
        scale_frame = ttk.Frame(lab5_frame)
        scale_frame.pack(fill=tk.X, pady=5)

        ttk.Label(scale_frame, text="Коэффициент:").pack(side=tk.LEFT)
        self.scale_var = tk.StringVar(value="2.0")
        scale_combo = ttk.Combobox(scale_frame, textvariable=self.scale_var,
                                   values=["0.25", "0.5", "2.0", "4.0"], width=8)
        scale_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(lab5_frame, text="Применить масштабирование",
                   command=self.apply_scaling).pack(fill=tk.X, pady=2)

        # Общие кнопки
        common_frame = ttk.LabelFrame(control_frame, text="Общие", padding=5)
        common_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(common_frame, text="Удалить все объекты",
                   command=self.clear_all).pack(fill=tk.X, pady=2)

        ttk.Button(common_frame, text="Обновить отображение",
                   command=self.redraw_canvas).pack(fill=tk.X, pady=2)

        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)

        # Status bar
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(control_frame, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    def create_test_bitmap(self):
        """Создание тестового растрового ресурса"""
        bitmap = BitmapResource(32, 32)
        bitmap.create_double_triangle_pattern()
        self.bitmap_resources.append(bitmap)

    # ===== LAB 2 Methods =====
    def create_double_triangle(self):
        """Создание двойного треугольника (вариант 16)"""
        shape = ShapeFactory.create_double_triangle(300, 200, 80)
        self.polygons.append(shape)
        self.current_polygon = shape
        self.redraw_canvas()
        self.status_var.set("Создан двойной треугольник")

    def apply_transformations(self):
        """Применение преобразований к текущему полигону"""
        if not self.current_polygon:
            messagebox.showwarning("Предупреждение", "Сначала создайте фигуру")
            return

        try:
            dx = float(self.dx_var.get())
            dy = float(self.dy_var.get())
            angle = float(self.angle_var.get())

            self.current_polygon.transform(dx, dy, angle)
            self.redraw_canvas()
            self.status_var.set(f"Применен перенос ({dx},{dy}) и поворот на {angle}°")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числовые значения")

    # ===== LAB 3 Methods (УЛУЧШЕННЫЕ) =====
    def start_spline(self):
        """Начало создания нового сплайна"""
        self.spline_manager.start_new_spline()
        self.is_adding_points = True
        self.update_spline_info()
        self.status_var.set("Режим создания сплайна - кликайте по canvas для добавления точек")

    def enable_point_adding(self):
        """Включить режим добавления точек к текущему сплайну"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            self.is_adding_points = True
            self.status_var.set("Режим добавления точек - кликайте по canvas")
        else:
            messagebox.showwarning("Предупреждение", "Сначала начните создание сплайна")

    def finish_spline(self):
        """Завершение создания текущего сплайна"""
        finished_spline = self.spline_manager.finish_current_spline()
        if finished_spline:
            self.is_adding_points = False
            self.redraw_canvas()
            point_count = finished_spline.get_point_count()
            self.update_spline_info()
            self.status_var.set(f"Сплайн завершен с {point_count} контрольными точками")
        else:
            messagebox.showwarning("Предупреждение", "Нужно как минимум 2 контрольные точки для сплайна")

    def remove_last_spline_point(self):
        """Удалить последнюю контрольную точку текущего сплайна"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            removed_point = current_spline.remove_last_control_point()
            if removed_point:
                self.redraw_canvas()
                point_count = current_spline.get_point_count()
                self.update_spline_info()
                self.status_var.set(f"Удалена точка. Осталось: {point_count}")
            else:
                self.status_var.set("Нет точек для удаления")
        else:
            messagebox.showwarning("Предупреждение", "Нет активного сплайна")

    def clear_current_spline(self):
        """Очистить текущий сплайн"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.clear_control_points()
            self.redraw_canvas()
            self.update_spline_info()
            self.status_var.set("Текущий сплайн очищен")

    def toggle_control_lines(self):
        """Переключить отображение контрольных линий"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.toggle_control_lines()
            self.redraw_canvas()
            state = "включены" if current_spline.show_control_lines else "выключены"
            self.status_var.set(f"Контрольные линии {state}")

    def toggle_points(self):
        """Переключить отображение контрольных точек"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.toggle_points()
            self.redraw_canvas()
            state = "включены" if current_spline.show_points else "выключены"
            self.status_var.set(f"Контрольные точки {state}")

    def remove_last_spline(self):
        """Удалить последний завершенный сплайн"""
        removed_spline = self.spline_manager.remove_last_spline()
        if removed_spline:
            self.redraw_canvas()
            self.update_spline_info()
            self.status_var.set("Удален последний сплайн")
        else:
            messagebox.showwarning("Предупреждение", "Нет завершенных сплайнов")

    def clear_all_splines(self):
        """Очистить все сплайны"""
        self.spline_manager.clear_all_splines()
        self.is_adding_points = False
        self.redraw_canvas()
        self.update_spline_info()
        self.status_var.set("Все сплайны удалены")

    def update_spline_info(self):
        """Обновить информацию о сплайнах"""
        spline_count = self.spline_manager.get_spline_count()
        total_points = self.spline_manager.get_total_point_count()
        current_spline = self.spline_manager.get_current_spline()

        if current_spline:
            current_points = current_spline.get_point_count()
            info_text = f"Сплайны: {spline_count}, Точки: {total_points} (текущий: {current_points})"
        else:
            info_text = f"Сплайны: {spline_count}, Точки: {total_points}"

        self.spline_info_var.set(info_text)

    # ===== LAB 4 Methods =====
    def show_bitmap_pattern(self):
        """Показать растровый шаблон"""
        if not self.bitmap_resources:
            return

        # Очищаем предыдущие изображения
        for widget in self.bitmap_frame.winfo_children():
            widget.destroy()

        # Показываем растровый шаблон
        bitmap = self.bitmap_resources[0]
        photo = bitmap.get_photo_image()

        ttk.Label(self.bitmap_frame, text="Растровый шаблон двойного треугольника:").pack(anchor="w")
        label = ttk.Label(self.bitmap_frame, image=photo)
        label.image = photo  # Keep reference
        label.pack(pady=5)

        self.status_var.set("Показан растровый шаблон")

    # ===== LAB 5 Methods =====
    def create_test_bmp_image(self):
        """Создание тестового BMP изображения"""
        self.bmp_loader.create_test_image()
        self.display_bmp_comparison()
        self.status_var.set("Тестовое изображение создано")

    def apply_scaling(self):
        """Применение масштабирования с сравнением"""
        if not self.bmp_loader.image_data:
            # Если нет загруженного изображения, создаем тестовое
            self.bmp_loader.create_test_image()

        self.display_bmp_comparison()
        self.status_var.set(f"Применено масштабирование, коэффициент: {self.scale_var.get()}")

    def display_bmp_comparison(self):
        """Показать сравнение методов масштабирования"""
        # Очищаем предыдущие изображения
        for widget in self.bitmap_frame.winfo_children():
            widget.destroy()

        if not self.bmp_loader.image_data:
            return

        try:
            scale_factor = float(self.scale_var.get())

            # Создаем основной фрейм для сравнения
            comparison_frame = ttk.Frame(self.bitmap_frame)
            comparison_frame.pack(fill=tk.BOTH, expand=True)

            # Заголовок
            ttk.Label(comparison_frame,
                      text=f"Масштабирование (коэффициент: {scale_factor})",
                      font=('Arial', 10, 'bold')).pack(pady=5)

            # Получаем масштабированные версии
            nearest_data, nw, nh = self.bmp_loader.scale_image(scale_factor, "nearest")

            # Отображаем изображения
            display_size = 300  # Размер для отображения

            orig_photo = self.bmp_loader.get_photo_image(width=display_size, height=display_size)
            scaled_photo = self.bmp_loader.get_photo_image(nearest_data, width=display_size, height=display_size)

            images_frame = ttk.Frame(comparison_frame)
            images_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            # Оригинал
            orig_frame = ttk.LabelFrame(images_frame,
                                        text=f"Оригинал ({self.bmp_loader.width}x{self.bmp_loader.height})")
            orig_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)
            ttk.Label(orig_frame, image=orig_photo).pack(padx=10, pady=10)

            # Масштабированное
            scaled_frame = ttk.LabelFrame(images_frame,
                                          text=f"Масштабированное ({nw}x{nh})")
            scaled_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True)
            ttk.Label(scaled_frame, image=scaled_photo).pack(padx=10, pady=10)

            # Сохраняем ссылки на изображения
            orig_frame.image = orig_photo
            scaled_frame.image = scaled_photo

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный коэффициент масштабирования")

    # ===== Common Methods =====
    def on_canvas_click(self, event):
        """Обработка клика по canvas"""
        current_spline = self.spline_manager.get_current_spline()
        if current_spline and self.is_adding_points:
            # Добавляем контрольную точку для сплайна
            point = Point(event.x, event.y)
            current_spline.add_control_point(point)
            point_count = current_spline.get_point_count()
            self.redraw_canvas()
            self.update_spline_info()
            self.status_var.set(f"Добавлена точка {point_count}. Кликайте дальше или завершите сплайн")

    def on_canvas_motion(self, event):
        """Обработка движения мыши по canvas"""
        # Можно добавить предпросмотр следующей точки
        pass

    def redraw_canvas(self):
        """Перерисовка canvas"""
        self.canvas.delete("all")

        # Рисуем все полигоны
        for polygon in self.polygons:
            polygon.draw(self.canvas)

        # Рисуем все завершенные сплайны
        for spline in self.spline_manager.splines:
            spline.draw(self.canvas)

        # Рисуем текущий сплайн (если есть)
        current_spline = self.spline_manager.get_current_spline()
        if current_spline:
            current_spline.draw(self.canvas)

    def clear_all(self):
        """Очистка всех объектов"""
        self.polygons.clear()
        self.spline_manager.clear_all_splines()
        self.current_polygon = None
        self.is_adding_points = False
        self.redraw_canvas()
        self.update_spline_info()

        # Очищаем панель bitmap
        for widget in self.bitmap_frame.winfo_children():
            widget.destroy()

        self.status_var.set("Все объекты удалены")


# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PainterApp(root)
    root.mainloop()
