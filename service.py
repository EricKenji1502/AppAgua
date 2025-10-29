import time
from plyer import notification

# Loop infinito que rodará em segundo plano
while True:
    # Envia a notificação
    notification.notify(
        title="Hora de Beber Água!",
        message="Um copo de água agora vai te fazer muito bem. Não se esqueça de se hidratar!",
        app_name="Lembrete de Água"
    )
    # Espera 2 horas (2 * 60 * 60 = 7200 segundos)
    time.sleep(7200)