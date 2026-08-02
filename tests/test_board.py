import unittest
from goban.board import Board


class TestBoard(unittest.TestCase):
    def test_initial_board(self):
        board = Board()
        self.assertEqual(board.get(0, 0), Board.EMPTY)
        self.assertEqual(board.black_captured, 0)
        self.assertEqual(board.white_captured, 0)

    def test_place_stone(self):
        board = Board()
        self.assertTrue(board.place(3, 3, Board.BLACK))
        self.assertEqual(board.get(3, 3), Board.BLACK)
        # Cannot place on top of existing stone
        self.assertFalse(board.place(3, 3, Board.WHITE))

    def test_get_neighbors(self):
        board = Board()
        # Corner
        self.assertEqual(set(board._get_neighbors(0, 0)), {(1, 0), (0, 1)})
        # Edge
        self.assertEqual(set(board._get_neighbors(0, 1)), {(0, 0), (1, 1), (0, 2)})
        # Center
        self.assertEqual(
            set(board._get_neighbors(3, 3)), {(2, 3), (4, 3), (3, 2), (3, 4)}
        )

    def test_get_group_and_liberties(self):
        board = Board()
        # Place single stone
        board.place(3, 3, Board.BLACK)
        group = board._get_group(3, 3)
        self.assertEqual(group, {(3, 3)})
        liberties = board._get_liberties(group)
        self.assertEqual(liberties, {(2, 3), (4, 3), (3, 2), (3, 4)})

        # Add adjacent stone of same color
        board.place(3, 4, Board.BLACK)
        group = board._get_group(3, 3)
        self.assertEqual(group, {(3, 3), (3, 4)})
        liberties = board._get_liberties(group)
        self.assertEqual(liberties, {(2, 3), (4, 3), (3, 2), (2, 4), (4, 4), (3, 5)})

    def test_capture_single_stone(self):
        board = Board()
        # Place white stone in the center
        board.place(3, 3, Board.WHITE)
        # Surround it with black stones
        self.assertTrue(board.place(3, 2, Board.BLACK))
        self.assertTrue(board.place(2, 3, Board.BLACK))
        self.assertTrue(board.place(4, 3, Board.BLACK))
        # Final move to capture
        self.assertTrue(board.place(3, 4, Board.BLACK))

        # White stone should be captured and removed
        self.assertEqual(board.get(3, 3), Board.EMPTY)
        self.assertEqual(board.black_captured, 1)
        self.assertEqual(board.white_captured, 0)

    def test_capture_group(self):
        board = Board()
        # Place two white stones
        board.place(3, 3, Board.WHITE)
        board.place(3, 4, Board.WHITE)

        # Surround them with black
        board.place(3, 2, Board.BLACK)
        board.place(2, 3, Board.BLACK)
        board.place(4, 3, Board.BLACK)
        board.place(2, 4, Board.BLACK)
        board.place(4, 4, Board.BLACK)
        # Final capture move
        self.assertTrue(board.place(3, 5, Board.BLACK))

        # Both white stones should be captured
        self.assertEqual(board.get(3, 3), Board.EMPTY)
        self.assertEqual(board.get(3, 4), Board.EMPTY)
        self.assertEqual(board.black_captured, 2)

    def test_prevent_self_capture(self):
        board = Board()
        # Surround (3, 3) with black
        board.place(3, 2, Board.BLACK)
        board.place(2, 3, Board.BLACK)
        board.place(4, 3, Board.BLACK)
        board.place(3, 4, Board.BLACK)

        # White tries to play on (3, 3) - self-capture, should be illegal
        self.assertFalse(board.place(3, 3, Board.WHITE))
        self.assertEqual(board.get(3, 3), Board.EMPTY)

    def test_self_capture_allowed_if_it_captures(self):
        board = Board()
        # Surround (3, 3) with black except (3, 4) which is white, but that white is also in atari
        # Set up a shape where White playing at (3, 3) will capture a Black stone at (3, 2)
        # White at (3, 2) - wait, let's keep it simple:
        # Black stones at: (2, 3), (4, 3), (3, 4), and (3, 2) - but wait, let's make (3, 2) in atari
        # Black stone at (3, 2) has adjacent empty space only at (3, 3).
        # Black at (3, 2) is surrounded by White at (2, 2), (4, 2), (3, 1).
        # White has also surrounded (3, 3) with (2, 3), (4, 3), (3, 4) which are White.
        # Now if White plays at (3, 3), it looks like self-capture because (3, 3) has no empty neighbors.
        # But it captures the Black stone at (3, 2), so it is legal!

        # Surround (3, 2) with White except for (3, 3)
        board.place(3, 2, Board.BLACK)
        board.place(3, 1, Board.WHITE)
        board.place(2, 2, Board.WHITE)
        board.place(4, 2, Board.WHITE)

        # Surround (3, 3) with White except for (3, 2) which has Black
        board.place(2, 3, Board.WHITE)
        board.place(4, 3, Board.WHITE)
        board.place(3, 4, Board.WHITE)

        # White playing at (3, 3) is legal because it captures Black at (3, 2)
        self.assertTrue(board.place(3, 3, Board.WHITE))
        self.assertEqual(board.get(3, 2), Board.EMPTY)
        self.assertEqual(board.get(3, 3), Board.WHITE)
        self.assertEqual(board.white_captured, 1)

    def test_ko_rule(self):
        board = Board()
        # Set up standard Ko shape:
        # Black has a stone at (3, 3) and surrounds (4, 3) with (4, 2), (5, 3), (4, 4)
        # White surrounds (3, 3) with (3, 2), (2, 3), (3, 4)
        # (4, 3) is empty and is the Ko intersection

        # Black stones
        board.place(4, 2, Board.BLACK)
        board.place(5, 3, Board.BLACK)
        board.place(4, 4, Board.BLACK)
        board.place(3, 3, Board.BLACK)  # target to capture

        # White stones
        board.place(3, 2, Board.WHITE)
        board.place(2, 3, Board.WHITE)
        board.place(3, 4, Board.WHITE)

        # Now, White plays (4, 3) - captures Black at (3, 3)
        self.assertTrue(board.place(4, 3, Board.WHITE))
        self.assertEqual(board.get(3, 3), Board.EMPTY)
        self.assertEqual(board.white_captured, 1)

        # Black is not allowed to immediately recapture at (3, 3)
        self.assertFalse(board.place(3, 3, Board.BLACK))

        # But Black can play elsewhere, say (0, 0)
        self.assertTrue(board.place(0, 0, Board.BLACK))

        # Now White plays somewhere, say (0, 1)
        self.assertTrue(board.place(0, 1, Board.WHITE))

        # Now the Ko is resolved, so Black can recapture at (3, 3)
        self.assertTrue(board.place(3, 3, Board.BLACK))
        self.assertEqual(board.get(4, 3), Board.EMPTY)
        self.assertEqual(board.black_captured, 1)

    def test_save_restore_state(self):
        board = Board()
        board.place(3, 3, Board.BLACK)
        board.place(3, 4, Board.WHITE)
        board.black_captured = 5
        board.white_captured = 3
        board.ko_point = (1, 1)

        # Save state
        state = board.save_state()

        # Modify board
        board.place(0, 0, Board.BLACK)
        board.black_captured = 10
        board.white_captured = 8
        board.ko_point = None

        # Restore state
        board.restore_state(state)

        # Assert old values restored
        self.assertEqual(board.get(3, 3), Board.BLACK)
        self.assertEqual(board.get(3, 4), Board.WHITE)
        self.assertEqual(board.get(0, 0), Board.EMPTY)
        self.assertEqual(board.black_captured, 5)
        self.assertEqual(board.white_captured, 3)
        self.assertEqual(board.ko_point, (1, 1))


if __name__ == "__main__":
    unittest.main()
