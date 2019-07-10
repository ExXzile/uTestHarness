from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import sqlite3

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

        # load challenge
        def load_challenge():
            if ch_var.get() != 'Select Challenge':
                sq_cur.execute(f'SELECT * FROM challenges WHERE name="{ch_var.get()}"')
                self.chall_data = sq_cur.fetchone()

                self.desc_box.configure(state='normal')
                self.desc_box.delete(1.0, END)
                self.desc_box.insert(1.0, self.chall_data[2])
                self.desc_box.configure(state='disabled')

                # if accompanying image is provided, load in a Toplevel() window
                if self.chall_data[3]:
                    self.desc_window = Toplevel(master)  # TODO: destroy Toplevel on repeat
                    self.desc_window.geometry('+840+240')
                    self.desc_image = PhotoImage(data=self.chall_data[3])
                    Label(self.desc_window, image=self.desc_image).pack()
            else:
                messagebox.showwarning('Error', 'No Challenge Selected!', icon='warning')

        self.load_btn = ttk.Button(
            self.logo_canvas, text="Load", width=8, style='TButton',
            command=load_challenge
        )
        self.load_btn.grid(row=0, column=0, padx=(204, 0))

        # description box
        self.desc_box = Text(
            master, font='Courier 9', height=20, width=99,
            relief='raised', borderwidth=2, state='disabled'
        )
        self.desc_box.grid(row=1, column=0, padx=12, sticky='news')

        # submit box
        Label(
            master, text='Paste your function or multiple functions here:'
        ).grid(row=2, padx=24, pady=12, sticky='w')

        self.sub_box = Text(
            master, relief='sunken', height=14, width=99, font='Courier 9', borderwidth=2
        )
        with open('WARNING.txt', 'r') as warning:
            self.sub_box.insert(END, warning.read())
        self.sub_box.grid(row=3, padx=12, sticky='news')

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

        # Func(s) test start ----------------------------------------------------------------------
        def func_test():
            user_funcs = self.sub_box.get(1.0, END)
            if user_funcs.strip('\n') == '':
                return
            try:
                exec(user_funcs)
            except (NameError, SyntaxError) as syn_error:
                messagebox.showwarning(
                    'Error', f'Code Error:\n{syn_error}', icon='warning'
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
                    # if user func(s) and syntax is accepted
                    # create report sheet Toplevel() window and continue
                    # -----------------------------------------------------------------------------
                    # TODO: create a separate .py for Toplevel as class, and 'test func'; clean up
                    rep_sheet = Toplevel(master)
                    rep_sheet.geometry('+200+200')
                    rep_box = Text(rep_sheet, width=112, height=36, font='Courier 9')
                    rep_box.pack(padx=12, pady=(12, 0))
                    rep_kill = ttk.Button(
                        rep_sheet, text='Close', width=9, style='TButton',
                        command=rep_sheet.destroy
                    )
                    rep_kill.pack(pady=6, padx=12, anchor='e')

                    # run user func(s) test
                    from code_length import rep_line_count

                    for func in user_funcs_list:
                        results = []
                        rep_box.insert(END, f'\nFunction Test <{func.__name__}> :')
                        for test_num, (test, expect) in enumerate(zip(tests, expects), 1):
                            rep_box.insert(END, f'\n\n_________ Test n: {test_num}')
                            rep_box.insert(END, f'\n   input: {rep_line_count(test)}')

                            # attempt to get func output, report errors
                            try:
                                result = func(test) if type(test) != tuple else func(*test)
                            except Exception as func_error:
                                result = '- NONE- '
                                rep_box.insert(END, f'\n--------- !Func Error!: {func_error}')
                                results.append(False)

                            # continue, compare and report..
                            # except in case of func error, assertion will fail by default
                            try:
                                assert result == expect
                            except AssertionError:
                                # if a 'not a match' received
                                # report mismatch, and check if it is not a 'type' mismatch
                                if type(result) != type(expect) and result != '- NONE -' and result:
                                    rep_box.insert(
                                        END,
                                        f'\nexpected: type <{type(expect).__name__}> - {rep_line_count(expect)}'
                                        f'\nreceived: type <{type(result).__name__}> - {rep_line_count(result)}'
                                    )
                                else:
                                    rep_box.insert(
                                        END,
                                        f'\nexpected: {rep_line_count(expect)}'
                                        f'\nreceived: {rep_line_count(result)}'
                                    )
                                rep_box.insert(END, '\n---> Failed!')
                                results.append(False)
                            else:
                                # if a 'match' received, report success
                                rep_box.insert(
                                    END,
                                    f'\nexpected: {rep_line_count(expect)}'
                                    f'\nreceived: - ✓ -'
                                )
                                rep_box.insert(END, '\n---> Passed!')
                                results.append(True)

                        # end result report for tested func
                        rep_box.insert(
                            END,
                            f'\n'
                            f'\nFunction: <{func.__name__}>'
                        )

                        # all tests successful, report and launch required stats
                        if all(results):
                            rep_box.insert(END, f'\n---> All Tests Passed!')

                            # if code length 'Merit' is specified,
                            # test, grant 'Merit' if qualifies
                            if self.chall_data[6]:
                                from code_length import code_line_count
                                merit_report = code_line_count(func, user_funcs, self.chall_data[6])
                                rep_box.insert(END, f'{merit_report}')

                        # if any of the tests failed
                        else:
                            rep_box.insert(END, f'\n---> Overall Test Failed!')

                        # end func report
                        rep_box.insert(
                            END,
                            '\n________________________________________________\n\n\n'
                        )

        # run tests button
        self.run = ttk.Button(
            master, text='Run Test', width=12, style='TButton',
            command=func_test
        )
        self.run.grid(row=4, pady=12)


def main():
    root = Tk()
    root.title('uTestHarness')
    root.geometry('+480+100')
    root.iconbitmap('Icons\\TH.ico')
    root.resizable(False, True)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(3, weight=3)
    _main_app = MainApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
