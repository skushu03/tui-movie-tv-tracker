from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.base_widgets.list_view import ListView
from tui_movie_tv_tracker.checklist_modal import ChecklistModal
from tui_movie_tv_tracker.input_modal import InputModal


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
    BINDINGS = [
        ("a", "add", "Add to lists"),
        ("A", "add", "Add to lists"),
        ("d", "delete", "Delete from list"),
        ("D", "delete", "Delete from list"),
    ]

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

    async def refresh_content(self, new_list_info={}):
        # self.app.notify("Refreshing list content...")
        try:
            if new_list_info.get("id"):
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

    async def action_add(self):
        # should prob make this into a general reusable function
        highlighted_item = self.query_one("MediaList").highlighted_child

        if not highlighted_item:
            return

        highlighted_item_data = highlighted_item.item_data

        lists = database.get_lists(self.app.db)

        for li in lists:
            if database.search_media_in_list(
                self.app.db,
                highlighted_item_data["media_type"],
                highlighted_item_data["tmdb_id"],
                li["id"],
            ):
                li["contains"] = True
            else:
                li["contains"] = False

        async def update_lists(changes):
            if not changes:
                return

            for list_id, ch in changes.items():
                if ch == 1:
                    database.add_list_item(self.app.db, highlighted_item_data, list_id)
                elif ch == -1:
                    database.delete_list_item(
                        self.app.db, highlighted_item_data, list_id
                    )

            await self.refresh_content()

        await self.app.push_screen(ChecklistModal("Lists", lists), update_lists)

    async def action_delete(self):
        highlighted_item = self.query_one("MediaList").highlighted_child

        if not self.list_info or not highlighted_item:
            return

        highlighted_item_data = highlighted_item.item_data

        async def delete_list_item(confirmation):
            if confirmation.lower() == "y":
                database.delete_list_item(
                    self.app.db,
                    highlighted_item_data,
                    self.list_info["id"],
                )

            await self.refresh_content()

        await self.app.push_screen(
            InputModal("Delete media from this list? (y/N)", 1), delete_list_item
        )
