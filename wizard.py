# -*- coding: utf-8 -*-
"""
    wizard.py

"""
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.model import ModelView, fields
from trytond.wizard import (
    Wizard, StateView, Button, StateTransition
)
from trytond.pyson import Eval

__all__ = [
    'ImportDataWizard', 'ImportDataWizardStart', 'ImportDataWizardSuccess',
    'ExportDataWizard', 'ExportDataWizardStart', 'ExportDataWizardSuccess',
    'ImportDataWizardProperties', 'ImportOrderStatesStart', 'ImportOrderStates',
    'ExportPricesStatus', 'ExportPricesStart', 'ExportPrices'
]


class ExportDataWizardStart(ModelView):
    "Export Data Start View"
    __name__ = 'sale.channel.export_data.start'

    message = fields.Text("Message", readonly=True)

    export_order_status = fields.Boolean("Export Order Status ?")
    export_products = fields.Boolean("Export Products ?")
    export_product_prices = fields.Boolean("Export Product Prices ?")
    channel = fields.Many2One("sale.channel", "Channel", select=True)

    @staticmethod
    def default_channel():
        """
        Sets current channel as default
        """
        return Transaction().context.get('active_id')


class ExportDataWizardSuccess(ModelView):
    "Export Data Wizard Success View"
    __name__ = 'sale.channel.export_data.success'

    no_of_orders = fields.Integer(
        "Number Of Orders With Status Exported", readonly=True
    )
    no_of_products = fields.Integer(
        "Number Of Products Exported", readonly=True
    )
    no_of_products_with_prices_exported = fields.Integer(
        "Number Of Products With Prices Exported", readonly=True
    )


class ExportDataWizard(Wizard):
    "Wizard to export data to external channel"
    __name__ = 'sale.channel.export_data'

    start = StateView(
        'sale.channel.export_data.start',
        'sale_channel.export_data_start_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'next', 'tryton-go-next'),
        ]
    )
    next = StateTransition()
    export_ = StateTransition()

    success = StateView(
        'sale.channel.export_data.success',
        'sale_channel.export_data_success_view_form',
        [
            Button('Ok', 'end', 'tryton-ok'),
        ]
    )

    def default_start(self, data):
        """
        Sets default data for wizard

        :param data: Wizard data
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))
        return {
            'message':
                "This wizard will export all order status or products placed "
                "on %s channel(%s). \n \n "
                "Checking checkboxes below, you may choose to export products "
                "or order status or product prices or all. \n \n "
                " * Order status will be exported only for orders which are "
                "updated / modified after the Last Order Export "
                "Time. If Last Order Export Time is missing, then it will "
                "export status for all the orders from beginning of time."
                "[This might be slow depending on number of orders]. \n \n"
                " * Products will be exported only which are "
                "updated / modified after the Last Product Export "
                "Time. If Last Product Export Time is missing, then all the "
                " products will be exported from  from beginning of time."
                "[This might be slow depending on number of products]. \n \n "
                " * Products Prices will be exported only which are "
                "updated / modified after the Last Product Prices Export "
                "Time. If Last Product Price Export Time is missing, then all "
                "the products prices will be exported from the beginning of "
                "time. [This might be slow depending on number of products]. "
                % (channel.name, channel.source),
            'channel': channel.id
        }

    def transition_next(self):
        """
        Move to export state transition
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        self.start.channel = channel

        return 'export_'

    def transition_export_(self):  # pragma: nocover
        """
        Downstream channel implementation can customize the wizard
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        orders = []
        products = []
        products_with_prices = []

        if not (
            self.start.export_order_status or self.start.export_products
            or self.start.export_product_prices
        ):
            return self.raise_user_error(
                "Atleast one checkbox need to be ticked"
            )

        if self.start.export_order_status:
            orders = channel.export_order_status()

        if self.start.export_products:
            products = channel.export_product_catalog()

        if self.start.export_product_prices:
            products_with_prices = channel.export_product_prices()

        self.success.no_of_orders = len(orders)
        self.success.no_of_products = len(products)
        self.success.no_of_products_with_prices_exported = products_with_prices
        return 'success'

    def default_success(self, data):  # pragma: nocover
        return {
            'no_of_orders': self.success.no_of_orders,
            'no_of_products': self.success.no_of_products,
            'no_of_products_with_prices_exported':
                self.success.no_of_products_with_prices_exported,
        }


class ImportDataWizardStart(ModelView):
    "Import Sale Order Start View"
    __name__ = 'sale.channel.import_data.start'

    message = fields.Text("Message", readonly=True)

    import_orders = fields.Boolean("Import Orders")
    import_products = fields.Boolean("Import Products")
    channel = fields.Many2One("sale.channel", "Channel", select=True)

    @staticmethod
    def default_channel():
        """
        Sets current channel as default
        """
        return Transaction().context.get('active_id')


class ImportDataWizardSuccess(ModelView):
    "Import Sale Order Success View"
    __name__ = 'sale.channel.import_data.success'

    no_of_orders = fields.Integer("Number Of Orders Imported", readonly=True)
    no_of_products = fields.Integer(
        "Number Of Products Imported", readonly=True
    )


class ImportDataWizardProperties(ModelView):
    "Import Sale Order Configure View"
    __name__ = 'sale.channel.import_data.properties'

    account_expense = fields.Many2One(
        'account.account', 'Account Expense', domain=[
            ('kind', '=', 'expense'),
            ('company', '=', Eval('company')),
        ], depends=['company']
    )

    account_revenue = fields.Many2One(
        'account.account', 'Account Revenue', domain=[
            ('kind', '=', 'revenue'),
            ('company', '=', Eval('company')),
        ], depends=['company']
    )
    company = fields.Many2One('company.company', 'Company')


class ImportDataWizard(Wizard):
    "Wizard to import data from channel"
    __name__ = 'sale.channel.import_data'

    start = StateView(
        'sale.channel.import_data.start',
        'sale_channel.import_data_start_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'next', 'tryton-go-next'),
        ]
    )
    next = StateTransition()
    properties = StateView(
        'sale.channel.import_data.properties',
        'sale_channel.import_data_properties_view_form',
        [
            Button('Continue', 'create_properties', 'tryton-go-next'),
        ]
    )
    create_properties = StateTransition()
    import_ = StateTransition()

    success = StateView(
        'sale.channel.import_data.success',
        'sale_channel.import_data_success_view_form',
        [
            Button('Ok', 'end', 'tryton-ok'),
        ]
    )

    def default_start(self, data):
        """
        Sets default data for wizard

        :param data: Wizard data
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))
        return {
            'message':
                "This wizard will import all orders and products placed on "
                "%s channel(%s). Orders will be imported only which are "
                "placed after the Last Order Import "
                "Time. If Last Order Import Time is missing, then it will "
                "import all the orders from beginning of time. "
                "[This might be slow depending on number of orders]. "
                "Checking checkboxes below you may choose to import products "
                "or orders or both. "
                % (channel.name, channel.source),
            'channel': channel.id
        }

    def default_properties(self, fields):
        return {
            'company': self.start.channel.company.id,
        }

    def get_model_field(self, kind):
        """
        Returns active record for account field
        """
        ModelField = Pool().get('ir.model.field')

        model_field, = ModelField.search([
            ('model.model', '=', 'product.template'),
            ('name', '=', 'account_%s' % kind),
        ], limit=1)

        return model_field

    def get_default_property(self, kind):
        """
        Returns default properties for product template

        :param kind: revenue or expense
        """
        Property = Pool().get('ir.property')

        company = self.start.channel.company

        model_field = self.get_model_field(kind)
        account_properties = Property.search([
            ('field', '=', model_field.id),
            ('res', '=', None),
            ('company', '=', company.id),
        ], limit=1)

        return account_properties

    def transition_next(self):
        """
        Move to properties view if default property is not set for product
        template while importing products, else continue to import products
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        self.start.channel = channel

        if not (
            self.get_default_property('revenue') and
            self.get_default_property('expense')
        ):
            return 'properties'

        return 'import_'

    def transition_create_properties(self):
        """
        Create default properties for product template
        """
        Property = Pool().get('ir.property')

        if not self.get_default_property('revenue') and \
                self.properties.account_revenue:
            Property.create([{
                'field': self.get_model_field('revenue').id,
                'value': str(self.properties.account_revenue),
                'company': self.start.channel.company.id,
            }])

        if not self.get_default_property('expense') and \
                self.properties.account_expense:
            Property.create([{
                'field': self.get_model_field('expense').id,
                'value': str(self.properties.account_expense),
                'company': self.start.channel.company.id,
            }])
        return 'import_'

    def transition_import_(self):  # pragma: nocover
        """
        Downstream channel implementation can customize the wizard
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        sales = []
        products = []

        if self.start.import_orders:
            sales = channel.import_orders()

        if self.start.import_products:
            products = channel.import_products()

        self.success.no_of_orders = len(sales)
        self.success.no_of_products = len(products)
        return 'success'

    def default_success(self, data):  # pragma: nocover
        return {
            'no_of_orders': self.success.no_of_orders,
            'no_of_products': self.success.no_of_products,
        }


