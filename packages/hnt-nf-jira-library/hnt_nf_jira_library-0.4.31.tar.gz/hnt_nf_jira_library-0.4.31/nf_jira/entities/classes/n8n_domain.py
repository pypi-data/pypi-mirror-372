import requests
from ..constants import *

class N8NDomain:
    def get_cfop_fornecedor(self, cnpj_fornecedor, cnpj_cliente):
        try:
            domain_request = requests.get(
                f"{API_DOMAIN_N8N_URL}/hnt/cfop_fornecedor?cnpj_fornecedor={cnpj_fornecedor}&cnpj_cliente={cnpj_cliente}",
                auth=N8N_AUTH,
            )
            domain_request.raise_for_status()
            domain_data = domain_request.json()
        except Exception as e:
            raise Exception(f"Erro ao receber cfop_fornecedor:\n{e}")

        return domain_data

    def get_nf_domain(self, type, cnpj):

        n8n_data = self._get_nf_domain_data(cnpj, type)
        return n8n_data

    def _get_nf_domain_data(self, cnpj, type):

        try:
            domain_request = requests.get(
                f"{API_DOMAIN_N8N_URL}/{'fornecedores' if type == 'fornecedor' else 'centros'}?cnpj={cnpj}",
                auth=N8N_AUTH,
            )
            domain_request.raise_for_status()
            domain_data = domain_request.json()

            if not domain_data:
                raise Exception("Could not find domain")

        except Exception as e:
            raise Exception(f"Erro ao receber {type}:\n{e}")

        return domain_data
