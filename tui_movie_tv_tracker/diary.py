import calendar
import datetime

from textual.containers import Horizontal, Vertical
from textual.widgets import Label, ListItem

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.base_widgets.list_view import ListView


class EntryList(ListView):
    BINDINGS = [("tab", "screen.next_focus", "Switch focus to next pane")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_focus(self):
        if not self.index:
            self.index = 0


class EntryItem(ListItem):
    def __init__(self, item_info, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.item_info = item_info
        self.day = item_info.get("date", "")[8:10]
        self.title = item_info.get("title", "[No Title Found]")

    def compose(self):
        yield Horizontal(Label(self.day), Label(self.title))


class Diary(Vertical, can_focus=True):
    def __init__(self, pane_title=None, *args, **kwargs):
        # why am i passing num_movie and num_tv?????
        super().__init__(*args, **kwargs)
        self.border_title = pane_title if pane_title else "Diary"

        self.year = datetime.date.today().year
        self.month = datetime.date.today().month

        self.str_month = calendar.month_name[self.month]

        self.num_movie = 0
        self.num_tv = 0

    def compose(self):
        yield Label(f"Movies: {self.num_movie}", id="diary-num-movie")
        yield Label(f"TV: {self.num_tv}", id="diary-num-tv")
        yield Label(str(self.year), id="diary-year")
        yield Label(self.str_month, id="diary-month")
        yield EntryList(*[], id="entry-list")

    async def on_mount(self):
        await self.refresh_content(self.num_movie, self.num_tv)

    async def refresh_content(self, year=None, month=None):
        try:
            if year:
                self.year = int(year)
            if month:
                if month < 1 or month > 12:
                    raise ValueError(f"Invalid month number: {month}")

                self.month = int(month)
                self.str_month = calendar.month_name[self.month]

            self.query_one("#diary-year").update(str(self.year))
            self.query_one("#diary-month").update(self.str_month)
            ###
            diary_entries = database.get_diary_entries(
                self.app.db, self.year, self.month
            )

            self.num_movie = 0
            self.num_tv = 0
            for entry in diary_entries:
                if entry["media_type"] == "movie":
                    self.num_movie += 1
                else:
                    self.num_tv += 1

            self.query_one("#diary-num-movie").update(f"Movies: {self.num_movie}")
            self.query_one("#diary-num-tv").update(f"TV: {self.num_tv}")
            ###
            list_view = self.query_one("#entry-list")
            await list_view.clear()
            new_list_items = [EntryItem(e) for e in diary_entries]
            await list_view.extend(new_list_items)

        except ValueError as e:
            self.app.notify(f"Value Error: {e}")
        except Exception as e:
            self.app.notify(str(e))

    def on_focus(self):
        self.query_one("#entry-list").focus()
