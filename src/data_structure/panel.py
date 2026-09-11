
from data_structure.segment_combined import SegmentCombined


class Panel:

    def __init__(self, text_box):
        self.text_box = text_box
        self.bubbles = []
        self.segments = []

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

    

    def contains_segment(self, segment):
        return self.text_box.intersects(segment.text_box)

    def add_segment(self, segment):
        self.segments.append(segment)

    def sort_segments(self, base_index):
        
        self.segments = self._sort_subset(self.segments).copy()
        i = base_index
        for seg in self.segments:
            i = seg.set_nro(i) +1
        return i, self.segments

    def _sort_subset(self, segments):

        if len(segments) <= 1:
            
            return segments


        pivot_v = self._find_pivot_v(segments)
        if pivot_v:
            print(f"found v pivot in: {pivot_v} ")
            left_segs = segments.copy()
            right_segs = []
            for seg in left_segs:
                if seg.text_box.xmin >= pivot_v:
                    right_segs.append(seg)
                    left_segs.remove(seg)

            if(left_segs and right_segs):
                print(right_segs)
                print(left_segs)
                right_sorted = self._sort_subset(right_segs)
                left_sorted = self._sort_subset(left_segs)
                return right_sorted + left_sorted

        pivot_h = self._find_pivot_h(segments)
        if pivot_h:
            print(f"found h pivot in {pivot_h}")
            top_segs = segments.copy()
            bottom_segs = []

            for seg in top_segs:
                if seg.text_box.ymin >= pivot_h:
                    bottom_segs.append(seg) 
                    top_segs.remove(seg)   

            if(top_segs and bottom_segs):
                self.logprint(top_segs)
                self.logprint(bottom_segs)
                top_sorted = self._sort_subset(top_segs)
                bottom_sorted = self._sort_subset(bottom_segs)
                return top_sorted + bottom_sorted

        return self.combine_segments(segments)

    def logprint(self, list):
        for l in list:
            print(l.text_box.xmin)
            print(l.text_box.ymin)
            print(l.text_box.xmax)
            print(l.text_box.ymax)
    def combine_segments(self,segments):
        #Sort
        print(f"Combined {len(segments)} segments")
        sorted = segments.copy()
        sorted.sort(key=lambda panel: panel.text_box.ymin)
        #Create Combined Segments and link until last one
        combined_head = SegmentCombined(None,-1)
        combined_head.clone_segment(sorted[0])
        previous = combined_head
        next = 1
        while (next< len(sorted)-1):
            combined_seg = SegmentCombined(None,-1)
            combined_seg.clone_segment(sorted[next])
            previous.set_next_segment(combined_seg)
            previous = combined_seg
            next+=1
        previous.set_next_segment(sorted[next])
        #Return a list with only 1 element that is head
        return [combined_head]

    def _find_pivot_h(self, segments):
            segments = list(segments)
            segments.sort(key=lambda panel: panel.text_box.ymax)
        
            possible_pivot = 0
            tolerance = 50
            while(possible_pivot < len(segments)-1):
                works = True
                for i in range(possible_pivot+1, len(segments)):   
                    if segments[i].text_box.intersects_h(segments[possible_pivot].text_box.ymax + tolerance):
                        works = False
                        break
                if works:
                    return segments[possible_pivot].text_box.ymax +tolerance
                else:
                    possible_pivot+=1
    
            return None
    
    def _find_pivot_v(self, segments):
            segments = list(segments)
            segments.sort(key=lambda panel: panel.text_box.xmax)
            possible_pivot = 0
            tolerance = 20
            while(possible_pivot < len(segments)-1):
                works = True
                for i in range(possible_pivot+1, len(segments)):   
                    if segments[i].text_box.intersects_v(segments[possible_pivot].text_box.xmax + tolerance):
                        works = False
                        break
                if works:
                    break
                else:
                    possible_pivot+=1
    
            if possible_pivot < len(segments)-1:
                return segments[possible_pivot].text_box.xmax + tolerance
            else:
                return None  