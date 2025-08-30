import asyncio
import os
from datetime import datetime
from pywinauto import Application, timings, findwindows
import sys
import io
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from worker_automate_hub.models.dto.rpa_historico_request_dto import (
    RpaHistoricoStatusEnum,
    RpaRetornoProcessoDTO,
    RpaTagDTO,
    RpaTagEnum,
)
from worker_automate_hub.models.dto.rpa_processo_entrada_dto import (
    RpaProcessoEntradaDTO,
)
from rich.console import Console
import re
from pywinauto.keyboard import send_keys
import warnings
from pywinauto.application import Application
from worker_automate_hub.api.client import get_config_by_name, send_file
from worker_automate_hub.utils.util import (
    kill_all_emsys,
    login_emsys,
    set_variable,
    type_text_into_field,
    worker_sleep,
)
from pywinauto_recorder.player import set_combobox

from datetime import timedelta
import pyautogui
from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.utils_nfe_entrada import EMSys

emsys = EMSys()

console = Console()
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False


async def extracao_saldo_estoque(task: RpaProcessoEntradaDTO):
    try:
        config = await get_config_by_name("login_emsys")
        periodo = task.configEntrada["periodo"]
        periodo_format = periodo.replace("/", "")
        filial = task.configEntrada["filialEmpresaOrigem"]
        historico_id = task.historico_id

        console.print("Finalizando processos antigos do EMSys...", style="bold yellow")
        await kill_all_emsys()

        console.print("Iniciando EMSys...", style="bold green")
        app = Application(backend="win32").start("C:\\Rezende\\EMSys3\\EMSys3_35.exe")
        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            message="32-bit application should be automated using 32-bit Python",
        )

        console.print("Fazendo login no EMSys...", style="bold cyan")
        return_login = await login_emsys(
            config.conConfiguracao, app, task, filial_origem=filial
        )

        if return_login.sucesso:
            console.print("Login realizado com sucesso", style="bold green")
            type_text_into_field(
                "Rel. Saldo Estoque ", app["TFrmMenuPrincipal"]["Edit"], True, "50"
            )
            pyautogui.press("enter")
            await worker_sleep(2)
            pyautogui.press("enter")
        else:
            logger.info(f"\nError Message: {return_login.retorno}")
            console.print(f"Erro no login: {return_login.retorno}", style="bold red")
            return return_login

        await worker_sleep(2)

        console.print("Abrindo janela Relatório de Saldo de Estoque...", style="bold cyan")
        app = Application().connect(class_name="TFrmRelSaldoEstoque", timeout=60)
        main_window = app["TFrmRelSaldoEstoque"]
        main_window.set_focus()

        console.print("Marcando campo de data...", style="bold cyan")
        main_window.child_window(class_name="TCheckBox", found_index=3).click_input()

        await worker_sleep(2)

        console.print(f"Inserindo período: {periodo}", style="bold cyan")
        data_input = main_window.child_window(class_name="TDBIEditDate", found_index=0) 
        data_input.set_edit_text(periodo)

        console.print("Gerando relatório...", style="bold cyan")
        main_window.child_window(class_name="TBitBtn", found_index=0).click_input()  

        timings.wait_until_passes(
            timeout=1800,
            retry_interval=1,
            func=lambda: Application().connect(class_name="TFrmPreviewRelatorio"),
        )
        await worker_sleep(2)

        console.print("Abrindo Preview Relatório...", style="bold cyan")
        app = Application().connect(class_name="TFrmPreviewRelatorio")
        main_window = app["TFrmPreviewRelatorio"]
        main_window.set_focus()

        max_tentativas = 5
        tentativa = 1
        sucesso = False

        while tentativa <= max_tentativas and not sucesso:
            console.print(f"Tentativa {tentativa} de {max_tentativas}", style="bold cyan")

            # 1) Abrir o picker de formatos pelo botão (imagem)
            console.print("Procurando botão de salvar (imagem)...", style="bold cyan")
            caminho_img = r'assets\\extracao_relatorios\\btn_salvar.png'
            if os.path.isfile(caminho_img):
                pos = pyautogui.locateCenterOnScreen(caminho_img, confidence=0.9)
                if pos:
                    pyautogui.click(pos)
                    console.print("Clique realizado no botão salvar", style="bold green")
                else:
                    console.print("Imagem encontrada mas não está visível na tela", style="bold yellow")
            else:
                console.print("Imagem do botão salvar NÃO existe", style="bold red")

            await worker_sleep(8)

            # 2) Selecionar formato "Excel" na janela TFrmRelatorioFormato
            console.print("Selecionando formato Excel...", style="bold cyan")
            try:
                app_fmt = Application().connect(class_name="TFrmRelatorioFormato", timeout=10)
                win_fmt = app_fmt["TFrmRelatorioFormato"]
                win_fmt.wait("visible", timeout=10)

                combo = win_fmt.ComboBox
                textos = combo.texts()
                console.print(f"Itens do ComboBox: {textos}", style="bold yellow")

                # Se souber o índice correto, mantenha. Caso contrário, tente por texto contendo 'Excel'
                try:
                    combo.select(8)
                except Exception:
                    alvo = None
                    for i, t in enumerate(textos):
                        if "EXCEL" in str(t).upper() or "XLSX" in str(t).upper():
                            alvo = i
                            break
                    if alvo is not None:
                        combo.select(alvo)
                    else:
                        console.print("Não foi possível localizar a opção de Excel no ComboBox.", style="bold red")
                        tentativa += 1
                        await worker_sleep(2)
                        continue

                await worker_sleep(1)

                # Botão OK/Confirmar na janela de formato
                # Em muitos Delphi VCL, TBitBtn com found_index=1 costuma ser OK.
                win_fmt.child_window(class_name="TBitBtn", found_index=1).wait("enabled", timeout=5)
                win_fmt.child_window(class_name="TBitBtn", found_index=1).click_input()
            except Exception as e:
                console.print(f"Falha ao selecionar formato: {e}", style="bold red")
                tentativa += 1
                await worker_sleep(3)
                continue

            await worker_sleep(5)

            # 3) Janela "Salvar para arquivo"
            console.print("Abrindo janela de salvar arquivo...", style="bold cyan")
            try:
                app_save = Application().connect(title_re="Salvar para arquivo", timeout=30)
                win_save = app_save.window(title_re="Salvar para arquivo")
                win_save.wait("visible", timeout=30)
            except Exception as e:
                console.print(f"Não achou a janela 'Salvar para arquivo': {e}", style="bold red")
                tentativa += 1
                await worker_sleep(3)
                continue

            # Caminho do arquivo a salvar
            caminho_arquivo = rf"C:\Users\automatehub\Downloads\saldo_estoque_{periodo_format}_{filial}.xlsx"

            # Se já existe, removemos para evitar pop-up de confirmação
            if os.path.exists(caminho_arquivo):
                try:
                    os.remove(caminho_arquivo)
                    console.print("Arquivo existente removido para evitar prompt de sobrescrita.", style="bold yellow")
                except Exception as e:
                    console.print(f"Não foi possível remover o arquivo existente: {e}", style="bold red")

            try:
                # Campo "Nome" (Edit, control_id=1148)
                campo_nome = win_save.child_window(class_name="Edit", control_id=1148).wrapper_object()
                campo_nome.set_focus()
                # limpa conteúdo
                try:
                    campo_nome.set_edit_text("")
                except Exception:
                    # fallback limpando com Ctrl+A + Delete
                    campo_nome.type_keys("^a{DELETE}", pause=0.02)

                # digita caminho
                campo_nome.type_keys(caminho_arquivo, with_spaces=True, pause=0.01)
                console.print(f"Arquivo configurado para: {caminho_arquivo}", style="bold green")

                await worker_sleep(1)

                # Botão Salvar (primeiro Button)
                btn_salvar = win_save.child_window(class_name="Button", found_index=0)
                btn_salvar.wait("enabled", timeout=10)
                btn_salvar.click_input()
            except Exception as e:
                console.print(f"Erro ao confirmar salvar: {e}", style="bold red")
                tentativa += 1
                await worker_sleep(3)
                continue

            await worker_sleep(2)

            # 3.1) Tratar confirmação de sobrescrita, se aparecer
            try:
                # Pode vir em PT/EN dependendo do SO
                # Título comum: "Confirm Save As" (EN) ou "Confirmar Salvar Como" (PT)
                try:
                    app_conf = Application().connect(title_re="Confirm(ar)?( )?Salvar( )?Como|Confirm Save As", timeout=3)
                    win_conf = app_conf.window(title_re="Confirm(ar)?( )?Salvar( )?Como|Confirm Save As")
                    win_conf.wait("visible", timeout=3)
                    # Botões costumam ser "Sim"/"Yes" como class_name="Button"
                    # Tente o primeiro botão (Yes/Sim)
                    win_conf.child_window(class_name="Button", found_index=0).click_input()
                    console.print("Confirmação de sobrescrita respondida.", style="bold yellow")
                except Exception:
                    pass
            except Exception:
                pass

            await worker_sleep(2)

            # 4) Aguardar o processamento/Printing encerrar
            console.print("Aguardando finalização do processo de impressão/salvamento...", style="bold cyan")
            try:
                app_print = Application().connect(title_re="Printing", timeout=5)
                win_print = app_print.window(title_re="Printing")
                try:
                    win_print.wait_not("visible", timeout=60)
                    console.print("Janela 'Printing' fechada.", style="bold green")
                except Exception:
                    console.print("Janela 'Printing' não fechou no tempo esperado. Seguindo.", style="bold yellow")
            except findwindows.ElementNotFoundError:
                console.print("Janela 'Printing' não apareceu.", style="bold yellow")
            except Exception as e:
                console.print(f"Erro ao aguardar 'Printing': {e}", style="bold yellow")

            # 5) Validar arquivo salvo
            if os.path.exists(caminho_arquivo):
                console.print(f"Arquivo encontrado: {caminho_arquivo}", style="bold green")
                with open(caminho_arquivo, "rb") as f:
                    file_bytes = io.BytesIO(f.read())
                sucesso = True
            else:
                console.print("Arquivo não encontrado, tentando novamente...", style="bold red")
                tentativa += 1
                await worker_sleep(3)

        if not sucesso:
            console.print("Falha após 5 tentativas. Arquivo não foi gerado.", style="bold red")

        nome_com_extensao = f'saldo_estoque_{periodo_format}_{filial}.xlsx'
        console.print("Enviando arquivo XLS para o BOF...", style="bold cyan")
        try:
            await send_file(
                historico_id,
                nome_com_extensao,
                "xlsx",
                file_bytes,
                file_extension="xlsx",
            )
            console.print("Removendo arquivo da pasta downloads", style="bold yellow")
            os.remove(caminho_arquivo)
            return RpaRetornoProcessoDTO(
                sucesso=True,
                retorno="Relatório enviado com sucesso!",
                status=RpaHistoricoStatusEnum.Sucesso,
            )

        except Exception as e:
            console.print(f"Erro ao enviar o arquivo: {e}", style="bold red")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Erro ao enviar o arquivo: {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
            )

        console.print("Processo concluído com sucesso!", style="bold green")

    except Exception as ex:
        retorno = f"Erro Processo Fechamento Balancete: {str(ex)}"
        logger.error(retorno)
        console.print(retorno, style="bold red")
        return RpaRetornoProcessoDTO(
            sucesso=False,
            retorno=retorno,
            status=RpaHistoricoStatusEnum.Falha,
            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)],
        )
