#!/usr/bin/env python3
"""
stddraw.py

Tkinter tabanlı, orijinal pygame’siz stddraw API implementasyonu.
"""
import tkinter as tk
import tempfile
import time
import color
import string

# Varsayılan sabitler
_DEFAULT_PEN_RADIUS = 1.0

# Renk sabitleri (color.py içinden)
from color import (
    BLACK, BLUE, CYAN, DARK_GRAY, GRAY, GREEN, LIGHT_GRAY, MAGENTA,
    ORANGE, PINK, RED, WHITE, YELLOW, DARK_RED, DARK_GREEN,
    DARK_BLUE, VIOLET, BOOK_BLUE, BOOK_LIGHT_BLUE, BOOK_RED
)

def _hex(c):
    """color.Color → '#rrggbb' dizgesi."""
    return f"#{c.getRed():02x}{c.getGreen():02x}{c.getBlue():02x}"

# Global durum
_width, _height = 512, 512
_xmin, _xmax = 0.0, 1.0
_ymin, _ymax = 0.0, 1.0
_pen_color = BLACK
_pen_radius = _DEFAULT_PEN_RADIUS
_font_family = "Sans"
_font_size = 12
_root = None
_canvas = None
_photo_images = []      # PhotoImage referanslarını saklamak için
_key_queue = []         # tuş kuyruklama
_mouse_pressed = False
_mouse_x = mouse_y = 0

# ─── Başlatma ve Olay bağlama ────────────────────────────────────────────
def _init():
    global _root, _canvas
    if _root:
        return
    _root = tk.Tk()
    _root.title("stddraw")
    _canvas = tk.Canvas(
        _root,
        width  = _width,
        height = _height,
        bg     = _hex(WHITE)
    )
    _canvas.pack()
    _root.bind("<Key>", _on_key)
    _root.bind("<Button-1>", _on_click)
    _root.bind("<ButtonRelease-1>", _on_release)

def _on_key(ev):
    _key_queue.append(ev.keysym.lower())

def _on_click(ev):
    global _mouse_pressed, _mouse_x, _mouse_y
    _mouse_pressed = True
    _mouse_x, _mouse_y = ev.x, ev.y

def _on_release(ev):
    global _mouse_pressed
    _mouse_pressed = False

# ─── Koordinat dönüşümleri ───────────────────────────────────────────────
def _to_screen(x, y):
    sx = (x - _xmin)/(_xmax - _xmin) * _width
    sy = _height - (y - _ymin)/(_ymax - _ymin) * _height
    return sx, sy

def _to_world(sx, sy):
    x = sx/_width*(_xmax - _xmin) + _xmin
    y = (_height - sy)/_height*(_ymax - _ymin) + _ymin
    return x, y

# ─── Ölçek ve Boyut ──────────────────────────────────────────────────────
def setCanvasSize(w, h):
    global _width, _height
    _width, _height = w, h
    _init()
    _canvas.config(width=_width, height=_height)

def setXscale(xmin, xmax):
    global _xmin, _xmax
    _xmin, _xmax = xmin, xmax

def setYscale(ymin, ymax):
    global _ymin, _ymax
    _ymin, _ymax = ymin, ymax

def setScale(xmin, xmax, ymin, ymax):
    setXscale(xmin, xmax)
    setYscale(ymin, ymax)

# ─── Kalem ve Yazı Ayarları ─────────────────────────────────────────────
def setPenColor(c):
    global _pen_color
    _pen_color = c

def setPenRadius(r=_DEFAULT_PEN_RADIUS):
    global _pen_radius
    _pen_radius = max(1.0, r)

def setFontFamily(name):
    global _font_family
    _font_family = name

def setFontSize(size):
    global _font_size
    _font_size = size

# ─── Temizleme ve Kaydetme ───────────────────────────────────────────────
def clear(c=None):
    _init()
    _canvas.delete("all")
    if c is not None:
        _canvas.config(bg=_hex(c))

def save(filename):
    _init()
    _canvas.postscript(file=filename)

