import asyncio
import datetime

from textual import events, on
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from tui_movie_tv_tracker import database
from tui_movie_tv_tracker.diary import Diary
from tui_movie_tv_tracker.list_contents import ListContents
from tui_movie_tv_tracker.lists import Lists
from tui_movie_tv_tracker.media_details import MediaDetails
from tui_movie_tv_tracker.modals.diary_entry_modal import DiaryEntryModal
from tui_movie_tv_tracker.search_screen import SearchScreen
from tui_movie_tv_tracker.watch_stats import WatchStats


class Pane(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_mount(self):
        self.border_title = "lists"


class MainScreen(Screen):
    BINDINGS = [
        ("tab", "next_focus", "Switch focus to next pane"),
        ("shift+tab", "prev_focus", "Switch focus to previous pane"),
        ("s", "show_search_screen", "Display search screen"),
        ("S", "show_search_screen", "Display search screen"),
        ("t", "temp", ""),
    ]

    def action_temp(self):
        x = database.get_watched_stats(self.app.db, 2026)
        # max_total = max(i["total_count"] for i in x)
        #
        # for i in x:
        #     self.app.notify(str(i))
        # self.app.notify(i["month"] + str(i["movie_count"] / max_total * 100))
        x = database.get_diary_entries(self.app.db, 2026, 7)
        #
        for i in x:
            self.app.notify(i["title"] + i["media_type"])
        #
        # for i in self.focusable_panes:
        #     self.app.notify(i.id)
        # self.app.notify(str(len(self.focusable_panes)))
        return

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Vertical(
            Horizontal(
                Lists(*[], id="lists", classes="pane-window"),
                ListContents({}, id="list-contents", classes="pane-window"),
                MediaDetails({}, id="media-details", classes="pane-window"),
            ),
            Horizontal(
                WatchStats(id="watch-stats", classes="pane-window"),
                Diary(id="diary", classes="pane-window"),
            ),
        )

    async def on_mount(self):
        selected_list = self.query_one("#lists").selected_item

        if selected_list:
            await self.query_one("#list-contents").refresh_content(
                selected_list.item_data
            )
        #
        self.focusable_panes = self.query(".pane-window")
        self.focus_index = 0

    async def refresh_panes(self, _=None):
        self.app.notify("refreshing panes")

        lists_pane = self.query_one("#lists")

        await lists_pane.refresh_content()
        await self.query_one("#list-contents").refresh_content(
            lists_pane.selected_item.item_data
        )
        # self.query_one("#media-details").refresh_content()
        self.query_one("#watch-stats").refresh_content()
        await self.query_one("#diary").refresh_content()
        pass

    def action_next_focus(self):
        self.focus_index = (self.focus_index + 1) % len(self.focusable_panes)
        self.focusable_panes[self.focus_index].focus()

    def action_prev_focus(self):
        self.focus_index = (self.focus_index - 1) % len(self.focusable_panes)
        self.focusable_panes[self.focus_index].focus()

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

    @on(Lists.Selected, "#media-list")
    def list_item_selected(self, event):
        origin_id = event.list_view.id
        selected_item = event.item

        if origin_id == "media-list":
            # self.app.notify(str(selected_item.item_data))
            self.query_one("#media-details").refresh_content(selected_item.item_data)

    @on(WatchStats.Selected)
    async def watch_stats_month_selected(self, event):
        await self.query_one("#diary").refresh_content(event.year, event.month)

    @on(Lists.Selected, "#entry-list")
    def entry_list_item_selected(self, event):
        selected_item = event.item
        # self.app.notify(str(selected_item.item_info))
        self.query_one("#media-details").refresh_content(selected_item.item_info)

    def action_show_search_screen(self):
        # async def update_lists(needs_update):
        #     if not needs_update:
        #         return
        #
        #     lists_widget = self.query_one("#lists")
        #
        #     await self.query_one("#list-contents").refresh_content(
        #         lists_widget.selected_item.item_data
        #     )

        self.app.push_screen(SearchScreen(), self.refresh_panes)


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def on_mount(self) -> None:
        self.ansi_color = True
        self.db = database.get_db()
        self.watched = database.get_watched(self.db)
        if not self.db:
            self.dismiss("")
        self.push_screen(MainScreen(self.db))

        # db.close()


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
