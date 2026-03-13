from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView

import requests


class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.username = MDTextField(
            text="Логин",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint_x = 0.6
        )

        self.password = MDTextField(
            text="Пароль",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x = 0.6
        )

        login_button = MDRaisedButton(
            text="Войти",
            pos_hint={"center_x": 0.35, "center_y": 0.4},
            on_release=self.login
        )

        register_button = MDRaisedButton(
            text="Регистрация",
            pos_hint={"center_x": 0.6, "center_y": 0.4},
            on_release=self.go_register
        )

        self.message_label = MDLabel(
            text="",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.3}
        )

        self.add_widget(self.username)
        self.add_widget(self.password)
        self.add_widget(login_button)
        self.add_widget(register_button)
        self.add_widget(self.message_label)
    def login(self, instance):
        try:
            response = requests.post("http://127.0.0.1:8000/auth/login", data={
                "username": self.username.text,
                "password": self.password.text
            })
            if response.status_code == 200:
                token = response.json().get('access_token')
                if token:
                    app = MDApp.get_running_app()
                    if app is not None:
                        app.token = token
                        self.message_label.text = ""
                        self.manager.current = "main"
                    else:
                        self.message_label.text = "Ошибка приложения: app == None"
                else:
                    self.message_label.text = "Не удалось получить токен"
            elif response.status_code == 401:
                self.message_label.text = "Неверный логин или пароль"
            else:
                self.message_label.text = f"Ошибка логина ({response.status_code}): {response.text}"
        except Exception as e:
            self.message_label.text = f"Ошибка: {e}"

    def go_register(self, instance):
        if self.manager:
            self.manager.current = "register"

class RegisterScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

        self.username = MDTextField(
            hint_text="Логин",
            pos_hint={"center_x": 0.5, "center_y": 0.65},
            size_hint_x=0.4
        )

        self.password = MDTextField(
            hint_text="Пароль",
            password=True,
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            size_hint_x=0.4
        )

        register_button = MDRaisedButton(
            text="Зарегистрироваться",
            pos_hint={"center_x": 0.6, "center_y": 0.25},
            on_release=self.register
        )

        self.surname = MDTextField(
            hint_text="Фамилия",
            pos_hint={"center_x": 0.5, "center_y": 0.45},
            size_hint_x=0.4
        )

        self.last_name = MDTextField(
            hint_text="Имя",
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            size_hint_x=0.4
        )

        back_button = MDRaisedButton(
            text="Назад",
            pos_hint={"center_x": 0.35, "center_y": 0.25},
            on_release=self.go_back
        )

        self.message_label = MDLabel(
            text="",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.28}
        )

        self.add_widget(self.username)
        self.add_widget(self.password)
        self.add_widget(register_button)
        self.add_widget(back_button)
        self.add_widget(self.message_label)
        self.add_widget(self.surname)
        self.add_widget(self.last_name)

    def register(self, instance):
        try:
            response = requests.post("http://127.0.0.1:8000/auth/register", json={
                "username": self.username.text,
                "password": self.password.text,
                "first_name": self.last_name.text,
                "surname": self.surname.text
            })

            if response.status_code in (200, 201):
                self.message_label.text = "Регистрация успешна!"
            else:
                self.message_label.text = f"Ошибка регистрации ({response.status_code}): {response.text}"

        except Exception as e:
            self.message_label.text = f"Ошибка: {e}"

    def go_back(self, instance):
        self.manager.current = "login"

class ChatScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title = MDLabel(text="Чат",
                             halign="center",
                             theme_text_color="Primary",
                             pos_hint={"center_x": 0.5, "center_y": 0.92})

        self.partner_label = MDLabel(
            text="Выберите диалог",
            halign="center",
            theme_text_color="Secondary",
            pos_hint={"center_x": 0.5, "center_y": 0.82}
        )

        self.messages_label = MDLabel(
            text="Заглушка сообщений",
            halign="center",
            theme_text_color="Secondary",
            pos_hint={"center_x": 0.5, "center_y": 0.65}
        )

        self.input_text = MDTextField(
            hint_text="Введите сообщение",
            pos_hint={"center_x": 0.5, "center_y": 0.35},
            size_hint_x=0.8
        )

        send_btn = MDRaisedButton(
            text="Отправить",
            pos_hint={"center_x": 0.8, "center_y": 0.20},
            on_release=self.send_message
        )

        back_btn = MDRaisedButton(
            text="Назад",
            pos_hint={"center_x": 0.2, "center_y": 0.20},
            on_release=self.go_back
        )

        self.add_widget(self.title)
        self.add_widget(self.partner_label)
        self.add_widget(self.messages_label)
        self.add_widget(self.input_text)
        self.add_widget(send_btn)
        self.add_widget(back_btn)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        selected_user = getattr(app, 'selected_user', None)

        if isinstance(selected_user, dict):
            username = selected_user.get('username', 'пользователь')
            self.partner_label.text = f"Чат с {username}"
            self.messages_label.text = "Заглушка: история диалога тут"
        elif selected_user is not None:
            self.partner_label.text = f"Чат с {selected_user}"
            self.messages_label.text = "Заглушка: история диалога тут"
        else:
            self.partner_label.text = "Пользователь не выбран"
            self.messages_label.text = "Выберите диалог на экране выбора"

    def send_message(self, instance):
        text = self.input_text.text.strip()
        if not text:
            return

        selected_user = getattr(MDApp.get_running_app(), 'selected_user', None)
        if isinstance(selected_user, dict):
            partner_name = selected_user.get('username', 'пользователь')
        else:
            partner_name = str(selected_user) if selected_user is not None else 'пользователь'

        self.messages_label.text = f"{partner_name}: {text}"
        self.input_text.text = ""

    def go_back(self, instance):
        self.manager.current = "dialogs"


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        label = MDLabel(text="Валюта:",
                         halign="center",
                         theme_text_color="Primary",
                         pos_hint={"center_x": 0.93, "center_y": 0.98})

        self.label_currency = MDLabel(text="?",
                                     halign="center",
                                     theme_text_color="Primary",
                                     pos_hint={"center_x": 0.98, "center_y": 0.98})
        
        chat_btn = MDIconButton(icon="chat",
                                pos_hint={"center_x": 0.1, "center_y": 0.8},
                                on_release=self.go_chat)

        self.add_widget(label)
        self.add_widget(self.label_currency)
        self.add_widget(chat_btn)

    def on_pre_enter(self):
        self.get_currency()

    def get_currency(self):
        app = MDApp.get_running_app()
        if app is None:
            self.label_currency.text = "Ошибка: приложение не запущено"
            return

        token = getattr(app, 'token', None)
        if not token:
            self.label_currency.text = "Нет токена, выполните вход"
            return

        try:
            response = requests.get(
                "http://127.0.0.1:8000/currency/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 401:
                self.label_currency.text = "Токен невалиден или истёк"
                return

            data = response.json()
            if data:
                currency = data[0].get('quantity')
                self.label_currency.text = str(currency)
            else:
                self.label_currency.text = "Нет данных"
        except Exception as e:
            self.label_currency.text = f"Ошибка при получении данных: {e}"
    
    def go_chat(self, instance):
        self.manager.current = "dialogs"


class DialogsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.title_label = MDLabel(
            text="Выберите пользователя",
            halign="center",
            theme_text_color="Primary",
            pos_hint={"center_x": 0.5, "center_y": 0.95}
        )
        self.add_widget(self.title_label)

        self.scroll = ScrollView(
            size_hint=(1, 0.85),
            pos_hint={"center_x": 0.5, "center_y": 0.45}
        )
        self.users_list = MDList()
        self.scroll.add_widget(self.users_list)
        self.add_widget(self.scroll)

        self.message_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            pos_hint={"center_x": 0.5, "center_y": 0.05}
        )
        self.add_widget(self.message_label)

    def on_pre_enter(self):
        self.load_dialogs()

    def load_dialogs(self):
        app = MDApp.get_running_app()
        if app is None:
            self.message_label.text = "Ошибка: приложение не запущено"
            return

        token = getattr(app, 'token', None)
        if not token:
            self.message_label.text = "Требуется авторизация"
            self.manager.current = "login"
            return

        try:
            response = requests.get(
                "http://127.0.0.1:8000/auth/users",
                headers={"Authorization": f"Bearer {token}"},
            )
            if response.status_code == 401:
                self.message_label.text = "Токен невалиден или истёк"
                return

            self.users_list.clear_widgets()
            users = response.json()
            if not users:
                self.message_label.text = "Пользователи не найдены"
                return

            if not isinstance(users, list):
                self.message_label.text = "Ошибка: некорректный формат списка пользователей"
                return

            for user in users:
                if isinstance(user, dict):
                    username = user.get('username', '')
                    first_name = user.get('first_name', '') or ''
                    surname = user.get('surname', '') or ''
                else:
                    username = str(user)
                    first_name = ''
                    surname = ''

                item_text = f"{username} ({first_name} {surname})".strip()
                item = OneLineListItem(
                    text=item_text,
                    on_release=lambda i, u=user: self.open_chat(u)
                )
                self.users_list.add_widget(item)

        except Exception as e:
            self.message_label.text = f"Ошибка загрузки: {e}"

    def open_chat(self, user):
        app = MDApp.get_running_app()
        if app is not None:
            app.selected_user = user
        self.manager.current = "chat"


class CurrencyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        sm = ScreenManager()
        
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DialogsScreen(name="dialogs"))
        sm.add_widget(ChatScreen(name="chat"))
        
        sm.current = "login"
        
        return sm
            

if __name__ == "__main__":
    CurrencyApp().run()