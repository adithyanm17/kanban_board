from datetime import datetime
import sqlite3
from models import Project, Task
from models import Project, Task, Employee # Update your imports
class Database:
    # ... (Keep existing __init__, create_tables, create_project, get_projects) ...
    def __init__(self, db_name="kanban.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                customer TEXT,
                estimated_time TEXT,
                start_date TEXT,
                end_date TEXT
            )
        """)
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists

        # Add History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                from_status TEXT,
                to_status TEXT,
                move_date TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        """)
        self.conn.commit()
                # Inside database.py -> create_tables()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                doj TEXT,
                designation TEXT,
                email TEXT,
                github TEXT
            )
        """)
        self.conn.commit()

    def create_project(self, data):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO projects (name, description, customer, estimated_time, start_date, end_date) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['name'], data['description'], data['customer'], data['estimated_time'], data['start_date'], data['end_date']))
            self.conn.commit()
            return Project(cursor.lastrowid, data['name'], data['description'], data['customer'], data['estimated_time'], data['start_date'], data['end_date'])
        except sqlite3.IntegrityError:
            return None 

    def get_projects(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects")
        rows = cursor.fetchall()
        return [Project(row['id'], row['name'], row['description'], row['customer'], row['estimated_time'], row['start_date'], row['end_date']) for row in rows]

    # --- NEW METHOD: Update Project ---
    def update_project(self, project_id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE projects 
            SET name=?, description=?, customer=?, estimated_time=?, start_date=?, end_date=?
            WHERE id=?
        """, (data['name'], data['description'], data['customer'], data['estimated_time'], data['start_date'], data['end_date'], project_id))
        self.conn.commit()

    # ... (Keep existing Task methods exactly as they are) ...
    def create_task(self, project_id, title, description, status):
        cursor = self.conn.cursor()
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
        cursor = self.conn.cursor()
        
        # Get current status before moving for history logging
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        old_status = cursor.fetchone()[0]
        
        # Update the task
        cursor.execute(
            "UPDATE tasks SET status = ?, sort_order = ? WHERE id = ?",
            (new_status, new_order, task_id)
        )
        
        # Log to history if the status actually changed
        if old_status != new_status:
            cursor.execute(
                "INSERT INTO task_history (task_id, from_status, to_status) VALUES (?, ?, ?)",
                (task_id, old_status, new_status)
            )
            
        for t_id, t_order in peer_tasks_to_update:
            cursor.execute("UPDATE tasks SET sort_order = ? WHERE id = ?", (t_order, t_id))
        self.conn.commit()
    def save_employee(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO employees (emp_code, name, doj, designation, email, github)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data['emp_code'], data['name'], data['doj'], 
            data['designation'], data['email'], data['github']))
        self.conn.commit()

    def get_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        return [Employee(row['id'], row['emp_code'], row['name'], row['doj'], 
                        row['designation'], row['email'], row['github']) for row in rows]

    def get_employee_by_id(self, emp_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = ?", (emp_id,))
        row = cursor.fetchone()
        if row:
            return Employee(row['id'], row['emp_code'], row['name'], row['doj'], 
                            row['designation'], row['email'], row['github'])
        return None

    def update_employee(self, emp_id, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE employees 
            SET emp_code=?, name=?, doj=?, designation=?, email=?, github=?
            WHERE id=?
        """, (data['emp_code'], data['name'], data['doj'], 
            data['designation'], data['email'], data['github'], emp_id))
        self.conn.commit()
    def get_latest_move(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT from_status, move_date FROM task_history 
            WHERE task_id = ? ORDER BY id DESC LIMIT 1
        """, (task_id,))
        return cursor.fetchone()
    def update_task_status_and_order(self, task_id, new_status, new_order, peer_tasks_to_update):
        cursor = self.conn.cursor()
        
        # 1. Get current status to see if it changed
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        old_status = cursor.fetchone()[0]
        
        # 2. Update the task
        cursor.execute("UPDATE tasks SET status = ?, sort_order = ? WHERE id = ?",
                    (new_status, new_order, task_id))
        
        # 3. Log move if status is different
        if old_status != new_status:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute("INSERT INTO task_history (task_id, from_status, to_status, move_date) VALUES (?, ?, ?, ?)",
                        (task_id, old_status, new_status, now))
            
        for t_id, t_order in peer_tasks_to_update:
            cursor.execute("UPDATE tasks SET sort_order = ? WHERE id = ?", (t_order, t_id))
        self.conn.commit()
    

    def close(self):
        self.conn.close()