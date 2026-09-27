import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://e-saudesp-telemedicina.prefeitura.sp.gov.br/e-saudesp/app/eoc"

# procura o campo pelo data-test-id OU pelo id (o que existir na página)
CAMPO_CNS = (By.CSS_SELECTOR, '[data-test-id="input-mat-input-2"], #input-mat-input-2')

TEMPO_ESPERA = 600   # até 10 minutos esperando o campo aparecer

driver = None


def navegador_aberto():
    if driver is None:
        return False
    try:
        driver.title
        return True
    except Exception:
        return False


def colar_cns(cns):
    global driver
    try:
        # 1. abre o site (só na primeira vez)
        if not navegador_aberto():
            print("Abrindo o site... faça o login.")
            driver = webdriver.Edge()
            driver.get(URL)

        # 2. espera o campo do CNS aparecer (depois do login)
        print("Esperando o campo do CNS aparecer...")
        campo = WebDriverWait(driver, TEMPO_ESPERA).until(
            EC.visibility_of_element_located(CAMPO_CNS)
        )

        # 3. cola o CNS
        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(cns)
        print("CNS colado:", cns)

    except Exception as erro:
        print("ERRO:", type(erro).__name__, "-", erro)


def iniciar(cns):
    threading.Thread(target=colar_cns, args=(cns,), daemon=True).start()