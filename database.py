# database.py
import sqlite3
from models import Project, Task

class Database:
    def __init__(self, db_name="kanban.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                sort_order INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        self.conn.commit()

    # --- Project Methods ---
    def create_project(self, name):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
            self.conn.commit()
            return Project(cursor.lastrowid, name)
        except sqlite3.IntegrityError:
            return None # Project name already exists

    def get_projects(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        return [Project(row['id'], row['name']) for row in rows]

    # --- Task Methods ---
    def create_task(self, project_id, title, description, status):
        cursor = self.conn.cursor()
        # Get the current highest sort_order for this column to append to the end
        cursor.execute("SELECT MAX(sort_order) FROM tasks WHERE project_id = ? AND status = ?", (project_id, status))
        max_order = cursor.fetchone()[0]
        new_order = (max_order + 1) if max_order is not None else 0

        cursor.execute(
            "INSERT INTO tasks (project_id, title, description, status, sort_order) VALUES (?, ?, ?, ?, ?)",
            (project_id, title, description, status, new_order)
        )
        self.conn.commit()
        return Task(cursor.lastrowid, project_id, title, description, status, new_order)

    def get_tasks_by_status(self, project_id, status):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE project_id = ? AND status = ? ORDER BY sort_order ASC",
            (project_id, status)
        )
        rows = cursor.fetchall()
        return [Task(row['id'], row['project_id'], row['title'], row['description'], row['status'], row['sort_order']) for row in rows]

    def update_task_status_and_order(self, task_id, new_status, new_order, peer_tasks_to_update):
        """
        Updates a task's status and order, and shifts the order of other tasks in the new column.
        peer_tasks_to_update: list of (task_id, new_order) tuples for tasks that need re-ordering.
        """
        cursor = self.conn.cursor()
        # 1. Update the moved task
        cursor.execute(
            "UPDATE tasks SET status = ?, sort_order = ? WHERE id = ?",
            (new_status, new_order, task_id)
        )
        # 2. Update orders of other tasks in the destination column
        for t_id, t_order in peer_tasks_to_update:
            cursor.execute("UPDATE tasks SET sort_order = ? WHERE id = ?", (t_order, t_id))
        
        self.conn.commit()

    def close(self):
        self.conn.close()