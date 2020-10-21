class ListStream:
    def __init__(self, obj):
        self.obj = obj
        self.i = 0
        self.lookback = 0

    def get(self):
        value = self.get_value(self.i)
        self.i += 1
        return value

    def get_value(self, i):
        return self.obj[i]

    def unget(self):
        self.i -= 1

    def has_values(self):
        return self.i < len(self.obj)

    def save(self):
        self.lookback = self.i

    def restore(self):
        self.i = self.lookback

class SeriesStream(ListStream):
    def get_value(self, i):
        return (self.obj.index[i], self.obj[i])
