import btree
import ujson


class DB():
    def __init__(self):
        try:
            self.f = open('data','r+b')
        except:
            self.f = open('data','w+b')
        self.db = btree.open(self.f)
        print('db init')
    
    def close(self):
        self.db.close()
        self.f.close()

    def save(self,s):
        json=ujson.loads(s)
        if self.db.get(json['word']) == None:
            print('insert: '+json['word'])
            self.db[json['word']]=s.encode('utf-8')

    def print(self):
        for i in self.db.values():
            print(i.decode('utf-8'))
    
    async def flush(self):
        self.db.flush()

    def values(self):
        return self.db.values()