import os

#PATH
DEST_PATH = os.path.join(os.getcwd(), "output", "pdf")

#Constant N8N
N8N_AUTH = (os.getenv("N8N_USERNAME"), os.getenv("N8N_PASSWORD"))
API_DOMAIN_N8N_URL = os.getenv("DOMAIN_URL")
FORNECEDOR_N8N_DOMAIN = "fornecedor"
CENTRO_N8N_DOMAIN = "centro"

# Constantes dos ID's de Formulario
FORM_TEMPLATE_AUTOMACAO = "910a886b-701a-490d-8b02-708b6c2d9881"
FORM_TEMPLATE_COMPLEMENTO = "720b4c69-9d84-4f08-930e-1d6c22805f71"

# Constants Jira
JIRA_AUTH = (os.getenv("USER"), os.getenv("ACCESS_TOKEN"))
API_ISSUE_URL = os.getenv("ISSUE_URL")
API_FORM_URL = os.getenv("FORM_URL")
CLOUD_ID = os.getenv("CLOUD_ID")
CONTA_RAZAO_JUROS_CM = '431100'
#Constantes de Validação
OPTIONAL_FIELDS = [
    "nro_fatura",
    "nro_nota_fiscal",
    "valor_liquido",
    "juros",
    "data_leitura_atual",
    "data_leitura_anterior"
]

SEFAZ_FIELDS = [
    "data_autorizacao",
    "hora_autorizacao",
    "protocolo_autorizacao",
    "chave_acesso"
]

FISCAL_FIELDS = [
    "InvoiceNumber"
]

FATURA_FIELDS = [
    "SupplierInvoiceNumber"
]

API_HEADERS = {
                "Accept": "application/json",
                "Content-Type": "application/json",
              }

API_ATTACHMENT_HEADERS = {
                            "Accept": "*/*",
                         }

API_ATLASSIAN_HEADERS = {
                            "Accept": "application/json",
                            "X-ExperimentalApi": "opt-in",
                        }

# Reference From Miro
SERIE_NF = '001'
MAX_LEN_NRO_NF = 6
CONDICOES_PAGAMENTO_30DIAS = '0000'
# Reference From Fatura
MAX_LEN_SAP_REFERENCE = 16
#Test Constants
ISSUE_KEY = "GHN-643"
TRASITION_PEDIDO_CRIADO = '241'
TRASITION_REVISAR_ERRO  = '231'
FORM_COMPLEMENTO_ID = "f1671ecd-fc44-418f-b6e3-88d774a4b0d4"
FORM_AUTOMACAO_ID = "e6214bb3-eafc-4de8-ad5a-c8b387346c3e"
STATUS_LIBERADO = "2"
STATUS_BLOQUEADO = "1"
# Jira Form Nota de Pedido
VALOR_LIQUIDO_DA_FATURA = "valor_liquido"
JUROS_DA_FATURA = "juro"
CEM_PORCENTO_DO_VALOR_BRUTO = 100.00
# Jira Form Automação
NRO_DOCUMENTO_FATURA_SAP_FIELD = "customfield_11145"
CODIGO_BARRAS_FIELD = "customfield_13127"
# # Constantes do Anexo Json
ID_DO_LOCATÁRIO = "TenantId"
NOME_DA_INTEGRAÇÃO = "IntegrationName"
NOME_DO_USUÁRIO = "UserName"
EMAIL_DO_USUÁRIO = "UserEmail"
ID_DA_FATURA = "InvoiceId"
NÚMERO_DA_FATURA_DO_APLICATIVO = "AplicationInvoiceNumber"
CNPJ_DO_FORNECEDOR = "SupplierCnpj"
RAZÃO_SOCIAL_DO_FORNECEDOR = "SupplierCorporateName"
CNPJ_DO_CLIENTE = "ClientCnpj"
RAZÃO_SOCIAL_DO_CLIENTE = "ClientCorporateName"
ENDEREÇO_DO_FORNECEDOR = "SupplierAddress"
ENDEREÇO_DO_CLIENTE = "ClientAddress"
DATA_DE_VENCIMENTO = "DueDate"
DATA_DE_EMISSÃO = "DateOfIssue"
DATA_DE_REFERÊNCIA = "ReferenceDate"
DATA_DE_REGISTRO = "DateRegister"
VALOR_TOTAL_DA_FATURA = "TotalInvoiceAmount"
VALOR_BRUTO_DA_FATURA = "GrossInvoiceValue"
CÓDIGO_DE_BARRAS = "BarCode"
NÚMERO_DA_FATURA = "InvoiceNumber"
CHAVE_DE_ACESSO_DA_FATURA = "InvoiceAccessKey"
NÚMERO_DA_FATURA_DO_FORNECEDOR = "SupplierInvoiceNumber"
CÓDIGO_DE_DEBITO_AUTOMÁTICO = "AutomaticDebitCode"
INFORMAÇÃO_DA_FATURA = "InvoiceInformation"
OBSERVAÇÃO_DA_FATURA = "InvoiceObservation"
NOME_DO_FORNECEDOR = "SupplierName"
NÚMERO_DO_CONTRATO = "ContractNumber"
ID_DO_CONTRATO = "ContractId"
STATUS_DO_CONTRATO = "ContractStatus"
STATUS_DA_FATURA = "InvoiceStatus"
LOCALIZAÇÃO_DO_CONTRATO = "ContractLocation"
VERTICAL_DO_FORNECEDOR = "SupplierVertical"
PROTOCOLO_DE_LANÇAMENTO = "launchProtocol"
SERVIÇOS_DA_FATURA = "InvoiceServices"
IMPOSTOS = "Taxes"
CAMPOS_CUSTOMIZADOS = "CustomFields"
ALOCAÇÕES_DE_CUSTO = "CostAllocations"
ARQUIVOS_DA_FATURA = "InvoiceFiles"
COMPLEMENTO_DE_ÁGUA = "WaterComplement"
COMPLEMENTO_DE_ENERGIA = "EnergyComplement"
COMPLEMENTO_DE_GÁS = "GasComplement"
POSSUI_CHAVE_ACESSO = "possui_chave_acesso"
