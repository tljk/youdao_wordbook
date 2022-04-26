import io
class logToFile(io.IOBase):
    def __init__(self):
        pass

    def write(self, data):
        with open("out.log", mode="a") as f:
            f.write(data.decode('utf-8'))
        return len(data)
