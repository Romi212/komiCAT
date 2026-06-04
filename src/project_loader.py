
from aux_types.chapter import Chapter
import json

class ProjectLoader:
    def __init__(self):
        self.chapter = None
        self.save_path = ""

    def create_project(self):
        self.chapter = Chapter("Kuro no sekai","abracadabra",4)
        
        return self.chapter

    def load_project(self, file_path):
        #Load project from file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.chapter = Chapter(
            series_name=data["series_name"],
            name=data["name"],
            number=data["number"]
        )
        self.chapter.load_chapter(data)
        return self.chapter

    def save_project(self, save_path):
        self.save_path = save_path +".romi"
        print(self.save_path)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.chapter.get_data(), f)
            
        

