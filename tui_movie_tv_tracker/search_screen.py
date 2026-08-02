from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, ListView

from tui_movie_tv_tracker import tmdb_api


class SearchScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.curr_media = "movie"

    def compose(self):
        yield Vertical(
            Label("Search:"),
            Input(id="search-input"),
            ListView(*[], id="search-results"),
            id="search-screen-container",
        )

    def on_mount(self):
        self.query_one("#search-input").focus()
        self.query_one("#search-results").loading = True

    def on_input_submitted(self, event):
        search_query = event.value.strip()
        if search_query:
            # tmdb_api.search(search_query, self.curr_media)
            self.query_one("#search-results").loading = False

    def key_space(self):
        self.dismiss("Search closed")
