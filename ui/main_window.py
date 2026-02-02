import tkinter as tk
from tkinter import messagebox, ttk
from ui.project_view import ProjectView
from ui.project_details import ProjectDetailsForm
from ui.project_planning_view import ProjectPlanningView # Add import
from ui.project_team_view import ProjectTeamView 
from ui.dialogs import ask_new_project_info

class MainWindow(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.title("Python Kanban App")
        self.geometry("1200x700")
        
        # State variables for project list
        self.all_projects = []
        self.filtered_projects = []
        
        self.setup_layout()
        self.show_projects_view() # Default view

    def setup_layout(self):
        # 1. Main Navigation Sidebar (Leftmost)
        self.nav_bar = tk.Frame(self, width=80, bg="#333")
        self.nav_bar.pack(side="left", fill="y")
        
        self.create_nav_button("Projects", self.show_projects_view)
        self.create_nav_button("Team", self.show_team_view)
        self.create_nav_button("Settings", self.show_settings_view)

        # 2. Sub-Sidebar (For Project List)
        self.sub_sidebar = tk.Frame(self, width=200, bg="#e0e0e0")

        # 3. Main Content Area
        self.content_area = tk.Frame(self, bg="white")
        self.content_area.pack(side="right", fill="both", expand=True)

    def create_nav_button(self, text, command):
        btn = tk.Button(self.nav_bar, text=text, command=command, bg="#333", fg="white", 
                        bd=0, font=("Arial", 10, "bold"), pady=15, activebackground="#555", activeforeground="white")
        btn.pack(fill="x")

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # --- View Controllers ---

    def show_projects_view(self):
        # Ensure Sub-sidebar is visible
        self.sub_sidebar.pack(side="left", fill="y", before=self.content_area)
        
        # Clear Sub-sidebar
        for widget in self.sub_sidebar.winfo_children():
            widget.destroy()

        tk.Label(self.sub_sidebar, text="Projects", font=("Arial", 14, "bold"), bg="#e0e0e0", pady=10).pack()

        # --- Search Bar ---
        search_frame = tk.Frame(self.sub_sidebar, bg="#e0e0e0")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        self.project_search_var = tk.StringVar()
        self.project_search_var.trace_add("write", self.filter_projects)
        
        search_entry = tk.Entry(search_frame, textvariable=self.project_search_var, font=("Arial", 10))
        search_entry.pack(fill="x")
        search_entry.insert(0, "Search projects...")
        
        # Clear placeholder logic
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if self.project_search_var.get() == "Search projects..." else None)
        search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search projects...") if not self.project_search_var.get() else None)

        # New Project Button
        btn_new_proj = tk.Button(self.sub_sidebar, text="+ New Project", command=self.create_project, bg="white", relief="flat")
        btn_new_proj.pack(fill="x", padx=10, pady=5)

        # Listbox for Projects
        self.project_list_box = tk.Listbox(self.sub_sidebar, bg="#e0e0e0", bd=0, highlightthickness=0, font=("Arial", 11), selectbackground="#bbdefb")
        self.project_list_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.project_list_box.bind("<<ListboxSelect>>", self.on_project_select)

        self.refresh_project_list()
        
        self.clear_content()
        tk.Label(self.content_area, text="Select a project to view details", font=("Arial", 14), fg="gray", bg="white").pack(expand=True)

    def show_team_view(self):
        self.sub_sidebar.pack_forget() 
        self.clear_content()
        from ui.team_view import TeamView
        team_frame = TeamView(self.content_area, self.db)
        team_frame.pack(fill="both", expand=True)

    def show_settings_view(self):
        self.sub_sidebar.pack_forget()
        self.clear_content()
        tk.Label(self.content_area, text="Settings (Coming Soon)", font=("Arial", 20), bg="white").pack(expand=True)

    # --- Project Logic ---

    def create_project(self):
        data = ask_new_project_info(self)
        if data and data['name']:
            project = self.db.create_project(data)
            if project:
                self.refresh_project_list()
            else:
                messagebox.showerror("Error", "Project name already exists.")

    def refresh_project_list(self):
        """Fetches all projects and triggers the filter/display logic."""
        self.all_projects = self.db.get_projects()
        self.filter_projects()

    def filter_projects(self, *args):
        """Filters the project list with a safety check for destroyed widgets."""
        # Check 1: Does the attribute exist?
        if not hasattr(self, 'project_list_box'):
            return
        
        # Check 2: Has the widget been destroyed by a view switch?
        try:
            if not self.project_list_box.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return

        query = self.project_search_var.get().lower()
        if query == "search projects...":
            query = ""

        self.project_list_box.delete(0, tk.END)
        
        # Rest of your filter logic...
        self.filtered_projects = [
            p for p in self.all_projects 
            if query in p.name.lower() or (p.customer and query in p.customer.lower())
        ]
        for p in self.filtered_projects:
            self.project_list_box.insert(tk.END, p.name)

    def on_project_select(self, event):
        selection = self.project_list_box.curselection()
        if selection:
            index = selection[0]
            project = self.filtered_projects[index]
            self.load_project_tabs(project)

    def load_project_tabs(self, project):
        self.clear_content()
        notebook = ttk.Notebook(self.content_area)
        notebook.pack(fill="both", expand=True)

        # Existing tabs...
        board_frame = ProjectView(notebook, self.db, project)
        notebook.add(board_frame, text="  Kanban Board  ")
        
        # NEW: Planning Tab
        planning_frame = ProjectPlanningView(notebook, self.db, project)
        notebook.add(planning_frame, text="  Project Planning  ")

        details_frame = ProjectDetailsForm(notebook, self.db, project)
        notebook.add(details_frame, text="  Project Description  ")

        team_tab = ProjectTeamView(notebook, self.db, project)
        notebook.add(team_tab, text="  Project Team  ")

    def close(self):
        self.db.close()