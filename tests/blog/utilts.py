class Custom_MockSet:
    def __init__(self, *args):
        self.args = args

    def count(self):
        return len(self.args)

    def none(self):
        return len(self.args)
