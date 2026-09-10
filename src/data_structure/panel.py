
class Panel:

    def __init__(self, text_box):
        self.text_box = text_box
        self.bubbles = []

    def contains_bubble(self, bubble):
        return self.text_box.intersects(bubble)

    def add_bubble(self, bubble):
        self.bubbles.append(bubble)

    def sort_bubbles(self,base_index):
        self.bubbles.sort(key=lambda bubble: bubble.ymin)
        i = base_index
        for bubble in self.bubbles:
            bubble.index = i
            i+=1
        return base_index + len(self.bubbles)

    def intersects_h(self, line):
        return (self.text_box.ymin <= line) and (self.text_box.ymax >= line)

    def intersects_v(self, line):
        return (self.text_box.xmin < line) and (self.text_box.xmax > line)
    