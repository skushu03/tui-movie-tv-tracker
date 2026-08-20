from textual.widgets import ListView as TextualListView


class ListView(TextualListView):
    BINDINGS = [
        ("j", "cursor_down", "Navigate down"),
        ("J", "cursor_down", "Navigate down"),
        ("k", "cursor_up", "Navigate Up"),
        ("K", "cursor_up", "Navigate Up"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
