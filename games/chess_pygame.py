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
PANEL_WIDTH = 340
WINDOW_WIDTH = BOARD_PIXELS + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_PIXELS
FPS = 60
BOT_ENABLED = True
BOT_COLOR = "b"
BOT_MODE = "minimax"
BOT_DEPTH = 2
BOT_MOVE_DELAY_MS = 300
BOT_DIFFICULTY_TO_DEPTH = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}

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
    bot_difficulty: str,
    bot_depth: int,
    training_mode: bool,
    last_move_quality: str | None,
) -> None:
    """Draw side panel status and minimal controls help."""
    panel_rect = pygame.Rect(BOARD_PIXELS, 0, PANEL_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, PANEL_BG, panel_rect)

    x0 = BOARD_PIXELS + 16
    y = 16

    # Title with training mode indicator.
    title_text = "Chess UI [LEARNING MODE]" if training_mode else "Chess UI"
    title = ui_font.render(title_text, True, (76, 175, 80) if training_mode else TEXT_ACCENT)
    surface.blit(title, (x0, y))
    y += 40

    turn_name = "White" if game.current_turn == "w" else "Black"
    turn_line = small_font.render(f"Turn: {turn_name}", True, TEXT_PRIMARY)
    surface.blit(turn_line, (x0, y))
    y += 26

    # Position evaluation.
    eval_score, eval_quality = game.get_position_quality(game.current_turn)
    eval_display = f"{eval_score:+.1f} ({eval_quality})"
    eval_text = small_font.render(f"Position: {eval_display}", True, TEXT_ACCENT)
    surface.blit(eval_text, (x0, y))
    y += 26

    # Last move quality (blunder detection).
    if last_move_quality is not None:
        quality_color = (231, 76, 60) if "Blunder" in last_move_quality else (76, 175, 80) if "Excellent" in last_move_quality else TEXT_PRIMARY
        quality_text = small_font.render(f"Last move: {last_move_quality}", True, quality_color)
        surface.blit(quality_text, (x0, y))
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

    # Opening detection.
    opening_info = game.detect_opening()
    if opening_info is not None:
        opening_name, opening_idea = opening_info
        opening_text = small_font.render(f"Opening: {opening_name}", True, TEXT_ACCENT)
        surface.blit(opening_text, (x0, y))
        y += 22
        idea_text = small_font.render(opening_idea, True, (160, 160, 160))
        surface.blit(idea_text, (x0, y))
        y += 28

    controls_title = small_font.render("Controls", True, TEXT_ACCENT)
    surface.blit(controls_title, (x0, y))
    y += 24

    controls = [
        "Click piece -> select",
        "Click target -> move",
        f"Black bot: {BOT_MODE}",
        f"Difficulty: {bot_difficulty} (d={bot_depth})",
        "1/2/3 -> easy/medium/hard",
        "T -> training mode",
        "U -> undo",
        "R -> new game",
        "Esc -> quit",
    ]
    for line in controls:
        t = small_font.render(line, True, TEXT_PRIMARY)
        surface.blit(t, (x0, y))
        y += 22

    # Training mode suggestions.
    if training_mode and game.result is None:
        y += 10
        suggestions_title = small_font.render("Top Moves", True, TEXT_ACCENT)
        surface.blit(suggestions_title, (x0, y))
        y += 24

        top_moves = game.get_top_moves_minimax(game.current_turn, depth=2, top_n=3)
        if top_moves:
            for i, (start, end, score) in enumerate(top_moves, 1):
                move_notation = f"{game.format_square(*start)}-{game.format_square(*end)}"
                move_text = small_font.render(f"{i}. {move_notation} {score:+.1f}", True, (100, 200, 255))
                surface.blit(move_text, (x0, y))
                y += 22
        else:
            t = small_font.render("(analyzing...)", True, (160, 160, 160))
            surface.blit(t, (x0, y))

    y += 10
    history_title = small_font.render("Recent Moves", True, TEXT_ACCENT)
    surface.blit(history_title, (x0, y))
    y += 24

    recent = game.move_history[-6:]
    if not recent:
        t = small_font.render("(none)", True, (160, 160, 160))
        surface.blit(t, (x0, y))
    else:
        for record in recent:
            text = game.format_move_record(record)
            # Keep lines narrow for the sidebar.
            text = text if len(text) <= 28 else text[:25] + "..."
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
    bot_difficulty = "medium"
    bot_depth = BOT_DIFFICULTY_TO_DEPTH[bot_difficulty]
    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
    training_mode = False
    last_move_quality: str | None = None
    prev_eval: int = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    bot_difficulty = "easy"
                    bot_depth = BOT_DIFFICULTY_TO_DEPTH[bot_difficulty]
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                elif event.key == pygame.K_2:
                    bot_difficulty = "medium"
                    bot_depth = BOT_DIFFICULTY_TO_DEPTH[bot_difficulty]
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                elif event.key == pygame.K_3:
                    bot_difficulty = "hard"
                    bot_depth = BOT_DIFFICULTY_TO_DEPTH[bot_difficulty]
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                elif event.key == pygame.K_t:
                    training_mode = not training_mode
                elif event.key == pygame.K_u:
                    game.undo_last_move()
                    selected_square = None
                    legal_targets = []
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                elif event.key == pygame.K_r:
                    game = ChessGame()
                    selected_square = None
                    legal_targets = []
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                    last_move_quality = None
                    prev_eval = 0

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
                    
                    # Capture evaluation before move (for blunder detection).
                    prev_eval = game.evaluate_position(game.current_turn)
                    
                    # Minimal UI choice: auto-promote to queen for now.
                    game.move_piece(start, end, promotion_choice="Q")
                    
                    # Assess move quality if in training mode.
                    if training_mode and game.move_history:
                        new_eval = game.evaluate_position(game.current_turn)
                        # Perspective: from previous player's view (so negate for current player).
                        last_move_quality = game.get_move_quality_assessment(-prev_eval, -new_eval, game.opposite_color(game.current_turn))
                    
                    selected_square = None
                    legal_targets = []
                    next_bot_move_at = pygame.time.get_ticks() + BOT_MOVE_DELAY_MS
                    continue

                # Select a new piece only if it belongs to the side to move.
                if clicked_piece is not None and clicked_piece.color == game.current_turn and game.result is None:
                    selected_square = (row, col)
                    legal_targets = game.generate_legal_moves_for_square(selected_square)
                else:
                    # Clicked empty or opponent piece without a valid move target.
                    selected_square = None
                    legal_targets = []

        # Let the bot move automatically for its configured side.
        # Delay prevents the move from feeling instantaneous and jarring.
        now = pygame.time.get_ticks()
        if (
            BOT_ENABLED
            and game.result is None
            and game.current_turn == BOT_COLOR
            and selected_square is None
            and now >= next_bot_move_at
        ):
            if BOT_MODE == "minimax":
                game.play_minimax_bot_move(BOT_COLOR, depth=bot_depth)
            else:
                game.play_random_bot_move(BOT_COLOR)
            next_bot_move_at = now + BOT_MOVE_DELAY_MS

        draw_board(screen, selected_square, legal_targets)
        draw_pieces(screen, game, piece_font)
        draw_sidebar(screen, game, ui_font, small_font, bot_difficulty, bot_depth, training_mode, last_move_quality)

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
