# -*- coding: utf-8 -*-
"""
    __init__.py

"""
from trytond.pool import Pool
from channel import (
    SaleChannel, ReadUser, WriteUser, ChannelException, ChannelOrderState
)
from wizard import (
    ImportDataWizard, ImportDataWizardStart, ImportDataWizardSuccess,
    ExportDataWizard, ExportDataWizardStart, ExportDataWizardSuccess,
    ImportDataWizardProperties, ImportOrderStatesStart, ImportOrderStates,
    ExportPricesStatus, ExportPricesStart, ExportPrices
)
from product import ProductSaleChannelListing, Product
from sale import Sale
from user import User


def register():
    Pool.register(
        SaleChannel,
        ReadUser,
        WriteUser,
        ChannelException,
        ChannelOrderState,
        User,
        Sale,
        ProductSaleChannelListing,
        Product,
        ImportDataWizardStart,
        ImportDataWizardSuccess,
        ImportDataWizardProperties,
        ExportDataWizardStart,
        ExportDataWizardSuccess,
        ImportOrderStatesStart,
        ExportPricesStatus,
        ExportPricesStart,
        module='sale_channel', type_='model'
    )
    Pool.register(
        ImportDataWizard,
        ExportDataWizard,
        ImportOrderStates,
        ExportPrices,
        module='sale_channel', type_='wizard'
    )
