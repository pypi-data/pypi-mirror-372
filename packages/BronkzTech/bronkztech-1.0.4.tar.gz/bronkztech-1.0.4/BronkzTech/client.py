import requests

class BronkzTech:
    def __init__(self, token: str, url: str = "https://bronkztech-api.squareweb.app/gerar_texto"):
        if not token or not isinstance(token, str):
            raise ValueError("É necessário fornecer um token válido.")
        self.token = token
        self.url = url

    def gerar_texto(self, prompt: str):
        if not prompt or not isinstance(prompt, str):
            raise ValueError("O prompt deve ser uma string não vazia.")

        headers = {"x-token": self.token}
        data = {"prompt": prompt}

        try:
            response = requests.post(self.url, json=data, headers=headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(f"Erro na requisição: {e}")
        except requests.RequestException as e:
            raise RuntimeError(f"Falha na conexão: {e}")

        resultado = response.json().get("resultado")
        if resultado is None:
            raise RuntimeError("Resposta inválida da API ou token inválido.")

        return resultado