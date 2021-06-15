#!/usr/bin/env python3

import curses
from curses import wrapper
from package import textpad
from curses import ascii
from package.mpu import CPU
from package.compiler import Compiler
from package.editor import Editor

ram_row = 0
ram_col = 0
cpu = CPU()
f = cpu.fetch
d = cpu.decode
e = cpu.execute
cpu_cycle = [f, d, e]
time = 0


def main(stdscr: 'curses._CursesWindow'):
    curses.curs_set(0)

    calc_mode = 'NORM'
    disp_mode = '02X'
    clk_frq = 10

    def win_title(window: 'curses._CursesWindow', title: str):
        height, width = window.getmaxyx()
        l = len(title)
        window.box(0, 0)
        window.addstr(0, (width//2)-l//2, title, curses.A_BOLD)
        window.refresh()

    def reg_addstr(window: 'curses._CursesWindow', content: str):
        reg_h, reg_w = window.getmaxyx()
        l = len(content)
        window.addstr(reg_h//2, (reg_w//2)-3//2, "   ")
        window.addstr(reg_h//2, (reg_w//2)-l//2, content)
        window.refresh()

    def create_ui(window: 'curses._CursesWindow'):
        h, w = window.getmaxyx()
        win = curses.newwin(h-6, w-6, 3, 3)
        win.box(0, 0)
        win_h, win_w = win.getmaxyx()
        cmdWin = win.derwin(1, win_w-5, win_h-2, 3)
        ramWin = win.derwin(18, 49, 1, 2)
        txtWin = win.derwin(win_h-21, win_w-4, 19, 2)
        modWin = win.derwin(3, win_w-54, 1, 52)
        dspWin = win.derwin(3, win_w-54, 4, 52)
        regWin = win.derwin(12, win_w-54, 7, 52)
        win.refresh()
        cmdWin.refresh()
        ramWin.refresh()
        txtWin.refresh()
        modWin.refresh()
        dspWin.refresh()
        regWin.refresh()
        return (win, cmdWin, ramWin, txtWin, modWin, dspWin, regWin)

    def create_reg_ui(window: 'curses._CursesWindow'):
        y, x = window.getmaxyx()
        aWin = window.derwin(3, x, 0, 0)
        bWin = window.derwin(3, x, 3, 0)
        czWin = window.derwin(3, x, 6, 0)
        pcWin = window.derwin(3, x, 9, 0)
        aWin.box(0, 0)
        bWin.box(0, 0)
        czWin.box(0, 0)
        pcWin.box(0, 0)
        aWin.refresh()
        bWin.refresh()
        czWin.refresh()
        pcWin.refresh()
        return (aWin, bWin, czWin, pcWin)

    def exit_app(window: 'curses._CursesWindow'):
        window.move(0, 0)
        window.clrtoeol()
        window.addstr(0, 0, "Exiting...")
        window.refresh()
        curses.napms(1000)

    def return_app(window: 'curses._CursesWindow'):
        window.move(0, 0)
        window.clrtoeol()
        window.refresh()

    def ram_out(window: 'curses._CursesWindow', mem: list, index: int, mode: str):
        out_str = ''
        for row in range(16):
            for col in range(16):
                i = (row*16)+col
                out_str = format(mem[i], '02X')
                if i == index and mode == 'PROG':
                    window.addstr(row+1, (col*3)+1, out_str,
                                  curses.A_REVERSE)
                elif i == index and mode == 'NORM':
                    window.addstr(row+1, (col*3)+1, out_str,
                                  curses.A_UNDERLINE)
                else:
                    window.addstr(row+1, (col*3)+1, out_str)
            window.refresh()
            out_str = ''

    def init_ui(ram, txt, mod, dsp, a, b, cz, pc, mode):
        win_title(ram, "RAM")
        win_title(txt, "EDITOR")
        win_title(mod, "MODE")
        win_title(dsp, "DISP")
        win_title(a, "REGA")
        win_title(b, "REGB")
        win_title(cz, "CZ")
        win_title(pc, "PC")

        if mode == 'PROG':
            win_title(pc, "ADDR")

    def get_input(window: 'curses._CursesWindow'):
        window.move(0, 0)
        curses.curs_set(1)
        box = textpad.Textbox(window, insert_mode=True)
        i = box.edit().strip()
        curses.curs_set(0)
        window.move(0, 0)
        window.clrtoeol()
        return i

    def checkHex(s: str):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    def action_up(mode: str):
        global ram_row
        if mode == 'PROG':
            if ram_row > 0:
                ram_row -= 1
            else:
                ram_row = 15

    def action_down(mode: str):
        global ram_row
        if mode == 'PROG':
            if ram_row < 15:
                ram_row += 1
            else:
                ram_row = 0

    def action_left(mode: str):
        global ram_col
        if mode == 'PROG':
            if ram_col > 0:
                ram_col -= 1
            else:
                ram_col = 15

    def action_right(mode: str):
        global ram_col
        if mode == 'PROG':
            if ram_col < 15:
                ram_col += 1
            else:
                ram_col = 0

    def action_enter(mode: str):
        if mode == 'PROG':
            data = get_input(cmd_win)
            if checkHex(data):
                value = int(data, 16)
                if value >= 0 and value <= 255:
                    cpu.ram_mem.write(
                        ram_index,
                        value
                    )
        elif mode == 'NORM':
            pass
        elif mode == 'ASML':
            list = txt_out(txt_win, calc_mode)
            compiler = Compiler(list)
            i_list, _ = compiler.compile()
            cpu.set_instructions(i_list)

    def get_index(mode: str):
        index = 0
        if mode == 'NORM':
            pc = cpu.pc.get_counter()
            index = pc
        elif mode == 'PROG':
            index = ram_row*16 + ram_col
        return index

    def dsp_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'PROG':
            cpu_memory = cpu.ram_mem.get_mem_list()
            reg_addstr(
                window,
                format(
                    cpu_memory[ram_index],
                    disp_mode
                )
            )
        elif mode == 'NORM':
            reg_out = cpu.reg_out.get_value()
            reg_addstr(
                window,
                format(reg_out,
                       disp_mode
                       )
            )
        elif mode == 'ASML':
            reg_addstr(
                window,
                "--"
            )

    def pc_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'PROG':
            reg_addstr(window, format(ram_index, disp_mode))
        elif mode == 'NORM':
            pc = cpu.pc.get_counter()
            reg_addstr(window, format(pc, disp_mode))
        elif mode == 'ASML':
            reg_addstr(window, "--")

    def reg_a_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'NORM':
            reg_a = cpu.reg_a.get_value()
            reg_addstr(window, format(reg_a, disp_mode))
        elif mode == 'PROG' or mode == 'ASML':
            reg_addstr(window, '--')

    def reg_b_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'NORM':
            reg_b = cpu.reg_b.get_value()
            reg_addstr(window, format(reg_b, disp_mode))
        elif mode == 'PROG' or mode == 'ASML':
            reg_addstr(window, '--')

    def reg_cz_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'NORM':
            reg_cz = cpu.reg_cz.get_value()
            reg_addstr(window, format(reg_cz, '02b'))
        elif mode == 'PROG' or mode == 'ASML':
            reg_addstr(window, '--')

    def txt_out(window: 'curses._CursesWindow', mode: str):
        if mode == 'ASML':
            curses.curs_set(1)
            h, w = window.getmaxyx()
            textwin = window.derwin(h-2, w-2, 1, 1)
            textwin.keypad(True)
            editor = Editor(textwin)
            curses.curs_set(0)
            return editor.getBuffer().split()
        else:
            return []

    ui_win, cmd_win, ram_win, txt_win, mod_win, dsp_win, reg_win = create_ui(
        stdscr)
    a_win, b_win, cz_win, pc_win = create_reg_ui(reg_win)

    while True:

        global time
        ram_index = get_index(calc_mode)
        cpu_memory = cpu.ram_mem.get_mem_list()

        init_ui(ram_win, txt_win, mod_win, dsp_win,
                a_win, b_win, cz_win, pc_win, calc_mode)
        ram_out(ram_win, cpu_memory, ram_index, calc_mode)
        dsp_out(dsp_win, calc_mode)
        pc_out(pc_win, calc_mode)
        reg_a_out(a_win, calc_mode)
        reg_b_out(b_win, calc_mode)
        reg_cz_out(cz_win, calc_mode)
        reg_addstr(mod_win, calc_mode)

        cmd = ''
        key = 0
        if cpu.is_enabled():
            if time > 2:
                time = 0
            cpu_cycle[time]()
            curses.napms(int((1/clk_frq)*1000))
            time += 1
        else:
            key = cmd_win.getch()

        if key == ord(':'):
            cmd = get_input(cmd_win)
        elif key == curses.KEY_RESIZE:
            ui_win.refresh()
        elif key == curses.KEY_UP:
            action_up(calc_mode)
        elif key == curses.KEY_DOWN:
            action_down(calc_mode)
        elif key == curses.KEY_LEFT:
            action_left(calc_mode)
        elif key == curses.KEY_RIGHT:
            action_right(calc_mode)
        elif key == ascii.NL or key == ascii.CR:
            action_enter(calc_mode)

        if cmd == 'quit' and calc_mode == 'NORM':
            cmd_win.addstr(0, 0, "Do You Want To Quit?(y/N)")
            cmd_win.refresh()
            usr_inpt = None
            while usr_inpt not in ['y', 'Y', 'n', 'N']:
                usr_inpt = cmd_win.getkey()
                if usr_inpt == 'y' or usr_inpt == 'Y':
                    exit_app(cmd_win)
                    break
                elif usr_inpt == 'n' or usr_inpt == 'N':
                    return_app(cmd_win)
                    continue
                else:
                    pass
            else:
                continue
            break
        elif cmd == 'reset' and calc_mode == 'NORM':
            cpu.reset()

        elif cmd[:4] == 'mode':
            arg = cmd[5:]
            if arg in ['NORM', 'PROG', 'ASML']:
                calc_mode = arg
        elif cmd[:4] == 'disp' and calc_mode == 'NORM':
            arg = cmd[5:]
            dict = {'DEC': 'd', 'HEX': '02X'}
            if arg in dict.keys():
                disp_mode = dict.get(arg, '02X')
        elif cmd == 'run' and calc_mode == 'NORM':
            cpu.reset()
            cpu.set_enabled(True)
        elif cmd[:3] == 'clk' and calc_mode == 'NORM':
            arg = cmd[4:]
            try:
                clk_frq = float(arg)
            except ValueError:
                pass


wrapper(main)
