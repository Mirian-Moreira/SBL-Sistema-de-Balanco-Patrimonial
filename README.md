# 🏢 SBL - Sistema de Balanço Patrimonial

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flet](https://img.shields.io/badge/Flet-UI-purple.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Android-green.svg)

Um sistema completo de gerenciamento de ativos corporativos (CRUD) desenvolvido 100% em Python com a biblioteca [Flet](https://flet.dev/). O sistema permite o controle rigoroso de bens, cálculo de patrimônio, gestão de imagens de equipamentos e exportação de relatórios, podendo ser executado tanto como um programa de Windows (`.exe`) quanto como um aplicativo Android (`.apk`).

## ✨ Funcionalidades Principais

* **Cadastro Completo de Ativos:** Registro de nome, categoria, status, localização (filial/sala/setor), preço, estado físico e observações.
* **Gestão de Imagens Local:** Upload de fotos dos equipamentos, renomeadas automaticamente com o ID do banco de dados e salvas em uma pasta local estruturada (`fotos_ativos/`).
* **Sistema de Busca Inteligente:** Autocompletar na barra de pesquisa para localizar rapidamente equipamentos já cadastrados.
* **Dashboard Financeiro (Balanço):** Resumo automático do valor patrimonial agrupado por Categoria do ativo e por Filial da empresa.
* **Listagem e Filtros:** Consulta em tempo real do inventário com filtros combinados por Status e Categoria.
* **Controle Total (CRUD):** Capacidade de editar dados e fotos de itens já cadastrados, além de exclusão segura (removendo os dados do banco e o arquivo de imagem do computador).
* **Exportação de Relatórios:** Geração de planilhas CSV com os dados do inventário e link para os nomes dos arquivos das fotos, salvas automaticamente na pasta `relatorios/`.
* **Multiplataforma:** Interface responsiva adaptada para telas de computador e dispositivos móveis.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface Gráfica:** Flet (Baseado em Flutter)
* **Banco de Dados:** SQLite3 (Nativo do Python)
* **Manipulação de Arquivos:** Bibliotecas `os`, `shutil` e manipulação de arquivos nativa para CSV.
* **Build/Deploy:** PyInstaller (Windows) e Flet CLI/Flutter (Android).

## 📂 Estrutura do Projeto

```
📁 SBL-Balanco-Patrimonial/
│
├── main.py             # Ponto de entrada do aplicativo e configurações da janela
├── telas.py            # Componentes visuais, rotas, lógica de interface e Flet
├── database.py         # Conexão com SQLite, queries SQL e manipulação das fotos
├── gerar_apk.py        # Script customizado para build de Android contornando erros do Windows
│
├── fotos_ativos/       # Diretório gerado automaticamente para salvar imagens dos bens
├── relatorios/         # Diretório gerado automaticamente para os relatórios CSV exportados
└── balanco.db          # Arquivo do banco de dados gerado no primeiro acesso
```
## 🚀 Como Executar o Projeto Localmente

**Pré-requisitos**
Python 3.10 ou superior.

 **Passos**
* Clone o repositório:
```
git clone [https://github.com/Mirian_Moreira/SBL-Balanco-Patrimonial.git](https://github.com/Mirian_Moreira/SBL-Balanco-Patrimonial.git)
cd SBL-Balanco-Patrimonial
```
* Instale o Flet:
```
pip install flet
```
* Execute o sistema no modo desktop:
```
flet run main.py
(Ou acesse pelo navegador/celular via Wi-Fi usando flet run --web main.py)
```
## 📦 Compilando para Windows (.exe)

Para gerar um arquivo executável para Windows, utilizei o PyInstaller. O comando abaixo garante que as dependências nativas do Flet (ícones e núcleo) sejam empacotadas corretamente.

* Instale o PyInstaller:
```
pip install pyinstaller
```
* Gere o executável:
```
python -m PyInstaller --noconsole --name "SistemaPatrimonial" --collect-all flet --collect-all flet_core main.py
```
O programa final estará disponível na pasta dist/SistemaPatrimonial.

## 📱 Compilando para Android (.apk)

Para contornar problemas comuns do Flutter/Gradle em ambientes Windows com caracteres especiais na pasta de usuário (ex: acentos, cedilhas) e erros de certificado SSL no download do SDK, este projeto inclui o script gerar_apk.py.

**Passos:**
* Instale a ferramenta CLI do Flet:
```
pip install "flet[cli]"
```
*Crie uma pasta na raiz do sistema para o cache do pub (ex: C:\PubCache).
*Ajuste os caminhos absolutos do Flutter e do Android SDK dentro do arquivo gerar_apk.py conforme a sua máquina local.

* Execute o script construtor:
```
python gerar_apk.py
```
O arquivo app-release.apk será gerado dentro da pasta build/apk/.

## 🤝 Contribuição

Sinta-se à vontade para realizar forks do projeto e submeter pull requests. Críticas e sugestões de melhorias de código são muito bem-vindas!

Projeto desenvolvido para otimização de gestão de ativos e exploração das capacidades multiplataforma da biblioteca Flet em Python.
