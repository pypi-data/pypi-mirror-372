"""Modelos del nucleo del sistema CPE."""

from .address import Address
from .base_sale import BaseSale, Legend, SaleDetail
from .charge import Charge
from .client import Client
from .company import Company
from .detraction import Detraction
from .invoice import Invoice
from .note import Note
from .payment_terms import PaymentTerms, Cuota
from .prepayment import Prepayment

__all__ = [
    "Address",
    "BaseSale", 
    "Charge",
    "Client",
    "Company",
    "Cuota",
    "Detraction", 
    "Invoice",
    "Legend",
    "Note",
    "PaymentTerms",
    "Prepayment",
    "SaleDetail",
]