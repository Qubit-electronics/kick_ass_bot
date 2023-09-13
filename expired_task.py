from datetime import datetime

class expired_task:
    def __init__(self, text:str,date:datetime, members:list[str]):
        self.text = text
        self.date = date
        self.members = members
        
    def __repr__(self) -> str:
        return self.text