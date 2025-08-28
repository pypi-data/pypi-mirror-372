import platform
import subprocess
import logging
import os
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List, Optional, Tuple, Union

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    InvalidSelectorException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


if platform.system() == "Windows":
    import winreg


class CustomChromeDriverManager:
    """
    Gerencia o download e a instalação do ChromeDriver de forma automatizada,
    buscando a versão compatível com o Google Chrome instalado no sistema.
    Funciona em Windows, Linux e macOS.

    Exemplos de Uso:
    --------------

    ### Instalação Padrão
    ```python
    try:
        # Salva o driver na raiz do projeto e verifica o SSL
        manager = CustomChromeDriverManager()
        driver_path = manager.install()
        print(f"Driver instalado com sucesso em: {driver_path}")
    except (ValueError, RuntimeError) as e:
        print(f"Erro: {e}")
    ```
    """

    CHROME_DRIVER_JSON_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

    def __init__(
        self, path: Optional[Union[str, Path]] = None, verify_ssl: bool = True
    ):
        """
        Inicializa o gerenciador de driver do Chrome.

        Args:
            path (str or Path, optional): Diretório para salvar o chromedriver.
                                        Se None, salva na raiz do projeto.
            verify_ssl (bool): Se True, verifica o certificado SSL durante o download. Padrão é True.
        """
        self.verify_ssl = verify_ssl
        self.system = platform.system()
        self.root_path = Path(path) if path else Path(__file__).parent.parent.resolve()

        if self.system == "Windows":
            self.driver_filename = "chromedriver.exe"
        elif self.system in ["Linux", "Darwin"]:
            self.driver_filename = "/chromedriver"
        else:
            raise RuntimeError(f"Sistema operacional '{self.system}' não suportado.")

        self.driver_path = self.root_path / self.driver_filename

    def install(self) -> str:
        """
        Orquestra o processo de verificação e instalação do ChromeDriver.
        Retorna o caminho (string) para o executável do driver.
        """
        chrome_version = self._get_installed_chrome_version()
        if not chrome_version:
            raise ValueError(
                "Não foi possível encontrar a versão do Google Chrome instalada."
            )

        print(f"Google Chrome versão {chrome_version} detectado.")
        download_url = self._get_driver_download_url(chrome_version)
        if not download_url:
            raise RuntimeError(
                f"Não foi possível encontrar uma URL de download do ChromeDriver para a versão {chrome_version}"
            )

        driver_executable_path = self._download_and_place_driver(download_url)
        if not driver_executable_path:
            raise RuntimeError(
                "Falha no processo de download e extração do ChromeDriver."
            )

        return str(driver_executable_path)

    def _get_installed_chrome_version(self) -> Optional[str]:
        """
        Verifica a versão do Google Chrome instalada no sistema.
        """
        if self.system == "Windows":
            return self._get_chrome_version_windows()
        elif self.system == "Linux":
            return self._get_chrome_version_linux()
        elif self.system == "Darwin":  # macOS
            return self._get_chrome_version_mac()
        return None

    def _get_chrome_version_windows(self) -> Optional[str]:
        """
        Verifica a versão do Google Chrome instalada no Windows lendo o registro.
        """
        for root_key in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                key = winreg.OpenKey(root_key, r"Software\Google\Chrome\BLBeacon")
                version, _ = winreg.QueryValueEx(key, "version")
                winreg.CloseKey(key)
                if version:
                    return version
            except (FileNotFoundError, NameError):
                continue
        return None

    def _get_chrome_version_linux(self) -> Optional[str]:
        """
        Verifica a versão do Google Chrome instalada no Linux.
        """
        for executable in [
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
        ]:
            try:
                result = subprocess.run(
                    [executable, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                version = result.stdout.strip().split()[-1]
                return version
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        return None

    def _get_chrome_version_mac(self) -> Optional[str]:
        """
        Verifica a versão do Google Chrome instalada no macOS.
        """
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if Path(chrome_path).exists():
            try:
                result = subprocess.run(
                    [chrome_path, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                version = result.stdout.strip().split()[-1]
                return version
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        return None

    def _get_driver_download_url(self, chrome_version: str) -> Optional[str]:
        """
        Busca a URL de download do ChromeDriver correspondente à versão do Chrome e plataforma.
        """
        major_version = chrome_version.split(".")[0]

        if self.system == "Linux":
            platform_name = "linux64"
        elif self.system == "Darwin":
            platform_name = "mac-arm64" if platform.machine() == "arm64" else "mac-x64"
        elif self.system == "Windows":
            platform_name = "win64"
        else:
            return None

        try:
            response = requests.get(self.CHROME_DRIVER_JSON_URL, verify=self.verify_ssl)
            response.raise_for_status()
            data = response.json()

            for channel_data in data["channels"].values():
                if channel_data["version"].startswith(major_version):
                    for download in channel_data.get("downloads", {}).get(
                        "chromedriver", []
                    ):
                        if download["platform"] == platform_name:
                            return download["url"]
            return None
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Erro ao acessar a API de drivers do Chrome: {e}"
            ) from e

    def _download_and_place_driver(self, url: str) -> Optional[Path]:
        """
        Baixa, extrai e posiciona o ChromeDriver no caminho de destino.
        """
        try:
            print(f"Baixando o driver de: {url}")
            response = requests.get(url, stream=True, verify=self.verify_ssl)
            response.raise_for_status()

            with BytesIO(response.content) as buffer:
                with zipfile.ZipFile(buffer) as zf:
                    driver_entry_name = next(
                        (
                            name
                            for name in zf.namelist()
                            if name.endswith(self.driver_filename)
                        ),
                        None,
                    )

                    if driver_entry_name:
                        extracted_content = zf.read(driver_entry_name)
                        if self.system == "Linux":
                            self.driver_path = (
                                self.root_path / self.driver_filename.replace("/", "")
                            )
                        self.driver_path.parent.mkdir(parents=True, exist_ok=True)
                        self.driver_path.write_bytes(extracted_content)

                        if self.system in ["Linux", "Darwin"]:
                            self.driver_path.chmod(0o755)

                        return self.driver_path
            return None
        except (
            requests.exceptions.RequestException,
            zipfile.BadZipFile,
            OSError,
            StopIteration,
        ) as e:
            raise RuntimeError(
                f"Ocorreu um erro durante o download ou extração: {e}"
            ) from e


class WebDriverManipulator:
    """
    Uma classe de manipulação de WebDriver que gerencia automaticamente a instância do driver.

    ### SEM CONTEXTO
    ```python
    # 1. Crie a instância normalmente
    import os
    from pathlib import Path
    from settings_os import WebDriverManipulator

    base = Path(os.getcwd())
    basedata = Path(os.getcwd()) / 'data'

    # driver_path, dinâmico.
    # logger opcional
    web = WebDriverManipulator(driver_path=basedata, logger=logger)

    try:
        # 2. Use o objeto 'web' como quiser e passe-o para onde precisar
        web.dr_get("https://www.google.com")

        # Exemplo: passando 'web' para outra função
        # minha_outra_funcao(web)

        # ... resto da sua lógica ...

    finally:
        # 3. Lembre-se de chamar .quit() no final para fechar o navegador
        # O bloco 'finally' garante que isso aconteça mesmo se ocorrer um erro no 'try'
        print("Encerrando o browser...")
        web.quit()
    ```

    ### COM CONTEXTO
    ```python
    # Exemplo de uso com gerenciamento automático
    with WebDriverManipulator(logger=logger) as web:
        web.dr_get("https://www.google.com")
        search_box = web.sl_find_element(selector_value="q", selector_type="name")
        if search_box:
            web.sl_send(search_box, "Nosso novo driver manager é demais!", Keys.ENTER, clear_first=True)
    ```
    """

    def __init__(
        self,
        driver_path: Optional[str] = None,
        options: Optional[ChromeOptions] = None,
        logger: logging.Logger = None,
        default_timeout: int = 60,
        verify_ssl: bool = True,
    ):
        self._logger = logger or logging.getLogger(__name__)
        self.driverpath = driver_path
        self.verify_ssl = verify_ssl
        self.options = options
        self.default_timeout = default_timeout
        self.action_chains = ActionChains(self.driver)
        self._logger.info("WebDriverManipulator inicializado.")

    def _config_driver(self):
        self.manager = CustomChromeDriverManager(
            path=self.driverpath, verify_ssl=self.verify_ssl
        )
        self.driver: WebDriver = self._initialize_driver(
            self.manager.install(), self.options
        )

    def _initialize_driver(
        self,
        driver_path: Optional[str | CustomChromeDriverManager],
        options: Optional[ChromeOptions],
    ) -> WebDriver:
        self._logger.debug("Inicializando driver para o navegador.")

        try:
            if not driver_path:
                raise "Nenhum 'driver_path' fornecido. Usando o gerenciador de driver customizado."

            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)

            self._logger.info("Driver inicializado com sucesso.")
            return driver
        except Exception as e:
            self._logger.error(f"Falha ao inicializar o driver: {e}")
            raise

    def quit(self):
        """Encerra a sessão do WebDriver."""
        if self.driver:
            self._logger.info("Encerrando a sessão do WebDriver.")
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _get_by_strategy(self, selector_type) -> By:
        """
        Mapeia strings de tipo de seletor para constantes By do Selenium.

        Args:
            selector_type (str): O tipo de seletor (ex: 'id', 'name', 'xpath', 'css_selector').

        Returns:
            By: A estratégia de localização By correspondente.

        Raises:
            ValueError: Se o tipo de seletor não for suportado.
        """
        strategy_map = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "xpath": By.XPATH,
            "tag_name": By.TAG_NAME,
            "css_selector": By.CSS_SELECTOR,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }
        normalized_type = selector_type.lower()
        if normalized_type not in strategy_map:
            self._logger.error(f"Tipo de seletor '{selector_type}' não suportado.")
            raise ValueError(
                f"Seletor '{selector_type}' não suportado. Escolha entre {list(strategy_map.keys())}."
            )
        return strategy_map[normalized_type]

    def _switch_to_frame(self, frame_element: Optional[WebElement]):
        """Alterna o driver para o frame especificado ou para o conteúdo padrão."""
        try:
            if frame_element is None:
                self.driver.switch_to.default_content()
                self._logger.debug("Alternado para o conteúdo padrão.")
            else:
                self.driver.switch_to.frame(frame_element)
                self._logger.debug(
                    f"Alternado para o frame: {frame_element.tag_name} [id: {frame_element.get_attribute('id')}]"
                )
        except Exception as e:
            self._logger.error(f"Falha ao alternar para o frame: {e}")
            raise

    def sl_find_element(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        raise_exception: bool = True,
    ) -> Optional[WebElement]:
        """
        Encontra um único elemento na página visível (fora de frames).

        Args:
            selector_value (str): O valor do seletor (ex: ID, XPath).
            selector_type (str): O tipo de seletor (ex: 'id', 'xpath').
            timeout (Optional[int]): Tempo limite para a espera do elemento. Se None, usa o default_timeout.
            raise_exception (bool): Se deve levantar uma exceção (NoSuchElementException/TimeoutException)
                                    se o elemento não for encontrado.

        Returns:
            Optional[WebElement]: O WebElement encontrado ou None se não encontrado e raise_exception=False.

        Raises:
            NoSuchElementException: Se o elemento não for encontrado e raise_exception=True.
            TimeoutException: Se o elemento não for encontrado dentro do timeout e raise_exception=True.
        """
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)

        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(
                EC.presence_of_element_located((by_strategy, selector_value))
            )
            self._logger.debug(
                f"Elemento '{selector_value}' encontrado com sucesso por {selector_type}."
            )
            return element
        except TimeoutException as e:
            if raise_exception:
                self._logger.error(
                    f"Timeout: Elemento '{selector_value}' não encontrado por {selector_type} em {current_timeout}s. Detalhes: {e}"
                )
                raise
            self._logger.warning(
                f"Elemento '{selector_value}' não encontrado em {current_timeout}s (silenciado)."
            )
            return None
        except NoSuchElementException as e:
            if raise_exception:
                self._logger.error(
                    f"NoSuchElement: Elemento '{selector_value}' não encontrado por {selector_type}. Detalhes: {e}"
                )
                raise
            self._logger.warning(
                f"Elemento '{selector_value}' não encontrado (silenciado)."
            )
            return None
        except InvalidSelectorException as e:
            self._logger.error(
                f"Seletor inválido: '{selector_value}' ({selector_type}). Detalhes: {e}"
            )
            if raise_exception:
                raise
            return None
        except Exception as e:
            self._logger.error(
                f"Erro inesperado ao buscar elemento '{selector_value}' por {selector_type}. Detalhes: {e}"
            )
            if raise_exception:
                raise
            return None

    def sl_find_elements(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        min_elements: int = 0,
    ) -> List[WebElement]:
        """
        Encontra múltiplos elementos na página visível (fora de frames).

        Args:
            selector_value (str): O valor do seletor.
            selector_type (str): O tipo de seletor.
            timeout (Optional[int]): Tempo limite para a espera. Se None, usa o default_timeout.
            min_elements (int): Número mínimo de elementos esperados.

        Returns:
            List[WebElement]: Uma lista de WebElements encontrados.

        Raises:
            TimeoutException: Se o número mínimo de elementos não for encontrado dentro do timeout.
        """
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)

        try:
            wait = WebDriverWait(self.driver, current_timeout)
            if min_elements > 0:
                elements = wait.until(
                    EC.number_of_elements_more_than(
                        (by_strategy, selector_value), min_elements - 1
                    )
                )
            else:
                elements = wait.until(
                    EC.presence_of_all_elements_located((by_strategy, selector_value))
                )

            if not elements:
                self._logger.warning(
                    f"Nenhum elemento '{selector_value}' encontrado por {selector_type}."
                )
            else:
                self._logger.debug(
                    f"Encontrados {len(elements)} elementos para '{selector_value}' por {selector_type}."
                )
            return elements
        except TimeoutException as e:
            self._logger.error(
                f"Timeout: Não foi possível encontrar {min_elements} ou mais elementos para '{selector_value}' por {selector_type} em {current_timeout}s. Detalhes: {e}"
            )
            raise
        except InvalidSelectorException as e:
            self._logger.error(
                f"Seletor inválido ao buscar múltiplos elementos: '{selector_value}' ({selector_type}). Detalhes: {e}"
            )
            raise
        except Exception as e:
            self._logger.error(
                f"Erro inesperado ao buscar múltiplos elementos '{selector_value}' por {selector_type}. Detalhes: {e}"
            )
            raise

    def sl_find_element_frames(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
        raise_exception: bool = True,
    ) -> Optional[WebElement]:
        """
        Busca um único elemento recursivamente em todos os frames da página.

        Args:
            selector_value (str): O valor do seletor do elemento.
            selector_type (str): O tipo de seletor.
            timeout (Optional[int]): Tempo limite total para a busca.
            raise_exception (bool): Se deve levantar uma exceção se o elemento não for encontrado.

        Returns:
            Optional[WebElement]: O WebElement encontrado ou None.

        Raises:
            NoSuchElementException: Se o elemento não for encontrado e raise_exception=True.
            TimeoutException: Se o elemento não for encontrado dentro do timeout e raise_exception=True.
        """
        current_timeout = timeout if timeout is not None else self.default_timeout
        start_time = self.driver.execute_script(
            "return performance.now()"
        )  # Tempo de início da busca total

        # Pilha para DFS (Depth-First Search) para explorar frames.
        # Armazena tuplas: (frame_element, current_depth)
        frames_stack: List[Tuple[Optional[WebElement], int]] = [(None, 0)]

        found_element: Optional[WebElement] = None

        # Usado para evitar loops infinitos em caso de frames cíclicos, embora raro.
        processed_frame_ids = set()

        self._logger.info(
            f"Iniciando busca recursiva por '{selector_value}' em frames. Timeout: {current_timeout}s."
        )

        while frames_stack:
            if (
                self.driver.execute_script("return performance.now()") - start_time
            ) / 1000 > current_timeout:
                self._logger.warning("Tempo limite de busca em frames atingido.")
                break

            current_frame_element, depth = (
                frames_stack.pop()
            )  # Pop do último elemento (DFS)

            # Evita processar o mesmo frame várias vezes
            if current_frame_element:
                frame_id = id(current_frame_element)
                if frame_id in processed_frame_ids:
                    continue
                processed_frame_ids.add(frame_id)

            try:
                self._switch_to_frame(current_frame_element)

                # Tenta encontrar o elemento no frame atual (timeout curto para não bloquear)
                element = self.sl_find_element(
                    selector_value,
                    selector_type=selector_type,
                    timeout=1,  # Timeout curto para busca individual em cada frame
                    raise_exception=False,
                )
                if element:
                    found_element = element
                    self._logger.info(
                        f"Elemento '{selector_value}' encontrado no frame em profundidade {depth}."
                    )
                    break  # Elemento encontrado, sai do loop

                # Se não encontrou, busca frames aninhados no contexto atual
                nested_frames = self.sl_find_elements(
                    "iframe", selector_type="tag_name", timeout=0.5, min_elements=0
                ) + self.sl_find_elements(
                    "frame", selector_type="tag_name", timeout=0.5, min_elements=0
                )

                # Adiciona frames aninhados à pilha
                for nested_frame in nested_frames:
                    if id(nested_frame) not in processed_frame_ids:
                        frames_stack.append((nested_frame, depth + 1))
                        self._logger.debug(
                            f"Adicionado frame aninhado à pilha (profundidade {depth + 1})."
                        )

            except Exception as e:
                self._logger.debug(
                    f"Erro ao explorar frame em profundidade {depth}. Detalhes: {e}"
                )
            finally:
                # Sempre volta para o frame pai depois de explorar um ramo
                if current_frame_element is not None:
                    self.driver.switch_to.parent_frame()
                    self._logger.debug(
                        f"Voltado para o frame pai de profundidade {depth}."
                    )

        # Garante que o driver esteja no conteúdo padrão ao final da busca
        self.driver.switch_to.default_content()

        if found_element is None and raise_exception:
            self._logger.error(
                f"Elemento '{selector_value}' não encontrado em nenhum frame após busca recursiva."
            )
            raise NoSuchElementException(
                f"Elemento '{selector_value}' não encontrado em nenhum frame."
            )

        return found_element

    def sl_click_element(self, element: WebElement, safe_click: bool = True):
        """
        Clica em um WebElement.

        Args:
            element (WebElement): O elemento para clicar.
            safe_click (bool): Se deve tentar clicar mesmo se o elemento estiver fora da visibilidade, usando ActionChains como fallback.
        """
        try:
            element.click()
            self._logger.debug("Elemento clicado com sucesso.")
        except MoveTargetOutOfBoundsException as e:
            if safe_click:
                self._logger.warning(
                    f"Elemento fora da visibilidade, tentando clique com ActionChains. Detalhes: {e}"
                )
                self.action_chains.move_to_element(element).click().perform()
            else:
                self._logger.error(
                    f"Elemento fora da visibilidade e safe_click=False. Detalhes: {e}"
                )
                raise
        except Exception as e:
            self._logger.error(f"Erro ao clicar no elemento: {e}")
            raise

    def sl_send(self, element: WebElement, *args, clear_first: bool = False):
        """
        Digita um texto em um campo de entrada.

        Args:
            element (WebElement): O campo de entrada.
            *args: Uma sequência de textos ou teclas a serem digitados.
            clear_first (bool): Se deve limpar o campo antes de digitar.
        """
        try:
            if clear_first:
                element.clear()
                self._logger.debug("Campo limpo antes de digitar.")
            element.send_keys(*args)
            self._logger.debug(f"Textos {args} digitados no elemento.")
        except Exception as e:
            self._logger.error(f"Erro ao digitar texto no elemento: {e}")
            raise

    def sl_get_element_text(self, element: WebElement) -> str:
        """
        Retorna o texto visível de um elemento.

        Args:
            element (WebElement): O elemento.

        Returns:
            str: O texto do elemento.
        """
        try:
            text = element.text
            self._logger.debug(f"Texto do elemento obtido: '{text}'.")
            return text
        except Exception as e:
            self._logger.error(f"Erro ao obter texto do elemento: {e}")
            raise

    def sl_get_element_attribute(self, element: WebElement, attribute_name: str) -> str:
        """
        Retorna o valor de um atributo de um elemento.

        Args:
            element (WebElement): O elemento.
            attribute_name (str): O nome do atributo.

        Returns:
            str: O valor do atributo.
        """
        try:
            attribute_value = element.get_attribute(attribute_name)
            self._logger.debug(
                f"Atributo '{attribute_name}' do elemento obtido: '{attribute_value}'."
            )
            return attribute_value
        except Exception as e:
            self._logger.error(
                f"Erro ao obter atributo '{attribute_name}' do elemento: {e}"
            )
            raise

    def sl_wait_element_visibility(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
    ) -> WebElement:
        """
        Espera até que um elemento esteja visível na página.

        Args:
            selector_value (str): O valor do seletor.
            selector_type (str): O tipo de seletor.
            timeout (Optional[int]): Tempo limite para a espera.

        Returns:
            WebElement: O elemento visível.

        Raises:
            TimeoutException: Se o elemento não estiver visível dentro do tempo limite.
        """
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)
        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(
                EC.visibility_of_element_located((by_strategy, selector_value))
            )
            self._logger.debug(f"Elemento '{selector_value}' visível após espera.")
            return element
        except TimeoutException as e:
            self._logger.error(
                f"Timeout: Elemento '{selector_value}' não ficou visível em {current_timeout}s. Detalhes: {e}"
            )
            raise
        except Exception as e:
            self._logger.error(
                f"Erro ao esperar pela visibilidade do elemento '{selector_value}': {e}"
            )
            raise

    def sl_wait_element_clickable(
        self,
        selector_value: str,
        selector_type: str = "xpath",
        timeout: Optional[int] = None,
    ) -> WebElement:
        """
        Espera até que um elemento esteja clicável na página.

        Args:
            selector_value (str): O valor do seletor.
            selector_type (str): O tipo de seletor.
            timeout (Optional[int]): Tempo limite para a espera.

        Returns:
            WebElement: O elemento clicável.

        Raises:
            TimeoutException: Se o elemento não estiver clicável dentro do tempo limite.
        """
        current_timeout = timeout if timeout is not None else self.default_timeout
        by_strategy = self._get_by_strategy(selector_type)
        try:
            wait = WebDriverWait(self.driver, current_timeout)
            element = wait.until(
                EC.element_to_be_clickable((by_strategy, selector_value))
            )
            self._logger.debug(f"Elemento '{selector_value}' clicável após espera.")
            return element
        except TimeoutException as e:
            self._logger.error(
                f"Timeout: Elemento '{selector_value}' não ficou clicável em {current_timeout}s. Detalhes: {e}"
            )
            raise
        except Exception as e:
            self._logger.error(
                f"Erro ao esperar pelo clique do elemento '{selector_value}': {e}"
            )
            raise

    def dr_execute_script(self, script: str, *args):
        """
        Executa um script JavaScript no contexto do driver.

        Args:
            script (str): O script JavaScript a ser executado.
            *args: Argumentos a serem passados para o script.
        """
        try:
            self._logger.debug(f"Executando script JS: {script[:50]}...")
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self._logger.error(f"Erro ao executar script JavaScript: {e}")
            raise

    def dr_switch_default_content(self):
        """
        Alterna o foco do driver de volta para o conteúdo principal da página.
        """
        try:
            self.driver.switch_to.default_content()
            self._logger.info("Foco do driver restaurado para o conteúdo padrão.")
        except Exception as e:
            self._logger.error(f"Erro ao alternar para o conteúdo padrão: {e}")
            raise

    def dr_get(self, url: str):
        """Navega o driver para uma URL específica."""
        try:
            self.driver.get(url)
            self._logger.info(f"Navegou para a URL: {url}")
        except Exception as e:
            self._logger.error(f"Erro ao navegar para a URL '{url}': {e}")
            raise

    def dr_current_url(self) -> str:
        """Retorna a URL atual do navegador."""
        try:
            url = self.driver.current_url
            self._logger.debug(f"URL atual: {url}")
            return url
        except Exception as e:
            self._logger.error(f"Erro ao obter a URL atual: {e}")
            raise

    def dr_refresh_page(self):
        """Atualiza a página atual."""
        try:
            self.driver.refresh()
            self._logger.info("Página atualizada.")
        except Exception as e:
            self._logger.error(f"Erro ao atualizar a página: {e}")
            raise

    def dr_close_current_tab(self):
        """Fecha a aba atualmente focada."""
        try:
            self.driver.close()
            self._logger.info("Aba atual fechada.")
        except Exception as e:
            self._logger.error(f"Erro ao fechar a aba atual: {e}")
            raise

    def dr_switch_tab(self, tab_index: int):
        """
        Muda para a aba do navegador especificada pelo índice.

        Args:
            tab_index (int): O índice da aba para a qual mudar (0 para a primeira).
        """
        try:
            window_handles = self.driver.window_handles
            if 0 <= tab_index < len(window_handles):
                self.driver.switch_to.window(window_handles[tab_index])
                self._logger.info(f"Mudou para a aba com índice: {tab_index}")
            else:
                self._logger.error(
                    f"Índice de aba inválido: {tab_index}. Total de abas: {len(window_handles)}."
                )
                raise IndexError(f"Aba com índice {tab_index} não existe.")
        except Exception as e:
            self._logger.error(f"Erro ao mudar para a aba {tab_index}: {e}")
            raise

    def dr_take_screenshot(self, file_path: str = os.getcwd()):
        """
        Tira uma captura de tela da página atual.

        Args:
            file_path (str): O caminho completo do arquivo para salvar a captura de tela (ex: 'screenshot.png').
        """
        try:
            self.driver.save_screenshot(file_path)
            self._logger.info(f"Captura de tela salva em: {file_path}")
        except Exception as e:
            self._logger.error(f"Erro ao tirar captura de tela em '{file_path}': {e}")
            raise
