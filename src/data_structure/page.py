import os

from data_structure.panel import Panel
from data_structure.segment import Segment
from data_structure.segment_combined import SegmentCombined
from data_structure.segment_list import SegmentList
from data_structure.text_box import TextBox
from image_area_widgets.text_box_rect import TextBoxRect


class Page:
    def __init__(self, file_path=None, image=None, chapter=None, number=0):
        
        self.file_path = file_path
        self.image = image
        self.page_name = os.path.basename(file_path)
        self.number = number
        self.segments = SegmentList()
        self.outside_segments = []
        self.chapter = chapter
        self.extracted_bubbles = 0
        self.segments_amount = 0
        self.detected_panels = []
        self.has_been_processed = False
    

    def store_detected_bubbles(self, detected_bubbles, detected_text_bubbles, detected_free_text, detected_panels):

        self.store_detected_panels(detected_panels)

        self._sort_panels()

        self.detected_bubbles = detected_bubbles
        self.detected_text_bubbles = detected_text_bubbles
        self.detected_free_text = detected_free_text
        remaining_bubbles = detected_bubbles.copy()

        for text_bubble in detected_text_bubbles:
            for bubble in remaining_bubbles:
                if self._is_within(text_bubble, bubble):
                    text_bubble.set_bubble_container(bubble)
                    remaining_bubbles.remove(bubble)
                    break

        for bubble in detected_text_bubbles + detected_free_text:             
            self.create_segment(text_box=bubble)
            
        self.sort_segments()
        self.has_been_processed = True

    def sort_segments(self):
        base = 1
        self.segments = SegmentList()
        for panel in self.detected_panels:
            print(f"sorting panel {base}")
            base, panel_segs = panel.sort_segments(base)
            self.segments.append_segments(panel_segs)
        

    def store_detected_panels(self, detected_panels):
        for panel in detected_panels:
            self.detected_panels.append(Panel(panel))

        

    def _sort_panels(self):
        
        self.detected_panels = list(self._sort_subset(self.detected_panels))


    def _sort_subset(self, panels):
        #BaseCase only one panel left
        if len(panels) <= 1:
            return panels

        #Recursive case: divide horizontaly
        pivot_h = self._find_pivot_h(panels)
        if pivot_h:
            print(f"Found pivot horizontal at height: {pivot_h}:")
            bottom_subset = list(panels)
            top_subset = []
            for panel in panels:
                if panel.text_box.ymax <= pivot_h:
                    top_subset.append(panel)
                    bottom_subset.remove(panel)

            if  bottom_subset and  top_subset:
                top_sorted =  self._sort_subset(top_subset)
                bottom_sorted = self._sort_subset(bottom_subset)
                return top_sorted + bottom_sorted

        #Recursive case: divide vertically
        pivot_v = self._find_pivot_v(panels)
        if pivot_v:
            print(f"found pivot verically at width: {pivot_v} ")
            left_subset = list(panels)
            right_subset = []
            for panel in panels:
                if panel.text_box.xmin >= pivot_v:
                    right_subset.append(panel)
                    left_subset.remove(panel)
            if right_subset and left_subset:
                right_sorted = self._sort_subset(right_subset)
                left_sorted = self._sort_subset(left_subset)
                return right_sorted + left_sorted
    #BaseCase: more panels but no straight line can divide them, returns 1 big panel
        return self._fusion_panels(panels)
            
    def _find_pivot_h(self, panels):
        panels = list(panels)
        panels.sort(key=lambda panel: panel.text_box.ymax)
    
        possible_pivot = 0
        tolerance = 1
        while(possible_pivot < len(panels)-1):
            works = True
            for i in range(possible_pivot+1, len(panels)):   
                if panels[i].text_box.intersects_h(panels[possible_pivot].text_box.ymax + tolerance):
                    works = False
                    break
            if works:
                return panels[possible_pivot].text_box.ymax +tolerance
            else:
                possible_pivot+=1

        return None

    def _find_pivot_v(self, panels):
        panels = list(panels)
        panels.sort(key=lambda panel: panel.text_box.xmax)
        possible_pivot = 0
        tolerance = 1
        while(possible_pivot < len(panels)-1):
            works = True
            for i in range(possible_pivot+1, len(panels)):   
                if panels[i].text_box.intersects_v(panels[possible_pivot].text_box.xmax + tolerance):
                    works = False
                    break
            if works:
                break
            else:
                possible_pivot+=1

        if possible_pivot < len(panels)-1:
            return panels[possible_pivot].text_box.xmax + tolerance
        else:
            return None

    def _fusion_panels(self, panels):
        xmin = min(panel.text_box.xmin for panel in panels)
        ymin = min(panel.text_box.ymin for panel in panels)
        xmax = max(panel.text_box.xmax for panel in panels)
        ymax = max(panel.text_box.ymax for panel in panels)
        text_box = TextBox(xmin, xmax, ymin, ymax, "panel")
        new_panel = Panel(text_box)
        to_return = []
        to_return.append(new_panel)
        return to_return

    def get_segments_to_extract(self, all_segments):
        
        return self.segments
        
    

    def _is_within(self, text_bubble, bubble):
        return (text_bubble.xmin >= bubble.xmin and
                text_bubble.ymin >= bubble.ymin and
                text_bubble.xmax <= bubble.xmax and
                text_bubble.ymax <= bubble.ymax)

    def create_segment(self, text_box):
        segment = Segment(self, len(self.segments))
        self.segments.add_segment(segment)
        segment.text_box = text_box
        text_box.segment = segment
        button = TextBoxRect(
                        text_box,
                        alpha=0.6
                    )
        segment.button = button
        button.set_segment(segment)
        if(text_box.label == "manual"):
            self.outside_segments.append(segment)
            segment.set_edit_mode(True)
        else:
            self._asign_panel(segment)
        self.segments_amount +=1
        
        return segment

    def _asign_panel(self,segment):
        for panel in self.detected_panels:
            if panel.contains_segment(segment):
                panel.add_segment(segment)
                segment.set_panel(panel)
    def get_data(self):
        return {
            "file_path": self.file_path,
            "panels": [panel.get_data() for panel in self.detected_panels]   
        }

    def load_panels(self, panels_data):
        for panel_data in panels_data:
            new_panel = Panel(None)
            new_panel.load_segments(panel_data,self)
            self.detected_panels.append(new_panel)
            self.segments.append_segments(new_panel.segments) 
        self.detected_panels.sort(key=lambda p: p.nro)

    

    def get_translation_text(self):
        translation_text = f"---------------------------{self.page_name}----------------------------------\n"
        for segment in self.segments.heads:
            translation_text += segment.get_translation() + "\n\n"
        return translation_text


    def set_edit_mode(self, can_edit):
        for segment in self.segments:
            segment.set_edit_mode(can_edit)
        if not can_edit:
            self.reasign_panels()

    def delete_segment(self, segment):
        if segment.panel:
            segment.panel.delete_segment(segment)
        self.segments.remove_segment(segment)
        self.segments.recount_segments()

    def reasign_panels(self):
        for segment in self.segments:
            if segment.panel and not segment.panel.contains_segment(segment):
                segment.panel.delete_segment(segment)
                segment.panel = None
                self._asign_panel(segment)
            if not segment.panel:
                self._asign_panel(segment)

        


    def automatic_sort(self):
        self.reasign_panels()
        self.sort_segments()
    
        