from textual.widgets import ListView

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

    async def on_mount(self):
        self.border_title = self.pane_title
        await self.refresh_list()

        if self.children:
            self.selected_item = self.children[0]

    async def refresh_list(self):
        # self.app.notify("Refreshing lists...")
        try:
            old_index = self.index
            await self.clear()

            new_items = get_lists(self.app.db)

            new_widgets = [ListItem(n) for n in new_items]

            await self.extend(new_widgets)

            if not old_index:
                self.index = 0
            elif old_index >= len(self.children):
                self.index = len(self.children) - 1
            else:
                self.index = old_index

            # self.app.notify("Lists updated")

        except Exception as e:
            self.app.notify(str(e))
