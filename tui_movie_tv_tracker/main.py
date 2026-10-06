import json
import sys

from textual import on
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from tui_movie_tv_tracker import database
from tui_movie_tv_tracker.diary import Diary
from tui_movie_tv_tracker.list_contents import ListContents
from tui_movie_tv_tracker.lists import Lists
from tui_movie_tv_tracker.media_details import MediaDetails
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
    ]

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
            Footer(),
        )

    async def on_mount(self):
        self.focusable_panes = self.query(".pane-window")

        self.pane_refs = {}
        for pane in self.focusable_panes:
            self.pane_refs[pane.id] = pane

        self.focus_index = 0

        selected_list = self.pane_refs["lists"].selected_item

        if selected_list:
            await self.pane_refs["list-contents"].refresh_content(
                selected_list.item_data
            )

    async def refresh_panes(self, panes_updated):
        lists_updated = panes_updated.get("lists", False)
        diary_updated = panes_updated.get("diary", False)
        # lists_updated, diary_updated = panes_updated

        if lists_updated:
            lists_pane = self.pane_refs["lists"]

            await lists_pane.refresh_content()
            if lists_pane.selected_item:
                await self.pane_refs["list-contents"].refresh_content(
                    lists_pane.selected_item.item_data
                )

        if diary_updated:
            self.pane_refs["watch-stats"].refresh_content()
            await self.pane_refs["diary"].refresh_content()

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

        if origin_id == "lists":
            lists_widget = self.pane_refs["lists"]
            lists_widget.selected_item = lists_widget.children[lists_widget.index]

            await self.pane_refs["list-contents"].refresh_content(
                selected_item.item_data
            )

    @on(Lists.Selected, "#media-list")
    def list_item_selected(self, event):
        origin_id = event.list_view.id
        selected_item = event.item

        if origin_id == "media-list":
            # self.app.notify(str(selected_item.item_data))
            self.pane_refs["media-details"].refresh_content(selected_item.item_data)

    @on(WatchStats.Selected)
    async def watch_stats_month_selected(self, event):
        await self.pane_refs["diary"].refresh_content(event.year, event.month)

    @on(Lists.Selected, "#entry-list")
    def entry_list_item_selected(self, event):
        selected_item = event.item
        # self.app.notify(str(selected_item.item_info))
        self.pane_refs["media-details"].refresh_content(selected_item.item_info)

    def action_show_search_screen(self):
        self.app.push_screen(SearchScreen(), self.refresh_panes)


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def __init__(self, db_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.exit()
        if db_name:
            self.db = database.get_db(db_name=db_name)
        else:
            self.db = database.get_db()

        self.watched = database.get_watched(self.db)

        with open("tui_movie_tv_tracker/keybinds.json", "r") as file:
            self.keybinds = json.load(file)

        if not self.db:
            self.dismiss("")

    def on_mount(self):
        self.ansi_color = True
        self.push_screen(MainScreen(self.db))

    def on_unmount(self):
        self.db.close()


def start():
    if len(sys.argv) > 1:
        app = LayoutApp(sys.argv[1])
    else:
        app = LayoutApp()

    app.run()


if __name__ == "__main__":
    start()
    # if len(sys.argv) > 1:
    #     app = LayoutApp(sys.argv[1])
    # else:
    #     app = LayoutApp()
    #
    # app.run()
