from textual.containers import Vertical
from textual.widgets import Label

import tui_movie_tv_tracker.database as database


class MediaDetails(Vertical, can_focus=True):
    def __init__(self, media_metadata, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_metadata = media_metadata
        self.media_info = {}

    def compose(self):
        yield Label(
            f"\[{self.media_info.get('media_type', '').upper()}]", id="md-label-type"
        )
        yield Label(f"Title: {self.media_info.get('title', '')}", id="md-label-title")
        yield Label(
            f"Release Date: {self.media_info.get('release_date', '')}",
            id="md-label-release",
        )
        yield Label(
            f"Rating: {self.media_info.get('rating', '0.0')}({self.media_info.get('num_ratings', 0)})",
            id="md-label-rating",
        )

    def on_mount(self):
        self.refresh_data()

    def refresh_data(self, new_media_metadata={}):
        try:
            if new_media_metadata:
                self.media_metadata = new_media_metadata
            elif not self.media_metadata:
                return

            # right now media_metadata already has all the info thats being displayed but
            # in the future the media_info table will like genres and overview and maybe director so in turn get_media_info will return all those too

            self.media_info = database.get_media_info(
                self.app.db,
                self.media_metadata.get("tmdb_id", ""),
                self.media_metadata.get("media_type", ""),
            )

            # also add if not self.media_info, make http request

            self.query_one("#md-label-type").update(
                f"\[{self.media_info.get('media_type', '').upper()}]"
            )
            self.query_one("#md-label-title").update(
                f"Title: {self.media_info.get('title', '')}"
            )
            self.query_one("#md-label-release").update(
                f"Release Date: {self.media_info.get('release_date', '')}",
            )
            self.query_one("#md-label-rating").update(
                f"Rating: {self.media_info.get('rating', '0.0')}({self.media_info.get('num_ratings', 0)})",
            )

        except Exception as e:
            self.app.notify(str(e), severity="warning")
