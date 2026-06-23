import flet as ft
import database      
import telas         
import ssl           # Biblioteca nativa de segurança

# 1. TRUQUE DE SEGURANÇA:
# Pede ao Python para não bloquear downloads confiáveis na primeira execução.
ssl._create_default_https_context = ssl._create_unverified_context

def main(page: ft.Page):
    # Configurações básicas da janela
    page.title = "Sistema de Balanço Patrimonial"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1000
    page.window_height = 700

    # Prepara o banco de dados antes de abrir a tela
    database.inicializar_banco()

    # Chama a função do arquivo telas.py para desenhar a interface
    interface_principal = telas.criar_interface(page)

    # Adiciona a interface construída na página
    page.add(interface_principal)

# Inicia o aplicativo Flet
if __name__ == "__main__":
    # 2. ATUALIZAÇÃO DO FLET:
    # Mudamos de ft.app para ft.run conforme exigido pela versão mais nova!
    ft.run(main)