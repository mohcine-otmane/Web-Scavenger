import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
from WebScavanger import WebScavanger
import os

class WebScavangerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scavenger")
        self.root.geometry("800x600")
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=5)
        style.configure("TLabel", padding=5)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Search query
        ttk.Label(main_frame, text="Search Query:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(main_frame, textvariable=self.query_var, width=50)
        self.query_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Number of pages
        ttk.Label(main_frame, text="Number of Pages:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pages_var = tk.StringVar(value="3")
        self.pages_entry = ttk.Entry(main_frame, textvariable=self.pages_var, width=10)
        self.pages_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="Start Search", command=self.start_search)
        self.search_button.grid(row=1, column=2, sticky=tk.E, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Results text area
        ttk.Label(main_frame, text="Results:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=80, height=20)
        self.results_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure root grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Bind Enter key to search
        self.query_entry.bind('<Return>', lambda e: self.start_search())
        self.pages_entry.bind('<Return>', lambda e: self.start_search())
        
    def start_search(self):
        query = self.query_var.get().strip()
        try:
            pages = int(self.pages_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of pages")
            return
            
        if not query:
            messagebox.showerror("Error", "Please enter a search query")
            return
            
        # Disable inputs during search
        self.query_entry.config(state='disabled')
        self.pages_entry.config(state='disabled')
        self.search_button.config(state='disabled')
        self.results_text.delete(1.0, tk.END)
        self.status_var.set("Searching...")
        self.progress_var.set(0)
        
        # Start search in a separate thread
        thread = threading.Thread(target=self.search_thread, args=(query, pages))
        thread.daemon = True
        thread.start()
        
    def search_thread(self, query, pages):
        try:
            # Create WebScavanger instance
            scraper = WebScavanger()
            
            # Override the print function to update GUI
            def gui_print(*args, **kwargs):
                text = ' '.join(map(str, args))
                self.results_text.insert(tk.END, text + '\n')
                self.results_text.see(tk.END)
                self.root.update_idletasks()
            
            # Replace print function
            original_print = print
            import builtins
            builtins.print = gui_print
            
            # Run the search
            scraper.search(query, pages)
            
            # Restore original print function
            builtins.print = original_print
            
            # Update GUI
            self.root.after(0, self.search_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.search_error(str(e)))
            
    def search_complete(self):
        # Re-enable inputs
        self.query_entry.config(state='normal')
        self.pages_entry.config(state='normal')
        self.search_button.config(state='normal')
        self.status_var.set("Search completed")
        self.progress_var.set(100)
        
        # Show results file location
        if os.path.exists('webscavanger_results.json'):
            messagebox.showinfo("Success", "Search completed! Results saved to webscavanger_results.json")
            
    def search_error(self, error_message):
        # Re-enable inputs
        self.query_entry.config(state='normal')
        self.pages_entry.config(state='normal')
        self.search_button.config(state='normal')
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", f"An error occurred: {error_message}")

def main():
    root = tk.Tk()
    app = WebScavangerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 