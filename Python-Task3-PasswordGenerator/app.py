"""
Random Password Generator - Premium Tkinter GUI Application

A polished desktop interface for generating secure random passwords
with customizable options and strength feedback.
Dark graphite theme with indigo/violet accents.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from password_generator import (
    PasswordGenerator,
    InvalidLengthError,
    NoCharactersSelectedError,
    PasswordGeneratorError
)


# ─── Premium Dark Theme Palette ──────────────────────────────────────────
# Graphite base with indigo/violet accents
BG_MAIN       = "#18181c"   # Main window background - dark graphite
BG_CARD       = "#1f1f26"   # Card/panel background
BG_INPUT      = "#27272f"   # Input field background
BG_HOVER      = "#2d2d38"   # Hover state for cards

ACCENT        = "#7c5cff"   # Primary accent - indigo/violet
ACCENT_DIM    = "#6b4fff"   # Darker accent
ACCENT_GLOW   = "#b8a8ff"   # Light accent for glow/focus
ACCENT_SOFT   = "#a855f7"   # Violet variant

TEXT_PRIMARY  = "#f4f4f5"   # Primary text (zinc-100)
TEXT_SECONDARY = "#a1a1aa"  # Secondary/muted text (zinc-400)
TEXT_MUTED    = "#71717a"   # Dim text (zinc-500)
TEXT_ON_ACCENT = "#18181c"  # Text on accent backgrounds

BORDER        = "#3f3f46"   # Subtle borders (zinc-700)
BORDER_ACCENT = "#7c5cff"   # Accent borders

# Strength level colors
STRENGTH_WEAK      = "#ef4444"   # red-500
STRENGTH_FAIR      = "#f97316"   # orange-500
STRENGTH_STRONG    = "#3b82f6"   # blue-500
STRENGTH_VERY_STRONG = "#22c55e" # green-500

STRENGTH_COLORS = {
    'Weak': STRENGTH_WEAK,
    'Fair': STRENGTH_FAIR,
    'Strong': STRENGTH_STRONG,
    'Very Strong': STRENGTH_VERY_STRONG,
}

STRENGTH_BG = {
    'Weak': '#451a1a',       # Dark red bg
    'Fair': '#432a10',       # Dark orange bg
    'Strong': '#1e3a5f',     # Dark blue bg
    'Very Strong': '#143d2a', # Dark green bg
}


class PasswordGeneratorApp:
    """Main application window for the password generator."""

    def __init__(self, root):
        """
        Initialize the application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("720x640")
        self.root.minsize(600, 520)
        self.root.configure(bg=BG_MAIN)

        # Initialize generator
        self.generator = PasswordGenerator()

        # Configure style
        self.setup_styles()

        # Create UI
        self.create_widgets()

        # Bind keyboard shortcuts
        self.root.bind('<Return>', lambda e: self.generate_password())
        self.root.bind('<Control-g>', lambda e: self.generate_password())
        self.root.bind('<Control-c>', lambda e: self.copy_to_clipboard())

        # Set focus to length entry
        self.length_entry.focus()

    # ─── Styling ─────────────────────────────────────────────────────────
    def setup_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use('clam')

        # Base frame styles
        style.configure('TFrame', background=BG_MAIN)
        style.configure('Card.TFrame', background=BG_CARD, borderwidth=1, relief='solid')

        # Label styles
        style.configure('TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=('Segoe UI', 10))
        style.configure('Card.TLabel', background=BG_CARD, foreground=TEXT_PRIMARY, font=('Segoe UI', 10))
        style.configure('Muted.TLabel', background=BG_MAIN, foreground=TEXT_SECONDARY, font=('Segoe UI', 9))
        style.configure('Card.Muted.TLabel', background=BG_CARD, foreground=TEXT_SECONDARY, font=('Segoe UI', 9))
        style.configure('Title.TLabel', background=BG_MAIN, foreground=TEXT_PRIMARY, font=('Segoe UI', 26, 'bold'))
        style.configure('SectionTitle.TLabel', background=BG_CARD, foreground=TEXT_MUTED, font=('Segoe UI', 8, 'bold'))

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

        # Spinbox styles (for length selector)
        style.configure('Dark.TSpinbox',
                       fieldbackground=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       background=BG_CARD,
                       arrowcolor=TEXT_SECONDARY,
                       bordercolor=BORDER,
                       lightcolor=BORDER,
                       darkcolor=BORDER,
                       borderwidth=1,
                       font=('Segoe UI', 11))
        style.map('Dark.TSpinbox',
                  fieldbackground=[('readonly', BG_INPUT)],
                  bordercolor=[('focus', ACCENT)],
                  arrowcolor=[('focus', ACCENT)])

        # Checkbutton styles
        style.configure('Dark.TCheckbutton',
                       background=BG_CARD,
                       foreground=TEXT_PRIMARY,
                       font=('Segoe UI', 10),
                       indicatorcolor=BG_INPUT,
                       indicatormargin=4)
        style.map('Dark.TCheckbutton',
                  background=[('active', BG_CARD)],
                  foreground=[('active', TEXT_PRIMARY)],
                  indicatorcolor=[('selected', ACCENT), ('!selected', BG_INPUT)])

        # Button styles
        style.configure('Primary.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       padding=(28, 14),
                       background=ACCENT,
                       foreground=TEXT_ON_ACCENT,
                       borderwidth=0,
                       focusthickness=0)
        style.map('Primary.TButton',
                  background=[('active', ACCENT_DIM), ('pressed', ACCENT_DIM)],
                  foreground=[('active', TEXT_ON_ACCENT), ('pressed', TEXT_ON_ACCENT)])

        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       padding=(18, 8),
                       background=BG_INPUT,
                       foreground=TEXT_PRIMARY,
                       borderwidth=1,
                       bordercolor=BORDER)
        style.map('Secondary.TButton',
                  background=[('active', BG_HOVER), ('pressed', BG_HOVER)],
                  foreground=[('active', ACCENT), ('pressed', ACCENT)],
                  bordercolor=[('active', BORDER_ACCENT)])

        style.configure('Ghost.TButton',
                       font=('Segoe UI', 10),
                       padding=(14, 6),
                       background=BG_CARD,
                       foreground=TEXT_SECONDARY,
                       borderwidth=1,
                       bordercolor=BORDER)
        style.map('Ghost.TButton',
                  background=[('active', BG_HOVER), ('pressed', BG_HOVER)],
                  foreground=[('active', ACCENT), ('pressed', ACCENT)],
                  bordercolor=[('active', BORDER_ACCENT)])

        # Scrollbar
        style.configure('Vertical.TScrollbar', background=BG_CARD, troughcolor=BG_MAIN, bordercolor=BG_MAIN, arrowcolor=TEXT_SECONDARY, width=10)

    # ─── Helper methods for custom widgets ───────────────────────────────
    def _card(self, parent, padding=(16, 8)):
        """Create a premium card frame with subtle border and hover effect."""
        frame = tk.Frame(
            parent,
            bg=BG_CARD,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=padding[0],
            pady=padding[1],
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

    def _modern_spinbox(self, parent, from_, to, textvariable, width=8, **kwargs):
        """Create a modern styled spinbox widget."""
        spinbox = ttk.Spinbox(
            parent,
            from_=from_,
            to=to,
            textvariable=textvariable,
            width=width,
            style='Dark.TSpinbox',
            font=("Segoe UI", 11),
            **kwargs,
        )
        return spinbox

    def _modern_checkbutton(self, parent, text, variable, **kwargs):
        """Create a modern styled checkbutton widget."""
        cb = ttk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            style='Dark.TCheckbutton',
            **kwargs,
        )
        return cb

    # ─── UI Sections ─────────────────────────────────────────────────────
    def create_widgets(self):
        """Create and layout all UI widgets with scrollable, centered layout."""
        # ─── Root grid config ────────────────────────────────────────────
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ─── Scrollable canvas ───────────────────────────────────────────
        self.canvas = tk.Canvas(self.root, bg=BG_MAIN, highlightthickness=0)
        self.vscroll = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview, style='Vertical.TScrollbar')
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vscroll.grid(row=0, column=1, sticky="ns")

        # ─── Content frame (inside canvas) ───────────────────────────────
        self.content = tk.Frame(self.canvas, bg=BG_MAIN)
        self.content_id = self.canvas.create_window((0, 0), window=self.content, anchor="n")

        # Centered container with max width
        self.container = tk.Frame(self.content, bg=BG_MAIN)
        self.container.pack(expand=True, fill='both', padx=24, pady=16)
        self.container.columnconfigure(0, weight=1)

        # Track content width for centering
        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # ─── Build sections inside container ─────────────────────────────
        row = 0

        # Header
        self._build_header(self.container, row); row += 1

        # Length selector
        self._build_length_section(self.container, row); row += 1

        # Categories
        self._build_categories_section(self.container, row); row += 1

        # Options
        self._build_options_section(self.container, row); row += 1

        # Generate button
        self._build_generate_button(self.container, row); row += 1

        # Password output
        self._build_password_section(self.container, row); row += 1

        # Strength meter
        self._build_strength_section(self.container, row); row += 1

        # Shortcuts hint
        self._build_shortcuts(self.container, row); row += 1

        # Make container rows expand minimally
        for i in range(row):
            self.container.rowconfigure(i, weight=0)

    def _on_content_configure(self, event):
        """Update scroll region when content changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Center content horizontally when canvas resizes."""
        canvas_width = event.width
        # Max content width ~950px (cards) + 48px padding = ~998px
        max_content_width = 950
        content_width = min(canvas_width, max_content_width)
        self.canvas.itemconfig(self.content_id, width=content_width)

    # ─── Section Builders ────────────────────────────────────────────────
    def _build_header(self, parent, row):
        """Build header with accent line, centered."""
        frame = tk.Frame(parent, bg=BG_MAIN)
        frame.grid(row=row, column=0, sticky='ew', pady=(0, 12))
        frame.columnconfigure(0, weight=1)

        # Accent line
        accent_line = tk.Frame(frame, bg=ACCENT, height=3)
        accent_line.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        title = tk.Label(frame, text="Password Generator",
                        font=('Segoe UI', 28, 'bold'), bg=BG_MAIN, fg=TEXT_PRIMARY)
        title.grid(row=1, column=0, sticky='w')

        subtitle = tk.Label(frame, text="Secure  •  Customizable  •  Strength Analyzed",
                           font=('Segoe UI', 11), bg=BG_MAIN, fg=TEXT_SECONDARY)
        subtitle.grid(row=2, column=0, sticky='w', pady=(4, 0))

    def _build_length_section(self, parent, row):
        """Build length selector card with better alignment."""
        card = self._card(parent, padding=(20, 14))
        card.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        card.columnconfigure(0, weight=1)

        # Section title
        title_bar = tk.Frame(card, bg=BG_CARD)
        title_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self._section_title(title_bar, "Password Length").pack(anchor='w')

        # Selector row
        sel_row = tk.Frame(card, bg=BG_CARD)
        sel_row.grid(row=1, column=0, sticky='ew')

        label = tk.Label(sel_row,
                text=f"Length ({self.generator.MIN_LENGTH}–{self.generator.MAX_LENGTH}):",
                font=('Segoe UI', 11), bg=BG_CARD, fg=TEXT_PRIMARY)
        label.pack(side='left', padx=(0, 16))

        self.length_var = tk.StringVar(value="16")
        self.length_entry = self._modern_spinbox(
            sel_row,
            from_=self.generator.MIN_LENGTH,
            to=self.generator.MAX_LENGTH,
            textvariable=self.length_var,
            width=10
        )
        self.length_entry.pack(side='left')

    def _build_categories_section(self, parent, row):
        """Build clean 2x2 categories grid with proper spacing."""
        card = self._card(parent, padding=(20, 14))
        card.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        card.columnconfigure(0, weight=1)

        title_bar = tk.Frame(card, bg=BG_CARD)
        title_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self._section_title(title_bar, "Character Categories").pack(anchor='w')

        cat_grid = tk.Frame(card, bg=BG_CARD)
        cat_grid.grid(row=1, column=0, sticky='ew')
        cat_grid.columnconfigure(0, weight=1)
        cat_grid.columnconfigure(1, weight=1)

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        # Row 0 - increased padding and spacing
        self._modern_checkbutton(cat_grid, "Uppercase (A–Z)", self.uppercase_var).grid(row=0, column=0, sticky='w', pady=6, padx=(0, 20))
        self._modern_checkbutton(cat_grid, "Lowercase (a–z)", self.lowercase_var).grid(row=0, column=1, sticky='w', pady=6)

        # Row 1
        self._modern_checkbutton(cat_grid, "Digits (0–9)", self.digits_var).grid(row=1, column=0, sticky='w', pady=6, padx=(0, 20))
        self._modern_checkbutton(cat_grid, "Special (!@#$%^&*)", self.special_var).grid(row=1, column=1, sticky='w', pady=6)

    def _build_options_section(self, parent, row):
        """Build options card with better spacing."""
        card = self._card(parent, padding=(20, 14))
        card.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        card.columnconfigure(0, weight=1)

        title_bar = tk.Frame(card, bg=BG_CARD)
        title_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self._section_title(title_bar, "Options").pack(anchor='w')

        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        self._modern_checkbutton(card, "Exclude ambiguous characters (O, 0, l, 1)", self.exclude_ambiguous_var).grid(row=1, column=0, sticky='w', pady=2)

    def _build_generate_button(self, parent, row):
        """Build prominent generate button."""
        btn = ttk.Button(
            parent,
            text="⚡  Generate Password",
            style='Primary.TButton',
            command=self.generate_password
        )
        btn.grid(row=row, column=0, sticky='ew', pady=(8, 16))

    def _build_password_section(self, parent, row):
        """Build password output with copy/clear buttons - polished."""
        card = self._card(parent, padding=(20, 14))
        card.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        card.columnconfigure(0, weight=1)

        title_bar = tk.Frame(card, bg=BG_CARD)
        title_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self._section_title(title_bar, "Generated Password").pack(anchor='w')

        # Password display
        pw_frame = tk.Frame(card, bg=BG_CARD)
        pw_frame.grid(row=1, column=0, sticky='ew', pady=(0, 12))
        pw_frame.columnconfigure(0, weight=1)

        self.password_text = tk.Text(
            pw_frame,
            height=1,
            wrap=tk.NONE,
            font=('JetBrains Mono', 14) if self._font_exists('JetBrains Mono') else ('Consolas', 14),
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            padx=16,
            pady=12,
        )
        self.password_text.grid(row=0, column=0, sticky='ew')
        self.password_text.bind('<Control-a>', lambda e: self._select_all_password())

        # Buttons row
        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.grid(row=2, column=0, sticky='ew')

        copy_btn = ttk.Button(
            btn_row,
            text="📋  Copy to Clipboard",
            style='Secondary.TButton',
            command=self.copy_to_clipboard
        )
        copy_btn.pack(side='left', padx=(0, 10))

        clear_btn = ttk.Button(
            btn_row,
            text="Clear",
            style='Ghost.TButton',
            command=self.clear_password
        )
        clear_btn.pack(side='left')

    def _build_strength_section(self, parent, row):
        """Build visually polished strength meter."""
        card = self._card(parent, padding=(20, 14))
        card.grid(row=row, column=0, sticky='ew', pady=(0, 10))
        card.columnconfigure(0, weight=1)

        title_bar = tk.Frame(card, bg=BG_CARD)
        title_bar.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self._section_title(title_bar, "Password Strength").pack(anchor='w')

        # Strength badge
        str_row = tk.Frame(card, bg=BG_CARD)
        str_row.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        self.strength_badge = tk.Label(
            str_row,
            text="  No password generated yet  ",
            font=('Segoe UI', 12, 'bold'),
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            padx=18,
            pady=10,
        )
        self.strength_badge.pack(side='left')

        self.strength_score = tk.Label(
            str_row,
            text="",
            font=('Segoe UI', 11),
            bg=BG_CARD,
            fg=TEXT_MUTED,
        )
        self.strength_score.pack(side='left', padx=(16, 0))

        # Progress bar visual
        self.strength_bar_bg = tk.Frame(card, bg=BG_INPUT, height=6)
        self.strength_bar_bg.grid(row=2, column=0, sticky='ew', pady=(0, 8))
        self.strength_bar_bg.grid_propagate(False)
        self.strength_bar_bg.columnconfigure(0, weight=1)

        self.strength_bar = tk.Frame(self.strength_bar_bg, bg=ACCENT, height=6)
        self.strength_bar.grid(row=0, column=0, sticky='w')
        self.strength_bar.grid_propagate(False)

        # Feedback
        self.feedback_label = tk.Label(
            card,
            text="",
            font=('Segoe UI', 10),
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            wraplength=850,
            justify='left',
            anchor='w'
        )
        self.feedback_label.grid(row=3, column=0, sticky='ew')

    def _build_shortcuts(self, parent, row):
        """Build shortcuts hint."""
        label = tk.Label(
            parent,
            text="Enter / Ctrl+G = Generate    |    Ctrl+C = Copy    |    Ctrl+A = Select All",
            font=('Segoe UI', 9), bg=BG_MAIN, fg=TEXT_MUTED
        )
        label.grid(row=row, column=0, pady=(12, 0))

    def _font_exists(self, font_name):
        """Check if a font is available."""
        try:
            import tkinter.font as tkfont
            return font_name in tkfont.families()
        except:
            return False

    def _select_all_password(self):
        """Select all text in password field."""
        self.password_text.tag_add('sel', '1.0', 'end')
        return 'break'

    # ─── Logic (preserved) ───────────────────────────────────────────────
    def generate_password(self):
        """Generate a new password based on user selections."""
        try:
            # Get length
            try:
                length = int(self.length_var.get())
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid number for password length."
                )
                self.length_entry.focus()
                return

            # Get category selections
            use_uppercase = self.uppercase_var.get()
            use_lowercase = self.lowercase_var.get()
            use_digits = self.digits_var.get()
            use_special = self.special_var.get()
            exclude_ambiguous = self.exclude_ambiguous_var.get()

            # Generate password
            password = self.generator.generate(
                length=length,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_digits=use_digits,
                use_special=use_special,
                exclude_ambiguous=exclude_ambiguous
            )

            # Display password
            self.password_text.delete(1.0, tk.END)
            self.password_text.insert(1.0, password)

            # Estimate and display strength
            strength = self.generator.estimate_strength(
                password,
                use_uppercase=use_uppercase,
                use_lowercase=use_lowercase,
                use_digits=use_digits,
                use_special=use_special
            )

            # Update strength display with premium styling
            level = strength['level']
            score = strength['score']
            color = STRENGTH_COLORS.get(level, TEXT_SECONDARY)
            bg_color = STRENGTH_BG.get(level, BG_CARD)

            self.strength_badge.config(text=f"  {level}  ", fg=color, bg=bg_color)
            self.strength_score.config(text=f"Score: {score}/100", fg=color)

            # Update visual progress bar
            bar_width = int((score / 100) * 850)
            self.strength_bar.config(width=max(bar_width, 1), bg=color)

            self.feedback_label.config(text=strength['feedback'])

            # Show success toast (non-blocking) instead of modal dialog
            self._show_toast(f"Generated {len(password)}-character password — {level}")

        except InvalidLengthError as e:
            messagebox.showerror("Invalid Length", str(e))
            self.length_entry.focus()

        except NoCharactersSelectedError as e:
            messagebox.showerror("No Characters Selected", str(e))

        except PasswordGeneratorError as e:
            messagebox.showerror("Generation Error", str(e))

        except Exception as e:
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n{str(e)}"
            )

    def _show_toast(self, message):
        """Show a brief non-blocking toast notification."""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        toast.configure(bg=BG_CARD, highlightthickness=1, highlightbackground=ACCENT)

        # Position near bottom-right of main window
        self.root.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + self.root.winfo_height() - 80
        toast.geometry(f"300x50+{x}+{y}")

        label = tk.Label(
            toast,
            text=message,
            font=('Segoe UI', 9),
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            padx=16,
            pady=12
        )
        label.pack()

        # Auto-dismiss after 2 seconds
        toast.after(2000, toast.destroy)

    def copy_to_clipboard(self):
        """Copy the generated password to clipboard."""
        password = self.password_text.get(1.0, tk.END).strip()

        if not password:
            messagebox.showwarning(
                "No Password",
                "Please generate a password first."
            )
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()  # Keep clipboard content

            self._show_toast("Password copied to clipboard!")

        except Exception as e:
            messagebox.showerror(
                "Copy Failed",
                f"Failed to copy to clipboard:\n{str(e)}"
            )

    def clear_password(self):
        """Clear the generated password and reset strength display."""
        self.password_text.delete(1.0, tk.END)
        self.strength_badge.config(
            text="  No password generated yet  ",
            bg=BG_CARD,
            fg=TEXT_SECONDARY
        )
        self.strength_score.config(text="")
        self.strength_bar.config(width=1, bg=ACCENT)
        self.feedback_label.config(text="")

        # Optionally clear clipboard
        try:
            self.root.clipboard_clear()
        except:
            pass  # Clipboard clearing is optional


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()