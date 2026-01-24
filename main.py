from database import Database
from ui.main_window import MainWindow

if __name__ == "__main__":
    db = Database("my_kanban.db")
    
    app = MainWindow(db)
    app.mainloop()
    
    db.close()