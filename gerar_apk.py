import sys
import ssl

# TRUQUE DE SEGURANÇA (O mesmo do seu main.py!)
# Pede ao Python para não bloquear os downloads do Flutter e do Android SDK por erro de certificado.
ssl._create_default_https_context = ssl._create_unverified_context

try:
    from flet_cli.cli import main
except ImportError:
    print("O Flet CLI não está instalado. Instale usando: python -m pip install flet[cli]")
    sys.exit(1)

if __name__ == "__main__":
    print("Iniciando o empacotamento para Android... Aguarde!")
    
    # Injetamos o comando
    sys.argv = ["flet", "build", "apk", "--product", "SistemaPatrimonial"]
    
    # Executamos o construtor
    main()