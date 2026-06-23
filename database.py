import os
import sqlite3
import shutil
from datetime import datetime

# Configurações de diretório e nome do banco
DB_NAME = "balanco.db"
FOTOS_DIR = os.path.join(".", "fotos_ativos")

def inicializar_banco():
    """Garante que a pasta de fotos e as tabelas existam."""
    if not os.path.exists(FOTOS_DIR):
        os.makedirs(FOTOS_DIR)
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS localizacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filial TEXT, sala TEXT, setor TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS ativos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT, tipo TEXT, localizacao_id INTEGER,
                        preco REAL, data_aquisicao TEXT, estado TEXT,
                        foto_path TEXT, observacoes TEXT,
                        FOREIGN KEY (localizacao_id) REFERENCES localizacoes(id))''')
    
    try:
        cursor.execute("SELECT status FROM ativos LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE ativos ADD COLUMN status TEXT DEFAULT 'Em uso'")
    
    cursor.execute("SELECT COUNT(*) FROM localizacoes")
    if cursor.fetchone()[0] == 0:
        dados = [
            ("Matriz", "Sala 101", "TI"),
            ("Matriz", "Sala 102", "RH"),
            ("Filial Sul", "Bloco A", "Operações")
        ]
        cursor.executemany("INSERT INTO localizacoes (filial, sala, setor) VALUES (?, ?, ?)", dados)
    
    conn.commit()
    conn.close()

def obter_localizacoes():
    """Busca as filiais e setores cadastrados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filial, sala, setor FROM localizacoes")
    dados = cursor.fetchall()
    conn.close()
    return dados

def salvar_localizacao(filial, sala, setor):
    """Insere uma nova localização customizada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO localizacoes (filial, sala, setor) VALUES (?, ?, ?)", (filial, sala, setor))
    conn.commit()
    conn.close()

def salvar_ativo(nome, tipo, status, loc_id, preco, data, estado, foto_origem, obs):
    """Salva um novo ativo, pega o ID gerado, e renomeia a foto."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''INSERT INTO ativos (nome, tipo, status, localizacao_id, preco, data_aquisicao, estado, foto_path, observacoes)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                   (nome, tipo, status, loc_id, preco, data, estado, "", obs))
    
    novo_id = cursor.lastrowid 
    
    if foto_origem and os.path.exists(foto_origem):
        extensao = os.path.splitext(foto_origem)[1] 
        nome_foto = f"ativo_{novo_id}{extensao}" 
        foto_destino = os.path.join(FOTOS_DIR, nome_foto)
        shutil.copy(foto_origem, foto_destino)
        cursor.execute("UPDATE ativos SET foto_path = ? WHERE id = ?", (foto_destino, novo_id))

    conn.commit()
    conn.close()

def deletar_ativo(ativo_id):
    """Remove o registro do ativo do banco de dados e tenta apagar a sua foto física."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT foto_path FROM ativos WHERE id = ?", (ativo_id,))
    foto = cursor.fetchone()
    if foto and foto[0] and os.path.exists(foto[0]):
        try:
            os.remove(foto[0])
        except:
            pass 
            
    cursor.execute("DELETE FROM ativos WHERE id = ?", (ativo_id,))
    conn.commit()
    conn.close()

def atualizar_ativo(ativo_id, nome, tipo, status, loc_id, preco, data, estado, foto_origem, obs):
    """Modifica os dados de um patrimônio existente."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if foto_origem and os.path.exists(foto_origem) and "fotos_ativos" not in foto_origem:
        extensao = os.path.splitext(foto_origem)[1]
        nome_foto = f"ativo_{ativo_id}{extensao}"
        foto_destino = os.path.join(FOTOS_DIR, nome_foto)
        shutil.copy(foto_origem, foto_destino)
        
        cursor.execute('''UPDATE ativos SET nome=?, tipo=?, status=?, localizacao_id=?, preco=?, 
                          data_aquisicao=?, estado=?, foto_path=?, observacoes=? WHERE id=?''',
                       (nome, tipo, status, loc_id, preco, data, estado, foto_destino, obs, ativo_id))
    else:
        cursor.execute('''UPDATE ativos SET nome=?, tipo=?, status=?, localizacao_id=?, preco=?, 
                          data_aquisicao=?, estado=?, observacoes=? WHERE id=?''',
                       (nome, tipo, status, loc_id, preco, data, estado, obs, ativo_id))
        
    conn.commit()
    conn.close()

def obter_lista_ativos():
    """Busca todos os campos detalhados para a listagem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT a.id, a.nome, a.tipo, a.status, a.localizacao_id, a.preco, 
                      a.data_aquisicao, a.estado, l.filial, l.sala, l.setor, a.foto_path, a.observacoes
                      FROM ativos a JOIN localizacoes l ON a.localizacao_id = l.id''')
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_dados_exportacao():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, tipo, status, preco, data_aquisicao, estado, foto_path FROM ativos")
    dados = cursor.fetchall()
    conn.close()
    return dados

# ------------------------------------------
# FUNÇÕES RESTAURADAS PARA O BALANÇO FINANCEIRO
# ------------------------------------------

def obter_resumo_tipos():
    """Busca a soma de valores agrupada por tipo de ativo (para o balanço)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, SUM(preco), COUNT(id) FROM ativos GROUP BY tipo")
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_resumo_filiais():
    """Busca a soma de valores agrupada por filial (para o balanço)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''SELECT l.filial, SUM(a.preco) FROM ativos a 
                      JOIN localizacoes l ON a.localizacao_id = l.id GROUP BY l.filial''')
    dados = cursor.fetchall()
    conn.close()
    return dados