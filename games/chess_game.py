"""
Chess Game Foundation
=====================

This file starts a long-term chess project the right way: with the game logic.

Why begin here instead of graphics first?
- Every polished chess UI still depends on the same underlying rules engine.
- If move validation is weak, the interface will feel broken no matter how nice it looks.
- A text-based core is faster to debug, easier to test, and easier to extend.

Current scope of this first version:
- Standard 8x8 board
- Standard starting position
- Turn-based play (White, then Black)
- Basic legal movement for every piece
- Captures
- Simple terminal rendering
- Input like: e2 e4

Implemented so far:
- Standard 8x8 board, pieces, turn-based play
- Full legal move enforcement with king-safety filtering
- Check, checkmate, and stalemate detection
- Castling (kingside and queenside)
- En passant
- Pawn promotion

Coming next:
- Better notation formatting
- Graphical interface (pygame)
- AI opponent
"""

from dataclasses import dataclass


BOARD_SIZE = 8
FILES = "abcdefgh"
RANKS = "12345678"

# Square coordinates for castling: where the king and rook start and end,
# and which squares the king must not be attacked on while castling.
CASTLING_CONFIG: dict = {
	"w": {
		"K": {"king_start": (7, 4), "king_end": (7, 6), "rook_start": (7, 7), "rook_end": (7, 5), "pass_through": [(7, 5), (7, 6)]},
		"Q": {"king_start": (7, 4), "king_end": (7, 2), "rook_start": (7, 0), "rook_end": (7, 3), "pass_through": [(7, 3), (7, 2)]},
	},
	"b": {
		"K": {"king_start": (0, 4), "king_end": (0, 6), "rook_start": (0, 7), "rook_end": (0, 5), "pass_through": [(0, 5), (0, 6)]},
		"Q": {"king_start": (0, 4), "king_end": (0, 2), "rook_start": (0, 0), "rook_end": (0, 3), "pass_through": [(0, 3), (0, 2)]},
	},
}


@dataclass
class Piece:
	"""Represents a chess piece on the board.

	color:
		'w' for white, 'b' for black

	kind:
		One of: 'P', 'R', 'N', 'B', 'Q', 'K'
	"""

	color: str
	kind: str

	def symbol(self) -> str:
		"""Return a single-character display symbol for the piece.

		Uppercase letters represent White.
		Lowercase letters represent Black.
		"""
		return self.kind if self.color == "w" else self.kind.lower()


@dataclass
class MoveRecord:
	"""Stores one executed move and the pre-move snapshot for undo."""

	move_index: int
	player: str
	start_square: str
	end_square: str
	piece_symbol: str
	captured_symbol: str | None
	is_castling: bool
	is_en_passant: bool
	promotion_to: str | None
	board_before: list[list[Piece | None]]
	castling_rights_before: dict
	en_passant_target_before: tuple[int, int] | None
	current_turn_before: str
	result_before: str | None
	halfmove_clock_before: int
	position_counts_before: dict[str, int]


