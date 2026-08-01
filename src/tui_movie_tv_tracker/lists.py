from textual.widgets import Label, ListView

from .database import get_lists
from .list_item import ListItem


class Lists(ListView):
    DEFAULT_CLASSES = "pane-window"

    def __init__(self, pane_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pane_title = pane_title
        self.selected_item = None

    def on_key(self, event):
        if not self.has_focus:
            return
        # num_items = len(self.children)
        if event.key in ("j", "J"):
            self.index += 1
        elif event.key in ("k", "K"):
            self.index -= 1

    def on_mount(self):
        self.border_title = self.pane_title
        self.refresh_list()

        if self.children:
            self.selected_item = self.children[0]

    def refresh_list(self):
        old_index = self.index
        self.clear()

        new_items = get_lists(self.app.db)

        new_widgets = [ListItem(n) for n in new_items]

        self.extend(new_widgets)

        if not old_index:
            self.index = 0
        elif old_index >= len(self.children):
            self.index = len(self.children) - 1
        else:
            self.index = old_index
