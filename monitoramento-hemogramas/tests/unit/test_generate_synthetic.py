import os
from generate_synthetic import gerar_dados_sinteticos

def test_gera_csv():
    caminho = "teste_sintetico.csv"
    gerar_dados_sinteticos(10, caminho)
    assert os.path.exists(caminho)
    os.remove(caminho)
