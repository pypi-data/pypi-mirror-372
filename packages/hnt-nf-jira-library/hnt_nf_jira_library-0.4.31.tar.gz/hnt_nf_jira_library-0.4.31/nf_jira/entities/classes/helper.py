import json
from os import getcwd, makedirs, path
from ..constants import *

class BaseHelper:

    def __init__(self):
        pass

class JsonHelper(BaseHelper):

    def save_json(self, filename, json_data):

        path_dir = path.join(getcwd(), 'output', 'json')
        if not path.exists(path_dir):
            makedirs(path_dir)

        with open(f"./output/json/{filename}.json", "w", encoding="utf-8") as json_file:
            json.dump( json_data, json_file, ensure_ascii=False, indent=4)

class JiraFieldsHelper(BaseHelper):

    def remove_null_fields(self, fields):
        fields_data_without_nulls = {}

        for key, value in fields.items():
            if value is not None:
                fields_data_without_nulls[key] = value

        return fields_data_without_nulls
    
    def _rename_fields(self, fields):
        fields = self._fields
        new_fields_data = {}

        for key, value in self._jira_fields.items():
            if value in fields:
                if "text" in fields[value]:
                    new_value = fields[value].get("text")
                elif "date" in fields[value]:
                    new_value = fields[value].get("date")
                elif "value" in fields[value]:
                    new_value = fields[value].get("value")
                else:
                    new_value = fields[value]

                new_fields_data[key] = new_value

        return new_fields_data
    
class GuiandoHelper(BaseHelper):
        
    def __init__(self):
        self._check_sefaz = lambda form_data: form_data[POSSUI_CHAVE_ACESSO][0] == "1"
        self._check_document_type = lambda document_type: 'nota_fiscal' if document_type == "2" else 'fatura'

    def include_cod_sap_miro(self, cod_sap, miro):
        miro['referencia_pedido']['numero_pedido'] = cod_sap
        return miro
    
    ## Validar o Form com base no Sefaz
    def check_guiando_form(self, form_data):
        check_sefaz = self._check_sefaz(form_data)
        if check_sefaz: self._check_sefaz_form(form_data)
        document_type = self._check_document_type(form_data['document_type'][0])
        self._check_fiscal_form(form_data) if document_type == 'nota_fiscal' else self._check_fatura_form(form_data)
        self._check_required_form(form_data)
        pass

    def _check_sefaz_form(self, form_data):
        for sefaz_field in SEFAZ_FIELDS:
            if sefaz_field not in form_data: raise KeyError(f"ERRO - O campo {sefaz_field} não foi enviado.")
            if form_data[sefaz_field] is None or form_data[sefaz_field] == "" : raise KeyError(f"ERRO - O campo {sefaz_field} está vazio.")
        pass

    def _check_fiscal_form(self, form_data):
        if 'nro_nota_fiscal' not in form_data: raise KeyError(f"ERRO - O Campo {'nro_nota_fiscal'} não foi enviado.")
        if form_data['nro_nota_fiscal'] is None or form_data['nro_nota_fiscal'] == "": raise KeyError(f"ERRO - O Campo {'nro_nota_fiscal'} está vazio.")
        pass

    def _check_fatura_form(self, form_data):
        if 'nro_fatura' not in form_data: raise KeyError(f"ERRO - O Campo {'nro_fatura'} não foi enviado.")
        if form_data['nro_fatura'] is None or form_data['nro_fatura'] == "": raise KeyError(f"ERRO - O Campo {'nro_fatura'} está vazio.")
        pass

    def _check_required_form(self, form_data):
        for field in form_data:
            if field not in OPTIONAL_FIELDS and field not in SEFAZ_FIELDS:
                if form_data[field] is None or form_data[field] == "":raise KeyError(f"ERRO - O Campo {field} está vazio")
        pass