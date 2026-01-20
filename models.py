# models.py

class Project:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Task:
    def __init__(self, id, project_id, title, description, status, sort_order):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.sort_order = sort_order