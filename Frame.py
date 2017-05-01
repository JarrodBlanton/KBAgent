class Frame:
    figure = None
    name = None
    node = None
    attributes = {}
    def __init__(self, object):
        self.figure = object['figure']
        self.name = object['name']
        self.shape = object['shape']
        self.size = object['size']
        self.fill = object['fill']

    def setNode(self, node):
        self.node = node


    def toString(self):
        return str("Figure: " + self.figure + " | Name: " + self.name + " | Shape: " + self.shape + " | Size: " +
                   self.size + " | Fill: " + self.fill)