# ShamsiCalendar: Persian Calendar & Date Entry for Tkinter

**ShamsiCalendar** یک پکیج پایتون برای نمایش و انتخاب تاریخ شمسی (Persian / Jalali) در رابط کاربری Tkinter است. این پکیج شامل یک تقویم شمسی و یک ویجت ورودی تاریخ است که استفاده از آن برای برنامه‌های GUI ساده و سریع است.

---

## ویژگی‌های اصلی

- **تقویم شمسی (ShamsiCalendar)**

  - انتخاب روز با کلیک روی تقویم
  - تغییر ماه و سال به راحتی
  - دکمه "امروز" برای انتخاب سریع تاریخ فعلی
  - رنگ‌بندی مخصوص روز جاری و جمعه‌ها

- **ورودی تاریخ شمسی (ShamsiDateEntry)**

  - نمایش تقویم به صورت Popup با کلیک روی ورودی
  - وارد کردن تاریخ شمسی به راحتی
  - سازگار با Tkinter و CustomTkinter

- **فارسی‌سازی کامل**: نام ماه‌ها و روزهای هفته به فارسی نمایش داده می‌شوند.

---

## نصب

```bash
pip install tk customtkinter jdatetime
```

---

## استفاده از ShamsiCalendar

```python
import tkinter as tk
from your_package import ShamsiCalendar
import jdatetime

def on_date_selected(date):
    print("Selected date:", date)

root = tk.Tk()
root.title("Persian Shamsi Calendar")

cal = ShamsiCalendar(root, year=1404, month=6, select_callback=on_date_selected)
cal.pack(padx=10, pady=10)

root.mainloop()
```

---

## استفاده از ShamsiDateEntry

```python
import tkinter as tk
from shamsicalendar import shamsi_calendar


WIDTH, HEIGHT = 500, 500

def show_value():
    lbl_show_date.configure(text=f'Date: {date_entry.get()}')

app = tk.Tk()

x = ((app.winfo_screenwidth() // 2) - (WIDTH//2))
y = ((app.winfo_screenheight() // 2) - (HEIGHT//2))

app.geometry(f'{WIDTH}x{HEIGHT}+{x}+{y}')
app.resizable(False, False)
app.title('Shamsi Calander App')


tk.Label(text='Hello Welcome', font=('Arial', 25, 'bold')).pack(pady=20)
tk.Label(text='Select Date', font=('Arial', 15, 'bold')).pack()

date_entry = shamsi_calendar.ShamsiDateEntry(app)
date_entry.pack(pady=5)

lbl_show_date = tk.Label(text='Date:                      ', font=('Arial', 30, 'bold'), foreground='red')
lbl_show_date.pack(pady=20)

btn_show = tk.Button(app, text="show Date", command=show_value)
btn_show.pack(pady=10)

app.mainloop()
```

---

## نکات مهم برای کاربران

- روز جاری با رنگ سبز روشن مشخص شده است.
- روز انتخاب‌شده با رنگ زرد نمایش داده می‌شود.
- جمعه‌ها به رنگ قرمز هستند.
- قابلیت callback برای دریافت تاریخ انتخاب شده وجود دارد.

---

## Keywords for Search Engines

Persian calendar, Shamsi calendar, Jalali date, Tkinter date picker, Python GUI, Persian date entry, Python ShamsiCalendar, تقویم شمسی, تقویم شمسی تکینتر

---

## لینک‌ها

- Telegram: @p7deli
- Github: https://github.com/p7deli
