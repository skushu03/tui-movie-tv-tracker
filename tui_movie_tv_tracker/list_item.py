from textual.widgets import Label
from textual.widgets import ListItem as TextualListItem


class ListItem(TextualListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

    def compose(self):
        if self.item_data.get("name"):
            yield Label(self.item_data["name"])
        elif self.item_data.get("title"):
            yield Label(self.item_data["title"])
