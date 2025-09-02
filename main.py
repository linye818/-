import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
import os

# 数据库管理类
class Database:
    def __init__(self, db_name='accounts.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    note TEXT,
                    date TEXT NOT NULL
                )
            ''')
            
            # 创建类别表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    icon TEXT
                )
            ''')
            
            # 插入默认类别
            default_categories = [
                ('支出', '餐饮', 'food'),
                ('支出', '购物', 'cart'),
                ('支出', '交通', 'car'),
                ('支出', '娱乐', 'gamepad'),
                ('支出', '医疗', 'medical-bag'),
                ('支出', '教育', 'book'),
                ('支出', '其他支出', 'dots-horizontal'),
                ('收入', '工资', 'cash'),
                ('收入', '奖金', 'gift'),
                ('收入', '投资', 'chart-line'),
                ('收入', '其他收入', 'dots-horizontal')
            ]
            
            cursor.execute('SELECT COUNT(*) FROM categories')
            if cursor.fetchone()[0] == 0:
                cursor.executemany('''
                    INSERT INTO categories (type, name, icon)
                    VALUES (?, ?, ?)
                ''', default_categories)
            
            conn.commit()

    def add_transaction(self, type_, category, amount, note, date):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (type, category, amount, note, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, category, amount, note, date))
            conn.commit()

    def get_transactions(self, limit=100, offset=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, type, category, amount, note, date 
                FROM transactions 
                ORDER BY date DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            return cursor.fetchall()

    def get_transactions_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM transactions')
            return cursor.fetchone()[0]

    def get_monthly_summary(self, year=None, month=None):
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT type, SUM(amount) 
                FROM transactions 
                WHERE date >= ? AND date < ?
                GROUP BY type
            ''', (start_date, end_date))
            result = cursor.fetchall()
            
            income = 0
            expense = 0
            
            for type_, amount in result:
                if type_ == '收入':
                    income = amount or 0
                elif type_ == '支出':
                    expense = amount or 0
            
            return income, expense

    def get_category_summary(self, type_=None, year=None, month=None):
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if type_:
                cursor.execute('''
                    SELECT category, SUM(amount) 
                    FROM transactions 
                    WHERE type = ? AND date >= ? AND date < ?
                    GROUP BY category
                ''', (type_, start_date, end_date))
            else:
                cursor.execute('''
                    SELECT category, SUM(amount) 
                    FROM transactions 
                    WHERE date >= ? AND date < ?
                    GROUP BY category
                ''', (start_date, end_date))
            return cursor.fetchall()

    def get_categories(self, type_=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if type_:
                cursor.execute('SELECT name, icon FROM categories WHERE type = ?', (type_,))
            else:
                cursor.execute('SELECT name, icon FROM categories')
            return cursor.fetchall()

    def delete_transaction(self, transaction_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0

# 主屏幕
class MainScreen(Screen):
    balance_label = ObjectProperty(None)
    income_label = ObjectProperty(None)
    expense_label = ObjectProperty(None)
    month_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        Clock.schedule_once(self.update_summary, 0.1)
    
    def update_summary(self, dt=None):
        # 更新月度摘要
        income, expense = self.db.get_monthly_summary(self.current_year, self.current_month)
        balance = income - expense
        
        month_text = f"{self.current_year}年{self.current_month}月"
        self.month_label.text = month_text
        self.balance_label.text = f"¥{balance:.2f}"
        self.income_label.text = f"收入: ¥{income:.2f}"
        self.expense_label.text = f"支出: ¥{expense:.2f}"
    
    def change_month(self, delta):
        # 更改显示的月份
        self.current_month += delta
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        elif self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        
        self.update_summary()
    
    def goto_add_transaction(self):
        self.manager.current = 'add_transaction'
    
    def goto_history(self):
        self.manager.current = 'history'
    
    def goto_statistics(self):
        self.manager.current = 'statistics'

# 记账应用主类
class AccountingApp(App):
    def build(self):
        # 创建屏幕管理器
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        
        return sm

if __name__ == '__main__':
    AccountingApp().run()
