from .client import BronkzTech

_cliente = None

def configure(token: str):
    global _cliente
    _cliente = BronkzTech(token=token)

def gerar_texto(prompt: str):
    if _cliente is None:
        raise RuntimeError("Você precisa chamar configure(token=...) antes.")
    return _cliente.gerar_texto(prompt)