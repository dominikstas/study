import tkinter as tk
from tkinter import messagebox
import sqlite3
from ui import UI

class app:
    def __init__(self, master):
        self.master = master
        self.master.title("Subject-based Note Manager")
        self.master.geometry("1000x600")
        self.master.configure(bg="#f0f0f0")

        self.ui = UI(self.master)
        self.create_db()
        self.create_widgets()
        self.load_subjects()

    def create_db(self):
        self.conn = sqlite3.connect("notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subjects
                              (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                              (id INTEGER PRIMARY KEY, subject_id INTEGER, content TEXT,
                               FOREIGN KEY (subject_id) REFERENCES subjects(id))''')
        self.conn.commit()

    def create_widgets(self):
        widgets = self.ui.create_main_frame()
        self.subject_tree, self.subject_entry, add_button, remove_button, \
        self.note_text, save_button, clear_button, flashcard_button = widgets

        add_button.config(command=self.add_subject)
        remove_button.config(command=self.remove_subject)
        save_button.config(command=self.save_note)
        clear_button.config(command=self.clear_note)
        flashcard_button.config(command=self.generate_flashcards)

        self.subject_tree.bind('<<TreeviewSelect>>', self.load_notes)

    def load_subjects(self):
        self.subject_tree.delete(*self.subject_tree.get_children())
        self.cursor.execute("SELECT name FROM subjects ORDER BY name")
        for subject in self.cursor.fetchall():
            self.subject_tree.insert("", "end", text=subject[0], values=(subject[0],))

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        if subject:
            try:
                self.cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subject,))
                self.conn.commit()
                self.load_subjects()
                self.subject_entry.delete(0, tk.END)
                self.ui.show_subject_info(f"Subject '{subject}' added successfully!")
            except sqlite3.IntegrityError:
                self.ui.show_subject_info(f"Error: Subject '{subject}' already exists!")
        else:
            self.ui.show_subject_info("Error: Subject name cannot be empty!")

    def remove_subject(self):
        selection = self.subject_tree.selection()
        if selection:
            subject = self.subject_tree.item(selection[0])['text']
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{subject}' and all its notes?")
            if confirm:
                self.cursor.execute("DELETE FROM notes WHERE subject_id = (SELECT id FROM subjects WHERE name = ?)", (subject,))
                self.cursor.execute("DELETE FROM subjects WHERE name = ?", (subject,))
                self.conn.commit()
                self.load_subjects()
                self.clear_note()
                self.ui.show_subject_info(f"Subject '{subject}' removed successfully!")
        else:
            self.ui.show_subject_info("Error: Please select a subject to remove!")

    def load_notes(self, event):
        selection = self.subject_tree.selection()
        if selection:
            subject = self.subject_tree.item(selection[0])['text']
            self.cursor.execute("SELECT content FROM notes WHERE subject_id = (SELECT id FROM subjects WHERE name = ?)", (subject,))
            note = self.cursor.fetchone()
            self.note_text.delete(1.0, tk.END)
            if note:
                self.note_text.insert(tk.END, note[0])

    def save_note(self):
        selection = self.subject_tree.selection()
        if selection:
            subject = self.subject_tree.item(selection[0])['text']
            content = self.note_text.get(1.0, tk.END).strip()
            self.cursor.execute("INSERT OR REPLACE INTO notes (subject_id, content) VALUES ((SELECT id FROM subjects WHERE name = ?), ?)", (subject, content))
            self.conn.commit()
            self.ui.show_note_info("Note saved successfully!")
        else:
            self.ui.show_note_info("Error: Please select a subject to save the note!")

    def clear_note(self):
        self.note_text.delete(1.0, tk.END)

    def generate_flashcards(self):
        content = self.note_text.get(1.0, tk.END).strip()
        lines = content.split("\n")
        flashcards = []

        for line in lines:
            if "-" in line:
                parts = line.split("-", 1)
                question = parts[0].strip()
                answer = parts[1].strip()
                if question and answer:
                    flashcards.append((question, answer))

        if flashcards:
            self.ui.start_flashcard_mode
        else:
            self.ui.show_note_info("No valid flashcards found!")
 
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = app(root)
    root.mainloop()