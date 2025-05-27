import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

class TeleprompterApp:
    def __init__(self, root):
        # Store the root Tkinter window
        self.root = root
        self.root.title("Teleprompter")  # Set window title
        self.root.geometry("350x400")    # Set initial window size
        
        # Remove window decorations (border, title bar) for a clean look
        self.root.overrideredirect(True)
        # Keep the window always on top of other windows
        self.root.attributes('-topmost', True)

        # Enable window dragging by tracking mouse events
        self.offset_x = 0
        self.offset_y = 0
        self.root.bind('<Button-1>', self.start_move)      # Start drag
        self.root.bind('<B1-Motion>', self.do_move)        # Dragging motion

        # Center the window at the top of the screen
        self.center_window_top()
        
        # Initialize state variables
        self.is_edit_mode = True         # True: edit mode, False: display mode
        self.is_scrolling = False        # True if auto-scrolling is active
        self.scroll_speed = 1.0          # Scrolling speed multiplier
        self.font_size = 20              # Default font size
        self.scroll_thread = None        # Thread for auto-scrolling
        
        # Apply dark theme to the window and widgets
        self.setup_dark_theme()
        
        # Build all GUI widgets
        self.create_widgets()
        
        # Bind the window close event to custom handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_dark_theme(self):
        """Configure dark theme for the entire application"""
        # Set main window background to dark
        self.root.configure(bg='#2b2b2b')
        
        # Configure ttk styles for dark theme
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base
        
        # Set background and foreground colors for various widgets
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', 
                       background='#404040', 
                       foreground='#ffffff',
                       borderwidth=1,
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', '#505050'), ('pressed', '#606060')])
        
        style.configure('TScale',
                       background='#2b2b2b',
                       troughcolor='#404040',
                       borderwidth=0,
                       lightcolor='#2b2b2b',
                       darkcolor='#2b2b2b')

    def center_window_top(self):
        """Position window at center-top of screen"""
        self.root.update_idletasks()  # Ensure geometry info is updated
        screen_width = self.root.winfo_screenwidth()
        window_width = 350
        x = (screen_width - window_width) // 2  # Center horizontally
        y = 0  # Position at absolute top
        self.root.geometry(f"{window_width}x400+{x}+{y}")
    
    def create_widgets(self):
        """Create and setup all GUI widgets"""
        # Main container frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights so text area expands with window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Text area frame at the top
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text widget for editing (edit mode)
        self.text_edit = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", self.font_size),
            height=15
        )
        self.text_edit.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text widget for display mode (read-only, styled)
        self.text_display = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", self.font_size, "bold"),
            bg="black",
            fg="white",
            height=15,
            cursor="none"
        )
        
        # Insert sample text for demonstration
        sample_text = """Welcome to the Teleprompter!

This is your teleprompter application. You can:

- Toggle between Edit and Display modes
- Adjust font size using the controls below
- Control scroll speed in Display mode
- Start and stop scrolling as needed

In Edit mode, you can type or paste your script. 

In Display mode, the text will be displayed with white text on a black background for better visibility during recording or presentation.

Use the controls at the bottom to customize your experience. The font size can be adjusted from 8 to 72 points, and scroll speed can be set from very slow to very fast.

Happy presenting!"""
        self.text_edit.insert(tk.END, sample_text)
        
        # Frame for mode toggle and scroll button
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Button to toggle between Edit and Display modes
        self.mode_var = tk.StringVar(value="Edit")
        self.mode_button = ttk.Button(
            mode_frame, 
            text="Display Mode", 
            command=self.toggle_mode,
            width=15
        )
        self.mode_button.pack(side=tk.LEFT)
        
        # Button to start/stop scrolling (only visible in display mode)
        self.scroll_button = ttk.Button(
            mode_frame,
            text="Start Scrolling",
            command=self.toggle_scrolling,
            width=15
        )
        
        # Controls frame for font size and scroll speed
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(3, weight=1)
        
        # Font size controls
        ttk.Label(controls_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.font_scale = ttk.Scale(
            controls_frame,
            from_=8,
            to=72,
            orient=tk.HORIZONTAL,
            value=self.font_size,
            command=self.update_font_size
        )
        self.font_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.font_label = ttk.Label(controls_frame, text=str(self.font_size))
        self.font_label.grid(row=0, column=2, padx=(0, 20))
        
        # Scroll speed controls
        # Label for scroll speed
        ttk.Label(controls_frame, text="Scroll Speed:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        # Scale widget for adjusting scroll speed (0.1x to 5.0x)
        self.speed_scale = ttk.Scale(
            controls_frame,
            from_=0.1,
            to=5.0,
            orient=tk.HORIZONTAL,
            value=self.scroll_speed,
            command=self.update_scroll_speed  # Updates speed when slider is moved
        )
        self.speed_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        # Entry widget for direct input of scroll speed (editable)
        self.speed_var = tk.StringVar(value=f"{self.scroll_speed:.1f}")  # Holds the speed value as string
        self.speed_entry = ttk.Entry(controls_frame, textvariable=self.speed_var, width=5)
        self.speed_entry.grid(row=1, column=2, padx=(0, 20), pady=(10, 0))
        # Bind Enter key and focus-out event to update speed from entry
        self.speed_entry.bind('<Return>', self.set_speed_from_entry)
        self.speed_entry.bind('<FocusOut>', self.set_speed_from_entry)
        
        # Close button frame at the bottom
        close_frame = ttk.Frame(main_frame)
        close_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Button to close the application
        self.close_button = ttk.Button(
            close_frame,
            text="Close",
            command=self.on_closing,
            width=10
        )
        self.close_button.pack(side=tk.RIGHT)
    
    def toggle_mode(self):
        """Toggle between Edit and Display modes"""
        if self.is_edit_mode:
            # Switch to Display mode
            self.is_edit_mode = False
            self.mode_button.config(text="Edit Mode")
            
            # Copy text from edit widget to display widget
            content = self.text_edit.get(1.0, tk.END)
            self.text_display.config(state=tk.NORMAL)  # Enable to update content
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, content)
            self.text_display.config(state=tk.DISABLED)  # Make read-only
            
            # Hide edit widget, show display widget
            self.text_edit.grid_remove()
            self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Show scroll button
            self.scroll_button.pack(side=tk.RIGHT)
            
        else:
            # Switch to Edit mode
            self.is_edit_mode = True
            self.mode_button.config(text="Display Mode")
            
            # Stop scrolling if it is active
            if self.is_scrolling:
                self.toggle_scrolling()
            
            # Do not copy text back from display to edit
            # Hide display widget, show edit widget
            self.text_display.grid_remove()
            self.text_edit.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Hide scroll button
            self.scroll_button.pack_forget()
    
    def toggle_scrolling(self):
        """Start or stop auto-scrolling"""
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_button.config(text="Stop Scrolling")
            self.start_scrolling()
        else:
            self.is_scrolling = False
            self.scroll_button.config(text="Start Scrolling")
    
    def start_scrolling(self):
        """Start the scrolling thread if not already running"""
        if self.scroll_thread and self.scroll_thread.is_alive():
            return
        self.scroll_thread = threading.Thread(target=self.scroll_text, daemon=True)
        self.scroll_thread.start()
    
    def scroll_text(self):
        """Auto-scroll the text in display mode using a thread"""
        while self.is_scrolling and not self.is_edit_mode:
            try:
                # Temporarily enable text widget to scroll
                self.text_display.config(state=tk.NORMAL)
                # Get current vertical position
                current_pos = self.text_display.yview()[0]
                # Scroll by a small increment
                base_increment = 0.002
                self.text_display.yview_moveto(current_pos + base_increment)
                # If reached the end, stop scrolling
                if self.text_display.yview()[1] >= 1.0:
                    self.is_scrolling = False
                    self.root.after(0, lambda: self.scroll_button.config(text="Start Scrolling"))
                # Disable editing again
                self.text_display.config(state=tk.DISABLED)
                # Calculate sleep time based on speed
                base_sleep = 0.05
                if self.scroll_speed >= 1.0:
                    sleep_time = base_sleep / self.scroll_speed
                else:
                    sleep_time = base_sleep * (1.0 / self.scroll_speed)
                time.sleep(sleep_time)
            except tk.TclError:
                # Widget was destroyed, exit thread
                break
    
    def update_font_size(self, value):
        """Update font size for both text widgets"""
        self.font_size = int(float(value))
        self.font_label.config(text=str(self.font_size))
        # Update font for edit and display widgets
        edit_font = ("Arial", self.font_size)
        display_font = ("Arial", self.font_size, "bold")
        self.text_edit.config(font=edit_font)
        self.text_display.config(font=display_font)
    
    def update_scroll_speed(self, value):
        """
        Update scroll speed multiplier from scale or entry.
        This method is called when the slider is moved. It updates the scroll_speed variable
        and also updates the entry box to reflect the new value.
        """
        self.scroll_speed = float(value)
        self.speed_var.set(f"{self.scroll_speed:.1f}")  # Keep entry in sync with slider
    
    def set_speed_from_entry(self, event=None):
        """
        Set scroll speed from the editable entry box.
        This method is called when the user presses Enter or leaves the entry box.
        It validates the input, clamps it to the allowed range, and updates the slider and scroll_speed.
        If the input is invalid, it resets the entry to the current scroll speed.
        """
        try:
            value = float(self.speed_var.get())
            if value < 0.1:
                value = 0.1
            elif value > 5.0:
                value = 5.0
            self.scroll_speed = value
            self.speed_scale.set(value)  # Update the slider to match entry
        except ValueError:
            # Reset to current scroll speed if invalid input
            self.speed_var.set(f"{self.scroll_speed:.1f}")
    
    def on_closing(self):
        """Handle application closing and cleanup"""
        self.is_scrolling = False
        if self.scroll_thread and self.scroll_thread.is_alive():
            self.scroll_thread.join(timeout=1.0)
        self.root.destroy()

    def start_move(self, event):
        """Record the offset of the mouse pointer from the window's top-left corner for dragging."""
        self.offset_x = event.x_root - self.root.winfo_x()
        self.offset_y = event.y_root - self.root.winfo_y()

    def do_move(self, event):
        """Move the window to the new position based on mouse drag."""
        new_x = event.x_root - self.offset_x
        new_y = event.y_root - self.offset_y
        self.root.geometry(f'+{new_x}+{new_y}')

def main():
    # Create the main Tkinter window and start the Teleprompter app
    root = tk.Tk()
    app = TeleprompterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
