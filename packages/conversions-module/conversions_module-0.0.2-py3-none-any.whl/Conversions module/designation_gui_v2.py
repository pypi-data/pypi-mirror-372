
import tkinter as tk
from tkinter import simpledialog, messagebox

from conversions_module_khan_compatible_v8 import (
    custom_designation_error,
    toggle_string_binary, toggle, toggle_with_return, toggle_with_print,
    get_designation_value, print_designation_value, list_designations, DesignationError
)

def add_designation():
    text = simpledialog.askstring("Input", "Enter string or binary:")
    name = simpledialog.askstring("Designation", "Enter designation name:")
    if text and name:
        try:
            result = toggle_string_binary(text, save_with_designation=True, designation=name)
            messagebox.showinfo("Saved", f"{name} → {result}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def do_toggle():
    name = simpledialog.askstring("Toggle", "Enter designation to toggle:")
    try:
        toggle(name)
        messagebox.showinfo("Toggled", f"{name} toggled.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def do_toggle_return():
    name = simpledialog.askstring("Toggle + Return", "Enter designation to toggle:")
    try:
        value = toggle_with_return(name)
        messagebox.showinfo("Result", value)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def do_print_toggle():
    name = simpledialog.askstring("Toggle + Print", "Enter designation:")
    try:
        toggle_with_print(name, prefix="Toggled: ")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def get_value():
    name = simpledialog.askstring("Get Value", "Enter designation:")
    try:
        value = get_designation_value(name)
        messagebox.showinfo("Value", value)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def print_value():
    name = simpledialog.askstring("Print Value", "Enter designation:")
    try:
        print_designation_value(name, prefix="Stored: ")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def list_all():
    try:
        values = list_designations()
        msg = "\n".join(f"{k}: {v}" for k, v in values.items())
        messagebox.showinfo("All Designations", msg or "None")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Designation Toggle GUI")

tk.Button(root, text="Add Designation", command=add_designation).pack(pady=3)
tk.Button(root, text="Toggle", command=do_toggle).pack(pady=3)
tk.Button(root, text="Toggle + Return", command=do_toggle_return).pack(pady=3)
tk.Button(root, text="Toggle + Print", command=do_print_toggle).pack(pady=3)
tk.Button(root, text="Get Value", command=get_value).pack(pady=3)
tk.Button(root, text="Print Value", command=print_value).pack(pady=3)
tk.Button(root, text="List All", command=list_all).pack(pady=3)
tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

root.mainloop()
