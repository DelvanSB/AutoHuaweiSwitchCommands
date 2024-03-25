# AutoHuaweiSwitchCommands

Script criado para automatizar comandos em lote, sequencialmente, em
vários switches da marca Huawei, fazendo uso de listas de IPs.

Este script foi desenvolvido para adicionar/remover e manipular vlans em
portas "tronco" e também inseri-las nas configurações de anel com
protocolo ERPS.
(se não usar esse protocolo, basta isolar trechos do codigo que tratam disso).

Este script, em expecifico, conecta-se aos switches listados previamente
identifica o nome do switch e o armazena numa variável. Em sequência,
"pergunta" ( incluir 'i', excluir 'e', ou sair 's' )
Dependendo da decisão, a rotina solicita a(s) vlan(s) ou escopos de vlans.
 
Obs.:
Há loops que verificam os caracteres e as respostas. Caso não sejam
inseridas informações válidas, o processo volta ao estado de 'input'.

----------------------------------------------------------------------------

Script created to automate batch commands, sequentially, on various Huawei switches, using IP lists.

This script was developed to add/remove and manipulate vlans on "trunk" ports and also insert them into ring configurations using the ERPS protocol. (If you don't use this protocol, just isolate parts of the code that deal with it).

This script, in particular, connects to the switches listed previously, identifies the switch name and stores it in a variable. Then it "asks" (include 'i', exclude 'e', or exit 's'). Depending on the decision, the routine requests the vlan(s) or vlan scopes.

Note: There are loops that check the characters and the answers. If no valid information is entered, the process returns to the 'input' state.



# Att, 
# Delvan's Braga.
