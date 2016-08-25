import association

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
            if val not in a:
                print(self.finding3(val, a))
        return '<--'

    def finding3(self, val, a):
        if val in self.keys():
            print(self.finding2(val, a))
        return '========'


def to_mem(arg):
    if type(arg) is dict:
        for key in arg.keys():
            arg[key] = [arg[key]]
        arg = association.mem(arg)
    return arg


class memes(list):
    def new(self, arg):
        if not isinstance(arg, association.mem):
            arg = association.to_mem(arg)
        self.append(arg)

    def find(self, word):
        a = []
        for semField in self:
            if word in semField.keys():
                print(self.find2(word, semField, a))
        return 'no such meme'

    def find2(self, key, sem_field, a):
        a += [key]
        if len(a) > 100:
            a = a[len(a) // 2:]
        print(key, '-->', *sem_field[key], '________', sep='\n')
        for val in sem_field[key][:5]:
            if val not in a:
                print(self.find3(val, sem_field, a))
        return '<--'

    def find3(self, val, sem_field, a):
        if val in sem_field.keys():
            return self.find2(val, sem_field, a)
        return '========'


