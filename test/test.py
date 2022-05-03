class n:
    tmp = 0

    def __init__(self):
        self.code = self.tmp
        self.tmp += 1
        self.name = f'n{self.code}'
        print(self.name)

    def debug(self):
        print(self)
        print(self.name)


endN = n()
startN = n()

endN.debug()
startN.debug()
name = 'line'
if name == 'line':
    endN = startN
endN.debug()
startN.debug()
