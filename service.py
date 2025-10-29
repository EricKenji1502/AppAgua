import time
import json
import os
from plyer import notification

# O Kivy/Buildozer nos dá acesso a uma variável que aponta para a pasta de dados do app
# Este é um truque para encontrar o caminho correto
# O nome 'waterapp' deve ser o mesmo do seu `package.name` no buildozer.spec
# O 'files' é o diretório padrão onde o `user_data_dir` do Kivy aponta.
data_dir = os.path.join(os.path.expanduser('~'), f'.local/share/waterapp/files')
data_file_path = os.path.join(data_dir, 'data.json')

def get_notification_interval():
    """Lê o intervalo de notificação do arquivo de dados."""
    default_interval_hours = 2
    try:
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as f:
                data = json.load(f)
                return data.get('settings', {}).get('notification_interval_hours', default_interval_hours)
    except Exception:
        # Se qualquer erro ocorrer, usa o valor padrão
        pass
    return default_interval_hours

while True:
    # Busca o intervalo atual
    interval_hours = get_notification_interval()
    interval_seconds = interval_hours * 3600

    # Envia a notificação
    notification.notify(
        title="Hora de Beber Água!",
        message=f"Lembrete para se hidratar. Você será notificado novamente em {interval_hours} horas.",
        app_name="Lembrete de Água"
    )
    
    # Espera o tempo configurado
    time.sleep(interval_seconds)