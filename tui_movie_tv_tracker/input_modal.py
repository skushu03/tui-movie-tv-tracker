from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class InputModal(ModalScreen):
    def __init__(self, prompt, max_len, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.max_len = max_len

    def compose(self):
        yield Vertical(
            Label(self.prompt),
            Input(id="modal-input", max_length=self.max_len),
            id="modal-container",
        )

    def on_mount(self):
        # focused when modla pops up
        self.query_one("#modal-input").focus()

    def on_input_submitted(self, event):
        if event.value.strip():
            # Close the modal and send the string value back to the main screen
            self.dismiss(event.value.strip()[: self.max_len])
        else:
            self.dismiss("")

    def on_key(self, event):
        if event.key == "escape":
            self.dismiss("")
