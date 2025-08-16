import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
import webbrowser
from .storage import load_prompt, save_prompt
from .models import Prompt
from .config import load_config, save_config


class PromptApp(tk.Tk):
    """Tkinter based prompt manager."""
    def __init__(self) -> None:
        super().__init__()
        self.title('Prompt Manager')
        self.cfg = load_config()
        self.prompt_dir = self.cfg.get('prompt_dir') or os.getcwd()
        self.llms = self.cfg.get('llms', {})
        self.prompts = []
        self.current_prompt: Prompt | None = None
        self._save_job = None

        self.listbox = tk.Listbox(self, width=30)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        right = tk.Frame(self)
        right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.text = tk.Text(right, wrap='word')
        self.text.pack(expand=True, fill=tk.BOTH)
        self.text.bind('<<Modified>>', self.on_modified)

        self.status = tk.StringVar(value='Idle')
        tk.Label(self, textvariable=self.status).pack(side=tk.BOTTOM, fill=tk.X)

        btn_frame = tk.Frame(right)
        btn_frame.pack(fill=tk.X)
        for name, url in self.llms.items():
            tk.Button(btn_frame, text=name, command=lambda u=url: webbrowser.open(u)).pack(side=tk.LEFT)

        menubar = tk.Menu(self)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Set Prompt Directory', command=self.choose_dir)
        menubar.add_cascade(label='Settings', menu=settings_menu)
        self.config(menu=menubar)

        self.load_prompt_list()
        threading.Thread(target=self.monitor_current_file, daemon=True).start()

    def load_prompt_list(self) -> None:
        self.prompts = []
        self.listbox.delete(0, tk.END)
        if not os.path.isdir(self.prompt_dir):
            return
        for fname in os.listdir(self.prompt_dir):
            if fname.endswith('.md'):
                path = os.path.join(self.prompt_dir, fname)
                try:
                    p = load_prompt(path)
                    p.filepath = path  # type: ignore[attr-defined]
                    self.prompts.append(p)
                    self.listbox.insert(tk.END, f"{p.id}: {p.name}")
                except Exception:
                    continue

    def on_select(self, _event) -> None:
        idx = self.listbox.curselection()
        if not idx:
            return
        prompt = self.prompts[idx[0]]
        self.current_prompt = prompt
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, prompt.content)
        self.text.edit_modified(False)
        self.status.set('Loaded')

    def on_modified(self, _event) -> None:
        if self.text.edit_modified():
            if self._save_job:
                self.after_cancel(self._save_job)
            self._save_job = self.after(2000, self.auto_save)
            self.status.set('Modified')
            self.text.edit_modified(False)

    def auto_save(self) -> None:
        if not self.current_prompt:
            return
        self.status.set('Saving...')
        self.current_prompt.content = self.text.get('1.0', tk.END)
        save_prompt(self.current_prompt, self.current_prompt.filepath)  # type: ignore[arg-type]
        self.status.set('Saved')

    def choose_dir(self) -> None:
        directory = filedialog.askdirectory()
        if directory:
            self.prompt_dir = directory
            self.cfg['prompt_dir'] = directory
            save_config(self.cfg)
            self.load_prompt_list()

    def monitor_current_file(self) -> None:
        last_mtime = 0.0
        while True:
            time.sleep(1)
            if not self.current_prompt:
                continue
            path = self.current_prompt.filepath  # type: ignore[attr-defined]
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if mtime != last_mtime:
                last_mtime = mtime
                prompt = load_prompt(path)
                self.current_prompt.content = prompt.content
                self.text.delete('1.0', tk.END)
                self.text.insert(tk.END, prompt.content)
                self.status.set('Updated from disk')


def main() -> None:
    app = PromptApp()
    app.mainloop()


if __name__ == '__main__':
    main()
