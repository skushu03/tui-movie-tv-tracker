from textual.widgets import Label
from textual.widgets import ListItem as TextualListItem

import tui_movie_tv_tracker.database as database
from tui_movie_tv_tracker.base_widgets.list_view import ListView
from tui_movie_tv_tracker.modals.input_modal import InputModal


class ListItem(TextualListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

    def compose(self):
        yield Label(self.item_data.get("name", ""))


class Lists(ListView):
    BINDINGS = [
        ("a", "create_list", "Create new list"),
        ("A", "create_list", "Create new list"),
        ("d", "delete_list", "Delete list"),
        ("D", "delete_list", "Delete list"),
    ]

    def __init__(self, pane_title=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = pane_title if pane_title else "Lists"
        self.selected_item = None

    async def on_mount(self):
        await self.refresh_content()

        if self.children:
            self.selected_item = self.children[0]

    async def refresh_content(self):
        # self.app.notify("Refreshing lists...")
        try:
            old_index = self.index
            await self.clear()

            new_items = database.get_lists(self.app.db)

            new_widgets = [ListItem(n) for n in new_items]

            await self.extend(new_widgets)

            if not old_index:
                self.index = 0
            elif old_index >= len(self.children):
                self.index = len(self.children) - 1
            else:
                self.index = old_index

            if self.index is not None:
                self.selected_item = self.children[self.index]
            # self.app.notify("Lists updated")

        except Exception as e:
            self.app.notify(str(e), severity="warning")

    async def action_create_list(self):
        async def handle_create_list(list_name):
            try:
                if not list_name:
                    return

                database.create_list(self.app.db, list_name)
                await self.refresh_content()

            except ValueError as e:
                self.app.notify(str(e), severity="warning")
            except Exception as e:
                raise Exception(e)

        await self.app.push_screen(
            InputModal("Enter new list name:"), callback=handle_create_list
        )

    async def action_delete_list(self):
        async def handle_delete_list(confirmation):
            if confirmation not in ("y", "Y"):
                return

            try:
                selected_list_name = self.highlighted_child.item_data["name"]
                database.delete_list(self.app.db, selected_list_name)

                await self.refresh_content()

            except Exception as e:
                self.app.notify(str(e), severity="warning")

        await self.app.push_screen(
            InputModal(
                "Are you sure you want to delete this list? (y/N)",
                1,
            ),
            callback=handle_delete_list,
        )
