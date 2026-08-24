import calendar

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, Static

import tui_movie_tv_tracker.database as database

MONTHS = list(calendar.month_name)[1:]


class DiaryEntryModal(ModalScreen):
    BINDINGS = [("escape", "exit", "Close modal"), ("x", "temp", "temp")]

    def __init__(self, media_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_info = media_info

        self.year = 0
        self.month = 0
        self.day = 0

    def compose(self):
        media_title = self.media_info["title"]

        if len(media_title) > 32:
            media_title = media_title[:29] + "..."

        yield Vertical(
            Label(f'Watched "{media_title}" on:'),
            Horizontal(
                Select.from_values(
                    [y for y in range(2026, 2000 - 1, -1)],
                    prompt="Year",
                    allow_blank=False,
                    id="diary-entry-year",
                ),
                Select.from_values(
                    MONTHS,
                    prompt="Month",
                    allow_blank=False,
                    id="diary-entry-month",
                ),
                Select.from_values(
                    [1],
                    prompt="Day",
                    allow_blank=False,
                    id="diary-entry-day",
                ),
            ),
            Container(Button("ADD", id="diary-entry-button")),
            classes="modal-container",
            id="diary-entry-modal",
        )

    @on(Select.Changed, "#diary-entry-year")
    @on(Select.Changed, "#diary-entry-month")
    def update_day_range(self):
        year = int(self.query_one("#diary-entry-year").selection)
        month = MONTHS.index(str(self.query_one("#diary-entry-month").selection)) + 1
        days_select = self.query_one("#diary-entry-day")

        month_range = calendar.monthrange(year, month)[1]

        days_select.set_options([(str(d), str(d)) for d in range(1, month_range + 1)])

        self.year = year
        self.month = month

    @on(Select.Changed, "#diary-entry-day")
    def update_day_var(self):
        self.day = int(self.query_one("#diary-entry-day").selection)

    @on(Button.Pressed, "#diary-entry-button")
    def add_entry(self):
        try:
            database.add_diary_entry(
                self.app.db,
                self.media_info,
                self.app.watched,
                f"{self.year}-{self.month:02d}-{self.day:02d}",
            )

            self.app.notify(f'Diary entry added for "{self.media_info["title"]}"')

        except Exception as e:
            self.app.notify(str(e), severity="warning")
        finally:
            self.dismiss()

    def action_exit(self):
        self.dismiss()
