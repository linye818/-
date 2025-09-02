#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat-Ledger Clone — Stand-alone Desktop Edition
author: you
python ledger_standalone.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
from datetime import datetime, timedelta

DB_NAME = 'ledger.db'

# ---------- 数据库 ----------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                note TEXT
            )
        """)

def add_record(amount, category, note):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO records (date, amount, category, note) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(sep=' ', timespec='seconds'), amount, category, note)
        )

def fetch_records(days=None):
    sql = "SELECT id, date, amount, category, note FROM records"
    params = []
    if days:
        sql += " WHERE date >= ?"
        params.append((datetime.now() - timedelta(days=days)).isoformat(sep=' ', timespec='seconds'))
    sql += " ORDER BY date DESC"
    with sqlite3.connect(DB_NAME) as conn:
        return conn.execute(sql, params).fetchall()

def delete_record(rid):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM records WHERE id=?", (rid,))

def today_total():
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.execute("SELECT SUM(amount) FROM records WHERE date LIKE ?", (today + '%',))
        return cur.fetchone()[0] or 0.0

# ---------- GUI ----------
class LedgerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("微信记账本 · 单机版")
        self.geometry("420x550")
        self.resizable(False, False)
        init_db()
        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # 顶部栏
        top = ttk.Frame(self)
        top.pack(fill='x', padx=10, pady=10)
        ttk.Label(top, text="今日支出:", font=("Helvetica", 14)).pack(side='left')
        self.today_lbl = ttk.Label(top, text="0.00", font=("Helvetica", 14, 'bold'))
        self.today_lbl.pack(side='left', padx=5)
        ttk.Button(top, text="导出CSV", command=self.export_csv).pack(side='right')

        # 记账区
        frm = ttk.LabelFrame(self, text="快速记账")
        frm.pack(fill='x', padx=10, pady=5)
        ttk.Label(frm, text="金额").grid(row=0, column=0, sticky='w')
        self.ent_amount = ttk.Entry(frm, width=10)
        self.ent_amount.grid(row=0, column=1, padx=5)
        ttk.Label(frm, text="分类").grid(row=0, column=2, sticky='w')
        self.ent_cat = ttk.Entry(frm, width=10)
        self.ent_cat.grid(row=0, column=3, padx=5)
        ttk.Label(frm, text="备注").grid(row=1, column=0, sticky='w')
        self.ent_note = ttk.Entry(frm, width=20)
        self.ent_note.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        ttk.Button(frm, text="记一笔", command=self.save).grid(row=2, column=0, columnspan=4, pady=5)

        # 列表区
        list_frm = ttk.LabelFrame(self, text="最近记录")
        list_frm.pack(fill='both', expand=True, padx=10, pady=5)
        self.tree = ttk.Treeview(list_frm, columns=('date', 'amount', 'cat', 'note'), show='headings', height=15)
        self.tree
