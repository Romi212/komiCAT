
class Panel:

    def __init__(self, text_box):
        self.text_box = text_box
        self.bubbles = []

    def contains_bubble(self, bubble):
        return self.text_box.intersects(bubble.text_box)

    def add_bubble(self, bubble):
        self.bubbles.append(bubble)

    def sort_bubbles(self):
        self.bubbles.sort(key=lambda bubble: bubble.text_box.ymin)

    def intersects_h(self, line):
        return (self.text_box.ymin <= line) and (self.text_box.ymax >= line)

    def intersects_v(self, line):
        return (self.text_box.xmin < line) and (self.text_box.xmax > line)
    