class ImportOrderStatesStart(ModelView):
    "Import Order States Start"
    __name__ = 'sale.channel.import_order_states.start'


class ImportOrderStates(Wizard):
    """
    Wizard to import order states for channel
    """
    __name__ = 'sale.channel.import_order_states'

    start = StateView(
        'sale.channel.import_order_states.start',
        'sale_channel.wizard_import_order_states_start_view_form',
        [
            Button('Ok', 'end', 'tryton-ok'),
        ]
    )

    def default_start(self, fields):
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        channel.import_order_states()

        return {}


class ExportPricesStart(ModelView):
    "Export Prices Start View"
    __name__ = 'sale.channel.export_prices.start'

    message = fields.Text("Messgae", readonly=True)


class ExportPricesStatus(ModelView):
    "Export Prices Status View"
    __name__ = 'sale.channel.export_prices.status'

    products_count = fields.Integer('Products Count', readonly=True)


class ExportPrices(Wizard):
    """
    Export Tier Prices Wizard
    """
    __name__ = 'sale.channel.export_prices'

    start = StateView(
        'sale.channel.export_prices.start',
        'sale_channel.export_prices_start_view_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Continue', 'export_', 'tryton-ok', default=True),
        ]
    )

    export_ = StateView(
        'sale.channel.export_prices.status',
        'sale_channel.export_prices_status_view_form',
        [
            Button('OK', 'end', 'tryton-ok'),
        ]
    )

    def default_start(self, fields):
        """
        Return message to display
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        return {
            'message':
                "This wizard will export product prices to %s "
                "channel (%s). " % (channel.name, channel.source)
        }

    def default_export_(self, fields):
        """
        Export prices and return count of products
        """
        Channel = Pool().get('sale.channel')

        channel = Channel(Transaction().context.get('active_id'))

        return {
            'products_count': channel.export_product_prices()
        }
