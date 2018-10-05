class test(object):
    def __init__(self):
        pass
    def test1(self):
        self.a = 5

    def test2(self, argv):
        print(self.a)
        print(argv)

if __name__ == '__main__':
    abc = test()
    abc.test2()
