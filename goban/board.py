SIZE = 19


class Board:

    EMPTY = "┼"
    BLACK = "●"
    WHITE = "○"

    def __init__(self):
        self.grid = [[self.EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
        self.black_captured = 0  # White stones captured by Black
        self.white_captured = 0  # Black stones captured by White
        self.ko_point = None

    def _get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                neighbors.append((nx, ny))
        return neighbors

    def _get_group(self, start_x, start_y):
        color = self.grid[start_y][start_x]
        if color == self.EMPTY:
            return set()

        group = set()
        queue = [(start_x, start_y)]
        group.add((start_x, start_y))

        while queue:
            cx, cy = queue.pop(0)
            for nx, ny in self._get_neighbors(cx, cy):
                if (nx, ny) not in group and self.grid[ny][nx] == color:
                    group.add((nx, ny))
                    queue.append((nx, ny))
        return group

    def _get_liberties(self, group):
        liberties = set()
        for gx, gy in group:
            for nx, ny in self._get_neighbors(gx, gy):
                if self.grid[ny][nx] == self.EMPTY:
                    liberties.add((nx, ny))
        return liberties

    def place(self, x, y, stone):
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            return False

        if self.grid[y][x] != self.EMPTY:
            return False

        if (x, y) == self.ko_point:
            return False

        # Temporarily place the stone
        self.grid[y][x] = stone

        # Find adjacent opponent groups
        opponent = self.WHITE if stone == self.BLACK else self.BLACK
        opponent_groups = []
        visited_opponent = set()

        for nx, ny in self._get_neighbors(x, y):
            if self.grid[ny][nx] == opponent and (nx, ny) not in visited_opponent:
                grp = self._get_group(nx, ny)
                opponent_groups.append(grp)
                visited_opponent.update(grp)

        # Find which opponent groups are captured (liberties == 0)
        captured_stones = set()
        for grp in opponent_groups:
            if len(self._get_liberties(grp)) == 0:
                captured_stones.update(grp)

        if captured_stones:
            # Remove captured stones from the board
            for cx, cy in captured_stones:
                self.grid[cy][cx] = self.EMPTY

            # Increase score
            if stone == self.BLACK:
                self.black_captured += len(captured_stones)
            else:
                self.white_captured += len(captured_stones)

            # Check for Ko point
            own_group = self._get_group(x, y)
            if len(captured_stones) == 1 and len(own_group) == 1:
                cx, cy = list(captured_stones)[0]
                own_liberties = self._get_liberties(own_group)
                if len(own_liberties) == 1 and list(own_liberties)[0] == (cx, cy):
                    self.ko_point = (cx, cy)
                else:
                    self.ko_point = None
            else:
                self.ko_point = None
        else:
            # Check for self-capture
            own_group = self._get_group(x, y)
            if len(self._get_liberties(own_group)) == 0:
                # Revert placement
                self.grid[y][x] = self.EMPTY
                return False
            self.ko_point = None

        return True

    def get(self, x, y):
        return self.grid[y][x]

    def save_state(self):
        import copy

        return {
            "grid": copy.deepcopy(self.grid),
            "black_captured": self.black_captured,
            "white_captured": self.white_captured,
            "ko_point": self.ko_point,
        }

    def restore_state(self, state):
        self.grid = state["grid"]
        self.black_captured = state["black_captured"]
        self.white_captured = state["white_captured"]
        self.ko_point = state["ko_point"]
