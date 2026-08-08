import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from tui_movie_tv_tracker import database
from tui_movie_tv_tracker.input_modal import InputModal
from tui_movie_tv_tracker.list_contents import ListContents
from tui_movie_tv_tracker.lists import Lists
from tui_movie_tv_tracker.search_screen import SearchScreen


class Pane(Static):
    def on_mount(self):
        self.border_title = "lists"


class MainScreen(Screen):
    BINDINGS = [
        ("tab", "switch_focus", "Switch focused pane"),
        ("a", "create_list", "Create new list"),
        ("A", "create_list", "Create new list"),
        ("d", "delete_list", "Delete list"),
        ("D", "delete_list", "Delete list"),
        ("s", "show_search_screen", "Display search screen"),
        ("S", "show_search_screen", "Display search screen"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self):
        yield Vertical(
            Horizontal(
                Lists("Lists", *[], id="lists"),
                ListContents({}, "List Info", id="list-contents"),
                Pane("Media Info"),
            ),
            Horizontal(Pane("year_month_stats"), Pane("diary")),
        )

    async def on_mount(self):
        selected_list = self.query_one("#lists").selected_item

        await self.query_one("#list-contents").refresh_content(
            selected_list.item_data if selected_list else {}
        )

    async def on_list_view_selected(self, event):
        origin_id = event.list_view.id
        selected_item = event.item

        if origin_id == "lists":
            await self.query_one("#list-contents").refresh_content(
                selected_item.item_data
            )

    def action_switch_focus(self):
        if self.focused and self.focused.id == "lists":
            self.query_one("#list-contents").focus()
        elif self.focused and self.focused.id == "list-contents":
            self.query_one("#lists").focus()

    async def action_create_list(self):
        async def handle_create_list(list_name):
            # if not list_name:
            #     return
            try:
                database.create_list(self.app.db, list_name)
                await self.query_one("#lists").refresh_list()
            except Exception as e:
                self.app.notify(str(e), severity="warning")

        await self.app.push_screen(
            InputModal("Enter list name:", 36), callback=handle_create_list
        )

    async def action_delete_list(self):
        async def handle_delete_list(confirmation):
            if confirmation not in ("y", "Y"):
                return

            try:
                selected_list_name = self.query_one(Lists).highlighted_child.item_data[
                    "name"
                ]
                database.delete_list(self.app.db, selected_list_name)

                await self.query_one("#lists").refresh_list()

            except Exception as e:
                self.app.notify(str(e), severity="warning")

        await self.app.push_screen(
            InputModal(
                "Are you sure you want to delete this list? (y/N)",
                1,
            ),
            callback=handle_delete_list,
        )

    def action_show_search_screen(self):
        def temp_callback(message):
            self.app.notify(message)

        self.app.push_screen(SearchScreen(), callback=temp_callback)


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def on_mount(self) -> None:
        self.ansi_color = True
        self.db = database.get_db()
        self.watched = database.get_watched(self.db)
        self.notify(str(self.watched))
        if not self.db:
            self.dismiss("")
        self.push_screen(MainScreen(self.db))

        # db.close()


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
