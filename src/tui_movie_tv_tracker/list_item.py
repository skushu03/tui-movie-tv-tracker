from textual.widgets import Label
from textual.widgets import ListItem as TextualListItem


class ListItem(TextualListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

    def compose(self):
        yield Label(self.item_data["name"])
