import asyncio

from httpx import ConnectError
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, ListView

from tui_movie_tv_tracker import tmdb
from tui_movie_tv_tracker.list_item import ListItem


class ResultsList(ListView):
    BINDINGS = [
        ("j", "nav_down", "Navigate down"),
        ("J", "nav_down", "Navigate down"),
        ("k", "nav_up", "Navigate Up"),
        ("K", "nav_up", "Navigate Up"),
    ]

    def action_nav_down(self):
        self.index += 1

    def action_nav_up(self):
        self.index -= 1


class SearchScreen(Screen):
    BINDINGS = [
        ("s", "search_focus", "Search input focus"),
        ("S", "search_focus", "Search input focus"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_type = "movie"
        self.results = []

    def compose(self):
        yield Vertical(
            Label("Search:"),
            Input(id="search-input"),
            ResultsList(*self.results, id="search-results"),
            id="search-screen-container",
        )

    def on_mount(self):
        self.query_one("#search-input").focus()

    def action_search_focus(self):
        self.query_one("#search-input").focus()

    async def start_search(self, search_query):
        try:
            results_view = self.query_one("#search-results")

            results_view.loading = True
            await asyncio.sleep(1)  # temp
            search_results = await tmdb.search(search_query, self.media_type)

            self.results = [ListItem(res) for res in search_results]

            results_view.clear()
            results_view.extend(self.results)

            if results_view.children:
                results_view.selected_item = results_view.children[0]

            results_view.loading = False
            results_view.focus()

            if results_view.children:
                results_view.selected_item = results_view.children[0]
                results_view.index = 0
        except Exception as e:
            self.app.notify(str(e), severity="warning")
        finally:
            results_view.loading = False
        # except Exception as e:
        #     self.app.notify(str(e), severity="warning")

    async def on_input_submitted(self, event):
        search_query = event.value.strip()
        if search_query:
            self.run_worker(self.start_search(search_query), exclusive=True)

    def key_escape(self):
        self.dismiss("Search closed")
