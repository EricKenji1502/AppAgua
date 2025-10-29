import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from plyer import notification
from datetime import datetime, time

# Garante que a versão do Kivy é compatível
kivy.require('2.1.0') 

class WaterAppLayout(BoxLayout):
    total_goal = 2500  # Meta total em ml
    current_intake = 0.0 # Consumo atual em ml

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Agenda a atualização dos textos a cada segundo
        Clock.schedule_interval(self.update_labels, 1)
        # Agenda as notificações a cada 2 horas (7200 segundos)
        Clock.schedule_interval(self.send_notification, 7200)

    def update_labels(self, *args):
        """Atualiza os textos da tela em tempo real."""
        # --- Cálculo da meta por horário ---
        now = datetime.now()
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0) # Consideramos o dia começando às 8h
        end_time = now.replace(hour=22, minute=0, second=0, microsecond=0) # e terminando às 22h
        
        # Se estiver fora do horário, a meta do horário é 0 ou a meta total
        if now < start_time:
            time_goal = 0
        elif now > end_time:
            time_goal = self.total_goal
        else:
            total_seconds_in_day = (end_time - start_time).total_seconds()
            seconds_passed = (now - start_time).total_seconds()
            time_goal = (seconds_passed / total_seconds_in_day) * self.total_goal

        # --- Atualiza os elementos da interface ---
        # Acessa os 'ids' definidos no arquivo .kv
        self.ids.time_goal_label.text = f"Até agora, você deveria ter bebido: {int(time_goal)} ml"
        self.ids.progress_bar.value = self.current_intake
        self.ids.progress_label.text = f"{int(self.current_intake)} / {self.total_goal} ml"

    def log_water(self):
        """Adiciona a quantidade de água informada."""
        try:
            # Pega o valor do campo de texto
            amount = float(self.ids.water_input.text)
            self.current_intake += amount
            # Limpa o campo de texto após adicionar
            self.ids.water_input.text = ""
        except ValueError:
            # Caso o usuário não digite um número
            self.ids.water_input.text = "Valor inválido"

    def send_notification(self, *args):
        """Envia uma notificação para o sistema."""
        notification.notify(
            title="Hora de Beber Água!",
            message=f"Não se esqueça de se hidratar. Sua meta é {self.total_goal}ml.",
            app_name="Lembrete de Água"
        )


class WaterApp(App):
    def build(self):
        # O Kivy vai carregar automaticamente o arquivo 'waterapp.kv'
        return WaterAppLayout()


if __name__ == '__main__':
    WaterApp().run()