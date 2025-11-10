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

    @staticmethod
    def create_complex_shape(center_x, center_y, size=50):
        """Альтернативное название для создания двойного треугольника"""
        return ShapeFactory.create_double_triangle(center_x, center_y, size)


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №3 - Сплайновые кривые
# =============================================================================

class SplineCurve:
    def __init__(self, control_points=None, color="red", segments=20):
        self.control_points = control_points if control_points else []
        self.color = color
        self.segments = segments

    def add_control_point(self, point):
        self.control_points.append(point)

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

    def draw(self, canvas):
        """Рисование сплайновой кривой"""
        if len(self.control_points) < 2:
            return

        # Для кубических кривых Безье нужны группы по 4 точки
        curve_points = []

        # Разбиваем контрольные точки на сегменты по 4 точки
        for i in range(0, len(self.control_points) - 1, 3):
            if i + 3 < len(self.control_points):
                segment_points = self.control_points[i:i + 4]

                # Генерируем точки кривой для этого сегмента
                for j in range(self.segments + 1):
                    t = j / self.segments
                    point = self.bezier_point(t, segment_points)
                    curve_points.append((point.x, point.y))

        # Рисуем кривую
        if len(curve_points) > 1:
            canvas.create_line(curve_points, fill=self.color, width=2, smooth=True)

        # Рисуем контрольные точки
        for point in self.control_points:
            canvas.create_oval(point.x - 3, point.y - 3, point.x + 3, point.y + 3,
                               fill="green", outline="green")


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

        # Заполняем фон
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = (240, 240, 240)  # Светло-серый фон

        # Создаем PIL изображение для рисования
        pil_image = Image.new('RGB', (self.width, self.height), (240, 240, 240))
        draw = ImageDraw.Draw(pil_image)

        # Координаты для двойного треугольника
        # Первый треугольник
        triangle1 = [
            (center_x + size, center_y),  # Правая
            (center_x, center_y - size),  # Верхняя
            (center_x - size // 2, center_y)  # Левая
        ]

        # Второй треугольник
        triangle2 = [
            (center_x - size, center_y),  # Левая
            (center_x, center_y + size),  # Нижняя
            (center_x + size // 2, center_y)  # Правая
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


class PatternBrush:
    def __init__(self, bitmap_resource):
        self.bitmap = bitmap_resource
        self.pattern_image = self.create_pattern_image()

    def create_pattern_image(self):
        """Создать изображение паттерна для кисти"""
        width, height = self.bitmap.width, self.bitmap.height
        pil_image = Image.new('RGB', (width * 4, height * 4), (255, 255, 255))

        # Заполняем паттерном
        for tile_y in range(4):
            for tile_x in range(4):
                for y in range(height):
                    for x in range(width):
                        pixel = self.bitmap.pixels[y % height][x % width]
                        pil_image.putpixel((tile_x * width + x, tile_y * height + y), pixel)

        return ImageTk.PhotoImage(pil_image)

    def fill_shape(self, canvas, polygon):
        """Заполнить фигуру паттернной кистью"""
        if not polygon.points:
            return

        # Получаем координаты полигона
        coords = []
        for point in polygon.points:
            coords.extend([point.x, point.y])

        # Создаем временное изображение для маски
        bounds = polygon.get_bounds()
        width = int(bounds[2] - bounds[0]) + 10
        height = int(bounds[3] - bounds[1]) + 10

        if width <= 0 or height <= 0:
            return

        # Создаем изображение с паттерном
        pattern_pil = Image.new('RGB', (width, height), (255, 255, 255))
        pattern_draw = ImageDraw.Draw(pattern_pil)

        # Смещаем координаты для отрисовки
        shifted_coords = [(x - bounds[0] + 5, y - bounds[1] + 5) for x, y in zip(coords[::2], coords[1::2])]

        # Заполняем паттерном
        pattern_draw.polygon(shifted_coords, fill=(100, 100, 100))

        # Накладываем текстуру
        pattern_width = self.bitmap.width * 4
        pattern_height = self.bitmap.height * 4

        for y in range(height):
            for x in range(width):
                if pattern_pil.getpixel((x, y)) != (255, 255, 255):
                    # Используем цвета из исходного bitmap
                    pattern_x = x % self.bitmap.width
                    pattern_y = y % self.bitmap.height
                    color = self.bitmap.pixels[pattern_y][pattern_x]
                    pattern_pil.putpixel((x, y), color)

        # Конвертируем в PhotoImage и отображаем
        result_image = ImageTk.PhotoImage(pattern_pil)
        canvas.create_image(bounds[0] - 5, bounds[1] - 5, image=result_image, anchor='nw')

        # Сохраняем ссылку чтобы изображение не удалилось сборщиком мусора
        canvas.pattern_fill_image = result_image


# =============================================================================
# ЛАБОРАТОРНАЯ РАБОТА №5 - Загрузка BMP и масштабирование (УЛУЧШЕННАЯ ВЕРСИЯ)
# =============================================================================

class EnhancedBMPLoader:
    def __init__(self):
        self.image_data = None
        self.width = 0
        self.height = 0
        self.bits_per_pixel = 0

    def load_bmp(self, filename):
        """Загрузка реального BMP файла"""
        try:
            with open(filename, 'rb') as f:
                # Читаем заголовок файла
                file_header = f.read(14)
                if file_header[0:2] != b'BM':
                    raise ValueError("Not a BMP file")

                # Читаем информационный заголовок
                info_header = f.read(40)
                self.width = struct.unpack('<I', info_header[4:8])[0]
                self.height = struct.unpack('<I', info_header[8:12])[0]
                self.bits_per_pixel = struct.unpack('<H', info_header[14:16])[0]

                # Пропускаем до начала данных пикселей
                data_offset = struct.unpack('<I', file_header[10:14])[0]
                f.seek(data_offset)

                # Читаем данные пикселей
                row_size = ((self.width * self.bits_per_pixel + 31) // 32) * 4
                self.image_data = []

                # BMP хранит строки в обратном порядке (снизу вверх)
                for y in range(self.height - 1, -1, -1):
                    row_data = f.read(row_size)
                    row_pixels = []

                    for x in range(self.width):
                        if self.bits_per_pixel == 24:
                            # BGR format
                            b = row_data[x * 3]
                            g = row_data[x * 3 + 1]
                            r = row_data[x * 3 + 2]
                            row_pixels.append((r, g, b))
                        elif self.bits_per_pixel == 8:
                            # Grayscale
                            intensity = row_data[x]
                            row_pixels.append((intensity, intensity, intensity))
                        else:
                            # Для простоты - серый для других форматов
                            row_pixels.append((128, 128, 128))

                    self.image_data.append(row_pixels)

                return True

        except Exception as e:
            print(f"Error loading BMP: {e}")
            return False

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

                elif mode == "linear":
                    # Билинейная интерполяция
                    x1 = int(math.floor(src_x))
                    y1 = int(math.floor(src_y))
                    x2 = min(x1 + 1, self.width - 1)
                    y2 = min(y1 + 1, self.height - 1)

                    dx = src_x - x1
                    dy = src_y - y1

                    # Интерполяция по X
                    top = self.interpolate_color(self.image_data[y1][x1], self.image_data[y1][x2], dx)
                    bottom = self.interpolate_color(self.image_data[y2][x1], self.image_data[y2][x2], dx)

                    # Интерполяция по Y
                    scaled_data[y][x] = self.interpolate_color(top, bottom, dy)

        return scaled_data, new_width, new_height

    def interpolate_color(self, color1, color2, t):
        """Интерполяция между двумя цветами"""
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        return (r, g, b)

    def get_photo_image(self, data=None, width=None, height=None):
        """Получить PhotoImage для отображения"""
        data_to_use = data if data else self.image_data
        if not data_to_use:
            return None

        h = len(data_to_use)
        w = len(data_to_use[0]) if h > 0 else 0

        # Масштабируем для отображения если нужно
        display_width = width if width else w
        display_height = height if height else h

        pil_image = Image.new('RGB', (w, h))
        for y in range(h):
            for x in range(w):
                pil_image.putpixel((x, y), data_to_use[y][x])

        # Масштабируем для отображения
        if display_width != w or display_height != h:
            pil_image = pil_image.resize((display_width, display_height), Image.NEAREST)

        return ImageTk.PhotoImage(pil_image)


# =============================================================================
# ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
# =============================================================================

class PainterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Painter - Лабораторные работы 2-5 (Вариант 16 - Двойной треугольник)")
        self.root.geometry("1200x800")

        # Данные приложения
        self.current_polygon = None
        self.polygons = []
        self.splines = []
        self.current_spline = None
        self.bitmap_resources = []
        self.bmp_loader = EnhancedBMPLoader()  # ИСПРАВЛЕНО: используем улучшенный загрузчик
        self.current_scaling_mode = "nearest"

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
        control_frame = ttk.Frame(main_frame, width=250)
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
        ttk.Button(lab2_frame, text="Удалить все",
                   command=self.clear_all).pack(fill=tk.X, pady=2)

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

        # ===== LAB 3 Controls =====
        lab3_frame = ttk.LabelFrame(control_frame, text="Лаб. 3: Сплайны", padding=5)
        lab3_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab3_frame, text="Начать сплайн",
                   command=self.start_spline).pack(fill=tk.X, pady=2)
        ttk.Button(lab3_frame, text="Закончить сплайн",
                   command=self.finish_spline).pack(fill=tk.X, pady=2)

        # ===== LAB 4 Controls =====
        lab4_frame = ttk.LabelFrame(control_frame, text="Лаб. 4: Растры", padding=5)
        lab4_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab4_frame, text="Показать растровый шаблон",
                   command=self.show_bitmap_pattern).pack(fill=tk.X, pady=2)
        ttk.Button(lab4_frame, text="Заполнить фигуру кистью",
                   command=self.fill_with_pattern_brush).pack(fill=tk.X, pady=2)

        # ===== LAB 5 Controls =====
        lab5_frame = ttk.LabelFrame(control_frame, text="Лаб. 5: BMP + Масштабирование", padding=5)
        lab5_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(lab5_frame, text="Загрузить BMP файл",
                   command=self.load_bmp_file).pack(fill=tk.X, pady=2)
        ttk.Button(lab5_frame, text="Создать тестовое изображение",
                   command=self.create_test_bmp_image).pack(fill=tk.X, pady=2)

        # Новые элементы управления для масштабирования
        scale_factor_frame = ttk.Frame(lab5_frame)
        scale_factor_frame.pack(fill=tk.X, pady=5)

        ttk.Label(scale_factor_frame, text="Коэффициент:").pack(side=tk.LEFT)
        self.scale_var = tk.StringVar(value="2.0")
        scale_combo = ttk.Combobox(scale_factor_frame, textvariable=self.scale_var,
                                   values=["0.25", "0.5", "2.0", "4.0"], width=8)
        scale_combo.pack(side=tk.LEFT, padx=5)

        scaling_frame = ttk.Frame(lab5_frame)
        scaling_frame.pack(fill=tk.X, pady=5)

        ttk.Label(scaling_frame, text="Режим масштабирования:").pack(anchor="w")
        self.scaling_mode = tk.StringVar(value="nearest")
        ttk.Radiobutton(scaling_frame, text="Ближайший сосед",
                        variable=self.scaling_mode, value="nearest").pack(anchor="w")
        ttk.Radiobutton(scaling_frame, text="Билинейная",
                        variable=self.scaling_mode, value="linear").pack(anchor="w")

        ttk.Button(lab5_frame, text="Применить масштабирование",
                   command=self.apply_scaling).pack(fill=tk.X, pady=2)

        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Status bar
        self.status_var = tk.StringVar(value="Готов")
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

    # ===== LAB 3 Methods =====
    def start_spline(self):
        """Начало создания сплайна"""
        self.current_spline = SplineCurve(color="red")
        self.status_var.set("Режим создания сплайна - кликайте по canvas")

    def finish_spline(self):
        """Завершение создания сплайна"""
        if self.current_spline and len(self.current_spline.control_points) >= 4:
            self.splines.append(self.current_spline)
            self.current_spline = None
            self.redraw_canvas()
            self.status_var.set("Сплайн завершен")
        else:
            messagebox.showwarning("Предупреждение", "Нужно как минимум 4 контрольные точки для сплайна")

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

    def fill_with_pattern_brush(self):
        """Заполнить текущую фигуру паттернной кистью"""
        if not self.current_polygon:
            messagebox.showwarning("Предупреждение", "Сначала создайте фигуру")
            return

        if not self.bitmap_resources:
            return

        bitmap = self.bitmap_resources[0]
        brush = PatternBrush(bitmap)
        brush.fill_shape(self.canvas, self.current_polygon)

        self.status_var.set("Фигура заполнена паттернной кистью")

    # ===== LAB 5 Methods (УЛУЧШЕННЫЕ) =====
    def load_bmp_file(self):
        """Загрузка реального BMP файла"""
        filename = filedialog.askopenfilename(
            title="Выберите BMP файл",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )

        if filename and self.bmp_loader.load_bmp(filename):
            self.display_bmp_comparison()
            self.status_var.set(f"BMP загружен: {self.bmp_loader.width}x{self.bmp_loader.height}")
        else:
            messagebox.showerror("Ошибка", "Не удалось загрузить BMP файл")

    def create_test_bmp_image(self):
        """Создание тестового BMP изображения"""
        self.bmp_loader.create_test_image()
        self.display_bmp_comparison()
        self.status_var.set("Тестовое изображение создано")

    def display_bmp_comparison(self):
        """Показать сравнение методов масштабирования"""
        # Очищаем предыдущие изображения
        for widget in self.bitmap_frame.winfo_children():
            widget.destroy()

        if not self.bmp_loader.image_data:
            return

        try:
            scale_factor = float(self.scale_var.get())
            mode = self.scaling_mode.get()

            # Создаем основной фрейм для сравнения
            comparison_frame = ttk.Frame(self.bitmap_frame)
            comparison_frame.pack(fill=tk.BOTH, expand=True)

            # Заголовок
            ttk.Label(comparison_frame,
                      text=f"Сравнение масштабирования (коэффициент: {scale_factor})",
                      font=('Arial', 10, 'bold')).pack(pady=5)

            # Фреймы для трех изображений
            images_frame = ttk.Frame(comparison_frame)
            images_frame.pack(fill=tk.BOTH, expand=True, pady=10)

            # Оригинал
            orig_frame = ttk.LabelFrame(images_frame,
                                        text=f"Оригинал ({self.bmp_loader.width}x{self.bmp_loader.height})")
            orig_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # Ближайший сосед
            nearest_frame = ttk.LabelFrame(images_frame,
                                           text=f"Ближайший сосед")
            nearest_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

            # Билинейная
            linear_frame = ttk.LabelFrame(images_frame,
                                          text=f"Билинейная")
            linear_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

            # Получаем масштабированные версии
            nearest_data, nw, nh = self.bmp_loader.scale_image(scale_factor, "nearest")
            linear_data, lw, lh = self.bmp_loader.scale_image(scale_factor, "linear")

            # Отображаем изображения
            display_size = 200  # Размер для отображения

            orig_photo = self.bmp_loader.get_photo_image(width=display_size, height=display_size)
            nearest_photo = self.bmp_loader.get_photo_image(nearest_data, width=display_size, height=display_size)
            linear_photo = self.bmp_loader.get_photo_image(linear_data, width=display_size, height=display_size)

            ttk.Label(orig_frame, image=orig_photo).pack(padx=10, pady=10)
            ttk.Label(nearest_frame, image=nearest_photo).pack(padx=10, pady=10)
            ttk.Label(linear_frame, image=linear_photo).pack(padx=10, pady=10)

            # Сохраняем ссылки на изображения
            orig_frame.image = orig_photo
            nearest_frame.image = nearest_photo
            linear_frame.image = linear_photo

            # Настраиваем равномерное распределение колонок
            images_frame.grid_columnconfigure(0, weight=1)
            images_frame.grid_columnconfigure(1, weight=1)
            images_frame.grid_columnconfigure(2, weight=1)

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный коэффициент масштабирования")

    def apply_scaling(self):
        """Применение масштабирования с сравнением"""
        if not self.bmp_loader.image_data:
            # Если нет загруженного изображения, создаем тестовое
            self.bmp_loader.create_test_image()

        self.display_bmp_comparison()
        self.status_var.set(f"Применено масштабирование, коэффициент: {self.scale_var.get()}")

    # ===== Common Methods =====
    def on_canvas_click(self, event):
        """Обработка клика по canvas"""
        if self.current_spline:
            # Добавляем контрольную точку для сплайна
            point = Point(event.x, event.y)
            self.current_spline.add_control_point(point)
            self.redraw_canvas()

    def redraw_canvas(self):
        """Перерисовка canvas"""
        self.canvas.delete("all")

        # Рисуем все полигоны
        for polygon in self.polygons:
            polygon.draw(self.canvas)

        # Рисуем все сплайны
        for spline in self.splines:
            spline.draw(self.canvas)

        # Рисуем текущий сплайн (если есть)
        if self.current_spline:
            self.current_spline.draw(self.canvas)

    def clear_all(self):
        """Очистка canvas"""
        self.polygons.clear()
        self.splines.clear()
        self.current_polygon = None
        self.current_spline = None
        self.redraw_canvas()
        self.status_var.set("Все объекты удалены")


# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PainterApp(root)
    root.mainloop()