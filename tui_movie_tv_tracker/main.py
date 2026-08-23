import asyncio

from textual import events, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from tui_movie_tv_tracker import database
from tui_movie_tv_tracker.list_contents import ListContents
from tui_movie_tv_tracker.lists import Lists
from tui_movie_tv_tracker.media_details import MediaDetails
from tui_movie_tv_tracker.modals.diary_entry_modal import DiaryEntryModal
from tui_movie_tv_tracker.search_screen import SearchScreen


class Pane(Static):
    def on_mount(self):
        self.border_title = "lists"


class MainScreen(Screen):
    BINDINGS = [
        ("tab", "next_focus", "Switch focus to next pane"),
        ("shift+tab", "prev_focus", "Switch focus to previous pane"),
        ("s", "show_search_screen", "Display search screen"),
        ("S", "show_search_screen", "Display search screen"),
        ("t", "test", "Testing"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Vertical(
            Horizontal(
                Lists("Lists", *[], id="lists", classes="pane-window"),
                ListContents(
                    {}, "List Info", id="list-contents", classes="pane-window"
                ),
                MediaDetails({}, id="media-details", classes="pane-window"),
            ),
            Horizontal(Pane("year_month_stats"), Pane("diary")),
        )

    async def on_mount(self):
        selected_list = self.query_one("#lists").selected_item

        await self.query_one("#list-contents").refresh_content(selected_list.item_data)

    def action_test(self):
        self.app.push_screen(DiaryEntryModal())

    def action_next_focus(self):
        # self.app.notify(str(self.focused.id))
        if self.focused.id == "lists":
            self.query_one("#list-contents-items").focus()
        elif self.focused.id == "list-contents-items":
            self.query_one("#media-details").focus()
        elif self.focused.id == "media-details":
            self.query_one("#lists").focus()

    def action_prev_focus(self):
        if self.focused.id == "lists":
            self.query_one("#media-details").focus()
        elif self.focused.id == "list-contents-items":
            self.query_one("#lists").focus()
        elif self.focused.id == "media-details":
            self.query_one("#list-contents-items").focus()

    @on(Lists.Selected, "#lists")
    async def list_selected(self, event):
        origin_id = event.list_view.id
        selected_item = event.item

        lists_widget = self.query_one("#lists")
        lists_widget.selected_item = lists_widget.children[lists_widget.index]

        if origin_id == "lists":
            await self.query_one("#list-contents").refresh_content(
                selected_item.item_data
            )

    @on(Lists.Selected, "#list-contents-items")
    def list_item_selected(self, event):
        origin_id = event.list_view.id
        selected_item = event.item

        if origin_id == "list-contents-items":
            # self.app.notify(str(selected_item.item_data))
            # return
            self.query_one("#media-details").refresh_data(selected_item.item_data)

    def action_show_search_screen(self):
        async def update_lists(needs_update):
            if not needs_update:
                return

            lists_widget = self.query_one("#lists")

            # await lists_widget.refresh_list()
            await self.query_one("#list-contents").refresh_content(
                lists_widget.selected_item.item_data
            )

        self.app.push_screen(SearchScreen(), callback=update_lists)


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def on_mount(self) -> None:
        self.ansi_color = True
        self.db = database.get_db()
        self.watched = database.get_watched(self.db)
        # self.lists = set(database.get_lists(self.db))
        # self.notify(str(self.watched))
        if not self.db:
            self.dismiss("")
        self.push_screen(MainScreen(self.db))

        # db.close()


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
