import calendar

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, Static

MONTHS = list(calendar.month_name)[1:]


class DiaryEntryModal(ModalScreen):
    BINDINGS = [("escape", "exit", "Close modal"), ("x", "temp", "temp")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp = "Spiderman: Brand New Day of Scho"

    def compose(self):
        shortened = self.temp

        if len(shortened) > 32:
            shortened = shortened[:29] + "..."

        yield Vertical(
            Label(f'Watched "{shortened}" on:'),
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
            Container(Button("ADD")),
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

    def action_exit(self):
        self.dismiss()
