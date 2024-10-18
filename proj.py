import customtkinter as ctk
import pyperclip
from pynput import keyboard
import threading
import time
from datetime import datetime
from CTkListbox import *

class ModernClipboardManager:
    def __init__(self):
        self.clipboard_history = []
        self.max_history = 20
        self.last_copy_time = 0
        self.duplicate_timeout = 0.5
        self.removing_item = False
        
        # Set theme and color
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_gui()

    def setup_gui(self):
        self.root = ctk.CTk()
        self.root.title("Modern Clipboard Manager")
        self.root.geometry("500x600")
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Clipboard History", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=ctk.CTkFont(size=16))
        search_icon.pack(side="left", padx=5)
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search clips...",
            textvariable=self.search_var,
            height=35
        )
        self.search_entry.pack(fill="x", expand=True, padx=5)
        self.search_var.trace('w', self.filter_list)
        
        # Clipboard list
        self.clip_list = CTkListbox(
            main_frame, 
            height=300,
            command=self.on_item_select,
            hover_color=("gray70", "gray30"),
            border_width=2,
            font=ctk.CTkFont(size=13)
        )
        self.clip_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame, 
            text="Clear History",
            command=self.clear_history,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "gray90")
        )
        clear_btn.pack(side="left", padx=5)

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        status_label = ctk.CTkLabel(
            main_frame, 
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=5)
        
        # Hotkey info
        hotkey_label = ctk.CTkLabel(
            main_frame, 
            text="Press Ctrl+Shift+H to show/hide",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        hotkey_label.pack(pady=5)
        
        # Start monitoring
        self.root.after(100, self.monitor_clipboard)
        
        # Start keyboard listener
        self.keyboard_thread = threading.Thread(target=self.start_global_hotkeys, daemon=True)
        self.keyboard_thread.start()

    def monitor_clipboard(self):
        try:
            current_content = pyperclip.paste()
            current_time = time.time()

            if not self.removing_item:  # Only monitor if not removing an item
                # Check if the current content is different from the last entry and not already in history
                if (not self.clipboard_history or 
                    current_content != self.clipboard_history[-1]['content']):
                    if current_time - self.last_copy_time >= self.duplicate_timeout:
                        # Check if the content already exists in history
                        if not any(item['content'] == current_content for item in self.clipboard_history):
                            self.clipboard_history.append({
                                'content': current_content,
                                'time': datetime.now().strftime("%H:%M:%S")
                            })
                            if len(self.clipboard_history) > self.max_history:
                                self.clipboard_history.pop(0)
                            self.update_list()
                            self.last_copy_time = current_time
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
        finally:
            self.root.after(100, self.monitor_clipboard)

    def update_list(self):
        self.clip_list.delete(0, "end")
        for item in reversed(self.clipboard_history):
            content_preview = f"{item['time']} | {item['content'][:50]}"
            if len(item['content']) > 50:
                content_preview += "..."
            self.clip_list.insert("end", content_preview)

    def filter_list(self, *args):
        search_term = self.search_var.get().lower()
        self.clip_list.delete(0, "end")
        
        for item in reversed(self.clipboard_history):
            if search_term in item['content'].lower():
                content_preview = f"{item['time']} | {item['content'][:50]}"
                if len(item['content']) > 50:
                    content_preview += "..."
                self.clip_list.insert("end", content_preview)

    def on_item_select(self, selected_item):
        if selected_item:
            index = self.clip_list.curselection()
            if index is not None:
                self.paste_from_history(len(self.clipboard_history) - 1 - index)

    def paste_from_history(self, index):
        if 0 <= index < len(self.clipboard_history):
            item_to_copy = self.clipboard_history[index]['content']
            current_clipboard = pyperclip.paste()
            
            if item_to_copy != current_clipboard:
                pyperclip.copy(item_to_copy)
                self.status_var.set(f"Copied: {item_to_copy[:30]}...")
            else:
                self.status_var.set("Item already in clipboard")

    def clear_history(self):
        self.clipboard_history.clear()  # Clear the application's history
        pyperclip.copy("")  # Clear the clipboard by copying an empty string
        self.update_list()  # Update the list display
        self.status_var.set("History cleared")

    def start_global_hotkeys(self):
        def on_activate_h():
            if self.root.state() == 'withdrawn':
                self.root.deiconify()
                self.root.lift()
            else:
                self.root.withdraw()
        
        with keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+h': on_activate_h,
        }) as listener:
            listener.join()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    manager = ModernClipboardManager()
    manager.run()


