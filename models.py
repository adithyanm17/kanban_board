class Project:
    def __init__(self, id, name, description=None, customer=None, estimated_time=None, start_date=None, end_date=None):
        self.id = id
        self.name = name
        self.description = description
        self.customer = customer
        self.estimated_time = estimated_time
        self.start_date = start_date
        self.end_date = end_date

class Task:
    def __init__(self, id, project_id, title, description, status, sort_order):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.sort_order = sort_order