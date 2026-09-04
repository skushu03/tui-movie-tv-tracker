import datetime

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Label

import tui_movie_tv_tracker.database as database

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
HIGHLIGHT_COLOUR = "#0178d4"


class WatchStats(Vertical, can_focus=True):
    class Selected(Message):
        def __init__(self, year, month, *args, **kwargs):
            self.month = month
            self.year = year
            super().__init__(*args, **kwargs)

        @property
        def control(self):
            pass

    BINDINGS = [
        ("j", "prev_year", "View prev year stats"),
        ("J", "prev_year", "View prev year stats"),
        ("k", "next_year", "View next year stats"),
        ("K", "next_year", "View next year stats"),
        ("h", "prev_month", "View prev month stats"),
        ("H", "prev_month", "View prev month stats"),
        ("l", "next_month", "View next month stats"),
        ("L", "next_month", "View next month stats"),
        ("enter", "select_month", "Select month to view diary entries"),
    ]

    def __init__(self, pane_title=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = pane_title if pane_title else "Watch Stats"

        self.year = datetime.date.today().year
        self.month = datetime.date.today().month

    def compose(self):
        yield Label(str(self.year), id="watch-stats-year")
        yield Horizontal(
            *(
                Vertical(
                    Label("", classes="watch-stats-tv-bar"),
                    Label("", classes="watch-stats-movie-bar"),
                    classes="watch-stats-bar",
                )
                for _ in range(12)
            ),
            id="watch-stats-numbers",
        )
        yield Horizontal(
            *(Label(m, classes="watch-stats-month") for m in MONTHS),
            id="watch-stats-months-row",
        )

    def on_mount(self):
        self.refresh_content(self.year)

    def refresh_content(self, year=None):
        try:
            if year:
                self.year = year
                self.year_label = self.query_one("#watch-stats-year")
                self.year_label.update(str(self.year))

            watched_stats = database.get_watched_stats(self.app.db, self.year)

            movie_bars = self.query(".watch-stats-movie-bar")
            tv_bars = self.query(".watch-stats-tv-bar")

            self.query(".watch-stats-month")[
                self.month - 1
            ].styles.background = HIGHLIGHT_COLOUR

            for i in range(12):
                movie_bars[i].styles.display = "none"
                tv_bars[i].styles.display = "none"

                # movie_bars[i].update("")
            if watched_stats:
                max_total = max(i["total_count"] for i in watched_stats)

                for info in watched_stats:
                    month_index = int(info["month"][5:]) - 1

                    if info["movie_count"]:
                        movie_bars[
                            month_index
                        ].styles.height = (
                            f"{(info['movie_count'] / max_total * 100):.0f}%"
                        )

                        movie_bars[month_index].styles.display = "block"

                    if info["tv_count"]:
                        tv_bars[
                            month_index
                        ].styles.height = f"{(info['tv_count'] / max_total * 100):.0f}%"

                        tv_bars[month_index].styles.display = "block"

        except Exception as e:
            self.app.notify(str(e))

    def action_prev_year(self):
        self.year -= 1
        self.refresh_stats(self.year)

    def action_next_year(self):
        self.year += 1
        self.refresh_stats(self.year)

    def action_prev_month(self):
        old_month = self.month
        self.month = (self.month - 1) % 12

        month_labels = self.query(".watch-stats-month")

        month_labels[old_month - 1].styles.background = "transparent"
        month_labels[self.month - 1].styles.background = HIGHLIGHT_COLOUR

    def action_next_month(self):
        old_month = self.month
        self.month = (self.month + 1) % 12

        month_labels = self.query(".watch-stats-month")

        month_labels[old_month - 1].styles.background = "transparent"
        month_labels[self.month - 1].styles.background = HIGHLIGHT_COLOUR

    def action_select_month(self):
        self.post_message(self.Selected(self.year, self.month))
