"""
Random Password Generator - Tkinter GUI Application

A polished desktop interface for generating secure random passwords
with customizable options and strength feedback.
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


class PasswordGeneratorApp:
    """Main application window for the password generator."""

    def __init__(self, root):
        """
        Initialize the application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("600x550")
        self.root.resizable(False, False)

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

    def setup_styles(self):
        """Configure custom styles for widgets."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure button styles
        style.configure(
            'Generate.TButton',
            font=('Arial', 11, 'bold'),
            padding=10
        )

        style.configure(
            'Action.TButton',
            font=('Arial', 10),
            padding=6
        )

    def create_widgets(self):
        """Create and layout all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Random Password Generator",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Password length section
        length_frame = ttk.LabelFrame(main_frame, text="Password Length", padding="10")
        length_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(
            length_frame,
            text=f"Length ({self.generator.MIN_LENGTH}-{self.generator.MAX_LENGTH} characters):",
            font=('Arial', 10)
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.length_var = tk.StringVar(value="16")
        self.length_entry = ttk.Entry(
            length_frame,
            textvariable=self.length_var,
            width=10,
            font=('Arial', 10)
        )
        self.length_entry.grid(row=0, column=1, sticky=tk.W)

        # Character categories section
        categories_frame = ttk.LabelFrame(
            main_frame,
            text="Character Categories",
            padding="10"
        )
        categories_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.special_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            categories_frame,
            text="Uppercase Letters (A-Z)",
            variable=self.uppercase_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        ttk.Checkbutton(
            categories_frame,
            text="Lowercase Letters (a-z)",
            variable=self.lowercase_var
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        ttk.Checkbutton(
            categories_frame,
            text="Digits (0-9)",
            variable=self.digits_var
        ).grid(row=2, column=0, sticky=tk.W, pady=2)

        ttk.Checkbutton(
            categories_frame,
            text="Special Characters (!@#$%^&*...)",
            variable=self.special_var
        ).grid(row=3, column=0, sticky=tk.W, pady=2)

        # Options section
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Exclude ambiguous characters (O, 0, l, 1)",
            variable=self.exclude_ambiguous_var
        ).grid(row=0, column=0, sticky=tk.W)

        # Generate button
        generate_btn = ttk.Button(
            main_frame,
            text="Generate Password",
            command=self.generate_password,
            style='Generate.TButton'
        )
        generate_btn.grid(row=4, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))

        # Generated password section
        password_frame = ttk.LabelFrame(
            main_frame,
            text="Generated Password",
            padding="10"
        )
        password_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Password display with scrollbar
        password_container = ttk.Frame(password_frame)
        password_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.password_text = tk.Text(
            password_container,
            height=3,
            width=50,
            wrap=tk.WORD,
            font=('Courier New', 11),
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.password_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(
            password_container,
            orient=tk.VERTICAL,
            command=self.password_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.password_text.configure(yscrollcommand=scrollbar.set)

        # Action buttons
        button_frame = ttk.Frame(password_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            style='Action.TButton'
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_password,
            style='Action.TButton'
        ).grid(row=0, column=1, padx=5)

        # Strength indicator section
        strength_frame = ttk.LabelFrame(
            main_frame,
            text="Password Strength",
            padding="10"
        )
        strength_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.strength_label = ttk.Label(
            strength_frame,
            text="No password generated yet",
            font=('Arial', 10)
        )
        self.strength_label.grid(row=0, column=0, sticky=tk.W)

        self.feedback_label = ttk.Label(
            strength_frame,
            text="",
            font=('Arial', 9),
            foreground='gray'
        )
        self.feedback_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # Keyboard shortcuts info
        shortcuts_label = ttk.Label(
            main_frame,
            text="Shortcuts: Enter or Ctrl+G = Generate  |  Ctrl+C = Copy",
            font=('Arial', 8),
            foreground='gray'
        )
        shortcuts_label.grid(row=7, column=0, columnspan=2, pady=(10, 0))

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

            # Update strength display with color coding
            strength_colors = {
                'Weak': 'red',
                'Fair': 'orange',
                'Strong': 'blue',
                'Very Strong': 'green'
            }

            color = strength_colors.get(strength['level'], 'black')
            self.strength_label.config(
                text=f"Strength: {strength['level']} (Score: {strength['score']}/100)",
                foreground=color
            )
            self.feedback_label.config(
                text=f"Note: {strength['feedback']}"
            )

            # Show success message
            messagebox.showinfo(
                "Success",
                f"Password generated successfully!\n\n"
                f"Length: {len(password)} characters\n"
                f"Strength: {strength['level']}\n\n"
                f"Remember: This is an estimate, not a guarantee of security."
            )

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

            messagebox.showinfo(
                "Copied",
                "Password copied to clipboard!\n\n"
                "Security reminder: The clipboard may be accessible to other applications."
            )
        except Exception as e:
            messagebox.showerror(
                "Copy Failed",
                f"Failed to copy to clipboard:\n{str(e)}"
            )

    def clear_password(self):
        """Clear the generated password and reset strength display."""
        self.password_text.delete(1.0, tk.END)
        self.strength_label.config(
            text="No password generated yet",
            foreground='black'
        )
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
