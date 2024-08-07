# Sistema de Monitoramento e Sincronização de Arquivos

Projeto da Disciplina de Sistema Distribuidos 2024/1

## Funcionalidades

- **Monitoramento de Arquivos:** Detecta eventos de criação, modificação e exclusão de arquivos em um diretório.
- **Sincronização em Rede:** Propaga eventos de arquivo para outros nós na rede utilizando XML-RPC.
- **Detecção Contínua:** Monitora todos os arquivos no diretório desde o início do programa, incluindo arquivos já existentes e novos arquivos.

Porém foi feito de uma forma onde só o criador do arquivo tem "autoridade" para modificar e deletar, enquanto os outros só conseguem observar e obviamente enviar arquivos também.

## Requisitos

- Python 3.x
- Bibliotecas: `watchdog`, `xmlrpc.client`, `xmlrpc.server`
