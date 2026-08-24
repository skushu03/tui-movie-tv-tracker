from textual import on
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class InputModal(ModalScreen):
    BINDINGS = [("escape", "close", "Close modal")]

    def __init__(self, prompt, max_len, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.max_len = max_len

    def compose(self):
        yield Vertical(
            Label(self.prompt),
            Input(classes="modal-input", max_length=self.max_len),
            classes="modal-container",
        )

    def on_mount(self):
        # focused when modla pops up
        self.query_one(".modal-input").focus()

    @on(Input.Submitted, ".modal-input")
    def input_submitted(self, event):
        if event.value.strip():
            # Close the modal and send the string value back to the main screen
            self.dismiss(event.value.strip()[: self.max_len])
        else:
            self.dismiss("")

    def action_close(self):
        self.dismiss("")
