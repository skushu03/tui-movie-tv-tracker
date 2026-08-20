import copy

from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label
from textual.widgets import ListItem as TextualListItem
from textual.widgets import ListView as TextualListView


class Checklist(TextualListView):
    BINDINGS = [
        ("j", "nav_down", "Navigate down"),
        ("J", "nav_down", "Navigate down"),
        ("k", "nav_up", "Navigate Up"),
        ("K", "nav_up", "Navigate Up"),
        ("space", "toggle_select", "Toggle item select"),
    ]

    def __init__(self, lists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lists = lists
        self.changes = {}  # list_name: -1, 0, 1

    def action_nav_down(self):
        self.index += 1

    def action_nav_up(self):
        self.index -= 1

    def action_toggle_select(self):
        self.highlighted_child.item_data[
            "contains"
        ] = not self.highlighted_child.item_data["contains"]

        selected_list_name = self.highlighted_child.item_data["name"]

        if self.changes.get(selected_list_name):
            self.changes[selected_list_name] = 0
        else:
            if self.highlighted_child.item_data["contains"]:
                self.changes[selected_list_name] = 1
            else:
                self.changes[selected_list_name] = -1

        highlighted_label = self.highlighted_child.query_one("Label")

        highlighted_label.update(
            f"\[x] {selected_list_name}"
            if self.highlighted_child.item_data["contains"]
            else f"\[ ] {selected_list_name}"
        )


class ListItem(TextualListItem):
    def __init__(self, item_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_data = item_data

    def compose(self):
        yield Label(
            f"\[x] {self.item_data['name']}"
            if self.item_data["contains"]
            else f"\[ ] {self.item_data['name']}"
        )


class ChecklistModal(ModalScreen):
    BINDINGS = [
        ("escape", "exit", "Close modal without saving changes"),
        ("enter", "apply_and_exit", "Close modal and save changes"),
    ]

    def __init__(self, prompt, lists, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.lists = lists  # [{"name": x, "id": x, "last_updated": x}, ...]
        # self.max_len 36

    def compose(self):
        yield Vertical(
            Label(self.prompt),
            Checklist(
                self.lists,
                *[ListItem(li) for li in self.lists],
                classes="checklist-view",
            ),
            classes="modal-container",
        )

    def on_mount(self):
        self.query_one(".checklist-view").focus()

    def action_exit(self):
        # self.app.notify(str(self.lists))
        self.dismiss({})

    def action_apply_and_exit(self):
        self.dismiss(self.query_one("Checklist").changes)
