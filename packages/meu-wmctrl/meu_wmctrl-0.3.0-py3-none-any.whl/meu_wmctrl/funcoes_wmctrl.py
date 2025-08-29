# meu_wmctrl/funcoes_wmctrl.py

import subprocess
import re
import time
from Xlib import display, X
from PIL import Image


def _modificar_estado(titulo, acao, estado):
    """
    Função auxiliar para modificar o estado de uma janela.
    """
    print(f"{acao.capitalize()} a janela '{titulo}'...")
    try:
        subprocess.check_call(['wmctrl', '-r', titulo, '-b', f'{acao},{estado}'])
        print("Concluído.")
    except subprocess.CalledProcessError:
        print(f"Não foi possível {acao.lower()} a janela '{titulo}'. Título não encontrado?")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def maximizar_janela(titulo):
    """
    Maximiza uma janela.
    """
    _modificar_estado(titulo, 'add', 'maximized_vert,maximized_horz')


def desmaximizar_janela(titulo):
    """
    Desmaximiza uma janela.
    """
    _modificar_estado(titulo, 'remove', 'maximized_vert,maximized_horz')


def minimizar_janela(titulo):
    """
    Minimiza (esconde) uma janela.
    """
    _modificar_estado(titulo, 'add', 'hidden')


def restaurar_janela(titulo):
    """
    Restaura uma janela minimizada (tornando-a visível).
    """
    _modificar_estado(titulo, 'remove', 'hidden')


def troca_desktop_janela(titulo, numero_desktop):
    """
    Move uma janela para um desktop virtual específico.

    Args:
        titulo (str): O título da janela.
        numero_desktop (int): O número do desktop de destino (0 para o primeiro, 1 para o segundo, etc.).
    """
    print(f"Movendo a janela '{titulo}' para o desktop {numero_desktop}...")
    try:
        subprocess.check_call(['wmctrl', '-r', titulo, '-t', str(numero_desktop)])
        print("Concluído.")
    except subprocess.CalledProcessError:
        print(f"Não foi possível mover a janela '{titulo}' para o desktop {numero_desktop}.")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def listar_janelas():
    """
    Lista todas as janelas abertas e seus IDs.

    Retorna:
        list: Uma lista de tuplas, onde cada tupla contém o ID (string)
              e o título da janela (string). Ex: [('0x04e00004', 'Terminal'), ...]
    """
    try:
        # Executa o comando e captura a saída
        resultado = subprocess.check_output(['wmctrl', '-l'], universal_newlines=True)

        janelas = []
        for linha in resultado.strip().split('\n'):
            partes = linha.split(maxsplit=3)
            if len(partes) >= 4:
                # O ID da janela está na primeira parte
                id_janela = partes[0]
                # O título da janela está na última parte
                titulo_janela = partes[3]
                janelas.append((id_janela, titulo_janela))
        return janelas
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar wmctrl: {e}")
        return []
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")
        return []


def ativar_janela(titulo):
    """
    Ativa (dá foco) a janela com o título especificado.

    Args:
        titulo (str): O título da janela a ser ativada.
    """
    print(f"Ativando janela: {titulo}")
    try:
        # Usa o 'check_call' para levantar um erro se o comando falhar
        subprocess.check_call(['wmctrl', '-a', titulo])
    except subprocess.CalledProcessError:
        print(f"Não foi possível ativar a janela '{titulo}'. Título não encontrado?")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def mover_redimensionar_janela(titulo, x, y, largura, altura):
    """
    Move e redimensiona uma janela específica.

    Args:
        titulo (str): O título da janela.
        x (int): A nova coordenada X da janela.
        y (int): A nova coordenada Y da janela.
        largura (int): A nova largura da janela.
        altura (int): A nova altura da janela.
    """
    print(f"Movendo e redimensionando a janela '{titulo}' para x={x}, y={y}, largura={largura}, altura={altura}")
    try:
        # O 'e' é para a opção '-e' do wmctrl
        subprocess.check_call(['wmctrl', '-r', titulo, '-e', f'0,{x},{y},{largura},{altura}'])
    except subprocess.CalledProcessError:
        print(f"Não foi possível mover/redimensionar a janela '{titulo}'. Título não encontrado?")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def fechar_janela(titulo):
    """
    Fecha uma janela específica.

    Args:
        titulo (str): O título da janela a ser fechada.
    """
    print(f"Fechando a janela: {titulo}")
    try:
        subprocess.check_call(['wmctrl', '-c', titulo])
    except subprocess.CalledProcessError:
        print(f"Não foi possível fechar a janela '{titulo}'. Título não encontrado?")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def mudar_desktop(indice_desktop):
    """
    Muda para o desktop virtual especificado. O índice começa em 0.

    Args:
        indice_desktop (int): O índice do desktop virtual (ex: 0 para o primeiro, 1 para o segundo).
    """
    print(f"Mudando para o desktop {indice_desktop}")
    try:
        subprocess.check_call(['wmctrl', '-s', str(indice_desktop)])
    except subprocess.CalledProcessError:
        print(f"Não foi possível mudar para o desktop '{indice_desktop}'.")
    except FileNotFoundError:
        print("wmctrl não está instalado. Por favor, instale-o.")


