from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, ListView, Placeholder, Static
from textual.widgets import ListItem as TextualListItem


class Pane(Static):
    def on_mount(self):
        self.border_title = "lists"


class ListItem(TextualListItem):
    def __init__(self, item_data):
        super().__init__()
        self.item_data = item_data

    def compose(self):
        yield Label(self.item_data["name"])


class MainScreen(Screen):
    # CSS = """
    # Item {
    #     background: transparent;
    #     color: white;
    #     border: ascii white;
    # }
    # """
    def compose(self) -> ComposeResult:
        lists_pane = self.init_lists_pane()
        # yield Header(id="Header")
        yield Vertical(
            Horizontal(lists_pane, Pane("List Info"), Pane("Media Info")),
            Horizontal(Pane("year_month_stats"), Pane("diary")),
        )

    def init_lists_pane(self):
        temp_data = [
            {
                "name": "Spiderman",
                "year": 2002,
            },
            {
                "name": "Lord of THe rings",
                "year": 1999,
            },
            {
                "name": "Obsession",
                "year": 2026,
            },
        ]
        list_items = [ListItem(n) for n in temp_data]

        lists_pane = ListView(*list_items)
        lists_pane.border_title = "Lists"

        return lists_pane


class SearchScreen(Screen):
    pass


class LayoutApp(App):
    CSS_PATH = "index.tcss"

    def on_mount(self) -> None:
        self.ansi_color = True
        self.push_screen(MainScreen())


if __name__ == "__main__":
    app = LayoutApp()
    app.run()
