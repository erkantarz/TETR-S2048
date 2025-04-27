#!/usr/bin/env python3
"""
picture.py

Minimal Picture sınıfı: sadece dosya yolu bazlı
(pygame ve Pillow yok).
"""
import os

class Picture:
    """
    Picture(arg1=None, arg2=None)
      • arg1 ve arg2 None ise: boştur, kullanılmaz.
      • arg1=str, arg2=None ise: arg1 dosya adı.
      • arg1=int,arg2=int ise: boş genişlik/yükseklik.
    """
    def __init__(self, arg1=None, arg2=None):
        if arg1 is None and arg2 is None:
            self._path = None
            self._w = 0
            self._h = 0
        elif arg1 is not None and arg2 is None:
            fileName = arg1
            if not os.path.exists(fileName):
                raise IOError(f"File not found: {fileName}")
            self._path = fileName
            self._w = self._h = None
        elif isinstance(arg1, int) and isinstance(arg2, int):
            self._path = None
            self._w = arg1
            self._h = arg2
        else:
            raise ValueError("Invalid args for Picture()")

    def save(self, f):
        """
        save(self, f): resim dosyasını f yoluna kopyalar.
        """
        if self._path:
            with open(self._path, "rb") as src, open(f, "wb") as dst:
                dst.write(src.read())
        else:
            # boşsa hiç bir şey yazmaz (ya da boş dosya)
            open(f, "wb").close()

    def width(self):
        if self._path and self._w is None:
            # kullanıldığı yerde width() pek gerekli değil, 0 dönebilir
            return 0
        return self._w

    def height(self):
        if self._path and self._h is None:
            return 0
        return self._h

    def get(self, x, y):
        raise NotImplementedError("get() not supported")

    def set(self, x, y, c):
        raise NotImplementedError("set() not supported")
