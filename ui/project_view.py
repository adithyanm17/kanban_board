import tkinter as tk
from ui.column import KanbanColumn
from ui.dialogs import ask_new_task_info

class ProjectView(tk.Frame):
    COLUMNS = ["Backlog", "Todo", "WIP", "Testing", "Done", "Approved"]
    COLORS = ["#fdf4f5", "#f0f4f8", "#fff9c4", "#e1f5fe", "#e8f5e9", "#dcedc8"]

    def __init__(self, parent, db, project):
        super().__init__(parent)
        self.db = db
        self.project = project
        self.column_widgets = {}
        self.dragging_card = None
        self.setup_board()
        self.refresh_board()

    def setup_board(self):
        toolbar = tk.Frame(self, height=40)
        toolbar.pack(fill="x", side="top", pady=(0, 10))
        tk.Label(toolbar, text=f"Project: {self.project.name}", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(toolbar, text="+ Add Task", bg="#4CAF50", fg="white", command=self.add_task_action).pack(side="right")

        board_frame = tk.Frame(self)
        board_frame.pack(fill="both", expand=True)

        for i, col_name in enumerate(self.COLUMNS):
            col = KanbanColumn(
                board_frame, 
                self.db,           # ADD THIS: Pass the database object here
                col_name, 
                self.COLORS[i], 
                self.on_card_drag_start, 
                self.on_card_drop
            )
            col.grid(row=0, column=i, sticky="nsew", padx=5)
            board_frame.columnconfigure(i, weight=1)
            board_frame.rowconfigure(0, weight=1)
            self.column_widgets[col_name] = col

    def add_task_action(self):
        team_members = self.db.get_employees() #
        
        title, desc, member_ids = ask_new_task_info(self, team_members=team_members) #
        
        if title:
            # 1. Create the task first to get its ID
            new_task = self.db.create_task(self.project.id, title, desc, "Backlog") #
            
            # 2. Save assignments for EVERY checked employee in the dialog
            if member_ids:
                for emp_id in member_ids:
                    self.db.assign_employee_to_task(new_task.id, emp_id) #
                    
            # 3. Refresh the board so the new card (with names) appears
            self.refresh_board() #

    def refresh_board(self):
        for col_name, col_widget in self.column_widgets.items():
            col_widget.clear_cards()
            tasks = self.db.get_tasks_by_status(self.project.id, col_name)
            for task in tasks:
                col_widget.add_task(task)

    def on_card_drag_start(self, card):
        self.dragging_card = card

    def on_card_drop(self, card, x_root, y_root):
        target_column = self.find_column_under_cursor(x_root)
        
        if target_column:
            old_status = card.task.status
            new_status = target_column.status
            
            try:
                old_idx = self.COLUMNS.index(old_status)
                new_idx = self.COLUMNS.index(new_status)
            except ValueError:
                return 

            
            allowed = False
            
            allowed = False

            if new_idx == old_idx:
                allowed = True # Reordering within the same column
            elif new_idx > old_idx:
                allowed = True # Allow moving forward to ANY future stage
            elif (old_status in ["Done", "Approved"]) and new_status == "Backlog":
                allowed = True # Allow rejection/re-work
            
            if allowed:
                insert_index = target_column.get_card_at_y(y_root)
                self.move_task_in_db(card.task, new_status, insert_index)
            else:
                print(f"Movement rejected: Cannot move from {old_status} to {new_status}")
        
        self.dragging_card = None

    def move_task_in_db(self, task, new_status, insert_index):
        peer_tasks_to_update = []
        current_tasks = self.db.get_tasks_by_status(self.project.id, new_status)
        
        current_tasks = [t for t in current_tasks if t.id != task.id]

        new_order = 0
        if insert_index == 0:
            new_order = 0
            for i, t in enumerate(current_tasks):
                peer_tasks_to_update.append((t.id, i + 1))
        elif insert_index >= len(current_tasks):
            new_order = len(current_tasks)
        else:
            new_order = insert_index
            for i, t in enumerate(current_tasks):
                if i >= insert_index:
                    peer_tasks_to_update.append((t.id, i + 1))
        
        self.db.update_task_status_and_order(task.id, new_status, new_order, peer_tasks_to_update)
        self.refresh_board()

    def find_column_under_cursor(self, x_root):
        for col in self.column_widgets.values():
            col_x = col.winfo_rootx()
            col_width = col.winfo_width()
            if col_x <= x_root <= col_x + col_width:
                return col
        return None