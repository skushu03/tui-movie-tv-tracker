from textual.containers import Vertical
from textual.widgets import Static


class ListContents(Vertical, can_focus=True):
    DEFAULT_CLASSES = "pane-window"

    def __init__(self, list_info, pane_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pane_title = pane_title
        self.list_info = list_info

    def compose(self):
        list_info_str = f"List Name: {self.list_info.get('name')}\nLast Updated: {self.list_info.get('last_updated')}"

        yield Static(list_info_str, id="list-info")

    def on_mount(self):
        self.border_title = self.pane_title

    def refresh_content(self, new_list_info):
        self.list_info = new_list_info

        list_info_str = f"List Name: {self.list_info['name']}\nLast Updated: {self.list_info['last_updated']}"

        self.query_one("#list-info").update(list_info_str)
