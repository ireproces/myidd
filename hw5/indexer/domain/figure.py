from domain.paragraph import Paragraph

class Figure:

    def __init__(self, paper_id: str, figure_id: str, caption: str, url: str, image_url: str):
        self.paper_id = paper_id
        self.figure_id = figure_id
        self.caption = caption
        self.url = url
        self.image_url = image_url