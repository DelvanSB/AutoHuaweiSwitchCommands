# AutoHuaweiSwitchCommands

# Script criado para automatizar comandos em lote, sequencialmente, em
# vários switches da marca Huawei, fazendo uso de listas de IPs.

# Este script foi desenvolvido para adicionar/remover e manipular vlans em
# portas "tronco" e também inseri-las nas configurações de anel com
# protocolo ERPS.
# (se não usar esse protocolo, basta isolar trechos do codigo que tratam disso).

# Este script, em expecifico, conecta-se aos switches listados previamente
# identifica o nome do switch e o armazena numa variável. Em sequência,
# "pergunta" ( incluir 'i', excluir 'e', ou sair 's' )
# Dependendo da decisão, a rotina solicita a(s) vlan(s) ou escopos de vlans.
# Obs.:
# Há loops que verificam os caracteres e as respostas. Caso não sejam
# inseridas informações válidas, o processo volta ao estado de 'input'.

# Att, 
# Delvan's Braga.
