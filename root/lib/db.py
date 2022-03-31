import btree
import ujson


class DB():
    def __init__(self):
        try:
            self.d = open('data','r+b')
        except:
            self.d = open('data','w+b')
        self.data = btree.open(self.d)
        try:
            self.r = open('record','r+b')
        except:
            self.r = open('record','w+b')
        self.records = btree.open(self.r)
        print('db init')
    
    def close(self):
        self.data.close()
        self.d.close()
        self.records.close()
        self.r.close()

    def save(self,s):
        json=ujson.loads(s)
        if self.data.get(json['word']) == None:
            print('insert: '+json['word'])
            self.data[json['word']]=s.encode('utf-8')
    
    def record(self,word):
        if self.records.get(word) == None:
            self.records[word] = str(1)
            print('record: '+word+' 1')
        else:
            self.records[word] = str(int(self.records[word].decode('utf-8')) + 1)
            print('record: '+word+' '+self.records[word].decode('utf-8'))
        self.records.flush()

    def print(self):
        for i in self.data.values():
            print(i.decode('utf-8'))
    
    async def flush(self):
        self.data.flush()
        self.record.flush()

    def values(self):
        return self.data.values()