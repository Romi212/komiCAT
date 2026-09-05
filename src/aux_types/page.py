import os

from aux_types.segment import Segment
from aux_types.segment_combined import SegmentCombined


class Page:
    def __init__(self, file_path=None, image=None, chapter=None):
        
        self.file_path = file_path
        self.image = image
        self.page_name = os.path.basename(file_path)
        self.segments = []
        self.chapter = chapter
        self.extracted_bubbles = 0
    

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

        return segments

    def _is_within(self, text_bubble, bubble):
        return (text_bubble.xmin >= bubble.xmin and
                text_bubble.ymin >= bubble.ymin and
                text_bubble.xmax <= bubble.xmax and
                text_bubble.ymax <= bubble.ymax)

    def create_segment(self):
        segment = Segment(self, -1)
        self.segments.append(segment)
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
            self.segments.append(segment)
            self.segments.sort(key=lambda s: s.nro)

    def get_translation_text(self):
        translation_text = f"---------------------------{self.page_name}----------------------------------\n"
        for segment in self.segments:
            translation_text += segment.get_translation() + "\n\n"
        return translation_text