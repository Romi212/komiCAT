class ViewsAdapter:
    def __init__(self, image_viewer, text_viewer):
        self.image_viewer = image_viewer
        image_viewer.set_adapter(self)
        self.text_viewer = text_viewer
        self.text_viewer.set_adapter(self)
        self.segment_bubble_map = {}

    def AddSegments(self, segments):
        for button in segments:
            bubble = button.text_box
            segment = self.text_viewer.create_segment(bubble.text)
            self.segment_bubble_map[segment] = bubble