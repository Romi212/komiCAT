
from aux_types.chapter import Chapter


class ProjectLoader:
    def __init__(self):
        self.chapter = None
        self.save_path = ""

    def create_project(self):
        self.chapter = Chapter("Kuro no sekai","abracadabra",4)
        
        return self.chapter

    def load_project(self):
        #Load project from file
        file_path = self.chapter.name + ".txt" 
        data = ""
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
            #Parse data and create chapter, pages and segments
        lines = data.split("\n")
        #iterate over lines 3 to rest
        for line in lines[3:]:
            file_path = ""
            page = line.split(":#")
            self.chapter.load_page(page[0],page[1])

    def save_project(self):
        #Create a file in save path
        file_name =  self.chapter.name + ".txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(self.chapter.get_data())
            
        

