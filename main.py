import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
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

# 添加交易屏幕
class AddTransactionScreen(Screen):
    type_spinner = ObjectProperty(None)
    category_spinner = ObjectProperty(None)
    amount_input = ObjectProperty(None)
    note_input = ObjectProperty(None)
    date_input = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.update_categories()
    
    def on_enter(self):
        # 每次进入屏幕时重置表单
        self.type_spinner.text = '支出'
        self.update_categories()
        self.amount_input.text = ""
        self.note_input.text = ""
        self.date_input.text = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def update_categories(self, *args):
        if self.type_spinner.text == '收入':
            categories = self.db.get_categories('收入')
            self.category_spinner.values = [cat[0] for cat in categories]
        else:
            categories = self.db.get_categories('支出')
            self.category_spinner.values = [cat[0] for cat in categories]
        
        if self.category_spinner.values:
            self.category_spinner.text = self.category_spinner.values[0]
    
    def add_transaction(self):
        type_ = self.type_spinner.text
        category = self.category_spinner.text
        
        # 验证金额
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.show_popup("错误", "金额必须大于0")
                return
        except ValueError:
            self.show_popup("错误", "请输入有效的金额")
            return
        
        note = self.note_input.text
        
        # 验证日期
        date_str = self.date_input.text
        try:
            if len(date_str) == 16:  # YYYY-MM-DD HH:MM
                date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            elif len(date_str) == 10:  # YYYY-MM-DD
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                raise ValueError("日期格式不正确")
        except ValueError:
            self.show_popup("错误", "请输入有效的日期格式 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM)")
            return
        
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        self.db.add_transaction(type_, category, amount, note, formatted_date)
        
        # 清空输入字段
        self.amount_input.text = ""
        self.note_input.text = ""
        
        self.show_popup("成功", "交易已添加", callback=self.go_back)
    
    def go_back(self, instance):
        self.manager.current = 'main'
        # 通知主屏幕更新数据
        main_screen = self.manager.get_screen('main')
        main_screen.update_summary()
    
    def show_popup(self, title, message, callback=None):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        
        button_layout = BoxLayout(spacing=10)
        close_button = Button(text="确定")
        button_layout.add_widget(close_button)
        popup_layout.add_widget(button_layout)
        
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.7, 0.3),
            auto_dismiss=False
        )
        
        if callback:
            close_button.bind(on_press=callback)
        else:
            close_button.bind(on_press=popup.dismiss)
        
        popup.open()

# 历史记录屏幕
class HistoryScreen(Screen):
    scroll_layout = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.current_page = 0
        self.page_size = 20
    
    def on_enter(self):
        self.load_transactions()
    
    def load_transactions(self, page=0):
        self.scroll_layout.clear_widgets()
        
        # 添加标题行
        title_layout = GridLayout(cols=5, size_hint_y=None, height='40dp')
        title_layout.add_widget(Label(text='类型', bold=True))
        title_layout.add_widget(Label(text='类别', bold=True))
        title_layout.add_widget(Label(text='金额', bold=True))
        title_layout.add_widget(Label(text='日期', bold=True))
        title_layout.add_widget(Label(text='操作', bold=True))
        self.scroll_layout.add_widget(title_layout)
        
        # 获取交易记录
        transactions = self.db.get_transactions(self.page_size, page * self.page_size)
        
        for transaction in transactions:
            id_, type_, category, amount, note, date = transaction
            
            # 格式化日期
            try:
                date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%m-%d %H:%M")
            except:
                formatted_date = date
            
            # 创建交易记录行
            row_layout = GridLayout(cols=5, size_hint_y=None, height='40dp')
            
            # 根据类型设置颜色
            type_color = (0.2, 0.8, 0.2, 1) if type_ == '收入' else (0.8, 0.2, 0.2, 1)
            
            row_layout.add_widget(Label(text=type_, color=type_color))
            row_layout.add_widget(Label(text=category))
            row_layout.add_widget(Label(text=f"¥{amount:.2f}"))
            row_layout.add_widget(Label(text=formatted_date))
            
            # 删除按钮
            delete_btn = Button(
                text='删除', 
                size_hint_x=None, 
                width='60dp',
                background_color=(0.8, 0.2, 0.2, 1)
            )
            delete_btn.transaction_id = id_
            delete_btn.bind(on_press=self.delete_transaction)
            row_layout.add_widget(delete_btn)
            
            self.scroll_layout.add_widget(row_layout)
        
        # 添加分页控件
        total_count = self.db.get_transactions_count()
        total_pages = (total_count + self.page_size - 1) // self.page_size
        
        pagination_layout = BoxLayout(
            size_hint_y=None, 
            height='50dp',
            padding=10
        )
        
        if page > 0:
            prev_btn = Button(text='上一页', size_hint_x=None, width='100dp')
            prev_btn.page = page - 1
            prev_btn.bind(on_press=self.load_page)
            pagination_layout.add_widget(prev_btn)
        else:
            pagination_layout.add_widget(Label(text=''))
        
        page_info = Label(text=f'第 {page + 1} 页 / 共 {total_pages} 页')
        pagination_layout.add_widget(page_info)
        
        if page < total_pages - 1:
            next_btn = Button(text='下一页', size_hint_x=None, width='100dp')
            next_btn.page = page + 1
            next_btn.bind(on_press=self.load_page)
            pagination_layout.add_widget(next_btn)
        else:
            pagination_layout.add_widget(Label(text=''))
        
        self.scroll_layout.add_widget(pagination_layout)
    
    def load_page(self, instance):
        self.load_transactions(instance.page)
    
    def delete_transaction(self, instance):
        transaction_id = instance.transaction_id
        if self.db.delete_transaction(transaction_id):
            self.show_popup("成功", "交易记录已删除")
            self.load_transactions(self.current_page)
        else:
            self.show_popup("错误", "删除失败")
    
    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text="确定")
        popup_layout.add_widget(close_button)
        
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.7, 0.3)
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()

