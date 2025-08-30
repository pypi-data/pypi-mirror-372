import tkinter as tk
from customtkinter import CTkButton
import jdatetime

class ShamsiCalendar(tk.Frame):
    def __init__(self, master=None, year=None, month=None, select_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        today = jdatetime.date.today()
        self.today = today
        self.year = year if year else today.year
        self.month = month if month else today.month
        self.select_callback = select_callback
        self.selected_date = None

        self.header_frame = tk.Frame(self, bg="#f0f0f0")
        self.header_frame.grid(row=0, column=0, columnspan=7, pady=5)

        self.today_btn = CTkButton(self.header_frame, text="امروز", command=self.select_today, bg_color="#ffffff", width=20, border_width=1, border_color="#5a5af2", fg_color='blue', hover_color='#5a5af2')
        self.today_btn.pack(side="left", padx=2)

        self.prev_btn = tk.Button(self.header_frame, text="◀", command=self.prev_month, width=3, relief="flat", bg="#e0e0e0")
        self.prev_btn.pack(side="left", padx=2)

        self.month_label = tk.Label(self.header_frame, text="", font=("Tahoma", 11, "bold"), bg="#f0f0f0")
        self.month_label.pack(side="left", padx=5)

        self.year_var = tk.IntVar(value=self.year)
        self.year_spin = tk.Spinbox(self.header_frame, from_=1300, to=1500,
                                    width=6, textvariable=self.year_var,
                                    command=self.change_year, relief="flat")
        self.year_spin.pack(side="left", padx=5)

        self.next_btn = tk.Button(self.header_frame, text="▶", command=self.next_month, width=3, relief="flat", bg="#e0e0e0")
        self.next_btn.pack(side="left", padx=2)

        self.days_frame = tk.Frame(self, bg="white")
        self.days_frame.grid(row=1, column=0, columnspan=7, pady=5)

        self.draw_calendar()

    def draw_calendar(self):
        if not self.days_frame.winfo_exists():
            return

        for widget in self.days_frame.winfo_children():
            if widget.winfo_exists():
                widget.destroy()

        month_name = jdatetime.date(self.year, self.month, 1).j_months_fa[self.month-1]
        self.month_label.config(text=f"{month_name}")

        days_of_week = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        colors = {"ش": "black", "ی": "black", "د": "black", "س": "black", "چ": "black", "پ": "black", "ج": "red"}
        for i, d in enumerate(days_of_week):
            tk.Label(self.days_frame, text=d, font=("Tahoma", 10, "bold"), width=4, bg="#fafafa", fg=colors[d]).grid(row=0, column=i, padx=1, pady=1)

        first_day = jdatetime.date(self.year, self.month, 1)
        start_weekday = (first_day.togregorian().weekday() + 1) % 7
        days_in_month = jdatetime.j_days_in_month[self.month-1]

        row = 1
        col = start_weekday
        for day in range(1, days_in_month+1):
            date_obj = jdatetime.date(self.year, self.month, day)

            bg = "white"
            fg = "#ececec"

            if col == 6:
                fg = "#f76565"

            if date_obj == self.today:
                fg = "#ADFFA2"

            if self.selected_date == date_obj:
                bg = "#fcef7c"

            btn = CTkButton(self.days_frame, text=str(day), width=10, height=15,
                            command=lambda d=day: self.select_date(d), hover_color='#aeeffc',
                            bg_color=bg, fg_color=fg, font=("Tahoma", 9), text_color='black')
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_today(self):
        self.year = self.today.year
        self.month = self.today.month
        self.year_var.set(self.year)
        self.selected_date = self.today
        if self.select_callback:
            self.select_callback(self.today)
        self.draw_calendar()

    def select_date(self, day):
        self.selected_date = jdatetime.date(self.year, self.month, day)
        if self.select_callback:
            self.select_callback(self.selected_date)
        self.draw_calendar()

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
            self.year_var.set(self.year)
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
            self.year_var.set(self.year)
        else:
            self.month += 1
        self.draw_calendar()

    def change_year(self):
        try:
            self.year = int(self.year_var.get())
            self.draw_calendar()
        except ValueError:
            pass


class ShamsiDateEntry(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tk.StringVar()

        self.entry = tk.Entry(self, textvariable=self.var, width=15, relief="groove", font=("Tahoma", 10), justify='center')
        self.entry.pack(side="left", ipady=2)

        self.btn = tk.Button(self, text="▼", width=2, command=self.toggle_calendar, relief="flat", bg="#e0e0e0")
        self.btn.pack(side="left")

        self.popup = None

    def toggle_calendar(self):
        if self.popup and self.popup.winfo_exists():
            self.close_popup()
        else:
            self.open_popup()

    def open_popup(self):
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()

        self.popup = tk.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.configure(bg="white", bd=1, relief="solid")
        self.popup.geometry(f"+{x}+{y}")

        cal = ShamsiCalendar(self.popup, select_callback=self.set_date, bg="white")
        cal.pack(padx=5, pady=5)

        self.popup.bind("<FocusOut>", lambda e: self.close_popup())
        self.popup.focus_set()

    def close_popup(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None

    def set_date(self, date):
        self.var.set(str(date))
        self.close_popup()

    def get(self):
        return self.var.get()
