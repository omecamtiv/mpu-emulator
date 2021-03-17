import curses
from curses import wrapper
from curses import ascii


class Window:
    def __init__(self, n_rows, n_cols, row=0, col=0):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.row = row
        self.col = col

    @property
    def bottom(self):
        return self.row + self.n_rows - 1

    def up(self, cursor):
        if cursor.row == self.row - 1 and self.row > 0:
            self.row -= 1

    def down(self, cursor, buffer):
        if cursor.row == self.bottom+1 and self.bottom < buffer.bottom:
            self.row += 1

    def translate(self, cursor):
        return cursor.row - self.row, cursor.col - self.col

    def horizontal_scroll(self, cursor,
                          left_margin=5,
                          right_margin=2):
        n_pages = cursor.col // (self.n_cols-right_margin)
        self.col = max(n_pages*self.n_cols-right_margin-left_margin, 0)


class Cursor:
    def __init__(self, row=0, col=0, col_hint=None):
        self.row = row
        self._col = col
        self._col_hint = col if col_hint == None else col_hint

    @ property
    def col(self):
        return self._col

    @ col.setter
    def col(self, col):
        self._col = col
        self._col_hint = col

    def _clamp_col(self, buffer):
        self._col = min(self._col_hint, len(buffer[self.row]))

    def up(self, buffer):
        if self.row > 0:
            self.row -= 1
            self._clamp_col(buffer)

    def down(self, buffer):
        if self.row < buffer.bottom:
            self.row += 1
            self._clamp_col(buffer)

    def left(self, buffer):
        if self.col > 0:
            self.col -= 1
        elif self.row > 0:
            self.row -= 1
            self.col = len(buffer[self.row])

    def right(self, buffer):
        if self.col < len(buffer[self.row]):
            self.col += 1
        elif self.row < buffer.bottom:
            self.row += 1
            self.col = 0


class Buffer:
    def __init__(self, lines):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, index):
        return self.lines[index]

    @ property
    def bottom(self):
        return len(self.lines) - 1

    def insert(self, cursor, string):
        row, col = cursor.row, cursor.col
        if len(self.lines) != 0:
            current = self.lines.pop(row)
            new = current[:col] + string + current[col:]
        else:
            new = string
        self.lines.insert(row, new)

    def split(self, cursor):
        row, col = cursor.row, cursor.col
        current = self.lines.pop(row) if (row, col) != (0, 0) else ""
        self.lines.insert(row, current[:col])
        self.lines.insert(row+1, current[col:])

    def delete(self, cursor):
        row, col = cursor.row, cursor.col
        if (row, col) < (self.bottom, len(self.lines[row])):
            current = self.lines.pop(row)
            if col < len(current):
                new = current[:col] + current[col + 1:]
                self.lines.insert(row, new)
            else:
                next = self.lines.pop(row)
                new = current + next
                self.lines.insert(row, new)


def right(window, cursor, buffer):
    cursor.right(buffer)
    window.down(cursor, buffer)
    window.horizontal_scroll(cursor)


def left(window, cursor, buffer):
    cursor.left(buffer)
    window.up(cursor)
    window.horizontal_scroll(cursor)


class Editor:

    def __init__(self, win: 'curses._CursesWindow', buffer=Buffer([])):
        self.win = win
        height, width = win.getmaxyx()
        self.window = Window(height, width)
        self.cursor = Cursor()
        self.buffer = buffer

        while True:
            self.win.erase()
            for row, line in enumerate(self.buffer[self.window.row:self.window.n_rows+self.window.row]):
                if row == self.cursor.row-self.window.row and self.window.col > 0:
                    line = "<<"+line[self.window.col+1:]
                if len(line) > self.window.n_cols:
                    line = line[:self.window.n_cols-1]+">>"
                win.addstr(row, 0, line)

            self.win.move(*self.window.translate(self.cursor))

            k = self.win.getch()
            if k == ascii.ESC:
                break
            elif k == curses.KEY_UP:
                self.cursor.up(self.buffer)
                self.window.up(self.cursor)
                self.window.horizontal_scroll(self.cursor)
            elif k == curses.KEY_DOWN:
                self.cursor.down(self.buffer)
                self.window.down(self.cursor, self.buffer)
                self.window.horizontal_scroll(self.cursor)
            elif k == curses.KEY_LEFT:
                self.cursor.left(self.buffer)
                self.window.up(self.cursor)
                self.window.horizontal_scroll(self.cursor)
            elif k == curses.KEY_RIGHT:
                self.cursor.right(self.buffer)
                self.window.down(self.cursor, self.buffer)
                self.window.horizontal_scroll(self.cursor)
            elif k == ascii.NL:
                self.buffer.split(self.cursor)
                right(self.window, self.cursor, self.buffer)
            elif k == ascii.DEL:
                r, c = self.cursor.row, self.cursor.col
                if (r, c) == (0, 0):
                    pass
                else:
                    left(self.window, self.cursor, self.buffer)
                    self.buffer.delete(self.cursor)
            else:
                self.buffer.insert(self.cursor, chr(k))
                for _ in chr(k):
                    right(self.window, self.cursor, self.buffer)

    def getBuffer(self):
        text = ""
        for line in self.buffer.lines:
            text += line+"\n"
        return text.strip()


if __name__ == '__main__':
    def main(stdscr: 'curses._CursesWindow'):
        y, x = stdscr.getmaxyx()
        win = curses.newwin(y//2, x//2, 3, 3)
        win.keypad(True)
        editor = Editor(win)
        return editor.getBuffer()

    x = wrapper(main)
    print(x)