# 统计屏幕
class StatisticsScreen(Screen):
    stats_layout = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
    
    def on_enter(self):
        self.show_statistics()
    
    def show_statistics(self):
        self.stats_layout.clear_widgets()
        
        # 获取当前月份的收支统计
        income, expense = self.db.get_monthly_summary()
        balance = income - expense
        
        # 显示月度摘要
        summary_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height='120dp',
            padding=10
        )
        
        summary_layout.add_widget(Label(
            text=f"本月结余: ¥{balance:.2f}", 
            font_size='20sp',
            bold=True
        ))
        summary_layout.add_widget(Label(
            text=f"收入: ¥{income:.2f}", 
            color=(0.2, 0.8, 0.2, 1)
        ))
        summary_layout.add_widget(Label(
            text=f"支出: ¥{expense:.2f}", 
            color=(0.8, 0.2, 0.2, 1)
        ))
        
        self.stats_layout.add_widget(summary_layout)
        
        # 显示收入分类统计
        income_stats = self.db.get_category_summary('收入')
        if income_stats:
            income_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=(len(income_stats) + 1) * 40
            )
            income_layout.add_widget(Label(
                text="收入分类统计", 
                bold=True,
                size_hint_y=None,
                height='40dp'
            ))
            
            for category, amount in income_stats:
                if amount:
                    row = BoxLayout(size_hint_y=None, height='40dp')
                    row.add_widget(Label(text=category))
                    row.add_widget(Label(text=f"¥{amount:.2f}"))
                    income_layout.add_widget(row)
            
            self.stats_layout.add_widget(income_layout)
        
        # 显示支出分类统计
        expense_stats = self.db.get_category_summary('支出')
        if expense_stats:
            expense_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=(len(expense_stats) + 1) * 40
            )
            expense_layout.add_widget(Label(
                text="支出分类统计", 
                bold=True,
                size_hint_y=None,
                height='40dp'
            ))
            
            for category, amount in expense_stats:
                if amount:
                    row = BoxLayout(size_hint_y=None, height='40dp')
                    row.add_widget(Label(text=category))
                    row.add_widget(Label(text=f"¥{amount:.2f}"))
                    expense_layout.add_widget(row)
            
            self.stats_layout.add_widget(expense_layout)

# 记账应用主类
class AccountingApp(App):
    def build(self):
        # 创建屏幕管理器
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddTransactionScreen(name='add_transaction'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        
        return sm

if __name__ == '__main__':
    AccountingApp().run()
