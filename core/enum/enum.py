from enum import Enum


class StatusEnum(str, Enum):
    planning = "Planejamento"
    cutting = "Corte"
    pre_assembly = "Pré-montagem"
    lamination = "Laminação"
    truck_loading = "Carregamento"
    installation = "Instalação"
    completed = "Concluído"
    cancelled = "Cancelado"

class ContactsTypes(str, Enum):
    architect = 'arquiteto'
    personal = 'pessoal'
    employed = 'colaborador'
    client = 'cliente'

class ProjectStageEnum(str, Enum):
    planning = "Planejamento"
    cutting = "Corte"
    pre_assembly = "Pre-montagem"
    lamination = "Laminacao"
    truck_loading = "Carregamento"
    installation = "Instalacao"
    finishing = "Acabamento"
    correction = "Correcao"
    other = "Outro"

class DebtStatusEnum(str, Enum):
    pending = "Pendente"
    cancelled = "Cancelado"
    paid = "Pago"
    overdue = "Vencido"


class TransactionTypeEnum(str, Enum):
    income = "Receita"
    expense = "Despesa"


class TransactionCategoryEnum(str, Enum):
    sale = "Venda"
    rent = "Aluguel"
    other_income = "Outras Receitas"
    salary = "Salários"
    purchases = "Compras"
    utilities = "Despesas Operacionais"
    debt_payment = "Pagamento de Dívida"
    receivable_payment = "Recebimento"
    material = "Material"


class ReceivablesStatusEnum(str, Enum):
    pending = "Pendente"
    paid = "Pago"
    cancelled = "Cancelado"
    overdue = "Vencido"


class UserRoleEnum(str, Enum):
    admin = "Administrador"
    carpenter = "Marceneiro"
    auxiliary = "Auxiliar"


class PlansEnum(str, Enum):
    basic = "Básico"
    premium = "Premium"
    enterprise = "Empresarial"


class SubscriptionStatusEnum(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"

class SubscriptionCycle(str, Enum):
    MONTHLY = "Mensal"
    ANNUALLY = "Anual"
    
class WeekDayEnum(str, Enum):
    monday = "segunda"
    tuesday = "terça"
    wednesday = "quarta"
    thursday = "quinta"
    friday = "sexta"
    saturday = "sabado"
    sunday = "domingo"
