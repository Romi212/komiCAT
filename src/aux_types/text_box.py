
class TextBox:
    def __init__(self, xmin,xmax,ymin,ymax,label):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.label = label
        self.text = ""
        self.bubble_container = None

    def set_bubble_container(self, bubble_container):
        self.bubble_container = bubble_container


    def intersects(self, other):
        #Check if self intersects with another TextBox with a tolerance of 5 pixels
        tolerance = 5
        return not (self.xmax + tolerance < other.xmin or
                    self.xmin - tolerance > other.xmax or
                    self.ymax + tolerance < other.ymin or
                    self.ymin - tolerance > other.ymax)