import kivy
import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from datetime import datetime, date

# --- Importações específicas para Android ---
# Essas importações causarão um erro se você rodar no PC.
# O Kivy as ignora no PC, mas o buildozer as usa no celular.
try:
    from android_permissions import request_permissions, Permission
    from jnius import autoclass
except ImportError:
    # Define classes falsas para poder testar no PC sem erros
    class Permission:
        POST_NOTIFICATIONS = "POST_NOTIFICATIONS" # Apenas um placeholder
    def request_permissions(perms, callback=None):
        pass

kivy.require('2.1.0')

class WaterAppLayout(BoxLayout):
    total_goal = 2500
    current_intake = 0.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # O carregamento de dados foi movido para o método on_start do App
        Clock.schedule_interval(self.update_labels, 1)

    def update_labels(self, *args):
        now = datetime.now()
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        
        if now < start_time:
            time_goal = 0
        elif now > end_time:
            time_goal = self.total_goal
        else:
            total_seconds_in_day = (end_time - start_time).total_seconds()
            seconds_passed = (now - start_time).total_seconds()
            time_goal = (seconds_passed / total_seconds_in_day) * self.total_goal

        self.ids.time_goal_label.text = f"Até agora, você deveria ter bebido: {int(time_goal)} ml"
        self.ids.progress_bar.value = self.current_intake
        self.ids.progress_label.text = f"{int(self.current_intake)} / {self.total_goal} ml"

    def log_water(self):
        try:
            amount = float(self.ids.water_input.text)
            self.current_intake += amount
            self.ids.water_input.text = ""
            # Pede ao App para salvar o estado atual
            App.get_running_app().save_state()
        except ValueError:
            self.ids.water_input.text = "Valor inválido"

class WaterApp(App):
    # Caminho para o arquivo que salvará os dados
    @property
    def state_file(self):
        # user_data_dir é uma pasta segura que o Kivy oferece para cada app
        return os.path.join(self.user_data_dir, 'state.json')

    def on_start(self):
        """Método executado quando o app inicia."""
        # 1. Pedir permissão de notificação
        request_permissions([Permission.POST_NOTIFICATIONS])

        # 2. Iniciar o serviço de notificação em segundo plano
        self.start_notification_service()

        # 3. Carregar o estado salvo (consumo de água)
        self.load_state()

        # Vincula o método on_pause para salvar o estado quando o app for minimizado
        self.bind(on_pause=self.save_state_on_pause)

    def save_state_on_pause(self, *args):
        self.save_state()
        return True # Importante para o ciclo de vida do app Kivy

    def load_state(self):
        """Carrega o consumo de água do arquivo JSON."""
        layout = self.root
        today_str = str(date.today())

        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                try:
                    state_data = json.load(f)
                    # Se a data salva for a de hoje, carrega o valor
                    if state_data.get("date") == today_str:
                        layout.current_intake = state_data.get("intake", 0)
                    else: # Se for um dia diferente, reseta
                        layout.current_intake = 0
                except json.JSONDecodeError:
                    layout.current_intake = 0
        else: # Se o arquivo não existe, começa do zero
            layout.current_intake = 0
        
        layout.update_labels() # Garante que a tela comece com os valores corretos

    def save_state(self, *args):
        """Salva o consumo atual e a data no arquivo JSON."""
        state_data = {
            "date": str(date.today()),
            "intake": self.root.current_intake
        }
        with open(self.state_file, 'w') as f:
            json.dump(state_data, f)
    
    def start_notification_service(self):
        """Inicia o serviço de segundo plano no Android."""
        # Este código só funciona no Android
        try:
            # Importa a classe de Serviço do Android
            service = autoclass('org.meuapp.waterapp.ServiceMyservice')
            # Pega o contexto da aplicação Android
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            # Cria um "Intent" para iniciar o serviço
            argument = ''
            intent = autoclass('android.content.Intent')(mActivity, service)
            # Inicia o serviço
            mActivity.startService(intent)
        except Exception as e:
            print(f"Não foi possível iniciar o serviço (normal se não estiver no Android): {e}")

    def build(self):
        return WaterAppLayout()

if __name__ == '__main__':
    WaterApp().run()