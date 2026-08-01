from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from . import database
from .input_modal import InputModal
from .list_contents import ListContents
from .lists import Lists


class Pane(Static):
    def on_mount(self):
        self.border_title = "lists"


class MainScreen(Screen):
    BINDINGS = [
        ("tab", "switch_focus", "Switch focused pane"),
        ("a", "create_list", "Create new list"),
        ("d", "delete_list", "Delete list"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def compose(self):
        list_contents = self.init_list_contents()
        # yield Header(id="Header")
        yield Vertical(
            Horizontal(
                Lists("Lists", *[], id="lists"), list_contents, Pane("Media Info")
            ),
            Horizontal(Pane("year_month_stats"), Pane("diary")),
        )

    def on_mount(self):
        selected_list = self.query_one("#lists").selected_item

        self.query_one("#list-contents").refresh_content(selected_list.item_data)

    def on_list_view_selected(self, event):
        # origin_id = event.list_view.id
        selected_item = event.item

        self.query_one("#list-contents").refresh_content(selected_item.item_data)

    def action_switch_focus(self):
        if self.focused and self.focused.id == "lists":
            self.query_one("#list-contents").focus()
        elif self.focused and self.focused.id == "list-contents":
            self.query_one("#lists").focus()

    def action_create_list(self):
        def handle_create_list(list_name):
            try:
                if not list_name:
                    return
                database.create_list(self.app.db, list_name)
            except Exception as e:
                self.app.notify(str(e), severity="warning")
            finally:
                self.query_one("#lists").refresh_list()

        self.app.push_screen(
            InputModal("Enter list name:", 36), callback=handle_create_list
        )

    def action_delete_list(self):
        def handle_delete_list(confirmation):
            try:
                if confirmation in ("y", "Y"):
                    selected_list_name = self.query_one(
                        Lists
                    ).highlighted_child.item_data["name"]
                    database.delete_list(self.app.db, selected_list_name)

            except Exception as e:
                self.app.notify(str(e), severity="warning")
            finally:
                self.query_one("#lists").refresh_list()

        self.app.push_screen(
            InputModal("Are you sure you want to delete this list?", 1),
            callback=handle_delete_list,
        )

    def init_list_contents(self):
        return ListContents({}, "List Info", id="list-contents")


class SearchScreen(Screen):
    pass


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def on_mount(self) -> None:
        self.ansi_color = True
        self.db = database.get_db()
        self.push_screen(MainScreen(self.db))

        # db.close()


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
