class Project:
    def __init__(self, id, name, description=None, customer=None, estimated_time=None, 
                 start_date=None, end_date=None, part_number=None, part_name=None, 
                 total_cost=None, project_manager=None, scopes=None, out_of_scopes=None, 
                 deliverables=None, po_number=None, wo_number=None, po_date=None, due_date=None):
        self.id = id
        self.name = name
        self.description = description
        self.customer = customer
        self.estimated_time = estimated_time
        self.start_date = start_date
        self.end_date = end_date
        self.part_number = part_number
        self.part_name = part_name
        self.total_cost = total_cost
        self.project_manager = project_manager
        self.scopes = scopes
        self.out_of_scopes = out_of_scopes
        self.deliverables = deliverables
        self.po_number = po_number
        self.wo_number = wo_number
        self.po_date = po_date
        self.due_date = due_date

class Task:
    def __init__(self, id, project_id, title, description, status, sort_order):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.status = status
        self.sort_order = sort_order


class Employee:
    def __init__(self, id, emp_code, name, doj, designation, email, github):
        self.id = id
        self.emp_code = emp_code
        self.name = name
        self.doj = doj
        self.designation = designation
        self.email = email
        self.github = github