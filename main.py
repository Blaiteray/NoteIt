"""
A note keeping tool
"""
import sqlite3 
database_connection = sqlite3.connect('note_db.db')
database_connection.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY,date_time TEXT, note TEXT)")
database_connection.commit()

import os
os.environ['KIVY_IMAGE'] = 'pil'
os.environ["KIVY_NO_CONSOLELOG"] = "1"

import kivy
kivy.require('2.1.0')
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics','resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App 
from kivy.core.window import Window
# Window.minimum_width, Window.minimum_height = (800, 600)
Window.clearcolor = (0.05, 0.1, 0.15, 1)
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
# from kivy.uix.screenmanager import Screen, ScreenManager
from hovekivy import HoverBehavior

with Window.canvas.before:
    Color(0.9, 0.8, 0.7, 0.5) 
    # Image(source='bg_img.jpg', size=(800, 600))
    Rectangle(size=Window.size, source="bg_img.jpg", pos=(0,0))


class HoverButton(Button, HoverBehavior):
    def __init__(self, enter, leave, **kwargs):
        super(HoverButton, self).__init__(**kwargs)
        self.enter = enter
        self.leave = leave
        # self.background_color = (0, 0, 0, 1)
    def on_enter(self):
        self.background_color = self.enter
    def on_leave(self):
        self.background_color = self.leave


class HoverTextInput(TextInput, HoverBehavior):
    def __init__(self, enter, leave, **kwargs):
        super(HoverTextInput, self).__init__(**kwargs)
        self.enter = enter
        self.leave = leave
        # self.background_color = (0, 0, 0, 1)
    def on_enter(self):
        self.background_color = self.enter
    def on_leave(self):
        self.background_color = self.leave


class MemoryPopup(Popup):
    def __init__(self, **kwargs):
        super(MemoryPopup, self).__init__(**kwargs)

    def on_dismiss(self):
        self.clear_widgets()

    def clear_widgets(self):
        for child in self.content.children:
            if isinstance(child, Popup):
                child.clear_widgets()
            else:
                self.content.remove_widget(child)


