#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信记账本 · 单机版
Kivy GUI + SQLite，零依赖
"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import sqlite3
import csv
import os
from datetime import datetime

DB = 'ledger.db'

KV = '''
<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        Label:
            text: root.today_text
            font_size: '24sp'
            size_hint_y: .15
        GridLayout:
            cols: 2
            size_hint_y: .3
            spacing: 5
            TextInput:
                id: amount
                hint_text: '金额'
                input_filter: 'float'
            TextInput:
                id: category
                hint_text: '分类'
            TextInput:
                id: note
                hint_text: '备注'
                multiline: False
            Button:
                text: '记一笔'
                on_release: app.save_record(amount.text, category.text, note.text)
        RecycleView:
            viewclass: 'Label'
            data: [{'text': str(x)} for x in root.records]
            RecycleBoxLayout:
                default_size: None, dp(30)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        Button:
            text: '导出CSV'
            size_hint_y: .1
            on_release: app.export_csv()
'''

class MainScreen(Screen):
    today_text = StringProperty('今日支出: 0')
    records = StringProperty('')

class LedgerApp(App):
    def build(self):
        init_db()
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

    def on_start(self):
        self.refresh()

    def init_db(self):
        with sqlite3.connect(DB) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    amount REAL,
                    category TEXT,
                    note TEXT
                )
            ''')

    def save_record(self, amount, category, note):
        try:
            amt = float(amount)
            if amt <= 0:
                raise ValueError
        except ValueError:
            return
        category = category or '未分类'
        note = note or ''
        with sqlite3.connect(DB) as conn:
            conn.execute(
                "INSERT INTO records (date, amount, category, note) VALUES (?, ?, ?, ?)",
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), amt, category, note)
            )
        self.refresh()

    def refresh(self):
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(DB) as conn:
            cur = conn.execute("SELECT SUM(amount) FROM records WHERE date LIKE ?", (today + '%',))
            total = cur.fetchone()[0] or 0.0
            self.root.get_screen('main').today_text = f'今日支出: {total:.2f}'

            rows = conn.execute("SELECT date, amount, category, note FROM records ORDER BY date DESC LIMIT 50").fetchall()
            self.root.get_screen('main').records = [f"{d} | {a:.2f} | {c} | {n}" for d, a, c, n in rows]

    def export_csv(self):
        rows = []
        with sqlite3.connect(DB) as conn:
            rows = conn.execute("SELECT * FROM records ORDER BY date DESC").fetchall()
        filename = f'ledger_{datetime.now():%Y%m%d_%H%M%S}.csv'
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['日期', '金额', '分类', '备注'])
            writer.writerows(rows)
        self.root.get_screen('main').ids.note.text = f'已导出 {filename}'

if __name__ == '__main__':
    LedgerApp().run()
