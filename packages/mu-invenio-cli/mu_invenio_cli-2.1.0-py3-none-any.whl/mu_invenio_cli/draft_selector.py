#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Draft selector GUI for the MU Invenio CLI application."""


import tkinter as tk
from tkinter import simpledialog, messagebox
from mu_invenio_cli.services.record_service import RecordService


class DraftSelector:
    def __init__(self, context):
        self.context = context
        self.root = tk.Tk()
        self.root.title("Select Draft")
        self.root.geometry("750x440")
        self.selected_draft = None
        self.page = 1
        self.query = ""
        self.user_drafts = []
        self.service = RecordService(self.context)

        self.search_var = tk.StringVar()
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind("<Return>", self.on_search)
        tk.Button(search_frame, text="Search", command=self.on_search).pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self.root, width=100, height=15)
        self.listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.listbox.bind('<Double-1>', self.on_select)

        page_frame = tk.Frame(self.root)
        page_frame.pack(fill=tk.X, padx=10, pady=5)
        self.prev_btn = tk.Button(page_frame, text="Previous", command=self.previous_page)
        self.prev_btn.pack(side=tk.LEFT)
        self.next_btn = tk.Button(page_frame, text="Next", command=self.next_page)
        self.next_btn.pack(side=tk.LEFT, padx=(5, 0))

        self.page_label = tk.Label(page_frame, text=f"Page {self.page}")
        self.page_label.pack(side=tk.LEFT, padx=(15, 0))

        tk.Label(page_frame, text="Go to page:").pack(side=tk.LEFT, padx=(15, 0))
        self.page_var = tk.StringVar()
        self.page_entry = tk.Entry(page_frame, textvariable=self.page_var, width=5)
        self.page_entry.pack(side=tk.LEFT)
        self.page_entry.bind("<Return>", self.goto_page)
        tk.Button(page_frame, text="Go", command=self.goto_page).pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(btn_frame, text="Select", command=self.on_select).pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=5)

        self.fetch_user_drafts()

    def fetch_user_drafts(self):
        self.user_drafts = self.service.get_user_records(query=self.query, page=self.page)
        self.update_listbox()
        self.page_label.config(text=f"Page {self.page}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for record in self.user_drafts:
            title = record.get("metadata", {}).get("titles", [{}])[0].get("titleText", "No Title")
            record_id = record.get("id", "N/A")
            state = record.get("state", "unknown")
            display = f"{title} - {record_id} - {state}"
            self.listbox.insert(tk.END, display)
            if state == "published":
                self.listbox.itemconfig(tk.END, {'fg': 'gray'})

    def on_search(self, event=None):
        self.query = self.search_var.get()
        self.page = 1
        self.fetch_user_drafts()

    def next_page(self):
        self.page += 1
        self.fetch_user_drafts()

    def previous_page(self):
        if self.page > 1:
            self.page -= 1
            self.fetch_user_drafts()

    def goto_page(self, event=None):
        try:
            page = int(self.page_var.get())
            if page > 0:
                self.page = page
                self.fetch_user_drafts()
            else:
                messagebox.showwarning("Page Input", "Page number must be positive.")
        except ValueError:
            messagebox.showwarning("Page Input", "Invalid page number.")

    def on_select(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Select Draft", "Please select a draft.")
            return
        idx = selection[0]
        record = self.user_drafts[idx]
        if record.get("state") == "published":
            messagebox.showwarning("Select Draft", "Cannot select a published record.")
            return
        self.selected_draft = record
        self.root.destroy()

    def on_cancel(self):
        self.selected_draft = None
        self.root.destroy()

    def select_draft(self):
        self.root.mainloop()
        return self.selected_draft