class ChessGame:
	"""Core chess state and move validation.

	The board is stored as a list of rows.
	Each square holds either:
	- None, meaning empty square
	- Piece(...), meaning a chess piece is present
	"""

	def __init__(self) -> None:
		self.board = self.create_starting_board()
		self.current_turn = "w"
		# result is None while the game is ongoing.
		# Possible values once finished: checkmate_*, stalemate, draw_*
		self.result: str | None = None
		# Tracks whether each king and rook have moved. Once revoked, cannot be restored.
		self.castling_rights: dict = {
			"w": {"K": True, "Q": True},
			"b": {"K": True, "Q": True},
		}
		# Square a pawn may capture to via en passant on the very next move.
		# Set when a pawn advances two squares; cleared after any other move.
		self.en_passant_target: tuple[int, int] | None = None
		# Number of half-moves since the last pawn move or capture.
		# Fifty-move draw claim becomes available at 100 half-moves.
		self.halfmove_clock = 0
		# Counts repeated positions for threefold repetition detection.
		self.position_counts: dict[str, int] = {}
		self.record_current_position()
		# Chronological list of moves that were actually played.
		self.move_history: list[MoveRecord] = []

	def create_starting_board(self) -> list[list[Piece | None]]:
		"""Create the standard chess opening position."""
		board: list[list[Piece | None]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

		back_rank = ["R", "N", "B", "Q", "K", "B", "N", "R"]

		for col, kind in enumerate(back_rank):
			board[0][col] = Piece("b", kind)
			board[1][col] = Piece("b", "P")
			board[6][col] = Piece("w", "P")
			board[7][col] = Piece("w", kind)

		return board

	def display(self) -> None:
		"""Print the board in a readable terminal layout."""
		print()
		print("    a   b   c   d   e   f   g   h")
		print("  +---+---+---+---+---+---+---+---+")
		for row in range(BOARD_SIZE):
			rank_label = str(8 - row)
			symbols = []
			for col in range(BOARD_SIZE):
				piece = self.board[row][col]
				symbols.append(piece.symbol() if piece else " ")
			print(f"{rank_label} | " + " | ".join(symbols) + f" | {rank_label}")
			print("  +---+---+---+---+---+---+---+---+")
		print("    a   b   c   d   e   f   g   h")
		print()

	def parse_square(self, square: str) -> tuple[int, int]:
		"""Convert algebraic input like 'e2' into board indexes.

		Mapping examples:
		- a8 -> (0, 0)
		- h1 -> (7, 7)
		- e2 -> (6, 4)
		"""
		if len(square) != 2:
			raise ValueError("Squares must look like e2 or a7")

		file_char = square[0].lower()
		rank_char = square[1]

		if file_char not in FILES or rank_char not in RANKS:
			raise ValueError("Square is outside the chess board")

		col = FILES.index(file_char)
		row = 8 - int(rank_char)
		return row, col

	def in_bounds(self, row: int, col: int) -> bool:
		"""Return True if indexes are on the 8x8 board."""
		return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

	def get_piece(self, row: int, col: int) -> Piece | None:
		"""Return the piece on a square, or None if empty."""
		return self.board[row][col]

	def format_square(self, row: int, col: int) -> str:
		"""Convert board indexes back into chess notation like 'e4'."""
		return f"{FILES[col]}{8 - row}"

	def opposite_color(self, color: str) -> str:
		"""Return the opposing side's color code."""
		return "b" if color == "w" else "w"

	def clone_board(self) -> list[list[Piece | None]]:
		"""Create a deep copy of the current board for reliable undo."""
		copied: list[list[Piece | None]] = []
		for row in self.board:
			copied_row: list[Piece | None] = []
			for piece in row:
				copied_row.append(None if piece is None else Piece(piece.color, piece.kind))
			copied.append(copied_row)
		return copied

	def clone_castling_rights(self) -> dict:
		"""Copy castling rights so undo restores exact prior rights."""
		return {
			"w": {"K": self.castling_rights["w"]["K"], "Q": self.castling_rights["w"]["Q"]},
			"b": {"K": self.castling_rights["b"]["K"], "Q": self.castling_rights["b"]["Q"]},
		}

	def clone_position_counts(self) -> dict[str, int]:
		"""Copy repetition counters for exact undo behavior."""
		return {key: value for key, value in self.position_counts.items()}

	def current_position_key(self) -> str:
		"""Build a compact key for repetition detection.

		Included components:
		- Piece placement
		- Side to move
		- Castling rights
		- En passant target
		"""
		rows: list[str] = []
		for row in self.board:
			parts: list[str] = []
			for piece in row:
				parts.append("." if piece is None else piece.symbol())
			rows.append("".join(parts))

		castle = ""
		if self.castling_rights["w"]["K"]:
			castle += "K"
		if self.castling_rights["w"]["Q"]:
			castle += "Q"
		if self.castling_rights["b"]["K"]:
			castle += "k"
		if self.castling_rights["b"]["Q"]:
			castle += "q"
		if castle == "":
			castle = "-"

		ep = "-"
		if self.en_passant_target is not None:
			ep = self.format_square(*self.en_passant_target)

		return f"{'/'.join(rows)} {self.current_turn} {castle} {ep}"

	def record_current_position(self) -> None:
		"""Increment repetition counter for the current board state."""
		key = self.current_position_key()
		self.position_counts[key] = self.position_counts.get(key, 0) + 1

	def is_threefold_repetition(self) -> bool:
		"""Return True when current position occurred at least three times."""
		return self.position_counts.get(self.current_position_key(), 0) >= 3

	def is_fifty_move_draw(self) -> bool:
		"""Return True if the fifty-move threshold has been reached."""
		return self.halfmove_clock >= 100

	def is_insufficient_material(self) -> bool:
		"""Return True if neither side can force checkmate with current material."""
		non_kings: list[tuple[str, str, tuple[int, int]]] = []
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				piece = self.get_piece(row, col)
				if piece is None or piece.kind == "K":
					continue
				non_kings.append((piece.color, piece.kind, (row, col)))

		if not non_kings:
			return True

		# Any pawn, rook, or queen means mating material exists.
		for _, kind, _ in non_kings:
			if kind in {"P", "R", "Q"}:
				return False

		# One minor piece total (K+B vs K or K+N vs K) is insufficient.
		if len(non_kings) == 1 and non_kings[0][1] in {"B", "N"}:
			return True

		# Two bishops only is insufficient if they are on same-colored squares.
		if len(non_kings) == 2 and all(kind == "B" for _, kind, _ in non_kings):
			(_, _, pos_a), (_, _, pos_b) = non_kings
			color_a = (pos_a[0] + pos_a[1]) % 2
			color_b = (pos_b[0] + pos_b[1]) % 2
			return color_a == color_b

		return False

	def format_move_record(self, record: MoveRecord) -> str:
		"""Return a human-readable single-line move description."""
		parts = [
			f"{record.move_index}.",
			"White" if record.player == "w" else "Black",
			f"{record.start_square}->{record.end_square}",
			record.piece_symbol,
		]
		if record.captured_symbol is not None:
			parts.append(f"x{record.captured_symbol}")
		if record.is_castling:
			parts.append("castle")
		if record.is_en_passant:
			parts.append("en-passant")
		if record.promotion_to is not None:
			parts.append(f"promo={record.promotion_to}")
		return " ".join(parts)

	def undo_last_move(self) -> bool:
		"""Undo the most recent move.

		Returns True if a move was undone; False if no moves exist.
		"""
		if not self.move_history:
			return False

		record = self.move_history.pop()
		self.board = record.board_before
		self.castling_rights = record.castling_rights_before
		self.en_passant_target = record.en_passant_target_before
		self.current_turn = record.current_turn_before
		self.result = record.result_before
		self.halfmove_clock = record.halfmove_clock_before
		self.position_counts = record.position_counts_before
		return True

	def is_path_clear(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
		"""Check that every square between start and end is empty.

		This is used by sliding pieces:
		- rook
		- bishop
		- queen

		Knights do not use path checking because they jump.
		Kings and pawns usually move just one step, so this helper is mostly
		for long-range motion.
		"""
		start_row, start_col = start
		end_row, end_col = end

		row_step = 0 if start_row == end_row else (1 if end_row > start_row else -1)
		col_step = 0 if start_col == end_col else (1 if end_col > start_col else -1)

		current_row = start_row + row_step
		current_col = start_col + col_step

		while (current_row, current_col) != (end_row, end_col):
			if self.get_piece(current_row, current_col) is not None:
				return False
			current_row += row_step
			current_col += col_step

		return True

	def piece_attacks_square(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
		"""Check whether a piece attacks a target square by movement pattern alone.

		This helper ignores king safety.
		It is used for:
		- attack detection
		- pseudo-legal move generation
		- king-in-check validation
		"""
		start_row, start_col = start
		end_row, end_col = end

		if not self.in_bounds(start_row, start_col) or not self.in_bounds(end_row, end_col):
			return False

		piece = self.get_piece(start_row, start_col)
		target = self.get_piece(end_row, end_col)

		if piece is None:
			return False

		if target is not None and target.color == piece.color:
			return False

		row_delta = end_row - start_row
		col_delta = end_col - start_col
		abs_row = abs(row_delta)
		abs_col = abs(col_delta)

		if piece.kind == "P":
			direction = -1 if piece.color == "w" else 1
			return abs_col == 1 and row_delta == direction

		if piece.kind == "R":
			if start_row != end_row and start_col != end_col:
				return False
			return self.is_path_clear(start, end)

		if piece.kind == "N":
			return (abs_row, abs_col) in {(2, 1), (1, 2)}

		if piece.kind == "B":
			if abs_row != abs_col:
				return False
			return self.is_path_clear(start, end)

		if piece.kind == "Q":
			is_straight = start_row == end_row or start_col == end_col
			is_diagonal = abs_row == abs_col
			if not (is_straight or is_diagonal):
				return False
			return self.is_path_clear(start, end)

		if piece.kind == "K":
			return max(abs_row, abs_col) == 1

		return False

	def is_legal_piece_move(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
		"""Check movement rules for the piece on the start square.

		This validates piece motion and board occupancy.
		King safety is handled separately so we can reuse this for move generation.
		"""
		start_row, start_col = start
		end_row, end_col = end

		if not self.in_bounds(start_row, start_col) or not self.in_bounds(end_row, end_col):
			return False

		piece = self.get_piece(start_row, start_col)
		target = self.get_piece(end_row, end_col)

		if piece is None:
			return False

		if target is not None and target.color == piece.color:
			return False

		row_delta = end_row - start_row
		col_delta = end_col - start_col

		if piece.kind == "P":
			direction = -1 if piece.color == "w" else 1
			start_rank = 6 if piece.color == "w" else 1

			if col_delta == 0:
				if row_delta == direction and target is None:
					return True
				if row_delta == 2 * direction and start_row == start_rank and target is None:
					middle_row = start_row + direction
					return self.get_piece(middle_row, start_col) is None
				return False

			if target is not None:
				return self.piece_attacks_square(start, end)

			# En passant: pawn captures diagonally to the empty square left as a target
			# after the opponent advanced a pawn two squares on the previous move.
			if end == self.en_passant_target:
				return self.piece_attacks_square(start, end)

			return False

		return self.piece_attacks_square(start, end)

	def make_move_on_board(self, start: tuple[int, int], end: tuple[int, int]) -> Piece | None:
		"""Apply a move on the board and return any captured piece.

		This is used both by real moves and temporary move simulation.
		"""
		moving_piece = self.board[start[0]][start[1]]
		captured_piece = self.board[end[0]][end[1]]
		self.board[end[0]][end[1]] = moving_piece
		self.board[start[0]][start[1]] = None
		return captured_piece

	def undo_move_on_board(self, start: tuple[int, int], end: tuple[int, int], captured_piece: Piece | None) -> None:
		"""Restore the board after a temporary move simulation."""
		moving_piece = self.board[end[0]][end[1]]
		self.board[start[0]][start[1]] = moving_piece
		self.board[end[0]][end[1]] = captured_piece

	def find_king(self, color: str) -> tuple[int, int] | None:
		"""Locate a side's king on the board."""
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				piece = self.get_piece(row, col)
				if piece is not None and piece.color == color and piece.kind == "K":
					return row, col
		return None

	def is_square_attacked(self, square: tuple[int, int], by_color: str) -> bool:
		"""Return True if any piece of by_color attacks the target square."""
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				piece = self.get_piece(row, col)
				if piece is None or piece.color != by_color:
					continue
				if self.piece_attacks_square((row, col), square):
					return True
		return False

	def is_in_check(self, color: str) -> bool:
		"""Return True if the given side's king is currently under attack."""
		king_square = self.find_king(color)
		if king_square is None:
			raise ValueError(f"No king found for color: {color}")
		return self.is_square_attacked(king_square, self.opposite_color(color))

	def can_castle(self, color: str, side: str) -> bool:
		"""Return True if the given side may castle kingside ('K') or queenside ('Q').

		All of these must hold:
		- Castling rights not revoked (king and relevant rook have never moved)
		- King and rook are on their expected starting squares
		- No pieces between king and rook
		- King is not currently in check
		- King does not pass through or land on an attacked square
		"""
		if not self.castling_rights[color][side]:
			return False

		cfg = CASTLING_CONFIG[color][side]
		king = self.get_piece(*cfg["king_start"])
		rook = self.get_piece(*cfg["rook_start"])

		if king is None or king.kind != "K" or king.color != color:
			return False
		if rook is None or rook.kind != "R" or rook.color != color:
			return False

		# Every square between king and rook must be empty.
		if not self.is_path_clear(cfg["king_start"], cfg["rook_start"]):
			return False

		# King may not castle out of, through, or into check.
		if self.is_in_check(color):
			return False
		for sq in cfg["pass_through"]:
			if self.is_square_attacked(sq, self.opposite_color(color)):
				return False

		return True

	def leaves_king_in_check(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
		"""Return True if making the move would leave the mover's king in check."""
		piece = self.get_piece(*start)
		if piece is None:
			return False

		# En passant removes the captured pawn from a different square than the
		# destination, so we must simulate that removal to get accurate check detection.
		is_en_passant = (
			piece.kind == "P"
			and start[1] != end[1]
			and self.get_piece(*end) is None
			and end == self.en_passant_target
		)

		captured_piece = self.make_move_on_board(start, end)

		ep_pawn_square: tuple[int, int] | None = None
		ep_pawn: Piece | None = None
		if is_en_passant:
			ep_pawn_square = (start[0], end[1])
			ep_pawn = self.board[ep_pawn_square[0]][ep_pawn_square[1]]
			self.board[ep_pawn_square[0]][ep_pawn_square[1]] = None

		try:
			return self.is_in_check(piece.color)
		finally:
			self.undo_move_on_board(start, end, captured_piece)
			if ep_pawn_square is not None:
				self.board[ep_pawn_square[0]][ep_pawn_square[1]] = ep_pawn

	def is_checkmate(self, color: str) -> bool:
		"""Return True if the given side is in check with no legal moves.

		Checkmate ends the game immediately. The side in checkmate loses.
		"""
		return self.is_in_check(color) and len(self.generate_legal_moves_for_color(color)) == 0

	def is_stalemate(self, color: str) -> bool:
		"""Return True if the given side has no legal moves but is NOT in check.

		Stalemate ends the game as a draw. The side to move has no legal option
		but is not under direct attack.
		"""
		return not self.is_in_check(color) and len(self.generate_legal_moves_for_color(color)) == 0

	def generate_pseudo_legal_moves_for_square(self, start: tuple[int, int]) -> list[tuple[int, int]]:
		"""List moves allowed by piece motion before king-safety filtering."""
		piece = self.get_piece(*start)
		if piece is None:
			return []

		moves = []
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				end = (row, col)
				if start == end:
					continue
				if self.is_legal_piece_move(start, end):
					moves.append(end)

		# Castling destinations are not reachable by normal king movement (max 1 step).
		# Add them explicitly when all castling requirements are met.
		if piece.kind == "K":
			for side in ("K", "Q"):
				if self.can_castle(piece.color, side):
					moves.append(CASTLING_CONFIG[piece.color][side]["king_end"])

		return moves

	def generate_legal_moves_for_square(self, start: tuple[int, int]) -> list[tuple[int, int]]:
		"""List fully legal moves for the piece on the given square."""
		piece = self.get_piece(*start)
		if piece is None:
			return []

		moves = []
		for end in self.generate_pseudo_legal_moves_for_square(start):
			if not self.leaves_king_in_check(start, end):
				moves.append(end)
		return moves

	def generate_legal_moves_for_color(self, color: str) -> list[tuple[tuple[int, int], tuple[int, int]]]:
		"""List all fully legal moves for one side.

		Each move is returned as:
		- ((start_row, start_col), (end_row, end_col))
		"""
		moves = []
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				piece = self.get_piece(row, col)
				if piece is None or piece.color != color:
					continue
				start = (row, col)
				for end in self.generate_legal_moves_for_square(start):
					moves.append((start, end))
		return moves

	def move_piece(self, start_square: str, end_square: str, promotion_choice: str = "Q") -> bool:
		"""Attempt to move a piece.

		promotion_choice is used when a pawn reaches the back rank.
		Valid values: 'Q', 'R', 'B', 'N'. Defaults to Queen.
		Returns True if the move succeeds, otherwise False.
		"""
		try:
			start = self.parse_square(start_square)
			end = self.parse_square(end_square)
		except ValueError as error:
			print(f"Input error: {error}")
			return False

		piece = self.get_piece(*start)
		if piece is None:
			print("No piece on the starting square.")
			return False

		if piece.color != self.current_turn:
			side_name = "White" if self.current_turn == "w" else "Black"
			print(f"It is {side_name}'s turn.")
			return False

		if start == end:
			print("Start and end squares are the same.")
			return False

		# Castling is detected by the king moving two squares horizontally.
		is_castling = piece.kind == "K" and abs(end[1] - start[1]) == 2 and start[0] == end[0]
		castle_side: str | None = None

		if is_castling:
			castle_side = "K" if end[1] > start[1] else "Q"
			if not self.can_castle(piece.color, castle_side):
				print("Castling is not available in this position.")
				return False
		else:
			if not self.is_legal_piece_move(start, end):
				print("That move is not legal for this piece in the current position.")
				return False
			if self.leaves_king_in_check(start, end):
				print("That move would leave your king in check.")
				return False

		# En passant: pawn captures diagonally to an empty square.
		is_en_passant = (
			piece.kind == "P"
			and start[1] != end[1]
			and self.get_piece(*end) is None
		)

		# Keep a full snapshot so undo can be exact.
		board_before = self.clone_board()
		castling_rights_before = self.clone_castling_rights()
		en_passant_target_before = self.en_passant_target
		current_turn_before = self.current_turn
		result_before = self.result
		halfmove_clock_before = self.halfmove_clock
		position_counts_before = self.clone_position_counts()

		captured_piece: Piece | None = None
		if is_en_passant:
			captured_piece = self.get_piece(start[0], end[1])
		else:
			captured_piece = self.get_piece(*end)

		# Promotion: pawn reaches the opponent's back rank.
		promotion_rank = 0 if piece.color == "w" else 7
		is_promotion = piece.kind == "P" and end[0] == promotion_rank

		# --- Execute the move ---
		if is_castling and castle_side is not None:
			cfg = CASTLING_CONFIG[piece.color][castle_side]
			self.make_move_on_board(start, end)
			self.make_move_on_board(cfg["rook_start"], cfg["rook_end"])
		elif is_en_passant:
			self.make_move_on_board(start, end)
			# The captured pawn sits on the same row as the moving pawn, same column as the destination.
			self.board[start[0]][end[1]] = None
		else:
			self.make_move_on_board(start, end)

		# Replace pawn with chosen piece on promotion.
		promotion_to: str | None = None
		if is_promotion:
			valid = {"Q", "R", "B", "N"}
			promo = promotion_choice.upper() if promotion_choice.upper() in valid else "Q"
			self.board[end[0]][end[1]] = Piece(piece.color, promo)
			promotion_to = promo

		# --- Update castling rights ---
		# Moving the king revokes both castling rights for that side.
		if piece.kind == "K":
			self.castling_rights[piece.color]["K"] = False
			self.castling_rights[piece.color]["Q"] = False
		# Moving a rook revokes the castling right for that side only.
		if piece.kind == "R":
			for side, cfg in CASTLING_CONFIG[piece.color].items():
				if start == cfg["rook_start"]:
					self.castling_rights[piece.color][side] = False

		# --- Update en passant target ---
		# Only set when a pawn advances two squares; clear on every other move.
		if piece.kind == "P" and abs(end[0] - start[0]) == 2:
			self.en_passant_target = ((start[0] + end[0]) // 2, start[1])
		else:
			self.en_passant_target = None

		# Fifty-move clock resets on pawn move or any capture.
		if piece.kind == "P" or captured_piece is not None:
			self.halfmove_clock = 0
		else:
			self.halfmove_clock += 1

		self.current_turn = "b" if self.current_turn == "w" else "w"
		self.record_current_position()

		# Check terminal conditions for the side that now has to move.
		if self.is_checkmate(self.current_turn):
			winner = "Black" if self.current_turn == "w" else "White"
			loser = "White" if self.current_turn == "w" else "Black"
			self.result = f"checkmate_{self.current_turn}"
			print(f"Checkmate! {loser} is in checkmate. {winner} wins!")
		elif self.is_stalemate(self.current_turn):
			side_name = "White" if self.current_turn == "w" else "Black"
			self.result = "stalemate"
			print(f"Stalemate! {side_name} has no legal moves and is not in check. Draw.")
		elif self.is_insufficient_material():
			self.result = "draw_insufficient_material"
			print("Draw by insufficient material.")
		elif self.is_fifty_move_draw():
			self.result = "draw_fifty_move"
			print("Draw by fifty-move rule.")
		elif self.is_threefold_repetition():
			self.result = "draw_threefold"
			print("Draw by threefold repetition.")

		record = MoveRecord(
			move_index=len(self.move_history) + 1,
			player=current_turn_before,
			start_square=start_square.lower(),
			end_square=end_square.lower(),
			piece_symbol=piece.symbol(),
			captured_symbol=None if captured_piece is None else captured_piece.symbol(),
			is_castling=is_castling,
			is_en_passant=is_en_passant,
			promotion_to=promotion_to,
			board_before=board_before,
			castling_rights_before=castling_rights_before,
			en_passant_target_before=en_passant_target_before,
			current_turn_before=current_turn_before,
			result_before=result_before,
			halfmove_clock_before=halfmove_clock_before,
			position_counts_before=position_counts_before,
		)
		self.move_history.append(record)

		return True

	def prompt_loop(self) -> None:
		"""Run a simple terminal game loop.

		Commands:
		- e2 e4   move a piece
		- moves   list all legal moves for the current side
		- moves e2   list legal moves for one piece
		- history   show all played moves
		- undo   undo the last move
		- draw?   show current draw-rule counters and status
		- quit    exit the program
		"""
		print("Welcome to the chess project foundation.")
		print("Enter moves like: e2 e4")
		print("Type 'moves' to list legal moves for the side to move.")
		print("Type 'moves e2' to inspect one piece.")
		print("Type 'history' to show move history.")
		print("Type 'undo' to revert the last move.")
		print("Type 'draw?' to inspect draw-rule status.")
		print("Type 'quit' to stop.")

		while True:
			self.display()

			# If the game has already ended, display the result and stop.
			if self.result is not None:
				print("Game over. Type 'quit' to exit.")
				user_input = input("> ").strip()
				if user_input.lower() in {"quit", "exit"}:
					break
				continue

			side_name = "White" if self.current_turn == "w" else "Black"
			if self.is_in_check(self.current_turn):
				print(f"{side_name} is in check.")
			user_input = input(f"{side_name} to move > ").strip()

			if user_input.lower() in {"quit", "exit"}:
				print("Exiting game.")
				break

			if user_input.lower() == "history":
				if not self.move_history:
					print("No moves have been played yet.")
				else:
					for record in self.move_history:
						print(self.format_move_record(record))
				continue

			if user_input.lower() == "undo":
				undone = self.undo_last_move()
				if undone:
					print("Last move undone.")
				else:
					print("Nothing to undo.")
				continue

			if user_input.lower() == "draw?":
				position_repeats = self.position_counts.get(self.current_position_key(), 0)
				print(f"Halfmove clock: {self.halfmove_clock} (draw at 100)")
				print(f"Current position repeats: {position_repeats} (draw at 3)")
				print(f"Insufficient material: {'yes' if self.is_insufficient_material() else 'no'}")
				continue

			if user_input.lower() == "moves":
				moves = self.generate_legal_moves_for_color(self.current_turn)
				formatted_moves = [
					f"{self.format_square(*start)}->{self.format_square(*end)}"
					for start, end in moves
				]
				print(f"Legal moves for {side_name} ({len(formatted_moves)} total):")
				print(", ".join(formatted_moves) if formatted_moves else "No legal moves available.")
				continue

			if user_input.lower().startswith("moves "):
				parts = user_input.split()
				if len(parts) != 2:
					print("Use 'moves e2' to inspect one piece.")
					continue
				try:
					start = self.parse_square(parts[1])
				except ValueError as error:
					print(f"Input error: {error}")
					continue

				piece = self.get_piece(*start)
				if piece is None:
					print("No piece on that square.")
					continue
				if piece.color != self.current_turn:
					print("You can only inspect the side whose turn it is.")
					continue

				moves = self.generate_legal_moves_for_square(start)
				formatted_moves = [self.format_square(*end) for end in moves]
				print(f"Legal moves for {parts[1].lower()}: {', '.join(formatted_moves) if formatted_moves else 'none'}")
				continue

			parts = user_input.split()
			if len(parts) != 2:
				print("Please enter moves in the format: e2 e4")
				continue

			# Detect pawn promotion before executing so we can prompt for the piece choice.
			promotion_choice = "Q"
			try:
				src = self.parse_square(parts[0])
				dst = self.parse_square(parts[1])
				mover = self.get_piece(*src)
				promotion_rank = 0 if self.current_turn == "w" else 7
				if mover is not None and mover.kind == "P" and dst[0] == promotion_rank:
					raw = input("Promote pawn to Q / R / B / N (default Q): ").strip().upper()
					if raw in {"Q", "R", "B", "N"}:
						promotion_choice = raw
			except ValueError:
				pass

			moved = self.move_piece(parts[0], parts[1], promotion_choice)
			if moved and self.result is None:
				print("Move played.")


def main() -> None:
	"""Start the basic chess prototype."""
	game = ChessGame()
	game.prompt_loop()


if __name__ == "__main__":
	main()
