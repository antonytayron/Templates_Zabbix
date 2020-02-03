#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2018 Unirede Soluções Corporativas
#  _   _       _              _
# | | | |_ __ (_)_ __ ___  __| | ___
# | | | | '_ \| | '__/ _ \/ _` |/ _ \
# | |_| | | | | | | |  __/ (_| |  __/
#  \___/|_| |_|_|_|  \___|\__,_|\___|
#
#+------------------------------------------------------------------------------+
# Description: Exibe quantos hosts de um grupo possuem determinada trigger
#
# Author: Aecio Pires <aecio.pires@unirede.net>
# Date: 29-Nov-2018
#
# Exemplos de execucao:
#   python countTriggerHostGroup.py CREDENTIALS_FILE REGEX_NAME_GRUPO NOME_TRIGGER amount|hosts
#   python countTriggerHostGroup.py /home/USUARIO/credentials_zabbix_api.txt "CLB/.*/SSA/.*/SE" "Equipamento inacessivel" amount
#   python countTriggerHostGroup.py /home/USUARIO/credentials_zabbix_api.txt "CLB/.*/SSA/.*/SE" "Equipamento inacessivel" hosts
#
# OBS.: No Zabbix 3.4 os subgrupos não são considerados na API, se comportam
# como grupo de host individual.
#
# https://support.zabbix.com/browse/ZBXNEXT-4142
# https://support.zabbix.com/browse/ZBX-13609
#
# Ao acessar a API do Zabbix serão requeridos os seguintes dados:
#
# URL do Zabbix. Exemplo: http://192.168.0.1/zabbix;
# Login, previamente cadastrado no Zabbix;
# Senha de acesso;
#
# Para que esses dados não sejam solicitados interativamente ou sejam armazenados
# diretamente em cada script deste diretório, você precisa criar o arquivo
# /home/USUARIO/credentials_zabbix_api.txt, com o seguinte conteúdo e passa-lo
# como parametro.
#
# url_zabbix,login_zabbix,senha
#
# Fonte:
# https://www.zabbix.com/documentation/3.4/manual/api/reference/trigger/object
# https://www.zabbix.com/documentation/3.4/manual/api/reference_commentary#common_get_method_parameters
# https://www.zabbix.com/documentation/3.0/manual/api/reference/trigger/get
# https://www.zabbix.com/documentation/3.0/manual/api/reference/hostgroup/get
#+------------------------------------------------------------------------------+

from zabbix_api import ZabbixAPI
import sys
import json
import re

# Definindo variaveis
#CREDENTIALS_FILE = sys.argv[1]
# Passando um caminho fixo na variavel para encurtar a chamada do script na linha de comando
CREDENTIALS_FILE = '/etc/zabbix/scripts/.credentials.txt'
REGEX = sys.argv[1]
TRIGGER_NAME = sys.argv[2]
TYPE_RESULT = sys.argv[3]
groupids_list = []
hosts_list=[]
groups_list=[]

# Lendo as credenciais
with open(CREDENTIALS_FILE) as f:
    credentials = [x.strip().split(',') for x in f.readlines()]
    for url,username,password in credentials:
        # Passando as credenciais para a API do Zabbix
        zapi = ZabbixAPI(server=url, timeout=120)
        zapi.login(username,password)

# Pesquisando no Zabbix pelos nomes de todos os grupos de hosts
grupo = zapi.hostgroup.get({ "output": ["groupid", "name"],
                             "sortorder": "ASC",
                             "real_hosts": 1,
                             "with_triggers": 1,
                             "monitored_hosts": 1 })

# Indexando cada grupo para obter o ID e o nome
for index1 in grupo:
    groupName = index1[u'name']
    groupID = index1[u'groupid']
    # Pesquisando por nomes de grupo que atendam a regex
    match = re.search(REGEX, groupName)
    # Se o grupo atender a regex...
    if match:
        # Exibindo o nome do grupo que atende a regex
        #print "Host group: " + match.group()

        # Adicionando ao array, os IDs dos grupos que atendem a regex
        groupids_list.append(int(groupID))

# Exibindo a quantidade de hosts que atenderam a regex
#print len(groupids_list)

if TYPE_RESULT == "amount":
    # Obtendo a quantidade da trigger acionada que pertence aos hosts dos grupos em questao
    amount_triggers = zapi.trigger.get({"output": "extend",
                                    "groupids": groupids_list,
                                    "monitored": 1,
                                    "active": 1,
                                    "filter": { "description": TRIGGER_NAME,
                                                "status": 0, #trigger ativa
                                                "value": 1 #trigger com o estado PROBLEM
                                              },
                                    #"selectHosts": "extend",
                                    "countOutput": "true",
                                    "expandDescription": 1})

    # Exibindo o total de trigger acionada para os hosts dos grupos que atendem a regex
    print amount_triggers

if TYPE_RESULT == "hosts":
    # Obtendo o array de hosts que possui a trigger acionada e pertencem aos grupos que atendem a regex
    hosts_object = zapi.trigger.get({"output": "extend",
                                     "groupids": groupids_list,
                                     "monitored": 1,
                                     #"expandData": "hosts",
                                     "active": 1,
                                     "filter": { "description": TRIGGER_NAME,
                                                 "status": 0, #trigger ativa
                                                 "value": 1 #trigger com o estado PROBLEM
                                                },
                                     "selectHosts": "extend",
                                     "expandDescription": 1})

    # Indexando cada objeto host para obter o nome
    for index1 in hosts_object:
        hosts_properties = index1[u'hosts']
        for index2 in hosts_properties:
            host_name = index2[u'host']
            hosts_list.append(str(host_name))

    print hosts_list

# Logout da API do Zabbix
exit = zapi.user.logout
