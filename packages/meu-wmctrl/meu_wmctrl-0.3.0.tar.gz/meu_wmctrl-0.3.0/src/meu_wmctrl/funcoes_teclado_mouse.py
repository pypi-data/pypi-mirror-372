import time
from pynput.keyboard import Controller

def digitar_texto(texto: str, delay_segundos: int = 1):
    """
    Digita uma string de texto na janela atualmente em foco.

    Args:
        texto (str): O texto a ser digitado.
        delay_segundos (int): Um tempo de espera em segundos antes de começar a digitar,
                              para dar tempo de focar na janela correta. Padrão é 1.
    """
    try:
        # Aguarda um pouco para garantir que a janela correta esteja em foco
        time.sleep(delay_segundos)

        # Inicializa o controlador do teclado
        keyboard = Controller()

        # Digita o texto
        keyboard.type(texto)

        print(f"Texto '{texto}' digitado com sucesso.")

    except Exception as e:
        print(f"Ocorreu um erro ao tentar digitar o texto: {e}")