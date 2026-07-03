from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, Date, Enum as SQLEnum, Float, JSON
from sqlalchemy.orm import relationship
from core.database import base
from core.enum.enum import PlansEnum, SubscriptionStatusEnum

class Subscription(base):
    __tablename__ = 'subscription'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User", back_populates="subscription")
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True, index=True)
    plan = relationship("Plans", back_populates="plan_subscription")
    current_period_start = Column(Date, nullable=True, index=True)
    cancel_at_period_end = Column(Date, nullable=True, index=True)
    current_period_end = Column(Date, nullable=True, index=True)
    amount = Column(Float, index=True, nullable=True)
    frequency = Column(String, index=True, nullable=True)
    payment_provider_id = Column(String, nullable=True)
    provider_subscription_id = Column(String, nullable=True)
    status = Column(SQLEnum(SubscriptionStatusEnum), nullable=False)
    is_active = Column(Boolean)
    moduls = Column(JSON, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", back_populates="company_subscription")
    
class Plans(base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    #mp_plan_id = Column(String, nullable=False, index=True) MALDITA BASURA DE MERCADO_PAGO
    name = Column(SQLEnum(PlansEnum), nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    frequency = Column(Integer, nullable=False, index=True)
    external_id = Column(String, nullable=True, index=True) #id del plan en el proveedor de pagos
    currency = Column(String, nullable=False, default="BRL", index=True) #siempre va a ser BRL no jodas
    plan_subscription = relationship("Subscription", back_populates="plan") 
