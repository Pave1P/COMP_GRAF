import tkinter as tk
from tkinter import ttk

# === Базовый класс фигуры ===
class BaseShape:
    def __init__(self, x=0, y=0, color="red"):
        self.x = x
        self.y = y
        self.color = color

    def show(self, canvas):
        raise NotImplementedError

    def get_region(self):
        raise NotImplementedError


# === Фигура 17: квадратная рамка + внутренняя окружность (контуры, без заливки) ===
class Shape17(BaseShape):
    def __init__(self, x, y, size=120, border_width=6, color="red"):
        super().__init__(x, y, color)
        self.size = size                # внешняя сторона квадрата
        self.border_width = border_width

    def show(self, canvas):
        # Центр (self.x, self.y)
        half = self.size / 2.0
        # координаты внешнего квадрата
        x0 = self.x - half
        y0 = self.y - half
        x1 = self.x + half
        y1 = self.y + half

        # Нарисуем квадрат (только контур). Тkinter draw rectangle uses outline и width.
        canvas.create_rectangle(
            x0, y0, x1, y1,
            outline=self.color, width=self.border_width
        )

        # Внутренняя окружность. Пусть диаметр будет чуть меньше квадрата, чтобы было видно отступ.
        # Можно сделать диаметр = size * 0.72 (поигрался по виду с рисунком).
        circ_diam = self.size * 0.72
        r = circ_diam / 2.0
        cx0 = self.x - r
        cy0 = self.y - r
        cx1 = self.x + r
        cy1 = self.y + r

        canvas.create_oval(
            cx0, cy0, cx1, cy1,
            outline=self.color, width=self.border_width
        )

    def get_region(self):
        half = self.size / 2.0
        return (self.x - half, self.y - half, self.x + half, self.y + half)


# === Простое приложение Painter с выбором параметров ===
class PainterApp:
    def __init__(self, root):
        self.root = root
        root.title("Painter — лабораторная №1 — фигура 17 (Квадрат + Окружность)")

        self.canvas = tk.Canvas(root, width=600, height=420, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Параметры
        self.size_var = tk.IntVar(value=140)
        self.width_var = tk.IntVar(value=6)
        self.color_var = tk.StringVar(value="red")

        ttk.Label(root, text="Размер (px):").grid(row=1, column=0, sticky="w", padx=6)
        self.size_scale = ttk.Scale(root, from_=40, to=360, variable=self.size_var, orient=tk.HORIZONTAL)
        self.size_scale.grid(row=1, column=1, sticky="we", padx=6)

        ttk.Label(root, text="Толщина линий:").grid(row=2, column=0, sticky="w", padx=6)
        self.width_scale = ttk.Scale(root, from_=1, to=20, variable=self.width_var, orient=tk.HORIZONTAL)
        self.width_scale.grid(row=2, column=1, sticky="we", padx=6)

        ttk.Label(root, text="Цвет:").grid(row=1, column=2, sticky="w", padx=6)
        self.color_entry = ttk.Combobox(root, textvariable=self.color_var, values=["red","blue","green","black","orange"])
        self.color_entry.grid(row=1, column=3, sticky="we", padx=6)

        btn_frame = ttk.Frame(root)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=8)

        self.draw_btn = ttk.Button(btn_frame, text="Нарисовать фигуру 17", command=self.draw_shape)
        self.draw_btn.pack(side="left", padx=6)

        self.clear_btn = ttk.Button(btn_frame, text="Очистить", command=self.clear_canvas)
        self.clear_btn.pack(side="left", padx=6)

        # Рисуем по клику мыши в позиции клика
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        ttk.Label(root, text="Клик на холст — нарисовать в позиции клика").grid(row=4, column=0, columnspan=4, pady=(0,8))

        # Отрисуем пример в центре
        self.draw_shape()

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_shape(self):
        self.clear_canvas()
        cx = self.canvas.winfo_width() // 2
        cy = self.canvas.winfo_height() // 2
        shape = Shape17(cx, cy, size=self.size_var.get(), border_width=self.width_var.get(), color=self.color_var.get())
        shape.show(self.canvas)

    def on_canvas_click(self, event):
        # рисуем в точке клика текущую фигуру
        shape = Shape17(event.x, event.y, size=self.size_var.get(), border_width=self.width_var.get(), color=self.color_var.get())
        shape.show(self.canvas)


if __name__ == "__main__":
    root = tk.Tk()
    # Сделаем grid колонки растягиваемыми
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)
    app = PainterApp(root)
    root.mainloop()
