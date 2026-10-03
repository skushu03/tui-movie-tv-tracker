from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.modals.checklist_modal import ChecklistModal
from tui_movie_tv_tracker.modals.diary_entry_modal import DiaryEntryModal


class MediaDetailsModal(ModalScreen):
    BINDINGS = [
        ("a", "add", "Add to list"),
        ("A", "add", "Add to list"),
        ("escape", "exit", "Close modal"),
        ("enter", "exit", "Close modal"),
        ("e", "add_diary_entry", "Add diary entry"),
        ("E", "add_diary_entry", "Add diary entry"),
    ]

    def __init__(self, media_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_info = media_info
        self.lists_updated = False
        self.diary_updated = True

    def compose(self):
        yield Vertical(
            Label(
                f"\\[{self.media_info.get('media_type', '').upper()}]",
            ),
            Label(f"Title: {self.media_info.get('title', '')}"),
            Label(
                f"Release Date: {self.media_info.get('release_date', '')}",
            ),
            Label(
                f"Rating: {self.media_info.get('rating', '0.0')}({self.media_info.get('num_ratings', 0)})",
            ),
            Static(f"Genres: {self.media_info.get('genre_ids', [])}"),
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

            self.lists_updated = (
                database.apply_changes_to_lists(self.app.db, self.media_info, changes)
                or self.lists_updated
            )

        await self.app.push_screen(ChecklistModal("Lists", lists), apply_changes)

    def action_exit(self):
        self.dismiss((self.lists_updated, self.diary_updated))

    def action_add_diary_entry(self):
        def set_diary_updated(diary_updated):
            self.diary_updated = self.diary_updated or diary_updated

        self.app.push_screen(DiaryEntryModal(self.media_info), set_diary_updated)
