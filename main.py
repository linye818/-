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
                   
