#!/usr/bin/env python3
import stddraw
from color import Color
import numpy as np

class GameGrid:
    """Class used for modelling the 2048-Tetris hybrid game grid."""
    def __init__(self, grid_h, grid_w):
        # Dimensions
        self.grid_height   = grid_h
        self.grid_width    = grid_w
        # Matrix of tiles (Tile instances or None)
        self.tile_matrix   = np.full((grid_h, grid_w), None)
        # Active tetromino
        self.current_tetromino = None
        # Game over flag
        self.game_over     = False
        # Drawing parameters
        self.line_color     = Color(0, 0, 0)
        self.boundary_color = Color(0, 0, 0)
        self.line_thickness = 0.01
        self.box_thickness  = 0.02
        # Score
        self.score         = 0

    def display(self):
        """Draw active tetromino (if any), then grid tiles and borders."""
        if self.current_tetromino:
            self.current_tetromino.draw()
        self.draw_grid()
        self.draw_boundaries()

    def draw_grid(self):
        """Draw filled tiles and internal grid lines."""
        # Draw existing tiles
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                tile = self.tile_matrix[row][col]
                if tile is not None:
                    tile.draw()
        # Draw grid lines
        stddraw.setPenColor(self.line_color)
        stddraw.setPenRadius(self.line_thickness)
        start_x, end_x = -0.5, self.grid_width - 0.5
        start_y, end_y = -0.5, self.grid_height - 0.5
        # Vertical lines
        for x in np.arange(start_x + 1, end_x, 1):
            stddraw.line(x, start_y, x, end_y)
        # Horizontal lines
        for y in np.arange(start_y + 1, end_y, 1):
            stddraw.line(start_x, y, end_x, y)
        stddraw.setPenRadius()

    def draw_boundaries(self):
        """Draw outer border around the grid."""
        stddraw.setPenColor(self.boundary_color)
        stddraw.setPenRadius(self.box_thickness)
        pos_x, pos_y = -0.5, -0.5
        stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
        stddraw.setPenRadius()

    def is_inside(self, row, col):
        """Check if (row, col) is within grid bounds."""
        return 0 <= row < self.grid_height and 0 <= col < self.grid_width

    def is_occupied(self, row, col):
        """Check if the cell at (row, col) has a tile."""
        if not self.is_inside(row, col):
            return False
        return self.tile_matrix[row][col] is not None

    def update_grid(self, tiles_to_place):
        """
        Place tiles from a tetromino into the grid;
        set game_over if any tile is out of bounds or overlaps.
        """
        # Reset game_over for this placement step
        self.game_over = False
        n_rows, n_cols = len(tiles_to_place), len(tiles_to_place[0])
        for col in range(n_cols):
            for row in range(n_rows):
                tile = tiles_to_place[row][col]
                if tile is not None:
                    pos = tile.get_position()
                    # 1) Out of grid → game over
                    if not self.is_inside(pos.y, pos.x):
                        self.game_over = True
                    else:
                        # 2) Overlap with existing tile → game over
                        if self.tile_matrix[pos.y][pos.x] is not None:
                            self.game_over = True
                        else:
                            # Place tile
                            self.tile_matrix[pos.y][pos.x] = tile
        return self.game_over

    def sumCheck(self, columnSet, current_tetromino):
        """
        Merge vertically same-numbered tiles (2048 rules) and update score.
        After merging, apply gravity so no tile floats.
        """
        for x in columnSet:
            merged = True
            while merged:
                merged = False
                for y in range(self.grid_height - 1):
                    bottom = self.tile_matrix[y][x]
                    top    = self.tile_matrix[y+1][x]
                    if bottom and top and bottom.number == top.number:
                        # Merge into bottom
                        bottom.number *= 2
                        self.score   += bottom.number
                        bottom.background_color = bottom.color_generator()
                        # Remove top
                        self.tile_matrix[y+1][x] = None
                        # Shift above tiles down by one
                        for yy in range(y+2, self.grid_height):
                            t = self.tile_matrix[yy][x]
                            if t:
                                t.move(0, -1)
                                self.tile_matrix[yy-1][x] = t
                                self.tile_matrix[yy][x]   = None
                        merged = True
                        break
        # After all merges, drop any floating tiles
        self.applyGravity()

    def rowCheck(self, rowSet):
        """
        Remove full rows, update score, and drop above tiles.
        Then apply gravity to clear any floating tiles.
        """
        validRows = sorted(y for y in rowSet if 0 <= y < self.grid_height)
        for y in validRows:
            if not all(self.tile_matrix[y][x] is not None for x in range(self.grid_width)):
                continue
            # Clear row and accumulate score
            for x in range(self.grid_width):
                self.score += self.tile_matrix[y][x].number
                self.tile_matrix[y][x] = None
            # Drop everything above
            for yy in range(y+1, self.grid_height):
                for x in range(self.grid_width):
                    t = self.tile_matrix[yy][x]
                    if t:
                        t.move(0, -1)
                        self.tile_matrix[yy-1][x] = t
                        self.tile_matrix[yy][x]   = None
        # Final gravity pass
        self.applyGravity()

    def applyGravity(self):
        """
        Drop all floating tiles until they land on another tile or bottom.
        """
        for x in range(self.grid_width):
            for y in range(1, self.grid_height):
                tile = self.tile_matrix[y][x]
                if tile and self.tile_matrix[y-1][x] is None:
                    ny = y
                    while ny > 0 and self.tile_matrix[ny-1][x] is None:
                        tile.move(0, -1)
                        self.tile_matrix[ny-1][x] = tile
                        self.tile_matrix[ny][x]   = None
                        ny -= 1
