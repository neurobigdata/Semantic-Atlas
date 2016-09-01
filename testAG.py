import association
MEM = association.mem({'hello':'word'})
MEM.new('Hello', 'world')
MEM.new('world', 'Hello')
MEM.new('world', 'big')
MEM.new('world', 'peace')
MEM.new('big', 'small')
MEM.new('word', 'letter')
MEM.new('letter', 'post')
MEM.new('post', 'slow')
MEM.new('peace', 'cake')
MEM.new('black', 'white')

D={'why':'question','question':'word','word':'number','a':'A','A':'b','b':'B'}
memes = association.memes()
memes.new(MEM)
memes.new(D)

print(memes.find('Hello'))
