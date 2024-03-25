#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import paramiko
import itertools
import threading
import time
import sys
import getpass
import re

# Só firula ;)


def loading_animation():
    start_time = time.time()
    while (time.time() - start_time) < 1:
        for char in "-\|/":
            print('\rCarregando ' + char, end='', flush=True)
            time.sleep(0.1)

    print("\r...Ok!          ")

# --------------------------------------------


loading_animation()


# Armazenar essas informações somente se for usar o loop 'for' do final do código
# switches = ['1.3.1.1', '1.3.1.2', '1.3.1.3'] # Lista de endereços IP dos switches Huawei
# username = "SeuUser"  # Insira seu nome de usuário SSH
# password = "SuaSenha"    # Insira sua senha SSH


def connect_to_switch(ip, username, password):
    try:
        # Cria uma conexão SSH
        ssh_client = paramiko.SSHClient()

        # Aceita automaticamente chaves SSH desconhecidas (não recomendado em produção)
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conecta-se ao switch
        ssh_client.connect(ip, username=username,
                           password=password, timeout=10)

        # Mantendo uma sessao aberta para receber comandos
        # pois nos Huawei, não e permitido abrir varias sessoes ssh simuntaneamente.
        # E é isso que a funcao 'exec_command' do paramiko faz, cada linha
        # enviada com essa funcao do paramiko abre uma nova sessao ssh.
        # Ja a funcao 'client.invoke_shell()' abre uma sessão interativa de shell
        # no canal ssh aberto na conexao e o mantem aberto, como se fosse um terminal.
        sshput = ssh_client.invoke_shell()
        print(f"Conectado ao switch {ip}\n \n")
        time.sleep(1.5)
        # Buscar o nome do dispositivo para armazenar numa variável:
        sshput.send('dis sysname \n ')
        time.sleep(0.5)

        # Output para pegar o nome do switch
        output = sshput.recv(65535)
        output = output.decode("utf-8")
        # Dividir o output(do print) em linhas
        linhas = output.split('\n')

        # Remover caracteres não imprimíveis(as vezes necessario)
        # output = re.sub(r'[^\x20-\x7E]', '', output)

        # Selecionar linhas específicas para imprimir
        linhas_selecionadas = [linhas[4]]

        # Imprimir as linhas selecionadas
        for linha in linhas_selecionadas:
            # print(linha)
            print(f"O nome desse dispositivo é: {linha}\n")

        sshput.send('system-view \n ')
        time.sleep(1.5)

        # Funcao para validar vlans inseridas se estão conforme
        # o padrao de 1 a 4094 e que possa ser usado o 'to'
        # para especificar escopos de vlans, exemplo '30 to 40'.
        # Aqui, acrescenta-se vlans de 30 a 40.

        def validar_vlans_input(input_str):
            try:
                vlans_range = input_str.split(" to ")

                vlans = set()
                for item in vlans_range:
                    if "to" in item:
                        start, end = map(int, item.split(" to "))
                        vlans.update(range(start, end+1))
                    else:
                        vlans.add(int(item))

                if all(1 <= vlan <= 4094 for vlan in vlans):
                    return vlans
                else:
                    return None
            except ValueError:
                return None
        # --------------------------------------------------------------

        while True:
            decide = input(
                "Você deseja incluir ou excluir uma VLAN? ( incluir 'i', excluir 'e', ou sair 's' ): ")

            if decide.lower() == "i":
                while True:
                    # Para incluir a VLAN
                    vlans_id = input(
                        "Digite o ID da ou das VLANs que você deseja incluir, (ex: ex: 1 to 4094): ")

                    # Inicio da validacao de caracteres
                    vlans = validar_vlans_input(vlans_id)
                    if vlans is not None:
                        batchvlan = "vlan batch " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        addvlan = "port trunk allow-pass vlan " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        adderpsvlan = "stp region-configuration\ninstance 15 vlan " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        print(" \n VLAN(s) válida(s)! \n ")
                        break
                    else:
                        print(
                            "Entrada inválida. Por favor, insira IDs de VLAN válidos (1 a 4094) ou intervalos válidos.")
                    # -----------------------------------

                batchvlan = (f"vlan batch {vlans_id} \n ")
                addvlan = (f"port trunk allow-pass vlan {vlans_id} \n ")
                adderpsvlan = (
                    f"stp region-configuration \n instance 15 vlan {vlans_id} \n ")
                sshput.send(adderpsvlan)
                sshput.send('q \n ')
                sshput.send(batchvlan)
                sshput.send('interface 10GE1/0/1 \n ')
                sshput.send(addvlan)
                sshput.send('interface 10GE1/0/4 \n ')
                sshput.send(addvlan)
                time.sleep(0.5)
                # Só firula ;)
                loading_animation()
                print(f" \n VLAN(s) {vlans_id} incluída(s) com sucesso! \n ")
                sshput.send('dis curr interface 10GE1/0/1  \n ')
                sshput.send('dis curr interface 10GE1/0/4  \n ')
                sshput.send('ret  \n ')
                sshput.send('save  \n ')
                sshput.send('Y  \n ')
                time.sleep(5.5)
                break

            elif decide.lower() == "e":
                while True:
                    # Para excluir a VLAN
                    vlans_id = input(
                        "Digite o ID da ou das VLANs que você deseja excluir, (ex: 1 to 4094): ")

                    # Inicio da validacao de caracteres
                    vlans = validar_vlans_input(vlans_id)
                    if vlans is not None:
                        batchvlan = "vlan batch " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        addvlan = "port trunk allow-pass vlan " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        adderpsvlan = "stp region-configuration\ninstance 15 vlan " + \
                            " ".join(str(vlan) for vlan in vlans) + "\n"
                        print(" \n VLAN(s) válida(s)! \n ")
                        break
                    else:
                        print(
                            "Entrada inválida. Por favor, insira IDs de VLAN válidos (1 a 4094) ou intervalos válidos.")
                    # -----------------------------------

                undobatchvlan = (f"undo vlan batch {vlans_id} \n ")
                delvlan = (f" undo port trunk allow-pass vlan {vlans_id} \n ")
                undoadderpsvlan = (
                    f"stp region-configuration \n undo instance 15 vlan {vlans_id} \n ")
                sshput.send(undoadderpsvlan)
                sshput.send('q \n ')
                sshput.send(undobatchvlan)
                sshput.send('Y  \n ')
                sshput.send('interface 10GE1/0/1 \n ')
                sshput.send(delvlan)
                sshput.send('interface 10GE1/0/4 \n ')
                sshput.send(delvlan)
                time.sleep(0.5)
                # Só firula ;)
                loading_animation()
                print(f" \n VLAN(s) {vlans_id} excluída(s) com sucesso! \n ")
                time.sleep(0.5)
                sshput.send('dis curr interface 10GE1/0/1  \n ')
                sshput.send('dis curr interface 10GE1/0/4  \n ')
                time.sleep(0.5)
                sshput.send('ret  \n ')
                sshput.send('save  \n ')
                sshput.send('Y  \n ')
                time.sleep(5.5)
                break

            elif decide.lower() == "s":
                sshput.send('ret  \n ')
                time.sleep(0.5)
                # Só firula ;)
                loading_animation()
                print(" \n Saindo do programa... \n ")
                break

            else:
                print(
                    "Resposta inválida. Por favor, responda 'incluir', 'excluir', ou 'sair'.")

        time.sleep(0.5)
        sshput.send(' \n ')

        # Output GERAL
        output = sshput.recv(65535)
        output = output.decode("utf-8")
        print(output)
        # print(linha)

    except paramiko.AuthenticationException:
        print(f"Falha na autenticação ao conectar-se ao switch {ip}")
    except paramiko.SSHException as ssh_err:
        print(f"Erro SSH ao conectar-se ao switch {ip}: {ssh_err}")
    except Exception as e:
        print(f"Erro ao conectar-se ao switch {ip}: {e}")

        # Fecha a conexão SSH
        ssh_client.close()
    print(f" \n Voce foi desconectado do switch {linha}\n endereço {ip}")
    print('\n----------------------------------\n Proximo switch... (ou não ^_^)\n----------------------------------')


# Essa funcao de baixo serva para se usar quando não se quer
# deixar usuario e senha salvo no arquivo de script.
def main():
    # Lista de endereços IP dos switches Huawei
    switches = ['1.3.1.1', '1.3.1.2', '1.3.1.3'] # Lista de endereços IP dos switches Huawei

    # Solicitar nome de usuário e senha
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    # Loop para execução de comandos em todos os switches
    for switch_ip in switches:
        connect_to_switch(switch_ip, username, password)


if __name__ == "__main__":
    main()

# Itera sobre os endereços IP dos switches e se conecta a cada um
# ESSE LOOP "for" PRECISA DA LISTA DE SWITCHES, DE USUARIO E SENHA
# SALVOS NO PROPRIO SCRIPT(COISA POUCO SEGURA).
# for switch_ip in switches:
#   connect_to_switch(switch_ip, username, password)
