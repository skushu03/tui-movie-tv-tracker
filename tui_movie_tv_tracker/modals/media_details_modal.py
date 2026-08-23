from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.actions import apply_changes_to_lists
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
        lists = database.get_lists_contain_media(
            self.app.db,
            self.media_info["media_type"],
            self.media_info["tmdb_id"],
        )

        async def apply_changes(changes):
            if not changes:
                return

            self.lists_updated = self.lists_updated or apply_changes_to_lists(
                self.app, self.media_info, changes
            )

        await self.app.push_screen(ChecklistModal("Lists", lists), apply_changes)

    def action_exit(self):
        self.dismiss(self.lists_updated)
