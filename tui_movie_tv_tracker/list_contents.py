from textual.containers import Vertical
from textual.widgets import ListView, Static

import tui_movie_tv_tracker.database as database

from .list_item import ListItem


class ListContents(Vertical, can_focus=True):
    def __init__(self, list_info, pane_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pane_title = pane_title
        self.list_info = list_info

    def compose(self):
        list_info_str = f"List Name: {self.list_info.get('name')}\nLast Updated: {self.list_info.get('last_updated')}"

        yield Static(list_info_str, id="list-info")
        yield ListView(*[], id="list-contents-items")

    def on_mount(self):
        self.border_title = self.pane_title

    async def refresh_content(self, new_list_info):
        # self.app.notify("Refreshing list content...")
        try:
            if not new_list_info.get("id"):
                return

            self.list_info = new_list_info

            list_info_str = f"List Name: {self.list_info.get('name', '')}\nLast Updated: {self.list_info.get('last_updated', '')}"

            self.query_one("#list-info").update(list_info_str)

            new_items = database.get_list_items(
                self.app.db, self.list_info.get("id", "")
            )
            #
            list_view = self.query_one("#list-contents-items")

            await list_view.clear()
            new_widgets = [ListItem(n) for n in new_items]
            await list_view.extend(new_widgets)

            # self.app.notify("List contents updated")

        except Exception as e:
            self.app.notify(str(e), severity="warning")
