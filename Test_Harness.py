from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import sqlite3
import math

sq_con = sqlite3.connect("challenges.sqlite")
sq_cur = sq_con.cursor()


class MainApp:
    def __init__(self, master):
        self.master = master
        self.chall_data = []

        # ttk style config
        self.ttk_style = ttk.Style()
        self.ttk_style.configure("TButton", justify="c")

        # logo
        self.logo_canvas = Canvas(master, highlightthickness=0)
        self.logo = PhotoImage(file="Icons\\Group.png")
        self.logo_canvas.create_image(482, 57, image=self.logo)
        self.logo_canvas.grid(row=0, column=0, padx=24, sticky='news')

        # challenge selection dropbox
        ch_var = StringVar(master)
        ch_var.set('Select Challenge')
        sq_cur.execute('SELECT name FROM challenges')
        challenges = [i[0] for i in sq_cur.fetchall()]
        self.ch_option = OptionMenu(self.logo_canvas, ch_var, *challenges)
        self.ch_option.grid(row=0, column=0, pady=42, padx=66, sticky='w')

        # load challenge and func()
        def load_challenge():
            sq_cur.execute(f'SELECT * FROM challenges WHERE name="{ch_var.get()}"')
            self.chall_data = sq_cur.fetchone()
            try:
                self.desc_box.configure(state='normal')
                self.desc_box.delete(1.0, END)
                self.desc_box.insert(1.0, self.chall_data[2])
                self.desc_box.configure(state='disabled')

                if self.chall_data[3]:
                    self.desc_image = PhotoImage(data=self.chall_data[3])
                    self.desc_window = Toplevel(master)  # TODO: destroy Toplevel on repeat
                    self.desc_window.geometry('+840+240')
                    Label(self.desc_window, image=self.desc_image).pack()
            except (TypeError, AttributeError):
                pass

        self.load_btn = ttk.Button(
            self.logo_canvas, text="Load", width=8, style='TButton',
            command=load_challenge
        )
        self.load_btn.grid(row=0, column=0, padx=(204, 0))

        # description box
        self.desc_box = Text(
            master, font='Courier 9', height=24, width=99,
            relief='raised', borderwidth=2, state='disabled'
        )
        self.desc_box.grid(row=1, column=0, padx=12, sticky='ew')

        # submit box
        Label(
            master, text='Paste your function or multiple functions here:'
        ).grid(row=2, padx=24, pady=12, sticky='w')

        self.sub_box = Text(
            master, relief='sunken', height=12, width=99, font='Courier 9', borderwidth=2
        )
        self.sub_box.grid(row=3, padx=12)

        # paste from clipboard
        def paste():
            self.sub_box.delete(1.0, END)
            self.sub_box.insert(1.0, master.clipboard_get())

        self.paste_bttn = ttk.Button(
            master, text="Paste from Clipboard", width=20, style='TButton',
            command=paste
        )
        self.paste_bttn.grid(row=2, padx=24, pady=12, sticky='e')

        # -----------------------------------------------------------------------------------------
        # Func(s) test
        def start_test():  # TODO: split this mess into smaller funcs
            user_funcs = self.sub_box.get(1.0, END)
            if user_funcs.strip('\n') == '':
                return
            try:
                exec(user_funcs)
            except Exception as syntax_error:
                messagebox.showwarning(
                    'Error', f'Code Error:\n{syntax_error}', icon='warning'
                )
            else:
                user_funcs_list = [func for name, func in locals().items() if callable(func)]
                try:
                    tests, expects = eval(self.chall_data[4]), eval(self.chall_data[5])
                except (IndexError, TypeError, ValueError):
                    messagebox.showwarning(
                        'Error', 'Error:\nCorrupt Data or No Data loaded', icon='warning'
                    )
                else:

                    # rep sheet Toplevel ----------------------------------------------------------
                    rep_sheet = Toplevel(master)
                    rep_sheet.geometry('+200+200')
                    rep_box = Text(rep_sheet, width=100, height=36, font='Courier 9')
                    rep_box.pack(padx=12, pady=(12, 0))
                    rep_kill = ttk.Button(
                        rep_sheet, text='Close', width=9, style='TButton',
                        command=rep_sheet.destroy
                    )
                    rep_kill.pack(pady=6, padx=12, anchor='e')
                    # -----------------------------------------------------------------------------

                    # run funcs
                    for func in user_funcs_list:
                        results = []
                        rep_box.insert(END, f'\nFunction Test <{func.__name__}> :')
                        for test_num, (test, expect) in enumerate(zip(tests, expects), 1):
                            rep_box.insert(END, f'\n\n_________ Test n: {test_num}')
                            try:
                                result = func(test) \
                                    if type(test) == str or type(test) == int \
                                    else func(*test)
                            except Exception as func_error:
                                result = '- NONE- '
                                rep_box.insert(END, f'\n--------- !Func Error!: {func_error}')
                                results.append(False)

                            try:
                                assert result == expect
                            except AssertionError:
                                rep_box.insert(END, f'\nexpected: {expect}\nreceived: {result}')
                                rep_box.insert(END, '\n---Failed!')
                                results.append(False)
                            else:
                                if len(str(test)) < 100:
                                    rep_box.insert(END, f'\n   input: {test}')
                                else:
                                    rep_box.insert(END, f'\n   input: {str(test)[:90]} <truncated>')
                                rep_box.insert(END, f'\nexpected: {expect}\nreceived: - ✓ -')
                                rep_box.insert(END, '\n---Passed!')
                                results.append(True)

                        # --------------------------------------------------------------------------
                        # if successful, test stats
                        if all(results):  # TODO: add timers
                            rep_box.insert(
                                END, f'\n\nFunction: <{func.__name__}>\n--- All Tests Passed!'
                            )

                            func_code_lines = []
                            func_code_line = []
                            for char in user_funcs:
                                if char != '\n':
                                    func_code_line.append(char)
                                else:
                                    func_code_lines.append(''.join(func_code_line))
                                    func_code_line = []

                            count = 0
                            break_count = False
                            for line in func_code_lines:
                                if line:
                                    line = line.lstrip(' ')
                                    if func.__name__ in line:
                                        count = 0
                                        break_count = True
                                        continue
                                    if line[0] == '#':
                                        continue
                                    if len(line) > 1:
                                        line_count = math.ceil(len(line)/72)
                                        count += line_count
                                    if 'return' in line and break_count:
                                        count -= 1
                                        break

                            rep_box.insert(END, f'\n--- Code Line Count: {count}')

                        else:
                            rep_box.insert(
                                END, f'\n\nFunction: <{func.__name__}>\n--- Test Failed!'
                            )
                        rep_box.insert(END, '\n_________________________________________________')
                        rep_box.insert(END, '\n\n')

        # run tests button
        self.run = ttk.Button(
            master, text='Run Test', width=12, style='TButton',
            command=start_test
        )
        self.run.grid(row=4, pady=12)


def main():
    root = Tk()
    root.title('Test Harness')
    root.geometry('+480+100')
    root.iconbitmap('Icons\\TH.ico')
    root.resizable(False, False)
    root.lift()
    _main_app = MainApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
