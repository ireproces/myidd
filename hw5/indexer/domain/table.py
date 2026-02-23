from domain.paragraph import Paragraph

class Table:

    paragraphs: list[Paragraph]

    def __init__(self, paper_id: str, table_id: str, caption: str, table_url: str, data: str):
        self.paper_id = paper_id
        self.table_id = table_id
        self.caption = caption
        self.data = data
        self.table_url = table_url