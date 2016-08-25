# an association-game class
class mem(dict):
    def new(self, key, val):
        if key in self.keys():
            if not isinstance(self[key], list):
                self[key] = [self[key]]
            self[key] += [val]
        else:
            self[key] = [val]

    def finding(self, key):
        a = []
        if key in self.keys():
            return self.finding2(key, a)
        else:
            return 'not in mem'

    def finding2(self, key, a):
        a += [key]
        if len(a) > 100:
            a = a[len(a)//2:]
        print(key, '-->', *self[key], '________', sep='\n')
        for val in self[key][:5]:
            if val not in a and val != key:
                print(self.finding3(val, a))
        return '<--'

    def finding3(self, val, a):
        if val in self.keys():
            print(self.finding2(val, a))
        return '========'


MEM=mem({'hello':'word'})
MEM.new('hello','world')
MEM.new('world','hello')
MEM.new('world','big')
MEM.new('world','peace')
MEM.new('bid','small')
MEM.new('word','letter')
MEM.new('letter','post')
MEM.new('post','slow')
MEM.new('peace','cake')
MEM.new('black','white')
print(MEM.finding('hello'))

