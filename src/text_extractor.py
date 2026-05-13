import PIL.Image

from manga_ocr import MangaOcr
from aux_types.text_box import TextBox
from transformers import AutoImageProcessor, AutoModelForObjectDetection, pipeline

class TextExtractor:

    def __init__(self):
        self.mocr = MangaOcr()
        processor = AutoImageProcessor.from_pretrained("ogkalu/comic-text-and-bubble-detector")
        model = AutoModelForObjectDetection.from_pretrained("ogkalu/comic-text-and-bubble-detector")

        self.bubble_detector = pipeline(
            "object-detection",
            model=model,
            feature_extractor=processor,
        )


    def detect_speech_bubbles(self, image):
        #image = PIL.Image.open(image).convert("RGB")
        results = self.bubble_detector(image)
        detected_bubbles = []
        print (results)
        # each result is {'score': 0.9623701572418213, 'label': 'text_bubble', 'box': {'xmin': 209, 'ymin': 312, 'xmax': 240, 'ymax': 365}}
        for result in results:
            box = result['box']
            label = result['label']
            score = result['score']
            if score > 0.5:  # Adjust threshold as needed
                text_box = TextBox(box['xmin'], box['xmax'], box['ymin'], box['ymax'], label)
                detected_bubbles.append(text_box)
                print(f"Detected {label} with confidence {score:.2f} at ({box['xmin']}, {box['ymin']}, {box['xmax']}, {box['ymax']})")
        return detected_bubbles
    
    def extract_text(self, image):
        text = self.mocr(image)
        print(text)
        return text
