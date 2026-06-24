"""
Pygame Chess UI (Minimal Board + Click-to-Move)
===============================================

This file provides a minimal graphical UI layer on top of the existing chess
engine in chess_game.py.

What this UI includes:
- Rendered 8x8 board
- Piece rendering using Unicode chess symbols
- Click a piece to select it
- Highlights legal destination squares for selected piece
- Click a legal target to move
- Status panel (turn, check, game result, simple controls)
- Undo support with U key
- New game with R key

What this UI intentionally keeps minimal:
- No piece animations yet
- No drag-and-drop yet (click-select/click-destination instead)
- Promotion defaults to Queen in this first UI pass
"""

from __future__ import annotations

import sys

import pygame

# Support both direct script execution and package-style imports.
try:
    from chess_game import ChessGame
except ImportError:
    from games.chess_game import ChessGame


BOARD_SIZE = 8
TILE_SIZE = 96
BOARD_PIXELS = BOARD_SIZE * TILE_SIZE
PANEL_WIDTH = 280
WINDOW_WIDTH = BOARD_PIXELS + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_PIXELS
FPS = 60

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECT_COLOR = (244, 208, 63)
TARGET_DOT_COLOR = (52, 73, 94)
TARGET_CAPTURE_RING = (192, 57, 43)
PANEL_BG = (22, 27, 34)
TEXT_PRIMARY = (235, 235, 235)
TEXT_ACCENT = (133, 193, 233)

PIECE_UNICODE = {
    "wK": "♔",
    "wQ": "♕",
    "wR": "♖",
    "wB": "♗",
    "wN": "♘",
    "wP": "♙",
    "bK": "♚",
    "bQ": "♛",
    "bR": "♜",
    "bB": "♝",
    "bN": "♞",
    "bP": "♟",
}


def square_from_mouse(pos: tuple[int, int]) -> tuple[int, int] | None:
    """Map a mouse position to board coordinates (row, col)."""
    x, y = pos
    if x < 0 or y < 0 or x >= BOARD_PIXELS or y >= BOARD_PIXELS:
        return None
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    return int(row), int(col)


def draw_board(surface: pygame.Surface, selected: tuple[int, int] | None, legal_targets: list[tuple[int, int]]) -> None:
    """Draw chessboard squares, selection highlight, and legal-target markers."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

    if selected is not None:
        sel_row, sel_col = selected
        sel_rect = pygame.Rect(sel_col * TILE_SIZE, sel_row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, SELECT_COLOR, sel_rect, width=4)

    for row, col in legal_targets:
        center = (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
        radius = TILE_SIZE // 7
        pygame.draw.circle(surface, TARGET_DOT_COLOR, center, radius)


def draw_pieces(surface: pygame.Surface, game: ChessGame, piece_font: pygame.font.Font) -> None:
    """Render pieces from game state using Unicode symbols."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.get_piece(row, col)
            if piece is None:
                continue

            key = f"{piece.color}{piece.kind}"
            symbol = PIECE_UNICODE[key]
            glyph = piece_font.render(symbol, True, (20, 20, 20))
            rect = glyph.get_rect(center=(col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2 + 2))
            surface.blit(glyph, rect)


def draw_sidebar(
    surface: pygame.Surface,
    game: ChessGame,
    ui_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    """Draw side panel status and minimal controls help."""
    panel_rect = pygame.Rect(BOARD_PIXELS, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, PANEL_BG, panel_rect)

    x0 = BOARD_PIXELS + 16
    y = 16

    title = ui_font.render("Chess UI", True, TEXT_ACCENT)
    surface.blit(title, (x0, y))
    y += 40

    turn_name = "White" if game.current_turn == "w" else "Black"
    turn_line = small_font.render(f"Turn: {turn_name}", True, TEXT_PRIMARY)
    surface.blit(turn_line, (x0, y))
    y += 26

    if game.is_in_check(game.current_turn) and game.result is None:
        in_check = small_font.render("Status: In Check", True, (241, 196, 15))
        surface.blit(in_check, (x0, y))
        y += 26

    if game.result is None:
        game_line = small_font.render("Game: In Progress", True, TEXT_PRIMARY)
    else:
        game_line = small_font.render(f"Game: {game.result}", True, (231, 76, 60))
    surface.blit(game_line, (x0, y))
    y += 34

    controls_title = small_font.render("Controls", True, TEXT_ACCENT)
    surface.blit(controls_title, (x0, y))
    y += 24

    controls = [
        "Click piece -> select",
        "Click target -> move",
        "U -> undo",
        "R -> new game",
        "Esc -> quit",
        "Promotion auto=Q",
    ]
    for line in controls:
        t = small_font.render(line, True, TEXT_PRIMARY)
        surface.blit(t, (x0, y))
        y += 22

    y += 10
    history_title = small_font.render("Recent Moves", True, TEXT_ACCENT)
    surface.blit(history_title, (x0, y))
    y += 24

    recent = game.move_history[-8:]
    if not recent:
        t = small_font.render("(none)", True, (160, 160, 160))
        surface.blit(t, (x0, y))
    else:
        for record in recent:
            text = game.format_move_record(record)
            # Keep lines narrow for the sidebar.
            text = text if len(text) <= 32 else text[:29] + "..."
            t = small_font.render(text, True, (210, 210, 210))
            surface.blit(t, (x0, y))
            y += 20


def main() -> None:
    """Run the minimal pygame chess interface."""
    pygame.init()

    # Font choice uses system fallback if preferred names are unavailable.
    piece_font = pygame.font.SysFont("Segoe UI Symbol, DejaVu Sans", 64)
    ui_font = pygame.font.SysFont("Segoe UI, Arial", 30, bold=True)
    small_font = pygame.font.SysFont("Segoe UI, Arial", 20)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess - Minimal Pygame UI")
    clock = pygame.time.Clock()

    game = ChessGame()
    selected_square: tuple[int, int] | None = None
    legal_targets: list[tuple[int, int]] = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_u:
                    game.undo_last_move()
                    selected_square = None
                    legal_targets = []
                elif event.key == pygame.K_r:
                    game = ChessGame()
                    selected_square = None
                    legal_targets = []

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board_square = square_from_mouse(event.pos)
                if board_square is None:
                    continue

                row, col = board_square
                clicked_piece = game.get_piece(row, col)

                # If a piece is already selected and user clicks a legal target, play move.
                if selected_square is not None and (row, col) in legal_targets and game.result is None:
                    start = game.format_square(*selected_square)
                    end = game.format_square(row, col)
                    # Minimal UI choice: auto-promote to queen for now.
                    game.move_piece(start, end, promotion_choice="Q")
                    selected_square = None
                    legal_targets = []
                    continue

                # Select a new piece only if it belongs to the side to move.
                if clicked_piece is not None and clicked_piece.color == game.current_turn and game.result is None:
                    selected_square = (row, col)
                    legal_targets = game.generate_legal_moves_for_square(selected_square)
                else:
                    # Clicked empty or opponent piece without a valid move target.
                    selected_square = None
                    legal_targets = []

        draw_board(screen, selected_square, legal_targets)
        draw_pieces(screen, game, piece_font)
        draw_sidebar(screen, game, ui_font, small_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except pygame.error as error:
        print("Pygame runtime error:", error)
        print("If pygame is not installed, run: pip install pygame-ce")
        sys.exit(1)
