import PIL.Image
import os
from dotenv import load_dotenv

from manga_ocr import MangaOcr
from matplotlib import text
from aux_types.text_box import TextBox
from transformers import AutoImageProcessor, AutoModelForObjectDetection, pipeline
from huggingface_hub import login

load_dotenv()

class TextExtractor:

    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")
        login(token=hf_token)
        self.mocr = MangaOcr()
        processor = AutoImageProcessor.from_pretrained("ogkalu/comic-text-and-bubble-detector")
        model = AutoModelForObjectDetection.from_pretrained("ogkalu/comic-text-and-bubble-detector")

        self.bubble_detector = pipeline(
            "object-detection",
            model=model,
            feature_extractor=processor,
        )

    def extract_text(self, image, bubbles):

        for bubble in bubbles:
            cropped_image = image.crop((bubble.xmin, bubble.ymin, bubble.xmax, bubble.ymax))
            bubble.text = self.mocr(cropped_image)
            print(bubble.text)
        return bubbles
    
    def detect_speech_bubbles(self, image):
        #image = PIL.Image.open(image).convert("RGB")
        results = self.bubble_detector(image)
        detected_bubbles = []
        detected_text_bubbles = []
        detected_free_text = []
        print (results)
        # each result is {'score': 0.9623701572418213, 'label': 'text_bubble', 'box': {'xmin': 209, 'ymin': 312, 'xmax': 240, 'ymax': 365}}
        for result in results:
            box = result['box']
            label = result['label']
            score = result['score']
            if score > 0.5:  # Adjust threshold as needed
                text_box = TextBox(box['xmin'], box['xmax'], box['ymin'], box['ymax'], label)
                if label == "text_bubble":
                    detected_text_bubbles.append(text_box)
                elif label == "text_free":
                    detected_free_text.append(text_box)
                else:
                    detected_bubbles.append(text_box)
                print(f"Detected {label} with confidence {score:.2f} at ({box['xmin']}, {box['ymin']}, {box['xmax']}, {box['ymax']})")
        return detected_bubbles, detected_text_bubbles, detected_free_text
    
    
