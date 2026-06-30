import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import random
import json
import os
from PIL import Image, ImageTk

FONT_FILE = "custom_font.json"
FRAME_FILE = "custom_frame.json"

LANGUAGES = {
    "RU": {
        "title": "Дизайнер Суффиксов Minecraft",
        "font_title": " 1. Шрифт 5x5 ",
        "clear_btn": "Очистить букву",
        "frame_title": " 2. Конструктор рамки (7x15) ",
        "brush_lbl": "Кисть:",
        "preview_title": " 3. Настройки и Просмотр ",
        "text_lbl": "Текст:",
        "btn_base": "Цвет рамки",
        "btn_text": "Цвет букв",
        "btn_shadow": "Тень текста",
        "chk_noise": "Шум",
        "btn_save": "💾 Скачать .PNG",
        "success": "Успех",
        "saved": "Суффикс успешно сохранен!"
    },
    "EN": {
        "title": "Minecraft Suffix Designer Pro",
        "font_title": " 1. Font 5x5 ",
        "clear_btn": "Clear Letter",
        "frame_title": " 2. Frame Builder (7x15) ",
        "brush_lbl": "Brush:",
        "preview_title": " 3. Settings & Preview ",
        "text_lbl": "Text:",
        "btn_base": "Frame Color",
        "btn_text": "Text Color",
        "btn_shadow": "Text Shadow",
        "chk_noise": "Noise",
        "btn_save": "💾 Download .PNG",
        "success": "Success",
        "saved": "Suffix successfully saved!"
    }
}
class PixelFontApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#1e1e24")

        self.lang_var = tk.StringVar(value="RU")
        self.chars = list("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
        self.current_char = "А"

        self.frame_h = 7
        self.frame_w = 15

        self.fonts = self._load_fonts()
        self.frame_matrix = self._load_frame_matrix()

        self.selected_shadow_value = 255
        self.draw_mode = None 

        self.preview_text = "МЕТЕОР"
        self.base_color = (130, 20, 210)       
        self.text_color = (255, 255, 255)       
        self.shadow_color = (60, 60, 60, 150)   
        self.use_noise = tk.BooleanVar(value=True)

        self.zoom_scale = 16.0
        self.pan_x = 40
        self.pan_y = 80
        self.drag_start_x = 0
        self.drag_start_y = 0

        self._setup_ui()
        self._update_ui_text()
        self.update_editor_grid()
        self.update_frame_grid()
        self.refresh_preview()

    def _load_fonts(self):
        if os.path.exists(FONT_FILE):
            try:
                with open(FONT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {char: [[0 for _ in range(5)] for _ in range(5)] for char in self.chars}

    def _load_frame_matrix(self):
        if os.path.exists(FRAME_FILE):
            try:
                with open(FRAME_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        
        matrix = [[1 for _ in range(self.frame_w)] for _ in range(self.frame_h)]
        for y in range(self.frame_h):
            for x in range(self.frame_w):
                if y in [0, self.frame_h-1] and x in [0, 1, self.frame_w-1, self.frame_w-2]: 
                    matrix[y][x] = 0
                elif y in [1, self.frame_h-2] and x in [0, self.frame_w-1]: 
                    matrix[y][x] = 0
                
                if matrix[y][x] != 0:
                    if y == self.frame_h-1 or x == self.frame_w-1: 
                        matrix[y][x] = 255
        return matrix

    def _save_data(self):
        try:
            with open(FONT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.fonts, f, ensure_ascii=False, indent=4)
            with open(FRAME_FILE, "w", encoding="utf-8") as f:
                json.dump(self.frame_matrix, f, ensure_ascii=False, indent=4)
        except: pass
    def _setup_ui(self):
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left_panel = tk.Frame(self.root, bg="#1e1e24", padx=15, pady=15)
        left_panel.grid(row=0, column=0, sticky="nsew")
        left_panel.rowconfigure(1, weight=1)

        self.font_frame = tk.LabelFrame(left_panel, text="", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2a2a35", bd=0, padx=10, pady=10)
        self.font_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))


        self.char_menu = tk.StringVar(value=self.current_char)
        dropdown = tk.OptionMenu(self.font_frame, self.char_menu, *self.chars, command=self._on_char_change)
        dropdown.config(bg="#3a3a4a", fg="#ffffff", activebackground="#4a4a5a", activeforeground="#ffffff", bd=0, highlightthickness=0, font=("Segoe UI", 10))
        dropdown["menu"].config(bg="#3a3a4a", fg="#ffffff", font=("Segoe UI", 10))
        dropdown.pack(fill="x", pady=(0, 10))

        self.font_grid = tk.Frame(self.font_frame, bg="#2a2a35")
        self.font_grid.pack(pady=5)
        self.font_buttons = [[None for _ in range(5)] for _ in range(5)]
        for r in range(5):
            for c in range(5):
                btn = tk.Label(self.font_grid, width=3, height=1, bg="#ffffff", bd=1, relief="flat", highlightbackground="#1e1e24", highlightthickness=1)
                btn.grid(row=r, column=c, padx=2, pady=2)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self._start_font_drag(r, c, 1))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self._start_font_drag(r, c, 0))
                btn.bind("<B1-Motion>", self._on_font_drag_move)
                btn.bind("<B3-Motion>", self._on_font_drag_move)
                self.font_buttons[r][c] = btn

        self.btn_clear = tk.Button(self.font_frame, text="", font=("Segoe UI", 9, "bold"), bg="#e67e22", fg="#ffffff", activebackground="#d35400", activeforeground="#ffffff", relief="flat", bd=0, padx=5, pady=5, command=self._clear_char)
        self.btn_clear.pack(fill="x", pady=(10, 0))

        self.frame_editor = tk.LabelFrame(left_panel, text="", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2a2a35", bd=0, padx=10, pady=10)
        self.frame_editor.grid(row=1, column=0, sticky="nsew")

        brush_frame = tk.Frame(self.frame_editor, bg="#2a2a35")
        brush_frame.pack(fill="x", pady=(0, 10))
        self.brush_lbl = tk.Label(brush_frame, text="", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2a2a35")
        self.brush_lbl.pack(side="left", padx=(0, 5))
        
        self.brush_var = tk.IntVar(value=255)
        brushes = [("100%", 255), ("75%", 190), ("50%", 125), ("25%", 60)]
        for text, val in brushes:
            rb = tk.Radiobutton(brush_frame, text=text, variable=self.brush_var, value=val, font=("Segoe UI", 9), fg="#ffffff", bg="#2a2a35", activebackground="#2a2a35", activeforeground="#ffffff", selectcolor="#3a3a4a", command=self._update_brush)
            rb.pack(side="left", padx=2)

        self.edge_grid = tk.Frame(self.frame_editor, bg="#2a2a35")
        self.edge_grid.pack(pady=5)
        self.frame_buttons = [[None for _ in range(self.frame_w)] for _ in range(self.frame_h)]
        for r in range(self.frame_h):
            for c in range(self.frame_w):
                btn = tk.Label(self.edge_grid, width=1, height=1, bg="#ffffff", bd=1, relief="flat", highlightbackground="#1e1e24", highlightthickness=1)
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, r=r, c=c: self._start_frame_drag(r, c, 1))
                btn.bind("<Control-Button-1>", lambda e, r=r, c=c: self._start_frame_drag(r, c, 2))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self._start_frame_drag(r, c, 0))
                btn.bind("<Control-Button-3>", lambda e, r=r, c=c: self._start_frame_drag(r, c, 3))
                btn.bind("<B1-Motion>", self._on_frame_drag_move)
                btn.bind("<B3-Motion>", self._on_frame_drag_move)
                self.frame_buttons[r][c] = btn

        right_panel = tk.Frame(self.root, bg="#1e1e24", padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)

        self.right_frame = tk.LabelFrame(right_panel, text="", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#2a2a35", bd=0, padx=15, pady=10)
        self.right_frame.grid(row=0, column=0, sticky="nsew")
        self.right_frame.rowconfigure(1, weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        control_panel = tk.Frame(self.right_frame, bg="#2a2a35")
        control_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.text_lbl = tk.Label(control_panel, text="", font=("Segoe UI", 10), fg="#ffffff", bg="#2a2a35")
        self.text_lbl.pack(side="left", padx=(0, 5))
        self.text_entry = tk.Entry(control_panel, width=10, font=("Segoe UI", 11), bg="#3a3a4a", fg="#ffffff", bd=0, insertbackground="#ffffff")
        self.text_entry.insert(0, self.preview_text)
        self.text_entry.pack(side="left", padx=(0, 10), ipady=3)
        self.text_entry.bind("<KeyRelease>", self._on_text_changed)

        btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#ffffff", "relief": "flat", "bd": 0, "padx": 5, "pady": 5}
        self.btn_base = tk.Button(control_panel, text="", bg="#9b59b6", activebackground="#8e44ad", activeforeground="#ffffff", **btn_style, command=lambda: self._choose_color('base'))
        self.btn_base.pack(side="left", padx=2)
        self.btn_text = tk.Button(control_panel, text="", bg="#3498db", activebackground="#2980b9", activeforeground="#ffffff", **btn_style, command=lambda: self._choose_color('text'))
        self.btn_text.pack(side="left", padx=2)
        self.btn_shadow = tk.Button(control_panel, text="", bg="#7f8c8d", activebackground="#95a5a6", activeforeground="#ffffff", **btn_style, command=lambda: self._choose_color('shadow'))
        self.btn_shadow.pack(side="left", padx=2)
        
        self.chk_noise = tk.Checkbutton(control_panel, text="", variable=self.use_noise, font=("Segoe UI", 10), fg="#ffffff", bg="#2a2a35", activebackground="#2a2a35", activeforeground="#ffffff", selectcolor="#3a3a4a", command=self.refresh_preview)
        self.chk_noise.pack(side="left", padx=10)

        lang_menu = tk.OptionMenu(control_panel, self.lang_var, "RU", "EN", command=self._on_lang_change)
        lang_menu.config(bg="#e74c3c", fg="#ffffff", activebackground="#c0392b", activeforeground="#ffffff", bd=0, highlightthickness=0, font=("Segoe UI", 9, "bold"))
        lang_menu["menu"].config(bg="#3a3a4a", fg="#ffffff", font=("Segoe UI", 10))
        lang_menu.pack(side="left", padx=5)
        
        self.btn_save = tk.Button(control_panel, text="", bg="#2ecc71", fg="#ffffff", activebackground="#27ae60", activeforeground="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", bd=0, padx=5, pady=5, command=self._save_image)
        self.btn_save.pack(side="right")

        self.canvas = tk.Canvas(self.right_frame, bg="#1a1a22", bd=0, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<B1-Motion>", self._on_drag_move)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.root.bind("<Configure>", lambda e: self.refresh_preview())
    def _on_lang_change(self, val):
        self._update_ui_text()
        self.refresh_preview()

    def _update_ui_text(self):
        t = LANGUAGES[self.lang_var.get()]
        self.root.title(t["title"])
        self.font_frame.config(text=t["font_title"])
        self.btn_clear.config(text=t["clear_btn"])
        self.frame_editor.config(text=t["frame_title"])
        self.brush_lbl.config(text=t["brush_lbl"])
        self.right_frame.config(text=t["preview_title"])
        self.text_lbl.config(text=t["text_lbl"])
        self.btn_base.config(text=t["btn_base"])
        self.btn_text.config(text=t["btn_text"])
        self.btn_shadow.config(text=t["btn_shadow"])
        self.chk_noise.config(text=t["chk_noise"])
        self.btn_save.config(text=t["btn_save"])

    def _update_brush(self):
        self.selected_shadow_value = self.brush_var.get()

    def _on_char_change(self, selected_char):
        self.current_char = selected_char
        self.update_editor_grid()

    def _start_font_drag(self, r, c, val):
        self.draw_mode = val
        self._set_font_pixel(r, c, val)

    def _on_font_drag_move(self, event):
        if self.draw_mode is None: return
        widget = self.font_grid.winfo_containing(event.x_root, event.y_root)
        if widget and widget in [btn for row in self.font_buttons for btn in row]:
            info = widget.grid_info()
            self._set_font_pixel(int(info['row']), int(info['column']), self.draw_mode)

    def _set_font_pixel(self, r, c, val):
        if self.fonts[self.current_char][r][c] != val:
            self.fonts[self.current_char][r][c] = val
            self.font_buttons[r][c].config(bg="#111111" if val == 1 else "#ffffff")
            self._save_data()
            self.refresh_preview()

    def _clear_char(self):
        self.fonts[self.current_char] = [[0 for _ in range(5)] for _ in range(5)]
        self.update_editor_grid()
        self._save_data()
        self.refresh_preview()

    def _start_frame_drag(self, r, c, val):
        self.draw_mode = val
        self._set_frame_pixel(r, c, val)

    def _on_frame_drag_move(self, event):
        if self.draw_mode is None: return
        widget = self.edge_grid.winfo_containing(event.x_root, event.y_root)
        if widget and widget in [btn for row in self.frame_buttons for btn in row]:
            info = widget.grid_info()
            self._set_frame_pixel(int(info['row']), int(info['column']), self.draw_mode)

    def _set_frame_pixel(self, r, c, mode):
        updated = False
        if mode == 1 and self.frame_matrix[r][c] != 1:
            self.frame_matrix[r][c] = 1
            updated = True
        elif mode == 0 and self.frame_matrix[r][c] != 0:
            self.frame_matrix[r][c] = 0
            updated = True
        elif mode == 2 and self.frame_matrix[r][c] != self.selected_shadow_value:
            self.frame_matrix[r][c] = self.selected_shadow_value
            updated = True
        elif mode == 3:
            if self.frame_matrix[r][c] >= 2:
                self.frame_matrix[r][c] = 1
                updated = True
        
        if updated:
            self.update_frame_grid()
            self._save_data()
            self.refresh_preview()

    def update_editor_grid(self):
        matrix = self.fonts[self.current_char]
        for r in range(5):
            for c in range(5):
                self.font_buttons[r][c].config(bg="#111111" if matrix[r][c] == 1 else "#ffffff")

    def update_frame_grid(self):
        for r in range(self.frame_h):
            for c in range(self.frame_w):
                val = self.frame_matrix[r][c]
                if val == 0:
                    self.frame_buttons[r][c].config(bg="#4a4a5a")
                elif val == 1:
                    self.frame_buttons[r][c].config(bg="#8214D2")
                elif val >= 2:
                    if val > 200: hex_color = "#111111"
                    elif val > 150: hex_color = "#333333"
                    elif val > 100: hex_color = "#555555"
                    else: hex_color = "#777777"
                    self.frame_buttons[r][c].config(bg=hex_color)

    def _on_text_changed(self, event):
        self.preview_text = self.text_entry.get().upper()
        self.refresh_preview()

    def _choose_color(self, target):
        color_code = colorchooser.askcolor(title="Color")
        if color_code and color_code[0]:
            rgb = tuple(map(int, color_code[0]))
            if target == 'base': self.base_color = rgb
            elif target == 'text': self.text_color = rgb
            elif target == 'shadow': self.shadow_color = (rgb[0], rgb[1], rgb[2], 160)
            self.refresh_preview()
    def build_suffix_pillow(self):
        text = self.preview_text if self.preview_text else " "
        letter_w, letter_h = 5, 5
        spacing = 1
        
        text_width = len(text) * letter_w + (len(text) - 1) * spacing
        padding_x, padding_y = 5, 1
        img_w = text_width + (padding_x * 2)
        img_h = self.frame_h
        
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        pixels = img.load()
        
        random.seed(42)

        for y in range(img_h):
            for x in range(img_w):
                if x < 7:
                    orig_val = self.frame_matrix[y][x]
                elif x >= img_w - 8:
                    orig_val = self.frame_matrix[y][self.frame_w - (img_w - x)]
                else:
                    orig_val = self.frame_matrix[y][7] 

                if orig_val == 0:
                    continue

                base_r, base_g, base_b = self.base_color

                if self.use_noise.get():
                    noise = random.randint(-18, 18)
                    r = max(0, min(255, base_r + noise))
                    g = max(0, min(255, base_g + noise))
                    b = max(0, min(255, base_b + noise))
                else:
                    r, g, b = base_r, base_g, base_b

                pixels[x, y] = (r, g, b, 255)

                if orig_val >= 2:
                    bg_r, bg_g, bg_b, _ = pixels[x, y]
                    ratio = orig_val / 255.0
                    out_r = int(bg_r * (1 - ratio))
                    out_g = int(bg_g * (1 - ratio))
                    out_b = int(bg_b * (1 - ratio))
                    pixels[x, y] = (out_r, out_g, out_b, 255)

        current_x = padding_x
        for char in text:
            bitmap = self.fonts.get(char, [[0 for _ in range(5)] for _ in range(5)])
            for row in range(letter_h):
                for col in range(letter_w):
                    if bitmap[row][col] == 1:
                        tx = current_x + col + 1
                        ty = padding_y + row
                        if 0 <= tx < img_w and pixels[tx, ty] != (0,0,0,0):
                            bg_r, bg_g, bg_b, _ = pixels[tx, ty]
                            sh_r, sh_g, sh_b, sh_a = self.shadow_color
                            ratio = sh_a / 255.0
                            out_r = int(bg_r * (1 - ratio) + sh_r * ratio)
                            out_g = int(bg_g * (1 - ratio) + sh_g * ratio)
                            out_b = int(bg_b * (1 - ratio) + sh_b * ratio)
                            pixels[tx, ty] = (out_r, out_g, out_b, 255)
            current_x += letter_w + spacing

        current_x = padding_x
        txt_r, txt_g, txt_b = self.text_color
        for char in text:
            bitmap = self.fonts.get(char, [[0 for _ in range(5)] for _ in range(5)])
            for row in range(letter_h):
                for col in range(letter_w):
                    if bitmap[row][col] == 1:
                        tx = current_x + col
                        ty = padding_y + row
                        if 0 <= tx < img_w:
                            pixels[tx, ty] = (txt_r, txt_g, txt_b, 255)
            current_x += letter_w + spacing

        return img
    def _on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag_move(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.pan_x += dx
        self.pan_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.refresh_preview()

    def _on_zoom(self, event):
        if event.delta > 0: self.zoom_scale = min(64.0, self.zoom_scale + 2.0)
        else: self.zoom_scale = max(4.0, self.zoom_scale - 2.0)
        self.refresh_preview()

    def refresh_preview(self):
        self.current_img = self.build_suffix_pillow()
        w = int(self.current_img.width * self.zoom_scale)
        h = int(self.current_img.height * self.zoom_scale)
        if w < 1 or h < 1: return

        resized = self.current_img.resize((w, h), Image.NEAREST)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(self.pan_x, self.pan_y, anchor="nw", image=self.tk_image)

    def _save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path:
            self.build_suffix_pillow().save(file_path)
            t = LANGUAGES[self.lang_var.get()]
            messagebox.showinfo(t["success"], t["saved"])

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelFontApp(root)
    root.mainloop()
