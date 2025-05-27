import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

class TeleprompterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Teleprompter")
        self.root.geometry("350x400")
        
        self.root.overrideredirect(True)

        # Center the window at the top of the screen
        self.center_window_top()
        
        # Initialize variables
        self.is_edit_mode = True
        self.is_scrolling = False
        self.scroll_speed = 1.0
        self.font_size = 20
        self.scroll_thread = None
        
        # Set dark theme for the entire window
        self.setup_dark_theme()
        
        # Create the GUI
        self.create_widgets()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_dark_theme(self):
        """Configure dark theme for the entire application"""
        # Set main window background to dark
        self.root.configure(bg='#2b2b2b')
        
        # Configure ttk styles for dark theme
        style = ttk.Style()
        
        # Configure dark theme colors
        style.theme_use('clam')  # Use clam theme as base
        
        # Configure styles for different widgets
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
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        window_width = 350
        x = (screen_width - window_width) // 2
        y = 0  # Position at absolute top of screen
        self.root.geometry(f"{window_width}x400+{x}+{y}")
    
    def create_widgets(self):
        """Create and setup all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights - text area gets most space
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)  # Text area row gets weight
        
        # Text area frame - now at the top (row 0)
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text widget (edit mode)
        self.text_edit = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", self.font_size),
            height=15
        )
        self.text_edit.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text widget (display mode) - initially hidden
        self.text_display = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", self.font_size, "bold"),
            bg="black",
            fg="white",
            height=15,
            cursor="none"
        )
        
        # Sample text
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
        
        # Mode toggle frame - now in the middle (row 1)
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Edit/Display mode toggle
        self.mode_var = tk.StringVar(value="Edit")
        self.mode_button = ttk.Button(
            mode_frame, 
            text="Display Mode", 
            command=self.toggle_mode,
            width=15
        )
        self.mode_button.pack(side=tk.LEFT)
        
        # Start/Stop scrolling button (only visible in display mode)
        self.scroll_button = ttk.Button(
            mode_frame,
            text="Start Scrolling",
            command=self.toggle_scrolling,
            width=15
        )
        
        # Controls frame - now at the bottom (row 2)
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
        ttk.Label(controls_frame, text="Scroll Speed:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        self.speed_scale = ttk.Scale(
            controls_frame,
            from_=0.1,
            to=5.0,
            orient=tk.HORIZONTAL,
            value=self.scroll_speed,
            command=self.update_scroll_speed
        )
        self.speed_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        self.speed_label = ttk.Label(controls_frame, text=f"{self.scroll_speed:.1f}x")
        self.speed_label.grid(row=1, column=2, padx=(0, 20), pady=(10, 0))
        
        # Close button frame - at the very bottom (row 3)
        close_frame = ttk.Frame(main_frame)
        close_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Close button
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
            
            # Always copy text from edit to display when switching to display mode
            content = self.text_edit.get(1.0, tk.END)
            self.text_display.config(state=tk.NORMAL)  # Enable temporarily to update content
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, content)
            self.text_display.config(state=tk.DISABLED)  # Disable again
            
            # Hide edit widget, show display widget
            self.text_edit.grid_remove()
            self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Show scroll button
            self.scroll_button.pack(side=tk.RIGHT)
            
        else:
            # Switch to Edit mode
            self.is_edit_mode = True
            self.mode_button.config(text="Display Mode")
            
            # Stop scrolling if active
            if self.is_scrolling:
                self.toggle_scrolling()
            
            # Don't copy text back from display to edit - keep edit content intact
            # This prevents overwriting user edits with old display content
            
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
        """Start the scrolling thread"""
        if self.scroll_thread and self.scroll_thread.is_alive():
            return
        
        self.scroll_thread = threading.Thread(target=self.scroll_text, daemon=True)
        self.scroll_thread.start()
    
    def scroll_text(self):
        """Auto-scroll the text in display mode"""
        while self.is_scrolling and not self.is_edit_mode:
            try:
                # Enable text widget temporarily to scroll
                self.text_display.config(state=tk.NORMAL)
                
                # Get current position
                current_pos = self.text_display.yview()[0]
                
                # Fixed scroll increment - always use a base increment that works
                # The speed control affects timing, not increment size
                base_increment = 0.002  # Larger base increment for visibility
                self.text_display.yview_moveto(current_pos + base_increment)
                
                # Check if we've reached the end
                if self.text_display.yview()[1] >= 1.0:
                    self.is_scrolling = False
                    self.root.after(0, lambda: self.scroll_button.config(text="Start Scrolling"))
                
                # Disable editing again
                self.text_display.config(state=tk.DISABLED)
                
                # Fixed sleep calculation - inverse relationship with speed
                # Speed 0.1 = very slow (sleep 0.5s), Speed 1.0 = normal (sleep 0.05s), Speed 5.0 = fast (sleep 0.01s)
                base_sleep = 0.05
                if self.scroll_speed >= 1.0:
                    sleep_time = base_sleep / self.scroll_speed
                else:
                    # For speeds < 1.0, increase sleep time proportionally
                    sleep_time = base_sleep * (1.0 / self.scroll_speed)
                
                time.sleep(sleep_time)
                
            except tk.TclError:
                # Widget was destroyed
                break
    
    def update_font_size(self, value):
        """Update font size for both text widgets"""
        self.font_size = int(float(value))
        self.font_label.config(text=str(self.font_size))
        
        # Update fonts
        edit_font = ("Arial", self.font_size)
        display_font = ("Arial", self.font_size, "bold")
        
        self.text_edit.config(font=edit_font)
        self.text_display.config(font=display_font)
    
    def update_scroll_speed(self, value):
        """Update scroll speed"""
        self.scroll_speed = float(value)
        self.speed_label.config(text=f"{self.scroll_speed:.1f}x")
    
    def on_closing(self):
        """Handle application closing"""
        self.is_scrolling = False
        if self.scroll_thread and self.scroll_thread.is_alive():
            self.scroll_thread.join(timeout=1.0)
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TeleprompterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
