import kivy
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from datetime import datetime, date

# --- Bloco de importação para Android (ignorado no PC) ---
try:
    from android_permissions import request_permissions, Permission
    from jnius import autoclass
except ImportError:
    class Permission:
        POST_NOTIFICATIONS = "POST_NOTIFICATIONS"
    def request_permissions(perms, callback=None):
        pass

kivy.require('2.1.0')

# --- Classes das Telas ---

class MainScreen(Screen):
    # Propriedades do Kivy que se atualizam automaticamente na interface
    time_goal_text = StringProperty("Até agora, você deveria ter bebido: 0 ml")
    progress_text = StringProperty("0 / 2500 ml")
    current_intake = NumericProperty(0)
    total_goal = NumericProperty(2500) # Valor padrão

    def on_enter(self, *args):
        """Executado sempre que a tela principal é exibida."""
        # Carrega as configurações mais recentes
        app = App.get_running_app()
        self.total_goal = app.settings.get('goal', 2500)
        self.current_intake = app.history.get(str(date.today()), {}).get('intake', 0)
        Clock.schedule_interval(self.update_labels, 1)

    def on_leave(self, *args):
        """Para o relógio quando sai da tela para economizar bateria."""
        Clock.unschedule(self.update_labels)

    def update_labels(self, *args):
        # Atualiza a meta por horário
        now = datetime.now()
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        if now < start_time: time_goal = 0
        elif now > end_time: time_goal = self.total_goal
        else:
            total_seconds_in_day = (end_time - start_time).total_seconds()
            seconds_passed = (now - start_time).total_seconds()
            time_goal = (seconds_passed / total_seconds_in_day) * self.total_goal

        self.time_goal_text = f"Até agora, você deveria ter bebido: {int(time_goal)} ml"
        self.progress_text = f"{int(self.current_intake)} / {int(self.total_goal)} ml"

    def log_water(self):
        try:
            amount = float(self.ids.water_input.text)
            self.current_intake += amount
            self.ids.water_input.text = ""
            App.get_running_app().save_all_data() # Salva tudo
        except ValueError:
            self.ids.water_input.text = "Valor inválido"

class SettingsScreen(Screen):
    def on_enter(self, *args):
        """Carrega as configurações salvas nos campos de texto."""
        app = App.get_running_app()
        self.ids.goal_input.text = str(app.settings.get('goal', 2500))
        self.ids.interval_input.text = str(app.settings.get('notification_interval_hours', 2))
    
    def save_settings(self):
        """Salva as novas configurações e reinicia o serviço de notificação."""
        app = App.get_running_app()
        try:
            app.settings['goal'] = int(self.ids.goal_input.text)
            app.settings['notification_interval_hours'] = int(self.ids.interval_input.text)
            app.save_all_data()
            
            # Reinicia o serviço para usar o novo intervalo
            app.stop_notification_service()
            app.start_notification_service()

            # Atualiza a tela principal com a nova meta
            app.root.get_screen('main').total_goal = app.settings['goal']

            self.ids.save_feedback.text = "Configurações salvas!"
        except ValueError:
            self.ids.save_feedback.text = "Valores inválidos!"

class HistoryScreen(Screen):
    def on_enter(self, *args):
        """Lê o histórico e o exibe na tela."""
        self.ids.history_grid.clear_widgets() # Limpa a lista antiga
        app = App.get_running_app()
        
        # Ordena as datas do mais recente para o mais antigo
        sorted_dates = sorted(app.history.keys(), reverse=True)

        for day in sorted_dates:
            data = app.history[day]
            intake = data.get('intake', 0)
            goal_met = "Sim" if data.get('goal_met', False) else "Não"
            
            entry_label = f"{day}: {int(intake)}ml - Meta cumprida: {goal_met}"
            self.ids.history_grid.add_widget(HistoryLabel(text=entry_label))

# --- Widget customizado para o histórico (para melhor formatação) ---
class HistoryLabel(BoxLayout):
    text = StringProperty('')

# --- Classe principal do App ---

class WaterApp(App):
    # Caminho do arquivo de dados
    @property
    def data_file(self):
        return os.path.join(self.user_data_dir, 'data.json')

    def build(self):
        self.settings = {}
        self.history = {}
        self.load_all_data()
        
        # Cria o gerenciador de telas
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(HistoryScreen(name='history'))
        return sm

    def on_start(self):
        request_permissions([Permission.POST_NOTIFICATIONS])
        self.start_notification_service()
        self.bind(on_pause=self.on_pause_save)

    def on_pause_save(self, *args):
        self.save_all_data()
        return True

    def load_all_data(self):
        """Carrega configurações e histórico do arquivo JSON."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    data = json.load(f)
                    self.settings = data.get('settings', {'goal': 2500, 'notification_interval_hours': 2})
                    self.history = data.get('history', {})
                except json.JSONDecodeError:
                    self.setup_default_data()
        else:
            self.setup_default_data()

    def setup_default_data(self):
        """Cria dados padrão se o arquivo não existir."""
        self.settings = {'goal': 2500, 'notification_interval_hours': 2}
        self.history = {}

    def save_all_data(self, *args):
        """Salva o estado atual (configurações e histórico) no arquivo."""
        today_str = str(date.today())
        main_screen = self.root.get_screen('main')

        # Atualiza o histórico do dia atual
        self.history[today_str] = {
            "intake": main_screen.current_intake,
            "goal_met": main_screen.current_intake >= main_screen.total_goal
        }

        # Junta tudo para salvar
        full_data = {
            'settings': self.settings,
            'history': self.history
        }
        with open(self.data_file, 'w') as f:
            json.dump(full_data, f, indent=4)
    
    def start_notification_service(self):
        try:
            service = autoclass('org.meuapp.waterapp.ServiceMyservice')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = autoclass('android.content.Intent')(mActivity, service)
            mActivity.startService(intent)
        except Exception as e:
            print(f"Serviço não iniciado (normal no PC): {e}")

    def stop_notification_service(self):
        try:
            service = autoclass('org.meuapp.waterapp.ServiceMyservice')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = autoclass('android.content.Intent')(mActivity, service)
            mActivity.stopService(intent)
        except Exception as e:
            print(f"Serviço não parado (normal no PC): {e}")


if __name__ == '__main__':
    WaterApp().run()