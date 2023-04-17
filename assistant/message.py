class Message:
    """
    Message class that creates a message as a dict for chat
    """

    def __init__(self, role, content):
        self.role = role
        self.content = content

    def message(self):
        return {"role": self.role, "content": self.content}
