import subprocess


class GnuGo:

    def __init__(self):

        self.process = subprocess.Popen(
            ["gnugo", "--mode", "gtp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def send(self, command):

        if self.process.stdin is None:
            raise RuntimeError("GNU Go stdin is not available")

        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        response = []

        while True:

            if self.process.stdout is None:
                raise RuntimeError("GNU Go stdout is not available")

            line = self.process.stdout.readline()

            if not line:
                break

            line = line.strip()

            if line == "":
                break

            response.append(line)

        return response

    def play(self, color, x, y):

        coord = self.coordinate(x, y)

        return self.send(f"play {color} {coord}")

    def genmove(self, color):

        result = self.send(f"genmove {color}")

        if result:

            move = result[0]

            # GTP 응답 처리
            if move.startswith("="):
                move = move[1:].strip()

            return move

        return None

    def coordinate(self, x, y):

        letters = "ABCDEFGHJKLMNOPQRST"

        return letters[x] + str(19 - y)

    def set_level(self, level):

        self.send(f"level {level}")

    def set_handicap(self, handicap):

        result = self.send(f"fixed_handicap {handicap}")

        positions = []

        if result:

            response_text = " ".join(result)

            if response_text.startswith("="):
                response_text = response_text[1:].strip()

            for coord in response_text.split():
                pos = self.parse_coordinate(coord)
                if pos:
                    positions.append(pos)

        return positions

    def get_final_score(self):

        result = self.send("final_score")

        if result:

            score = result[0]

            if score.startswith("="):
                score = score[1:].strip()

            return score

        return "Unknown"

    def get_territory(self, color):
        result = self.send(f"final_status_list {color}_territory")
        coords = []
        if result:
            response_text = " ".join(result)
            if response_text.startswith("="):
                response_text = response_text[1:].strip()
            for coord in response_text.split():
                pos = self.parse_coordinate(coord)
                if pos:
                    coords.append(pos)
        return coords

    def close(self):

        self.process.terminate()

    def parse_coordinate(self, coord):

        if not coord:
            return None

        coord = coord.strip()

        if coord.upper() in ("PASS", "RESIGN"):
            return None

        letters = "ABCDEFGHJKLMNOPQRST"

        x = letters.index(coord[0].upper())

        y = 19 - int(coord[1:])

        return x, y
