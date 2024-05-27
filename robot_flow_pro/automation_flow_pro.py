import mysql.connector
import logging
import pandas as pd
from selenium import webdriver as opcoes_selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
import os
from utils.helpers import montar_href_absoluto
from db_operations import chamar_procedure


# Configuração de log
log_file_path = os.path.join(os.path.dirname(__file__), 'logs', 'execution.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_file_path,
                    filemode='a')

def acessar_site(chrome, usuario, senha, endereco):
    try:
        logging.info('Acessando site: %s', endereco)
        chrome.get(endereco)

        logging.info('Realizando login com usuario: %s', usuario)
        WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.ID, 'username'))
        ).send_keys(usuario)
        chrome.find_element(By.ID, 'password').send_keys(senha)
        time.sleep(2)
        chrome.find_element(By.XPATH, '//*[@id="loginFormDiv"]/form/div[3]/button').click()
        time.sleep(5)
    except Exception as e:
        logging.error('Erro ao efetuar login: %s', e)
        raise

def navegar_site(chrome, endereco):
    try:
        logging.info('Inicio navegacao no site: %s', endereco)
        WebDriverWait(chrome, 30).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="appnavigator"]'))
        ).click()

        WebDriverWait(chrome, 30).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="SUPPORT_modules_dropdownMenu"]/div'))
        ).click()

        link_element_demandas = WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.LINK_TEXT, 'Demandas'))
        )
        href_demandas = link_element_demandas.get_attribute('href')
        chrome.get(href_demandas)

        logging.info('Acessando demanda ATD_2966')
        td_element_2966 = WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'td.listViewEntryValue[data-name="ticket_no"][title="ATD_2966"]'))
        )
        link_element_2966 = td_element_2966.find_element(By.TAG_NAME, 'a')
        href_relativo_2966 = link_element_2966.get_dom_attribute('href')
        href_absoluto_2966 = montar_href_absoluto(href_relativo_2966, endereco)
        chrome.get(href_absoluto_2966)
        time.sleep(5)

        acessar_aba_documentos(chrome)
        dados_tabela_2966 = extrair_dados(chrome, "2966")
        numero_downloads = download_arquivos(chrome, endereco)
        dados_tabela_2966.insert(6, 'Nova Coluna', numero_downloads)
        retornar_demandas(chrome, endereco)

        logging.info('Acessando demanda ATD_2967')
        td_element_2967 = WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'td.listViewEntryValue[data-name="ticket_no"][title="ATD_2967"]'))
        )
        link_element_2967 = td_element_2967.find_element(By.TAG_NAME, 'a')
        href_relativo_2967 = link_element_2967.get_dom_attribute('href')
        href_absoluto_2967 = montar_href_absoluto(href_relativo_2967, endereco)
        chrome.get(href_absoluto_2967)
        time.sleep(5)

        acessar_aba_documentos(chrome)
        dados_tabela_2967 = extrair_dados(chrome, "2967")
        numero_downloads = download_arquivos(chrome, endereco)
        dados_tabela_2967.insert(6, 'Nova Coluna', numero_downloads)
        retornar_demandas(chrome, endereco)

        logging.info('Acessando demanda ATD_2968')
        td_element_2968 = WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, 'td.listViewEntryValue[data-name="ticket_no"][title="ATD_2968"]'))
        )
        link_element_2968 = td_element_2968.find_element(By.TAG_NAME, 'a')
        href_relativo_2968 = link_element_2968.get_dom_attribute('href')
        href_absoluto_2968 = montar_href_absoluto(href_relativo_2968, endereco)
        chrome.get(href_absoluto_2968)
        time.sleep(5)

        acessar_aba_documentos(chrome)
        dados_tabela_2968 = extrair_dados(chrome, "2968")
        numero_downloads = download_arquivos(chrome, endereco)
        dados_tabela_2968.insert(6, 'Nova Coluna', numero_downloads)

        chrome.quit()
        return dados_tabela_2966, dados_tabela_2967, dados_tabela_2968
    except Exception as e:
        logging.error('Erro navegacao do site: %s', e)
        chrome.quit()
        raise

def download_arquivos(chrome, endereco):
    try:
        logging.info('Iniciando download de arquivos')
        links_download = chrome.find_elements(By.CSS_SELECTOR, 'a[name="downloadfile"]')
        downloads = 0

        for link in links_download:
            url_download_relativo = link.get_attribute('href')
            chrome.execute_script('window.open();')
            chrome.switch_to.window(chrome.window_handles[-1])
            url_download_absoluto = montar_href_absoluto(url_download_relativo, endereco)
            chrome.get(url_download_absoluto)
            chrome.close()
            chrome.switch_to.window(chrome.window_handles[0])
            downloads += 1

        time.sleep(3)
        logging.info('Numero de arquivos baixados: %d', downloads)
        return downloads
    except Exception as e:
        logging.error('Erro ao baixar arquivos: %s', e)
        raise

def retornar_demandas(chrome, endereco):
    try:
        link_element_demandas = chrome.find_element(By.XPATH, '//a[@title="Demandas"]')
        href_demandas_relativo = link_element_demandas.get_attribute('href')
        href_demandas_absoluto = montar_href_absoluto(href_demandas_relativo, endereco)
        chrome.get(href_demandas_absoluto)
        time.sleep(10)
    except Exception as e:
        logging.error('Erro ao retornar para a página de demandas: %s', e)
        raise

def extrair_dados(chrome, demandas):
    try:
        tabela = WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'listview-table'))
        )
        html_tabela = tabela.get_attribute('outerHTML')
        dados = pd.read_html(html_tabela)[0]
        dados.insert(0, 'Demandas', demandas)
        return dados
    except Exception as e:
        logging.error('Erro ao extrair dados da demanda %s: %s', demandas, e)
        raise

def acessar_aba_documentos(chrome):
    try:
        chrome.find_element(By.XPATH, '//*[@id="nav-tabs"]/ul/li[4]/a/span[1]/i').click()
        WebDriverWait(chrome, 30).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'listview-table'))
        )
    except Exception as e:
        logging.error('Erro ao acessar a aba de documentos: %s', e)
        raise

def montar_dt(dados2966, dados2967, dados2968):
    try:
        data_table = pd.DataFrame()
        for dados_tabela in [dados2966, dados2967, dados2968]:
            dados_selecionados = dados_tabela.iloc[:, [0, 4, 5, 6]]
            data_table = pd.concat([data_table, dados_selecionados], ignore_index=True)
        data_table.columns = range(data_table.shape[1])
        return data_table
    except Exception as e:
        logging.error('Erro ao montar DataTable: %s', e)
        raise

def conexao_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="14h1MP9982dr4.45",
        database="my_db"
    )


def main():
    try:
        logging.info('Automacao iniciada')
        os.chdir(os.path.dirname(__file__))
        config_file_path = "./config/appDev.properties"
        url = ''
        login = ''
        password = ''
        with open(config_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    key_value = line.split(':', 1)
                    if len(key_value) == 2:
                        key, value = key_value
                        if key.strip() == 'URL':
                            url = value.strip()
                        elif key.strip() == 'Login':
                            login = value.strip()
                        elif key.strip() == 'Senha':
                            password = value.strip()

        navegador = opcoes_selenium.Chrome()
        acessar_site(navegador, login, password, url)
        dados_tabela1, dados_tabela2, dados_tabela3 = navegar_site(navegador, url)
        tabela = montar_dt(dados_tabela1, dados_tabela2, dados_tabela3)
        chamar_procedure(tabela)

        logging.info('Automacao finalizada com sucesso')
    except Exception as e:
        logging.critical('Erro critico: %s', e)

main()
