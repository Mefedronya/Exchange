from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.list import MDList, TwoLineListItem, OneLineListItem
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.metrics import dp

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
        self.title_label = MDLabel(
            text="Чат", 
            halign="center", 
            theme_text_color="Primary", 
            pos_hint={"center_x": 0.5, "center_y": 0.95}
        )
        self.partner_label = MDLabel(
            text="", 
            halign="center", 
            theme_text_color="Secondary", 
            pos_hint={"center_x": 0.5, "center_y": 0.88}
        )
        
        # ScrollView с сообщениями
        self.scroll = ScrollView(
            size_hint=(1, 0.65), 
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.messages_list = MDList()
        self.scroll.add_widget(self.messages_list)  # ✅ messages_list внутри scroll
        
        # Поле ввода и кнопка отправки
        input_layout = MDBoxLayout(
            orientation='horizontal', 
            padding="10dp", 
            spacing="10dp", 
            size_hint=(1, None), 
            height=dp(60), 
            pos_hint={"center_x": 0.5, "center_y": 0.15}
        )
        self.input_text = MDTextField(hint_text="Введите сообщение...", size_hint_x=0.8)
        send_btn = MDRaisedButton(text="➤", size_hint_x=0.15, on_release=self.send_message)
        input_layout.add_widget(self.input_text)    # ✅ input_text внутри input_layout
        input_layout.add_widget(send_btn)           # ✅ send_btn внутри input_layout
        
        # Кнопка "Назад"
        back_btn = MDIconButton(
            icon="arrow-left", 
            pos_hint={"center_x": 0.1, "center_y": 0.92}, 
            on_release=self.go_back
        )
        
        # === Добавляем на экран ТОЛЬКО верхнеуровневые виджеты ===
        self.add_widget(self.title_label)      
        self.add_widget(self.partner_label)    
        self.add_widget(self.scroll)           
        self.add_widget(input_layout)          
        self.add_widget(back_btn)

    def on_pre_enter(self):
        app = MDApp.get_running_app()
        chat = getattr(app, 'current_chat', None)
        partner_id = getattr(app, 'current_partner_id', None)
        
        if chat and partner_id:
            # Загружаем имя собеседника
            token = getattr(app, 'token', None)
            partner_name = f"Пользователь #{partner_id}"
            if token:
                try:
                    resp = requests.get("http://127.0.0.1:8000/auth/users", headers={"Authorization": f"Bearer {token}"})
                    if resp.status_code == 200:
                        for u in resp.json():
                            if u['id'] == partner_id:
                                partner_name = u.get('username', partner_name)
                                break
                except:
                    pass
            self.partner_label.text = f"Чат с {partner_name}"
            self.load_messages(chat['ChatID'])
        else:
            self.partner_label.text = "Чат не выбран"
    
    def load_messages(self, chat_id):
        app = MDApp.get_running_app()
        token = getattr(app, 'token', None)
        current_user_id = getattr(app, 'current_user_id', None)
        if not token or not current_user_id:
            return
        try: 
            response = requests.get(
                f"http://127.0.0.1:8000/Chatiks/messages/{chat_id}",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": 100}
            )
            if response.status_code != 200:
                return
            self.messages_list.clear_widgets()
            messages = response.json()
            for msg in messages:
             is_mine = msg['user_id'] == current_user_id
             item = OneLineListItem(
                text = msg['MessagesText'],
                theme_text_color = "Custom" if is_mine else "Primary",
                text_color =(0,0,0,1) if not is_mine else (1,1,1,1)
            )
             if is_mine:
                item.md_bg_color = (0.2, 0.6, 1, 1) # Синий
                item.pos_hint = {"right": 1}
             else:
                item.md_bg_color = (0.9, 0.9, 0.9, 1)  # Серый
                item.pos_hint = {"right": 0.7}
             item.secondary_text = msg.get('sentAt', '') [-8] if msg.get('sentAt') else ''
             item.secondary_theme_text_color = "Secondary"
             self.messages_list.add_widget(item)
             Clock.schedule_once(lambda dt: self.scroll.scroll_to(self.messages_list.children[-1]) if self.messages_list.children else None, 0.1)

        except Exception as e:
            print(f"Ошибка загрузки сообщений: {e}")

    def send_message(self, instance):
        text = self.input_text.text.strip()
        if not text:
            return
            
        app = MDApp.get_running_app()
        chat = getattr(app, 'current_chat', None)
        token = getattr(app, 'token', None)
        
        if not chat or not token:
            return
            
        try:
            response = requests.post(
                "http://127.0.0.1:8000/Chatiks/messages/",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"chat_Id": chat['ChatID'], "MessagesText": text}
            )
            if response.status_code in (200, 201):
                self.input_text.text = ""
                self.load_messages(chat['ChatID'])  # Обновляем список
            else:
                print(f"Ошибка отправки: {response.text}")
        except Exception as e:
            print(f"Ошибка сети: {e}")

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
        self.chats_list = MDList()
        self.scroll.add_widget(self.chats_list)
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

        self.chats_list.clear_widgets()
        chats = response.json()
        
        # 🔍 ОТЛАДКА: выводим структуру данных
        print("📦 Полученные чаты:", chats)
        if chats and isinstance(chats, list) and len(chats) > 0:
            print("🔑 Ключи первого чата:", list(chats[0].keys()) if isinstance(chats[0], dict) else "Не словарь")
        
        if not chats:
            self.message_label.text = "Чаты не найдены, создайте новый"
            return
        self.message_label.text = ""
        user_map = self._load_users_map(token)

        if not isinstance(chats, list):
            self.message_label.text = "Ошибка: некорректный формат списка чатов"
            return

        for chat in chats:
            if isinstance(chat, dict):
                # 🔧 БЕЗОПАСНЫЙ доступ к ключам с проверкой
                user1_id = chat.get('user1_id') or chat.get('user_id') or chat.get('userId')
                user2_id = chat.get('user2_id') or chat.get('partner_id') or chat.get('partnerId')
                chat_id = chat.get('ChatID') or chat.get('chat_id') or chat.get('id')
                chat_name = chat.get('ChatName') or chat.get('chat_name') or chat.get('name', f'Чат #{chat_id}')
                
                # Определяем собеседника
                current_uid = getattr(app, 'current_user_id', None)
                print(f"👤 Текущий пользователь: {current_uid}, user1: {user1_id}, user2: {user2_id}")
                
                if user1_id == current_uid and user2_id:
                    partner_id = user2_id
                elif user2_id == current_uid and user1_id:
                    partner_id = user1_id
                else:
                    # Если не удалось определить, берём первого, кто не текущий пользователь
                    partner_id = user2_id if user1_id == current_uid else user1_id
                
                if not partner_id:
                    print("⚠️ Не удалось определить partner_id для чата:", chat)
                    continue
                
                partner_info = user_map.get(partner_id, {})
                partner_name = partner_info.get('username', f'Пользователь #{partner_id}')
                
                item = TwoLineListItem(
                    text=partner_name,
                    secondary_text=f"Чат #{chat_id}",
                    on_release=lambda i, c=chat, p=partner_id: self.open_chat(c, p)
                )
                self.chats_list.add_widget(item)
            else:
                print("⚠️ Элемент не является словарём:", chat)

     except KeyError as e:
        error_msg = f"Отсутствует ключ: {e}"
        self.message_label.text = error_msg
        print("❌ KeyError:", error_msg)
        print("📋 Данные:", chats if 'chats' in locals() else "Не получены")
     except Exception as e:
        error_msg = f"Ошибка загрузки: {e}"
        self.message_label.text = error_msg
        print("❌ Exception:", error_msg)
        import traceback
        traceback.print_exc()

    def _load_users_map(self, token):
        try:
            resp = requests.get(
                "http://127.0.0.1:8000/auth/users", 
                headers={"Authorization": f"Bearer {token}"}
            )
            if resp.status_code == 200:
                return {u['id']: u for u in resp.json()}
        except:
            pass
        return {}

    # 🔧 ИСПРАВЛЕНО: имя метода и ВСЯ индентация
    def show_create_chat_dialog(self, instance):  # ← Исправлено: dialoog → dialog
        app = MDApp.get_running_app()
        if app is None:
            return
        
        token = getattr(app, 'token', None)
        if not token:
            return

        # Создаём НОВЫЕ виджеты каждый раз
        content = MDBoxLayout(orientation='vertical', spacing="12dp", padding="20dp")
        
        chat_name_input = MDTextField(hint_text="Название чата", size_hint_y=None, height="40dp")
        partner_input = MDTextField(hint_text="ID партнёра", size_hint_y=None, height="40dp")
        
        title_label = MDLabel(text="Создать новый чат", theme_text_color="Primary", bold=True, size_hint_y=None, height="30dp")
        hint_label = MDLabel(text="Введите ID или имя пользователя", theme_text_color="Hint", font_size="12sp", size_hint_y=None, height="25dp")
        
        content.add_widget(title_label)
        content.add_widget(chat_name_input)
        content.add_widget(partner_input)
        content.add_widget(hint_label)

        dialog_error_label = MDLabel(text="", theme_text_color="Error", size_hint_y=None, height="25dp")
        content.add_widget(dialog_error_label)

        # 🔧 Внутренние функции - правильная индентация
        def create_chat_dialog(instance):
            partner_val = partner_input.text.strip()
            if not partner_val:
                dialog_error_label.text = "Введите партнёра"
                return
            
            partner_id = None
            if partner_val.isdigit():
                partner_id = int(partner_val)
            else:
                try:
                    resp = requests.get(
                        "http://127.0.0.1:8000/auth/users",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    if resp.status_code == 200:
                        current_uid = getattr(app, 'current_user_id', None)
                        users = resp.json()
                        for u in users:
                            if u['id'] != current_uid and u["username"].lower() == partner_val.lower():
                                partner_id = u['id']
                                break
                except:
                    pass
            
            if not partner_id:
                dialog_error_label.text = "Пользователь не найден"
                return
            
            chat_name = chat_name_input.text.strip() or f"Чат с {partner_val}"
            self._create_chat_api(chat_name, partner_id)
            dialog.dismiss()

        def cancel_dialog(instance):
            dialog.dismiss()

        dialog = MDDialog(
            title="Новый чат",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Отмена", on_release=cancel_dialog),
                MDFlatButton(text="Создать", on_release=create_chat_dialog)
            ]
        )
        dialog.open()

    # 🔧 Эти методы теперь НА УРОВНЕ КЛАССА, а не внутри show_create_chat_dialog!
    def _create_chat_api(self, chat_name, partner_id):
        app = MDApp.get_running_app()
        token = getattr(app, 'token', None)
        if not token:
            return
        try:
            response = requests.post(
                "http://127.0.0.1:8000/Chatiks/chats/",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"ChatName": chat_name, "user2_id": partner_id}
            )
            if response.status_code in (200, 201):
                self.load_dialogs()  # ← Исправлено: добавлены скобки!
                chat_data = response.json()
                self.open_chat(chat_data, partner_id)
            else:
                self.message_label.text = f"Ошибка: {response.text}"
        except Exception as e:
            self.message_label.text = f"Ошибка сети: {e}"

    def open_chat(self, chat, partner_id):
        app = MDApp.get_running_app()
        if app is not None:
            app.current_chat = chat  # ← Исправлено: selected_chat → current_chat
            app.current_partner_id = partner_id  # ← Исправлено: partner_id → current_partner_id
        if self.manager:
            self.manager.current = "chat"

    def go_back(self, instance):
        self.manager.current = "main"


class CurrencyApp(MDApp):
    token = None
    current_user_id = None
    current_chat = None
    current_partner_id = None
    selected_user = None
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
    def on_start(self):
        """После успешного логина можно сохранить ID пользователя"""
        pass
            

if __name__ == "__main__":
    CurrencyApp().run()