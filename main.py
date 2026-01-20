# main.py
from database import Database
from ui.main_window import MainWindow

if __name__ == "__main__":
    # Initialize Database
    db = Database("my_kanban.db")
    
    # Start Application
    app = MainWindow(db)
    app.mainloop()
    
    # Clean up connection on exit
    db.close()