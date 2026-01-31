import tkinter as tk
from ui.task_card import TaskCard

class KanbanColumn(tk.Frame):
    def __init__(self, parent, db, status, color, drag_start_cb, drag_end_cb):
        super().__init__(parent, bg=color, bd=1, relief="flat")
        self.db = db
        self.status = status
        self.drag_start_cb = drag_start_cb
        self.drag_end_cb = drag_end_cb
        
        # Initialize the cards list early to prevent AttributeError
        self.cards = [] 
        
        self.setup_ui(status, color)

    def setup_ui(self, status, color):
        # Column Header
        self.header = tk.Label(self, text=status, bg=color, font=("Arial", 12, "bold"), pady=10)
        self.header.pack(fill="x")

        # The Canvas acts as the scrollable viewport
        self.canvas = tk.Canvas(self, bg=color, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Inner frame that actually holds the TaskCards
        self.card_container = tk.Frame(self.canvas, bg=color)
        
        # Create a window inside the canvas to hold the card_container
        self.canvas_window = self.canvas.create_window((0, 0), window=self.card_container, 
                                               anchor="nw", width=220)

        # Configure the canvas to update its scroll region when cards are added
        self.card_container.bind("<Configure>", self.on_frame_configure)
        
        # Ensure the card_container stays the same width as the canvas
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind MouseWheel for the entire column area
        self.bind_mouse_wheel(self.canvas)
        self.bind_mouse_wheel(self.card_container)

    def on_frame_configure(self, event):
        """Update the scrollable area to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Force the inner frame to match the canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_wheel(self, widget):
        """Bind mouse wheel only to major containers to prevent event lag."""
        widget.bind("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        """Scroll the canvas vertically based on mouse wheel movement."""
        # Finds the specific canvas to scroll
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear_cards(self):
        """Remove all task cards from the column."""
        for card in self.cards:
            card.destroy()
        self.cards = []

    def add_task(self, task):
        # Create the card normally
        card = TaskCard(self.card_container, self.db, task, self.drag_start_cb, self.drag_end_cb)
        card.pack(fill="x", pady=5, padx=10)
        self.cards.append(card)
        
    def get_card_at_y(self, y_root):
        """Determine where to insert a dropped card based on Y coordinates."""
        container_y_root = self.card_container.winfo_rooty()
        relative_y = y_root - container_y_root
        
        cumulative_y = 0
        for i, card in enumerate(self.cards):
            card_height = card.winfo_height()
            if relative_y < cumulative_y + card_height / 2:
                return i 
            cumulative_y += card_height + 10 
            
        return len(self.cards)