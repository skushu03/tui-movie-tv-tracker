from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.base_widgets.list_view import ListView


class MediaList(ListView):
    BINDINGS = [("tab", "screen.next_focus", "Switch focus to next pane")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_focus(self):
        if not self.index:
            self.index = 0


class MediaItem(ListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

    def compose(self):
        yield Horizontal(
            Static(self.item_data.get("title", "")),
            Static(self.item_data.get("release_date", "")[:4]),
            Static(self.item_data.get("media_type", "")),
        )


class ListContents(Vertical, can_focus=True):
    def __init__(self, list_info, pane_title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pane_title = pane_title
        self.list_info = list_info

    def compose(self):
        list_info_str = f"List Name: {self.list_info.get('name', '')}\nLast Updated: {self.list_info.get('last_updated', '')}"

        yield Static(list_info_str, id="list-info")
        yield MediaList(*[], id="list-contents-items")

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
            new_widgets = [MediaItem(n) for n in new_items]
            await list_view.extend(new_widgets)

            # self.app.notify("List contents updated")

        except Exception as e:
            self.app.notify(str(e), severity="warning")

    def on_focus(self):
        self.query_one("#list-contents-items").focus()
