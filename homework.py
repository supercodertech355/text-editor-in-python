"""A small text editor built using Tkinter."""

from tkinter import Button, END, Frame, Label, Tk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class TextEditor:
    def __init__(self, window: Tk) -> None:
        self.window = window
        self.filepath: str | None = None
        self.is_dirty = False

        self.window.title("Text Editor")
        self.window.geometry("800x600")
        self.window.minsize(500, 350)

        toolbar = self._make_toolbar()
        toolbar.pack(fill="x")

        self.editor = ScrolledText(window, wrap="word", undo=True)
        self.editor.pack(fill="both", expand=True)
        self.editor.bind("<<Modified>>", self._on_modified)
        self.editor.edit_modified(False)

        self.status = self._make_status_bar()
        self.status.pack(fill="x")
        self.window.protocol("WM_DELETE_WINDOW", self._close)

    def _make_toolbar(self):
        toolbar = Frame(self.window, padx=6, pady=6)
        for label, command in (
            ("New", self.new_file),
            ("Open", self.open_file),
            ("Save", self.save_file),
            ("Save As", self.save_file_as),
        ):
            Button(toolbar, text=label, command=command).pack(
                side="left", padx=(0, 6)
            )
        return toolbar

    def _make_status_bar(self):
        return Label(self.window, text="Ready", anchor="w", padx=8, pady=4)

    def _on_modified(self, _event=None) -> None:
        if self.editor.edit_modified():
            self.is_dirty = True
            self.editor.edit_modified(False)
            self._update_title()

    def _update_title(self) -> None:
        name = self.filepath.replace("\\", "/").rsplit("/", 1)[-1] if self.filepath else "Untitled"
        marker = " *" if self.is_dirty else ""
        self.window.title(f"{name}{marker} - Text Editor")

    def _confirm_discard_changes(self) -> bool:
        if not self.is_dirty:
            return True

        choice = messagebox.askyesnocancel(
            "Unsaved changes",
            "Save changes before continuing?",
            parent=self.window,
        )
        if choice is None:
            return False
        if choice:
            return self.save_file()
        return True

    def new_file(self) -> None:
        if not self._confirm_discard_changes():
            return
        self.editor.delete("1.0", END)
        self.filepath = None
        self.is_dirty = False
        self.editor.edit_modified(False)
        self.status.config(text="New document")
        self._update_title()

    def open_file(self) -> None:
        if not self._confirm_discard_changes():
            return
        selected = filedialog.askopenfilename(
            parent=self.window,
            title="Open text file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if not selected:
            return

        try:
            with open(selected, "r", encoding="utf-8-sig") as input_file:
                text = input_file.read()
        except (OSError, UnicodeError) as error:
            messagebox.showerror("Open failed", str(error), parent=self.window)
            return
        self._load_document(selected, text)

    def save_file(self) -> bool:
        if self.filepath is None:
            return self.save_file_as()
        return self._write_file(self.filepath)

    def save_file_as(self) -> bool:
        selected = filedialog.asksaveasfilename(
            parent=self.window,
            title="Save text file",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if not selected:
            return False
        return self._write_file(selected)

    def _write_file(self, path: str) -> bool:
        text = self.editor.get("1.0", "end-1c")
        try:
            with open(path, "w", encoding="utf-8", newline="") as output_file:
                output_file.write(text)
        except OSError as error:
            messagebox.showerror("Save failed", str(error), parent=self.window)
            return False

        self.filepath = path
        self.is_dirty = False
        self.editor.edit_modified(False)
        self._update_title()
        self.status.config(text=f"Saved {path}")
        return True

    def _load_document(self, path: str, text: str) -> None:
        self.editor.delete("1.0", END)
        self.editor.insert("1.0", text)
        self.filepath = path
        self.is_dirty = False
        self.editor.edit_modified(False)
        self._update_title()
        self.status.config(text=f"Opened {path}")

    def _close(self) -> None:
        if self._confirm_discard_changes():
            self.window.destroy()


def main() -> None:
    window = Tk()
    TextEditor(window)
    window.mainloop()


if __name__ == "__main__":
    main()