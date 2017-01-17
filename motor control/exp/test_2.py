def test():
    global a
    a = 5

def test_2():
    global a
    a = a +1
    print(a)

test()
print(a)
test_2()
print(a)