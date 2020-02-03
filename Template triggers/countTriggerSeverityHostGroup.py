#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright (C) 2019 Unirede Soluções Corporativas
#  _   _       _              _
# | | | |_ __ (_)_ __ ___  __| | ___
# | | | | '_ \| | '__/ _ \/ _` |/ _ \
# | |_| | | | | | | |  __/ (_| |  __/
#  \___/|_| |_|_|_|  \___|\__,_|\___|
#
#+------------------------------------------------------------------------------+
# Description: Exibe a quantidade de trigger por severidade para um grupo de hosts que possui determinada REGEX no nome
#
# Author: Aecio Pires <aecio.pires@unirede.net>
# Date: 12-Nov-2019
#
# Exemplos de execucao:
#   python countTriggerSeverityHostGroup.py CREDENTIALS_FILE REGEX_NAME_GRUPO SEVERITY_TRIGGER amount|total
#   python countTriggerSeverityHostGroup.py /home/USUARIO/credentials_zabbix_api.txt "CLB/.*/SSA/.*/SE" 4 amount
#   python countTriggerSeverityHostGroup.py /home/USUARIO/credentials_zabbix_api.txt "CLB/.*/SSA/.*/SE" 99 total
#
# SEVERITY_TRIGGER pode ser:
#
#  0  => Not classfied
#  1  => Information
#  2  => Warning
#  3  => Average
#  4  => High
#  5  => Disaster
#  99 => total (independente da severidade)
#
#  Vide: https://www.zabbix.com/documentation/4.2/manual/api/reference/trigger/object
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
TRIGGER_SEVERITY = sys.argv[2]
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
        #print "Host group: " + groupName + " => regex:" + match.group()

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
                                    "filter": { "priority": TRIGGER_SEVERITY,
                                                "status": 0, #trigger ativa
                                                "value": 1 #trigger com o estado PROBLEM
                                              },
                                    #"selectHosts": "extend",
                                    "countOutput": "true",
                                    "expandDescription": 1})

    # Exibindo o total de trigger acionada para os hosts dos grupos que atendem a regex
    # De acordo com a Severidade
    print amount_triggers

if TYPE_RESULT == "total":
    # Obtendo a quantidade da trigger acionadas que pertence aos hosts dos grupos em questao
    amount_triggers = zapi.trigger.get({"output": "extend",
                                    "groupids": groupids_list,
                                    "monitored": 1,
                                    "active": 1,
                                    "filter": { "status": 0, #trigger ativa
                                                "value": 1 #trigger com o estado PROBLEM
                                              },
                                    #"selectHosts": "extend",
                                    "countOutput": "true",
                                    "expandDescription": 1})

    # Exibindo o total de triggers acionadas para os hosts dos grupos que atendem a regex
    # Independente da Severidade
    print amount_triggers


# Logout da API do Zabbix
exit = zapi.user.logout
