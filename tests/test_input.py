import unittest
from goban.input import move


class TestInput(unittest.TestCase):
    def test_normal_movement(self):
        # Center starting position
        cursor = (9, 9)
        self.assertEqual(move("h", cursor), (8, 9))
        self.assertEqual(move("l", cursor), (10, 9))
        self.assertEqual(move("k", cursor), (9, 8))
        self.assertEqual(move("j", cursor), (9, 10))

    def test_jump_movement_letter(self):
        cursor = (9, 9)
        self.assertEqual(move("b", cursor), (6, 9))  # Left 3 spaces
        self.assertEqual(move("w", cursor), (12, 9))  # Right 3 spaces

    def test_absolute_positioning(self):
        cursor = (5, 2)
        self.assertEqual(move("H", cursor), (5, 0))  # Top of current column
        self.assertEqual(move("L", cursor), (5, 18))  # Bottom of current column
        self.assertEqual(move("M", cursor), (5, 9))  # Middle of current column
        self.assertEqual(move("A", cursor), (0, 2))  # Far left of the row
        self.assertEqual(move("I", cursor), (18, 2))  # Far right of the row

    def test_jump_movement_ctrl(self):
        cursor = (9, 9)
        self.assertEqual(move("\x08", cursor), (6, 9))  # Ctrl-H
        self.assertEqual(
            move("\x7f", cursor), (6, 9)
        )  # Ctrl-H / Backspace on modern terminals
        self.assertEqual(move("KEY_BACKSPACE", cursor), (6, 9))  # Backspace on curses
        self.assertEqual(move("\x0c", cursor), (12, 9))  # Ctrl-L
        self.assertEqual(move("\x0b", cursor), (9, 6))  # Ctrl-K
        self.assertEqual(move("\x0a", cursor), (9, 12))  # Ctrl-J (which is \n)

    def test_boundary_constraints(self):
        # Left/Top edge
        cursor = (0, 0)
        self.assertEqual(move("h", cursor), (0, 0))
        self.assertEqual(move("k", cursor), (0, 0))
        self.assertEqual(move("b", cursor), (0, 0))
        self.assertEqual(move("\x0b", cursor), (0, 0))  # Ctrl-K

        # Right/Bottom edge
        cursor = (18, 18)
        self.assertEqual(move("l", cursor), (18, 18))
        self.assertEqual(move("j", cursor), (18, 18))
        self.assertEqual(move("w", cursor), (18, 18))
        self.assertEqual(move("\x0a", cursor), (18, 18))  # Ctrl-J
