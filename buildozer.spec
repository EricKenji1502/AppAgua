[app]

# (str) Título do seu aplicativo
title = Lembrete de Água

# (str) Nome do pacote, sem espaços ou caracteres especiais.
package.name = waterapp

# (str) Domínio do pacote, geralmente em ordem inversa.
# MUDE ISSO para algo único seu. Ex: se seu site é meunome.com, use com.meunome
package.domain = org.meuapp

# (str) Diretório do código fonte. '.' significa a pasta atual.
source.dir = .

# (str) Arquivo principal a ser executado.
source.main_py = main.py

# (list) Lista de arquivos para incluir no projeto (deixe em branco para incluir todos).
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Versão do seu aplicativo.
version = 1.0

# (list) Lista de bibliotecas que seu aplicativo precisa.
# Adicionamos plyer e android-permissions para as funcionalidades que criamos.
requirements = python3,kivy,plyer,android-permissions

# (str) Orientação da tela. Pode ser 'portrait', 'landscape' ou 'all'.
orientation = portrait

# (str) Ícone do seu aplicativo. Crie um arquivo 'icon.png' de 512x512 pixels.
icon.filename = %(modulename)s.png

# (str) Imagem de splash screen (tela de carregamento).
presplash.filename = %(modulename)s-presplash.png

# (bool) Se o aplicativo deve rodar em tela cheia.
fullscreen = 0


[buildozer]

# (int) Nível de log (0 = silencioso, 1 = info, 2 = debug). 2 é bom para encontrar erros.
log_level = 2

# (int) Mostra um aviso se o espaço em disco for baixo.
warn_on_root = 1


# --- SEÇÃO ANDROID ---

# (list) Permissões que seu aplicativo precisa no Android.
# POST_NOTIFICATIONS é essencial para o Android 13+.
android.permissions = POST_NOTIFICATIONS

# (list) Serviços a serem declarados para rodar em segundo plano.
# Formato: NomeDoServico:caminho/para/o/arquivo.py
# O "NomeDoServico" (Myservice) deve corresponder ao que chamamos no main.py (ServiceMyservice)
services = Myservice:service.py