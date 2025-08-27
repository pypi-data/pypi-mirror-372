"""Simple tests"""


import io


def test_getch(monkeypatch):
    return True

    # # monkeypatch.setattr('sys.stdin', io.StringIO('my input'))
    # # monkeypatch.setattr('sys.stdin.fileno', lambda: list(range(7)))
    # # monkeypatch.setattr('termios.tcgetattr', lambda *args, **kwargs: None)
    # #
    # # from keyboardstream2py.getch import getch
    #
    # monkeypatch.setattr('getch', lambda *args, **kwargs: None)
    #
    #
    # def getch_loop(is_blocking=True):
    #     print(
    #         f'{"Blocking" if is_blocking is True else "Non-blocking"} '
    #         'getch! Press any key! Esc to quit!'
    #     )
    #     i = 0
    #     getch_func = getch.blocking if is_blocking is True else getch.non_blocking
    #     while True:
    #         char = getch_func()
    #         if char or i % 15000 == 0:
    #             print(f'{i}: {char}')
    #
    #         if char == '\x1b':  # ESC key
    #             break
    #         i += 1
    #
    # getch_file, *args = sys.argv
    #
    # print(
    #     'Getch! Echo key press usage:\n'
    #     f'Blocking mode: python {getch_file}\n'
    #     f'Non-blocking mode: python {getch_file} False\n'
    # )
    #
    # getch_loop(is_blocking=False if len(args) and args[0] == 'False' else True)
