import json


class Test:


    def __init__(self):
        self.eins = 1
        self.zwei = "zwei"
        self.drei = False

    def toJSON(self):
        return "ses"

tt = [Test()]


f = open("test.json", "w")
f.write(json.dumps(tt))
f.close()