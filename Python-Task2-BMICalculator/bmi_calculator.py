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


# ─── Premium Dark Theme Palette ──────────────────────────────────────────
# Charcoal base with emerald/teal accents
BG_MAIN       = "#1a1a2e"   # Main window background
BG_CARD       = "#22223a"   # Card/panel background
BG_INPUT      = "#2a2a4a"   # Input field background
BG_HEADER     = "#16213e"   # Header background
BG_HOVER      = "#2d2d50"   # Hover state for cards

ACCENT        = "#00d4aa"   # Primary accent - emerald
ACCENT_DIM    = "#00b894"   # Darker accent
ACCENT_GLOW   = "#55efc4"   # Light accent for glow effects
ACCENT_SOFT   = "#00cec9"   # Teal variant

TEXT_PRIMARY  = "#f0f4f8"   # Primary text
TEXT_SECONDARY = "#a0a8b8"  # Secondary/muted text
TEXT_MUTED    = "#6b7280"   # Dim text
TEXT_ON_ACCENT = "#0d1b1e"  # Text on accent backgrounds

BORDER        = "#3a3a5c"   # Subtle borders
BORDER_ACCENT = "#00d4aa"   # Accent borders

# Category colors (preserved from bmi_core for consistency)
CAT_UNDERWEIGHT = "#3498db"  # Blue
CAT_NORMAL      = "#2ecc71"  # Green
CAT_OVERWEIGHT  = "#f39c12"  # Orange
CAT_OBESE       = "#e74c3c"  # Red

# Category display colors (softer versions for badges)
CAT_BADGE = {
    "Underweight": ("#1e3a5f", "#3498db"),
    "Normal":      ("#1a3d2e", "#2ecc71"),
    "Overweight":  ("#3d2a10", "#f39c12"),
    "Obese":       ("#3d1a1a", "#e74c3c"),
}


