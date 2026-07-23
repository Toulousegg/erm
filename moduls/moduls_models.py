from sqlalchemy import Integer, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import base

class Moduls(base):
    __tablename__ = 'moduls'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False, index=True)
    slug = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    icon_url = Column(String, index=True, nullable=True)
    external_id = Column(String, index=True, nullable=True) #id del modulo en el proveedor de abacatepay
    module_route = Column(String, index=True, nullable=True)
    icon_aside = Column(String, index=True, nullable=True)
    company_moduls = relationship("Moduls_Companies", back_populates="modul")


class Moduls_Companies(base):
    __tablename__ = 'moduls_companies'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    modul_id = Column(Integer, ForeignKey('moduls.id'), nullable=False)
    modul = relationship("Moduls", back_populates="company_moduls")
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="moduls_company")
    __table_args__ = (
    UniqueConstraint(
        "company_id",
        "modul_id",
        name="uq_company_module"
    ),
)