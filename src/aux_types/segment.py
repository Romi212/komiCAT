
class Segment:
    def __init__(self, page, segment_nro, proxy):
        self.page = page
        self.nro = segment_nro
        self.source_text = None
        self.translation = ""

        self.text_box_button_proxy = proxy
        self.segment_box = None 

    def set_segment_box(self, segment_box):
        self.segment_box = segment_box
        self.source_text = segment_box.get_japanese_text()

    def text_extracted(self, text):
        self.source_text = text

    def update_source_text(self, new_text):
        self.source_text = new_text
        if self.segment_box:
            self.segment_box.set_japanese_text(new_text)

    def show_focus(self, focused):
        self.text_box_button_proxy.widget().set_focus(focused)


    def get_data(self):
        #[segment_nro, isExtracted, [TextBox bounds], label , source_text, translation]
        data = "["+f"{self.nro}"
        if self.source_text:
            data += ",1"
        else:
            data += ",0"
        data += ",(" + str(self.text_box_button_proxy.widget().text_box.xmin) + "," + str(self.text_box_button_proxy.widget().text_box.ymin) + "," + str(self.text_box_button_proxy.widget().text_box.xmax) + "," + str(self.text_box_button_proxy.widget().text_box.ymax) + ")"
        
        data += "," + self.text_box_button_proxy.widget().text_box.label

        data += "," + self.source_text if self.source_text else ","
        data += "," + self.translation if self.translation else ""
        
        return data + "]"