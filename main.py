from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window

class Root(BoxLayout):
    pass

class DemoApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)  # 白色背景，便于检查
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Hello from Kivy on Android!", color=(0,0,0,1), font_size='20sp'))
        return layout

if __name__ == "__main__":
    DemoApp().run()
