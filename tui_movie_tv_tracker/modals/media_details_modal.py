from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.checklist_modal import ChecklistModal


class MediaDetailsModal(ModalScreen):
    BINDINGS = [
        ("a", "add", "Add to list"),
        ("A", "add", "Add to list"),
        ("escape", "exit", "Close modal"),
        ("enter", "exit", "Close modal"),
    ]

    def __init__(self, media_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_info = media_info
        self.lists_updated = False

    def compose(self):
        yield Vertical(
            Label(
                f"\[{self.media_info.get('media_type', '').upper()}]",
            ),
            Label(f"Title: {self.media_info.get('title', '')}"),
            Label(
                f"Release Date: {self.media_info.get('release_date', '')}",
            ),
            Label(
                f"Rating: {self.media_info.get('rating', '0.0')}({self.media_info.get('num_ratings', 0)})",
            ),
            Static(self.media_info.get("overview", "")),
            classes="modal-container",
            id="search-details-modal",
        )

    async def action_add(self):
        lists = database.get_lists(self.app.db)

        for li in lists:
            if database.search_media_in_list(
                self.app.db,
                self.media_info["media_type"],
                self.media_info["tmdb_id"],
                li["id"],
            ):
                li["contains"] = True
            else:
                li["contains"] = False

        async def update_lists(changes):
            if not changes:
                return

            for list_id, ch in changes.items():
                if ch == 1:
                    database.add_list_item(self.app.db, self.media_info, list_id)
                    self.lists_updated = True
                elif ch == -1:
                    database.delete_list_item(self.app.db, self.media_info, list_id)
                    self.lists_updated = True

        await self.app.push_screen(ChecklistModal("Lists", lists), update_lists)

    def action_exit(self):
        self.dismiss(self.lists_updated)
