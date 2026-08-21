import asyncio

from textual import on
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, Static
from textual.widgets import ListItem as TextualListItem

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker import tmdb
from tui_movie_tv_tracker.base_widgets.list_view import ListView
from tui_movie_tv_tracker.checklist_modal import ChecklistModal
from tui_movie_tv_tracker.modals.media_details_modal import MediaDetailsModal


class SearchResultsList(ListView):
    BINDINGS = [
        ("a", "add", "Add to list"),
        ("A", "add", "Add to list"),
        # ("w", "toggle_watched", "Toggle watched status"),
        # ("W", "toggle_watched", "Toggle watched status"), this is for if they want to say they watched again
        # to delete entry theyd have to go to the diary pane
    ]

    def action_add(self):
        lists = database.get_lists(self.app.db)

        selected_item_data = self.children[self.index].item_data

        for li in lists:
            if database.search_media_in_list(
                self.app.db,
                selected_item_data["media_type"],
                selected_item_data["tmdb_id"],
                li["id"],
            ):
                li["contains"] = True
            else:
                li["contains"] = False

        def update_lists(changes):
            if not changes:
                return
            # self.app.notify(str(changes))
            for list_id, value in changes.items():
                if value == 1:
                    database.add_list_item(
                        self.app.db,
                        selected_item_data,
                        list_id,
                    )
                    self.screen.lists_updated = True
                elif value == -1:
                    database.delete_list_item(
                        self.app.db,
                        selected_item_data,
                        list_id,
                    )
                    self.screen.lists_updated = True

        self.app.push_screen(ChecklistModal("Lists", lists), update_lists)


class SearchResultItem(TextualListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

        # Static("\\[x]" if self.item_data["watched"] else "[ ]"),

    def compose(self):
        yield Horizontal(
            Static(self.item_data.get("title", "")),
            Static(self.item_data.get("release_date", "")),
            Static(str(self.item_data.get("rating", ""))),
            classes=f"result-item-row {'media-item-watched' if self.item_data['watched'] else ''}",
        )


class SearchScreen(Screen):
    BINDINGS = [
        ("s", "search_focus", "Search input focus"),
        ("S", "search_focus", "Search input focus"),
        ("tab", "switch_media", "Switch media type for search"),
        ("escape", "close", "Close search screen"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_type = "movie"
        self.results = []
        self.search_query = ""
        self.curr_page = 0
        self.num_pages = 0

        self.lists_updated = False

    def compose(self):
        yield Vertical(
            Label("Search:"),
            Input(id="search-input"),
            Vertical(
                Static(f'Search results for "{self.search_query}"', id="search-label"),
                Static(
                    "\\[Movie] | TV",
                    id="search-media-type",
                ),
                Static(f"Page {self.curr_page} of {self.num_pages}", id="search-page"),
                Vertical(
                    Horizontal(
                        Static("TITLE"),
                        Static("RELEASE DATE"),
                        Static("RATING"),
                        id="search-results-header",
                    ),
                    SearchResultsList(*self.results, id="search-results-list"),
                    id="search-results-container",
                ),
            ),
            id="search-screen-container",
        )

    def on_mount(self):
        self.query_one("#search-input").focus()

    def update_labels(self):
        self.query_one("#search-label").update(
            f'Search results for "{self.search_query}"'
        )

        self.query_one("#search-media-type")

        self.query_one("#search-page").update(
            f"Page {self.curr_page} of {self.num_pages}"
        )

    async def start_search(self):
        try:
            results_view = self.query_one("#search-results-list")

            results_view.loading = True
            # await asyncio.sleep(1)  # temp
            self.curr_page, self.num_pages, search_results = await tmdb.search(
                self.search_query, self.media_type
            )

            for res in search_results:
                if (res["tmdb_id"], res["media_type"]) in self.app.watched:
                    res["watched"] = True
                else:
                    res["watched"] = False

            self.results = [SearchResultItem(res) for res in search_results]

            await results_view.clear()
            await results_view.extend(self.results)

            if results_view.children:
                results_view.selected_item = results_view.children[0]

            results_view.focus()

            self.update_labels()

            if results_view.children:
                results_view.selected_item = results_view.children[0]
                results_view.index = 0

        except Exception as e:
            self.app.notify(str(e), severity="warning")
        finally:
            results_view.loading = False

    @on(Input.Submitted, "#search-input")
    async def handle_input_submitted(self, event):
        self.search_query = event.value.strip()
        if self.search_query:
            self.run_worker(self.start_search(), exclusive=True)

    @on(SearchResultsList.Selected, "#search-results-list")
    def handle_search_result_selected(self, event):
        selected_item = event.item

        def set_lists_updated(lists_updated):
            self.lists_updated = lists_updated or self.lists_updated

        self.app.push_screen(
            MediaDetailsModal(selected_item.item_data), set_lists_updated
        )

        # self.app.notify(str(selected_item.item_data))

    def action_search_focus(self):
        self.query_one("#search-input").focus()

    def action_switch_media(self):
        if self.media_type == "movie":
            self.media_type = "show"
        else:
            self.media_type = "movie"

        self.query_one("#search-media-type").update(
            "\\[Movie] | TV" if self.media_type == "movie" else "Movie | \\[TV]"
        )

        if self.search_query:
            self.run_worker(self.start_search(), exclusive=True)
        # self.app.notify("testing")

    def action_close(self):
        self.dismiss(self.lists_updated)