class BMICalculatorApp:
    """Main BMI Calculator GUI Application."""

    def __init__(self, root):
        """Initialize the BMI Calculator application."""
        self.root = root
        self.root.title("BMI Calculator — Advanced")
        self.root.geometry("640x780")
        self.root.minsize(600, 720)
        self.root.configure(bg=BG_MAIN)

        # Initialize database
        self.db = BMIDatabase()

        # Configure styles
        self.setup_styles()

        # Create UI components
        self.create_header()
        self.create_input_section()
        self.create_result_section()
        self.create_buttons_section()
        self.create_disclaimer()  # Disclaimer at bottom, always visible

        # Load existing users
        self.load_users()

    # ─── Styling ─────────────────────────────────────────────────────────
    def setup_styles(self):
        """Configure ttk styles for the premium dark theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Base frame styles
        style.configure('TFrame', background=BG_MAIN)
        style.configure('Card.TFrame', background=BG_CARD, borderwidth=1, relief='solid')
        style.configure('InputCard.TFrame', background=BG_CARD, borderwidth=1, relief='solid')

        # Label styles
        style.configure('TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=('Segoe UI', 10))
        style.configure('Card.TLabel', background=BG_CARD, foreground=TEXT_PRIMARY, font=('Segoe UI', 10))
        style.configure('Muted.TLabel', background=BG_MAIN, foreground=TEXT_SECONDARY, font=('Segoe UI', 9))
        style.configure('Card.Muted.TLabel', background=BG_CARD, foreground=TEXT_SECONDARY, font=('Segoe UI', 9))
        style.configure('Title.TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=('Segoe UI', 28, 'bold'))
        style.configure('SectionTitle.TLabel', background=BG_CARD, foreground=TEXT_SECONDARY, font=('Segoe UI', 8, 'bold'))
        style.configure('HeaderTitle.TLabel', background=BG_HEADER, foreground=TEXT_PRIMARY, font=('Segoe UI', 26, 'bold'))

        # Entry styles
        style.configure('Dark.TEntry',
                       fieldbackground=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       bordercolor=BORDER,
                       lightcolor=BORDER,
                       darkcolor=BORDER,
                       borderwidth=1,
                       insertcolor=ACCENT,
                       font=('Segoe UI', 11))
        style.map('Dark.TEntry',
                  fieldbackground=[('focus', BG_INPUT)],
                  bordercolor=[('focus', ACCENT)],
                  lightcolor=[('focus', ACCENT)],
                  darkcolor=[('focus', ACCENT)])

        # Combobox styles
        style.configure('Dark.TCombobox',
                       fieldbackground=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       background=BG_CARD,
                       arrowcolor=TEXT_SECONDARY,
                       bordercolor=BORDER,
                       lightcolor=BORDER,
                       darkcolor=BORDER,
                       borderwidth=1,
                       font=('Segoe UI', 11))
        style.map('Dark.TCombobox',
                  fieldbackground=[('readonly', BG_INPUT)],
                  selectbackground=[('readonly', ACCENT)],
                  selectforeground=[('readonly', TEXT_ON_ACCENT)],
                  bordercolor=[('focus', ACCENT)])

        # Button styles
        style.configure('Primary.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       padding=(24, 12),
                       background=ACCENT,
                       foreground=TEXT_ON_ACCENT,
                       borderwidth=0,
                       focusthickness=0)
        style.map('Primary.TButton',
                  background=[('active', ACCENT_DIM), ('pressed', ACCENT_DIM)],
                  foreground=[('active', TEXT_ON_ACCENT), ('pressed', TEXT_ON_ACCENT)])

        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       padding=(16, 8),
                       background=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       borderwidth=1,
                       bordercolor=BORDER)
        style.map('Secondary.TButton',
                  background=[('active', BG_HOVER), ('pressed', BG_HOVER)],
                  foreground=[('active', ACCENT), ('pressed', ACCENT)],
                  bordercolor=[('active', BORDER_ACCENT)])

        style.configure('Ghost.TButton',
                       font=('Segoe UI', 9),
                       padding=(12, 6),
                       background='transparent',
                       foreground=TEXT_SECONDARY,
                       borderwidth=0)
        style.map('Ghost.TButton',
                  foreground=[('active', ACCENT), ('pressed', ACCENT)])

        # Notebook (if used)
        style.configure('TNotebook', background=BG_MAIN, borderwidth=0)
        style.configure('TNotebook.Tab', background=BG_CARD, foreground=TEXT_SECONDARY, padding=(16, 8), font=('Segoe UI', 9))
        style.map('TNotebook.Tab', background=[('selected', BG_INPUT), ('active', BG_HOVER)], foreground=[('selected', ACCENT), ('active', TEXT_PRIMARY)])

        # Scrollbar
        style.configure('Vertical.TScrollbar', background=BG_CARD, troughcolor=BG_MAIN, bordercolor=BG_MAIN, arrowcolor=TEXT_SECONDARY, width=10)
        style.configure('Horizontal.TScrollbar', background=BG_CARD, troughcolor=BG_MAIN, bordercolor=BG_MAIN, arrowcolor=TEXT_SECONDARY, width=10)

        # Treeview styles
        style.configure('Treeview',
                       background=BG_CARD,
                       foreground=TEXT_PRIMARY,
                       fieldbackground=BG_CARD,
                       borderwidth=0,
                       font=('Segoe UI', 10),
                       rowheight=36)
        style.configure('Treeview.Heading',
                       background=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0)
        style.map('Treeview',
                 background=[('selected', ACCENT)],
                 foreground=[('selected', TEXT_ON_ACCENT)])

    # ─── Helper methods for custom widgets ───────────────────────────────
    def _card(self, parent, padding=20):
        """Create a premium card frame with subtle border and hover effect."""
        frame = tk.Frame(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=padding,
            pady=padding,
        )
        # Hover effect
        def on_enter(e):
            frame.configure(highlightbackground=BORDER_ACCENT)
        def on_leave(e):
            frame.configure(highlightbackground=BORDER)
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        return frame

    def _section_title(self, parent, text):
        """Create a small uppercase section heading."""
        return tk.Label(
            parent,
            text=text.upper(),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=("Segoe UI", 8, "bold"),
        )

    def _modern_entry(self, parent, textvariable, width=28, **kwargs):
        """Create a modern styled entry widget."""
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            font=("Segoe UI", 11),
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            width=width,
            **kwargs,
        )
        return entry

    def _modern_combobox(self, parent, textvariable, width=26, **kwargs):
        """Create a modern styled combobox widget."""
        combo = ttk.Combobox(
            parent,
            textvariable=textvariable,
            font=("Segoe UI", 11),
            width=width,
            style='Dark.TCombobox',
            **kwargs,
        )
        return combo

    # ─── UI Sections ─────────────────────────────────────────────────────
    def create_header(self):
        """Create premium application header."""
        header_frame = tk.Frame(self.root, bg=BG_HEADER, height=90)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Accent line at top
        accent_line = tk.Frame(header_frame, bg=ACCENT, height=3)
        accent_line.pack(fill='x')

        title = tk.Label(header_frame,
                        text="BMI Calculator",
                        font=('Segoe UI', 26, 'bold'),
                        bg=BG_HEADER,
                        fg=TEXT_PRIMARY)
        title.pack(pady=(16, 2))

        subtitle = tk.Label(header_frame,
                           text="Advanced  •  Multi-User  •  Trend Tracking",
                           font=('Segoe UI', 10),
                           bg=BG_HEADER,
                           fg=TEXT_SECONDARY)
        subtitle.pack()

    def create_input_section(self):
        """Create input fields section with premium card styling."""
        # Outer card
        outer_card = self._card(self.root, padding=0)
        outer_card.pack(padx=24, pady=(20, 12), fill='x')

        # Section title
        title_bar = tk.Frame(outer_card, bg=BG_CARD)
        title_bar.pack(fill='x', padx=24, pady=(20, 8))
        self._section_title(title_bar, "Enter Your Details").pack(anchor='w')

        # Input grid
        input_grid = tk.Frame(outer_card, bg=BG_CARD)
        input_grid.pack(fill='x', padx=24, pady=(0, 20))
        input_grid.columnconfigure(1, weight=1)

        # Username input
        tk.Label(input_grid,
                text="Name (optional):",
                font=('Segoe UI', 10),
                bg=BG_CARD,
                fg=TEXT_PRIMARY).grid(row=0, column=0, sticky='w', pady=12)

        self.username_var = tk.StringVar()
        self.username_combo = self._modern_combobox(input_grid, self.username_var, width=26)
        self.username_combo.grid(row=0, column=1, pady=12, sticky='ew')

        # Weight input
        tk.Label(input_grid,
                text="Weight (kg):",
                font=('Segoe UI', 10),
                bg=BG_CARD,
                fg=TEXT_PRIMARY).grid(row=1, column=0, sticky='w', pady=12)

        self.weight_var = tk.StringVar()
        weight_entry = self._modern_entry(input_grid, self.weight_var, width=28)
        weight_entry.grid(row=1, column=1, pady=12, sticky='ew')

        # Height input
        tk.Label(input_grid,
                text="Height (metres):",
                font=('Segoe UI', 10),
                bg=BG_CARD,
                fg=TEXT_PRIMARY).grid(row=2, column=0, sticky='w', pady=12)

        self.height_var = tk.StringVar()
        height_entry = self._modern_entry(input_grid, self.height_var, width=28)
        height_entry.grid(row=2, column=1, pady=12, sticky='ew')

        # Bind Enter key to calculate
        weight_entry.bind('<Return>', lambda e: self.calculate_bmi())
        height_entry.bind('<Return>', lambda e: self.calculate_bmi())

    def create_result_section(self):
        """Create premium results display section."""
        # Result card - initially hidden
        self.result_frame = self._card(self.root, padding=0)
        # Don't pack yet - will be shown after calculation

        # Inner content
        content = tk.Frame(self.result_frame, bg=BG_CARD)
        content.pack(fill='both', expand=True, padx=28, pady=28)

        # Section title
        self._section_title(content, "Your BMI Result").pack(anchor='w', pady=(0, 16))

        # Main BMI display - large and prominent
        self.bmi_label = tk.Label(content,
                                 text="--",
                                 font=('Segoe UI', 64, 'bold'),
                                 bg=BG_CARD,
                                 fg=TEXT_PRIMARY)
        self.bmi_label.pack(pady=(8, 4))

        # BMI unit label
        tk.Label(content,
                text="kg/m²",
                font=('Segoe UI', 12),
                bg=BG_CARD,
                fg=TEXT_MUTED).pack()

        # Divider
        divider = tk.Frame(content, bg=BORDER, height=1)
        divider.pack(fill='x', pady=20)

        # Category badge container
        cat_frame = tk.Frame(content, bg=BG_CARD)
        cat_frame.pack()

        tk.Label(cat_frame,
                text="Category:",
                font=('Segoe UI', 11),
                bg=BG_CARD,
                fg=TEXT_SECONDARY).pack(side='left', padx=(0, 12))

        self.category_badge = tk.Label(cat_frame,
                                      text="—",
                                      font=('Segoe UI', 13, 'bold'),
                                      bg=BG_CARD,
                                      fg=TEXT_SECONDARY,
                                      padx=20,
                                      pady=8)
        self.category_badge.pack(side='left')

    def create_buttons_section(self):
        """Create action buttons with premium styling."""
        button_frame = tk.Frame(self.root, bg=BG_MAIN)
        button_frame.pack(pady=16, fill='x', padx=24)

        # Configure all columns equally
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)

        # Primary calculate button
        calc_btn = ttk.Button(button_frame,
                             text="Calculate BMI",
                             style='Primary.TButton',
                             command=self.calculate_bmi)
        calc_btn.grid(row=0, column=0, padx=4, sticky='ew')

        # Secondary buttons
        history_btn = ttk.Button(button_frame,
                                text="View History",
                                style='Secondary.TButton',
                                command=self.show_history)
        history_btn.grid(row=0, column=1, padx=4, sticky='ew')

        trend_btn = ttk.Button(button_frame,
                              text="Show Trend",
                              style='Secondary.TButton',
                              command=self.show_trend)
        trend_btn.grid(row=0, column=2, padx=4, sticky='ew')

        clear_btn = ttk.Button(button_frame,
                              text="Clear",
                              style='Secondary.TButton',
                              command=self.clear_inputs)
        clear_btn.grid(row=0, column=3, padx=4, sticky='ew')

    def create_disclaimer(self):
        """Create BMI disclaimer with premium styling."""
        disclaimer_frame = tk.Frame(self.root, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        disclaimer_frame.pack(side='bottom', fill='x', padx=24, pady=(12, 24))

        # Accent line at top of disclaimer
        accent_line = tk.Frame(disclaimer_frame, bg=ACCENT, height=2)
        accent_line.pack(fill='x')

        disclaimer_text = ("⚠ Disclaimer: BMI is a screening measure and not a diagnostic tool. "
                          "It does not account for muscle mass, bone density, or body composition. "
                          "Consult a healthcare professional for personalized health advice.")

        disclaimer_label = tk.Label(disclaimer_frame,
                                   text=disclaimer_text,
                                   font=('Segoe UI', 8),
                                   bg=BG_CARD,
                                   fg=TEXT_MUTED,
                                   wraplength=580,
                                   justify='left')
        disclaimer_label.pack(padx=16, pady=12)

        # Store reference for result_frame packing
        self.disclaimer_frame = disclaimer_frame

    # ─── Logic (unchanged) ───────────────────────────────────────────────
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

        # Display result with animation-like update
        self.bmi_label.config(text=f"{bmi}", fg=color)

        # Update category badge with proper styling
        badge_bg, badge_fg = CAT_BADGE.get(category, (BG_CARD, TEXT_SECONDARY))
        self.category_badge.config(text=category, bg=badge_bg, fg=badge_fg)

        # Show result frame - pack it above the disclaimer
        self.result_frame.pack(padx=24, pady=12, fill='x', before=self.disclaimer_frame)

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
        """Display user's BMI history in a premium styled window."""
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

        # Create premium history window
        history_window = tk.Toplevel(self.root)
        history_window.title(f"BMI History — {username}")
        history_window.geometry("780x500")
        history_window.minsize(700, 450)
        history_window.configure(bg=BG_MAIN)
        history_window.transient(self.root)
        history_window.grab_set()

        # Header
        header = tk.Frame(history_window, bg=BG_HEADER, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Frame(header, bg=ACCENT, height=3).pack(fill='x')
        tk.Label(header,
                text=f"BMI History — {username}",
                font=('Segoe UI', 18, 'bold'),
                bg=BG_HEADER,
                fg=TEXT_PRIMARY).pack(pady=16)

        # Toolbar
        toolbar = tk.Frame(history_window, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        toolbar.pack(fill='x', padx=16, pady=(12, 0))
        tk.Label(toolbar,
                text=f"{len(records)} record(s)",
                font=('Segoe UI', 9),
                bg=BG_CARD,
                fg=TEXT_SECONDARY).pack(side='left', padx=16, pady=10)

        # Table using Treeview for better presentation
        columns = ('Date', 'Weight (kg)', 'Height (m)', 'BMI', 'Category')
        tree = ttk.Treeview(history_window, columns=columns, show='headings', height=18, style='Treeview')

        # Configure column headings and widths
        tree.heading('Date', text='Date')
        tree.heading('Weight (kg)', text='Weight (kg)')
        tree.heading('Height (m)', text='Height (m)')
        tree.heading('BMI', text='BMI')
        tree.heading('Category', text='Category')

        tree.column('Date', width=180, anchor='center')
        tree.column('Weight (kg)', width=120, anchor='center')
        tree.column('Height (m)', width=120, anchor='center')
        tree.column('BMI', width=100, anchor='center')
        tree.column('Category', width=140, anchor='center')

        # Scrollbars
        vsb = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(history_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Pack treeview and scrollbars
        tree_frame = tk.Frame(history_window, bg=BG_MAIN)
        tree_frame.pack(fill='both', expand=True, padx=16, pady=(0, 16))
        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # Insert records with category color tags
        for i, record in enumerate(records):
            date_str = record[6][:19]  # Trim milliseconds
            weight = f"{record[2]:.1f}"
            height = f"{record[3]:.2f}"
            bmi = f"{record[4]:.2f}"
            category = record[5]

            # Determine tag for category coloring
            tag = category.lower()
            tree.insert('', 'end', values=(date_str, weight, height, bmi, category), tags=(tag,))

        # Configure category tags
        tree.tag_configure('underweight', foreground=CAT_UNDERWEIGHT)
        tree.tag_configure('normal', foreground=CAT_NORMAL)
        tree.tag_configure('overweight', foreground=CAT_OVERWEIGHT)
        tree.tag_configure('obese', foreground=CAT_OBESE)

        # Close button
        close_btn = ttk.Button(history_window,
                              text="Close",
                              style='Secondary.TButton',
                              command=history_window.destroy)
        close_btn.pack(pady=(0, 16))

    def show_trend(self):
        """Display BMI trend chart with premium dark styling."""
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
        trend_window.title(f"BMI Trend — {username}")
        trend_window.geometry("900x650")
        trend_window.minsize(800, 550)
        trend_window.configure(bg=BG_MAIN)
        trend_window.transient(self.root)

        # Header
        header = tk.Frame(trend_window, bg=BG_HEADER, height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Frame(header, bg=ACCENT, height=3).pack(fill='x')
        tk.Label(header,
                text=f"BMI Trend — {username}",
                font=('Segoe UI', 18, 'bold'),
                bg=BG_HEADER,
                fg=TEXT_PRIMARY).pack(pady=16)

        # Create matplotlib figure with dark theme
        plt.style.use('dark_background')
        fig = Figure(figsize=(10, 6.5), dpi=100, facecolor=BG_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(BG_INPUT)

        # Plot BMI trend with premium styling
        ax.plot(dates, bmis, marker='o', linestyle='-', linewidth=3, markersize=10,
                color=ACCENT, markerfacecolor=ACCENT, markeredgecolor=TEXT_ON_ACCENT, markeredgewidth=2,
                label='BMI', zorder=10)

        # Add category zones with premium colors and transparency
        ax.axhspan(0, 18.5, alpha=0.08, color=CAT_UNDERWEIGHT, label='Underweight', zorder=1)
        ax.axhspan(18.5, 25, alpha=0.08, color=CAT_NORMAL, label='Normal', zorder=1)
        ax.axhspan(25, 30, alpha=0.08, color=CAT_OVERWEIGHT, label='Overweight', zorder=1)
        ax.axhspan(30, 50, alpha=0.08, color=CAT_OBESE, label='Obese', zorder=1)

        # Styling
        ax.set_xlabel('Date', fontsize=13, color=TEXT_SECONDARY, fontweight='medium', labelpad=12)
        ax.set_ylabel('BMI', fontsize=13, color=TEXT_SECONDARY, fontweight='medium', labelpad=12)
        ax.set_title(f'BMI Trend for {username}', fontsize=16, fontweight='bold', color=TEXT_PRIMARY, pad=20)

        # Grid
        ax.grid(True, alpha=0.15, color=TEXT_SECONDARY, linewidth=0.5, linestyle='-')

        # Spines
        for spine in ax.spines.values():
            spine.set_color(BORDER)
            spine.set_linewidth(0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Tick styling
        ax.tick_params(colors=TEXT_SECONDARY, labelsize=10, pad=8)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname('Segoe UI')

        # Legend
        legend = ax.legend(loc='upper right', frameon=True, fancybox=True, framealpha=0.9,
                          facecolor=BG_CARD, edgecolor=BORDER, fontsize=10,
                          labelcolor=TEXT_PRIMARY)
        legend.get_frame().set_linewidth(0)

        # Rotate date labels
        fig.autofmt_xdate(rotation=30, ha='right')

        # Tight layout
        fig.tight_layout(pad=2.0)

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=trend_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=16, pady=(0, 16))

        # Close button
        close_btn = ttk.Button(trend_window,
                              text="Close",
                              style='Secondary.TButton',
                              command=trend_window.destroy)
        close_btn.pack(pady=(0, 16))

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