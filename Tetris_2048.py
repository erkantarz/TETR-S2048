#!/usr/bin/env python3

# ─── BACKGROUND MUSIC via afplay (stops on Game Over) ────────────────────────
import threading, subprocess, time

stop_bgm = threading.Event()
_bgmp = None

def _play_bgm_loop(filename: str):
    global _bgmp
    while not stop_bgm.is_set():
        _bgmp = subprocess.Popen(['afplay', filename])
        while True:
            if stop_bgm.is_set():
                _bgmp.terminate()
                break
            if _bgmp.poll() is not None:
                break
            time.sleep(0.1)
    if _bgmp and _bgmp.poll() is None:
        _bgmp.terminate()

threading.Thread(
    target=_play_bgm_loop,
    args=('bgm.wav',),
    daemon=True
).start()


# ─── IMPORTS & ACHIEVEMENTS ──────────────────────────────────────────────────
import stddraw
import random, os
from game_grid    import GameGrid
from tetromino    import Tetromino
from picture      import Picture
from color        import Color
from achievements import AchievementManager

ach_mgr = AchievementManager()


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def rowsToCheck(tiles):
    s = set()
    for col in tiles:
        for t in col:
            if t: s.add(t.position.y)
    return s

def columnsToCheck(tiles):
    s = set()
    for col in tiles:
        for t in col:
            if t: s.add(t.position.x)
    return s

def create_tetromino(h, w):
    return Tetromino(random.choice(['I','O','Z']), h, w)


# ─── MAIN ───────────────────────────────────────────────────────────────────
def start():
    grid_h, grid_w = 20, 12
    extra_cols     = 4
    canvas_h       = 40 * grid_h
    canvas_w       = 40 * (grid_w + extra_cols)

    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w + extra_cols - 0.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)

    # Colors
    bg    = Color(42,69,99)
    btn   = Color(25,255,228)
    txt   = Color(31,160,239)
    sb_bg = Color(205,193,180)
    sb_tx = Color(119,110,101)
    ghost = Color(150,150,150)

    # 1) MENU SCREEN
    stddraw.clear(bg)
    pic = Picture(os.path.join(os.path.dirname(__file__),'menu_image.png'))
    stddraw.picture(pic, (grid_w-1)/2, grid_h-7)
    bx,by,bw,bh = (grid_w-1)/2,3.5,8,3
    stddraw.setPenColor(btn)
    stddraw.filledRectangle(bx,by,bw/2,bh/2)
    stddraw.setFontFamily('Arial'); stddraw.setFontSize(25)
    stddraw.setPenColor(txt); stddraw.text(bx,by,'Click Here to Start')
    while True:
        stddraw.show(50)
        if stddraw.mousePressed():
            mx,my = stddraw.mouseX(), stddraw.mouseY()
            if bx-bw/2<=mx<=bx+bw/2 and by-bh/2<=my<=by+bh/2:
                break

    # 2) GAME LOOP
    grid       = GameGrid(grid_h, grid_w)
    game_over  = False
    current    = create_tetromino(grid_h, grid_w)
    next_piece = create_tetromino(grid_h, grid_w)

    while not game_over:
        grid.current_tetromino = current

        # DROP LOOP
        while True:
            if stddraw.hasNextKeyTyped():
                k = stddraw.nextKeyTyped()
                if k in ('left','right','down','up','space'):
                    current.move(k, grid)

            stddraw.clear(bg)
            grid.draw_grid()

            # ── GHOST PIECE ─────────────────────
            min_drop = grid.grid_height
            for col in current.tile_matrix:
                for t in col:
                    if t:
                        x,y = t.position.x, t.position.y; d=0
                        while True:
                            if not grid.is_inside(y-d-1,x) or grid.is_occupied(y-d-1,x):
                                break
                            d+=1
                        min_drop = min(min_drop,d)
            stddraw.setPenColor(ghost)
            for col in current.tile_matrix:
                for t in col:
                    if t:
                        x,y = t.position.x, t.position.y
                        stddraw.filledSquare(x, y-min_drop, 0.5)

            # ACTUAL PIECE
            current.draw()
            grid.draw_boundaries()

            # ── SIDEBAR: Next preview ─────────────
            preview_x, preview_y = grid_w+2, grid_h/2+5
            hw, hh = 1.5, 1.5
            # background box
            stddraw.setPenColor(sb_bg)
            stddraw.filledRectangle(preview_x, preview_y, hw, hh)
            # border
            stddraw.setPenColor(sb_tx); stddraw.setPenRadius(2)
            stddraw.rectangle(preview_x, preview_y, hw, hh)
            stddraw.setPenRadius()
            # label
            stddraw.setFontFamily('Arial'); stddraw.setFontSize(14)
            stddraw.text(preview_x, preview_y-hh-1, 'Next')

            # draw next piece inside box
            dx = preview_x - (grid_w-1)/2
            dy = preview_y - (grid_h-1)/2
            for col in next_piece.tile_matrix:
                for t in col:
                    if t:
                        tx, ty = t.position.x + dx, t.position.y + dy
                        stddraw.setPenColor(t.background_color)
                        stddraw.filledSquare(tx, ty, 0.5)
                        stddraw.setPenColor(t.boundary_color)
                        stddraw.square(tx, ty, 0.5)
                        stddraw.setFontFamily('Arial'); stddraw.setFontSize(16)
                        stddraw.setPenColor(t.foreground_color)
                        stddraw.boldText(tx, ty, str(t.number))

            # ── SCOREBOARD ────────────────────────
            stddraw.setFontSize(18)
            stddraw.setPenColor(Color(255,255,255))
            stddraw.text(grid_w+1, grid_h-2, f'Next: {next_piece.type}')
            sx = grid_w + extra_cols/2
            stddraw.setPenColor(sb_bg)
            stddraw.filledRectangle(sx, grid_h/2, extra_cols/2-0.5, grid_h/2)
            stddraw.setPenColor(sb_tx)
            stddraw.setFontSize(16)
            stddraw.text(sx, grid_h/2+2, 'Score')
            stddraw.setFontSize(22)
            stddraw.text(sx, grid_h/2-1, str(grid.score))

            stddraw.show(300)
            if not current.move('down', grid):
                break

        # PLACE & CHECKS
        tiles     = current.tile_matrix
        game_over = grid.update_grid(tiles)

        rows = rowsToCheck(tiles)
        grid.rowCheck(rows)
        if rows:
            ach_mgr.report_event('row_cleared', len(rows))

        cols = columnsToCheck(tiles)
        grid.sumCheck(cols, current)
        ach_mgr.report_event('score_update', grid.score)

        if game_over:
            break

        current, next_piece = next_piece, create_tetromino(grid_h, grid_w)

    # GAME OVER
    stop_bgm.set()
    stddraw.clear(bg)
    stddraw.setFontSize(40)
    stddraw.setPenColor(Color(255,255,255))
    stddraw.text((grid_w-1)/2, grid_h/2, 'Game Over')
    stddraw.setFontSize(24)
    stddraw.text((grid_w-1)/2, grid_h/2-2, f'Score: {grid.score}')
    stddraw.show(0)
    stddraw.mainloop()

if __name__ == '__main__':
    start()
