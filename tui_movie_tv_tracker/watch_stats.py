from textual.containers import Horizontal, Vertical
from textual.widgets import Label, Sparkline, Static

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


class WatchStats(Vertical, can_focus=True):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Watch Stats"

        self.year = 2026

    def compose(self):
        yield Label("2026")
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
        yield Horizontal(*(Label(m) for m in MONTHS), id="watch-stats-months")

    def on_mount(self):
        try:
            watched_stats = database.get_watched_stats(self.app.db, self.year)

            max_total = max(i["total_count"] for i in watched_stats)

            movie_bars = self.query(".watch-stats-movie-bar")
            tv_bars = self.query(".watch-stats-tv-bar")
            # self.app.notify(str(max_total))

            for info in watched_stats:
                month_index = int(info["month"][5:]) - 1

                movie_bars[
                    month_index
                ].styles.height = f"{(info['movie_count'] / max_total * 100):.0f}%"
                movie_bars[month_index].styles.width = 3

                tv_bars[
                    month_index
                ].styles.height = f"{(info['tv_count'] / max_total * 100):.0f}%"
                tv_bars[month_index].styles.width = 3

        except Exception as e:
            self.app.notify(str(e))
