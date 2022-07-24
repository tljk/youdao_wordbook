import btree
import ujson

class DB():
    def __init__(self):
        try:
            self.d = open('data','r+b')
        except:
            self.d = open('data','w+b')
        self.data = btree.open(self.d)
        print('db init')
    
    def close(self):
        self.data.close()
        self.d.close()
        self.records.close()
        self.r.close()

    def save(self,s):
        json=ujson.loads(s)
        word = json['word']
        if self.data.get(word.encode('utf-8')) == None:
            json.pop('word')
            json.pop('itemId')
            json.pop('modifiedTime')
            json.pop('bookId')
            json['p'] = json.pop('phonetic')
            json['b'] = json.pop('bookName')
            json['t'] = json.pop('trans')
            print('insert: '+word)
            # print(word+': '+ujson.dumps(json))
            self.data[word] = ujson.dumps(json).encode('utf-8')
        else:
            curr = ujson.loads(self.data.get(word.encode('utf-8')).decode('utf-8'))
            if curr['b'] != json['bookName'] or curr['p'] != json['phonetic'] or curr['t'] != json['trans']:
                curr['p'] = json['phonetic']
                curr['b'] = json['bookName']
                curr['t'] = json['trans']
                print('update: '+word)
                # print(word+': '+ujson.dumps(curr))
                self.data[word] = ujson.dumps(curr).encode('utf-8')



    def printData(self):
        for i in self.data.values():
            print(i.decode('utf-8'))
    
    def flush(self):
        self.data.flush()
        self.d.flush()

    def values(self):
        return self.data.values()