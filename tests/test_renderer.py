import unittest
from unittest.mock import MagicMock, patch
import curses
from goban.board import Board
from goban.main import safe_render_and_draw

class TestRendererColors(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.cursor = (9, 9)

    @patch('curses.has_colors')
    @patch('curses.color_pair')
    def test_safe_render_and_draw_color_mode_disabled(self, mock_color_pair, mock_has_colors):
        mock_has_colors.return_value = True
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        # Call with color_mode=False
        safe_render_and_draw(
            mock_stdscr,
            self.board,
            self.cursor,
            white_captured=0,
            black_captured=0,
            turn=Board.BLACK,
            message="Test message",
            show_help=False,
            color_mode=False
        )

        # In non-color mode, addstr should be called to print lines
        self.assertTrue(mock_stdscr.addstr.called)
        # addch should NOT be called
        self.assertFalse(mock_stdscr.addch.called)

    @patch('curses.has_colors')
    @patch('curses.color_pair')
    def test_safe_render_and_draw_color_mode_enabled(self, mock_color_pair, mock_has_colors):
        mock_has_colors.return_value = True
        mock_color_pair.side_effect = lambda x: x * 100

        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        # Place a black stone at (3, 3) and a white stone at (3, 4)
        self.board.place(3, 3, Board.BLACK)
        self.board.place(3, 4, Board.WHITE)

        # Call with color_mode=True
        safe_render_and_draw(
            mock_stdscr,
            self.board,
            self.cursor,
            white_captured=0,
            black_captured=0,
            turn=Board.BLACK,
            message="Test message",
            show_help=False,
            color_mode=True
        )

        # In color mode, addch should be called for board lines
        self.assertTrue(mock_stdscr.addch.called)
        # and addstr should be called for non-board lines
        self.assertTrue(mock_stdscr.addstr.called)

        has_grid_line_call = False
        has_star_point_call = False
        has_cursor_call = False
        has_black_stone_call = False
        has_filled_white_stone_call = False

        for call_args in mock_stdscr.addch.call_args_list:
            args = call_args[0]
            char = args[2]
            attr = args[3]
            if char in ("┌", "─", "│"):
                has_grid_line_call = True
                self.assertEqual(attr, 1000)
            elif char in ("+", "·"):
                has_star_point_call = True
                self.assertEqual(attr, 1100)
            elif char == "⊙":
                has_cursor_call = True
                # Should include color pair 14 (1400) OR'ed with A_BOLD attribute
                self.assertTrue(attr & 1400 == 1400)
            elif char == "●" and attr == 1200:
                has_black_stone_call = True
            elif char == "●" and attr == 1300:
                # The white stone (originally '○') must be mapped to filled circle '●' but have color pair 13
                has_filled_white_stone_call = True

        self.assertTrue(has_grid_line_call, "Should render grid lines/border using addch")
        self.assertTrue(has_star_point_call, "Should render star points using addch")
        self.assertTrue(has_cursor_call, "Should render cursor using addch")
        self.assertTrue(has_black_stone_call, "Should render black stone as filled circle with black color")
        self.assertTrue(has_filled_white_stone_call, "Should render white stone as filled circle with white color")
