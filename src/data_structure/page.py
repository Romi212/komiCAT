import os

from data_structure.panel import Panel
from data_structure.segment import Segment
from data_structure.segment_combined import SegmentCombined
from data_structure.text_box import TextBox


class Page:
    def __init__(self, file_path=None, image=None, chapter=None, number=0):
        
        self.file_path = file_path
        self.image = image
        self.page_name = os.path.basename(file_path)
        self.number = number
        self.segments = []
        self.chapter = chapter
        self.extracted_bubbles = 0
        self.detected_panels = []
    

    def store_detected_bubbles(self, detected_bubbles, detected_text_bubbles, detected_free_text):
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

        base= 1
        for panel in self.detected_panels:
            for bubble in detected_text_bubbles + detected_free_text:
                if panel.contains_bubble(bubble):
                    panel.add_bubble(bubble)
            base = panel.sort_bubbles(base)
            

    def store_detected_panels(self, detected_panels):
        for panel in detected_panels:
            self.detected_panels.append(Panel(panel))

        self._sort_panels()

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
                if panels[i].intersects_h(panels[possible_pivot].text_box.ymax + tolerance):
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
                if panels[i].intersects_v(panels[possible_pivot].text_box.xmax + tolerance):
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


    def extracted_segments(self, extracted_bubbles):
        segments = []
        base_index = self.extracted_bubbles
        combined_segment_head = None
        print("--------------------------EXTRACTED SEGMENTS--------------------------------")
        for i in range(1, len(extracted_bubbles)):
            bubble_button = extracted_bubbles[i-1]
            if extracted_bubbles[i].text_box.intersects(bubble_button.text_box):
                segment = SegmentCombined(self, -1)
                self.segments.remove(bubble_button.segment)
                bubble_button.segment = segment
                segment.button = bubble_button
                segment.text_box = bubble_button.text_box
                if combined_segment_head:
                    print("Segment "+ bubble_button.text + " " + bubble_button.text_box.text + " ~continua~")
                    combined_segment_head.set_next_segment(segment)
                    combined_segment_head = segment
                else:
                    print("Segment "+ bubble_button.text+ " " + bubble_button.text_box.text + "EMPEZO COMBINADO OwO")
                    combined_segment_head = segment
                    segments.append(segment)
                    self.segments.append(segment)
            else:
                segment = bubble_button.segment
                if combined_segment_head:
                    print("Segment "+ bubble_button.text + " " + bubble_button.text_box.text + "~TERMINO//")
                    combined_segment_head.set_next_segment(segment)
                    combined_segment_head = None
                    self.segments.remove(segment)
                else:
                    print("Segment "+ bubble_button.text + " " + bubble_button.text_box.text + "")
                    segments.append(segment)
            
            segment.nro = base_index + int(bubble_button.text)
            segment.text_extracted(bubble_button.text_box.text)
            
            bubble_button.has_been_extracted()

        last_button = extracted_bubbles[len(extracted_bubbles)-1]
        segment = last_button.segment
        segment.nro = base_index + int(last_button.text)
        segment.text_extracted(last_button.text_box.text)

        if combined_segment_head:
            combined_segment_head.set_next_segment(segment)
            self.segments.remove(segment)
        else:
            segments.append(segment)

        last_button.has_been_extracted()
        self.extracted_bubbles += len(extracted_bubbles)
        print("--------------------------EXTRACTED SEGMENTS--------------------------------")
        for segment in self.segments:
            print(f"Segment {segment.nro}: {segment.source_text} ")
        return segments

    def _is_within(self, text_bubble, bubble):
        return (text_bubble.xmin >= bubble.xmin and
                text_bubble.ymin >= bubble.ymin and
                text_bubble.xmax <= bubble.xmax and
                text_bubble.ymax <= bubble.ymax)

    def create_segment(self, text_box):
        segment = Segment(self, len(self.segments))
        self.segments.append(segment)
        segment.text_box = text_box
        return segment
    
    def get_data(self):
        return {
            "file_path": self.file_path,
            "segments": [segment.get_data() for segment in self.segments]
        }
    
    def load_segments(self, segments_data):
        for segment_data in segments_data:
            if segment_data["next_segment"]:
                print("loading combined")
                segment = SegmentCombined(self, segment_data["nro"])
            else:
                segment = Segment(self, segment_data["nro"])
            segment.load_data(segment_data)
            if segment.source_text:
                self.extracted_bubbles += 1
            self.segments.append(segment)
            self.segments.sort(key=lambda s: s.nro)

    def get_translation_text(self):
        translation_text = f"---------------------------{self.page_name}----------------------------------\n"
        for segment in self.segments:
            translation_text += segment.get_translation() + "\n\n"
        return translation_text