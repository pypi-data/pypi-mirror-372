import json
import requests
import os
import locale
from os import getcwd, path
from datetime import datetime
from pydantic import ValidationError

from .entities.nota_pedido import NotaPedido
from .entities.miro import Miro
from .entities.fatura import Fatura
from .entities.constants import *

from .entities.classes.form_jira    import FormJira
from .entities.classes.issue_jira   import IssueJira, AttachmentJira, TransitionJira, CommentJira
from .entities.classes.issue_fields import IssueFields
from .entities.classes.helper       import JiraFieldsHelper, JsonHelper, GuiandoHelper
from .entities.classes.n8n_domain   import N8NDomain
class wrapper_jira:

    def __init__(self, miro_is_active=False ,debug=False):
        locale.setlocale(locale.LC_ALL, ('pt_BR.UTF-8'))
        self._test_mode = debug
        self._miro_is_active  = miro_is_active
        self._instance_class()

    def _instance_class(self):
        self.FormJira         = FormJira()
        self.IssueJira        = IssueJira()
        self.AttachmentJira   = AttachmentJira()
        self.TransitionJira   = TransitionJira()
        self.CommentJira      = CommentJira()
        self.JiraFieldsHelper = JiraFieldsHelper()
        self.GuiandoHelper    = GuiandoHelper()
        self.JsonHelper       = JsonHelper()
        self.IssueFields      = IssueFields()
        self.N8NDomain        = N8NDomain()

    def get_issues_by_jql(self, jql):
        return self.IssueJira.get_issue_jql(jql)
    
    def get_jira_info_by_issue(self, issue_key):
        automation_form_id = self.FormJira.get_form_id(issue_key, FORM_TEMPLATE_AUTOMACAO)
        return {"issue_id": issue_key, "form_id": automation_form_id}

    def get_document_by_issue(self, issue_key):

        issue_sap_json = {}

        issue = self._get_issue_by_key(issue_key)
        issue_transition = issue['domain_data']['fornecedor']['transacao']

        if issue_transition == 'ME21N':
            nota_pedido_factory = self._issue_factory(issue)
            nota_pedido_model   = NotaPedido(**nota_pedido_factory).model_dump()
            issue_sap_json["nota_pedido"] = nota_pedido_model

            if self._miro_is_active:
                miro_factory = self._miro_factory(issue)
                miro_model = Miro(**miro_factory).model_dump()
                issue_sap_json["miro"] = miro_model

        elif issue_transition == 'FV60':
            fatura_factory = self._fatura_factory(issue)
            fatura_model   = Fatura(**fatura_factory).model_dump()
            issue_sap_json["fatura"] = fatura_model

        issue_sap_json["jira_info"] = issue["jira_info"]

        if self._test_mode:
            for json in issue_sap_json:
                self.JsonHelper.save_json(f'{json}_{issue_key}', issue_sap_json[json])
            
        return issue_sap_json

    def _get_issue_by_key(self, issue_key):

        issue_json = self._get_nf_jira(issue_key)

        issue_attachment = issue_json["attachment"]
        jira_info = issue_json["jira_info"]

        fornecedor_domain = self.N8NDomain.get_nf_domain(FORNECEDOR_N8N_DOMAIN, issue_attachment[CNPJ_DO_FORNECEDOR])
        centro_domain = self.N8NDomain.get_nf_domain(CENTRO_N8N_DOMAIN, issue_attachment[CNPJ_DO_CLIENTE])
        cfop_fornecedor = self.N8NDomain.get_cfop_fornecedor(issue_attachment[CNPJ_DO_FORNECEDOR], issue_attachment[CNPJ_DO_CLIENTE])

        domain = {
            "fornecedor"    : fornecedor_domain,
            "centro" : centro_domain,
            "cfop_fornecedor": cfop_fornecedor
        }

        issue = {
            "issue_data": issue_json["issue_data"],
            "json_data": issue_attachment,
            "domain_data": domain,
            "pdf_data": issue_json["pdf_data"],
            "jira_info": jira_info,
        }

        if self._test_mode:
            self.JsonHelper.save_json(f'Issue_data_{issue_key}', issue)

        return issue

    def _issue_factory(self, issue: dict):

        sintese_itens = []

        if not issue['json_data'][ALOCAÇÕES_DE_CUSTO]:

            item = {
                "centro_desc": issue["domain_data"]["centro"]["centro"],
                "centro_custo": f"{issue['domain_data']['centro']['centro_custo']}",
                "cod_imposto": "C6",
                "montante": issue["json_data"][VALOR_TOTAL_DA_FATURA],
                "percentage": CEM_PORCENTO_DO_VALOR_BRUTO
            }

            sintese_item = {
                "categoria_cc": "K",
                "quantidade": 1,
                "cod_material": issue["domain_data"]["fornecedor"]["codigo_material"],
                "item": item,
            }

            sintese_itens.append(sintese_item)

        else:

            for cost_allocation in issue['json_data'][ALOCAÇÕES_DE_CUSTO]:
                
                item = {
                    "centro_desc": cost_allocation['CustCenterDescription'].split(' - ')[0],
                    "centro_custo": cost_allocation['Code'],
                    "cod_imposto": "C6",
                    "montante": cost_allocation['CustCenterTotalAmount'],
                    "percentage": cost_allocation['Percentage']
                }

                sintese_item = {
                    "categoria_cc": "K",
                    "quantidade": 1,
                    "cod_material": issue["domain_data"]["fornecedor"][
                        "codigo_material"
                    ],
                    "item": item,
                }

                sintese_itens.append(sintese_item)

        nota_pedido = {
            "montante": issue['json_data'][VALOR_TOTAL_DA_FATURA],
            "valor_liquido": issue["json_data"][VALOR_LIQUIDO_DA_FATURA],
            "juros": issue["json_data"][JUROS_DA_FATURA],
            "tipo": "ZCOR",
            "org_compras": issue["domain_data"]["centro"]["org_compras"],
            "grp_compradores": issue['json_data']['grupo_compradores'][0],
            "empresa": "HFNT",
            "cod_fornecedor": issue["domain_data"]["fornecedor"]["codigo_sap"],
            "centro_custo_destinatario": issue["domain_data"]["centro"]["centro_custo"],
            "centro_destinatario": issue["domain_data"]["centro"]["centro"],
            "sintese_itens": sintese_itens,
            "anexo": issue['pdf_data'],
        }

        return nota_pedido

    def _miro_factory(self, issue: dict):

        texto = self._prepare_ref(issue)

        dados_basicos = {
            "data_da_fatura": datetime.strptime(
                issue['json_data'][DATA_DE_EMISSÃO], "%Y-%m-%d"
            ).strftime("%d.%m.%Y"),
            "referencia": f"{issue['json_data'][CHAVE_DE_ACESSO_DA_FATURA][25:34]}-{issue['json_data'][CHAVE_DE_ACESSO_DA_FATURA][22:25]}" if CHAVE_DE_ACESSO_DA_FATURA in issue["json_data"] and issue["json_data"].get(CHAVE_DE_ACESSO_DA_FATURA) is not None else f"{issue['json_data'].get(NÚMERO_DA_FATURA)[-MAX_LEN_NRO_NF:].rjust(MAX_LEN_NRO_NF, '0')}-{SERIE_NF}",
            "montante": issue['json_data'][VALOR_TOTAL_DA_FATURA],
            "texto": texto,
        }
        pagamento = {
            "data_basica": datetime.strptime(
                issue['json_data'][DATA_DE_VENCIMENTO], "%Y-%m-%d"
            ).strftime("%d.%m.%Y"),
            "cond_pgto": CONDICOES_PAGAMENTO_30DIAS
        }

        if issue["json_data"][VALOR_LIQUIDO_DA_FATURA]:
            dados_basicos["valor_liquido"] = issue["json_data"][VALOR_LIQUIDO_DA_FATURA]

        detalhe = {"ctg_nf": issue["domain_data"]["fornecedor"]["categoria_nf"]}
        sintese = []
        cfop = None
        if 'cfop_fornecedor' in issue["domain_data"] and 'cfop' in issue["domain_data"]['cfop_fornecedor'] and len(issue["domain_data"]['cfop_fornecedor']['cfop']) > 0:
            cfop = issue["domain_data"]['cfop_fornecedor']['cfop']
        elif 'fornecedor' in issue["domain_data"] and len(issue["domain_data"]['fornecedor']['cfop']) > 0:
            cfop = issue["domain_data"]['fornecedor']['cfop']
        if cfop is None:
            raise Exception(f"Erro ao obter o CFOP:\n")
        
        if not issue['json_data'][ALOCAÇÕES_DE_CUSTO]:
            sintese.append({ "CFOP": cfop})
        else:
            for _ in range(len(issue['json_data'][ALOCAÇÕES_DE_CUSTO])):
                sintese.append({
                    "CFOP": cfop
                })

        chave_acesso = {
            "tp_emissao": f"{issue['json_data'][CHAVE_DE_ACESSO_DA_FATURA][34]}"if CHAVE_DE_ACESSO_DA_FATURA in issue["json_data"] and issue["json_data"].get(CHAVE_DE_ACESSO_DA_FATURA) is not None else None,
            "numero_aleatorio": f"{issue['json_data'][CHAVE_DE_ACESSO_DA_FATURA][35:43]}" if CHAVE_DE_ACESSO_DA_FATURA in issue["json_data"] and issue["json_data"].get(CHAVE_DE_ACESSO_DA_FATURA) is not None else None,
            "dig_verif": f"{issue['json_data'][CHAVE_DE_ACESSO_DA_FATURA][43:]}" if CHAVE_DE_ACESSO_DA_FATURA in issue["json_data"] and issue["json_data"].get(CHAVE_DE_ACESSO_DA_FATURA) is not None else None,
        }

        nfe_sefaz = {
            "numero_log": issue['json_data']["numero_log"],
            "data_procmto": datetime.strptime(issue['json_data']["data_procmto"], "%Y-%m-%d").strftime("%d.%m.%Y") if "data_procmto" in issue["json_data"] and issue["json_data"].get("data_procmto") is not None else None,
            "hora_procmto": issue['json_data']["hora_procmto"] if "hora_procmto" in issue["json_data"] and issue["json_data"].get("hora_procmto") is not None else None,
        }

        dados_nfe = {"chave_acesso_sefaz": chave_acesso, "nfe_sefaz": nfe_sefaz}

        miro_model = {
            "dados_basicos": dados_basicos,
            "pagamento":pagamento,
            "detalhe": detalhe,
            "sintese": sintese,
            "dados_nfe": dados_nfe,
        }

        return miro_model
    
    def _fatura_factory(self, issue): 

        texto = self._prepare_ref(issue)
        itens = []
        if not issue['json_data'][ALOCAÇÕES_DE_CUSTO]:
            itens.append({
                "cta_razao": issue['domain_data']['fornecedor']['razao'], #Conta Contabil SAP
                "montante":  issue['json_data'][VALOR_TOTAL_DA_FATURA],
                "percentage" : CEM_PORCENTO_DO_VALOR_BRUTO,
                "loc_negocios": issue['domain_data']['centro']['centro'],
                "atribuicao": datetime.strptime(issue['json_data'][DATA_DE_EMISSÃO], "%Y-%m-%d").strftime("%Y%m%d"),
                "texto": texto,
                "centro_custo":  f"{issue['domain_data']['centro']['centro_custo']}",
            })
        else:
            for cost_allocation in issue['json_data'][ALOCAÇÕES_DE_CUSTO]:
                itens.append({
                    "cta_razao": issue['domain_data']['fornecedor']['razao'], #Conta Contabil SAP
                    "montante":  cost_allocation['CustCenterTotalAmount'],
                    "percentage" : cost_allocation['Percentage'],
                    "loc_negocios": cost_allocation['CustCenterDescription'].split(' - ')[0],
                    "atribuicao": datetime.strptime(issue['json_data'][DATA_DE_EMISSÃO], "%Y-%m-%d").strftime("%Y%m%d"),
                    "texto": texto,
                    "centro_custo":  cost_allocation['Code']
                })

        dados_basicos = {
            "cod_fornecedor": issue['domain_data']['fornecedor']['codigo_sap'], #ID_EXTERNO_SAP
            "data_fatura": datetime.strptime(issue['json_data'][DATA_DE_EMISSÃO], "%Y-%m-%d").strftime("%d.%m.%Y"),
            "referencia": issue['json_data'][NÚMERO_DA_FATURA_DO_FORNECEDOR],
            "montante": issue['json_data'][VALOR_TOTAL_DA_FATURA],
            "valor_liquido": issue["json_data"][VALOR_LIQUIDO_DA_FATURA],
            "juros": issue["json_data"][JUROS_DA_FATURA],
            "bus_pl_sec_cd": itens[0]["loc_negocios"],
            "texto": texto,
            "centro_custo_destinatario": issue["domain_data"]["centro"]["centro_custo"],
            "centro_destinatario": issue["domain_data"]["centro"]["centro"],
            "itens": itens
        }

        pagamento = {
            "data_basica": datetime.strptime(
                issue['json_data'][DATA_DE_VENCIMENTO], "%Y-%m-%d"
            ).strftime("%d.%m.%Y"),
            "cond_pgto": CONDICOES_PAGAMENTO_30DIAS 
        }

        fatura_model = {
            "dados_basicos": dados_basicos,
            "pagamento":pagamento,
            "anexo": issue['pdf_data']
        }

        return fatura_model

    def _get_nf_jira(self, issue_id):
        try:

            issue_data = self.IssueJira.get_issue(issue_id)
            complement_form = self._get_issue_fields_by_keys( issue_id, FORM_TEMPLATE_COMPLEMENTO )
            self.GuiandoHelper.check_guiando_form(complement_form)
            donwload_attachment = self.AttachmentJira.download_attachments(issue_data)

            issue_data["fields"] = self.JiraFieldsHelper.remove_null_fields(issue_data.get("fields"))
            attachment = self.AttachmentJira.get_attachment(issue_data)

            nf_type_id = complement_form["tipo_conta"]
            nf_type = None
            if nf_type_id == "ÁGUA":
                nf_type = COMPLEMENTO_DE_ÁGUA

            elif nf_type_id == "ENERGIA" or nf_type_id == ['580547']:
                nf_type = COMPLEMENTO_DE_ENERGIA

            elif nf_type_id == "GÁS":
                nf_type = COMPLEMENTO_DE_GÁS

            attachment[CNPJ_DO_FORNECEDOR] = complement_form['cnpj_fornecedor']
            attachment[RAZÃO_SOCIAL_DO_FORNECEDOR] = complement_form['razao_social_fornecedor']

            attachment[CNPJ_DO_CLIENTE] = complement_form['cnpj_destinatario']
            attachment[NÚMERO_DA_FATURA] = complement_form['nro_nota_fiscal']
            attachment[NÚMERO_DA_FATURA_DO_FORNECEDOR] = complement_form['nro_fatura']
            attachment[DATA_DE_EMISSÃO] = complement_form['data_emissao']
            attachment[DATA_DE_VENCIMENTO] = complement_form['data_vencimento']
            attachment[CHAVE_DE_ACESSO_DA_FATURA] = complement_form['chave_acesso']
            attachment[DATA_DE_REFERÊNCIA] = complement_form['periodo_referencia']
            attachment["numero_log"] = complement_form['protocolo_autorizacao']
            attachment["data_procmto"] = complement_form['data_autorizacao']
            attachment["hora_procmto"] = complement_form['hora_autorizacao']
            if nf_type is not None:
                attachment[nf_type] = {
                    "DataLeituraAnterior" : complement_form['data_leitura_anterior'],
                    "DataLeituraAtual"    : complement_form['data_leitura_atual']
                }

            attachment["grupo_compradores"] = complement_form['grupo_compradores']

            #Init Valor Liquido e Juros
            attachment[VALOR_LIQUIDO_DA_FATURA] = 0
            attachment[JUROS_DA_FATURA] = 0
            attachment[VALOR_TOTAL_DA_FATURA] = float(complement_form['valor_nota'].replace('.','').replace(',','.'))
            if complement_form['valor_liquido'] != "" and complement_form['valor_liquido'] != None:
                attachment[VALOR_LIQUIDO_DA_FATURA] = float(complement_form['valor_liquido'].replace('.','').replace(',','.'))
            if complement_form['juros'] != "" and complement_form['juros'] != None:
                attachment[JUROS_DA_FATURA] = float(complement_form['juros'].replace('.','').replace(',','.'))

            automation_form_id = self.FormJira.get_form_id(issue_id, FORM_TEMPLATE_AUTOMACAO)

            jira_info = {"issue_id": issue_id, "form_id": automation_form_id}

            nf_jira_json = {
                "issue_data": issue_data,
                "attachment": attachment,
                "jira_info": jira_info,
                "pdf_data": donwload_attachment
            }

            return nf_jira_json

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

        except Exception as e:
            raise Exception(f"Erro ao receber a Nota Fiscal:\n{e}")

    def _prepare_ref(self, issue):

        data_ref = datetime.strptime(issue['json_data'][DATA_DE_REFERÊNCIA], "%m/%Y").strftime("%b/%y").upper()
        leitura_anterior = None
        leitura_atual = None
        if issue['json_data'][COMPLEMENTO_DE_ÁGUA] is not None:
            leitura_anterior = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_ÁGUA]['DataLeituraAnterior'], "%Y-%m-%d").strftime("%d/%m/%y").upper() if issue['json_data'][COMPLEMENTO_DE_ÁGUA]['DataLeituraAnterior'] is not None else None
            leitura_atual = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_ÁGUA]['DataLeituraAtual'], "%Y-%m-%d").strftime("%d/%m/%y").upper() if issue['json_data'][COMPLEMENTO_DE_ÁGUA]['DataLeituraAtual'] is not None else None
        elif issue['json_data'][COMPLEMENTO_DE_ENERGIA] is not None:
            leitura_anterior = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_ENERGIA]['DataLeituraAnterior'], "%Y-%m-%d").strftime("%d/%m/%y").upper() if issue['json_data'][COMPLEMENTO_DE_ENERGIA]['DataLeituraAnterior'] is not None else None
            leitura_atual = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_ENERGIA]['DataLeituraAtual'], "%Y-%m-%d").strftime("%d/%m/%y").upper() if issue['json_data'][COMPLEMENTO_DE_ENERGIA]['DataLeituraAtual'] is not None else None
        elif issue['json_data'][COMPLEMENTO_DE_GÁS] is not None:
            leitura_anterior = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_GÁS]['DataLeituraAnterior'], "%Y-%m-%d").strftime("%d/%m/%y").upper() if issue['json_data'][COMPLEMENTO_DE_GÁS]['DataLeituraAnterior'] is not None else None
            leitura_atual = datetime.strptime(issue['json_data'][COMPLEMENTO_DE_GÁS]['DataLeituraAtual'], "%Y-%m-%d").strftime("%d/%m/%y").upper()  if issue['json_data'][COMPLEMENTO_DE_GÁS]['DataLeituraAtual'] is not None else None

        extra_ref = f"PERIODO: {leitura_anterior} A {leitura_atual}" if leitura_anterior is not None and leitura_atual is not None else None
        
        return f"REF: {data_ref} {extra_ref}" if extra_ref is not None else f"REF: {data_ref}"

    def _get_issue_fields_by_keys(self, issue_key, form_template):

        form_jira_keys = self.FormJira.get_form_jira_keys(issue_key, form_template)
        form_fields    = self.FormJira.get_form_fields(issue_key, form_template)
        jira_fields    = self.IssueJira.get_issue_fields_data(issue_key)
        fields_by_jira_and_form = self.IssueFields.get_fields_by_form_and_jira(form_jira_keys, form_fields, jira_fields)

        return fields_by_jira_and_form