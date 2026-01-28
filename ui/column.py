import tkinter as tk
from ui.task_card import TaskCard

class KanbanColumn(tk.Frame):
    def __init__(self, parent, db, status, color, drag_start_cb, drag_end_cb):
        super().__init__(parent, bg=color, bd=2, relief="sunken")
        self.db = db
        self.status = status
        self.drag_start_cb = drag_start_cb
        self.drag_end_cb = drag_end_cb
        
        # FIX: Initialize the cards list BEFORE anything else
        self.cards = [] 
        
        self.setup_ui(status, color)

    def setup_ui(self, status, color):
        header = tk.Label(self, text=status, bg=color, font=("Arial", 12, "bold"), pady=8)
        header.pack(fill="x")

        self.canvas = tk.Canvas(self, bg=color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.card_container = tk.Frame(self.canvas, bg=color)

        self.card_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.card_container, anchor="nw", width=250)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def clear_cards(self):
        for card in self.cards:
            card.destroy()
        self.cards = []

    def add_task(self, task):
        # Ensure self.db is passed here
        card = TaskCard(self.card_container, self.db, task, self.drag_start_cb, self.drag_end_cb)
        card.pack(fill="x", pady=5, padx=5)
        self.cards.append(card)

    def get_card_at_y(self, y_root):
        container_y_root = self.card_container.winfo_rooty()
        relative_y = y_root - container_y_root
        
        cumulative_y = 0
        for i, card in enumerate(self.cards):
            card_height = card.winfo_height()
            if cumulative_y <= relative_y < cumulative_y + card_height / 2:
                return i 
            elif cumulative_y + card_height / 2 <= relative_y < cumulative_y + card_height + 10:
                return i + 1 
            cumulative_y += card_height + 10 
            
        return len(self.cards)