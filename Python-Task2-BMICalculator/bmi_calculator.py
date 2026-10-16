"""
BMI Calculator - Advanced GUI Application
A desktop application for calculating and tracking BMI with user history.
Oasis Infobyte Python Programming Internship - Task 2
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from bmi_core import calculate_bmi, classify_bmi, validate_input, get_category_color
from database import BMIDatabase


class BMICalculatorApp:
    """Main BMI Calculator GUI Application."""

    def __init__(self, root):
        """Initialize the BMI Calculator application."""
        self.root = root
        self.root.title("BMI Calculator - Advanced")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        # Initialize database
        self.db = BMIDatabase()

        # Configure styles
        self.setup_styles()

        # Create UI components
        self.create_header()
        self.create_input_section()
        self.create_result_section()
        self.create_buttons_section()
        self.create_history_section()
        self.create_disclaimer()

        # Load existing users
        self.load_users()

    def setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure button styles
        style.configure('Calculate.TButton',
                       font=('Arial', 12, 'bold'),
                       padding=10)

        style.configure('Action.TButton',
                       font=('Arial', 10),
                       padding=5)

    def create_header(self):
        """Create application header."""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title = tk.Label(header_frame,
                        text="BMI Calculator",
                        font=('Arial', 24, 'bold'),
                        bg='#2c3e50',
                        fg='white')
        title.pack(pady=20)

    def create_input_section(self):
        """Create input fields section."""
        input_frame = tk.LabelFrame(self.root,
                                   text="Enter Your Details",
                                   font=('Arial', 12, 'bold'),
                                   padx=20,
                                   pady=20)
        input_frame.pack(padx=20, pady=20, fill='x')

        # Username input
        tk.Label(input_frame,
                text="Name (optional):",
                font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)

        self.username_var = tk.StringVar()
        self.username_combo = ttk.Combobox(input_frame,
                                          textvariable=self.username_var,
                                          font=('Arial', 10),
                                          width=25)
        self.username_combo.grid(row=0, column=1, pady=5, sticky='ew')

        # Weight input
        tk.Label(input_frame,
                text="Weight (kg):",
                font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)

        self.weight_var = tk.StringVar()
        weight_entry = tk.Entry(input_frame,
                               textvariable=self.weight_var,
                               font=('Arial', 10),
                               width=27)
        weight_entry.grid(row=1, column=1, pady=5, sticky='ew')

        # Height input
        tk.Label(input_frame,
                text="Height (metres):",
                font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)

        self.height_var = tk.StringVar()
        height_entry = tk.Entry(input_frame,
                               textvariable=self.height_var,
                               font=('Arial', 10),
                               width=27)
        height_entry.grid(row=2, column=1, pady=5, sticky='ew')

        # Configure grid weights
        input_frame.columnconfigure(1, weight=1)

        # Bind Enter key to calculate
        weight_entry.bind('<Return>', lambda e: self.calculate_bmi())
        height_entry.bind('<Return>', lambda e: self.calculate_bmi())

    def create_result_section(self):
        """Create results display section."""
        self.result_frame = tk.LabelFrame(self.root,
                                         text="Your BMI Result",
                                         font=('Arial', 12, 'bold'),
                                         padx=20,
                                         pady=20)
        self.result_frame.pack(padx=20, pady=10, fill='x')

        # BMI value display
        self.bmi_label = tk.Label(self.result_frame,
                                 text="--",
                                 font=('Arial', 36, 'bold'),
                                 fg='#34495e')
        self.bmi_label.pack()

        # Category display
        self.category_label = tk.Label(self.result_frame,
                                      text="Enter your details and click Calculate",
                                      font=('Arial', 14),
                                      fg='#7f8c8d')
        self.category_label.pack(pady=5)

        # Hide initially
        self.result_frame.pack_forget()

    def create_buttons_section(self):
        """Create action buttons."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Calculate button
        calc_btn = ttk.Button(button_frame,
                             text="Calculate BMI",
                             style='Calculate.TButton',
                             command=self.calculate_bmi)
        calc_btn.grid(row=0, column=0, padx=5)

        # History button
        history_btn = ttk.Button(button_frame,
                                text="View History",
                                style='Action.TButton',
                                command=self.show_history)
        history_btn.grid(row=0, column=1, padx=5)

        # Trend button
        trend_btn = ttk.Button(button_frame,
                              text="Show Trend",
                              style='Action.TButton',
                              command=self.show_trend)
        trend_btn.grid(row=0, column=2, padx=5)

        # Clear button
        clear_btn = ttk.Button(button_frame,
                              text="Clear",
                              style='Action.TButton',
                              command=self.clear_inputs)
        clear_btn.grid(row=0, column=3, padx=5)

    def create_history_section(self):
        """Create history display section."""
        self.history_frame = tk.LabelFrame(self.root,
                                          text="BMI History",
                                          font=('Arial', 12, 'bold'),
                                          padx=10,
                                          pady=10)
        # Initially hidden, shown when View History is clicked

    def create_disclaimer(self):
        """Create BMI disclaimer."""
        disclaimer_frame = tk.Frame(self.root, bg='#ecf0f1', relief='solid', borderwidth=1)
        disclaimer_frame.pack(side='bottom', fill='x', padx=20, pady=10)

        disclaimer_text = ("⚠ Disclaimer: BMI is a screening measure and not a diagnostic tool. "
                          "It does not account for muscle mass, bone density, or body composition. "
                          "Consult a healthcare professional for personalized health advice.")

        disclaimer_label = tk.Label(disclaimer_frame,
                                   text=disclaimer_text,
                                   font=('Arial', 8),
                                   bg='#ecf0f1',
                                   fg='#7f8c8d',
                                   wraplength=550,
                                   justify='left')
        disclaimer_label.pack(padx=10, pady=5)

    def load_users(self):
        """Load existing users from database into combobox."""
        users = self.db.get_all_users()
        self.username_combo['values'] = users

    def calculate_bmi(self):
        """Calculate BMI and display result."""
        # Get inputs
        weight_str = self.weight_var.get()
        height_str = self.height_var.get()
        username = self.username_var.get().strip()

        # Validate inputs
        is_valid, error_msg, weight, height = validate_input(weight_str, height_str, username)

        if not is_valid:
            messagebox.showerror("Invalid Input", error_msg)
            return

        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = get_category_color(category)

        # Display result
        self.bmi_label.config(text=f"{bmi}", fg=color)
        self.category_label.config(text=f"Category: {category}", fg=color)
        self.result_frame.pack(padx=20, pady=10, fill='x')

        # Save to database if username provided
        if username:
            success = self.db.save_record(username, weight, height, bmi, category)
            if success:
                # Update users list
                self.load_users()
        else:
            # Ask if user wants to save
            save = messagebox.askyesno("Save Record",
                                      "Would you like to save this record?\n"
                                      "Enter a name above and calculate again to save.")

    def show_history(self):
        """Display user's BMI history."""
        username = self.username_var.get().strip()

        if not username:
            messagebox.showinfo("No User Selected",
                              "Please enter or select a name to view history.")
            return

        records = self.db.get_user_history(username)

        if not records:
            messagebox.showinfo("No History",
                              f"No BMI records found for {username}.")
            return

        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title(f"BMI History - {username}")
        history_window.geometry("700x400")

        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(history_window,
                                               font=('Courier', 10),
                                               width=80,
                                               height=20)
        text_widget.pack(padx=10, pady=10, fill='both', expand=True)

        # Header
        header = f"{'Date':<20} {'Weight (kg)':<15} {'Height (m)':<15} {'BMI':<10} {'Category':<15}\n"
        header += "-" * 80 + "\n"
        text_widget.insert('1.0', header)

        # Insert records
        for record in records:
            date_str = record[6][:19]  # Trim milliseconds
            weight = f"{record[2]:.1f}"
            height = f"{record[3]:.2f}"
            bmi = f"{record[4]:.2f}"
            category = record[5]

            line = f"{date_str:<20} {weight:<15} {height:<15} {bmi:<10} {category:<15}\n"
            text_widget.insert('end', line)

        text_widget.config(state='disabled')

        # Close button
        close_btn = ttk.Button(history_window,
                              text="Close",
                              command=history_window.destroy)
        close_btn.pack(pady=5)

    def show_trend(self):
        """Display BMI trend chart."""
        username = self.username_var.get().strip()

        if not username:
            messagebox.showinfo("No User Selected",
                              "Please enter or select a name to view trend.")
            return

        records = self.db.get_user_history(username)

        if len(records) < 2:
            messagebox.showinfo("Insufficient Data",
                              f"At least 2 BMI records are needed to show a trend.\n"
                              f"{username} currently has {len(records)} record(s).")
            return

        # Extract data (reverse to show oldest first)
        records = list(reversed(records))
        dates = [datetime.strptime(r[6][:19], '%Y-%m-%d %H:%M:%S') for r in records]
        bmis = [r[4] for r in records]

        # Create trend window
        trend_window = tk.Toplevel(self.root)
        trend_window.title(f"BMI Trend - {username}")
        trend_window.geometry("800x600")

        # Create matplotlib figure
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        # Plot BMI trend
        ax.plot(dates, bmis, marker='o', linestyle='-', linewidth=2, markersize=8)

        # Add category zones
        ax.axhspan(0, 18.5, alpha=0.1, color='blue', label='Underweight')
        ax.axhspan(18.5, 25, alpha=0.1, color='green', label='Normal')
        ax.axhspan(25, 30, alpha=0.1, color='orange', label='Overweight')
        ax.axhspan(30, 50, alpha=0.1, color='red', label='Obese')

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('BMI', fontsize=12)
        ax.set_title(f'BMI Trend for {username}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')

        # Rotate date labels
        fig.autofmt_xdate()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=trend_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        # Close button
        close_btn = ttk.Button(trend_window,
                              text="Close",
                              command=trend_window.destroy)
        close_btn.pack(pady=10)

    def clear_inputs(self):
        """Clear all input fields and hide results."""
        self.weight_var.set("")
        self.height_var.set("")
        self.result_frame.pack_forget()


def main():
    """Main entry point for the BMI Calculator application."""
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
