import calendar
import datetime

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select

import tui_movie_tv_tracker.database as database

MONTHS = list(calendar.month_name)[1:]

MIN_YEAR = 1940


class DateSelectModal(ModalScreen):
    BINDINGS = [("escape", "exit", "Close modal")]

    def __init__(self, media_title, prompt="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_title = media_title
        self.curr_year = datetime.date.today().year
        self.year = 0
        self.month = 0
        self.day = 0

    def compose(self):
        if len(self.media_title) > 32:
            self.media_title = self.media_title[:29] + "..."

        today = datetime.datetime.today()

        yield Vertical(
            Label(f'Watched "{self.media_title}" on:'),
            Horizontal(
                Select.from_values(
                    [y for y in range(self.curr_year, MIN_YEAR - 1, -1)],
                    prompt="Year",
                    value=today.year,
                    allow_blank=False,
                    id="diary-entry-year",
                ),
                Select.from_values(
                    MONTHS,
                    prompt="Month",
                    value=today.strftime("%B"),
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

        days_select.set_options(
            [(f"{d:02d}", f"{d:02d}") for d in range(1, month_range + 1)]
        )
        days_select.value = f"{datetime.datetime.today().day:02d}"

        self.year = year
        self.month = month

    @on(Select.Changed, "#diary-entry-day")
    def update_day_var(self):
        self.day = int(self.query_one("#diary-entry-day").selection)

    @on(Button.Pressed, "#diary-entry-button")
    def add_entry(self):
        try:
            date_str = f"{self.year}-{self.month:02d}-{self.day:02d}"

        except Exception as e:
            self.app.notify(str(e), severity="warning")
        finally:
            self.dismiss(date_str)

    def action_exit(self):
        self.dismiss(None)