def remove_widget_recursive(widget):
    for child in widget.children:
        remove_widget_recursive(child)
    if widget.parent:
        widget.parent.remove_widget(widget)


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.new_icon = HoverButton((0.1,0.2,0,0.5), (0.1,0.2,0,0.9),
            text="N", 
            background_color=(0.1,0.2,0,0.9),
            pos=(5,555), 
            size=(40, 40),
            font_name="AnonymousPro-Bold",
            font_size='20sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        self.new_icon.bind(on_release=self.new_selection_callback)

        self.main_label = Label(text="NoteIt", 
            pos=(50,555), 
            size=(300, 40), 
            size_hint=(None, None), 
            font_size='28sp', 
            # color=(0.9, 0.8, 0.7, 1),
            font_name="AnonymousPro-Bold")
        # with self.main_label.canvas:
        #     Color(0, 1, 0, 0.25)
        #     Rectangle(pos=self.main_label.pos, size=self.main_label.size)
        self.search_box = HoverTextInput((1, 1, 1, 1), (1, 0.95, 0.9, 1),
            text='',
            hint_text = 'Search from notes',
            background_color=(1, 0.95, 0.9, 1),
            pos=(360, 560), 
            size=(430, 30), 
            font_name="AnonymousPro-Regular",
            multiline=False,
            size_hint=(None, None))
        self.search_icon = HoverButton((0.1,0.2,0,0.8), (0.1,0.2,0,0.95),
            text="Go", 
            background_color=(0.1,0.2,0,0.9),
            pos=(730,563), 
            size=(28, 25),
            font_name="AnonymousPro-Bold",
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        self.search_icon.bind(on_release=self.search_icon_callback)
        self.search_reset_icon = HoverButton((0.1,0.2,0,0.8), (0.1,0.2,0,0.95),
            text="X", 
            background_color=(0.1,0.2,0,0.9),
            pos=(760,563), 
            size=(25, 25),
            # font_name="AnonymousPro-Bold",
            font_size='18sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        self.search_reset_icon.bind(on_release=self.search_reset_icon_callback)


        with self.canvas:
            Color(0.0, 0.0, 0.0, 0.3)
            Rectangle(pos=(60, 80), size=(680, 390))

        
        self.note_list_panel = self.show_filtered_notes('')



        self.add_widget(self.new_icon)
        self.add_widget(self.main_label)
        self.add_widget(self.search_box)
        self.add_widget(self.search_icon)
        self.add_widget(self.search_reset_icon)
        self.add_widget(self.note_list_panel)


    def show_filtered_notes(self, key):
        rows = list(database_connection.execute("SELECT * FROM notes WHERE note LIKE ?", ('%'+key+'%',)))
        note_list = []
        for row in rows:
            current_id = " " * (5-len(str(row[0]))) + str(row[0])
            current_datetime = row[1]
            current_note = row[2][:28]
            if len(row[2]) > 28:
                current_note = current_note[:25] + "..."
            else:
                current_note = " " *(28 - len(current_note)) + current_note
            current_note = current_note + "   "
            note_list.append(f"{current_id}    {current_datetime}    {current_note}")
        note_list_container = ScrollView(
            pos=(100, 100), 
            size=(600, 350), 
            size_hint=(None, None),
            scroll_wheel_distance = 100)
        note_button_container = BoxLayout(orientation='vertical',size_hint_y=None, height=len(note_list)*40)
        
        def color_on_enter(btn):
            def temp():
                btn.background_color = (0.7, 0.3, 0.3, 0.3)
            return temp

        for note in note_list:
            note_containing_buttion = HoverButton((0.5, 0.2, 0, 0.0), (0.5, 0.2, 0, 0.5),
                    text=note, 
                    background_color=(0.5, 0.2, 0, 0.5),
                    font_name="AnonymousPro-Bold",
                    font_size='16sp',
                    size_hint_y=None,
                    border=(-20, 16, 20, 16),
                    height=40)
            note_containing_buttion.bind(on_release=self.note_selection_callback)
            note_containing_buttion.on_enter = color_on_enter(note_containing_buttion)
            note_button_container.add_widget(note_containing_buttion)
        note_list_container.add_widget(note_button_container)
        return note_list_container


    def update_note_list_panel(self, key):
        remove_widget_recursive(self.note_list_panel)
        self.note_list_panel = self.show_filtered_notes(key)
        self.add_widget(self.note_list_panel)


    def search_icon_callback(self, i):
        self.update_note_list_panel(self.search_box.text)

    def search_reset_icon_callback(self, i):
        self.search_box.text = ''
        self.update_note_list_panel('')



    def new_selection_callback(self, i):
        content = FloatLayout()
        note = TextInput(hint_text="Write your note...",
            pos=(253, 250), 
            size=(295, 120), 
            font_name="AnonymousPro-Regular",
            size_hint=(None, None))
        note_add_button = HoverButton((0.4,0.7,0.0,0.5), (0.4,0.7,0.0,0.9), 
            text="Add", 
            background_color=(0.4,0.7,0.0,0.9), 
            pos=(315,205), 
            size=(80, 30),
            font_name="AnonymousPro-Bold",
            font_size='16sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        close_popup_button = HoverButton((0.7,0.4,0.0,0.5), (0.7,0.4,0.0,0.9),
            text="Close", 
            background_color=(0.7,0.4,0.0,0.9),
            pos=(400,205), 
            size=(80, 30),
            font_name="AnonymousPro-Bold",
            font_size='16sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        content.add_widget(note)
        content.add_widget(note_add_button)
        content.add_widget(close_popup_button)
        popup = MemoryPopup(content=content, 
            auto_dismiss=False, 
            size_hint=(.4, .4),
            separator_height=1,
            separator_color=(0.9, 1, 1, 1),
            background_color=(0.1, 0, 0, 0.8),
            title_font="AnonymousPro-Bold",
            title_size='16sp',
            title='New Note')

        def add_row_to_db_callback(i):
            selection_of_rows = database_connection.execute("SELECT * FROM notes")
            new_id = len(list(selection_of_rows)) + 1
            datetime = database_connection.execute("SELECT datetime('now')")
            new_datetime = list(datetime)[0][0]
            new_note = note.text
            database_connection.execute("INSERT INTO notes VALUES (?, ?, ?)", (new_id, new_datetime, new_note))
            database_connection.commit()
            # UPDATE NEEDED
            self.update_note_list_panel('')
            popup.dismiss()

        note_add_button.bind(on_release=add_row_to_db_callback)
        close_popup_button.bind(on_press=popup.dismiss)
        popup.open()



    def note_selection_callback(self, i):
        content = FloatLayout()
        selected_id = int((i.text[:5]).strip())
        selected_row = database_connection.execute("SELECT note FROM notes WHERE id=?", (selected_id,))
        note_content = list(selected_row)[0][0]
        note = TextInput(text=note_content,
            pos=(253, 250), 
            size=(295, 120), 
            font_name="AnonymousPro-Regular",
            size_hint=(None, None))
        note.cursor = (0, 0)
        note_edit_button = HoverButton((0.1,0.9,0.2,0.4), (0.1,0.9,0.2,0.8),
            text="OK", 
            background_color=(0.1,0.9,0.2,0.7),
            pos=(400,205), 
            size=(80, 30),
            font_name="AnonymousPro-Bold",
            font_size='16sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        delete_note_button = HoverButton((0.9,0.2,0.1,0.4), (0.9,0.2,0.1,0.8),
            text="Delete", 
            background_color=(0.9,0.2,0.1,0.8),
            pos=(315,205), 
            size=(80, 30),
            font_name="AnonymousPro-Bold",
            font_size='16sp',
            color=(1, 1, 1, 1),
            size_hint=(None, None))
        content.add_widget(note)
        content.add_widget(note_edit_button)
        content.add_widget(delete_note_button)
        popup = MemoryPopup(content=content, 
            auto_dismiss=False, 
            size_hint=(.4, .4),
            separator_height=1,
            separator_color=(0.9, 1, 1, 1),
            background_color=(0.1, 0, 0, 0.8),
            title_font="AnonymousPro-Bold",
            title_size='16sp',
            title='Edit Note')
        def note_edit_button_callback(i):
            if note.text != note_content:
                database_connection.execute("UPDATE notes SET note=? WHERE id=?", (note.text, selected_id))
                database_connection.commit()
                # UPDATE NEEDED
                self.update_note_list_panel('')
            popup.dismiss()
        def delete_note_button_callback(i):
            id_need_to_be_fixed = list(database_connection.execute("SELECT * FROM notes WHERE id>?", (selected_id,)))
            database_connection.execute("DELETE FROM notes WHERE id>=?", (selected_id,))
            for row in id_need_to_be_fixed:
                database_connection.execute("INSERT INTO notes VALUES (?, ?, ?)", (row[0]-1, row[1], row[2]))
            database_connection.commit()
            # UPDATE NEEDED
            self.update_note_list_panel('')
            popup.dismiss()
        note_edit_button.bind(on_release=note_edit_button_callback)
        delete_note_button.bind(on_press=delete_note_button_callback)
        popup.open()





class NoteIt(App):
    def build(self):
        return MainLayout()

NoteIt().run()

database_connection.close()