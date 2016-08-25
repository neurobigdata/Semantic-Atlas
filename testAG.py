import association
MEM = association.mem({'hello':'word'})
MEM.new('hello', 'world')
MEM.new('world', 'hello')
MEM.new('world', 'big')
MEM.new('world', 'peace')
MEM.new('big', 'small')
MEM.new('word', 'letter')
MEM.new('letter', 'post')
MEM.new('post', 'slow')
MEM.new('peace', 'cake')
MEM.new('black', 'white')

D={'why':'question','question':'word','word':'number'}
memes = association.memes()
memes.new(MEM)
memes.new(D)

print(memes.find('word'))
