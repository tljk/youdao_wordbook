import btree
import ujson
import ure

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
        if self.data.get(json['word'].encode('utf-8')) == None:
            print('insert: '+json['word'])
            self.data[json['word']]=s.replace(' ', '').encode('utf-8')

    def record(self,word):
        if self.records.get(word.encode('utf-8')) == None:
            self.records[word] = str(1)
            print('record: '+word+' 1')
        else:
            self.records[word] = str(int(self.records[word].decode('utf-8')) + 1)
            print('record: '+word+' '+self.records[word].decode('utf-8'))
        self.records.flush()

    def printRecords(self):
        for i in self.records.items():
            print(i)
    
    def printData(self):
        for i in self.data.values():
            print(i.decode('utf-8'))
    
    def flush(self):
        self.data.flush()
        self.records.flush()

    def values(self):
        return self.data.values()