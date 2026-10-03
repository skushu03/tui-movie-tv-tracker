from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.base_widgets.list_view import ListView
from tui_movie_tv_tracker.modals.checklist_modal import ChecklistModal
from tui_movie_tv_tracker.modals.date_select_modal import DateSelectModal
from tui_movie_tv_tracker.modals.input_modal import InputModal


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
        media_type = self.item_data.get("media_type", "")

        if media_type == "movie":
            media_type_label = "\\[MV]"
        elif media_type == "tv":
            media_type_label = "\\[TV]"
        else:
            media_type_label = "\\[NA]"

        yield Horizontal(
            # Label(media_type_label),
            Label(
                f"{media_type_label} {self.item_data.get('title', '')}",
                classes=f"{'media-item-watched' if self.item_data['watched'] else ''} list-contents-item-title",
            ),
            Label(self.item_data.get("release_date", "")[:4]),
        )


class ListContents(Vertical, can_focus=True):
    BINDINGS = [
        ("a", "add", "Add to lists"),
        ("A", "add", "Add to lists"),
        ("d", "delete", "Delete from list"),
        ("D", "delete", "Delete from list"),
        ("e", "add_diary_entry", "Add diary entry"),
        ("E", "add_diary_entry", "Add diary entry"),
    ]

    def __init__(self, list_info, pane_title=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = pane_title if pane_title else "List Contents"
        self.list_info = list_info

        self.movie_count = 0
        self.tv_count = 0

    def compose(self):
        list_info_str = f"List Name: {self.list_info.get('name', '')}\nLast Updated: {self.list_info.get('last_updated', '')}\nMovies: {self.movie_count}\nTV: {self.tv_count}"

        yield Static(list_info_str, id="list-info")
        yield MediaList(*[], id="media-list")

    async def refresh_content(self, new_list_info={}):
        # self.app.notify("Refreshing list content...")
        try:
            if new_list_info.get("id"):
                self.list_info = new_list_info

            new_items = database.get_list_items(
                self.app.db, self.list_info.get("id", "")
            )

            movie_count = 0
            tv_count = 0
            for item in new_items:
                if item.get("media_type") == "movie":
                    movie_count += 1
                elif item.get("media_type") == "tv":
                    tv_count += 1

            self.movie_count = movie_count
            self.tv_count = tv_count

            list_info_str = f"List Name: {self.list_info.get('name', '')}\nLast Updated: {self.list_info.get('last_updated', '')}\nMovies: {self.movie_count}\nTV: {self.tv_count}"

            self.query_one("#list-info").update(list_info_str)

            #
            list_view = self.query_one("#media-list")

            await list_view.clear()
            new_widgets = [MediaItem(n) for n in new_items]
            await list_view.extend(new_widgets)

            if list_view.children:
                list_view.index = 0

            # self.app.notify("List contents updated")

        except Exception as e:
            self.app.notify(str(e), severity="warning")

    def on_focus(self):
        self.query_one("#media-list").focus()

    async def action_add(self):
        # should prob make this into a general reusable function
        highlighted_item = self.query_one("MediaList").highlighted_child

        if not highlighted_item:
            return

        highlighted_item_data = highlighted_item.item_data

        lists = database.get_lists_contain_media(
            self.app.db,
            highlighted_item_data["media_type"],
            highlighted_item_data["tmdb_id"],
        )

        async def apply_changes(changes):
            if not changes:
                return

            try:
                if database.apply_changes_to_lists(
                    self.app.db, highlighted_item_data, changes
                ):
                    await self.refresh_content({"lists": True})

            except Exception as e:
                self.app.notify(str(e), severity="warning")

        await self.app.push_screen(ChecklistModal("Lists", lists), apply_changes)

    async def action_delete(self):
        highlighted_item = self.query_one("MediaList").highlighted_child

        if not self.list_info or not highlighted_item:
            return

        highlighted_item_data = highlighted_item.item_data

        async def delete_list_item(confirmation):
            try:
                if confirmation.lower() == "y":
                    database.delete_list_item(
                        self.app.db,
                        highlighted_item_data,
                        self.list_info["id"],
                    )
                    await self.refresh_content()
            except Exception as e:
                self.app.notify(str(e), severity="warning")

        await self.app.push_screen(
            InputModal("Delete media from this list? (y/N)", 1), delete_list_item
        )

    async def action_add_diary_entry(self):
        highlighted_item = self.query_one("MediaList").highlighted_child

        if not self.list_info or not highlighted_item:
            return

        highlighted_item_data = highlighted_item.item_data

        async def add_to_diary(selected_date):
            panes_updated = {}

            if selected_date:
                panes_updated["diary"] = True

                database.add_diary_entry(
                    self.app.db, highlighted_item_data, self.app.watched, selected_date
                )

            await self.screen.refresh_panes(panes_updated)

        await self.app.push_screen(
            DateSelectModal(highlighted_item_data["title"]), add_to_diary
        )
