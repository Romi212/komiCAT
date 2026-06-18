
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
        if not self.bubble_container or not other.bubble_container:
            return False
        return ((self.bubble_container.xmin in range(other.bubble_container.xmin, other.bubble_container.xmax) and self.bubble_container.ymin in range(other.bubble_container.ymin, other.bubble_container.ymax)) or
                (self.bubble_container.xmax in range(other.bubble_container.xmin, other.bubble_container.xmax) and self.bubble_container.ymax in range(other.bubble_container.ymin, other.bubble_container.ymax)) or
                (self.bubble_container.xmin in range(other.bubble_container.xmin, other.bubble_container.xmax) and self.bubble_container.ymax in range(other.bubble_container.ymin, other.bubble_container.ymax)) or
                (self.bubble_container.xmax in range(other.bubble_container.xmin, other.bubble_container.xmax) and self.bubble_container.ymin in range(other.bubble_container.ymin, other.bubble_container.ymax)))