# ─── Çizim Primitifleri ─────────────────────────────────────────────────
def line(x1, y1, x2, y2):
    _init()
    s1, s2 = _to_screen(x1, y1), _to_screen(x2, y2)
    _canvas.create_line(*s1, *s2,
                        fill  = _hex(_pen_color),
                        width = _pen_radius)

def circle(x, y, r):
    _init()
    sx, sy = _to_screen(x, y)
    sr = r*_width/(_xmax - _xmin)
    _canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr,
                        outline = _hex(_pen_color),
                        width   = _pen_radius)

def filledCircle(x, y, r):
    _init()
    sx, sy = _to_screen(x, y)
    sr = r*_width/(_xmax - _xmin)
    _canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr,
                        outline = _hex(_pen_color),
                        width   = _pen_radius,
                        fill    = _hex(_pen_color))

def rectangle(x, y, hw, hh):
    _init()
    sx, sy = _to_screen(x, y)
    w = hw*_width/(_xmax - _xmin)
    h = hh*_height/(_ymax - _ymin)
    _canvas.create_rectangle(sx-w, sy-h, sx+w, sy+h,
                             outline = _hex(_pen_color),
                             width   = _pen_radius)

def filledRectangle(x, y, hw, hh):
    _init()
    sx, sy = _to_screen(x, y)
    w = hw*_width/(_xmax - _xmin)
    h = hh*_height/(_ymax - _ymin)
    _canvas.create_rectangle(sx-w, sy-h, sx+w, sy+h,
                             outline = _hex(_pen_color),
                             width   = _pen_radius,
                             fill    = _hex(_pen_color))

# Kareler
def square(x, y, half):
    rectangle(x, y, half, half)
def filledSquare(x, y, half):
    filledRectangle(x, y, half, half)

# Çokgenler
def polygon(*coords):
    _init()
    pts = []
    for i in range(0, len(coords), 2):
        pts.extend(_to_screen(coords[i], coords[i+1]))
    _canvas.create_polygon(*pts,
                           outline = _hex(_pen_color),
                           fill    = "")

def filledPolygon(*coords):
    _init()
    pts = []
    for i in range(0, len(coords), 2):
        pts.extend(_to_screen(coords[i], coords[i+1]))
    _canvas.create_polygon(*pts,
                           outline = _hex(_pen_color),
                           fill    = _hex(_pen_color))

# Metin
def text(x, y, s):
    _init()
    sx, sy = _to_screen(x, y)
    _canvas.create_text(sx, sy,
                        text = s,
                        fill = _hex(_pen_color),
                        font = (_font_family, _font_size))

# Kalın Metin
def boldText(x, y, s):
    _init()
    sx, sy = _to_screen(x, y)
    _canvas.create_text(sx, sy,
                        text = s,
                        fill = _hex(_pen_color),
                        font = (_font_family, _font_size, "bold"))

# ─── Resim Gösterme ──────────────────────────────────────────────────────
def picture(pic, x, y):
    _init()
    # Picture.save() veya doğrudan dosya adı
    if hasattr(pic, "save"):
        tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tf.close()
        pic.save(tf.name)
        path = tf.name
    else:
        path = pic
    img = tk.PhotoImage(file=path)
    _photo_images.append(img)
    sx, sy = _to_screen(x, y)
    _canvas.create_image(sx, sy, image=img)

# ─── Etkileşim ──────────────────────────────────────────────────────────
def hasNextKeyTyped(): return len(_key_queue) > 0
def nextKeyTyped():    return _key_queue.pop(0) if hasNextKeyTyped() else None
def clearKeysTyped():  _key_queue.clear()
def mousePressed():    return _mouse_pressed
def mouseX():          return _to_world(_mouse_x, _mouse_y)[0]
def mouseY():          return _to_world(_mouse_x, _mouse_y)[1]

# ─── Animasyon ve Mainloop ─────────────────────────────────────────────
def show(t=None):
    _init()
    _root.update()
    if t is not None:
        time.sleep(t/1000.0)    # gerçek bekleme

def pause(t=1000):
    _init()
    time.sleep(t/1000.0)

def enableDoubleBuffering():
    global _double_buffering
    _double_buffering = True

def mainloop():
    _init()
    _root.mainloop()
