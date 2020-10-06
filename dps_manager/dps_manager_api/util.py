class Diff:
    def __init__(self, A, B):
        A = set(A)
        B = set(B)

        self.deletes = A - B
        self.adds = B - A
        self.same = A & B

    def get_additions(self):
        return self.adds

    def get_deletions(self):
        return self.deletes

    def get_unchanged(self):
        return self.same
