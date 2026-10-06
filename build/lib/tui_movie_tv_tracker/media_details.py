from textual.containers import Vertical
from textual.widgets import Label, Static

import tui_movie_tv_tracker.constants as constants
import tui_movie_tv_tracker.database as database


class MediaDetails(Vertical, can_focus=True):
    def __init__(self, media_metadata, pane_title=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_metadata = media_metadata
        self.media_info = {}
        self.border_title = pane_title if pane_title else "Media Details"

        self.genre_names = [
            constants.MOVIE_GENRE_MAP[id] for id in self.media_info.get("genre_ids", [])
        ]

    def compose(self):
        yield Label(
            f"\\[{self.media_info.get('media_type', '').upper()}]", id="md-label-type"
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
        yield Label(f"Genres: {self.genre_names}", id="md-label-genres")
        yield Static(self.media_info.get("overview", ""), id="md-label-overview")

    def on_mount(self):
        self.type_label = self.query_one("#md-label-type")
        self.title_label = self.query_one("#md-label-title")
        self.release_label = self.query_one("#md-label-release")
        self.rating_label = self.query_one("#md-label-rating")
        self.genres_label = self.query_one("#md-label-genres")
        self.overview_label = self.query_one("#md-label-overview")

        self.refresh_content()

    def refresh_content(self, new_media_metadata={}):
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

            media_type = self.media_info.get("media_type", "")

            self.type_label.update(f"\\[{media_type.upper()}]")

            self.title_label.update(f"Title: {self.media_info.get('title', '')}")

            self.release_label.update(
                f"Release Date: {self.media_info.get('release_date', '')}",
            )

            self.rating_label.update(
                f"Rating: {self.media_info.get('rating', '0.0')}({self.media_info.get('num_ratings', 0)})",
            )

            genre_ids_str = self.media_info.get("genre_ids", "")

            if not genre_ids_str:
                genre_id_list = []
            else:
                genre_id_list = self.media_info.get("genre_ids", "").split(",")

            if media_type == "movie":
                self.genre_names = [
                    constants.MOVIE_GENRE_MAP[int(id)] for id in genre_id_list
                ]

            elif media_type == "tv":
                self.genre_names = [
                    constants.TV_GENRE_MAP[int(id)] for id in genre_id_list
                ]
            else:
                self.genre_names = []

            self.genres_label.update(f"Genres: {self.genre_names}")

            self.overview_label.update(f"{self.media_info.get('overview', '')}")

        except Exception as e:
            raise Exception(e)
