# app_config.py
LANGUAGES = {"en": "English", "es": "Español"}
FONT_RANGE = (8, 24)
class AppConfig:
    def __init__(self):
        self.theme = "Dark"
        self.font_size = 12
        self.app_language = "en"
        self.recent_projects = []      # [{"path", "name", "last_opened"}]

    def load_data(self, data):
        self.theme = data.get("theme", self.theme)
        self.font_size = data.get("font_size", self.font_size)
        self.app_language = data.get("app_language", self.app_language)
        self.recent_projects = data.get("recent_projects", [])

    def get_data(self):
        return {
            "schema_version": 1,
            "theme": self.theme,
            "font_size": self.font_size,
            "app_language": self.app_language,
            "recent_projects": self.recent_projects,
        }

config = AppConfig()  