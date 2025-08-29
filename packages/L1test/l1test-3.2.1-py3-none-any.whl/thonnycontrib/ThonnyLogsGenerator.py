'''
Permet de générer pour le plugin de log une synthèse des tests exécutés.
Corentin.
'''

from typing import List
from thonny import get_workbench
from .backend.ast_parser import L1DocTest

#Attention si le nom change ici, il faut aussi le changer dans Thonny-LoggingPlugin
NOM_EVENT_TEST = "l1Tests"
NOM_EVENT_DOC = "l1Tests.DocGenerator"
wb = get_workbench() 

# Modifié par Mathieu Bachelet, PJI 2022-2023, mais sur la V2 de L1test
# Modifié par Mirabelle pour adaptation à la V3 de L1test
def log_in_thonny(test_results: List[L1DocTest], filename:str, selected):
    tests_data = []
    for l1doctest in test_results:
        for example in l1doctest.get_examples():
            # test:Example
            verdict = example.get_verdict() # type ExampleVerdict
            res = vars(verdict).copy() # pour récupérer les attributs filename, lineno, tested_line, expected_results, details
            res['details'] = str(res['details']) # sinon on peut récupérer un entier
            res['verdict'] = type(verdict).__name__ # pour connaître le verdict, qui n'est pas dans une champ quelconque mais ds le type lui-même
            res['name'] = l1doctest.get_name() # nom fonction ou classe
            res['status'] = verdict.isSuccess() # True si test au vert
            tests_data.append(res)
    wb.event_generate(NOM_EVENT_TEST, None, selected=selected, tests=tests_data, filename=filename)


def log_doc_in_thonny(docstring_data:tuple):#node):
    if wb:
        selected_lineno, filename, source = docstring_data
        wb.event_generate(NOM_EVENT_DOC,None, selected_lineno=selected_lineno, filename=filename, signature=source) # TODO : non


#La fonction anonyme car il faut une fonction pour bind, avec un argument parce qu'elle reçoit l'événement. 
if wb:   
    wb.bind(NOM_EVENT_TEST, lambda x : 0, True)
    wb.bind(NOM_EVENT_DOC, lambda x : 0, True)
