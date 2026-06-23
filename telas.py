import os
from datetime import datetime
import flet as ft
import database 

def criar_interface(page: ft.Page):
    """Função principal que constrói todas as telas e retorna o menu de abas."""
    
    foto_selecionada_path = ft.Ref[ft.Text]()
    caminho_foto_temp = ""

    # ------------------------------------------
    # COMPONENTES COMPARTILHADOS E SERVIÇOS
    # ------------------------------------------
    
    # SOLUÇÃO RESTAURADA: FilePicker como serviço (sem a tela vermelha!)
    picker = ft.FilePicker()
    page.services.append(picker) 

    # Função assíncrona direta para o cadastro principal
    async def ao_selecionar_foto(e):
        nonlocal caminho_foto_temp
        files = await picker.pick_files(file_type=ft.FilePickerFileType.IMAGE)
        if files:
            caminho_foto_temp = files[0].path
            txt_foto.value = f"Foto selecionada: {files[0].name}"
            page.update() 

    def mostrar_aviso(mensagem):
        aviso = ft.SnackBar(content=ft.Text(mensagem), open=True)
        page.overlay.append(aviso)
        page.update()

    def abrir_ajuda_tipo(e):
        def fechar_dialogo(e):
            dialogo.open = False
            page.update()

        dialogo = ft.AlertDialog(
            title=ft.Text("Guia Patrimonial Corporativo"),
            content=ft.Column([
                ft.Text("🏢 Categorias do Ativo:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("📦 Estoque: Itens mantidos para venda no curso normal dos negócios.", size=13),
                ft.Text("🏭 Imobilizado: Bens físicos usados na empresa com vida útil superior a 1 ano.", size=13),
                ft.Text("📈 Propriedade para Investimento: Imóveis mantidos para gerar aluguel ou valorização.", size=13),
                ft.Divider(),
                ft.Text("🚦 Status do Bem:", weight=ft.FontWeight.BOLD, size=16),
                ft.Text("🟢 Em uso: O ativo está operando normalmente.", size=13),
                ft.Text("🟡 Ocioso: Disponível na empresa, mas sem uso atual.", size=13),
                ft.Text("🛠️ Em manutenção: Sendo consertado ou atualizado.", size=13),
                ft.Text("🔴 Para venda: Ativo destinado ao desinvestimento.", size=13),
            ], tight=True, scroll="adaptive"),
            actions=[ft.TextButton("Entendi", on_click=fechar_dialogo)]
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    # ------------------------------------------
    # COMPONENTES DE CADASTRO
    # ------------------------------------------
    txt_nome = ft.TextField(label="Nome do Item", expand=True)
    
    drop_tipo = ft.Dropdown(label="Categoria do Ativo", expand=True, options=[
        ft.dropdown.Option("Estoque"), ft.dropdown.Option("Imobilizado"), ft.dropdown.Option("Propriedade para Investimento")
    ])
    
    drop_status = ft.Dropdown(label="Status do Bem", expand=True, options=[
        ft.dropdown.Option("Em uso"), ft.dropdown.Option("Ocioso"), ft.dropdown.Option("Em manutenção"), ft.dropdown.Option("Para venda")
    ], value="Em uso")
    
    drop_loc = ft.Dropdown(label="Localização", expand=True)

    def atualizar_opcoes_localizacao():
        locais = database.obter_localizacoes()
        drop_loc.options = [ft.dropdown.Option(key=str(i), text=f"{f} > {s} > {t}") for i, f, s, t in locais]
        page.update()

    def abrir_cadastro_localizacao(e):
        txt_nova_filial = ft.TextField(label="Filial (Ex: Matriz)")
        txt_nova_sala = ft.TextField(label="Sala (Ex: Sala 302)")
        txt_novo_setor = ft.TextField(label="Setor (Ex: Contabilidade)")

        def submeter_nova_localizacao(e):
            if not txt_nova_filial.value or not txt_nova_sala.value or not txt_novo_setor.value:
                mostrar_aviso("Preencha Filial, Sala e Setor!")
                return
            
            database.salvar_localizacao(txt_nova_filial.value, txt_nova_sala.value, txt_novo_setor.value)
            mostrar_aviso("Nova localização adicionada com sucesso!")
            atualizar_opcoes_localizacao()
            dialogo_loc.open = False
            page.update()

        dialogo_loc = ft.AlertDialog(
            title=ft.Text("Nova Localização"),
            content=ft.Column([txt_nova_filial, txt_nova_sala, txt_novo_setor], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(dialogo_loc, 'open', False), page.update()]),
                ft.TextButton("Salvar", on_click=submeter_nova_localizacao)
            ]
        )
        page.overlay.append(dialogo_loc)
        dialogo_loc.open = True
        page.update()

    btn_add_loc = ft.IconButton(icon=ft.Icons.ADD_LOCATION_ALT, on_click=abrir_cadastro_localizacao, icon_color=ft.Colors.BLUE)

    # ------------------------------------------
    # LÓGICA DE AUTOCOMPLETAR
    # ------------------------------------------
    caixa_sugestoes = ft.Column(visible=False, spacing=0)

    def preencher_dados(nome, tipo, status, preco):
        txt_nome.value = nome
        drop_tipo.value = tipo
        drop_status.value = status 
        txt_preco.value = f"{preco:.2f}"
        caixa_sugestoes.visible = False
        page.update()

    def ao_digitar_nome(e):
        texto_digitado = txt_nome.value.lower()
        caixa_sugestoes.controls.clear()
        
        if len(texto_digitado) > 0:
            ativos = database.obter_lista_ativos()
            sugestoes_unicas = {}
            
            for id_atv, nome, tipo, status, loc_id, preco, data, estado, fil, sal, setr, foto, obs in ativos:
                if texto_digitado in nome.lower():
                    if nome not in sugestoes_unicas:
                        sugestoes_unicas[nome] = (tipo, status, preco)
            
            if sugestoes_unicas:
                caixa_sugestoes.visible = True
                for nome, dados in sugestoes_unicas.items():
                    tipo, status, preco = dados
                    caixa_sugestoes.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.SEARCH),
                            title=ft.Text(nome, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"{tipo} ({status}) | R$ {preco:.2f}"),
                            on_click=lambda e, n=nome, t=tipo, s=status, p=preco: preencher_dados(n, t, s, p)
                        )
                    )
            else:
                caixa_sugestoes.visible = False
        else:
            caixa_sugestoes.visible = False
            
        page.update()

    txt_nome.on_change = ao_digitar_nome 
    
    btn_ajuda = ft.IconButton(icon=ft.Icons.HELP_OUTLINE, on_click=abrir_ajuda_tipo)
    
    txt_preco = ft.TextField(label="Preço (R$)", value="0.00")
    txt_data = ft.TextField(label="Data", value=datetime.now().strftime("%d/%m/%Y"))
    drop_estado = ft.Dropdown(label="Estado Físico", options=[ft.dropdown.Option("Novo"), ft.dropdown.Option("Bom"), ft.dropdown.Option("Ruim")])
    
    txt_foto = ft.Text("Nenhuma foto", italic=True)
    
    # ATUALIZADO: Chamando diretamente a função assíncrona correta
    btn_foto = ft.ElevatedButton("Selecionar Foto", icon=ft.Icons.CAMERA, on_click=ao_selecionar_foto)
    txt_obs = ft.TextField(label="Observações", multiline=True)

    def submeter_cadastro(e):
        nonlocal caminho_foto_temp
        if not txt_nome.value or not drop_tipo.value or not drop_loc.value or not drop_status.value:
            mostrar_aviso("Preencha Nome, Categoria, Status e Localização!")
            return
        
        e.control.disabled = True
        page.update()
        
        try:
            preco = float(txt_preco.value.replace(",", "."))
        except:
            preco = 0.0
            
        database.salvar_ativo(txt_nome.value, drop_tipo.value, drop_status.value, int(drop_loc.value), preco, txt_data.value, drop_estado.value, caminho_foto_temp, txt_obs.value)
        
        mostrar_aviso("Ativo salvo com sucesso!")
        caminho_foto_temp = "" 
        txt_nome.value = ""
        caixa_sugestoes.visible = False 
        txt_foto.value = "Nenhuma foto" 
        
        e.control.disabled = False
        page.update()
        atualizar_telas()

    tela_cadastro = ft.Container(
        content=ft.Column([
            ft.Text("Cadastrar Novo Ativo", size=20, weight=ft.FontWeight.BOLD),
            txt_nome,
            caixa_sugestoes, 
            ft.Row([drop_tipo, btn_ajuda]),
            drop_status,
            ft.Row([drop_loc, btn_add_loc]), 
            ft.Row([txt_preco, txt_data]), drop_estado,
            ft.Row([btn_foto, txt_foto]), txt_obs,
            ft.FilledButton("Salvar Ativo", on_click=submeter_cadastro)
        ], scroll="adaptive"), padding=20
    )

    # ------------------------------------------
    # LÓGICA DE EXCLUSÃO E EDIÇÃO VISUAL
    # ------------------------------------------
    
    def confirmar_exclusao_ativo(id_atv, nome_atv):
        def deletar_confirmado(e):
            database.deletar_ativo(id_atv)
            mostrar_aviso(f"'{nome_atv}' excluído com sucesso!")
            dialogo_del.open = False
            atualizar_telas()
            page.update()

        dialogo_del = ft.AlertDialog(
            title=ft.Text("Excluir Ativo"),
            content=ft.Text(f"Tem certeza que deseja excluir o ativo '{nome_atv}'? Essa ação é permanente."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: [setattr(dialogo_del, 'open', False), page.update()]),
                ft.TextButton("Excluir", on_click=deletar_confirmado, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        page.overlay.append(dialogo_del)
        dialogo_del.open = True
        page.update()

    def abrir_edicao_ativo(id_atv, nome, tipo, status, loc_id, preco, data, estado, foto_antiga, obs):
        edit_nome = ft.TextField(label="Nome do Item", value=nome)
        edit_tipo = ft.Dropdown(label="Categoria", value=tipo, options=[
            ft.dropdown.Option("Estoque"), ft.dropdown.Option("Imobilizado"), ft.dropdown.Option("Propriedade para Investimento")
        ])
        edit_status = ft.Dropdown(label="Status", value=status, options=[
            ft.dropdown.Option("Em uso"), ft.dropdown.Option("Ocioso"), ft.dropdown.Option("Em manutenção"), ft.dropdown.Option("Para venda")
        ])
        
        locais = database.obter_localizacoes()
        edit_loc = ft.Dropdown(label="Localização", value=str(loc_id), options=[ft.dropdown.Option(key=str(i), text=f"{f} > {s} > {t}") for i, f, s, t in locais])
        edit_preco = ft.TextField(label="Preço (R$)", value=f"{preco:.2f}")
        edit_data = ft.TextField(label="Data", value=data)
        edit_estado = ft.Dropdown(label="Estado Físico", value=estado, options=[ft.dropdown.Option("Novo"), ft.dropdown.Option("Bom"), ft.dropdown.Option("Ruim")])
        edit_obs = ft.TextField(label="Observações", value=obs, multiline=True)
        
        caminho_foto_edit = foto_antiga
        txt_foto_edit = ft.Text(os.path.basename(foto_antiga) if foto_antiga else "Nenhuma foto", italic=True)
        
        # MÁGICA DO FLET NOVO: Função de edição de foto limpa e assíncrona!
        async def ao_selecionar_foto_edit(e):
            nonlocal caminho_foto_edit
            files = await picker.pick_files(file_type=ft.FilePickerFileType.IMAGE)
            if files:
                caminho_foto_edit = files[0].path
                txt_foto_edit.value = f"Nova foto: {files[0].name}"
                page.update()
                
        btn_foto_edit = ft.ElevatedButton("Alterar Foto", icon=ft.Icons.CAMERA, on_click=ao_selecionar_foto_edit)

        def salvar_edicao(e):
            if not edit_nome.value or not edit_tipo.value or not edit_loc.value or not edit_status.value:
                mostrar_aviso("Preencha os campos obrigatórios!")
                return
            try:
                p = float(edit_preco.value.replace(",", "."))
            except:
                p = 0.0
            
            database.atualizar_ativo(id_atv, edit_nome.value, edit_tipo.value, edit_status.value, int(edit_loc.value), p, edit_data.value, edit_estado.value, caminho_foto_edit, edit_obs.value)
            mostrar_aviso("Ativo atualizado com sucesso!")
            
            dialogo_edit.open = False
            atualizar_telas()
            page.update()

        def cancelar_edicao(e):
            dialogo_edit.open = False
            page.update()

        dialogo_edit = ft.AlertDialog(
            title=ft.Text(f"Editar Ativo #{id_atv}"),
            content=ft.Column([
                edit_nome, edit_tipo, edit_status, edit_loc,
                ft.Row([edit_preco, edit_data]), edit_estado,
                ft.Row([btn_foto_edit, txt_foto_edit]), edit_obs
            ], tight=True, scroll="adaptive"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_edicao),
                ft.TextButton("Salvar Alterações", on_click=salvar_edicao)
            ]
        )
        page.overlay.append(dialogo_edit)
        dialogo_edit.open = True
        page.update()

    # ------------------------------------------
    # TELA 2 e 3: BALANÇO E LISTAGEM
    # ------------------------------------------
    coluna_balanco = ft.Column(spacing=20)
    coluna_lista_dados = ft.Column(spacing=10) 

    filtra_categoria = ft.Dropdown(label="Filtrar por Categoria", expand=True, options=[
        ft.dropdown.Option("Todos"), ft.dropdown.Option("Estoque"), ft.dropdown.Option("Imobilizado"), ft.dropdown.Option("Propriedade para Investimento")
    ], value="Todos")

    filtra_status = ft.Dropdown(label="Filtrar por Status", expand=True, options=[
        ft.dropdown.Option("Todos"), ft.dropdown.Option("Em uso"), ft.dropdown.Option("Ocioso"), ft.dropdown.Option("Em manutenção"), ft.dropdown.Option("Para venda")
    ], value="Todos")

    filtra_categoria.on_change = lambda e: filtrar_lista_ativos()
    filtra_status.on_change = lambda e: filtrar_lista_ativos()

    def filtrar_lista_ativos():
        coluna_lista_dados.controls.clear()
        ativos = database.obter_lista_ativos()
        
        cat_alvo = filtra_categoria.value
        status_alvo = filtra_status.value
        
        for id_atv, nome, tipo, status, loc_id, preco, data, estado, fil, sal, setr, foto, obs in ativos:
            passa_filtro_cat = (cat_alvo == "Todos" or tipo == cat_alvo)
            passa_filtro_status = (status_alvo == "Todos" or status == status_alvo)
            
            if passa_filtro_cat and passa_filtro_status:
                img = ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED)
                if foto and os.path.exists(foto):
                    img = ft.Image(src=foto, width=50, height=50)
                
                cor_status = ft.Colors.GREEN if status == "Em uso" else ft.Colors.ORANGE if status == "Ocioso" else ft.Colors.BLUE if status == "Em manutenção" else ft.Colors.RED
                
                coluna_lista_dados.controls.append(
                    ft.Card(content=ft.Container(
                        content=ft.Row([
                            img, 
                            ft.Text(f"{nome} ({tipo})\n{fil} > {setr}\nStatus: {status}", expand=True, color=cor_status), 
                            ft.Text(f"R$ {preco:.2f}", weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.EDIT, 
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, i=id_atv, n=nome, t=tipo, s=status, l=loc_id, p=preco, d=data, est=estado, f=foto, o=obs: abrir_edicao_ativo(i, n, t, s, l, p, d, est, f, o)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE, 
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, i=id_atv, n=nome: confirmar_exclusao_ativo(i, n)
                            )
                        ]),
                        padding=10
                    ))
                )
        page.update()

    def atualizar_telas():
        coluna_balanco.controls.clear()
        dados_tipo = database.obter_resumo_tipos()
        dados_filial = database.obter_resumo_filiais()
        
        coluna_balanco.controls.append(ft.Text("Balanço Financeiro por Categorias", size=20, weight=ft.FontWeight.BOLD))
        for tipo, soma, qtd in dados_tipo:
            coluna_balanco.controls.append(ft.Text(f"{tipo}: R$ {soma:.2f} ({qtd} itens)", size=16))
            
        coluna_balanco.controls.append(ft.Divider())
        coluna_balanco.controls.append(ft.Text("Patrimônio por Filial", size=18, weight=ft.FontWeight.BOLD))
        
        for filial, soma in dados_filial:
            coluna_balanco.controls.append(ft.Text(f"{filial}: R$ {soma:.2f}", color=ft.Colors.GREEN))

        filtrar_lista_ativos()

    tela_listagem_completa = ft.Container(
        content=ft.Column([
            ft.Text("Gerenciamento e Consulta de Bens", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([filtra_categoria, filtra_status]), 
            ft.Divider(),
            coluna_lista_dados 
        ], scroll="adaptive"), padding=20
    )

    # ------------------------------------------
    # TELA 4: EXPORTAR
    # ------------------------------------------
    def exportar_csv(e):
        dados = database.obter_dados_exportacao()
        pasta_relatorios = "relatorios"
        if not os.path.exists(pasta_relatorios):
            os.makedirs(pasta_relatorios)
            
        nome_arq = os.path.join(pasta_relatorios, f"relatorio_{int(datetime.now().timestamp())}.csv")
        
        with open(nome_arq, "w", encoding="utf-8") as f:
            f.write("ID;Nome;Categoria;Status;Preco;Data;Estado;Foto\n")
            for r in dados:
                caminho_foto = r[7]
                nome_da_foto = os.path.basename(caminho_foto) if caminho_foto else "Sem foto"
                f.write(f"{r[0]};{r[1]};{r[2]};{r[3]};{r[4]};{r[5]};{r[6]};{nome_da_foto}\n")
                
        mostrar_aviso(f"Sucesso! Relatório salvo na pasta: {pasta_relatorios}")

    tela_exportar = ft.Container(
        content=ft.Column([
            ft.Text("Exportar Dados", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Gerar CSV", icon=ft.Icons.DOWNLOAD, on_click=exportar_csv)
        ]), padding=20
    )

    # ------------------------------------------
    # NAVEGAÇÃO PRINCIPAL
    # ------------------------------------------
    area_conteudo = ft.Container(content=tela_cadastro, expand=True)

    def mudar_tela(indice):
        if indice == 0:
            area_conteudo.content = tela_cadastro
        elif indice == 1:
            atualizar_telas()
            area_conteudo.content = coluna_balanco
        elif indice == 2:
            atualizar_telas()
            area_conteudo.content = tela_listagem_completa 
        elif indice == 3:
            area_conteudo.content = tela_exportar
        page.update()

    menu_botoes = ft.Row(
        controls=[
            ft.ElevatedButton("Cadastrar", icon=ft.Icons.ADD_BOX, on_click=lambda _: mudar_tela(0)),
            ft.ElevatedButton("Balanço", icon=ft.Icons.ANALYTICS, on_click=lambda _: mudar_tela(1)),
            ft.ElevatedButton("Lista", icon=ft.Icons.LIST, on_click=lambda _: mudar_tela(2)),
            ft.ElevatedButton("Exportar", icon=ft.Icons.DOWNLOAD, on_click=lambda _: mudar_tela(3)),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    atualizar_opcoes_localizacao()
    atualizar_telas() 

    layout_principal = ft.Column(
        controls=[
            menu_botoes,
            ft.Divider(),
            area_conteudo
        ],
        expand=True
    )
    
    return layout_principal