def obter_geometria_janela(titulo):
    """
    Obtém a posição e o tamanho (geometria) de uma janela.

    Args:
        titulo (str): O título da janela.

    Retorna:
        tuple: Uma tupla com (x, y, largura, altura) se a janela for encontrada,
               ou None se não for.
    """
    try:
        # Executa o comando e captura a saída.
        # A opção -lG retorna: ID, desktop, X, Y, W, H, hostname, título
        resultado = subprocess.check_output(['wmctrl', '-lG'], universal_newlines=True)

        for linha in resultado.strip().split('\n'):
            # Usa regex para encontrar o título da janela na linha
            if re.search(re.escape(titulo), linha):
                partes = linha.split()
                if len(partes) >= 7:
                    x = int(partes[2])
                    y = int(partes[3])
                    largura = int(partes[4])
                    altura = int(partes[5])
                    return (x, y, largura, altura)
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Erro: wmctrl não está instalado ou não foi possível obter a geometria.")
        return None


def mover_janela(titulo, x, y):
    """
    Move uma janela para uma nova posição, mantendo seu tamanho original.

    Args:
        titulo (str): O título da janela.
        x (int): A nova coordenada X da janela.
        y (int): A nova coordenada Y da janela.
    """
    geometria_original = obter_geometria_janela(titulo)
    if not geometria_original:
        print(f"Não foi possível encontrar a janela '{titulo}' para mover.")
        return

    # Extrai a largura e a altura originais
    _, _, largura, altura = geometria_original

    print(f"Movendo a janela '{titulo}' para x={x}, y={y} (mantendo o tamanho {largura}x{altura})")
    try:
        # Usa os parâmetros de movimento com a largura e altura originais
        subprocess.check_call(['wmctrl', '-r', titulo, '-e', f'0,{x},{y},{largura},{altura}'])
    except subprocess.CalledProcessError:
        print(f"Não foi possível mover a janela '{titulo}'.")


def redimensionar_janela(titulo, largura, altura):
    """
    Redimensiona uma janela, mantendo sua posição original.

    Args:
        titulo (str): O título da janela.
        largura (int): A nova largura da janela.
        altura (int): A nova altura da janela.
    """
    geometria_original = obter_geometria_janela(titulo)
    if not geometria_original:
        print(f"Não foi possível encontrar a janela '{titulo}' para redimensionar.")
        return

    # Extrai a posição original
    x, y, _, _ = geometria_original

    print(f"Redimensionando a janela '{titulo}' para {largura}x{altura} (mantendo a posição x={x}, y={y})")
    try:
        # Usa os parâmetros de redimensionamento com a posição original
        subprocess.check_call(['wmctrl', '-r', titulo, '-e', f'0,{x},{y},{largura},{altura}'])
    except subprocess.CalledProcessError:
        print(f"Não foi possível redimensionar a janela '{titulo}'.")


def get_desktop_janela(titulo):
    """
    Retorna o número do desktop onde a janela com o título especificado se encontra.

    Args:
        titulo (str): O título da janela.

    Returns:
        int: O número do desktop (ex: 0 para o primeiro), ou -1 se a janela não for encontrada.
    """
    try:
        # O comando 'wmctrl -l' retorna: ID_JANELA, DESKTOP, NOME_HOST, TITULO
        resultado = subprocess.check_output(['wmctrl', '-l'], universal_newlines=True)

        for linha in resultado.strip().split('\n'):
            partes = linha.split(maxsplit=3)
            # Verifica se o título da janela na linha corresponde ao título buscado
            if len(partes) >= 4 and titulo in partes[3]:
                return int(partes[1])  # A segunda parte é o número do desktop
        
        # Se o loop terminar e a janela não for encontrada
        print(f"Janela com o título '{titulo}' não encontrada.")
        return -1
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Erro: wmctrl não está instalado ou a execução falhou.")
        return -1
    

def get_id_janela_por_nome(name):
    # Retorna o ID da janela cujo título contém 'name'.
    output = subprocess.check_output(['wmctrl', '-l']).decode('utf-8')
    for line in output.splitlines():
        parts = line.split(None, 3)
        if len(parts) == 4:
            win_id, _, _, title = parts
            if name.lower() in title.lower():
                return int(win_id, 16)  # Converte de hexadecimal
    return None

def screenshot_janela(win_id):
    # Captura a janela com o ID fornecido.
    dsp = display.Display()
    window = dsp.create_resource_object('window', win_id)
    
    geom = window.get_geometry()
    x, y, w, h = geom.x, geom.y, geom.width, geom.height
    
    # Captura a área da janela
    raw = window.get_image(0, 0, w, h, X.ZPixmap, 0xffffffff)
    img = Image.frombytes("RGB", (w, h), raw.data, "raw", "BGRX")
    return img
