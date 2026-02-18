from sqlalchemy import Integer, String, Date, create_engine, Column
from sqlalchemy.orm import declarative_base
import os

db = create_engine(os.getenv('DATABASE_URL'))

base = declarative_base()

class Production(base):
    __tablename__ = 'production'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    client_name = Column('client_name', String, unique=True, index=True, nullable=False)
    project_name = Column('project_name', String, nullable=False)
    delivery_date = Column('delivery_date', Date, nullable=False)
    description = Column('description', String, nullable=True)

# 3. Dica de Ouro: Interface HTML
# Se sua interface for um formulário HTML, use <input type="date">.
# O navegador mostrará o formato local para o usuário (ex: DD/MM/YYYY no Brasil/LatAm).
# Mas o navegador sempre enviará para o seu Python no formato YYYY-MM-DD por padrão. MDN Web Docs - Input Date.
# Qual dessas opções se encaixa melhor no seu projeto? Se estiver usando um formulário HTML, a opção 3 é a mais fácil de todas.