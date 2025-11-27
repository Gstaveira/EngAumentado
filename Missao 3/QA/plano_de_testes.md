
# Plano de Testes – Sistema de Monitoramento de Hemogramas

## Objetivo
Garantir que o sistema Flask funcione corretamente nas rotas:
- Home
- Upload
- Processamento do CSV
- Predição (/predict)

## Itens testados
- Upload seguro
- Estrutura do CSV
- Interação com o banco SQLite
- Respostas JSON consistentes
- Templates renderizando sem erro

## Critérios de sucesso
- 0 falhas críticas
- Cobertura ≥ 70%
- Todas as rotas retornando códigos HTTP esperados
