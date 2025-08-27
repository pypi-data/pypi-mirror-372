from typing import Dict, Type, Optional
from .query import *  # Import all query models
from .request_body import *  # Import all request body models
from .fields import *

class Endpoints:
    """
    Registry for storing endpoint metadata, including paths,
    query models, and request body models.
    """

    registry: Dict[str, Dict[str, Optional[Type]]] = {}

    @classmethod
    def initialize_registry(cls):
        """
        Initialize the endpoint registry dynamically.
        """
        cls.registry['Activity_index'] = {
            'path': '/activities.json',
            'method': 'GET',
            'query_model': Activity_index_Query,
            'request_body_model': None,
            'field_model': Activity_Fields,
            'summary': 'Return the data for all Activities',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Activities',
        }
        cls.registry['Activity_create'] = {
            'path': '/activities.json',
            'method': 'POST',
            'query_model': Activity_create_Query,
            'request_body_model': Activity_create_RequestBody,
            'field_model': Activity_Fields,
            'summary': 'Create a new Activity',
            'description': 'Outlines the parameters and data fields used when creating a new Activity',
        }
        cls.registry['Activity_show'] = {
            'path': '/activities/{id}.json',
            'method': 'GET',
            'query_model': Activity_show_Query,
            'request_body_model': None,
            'field_model': Activity_Fields,
            'summary': 'Return the data for a single Activity',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Activity',
        }
        cls.registry['Activity_update'] = {
            'path': '/activities/{id}.json',
            'method': 'PATCH',
            'query_model': Activity_update_Query,
            'request_body_model': Activity_update_RequestBody,
            'field_model': Activity_Fields,
            'summary': 'Update a single Activity',
            'description': 'Outlines the parameters and data fields used when updating a single Activity',
        }
        cls.registry['Activity_destroy'] = {
            'path': '/activities/{id}.json',
            'method': 'DELETE',
            'query_model': Activity_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Activity',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Activity',
        }
        cls.registry['Activityrate_index'] = {
            'path': '/activity_rates.json',
            'method': 'GET',
            'query_model': Activityrate_index_Query,
            'request_body_model': None,
            'field_model': ActivityRate_Fields,
            'summary': 'Return the data for all ActivityRates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ActivityRates',
        }
        cls.registry['Activityrate_create'] = {
            'path': '/activity_rates.json',
            'method': 'POST',
            'query_model': Activityrate_create_Query,
            'request_body_model': Activityrate_create_RequestBody,
            'field_model': ActivityRate_Fields,
            'summary': 'Create a new ActivityRate',
            'description': 'Outlines the parameters and data fields used when creating a new ActivityRate',
        }
        cls.registry['Activityrate_show'] = {
            'path': '/activity_rates/{id}.json',
            'method': 'GET',
            'query_model': Activityrate_show_Query,
            'request_body_model': None,
            'field_model': ActivityRate_Fields,
            'summary': 'Return the data for a single ActivityRate',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ActivityRate',
        }
        cls.registry['Activityrate_update'] = {
            'path': '/activity_rates/{id}.json',
            'method': 'PATCH',
            'query_model': Activityrate_update_Query,
            'request_body_model': Activityrate_update_RequestBody,
            'field_model': ActivityRate_Fields,
            'summary': 'Update a single ActivityRate',
            'description': 'Outlines the parameters and data fields used when updating a single ActivityRate',
        }
        cls.registry['Activityrate_destroy'] = {
            'path': '/activity_rates/{id}.json',
            'method': 'DELETE',
            'query_model': Activityrate_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single ActivityRate',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single ActivityRate',
        }
        cls.registry['Activitydescription_index'] = {
            'path': '/activity_descriptions.json',
            'method': 'GET',
            'query_model': Activitydescription_index_Query,
            'request_body_model': None,
            'field_model': ActivityDescription_Fields,
            'summary': 'Return the data for all ActivityDescriptions',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ActivityDescriptions',
        }
        cls.registry['Activitydescription_create'] = {
            'path': '/activity_descriptions.json',
            'method': 'POST',
            'query_model': Activitydescription_create_Query,
            'request_body_model': Activitydescription_create_RequestBody,
            'field_model': ActivityDescription_Fields,
            'summary': 'Create a new ActivityDescription',
            'description': 'Outlines the parameters and data fields used when creating a new ActivityDescription',
        }
        cls.registry['Activitydescription_show'] = {
            'path': '/activity_descriptions/{id}.json',
            'method': 'GET',
            'query_model': Activitydescription_show_Query,
            'request_body_model': None,
            'field_model': ActivityDescription_Fields,
            'summary': 'Return the data for a single ActivityDescription',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ActivityDescription',
        }
        cls.registry['Activitydescription_update'] = {
            'path': '/activity_descriptions/{id}.json',
            'method': 'PATCH',
            'query_model': Activitydescription_update_Query,
            'request_body_model': Activitydescription_update_RequestBody,
            'field_model': ActivityDescription_Fields,
            'summary': 'Update a single ActivityDescription',
            'description': 'Outlines the parameters and data fields used when updating a single ActivityDescription',
        }
        cls.registry['Activitydescription_destroy'] = {
            'path': '/activity_descriptions/{id}.json',
            'method': 'DELETE',
            'query_model': Activitydescription_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single ActivityDescription',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single ActivityDescription',
        }
        cls.registry['Allocation_index'] = {
            'path': '/allocations.json',
            'method': 'GET',
            'query_model': Allocation_index_Query,
            'request_body_model': None,
            'field_model': Allocation_Fields,
            'summary': 'Return the data for all Allocations',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Allocations',
        }
        cls.registry['Allocation_show'] = {
            'path': '/allocations/{id}.json',
            'method': 'GET',
            'query_model': Allocation_show_Query,
            'request_body_model': None,
            'field_model': Allocation_Fields,
            'summary': 'Return the data for a single Allocation',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Allocation',
        }
        cls.registry['Bankaccount_index'] = {
            'path': '/bank_accounts.json',
            'method': 'GET',
            'query_model': Bankaccount_index_Query,
            'request_body_model': None,
            'field_model': BankAccount_Fields,
            'summary': 'Return the data for all BankAccounts',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all BankAccounts',
        }
        cls.registry['Bankaccount_create'] = {
            'path': '/bank_accounts.json',
            'method': 'POST',
            'query_model': Bankaccount_create_Query,
            'request_body_model': Bankaccount_create_RequestBody,
            'field_model': BankAccount_Fields,
            'summary': 'Create a new BankAccount',
            'description': 'Outlines the parameters and data fields used when creating a new BankAccount',
        }
        cls.registry['Bankaccount_show'] = {
            'path': '/bank_accounts/{id}.json',
            'method': 'GET',
            'query_model': Bankaccount_show_Query,
            'request_body_model': None,
            'field_model': BankAccount_Fields,
            'summary': 'Return the data for a single BankAccount',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single BankAccount',
        }
        cls.registry['Bankaccount_update'] = {
            'path': '/bank_accounts/{id}.json',
            'method': 'PATCH',
            'query_model': Bankaccount_update_Query,
            'request_body_model': Bankaccount_update_RequestBody,
            'field_model': BankAccount_Fields,
            'summary': 'Update a single BankAccount',
            'description': 'Outlines the parameters and data fields used when updating a single BankAccount',
        }
        cls.registry['Bankaccount_destroy'] = {
            'path': '/bank_accounts/{id}.json',
            'method': 'DELETE',
            'query_model': Bankaccount_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single BankAccount',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single BankAccount',
        }
        cls.registry['Banktransaction_index'] = {
            'path': '/bank_transactions.json',
            'method': 'GET',
            'query_model': Banktransaction_index_Query,
            'request_body_model': None,
            'field_model': BankTransaction_Fields,
            'summary': 'Return the data for all BankTransactions',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all BankTransactions',
        }
        cls.registry['Banktransaction_show'] = {
            'path': '/bank_transactions/{id}.json',
            'method': 'GET',
            'query_model': Banktransaction_show_Query,
            'request_body_model': None,
            'field_model': BankTransaction_Fields,
            'summary': 'Return the data for a single BankTransaction',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single BankTransaction',
        }
        cls.registry['Banktransfer_show'] = {
            'path': '/bank_transfers/{id}.json',
            'method': 'GET',
            'query_model': Banktransfer_show_Query,
            'request_body_model': None,
            'field_model': BankTransfer_Fields,
            'summary': 'Return the data for a single BankTransfer',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single BankTransfer',
        }
        cls.registry['Billtheme_index'] = {
            'path': '/bill_themes.json',
            'method': 'GET',
            'query_model': Billtheme_index_Query,
            'request_body_model': None,
            'field_model': BillTheme_Fields,
            'summary': 'Return the data for all BillThemes',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all BillThemes',
        }
        cls.registry['Billtheme_update'] = {
            'path': '/bill_themes/{id}.json',
            'method': 'PATCH',
            'query_model': Billtheme_update_Query,
            'request_body_model': Billtheme_update_RequestBody,
            'field_model': BillTheme_Fields,
            'summary': 'Update a single BillTheme',
            'description': 'Outlines the parameters and data fields used when updating a single BillTheme',
        }
        cls.registry['Billableclient_index'] = {
            'path': '/billable_clients.json',
            'method': 'GET',
            'query_model': Billableclient_index_Query,
            'request_body_model': None,
            'field_model': BillableClient_Fields,
            'summary': 'Return the data for all BillableClients',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all BillableClients',
        }
        cls.registry['Billablematter_ids'] = {
            'path': '/billable_matters/ids.json',
            'method': 'GET',
            'query_model': Billablematter_ids_Query,
            'request_body_model': None,
            'field_model': BillableMatter_Fields,
            'summary': 'Returns the unique identifiers of all BillableMatter',
            'description': 'This data is retrieved asynchronously',
        }
        cls.registry['Billablematter_index'] = {
            'path': '/billable_matters.json',
            'method': 'GET',
            'query_model': Billablematter_index_Query,
            'request_body_model': None,
            'field_model': BillableMatter_Fields,
            'summary': 'Return the data for all BillableMatters',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all BillableMatters',
        }
        cls.registry['Bill_preview'] = {
            'path': '/bills/{id}/preview.json',
            'method': 'GET',
            'query_model': Bill_preview_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Returns the pre-rendered html for the Bill',
            'description': "This endpoint returns a pre-rendered HTML object that you can use to view a preview of your bills.\nThe HTML provided contains all of the CSS rules it requires to show the bill correctly,\nas well as the DOCTYPE setting it requires.\nIt's best to use an iframe, or similar object, to render the results of this endpoint.\n",
        }
        cls.registry['Bill_index'] = {
            'path': '/bills.json',
            'method': 'GET',
            'query_model': Bill_index_Query,
            'request_body_model': None,
            'field_model': Bill_Fields,
            'summary': 'Return the data for all Bills',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Bills',
        }
        cls.registry['Bill_show'] = {
            'path': '/bills/{id}.json',
            'method': 'GET',
            'query_model': Bill_show_Query,
            'request_body_model': None,
            'field_model': Bill_Fields,
            'summary': 'Return the data for a single Bill',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Bill',
        }
        cls.registry['Bill_update'] = {
            'path': '/bills/{id}.json',
            'method': 'PATCH',
            'query_model': Bill_update_Query,
            'request_body_model': Bill_update_RequestBody,
            'field_model': Bill_Fields,
            'summary': 'Update a single Bill',
            'description': 'Outlines the parameters and data fields used when updating a single Bill',
        }
        cls.registry['Bill_destroy'] = {
            'path': '/bills/{id}.json',
            'method': 'DELETE',
            'query_model': Bill_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete or void a Bill',
            'description': 'This endpoint will transition a bill to either its deleted or voided state.\nA bill can only be deleted or voided if it has no payments recorded\nand its current state is one of the following:\n* Draft\n* Pending Approval\n* Unpaid\n\nA bill will automatically be moved to a deleted or void state based on its current state.\nThe mappings for this are:\n* Draft -> Deleted\n* Pending Approval -> Deleted\n* Unpaid -> Void\n',
        }
        cls.registry['Calendarentry_index'] = {
            'path': '/calendar_entries.json',
            'method': 'GET',
            'query_model': Calendarentry_index_Query,
            'request_body_model': None,
            'field_model': CalendarEntry_Fields,
            'summary': 'Return the data for all CalendarEntries',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CalendarEntries',
        }
        cls.registry['Calendarentry_create'] = {
            'path': '/calendar_entries.json',
            'method': 'POST',
            'query_model': Calendarentry_create_Query,
            'request_body_model': Calendarentry_create_RequestBody,
            'field_model': CalendarEntry_Fields,
            'summary': 'Create a new CalendarEntry',
            'description': 'Outlines the parameters and data fields used when creating a new CalendarEntry',
        }
        cls.registry['Calendarentry_show'] = {
            'path': '/calendar_entries/{id}.json',
            'method': 'GET',
            'query_model': Calendarentry_show_Query,
            'request_body_model': None,
            'field_model': CalendarEntry_Fields,
            'summary': 'Return the data for a single CalendarEntry',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CalendarEntry',
        }
        cls.registry['Calendarentry_update'] = {
            'path': '/calendar_entries/{id}.json',
            'method': 'PATCH',
            'query_model': Calendarentry_update_Query,
            'request_body_model': Calendarentry_update_RequestBody,
            'field_model': CalendarEntry_Fields,
            'summary': 'Update a single CalendarEntry',
            'description': 'Outlines the parameters and data fields used when updating a single CalendarEntry',
        }
        cls.registry['Calendarentry_destroy'] = {
            'path': '/calendar_entries/{id}.json',
            'method': 'DELETE',
            'query_model': Calendarentry_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single CalendarEntry',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single CalendarEntry',
        }
        cls.registry['Calendarentryeventtype_index'] = {
            'path': '/calendar_entry_event_types.json',
            'method': 'GET',
            'query_model': Calendarentryeventtype_index_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Return the data for all calendar entry event types',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CalendarEntryEventTypes',
        }
        cls.registry['Calendarentryeventtype_create'] = {
            'path': '/calendar_entry_event_types.json',
            'method': 'POST',
            'query_model': Calendarentryeventtype_create_Query,
            'request_body_model': Calendarentryeventtype_create_RequestBody,
            'field_model': None,
            'summary': 'Create a new calendar entry event type',
            'description': 'Outlines the parameters and data fields used when creating a new CalendarEntryEventType',
        }
        cls.registry['Calendarentryeventtype_show'] = {
            'path': '/calendar_entry_event_types/{id}.json',
            'method': 'GET',
            'query_model': Calendarentryeventtype_show_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Return the data for a single calendar entry event type',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CalendarEntryEventType',
        }
        cls.registry['Calendarentryeventtype_update'] = {
            'path': '/calendar_entry_event_types/{id}.json',
            'method': 'PATCH',
            'query_model': Calendarentryeventtype_update_Query,
            'request_body_model': Calendarentryeventtype_update_RequestBody,
            'field_model': None,
            'summary': 'Update a single calendar entry event type',
            'description': 'Outlines the parameters and data fields used when updating a single CalendarEntryEventType',
        }
        cls.registry['Calendarentryeventtype_destroy'] = {
            'path': '/calendar_entry_event_types/{id}.json',
            'method': 'DELETE',
            'query_model': Calendarentryeventtype_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single calendar entry event type',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single CalendarEntryEventType',
        }
        cls.registry['Calendar_index'] = {
            'path': '/calendars.json',
            'method': 'GET',
            'query_model': Calendar_index_Query,
            'request_body_model': None,
            'field_model': Calendar_Fields,
            'summary': 'Return the data for all Calendars',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Calendars',
        }
        cls.registry['Calendar_create'] = {
            'path': '/calendars.json',
            'method': 'POST',
            'query_model': Calendar_create_Query,
            'request_body_model': Calendar_create_RequestBody,
            'field_model': Calendar_Fields,
            'summary': 'Create a new Calendar',
            'description': 'Outlines the parameters and data fields used when creating a new Calendar',
        }
        cls.registry['Calendar_show'] = {
            'path': '/calendars/{id}.json',
            'method': 'GET',
            'query_model': Calendar_show_Query,
            'request_body_model': None,
            'field_model': Calendar_Fields,
            'summary': 'Return the data for a single Calendar',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Calendar',
        }
        cls.registry['Calendar_update'] = {
            'path': '/calendars/{id}.json',
            'method': 'PATCH',
            'query_model': Calendar_update_Query,
            'request_body_model': Calendar_update_RequestBody,
            'field_model': Calendar_Fields,
            'summary': 'Update a single Calendar',
            'description': 'Outlines the parameters and data fields used when updating a single Calendar',
        }
        cls.registry['Calendar_destroy'] = {
            'path': '/calendars/{id}.json',
            'method': 'DELETE',
            'query_model': Calendar_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Calendar',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Calendar',
        }
        cls.registry['Cliopaymentslink_index'] = {
            'path': '/clio_payments/links.json',
            'method': 'GET',
            'query_model': Cliopaymentslink_index_Query,
            'request_body_model': None,
            'field_model': ClioPaymentsLink_Fields,
            'summary': 'Return the data for all ClioPaymentsLinks',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ClioPaymentsLinks',
        }
        cls.registry['Cliopaymentslink_create'] = {
            'path': '/clio_payments/links.json',
            'method': 'POST',
            'query_model': Cliopaymentslink_create_Query,
            'request_body_model': Cliopaymentslink_create_RequestBody,
            'field_model': ClioPaymentsLink_Fields,
            'summary': 'Create a new ClioPaymentsLink',
            'description': 'Outlines the parameters and data fields used when creating a new ClioPaymentsLink',
        }
        cls.registry['Cliopaymentslink_show'] = {
            'path': '/clio_payments/links/{id}.json',
            'method': 'GET',
            'query_model': Cliopaymentslink_show_Query,
            'request_body_model': None,
            'field_model': ClioPaymentsLink_Fields,
            'summary': 'Return the data for a single ClioPaymentsLink',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ClioPaymentsLink',
        }
        cls.registry['Cliopaymentslink_update'] = {
            'path': '/clio_payments/links/{id}.json',
            'method': 'PATCH',
            'query_model': Cliopaymentslink_update_Query,
            'request_body_model': Cliopaymentslink_update_RequestBody,
            'field_model': ClioPaymentsLink_Fields,
            'summary': 'Update a single ClioPaymentsLink',
            'description': 'Outlines the parameters and data fields used when updating a single ClioPaymentsLink',
        }
        cls.registry['Cliopaymentspayment_index'] = {
            'path': '/clio_payments/payments.json',
            'method': 'GET',
            'query_model': Cliopaymentspayment_index_Query,
            'request_body_model': None,
            'field_model': ClioPaymentsPayment_Fields,
            'summary': 'Return the data for all ClioPaymentsPayments',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ClioPaymentsPayments',
        }
        cls.registry['Cliopaymentspayment_show'] = {
            'path': '/clio_payments/payments/{id}.json',
            'method': 'GET',
            'query_model': Cliopaymentspayment_show_Query,
            'request_body_model': None,
            'field_model': ClioPaymentsPayment_Fields,
            'summary': 'Return the data for a single ClioPaymentsPayment',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ClioPaymentsPayment',
        }
        cls.registry['Communication_index'] = {
            'path': '/communications.json',
            'method': 'GET',
            'query_model': Communication_index_Query,
            'request_body_model': None,
            'field_model': Communication_Fields,
            'summary': 'Return the data for all Communications',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Communications',
        }
        cls.registry['Communication_create'] = {
            'path': '/communications.json',
            'method': 'POST',
            'query_model': Communication_create_Query,
            'request_body_model': Communication_create_RequestBody,
            'field_model': Communication_Fields,
            'summary': 'Create a new Communication',
            'description': 'Outlines the parameters and data fields used when creating a new Communication',
        }
        cls.registry['Communication_show'] = {
            'path': '/communications/{id}.json',
            'method': 'GET',
            'query_model': Communication_show_Query,
            'request_body_model': None,
            'field_model': Communication_Fields,
            'summary': 'Return the data for a single Communication',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Communication',
        }
        cls.registry['Communication_update'] = {
            'path': '/communications/{id}.json',
            'method': 'PATCH',
            'query_model': Communication_update_Query,
            'request_body_model': Communication_update_RequestBody,
            'field_model': Communication_Fields,
            'summary': 'Update a single Communication',
            'description': 'Outlines the parameters and data fields used when updating a single Communication',
        }
        cls.registry['Communication_destroy'] = {
            'path': '/communications/{id}.json',
            'method': 'DELETE',
            'query_model': Communication_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Communication',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Communication',
        }
        cls.registry['Emailaddress_index'] = {
            'path': '/contacts/{contact_id}/email_addresses.json',
            'method': 'GET',
            'query_model': Emailaddress_index_Query,
            'request_body_model': None,
            'field_model': EmailAddress_Fields,
            'summary': 'Return the data for all EmailAddresses',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all EmailAddresses',
        }
        cls.registry['Phonenumber_index'] = {
            'path': '/contacts/{contact_id}/phone_numbers.json',
            'method': 'GET',
            'query_model': Phonenumber_index_Query,
            'request_body_model': None,
            'field_model': PhoneNumber_Fields,
            'summary': 'Return the data for all PhoneNumbers',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all PhoneNumbers',
        }
        cls.registry['Contact_index'] = {
            'path': '/contacts.json',
            'method': 'GET',
            'query_model': Contact_index_Query,
            'request_body_model': None,
            'field_model': Contact_Fields,
            'summary': 'Return the data for all Contacts',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Contacts',
        }
        cls.registry['Contact_create'] = {
            'path': '/contacts.json',
            'method': 'POST',
            'query_model': Contact_create_Query,
            'request_body_model': Contact_create_RequestBody,
            'field_model': Contact_Fields,
            'summary': 'Create a new Contact',
            'description': 'Outlines the parameters and data fields used when creating a new Contact',
        }
        cls.registry['Contact_show'] = {
            'path': '/contacts/{id}.json',
            'method': 'GET',
            'query_model': Contact_show_Query,
            'request_body_model': None,
            'field_model': Contact_Fields,
            'summary': 'Return the data for a single Contact',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Contact',
        }
        cls.registry['Contact_update'] = {
            'path': '/contacts/{id}.json',
            'method': 'PATCH',
            'query_model': Contact_update_Query,
            'request_body_model': Contact_update_RequestBody,
            'field_model': Contact_Fields,
            'summary': 'Update a single Contact',
            'description': 'Outlines the parameters and data fields used when updating a single Contact',
        }
        cls.registry['Contact_destroy'] = {
            'path': '/contacts/{id}.json',
            'method': 'DELETE',
            'query_model': Contact_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Contact',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Contact',
        }
        cls.registry['Conversationmessage_index'] = {
            'path': '/conversation_messages.json',
            'method': 'GET',
            'query_model': Conversationmessage_index_Query,
            'request_body_model': None,
            'field_model': ConversationMessage_Fields,
            'summary': 'Return the data for all ConversationMessages',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ConversationMessages',
        }
        cls.registry['Conversationmessage_create'] = {
            'path': '/conversation_messages.json',
            'method': 'POST',
            'query_model': Conversationmessage_create_Query,
            'request_body_model': Conversationmessage_create_RequestBody,
            'field_model': ConversationMessage_Fields,
            'summary': 'Create a new ConversationMessage',
            'description': 'Outlines the parameters and data fields used when creating a new ConversationMessage',
        }
        cls.registry['Conversationmessage_show'] = {
            'path': '/conversation_messages/{id}.json',
            'method': 'GET',
            'query_model': Conversationmessage_show_Query,
            'request_body_model': None,
            'field_model': ConversationMessage_Fields,
            'summary': 'Return the data for a single ConversationMessage',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ConversationMessage',
        }
        cls.registry['Conversation_index'] = {
            'path': '/conversations.json',
            'method': 'GET',
            'query_model': Conversation_index_Query,
            'request_body_model': None,
            'field_model': Conversation_Fields,
            'summary': 'Return the data for all Conversations',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Conversations',
        }
        cls.registry['Conversation_show'] = {
            'path': '/conversations/{id}.json',
            'method': 'GET',
            'query_model': Conversation_show_Query,
            'request_body_model': None,
            'field_model': Conversation_Fields,
            'summary': 'Return the data for a single Conversation',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Conversation',
        }
        cls.registry['Conversation_update'] = {
            'path': '/conversations/{id}.json',
            'method': 'PATCH',
            'query_model': Conversation_update_Query,
            'request_body_model': Conversation_update_RequestBody,
            'field_model': Conversation_Fields,
            'summary': 'Update a single Conversation',
            'description': 'Outlines the parameters and data fields used when updating a single Conversation',
        }
        cls.registry['Jurisdictionstotrigger_index'] = {
            'path': '/court_rules/jurisdictions/{jurisdiction_id}/triggers.json',
            'method': 'GET',
            'query_model': Jurisdictionstotrigger_index_Query,
            'request_body_model': None,
            'field_model': JurisdictionsToTrigger_Fields,
            'summary': 'Return the data for all triggers',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all JurisdictionsToTriggers',
        }
        cls.registry['Jurisdictionstotrigger_show'] = {
            'path': '/court_rules/jurisdictions/{jurisdiction_id}/triggers/{id}.json',
            'method': 'GET',
            'query_model': Jurisdictionstotrigger_show_Query,
            'request_body_model': None,
            'field_model': JurisdictionsToTrigger_Fields,
            'summary': 'Return the data for the trigger',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single JurisdictionsToTrigger',
        }
        cls.registry['Jurisdiction_index'] = {
            'path': '/court_rules/jurisdictions.json',
            'method': 'GET',
            'query_model': Jurisdiction_index_Query,
            'request_body_model': None,
            'field_model': Jurisdiction_Fields,
            'summary': 'Return the data for all jurisdictions',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Jurisdictions',
        }
        cls.registry['Jurisdiction_show'] = {
            'path': '/court_rules/jurisdictions/{id}.json',
            'method': 'GET',
            'query_model': Jurisdiction_show_Query,
            'request_body_model': None,
            'field_model': Jurisdiction_Fields,
            'summary': 'Return the data for the jurisdiction',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Jurisdiction',
        }
        cls.registry['Matterdocket_preview'] = {
            'path': '/court_rules/matter_dockets/preview.json',
            'method': 'GET',
            'query_model': Matterdocket_preview_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Preview calendar dates for the docket',
            'description': 'Preview calendar dates for the docket',
        }
        cls.registry['Matterdocket_index'] = {
            'path': '/court_rules/matter_dockets.json',
            'method': 'GET',
            'query_model': Matterdocket_index_Query,
            'request_body_model': None,
            'field_model': MatterDocket_Fields,
            'summary': 'Return the data for all matter dockets',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all MatterDockets',
        }
        cls.registry['Matterdocket_create'] = {
            'path': '/court_rules/matter_dockets.json',
            'method': 'POST',
            'query_model': Matterdocket_create_Query,
            'request_body_model': Matterdocket_create_RequestBody,
            'field_model': MatterDocket_Fields,
            'summary': 'Creates a matter docket',
            'description': 'Outlines the parameters and data fields used when creating a new MatterDocket',
        }
        cls.registry['Matterdocket_show'] = {
            'path': '/court_rules/matter_dockets/{id}.json',
            'method': 'GET',
            'query_model': Matterdocket_show_Query,
            'request_body_model': None,
            'field_model': MatterDocket_Fields,
            'summary': 'Return the data for the matter docket',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single MatterDocket',
        }
        cls.registry['Matterdocket_destroy'] = {
            'path': '/court_rules/matter_dockets/{id}.json',
            'method': 'DELETE',
            'query_model': Matterdocket_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Deletes the requested matter docket',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single MatterDocket',
        }
        cls.registry['Servicetype_index'] = {
            'path': '/court_rules/service_types.json',
            'method': 'GET',
            'query_model': Servicetype_index_Query,
            'request_body_model': None,
            'field_model': ServiceType_Fields,
            'summary': 'Return the data for all service types',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ServiceTypes',
        }
        cls.registry['Servicetype_show'] = {
            'path': '/court_rules/service_types/{id}.json',
            'method': 'GET',
            'query_model': Servicetype_show_Query,
            'request_body_model': None,
            'field_model': ServiceType_Fields,
            'summary': 'Return the data for the service type',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ServiceType',
        }
        cls.registry['Creditmemo_index'] = {
            'path': '/credit_memos.json',
            'method': 'GET',
            'query_model': Creditmemo_index_Query,
            'request_body_model': None,
            'field_model': CreditMemo_Fields,
            'summary': 'Return the data for all CreditMemos',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CreditMemos',
        }
        cls.registry['Creditmemo_show'] = {
            'path': '/credit_memos/{id}.json',
            'method': 'GET',
            'query_model': Creditmemo_show_Query,
            'request_body_model': None,
            'field_model': CreditMemo_Fields,
            'summary': 'Return the data for a single CreditMemo',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CreditMemo',
        }
        cls.registry['Currency_index'] = {
            'path': '/currencies.json',
            'method': 'GET',
            'query_model': Currency_index_Query,
            'request_body_model': None,
            'field_model': Currency_Fields,
            'summary': 'Return the data for all Currencies',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Currencies',
        }
        cls.registry['Customfield_index'] = {
            'path': '/custom_fields.json',
            'method': 'GET',
            'query_model': Customfield_index_Query,
            'request_body_model': None,
            'field_model': CustomField_Fields,
            'summary': 'Return the data for all CustomFields',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CustomFields',
        }
        cls.registry['Customfield_create'] = {
            'path': '/custom_fields.json',
            'method': 'POST',
            'query_model': Customfield_create_Query,
            'request_body_model': Customfield_create_RequestBody,
            'field_model': CustomField_Fields,
            'summary': 'Create a new CustomField',
            'description': 'Outlines the parameters and data fields used when creating a new CustomField',
        }
        cls.registry['Customfield_show'] = {
            'path': '/custom_fields/{id}.json',
            'method': 'GET',
            'query_model': Customfield_show_Query,
            'request_body_model': None,
            'field_model': CustomField_Fields,
            'summary': 'Return the data for a single CustomField',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CustomField',
        }
        cls.registry['Customfield_update'] = {
            'path': '/custom_fields/{id}.json',
            'method': 'PATCH',
            'query_model': Customfield_update_Query,
            'request_body_model': Customfield_update_RequestBody,
            'field_model': CustomField_Fields,
            'summary': 'Update a single CustomField',
            'description': 'Outlines the parameters and data fields used when updating a single CustomField',
        }
        cls.registry['Customfield_destroy'] = {
            'path': '/custom_fields/{id}.json',
            'method': 'DELETE',
            'query_model': Customfield_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single CustomField',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single CustomField',
        }
        cls.registry['Customfieldset_index'] = {
            'path': '/custom_field_sets.json',
            'method': 'GET',
            'query_model': Customfieldset_index_Query,
            'request_body_model': None,
            'field_model': CustomFieldSet_Fields,
            'summary': 'Return the data for all CustomFieldSets',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CustomFieldSets',
        }
        cls.registry['Customfieldset_create'] = {
            'path': '/custom_field_sets.json',
            'method': 'POST',
            'query_model': Customfieldset_create_Query,
            'request_body_model': Customfieldset_create_RequestBody,
            'field_model': CustomFieldSet_Fields,
            'summary': 'Create a new CustomFieldSet',
            'description': 'Outlines the parameters and data fields used when creating a new CustomFieldSet',
        }
        cls.registry['Customfieldset_show'] = {
            'path': '/custom_field_sets/{id}.json',
            'method': 'GET',
            'query_model': Customfieldset_show_Query,
            'request_body_model': None,
            'field_model': CustomFieldSet_Fields,
            'summary': 'Return the data for a single CustomFieldSet',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CustomFieldSet',
        }
        cls.registry['Customfieldset_update'] = {
            'path': '/custom_field_sets/{id}.json',
            'method': 'PATCH',
            'query_model': Customfieldset_update_Query,
            'request_body_model': Customfieldset_update_RequestBody,
            'field_model': CustomFieldSet_Fields,
            'summary': 'Update a single CustomFieldSet',
            'description': 'Outlines the parameters and data fields used when updating a single CustomFieldSet',
        }
        cls.registry['Customfieldset_destroy'] = {
            'path': '/custom_field_sets/{id}.json',
            'method': 'DELETE',
            'query_model': Customfieldset_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single CustomFieldSet',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single CustomFieldSet',
        }
        cls.registry['Customaction_index'] = {
            'path': '/custom_actions.json',
            'method': 'GET',
            'query_model': Customaction_index_Query,
            'request_body_model': None,
            'field_model': CustomAction_Fields,
            'summary': 'Return the data for all CustomActions',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CustomActions',
        }
        cls.registry['Customaction_create'] = {
            'path': '/custom_actions.json',
            'method': 'POST',
            'query_model': Customaction_create_Query,
            'request_body_model': Customaction_create_RequestBody,
            'field_model': CustomAction_Fields,
            'summary': 'Create a new CustomAction',
            'description': 'Outlines the parameters and data fields used when creating a new CustomAction',
        }
        cls.registry['Customaction_show'] = {
            'path': '/custom_actions/{id}.json',
            'method': 'GET',
            'query_model': Customaction_show_Query,
            'request_body_model': None,
            'field_model': CustomAction_Fields,
            'summary': 'Return the data for a single CustomAction',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CustomAction',
        }
        cls.registry['Customaction_update'] = {
            'path': '/custom_actions/{id}.json',
            'method': 'PATCH',
            'query_model': Customaction_update_Query,
            'request_body_model': Customaction_update_RequestBody,
            'field_model': CustomAction_Fields,
            'summary': 'Update a single CustomAction',
            'description': 'Outlines the parameters and data fields used when updating a single CustomAction',
        }
        cls.registry['Customaction_destroy'] = {
            'path': '/custom_actions/{id}.json',
            'method': 'DELETE',
            'query_model': Customaction_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single CustomAction',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single CustomAction',
        }
        cls.registry['Damage_index'] = {
            'path': '/damages.json',
            'method': 'GET',
            'query_model': Damage_index_Query,
            'request_body_model': None,
            'field_model': Damage_Fields,
            'summary': 'Return the data for all Damages',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Damages',
        }
        cls.registry['Damage_create'] = {
            'path': '/damages.json',
            'method': 'POST',
            'query_model': Damage_create_Query,
            'request_body_model': Damage_create_RequestBody,
            'field_model': Damage_Fields,
            'summary': 'Creating a Damage',
            'description': 'Outlines the parameters and data fields used when creating a new Damage',
        }
        cls.registry['Damage_show'] = {
            'path': '/damages/{id}.json',
            'method': 'GET',
            'query_model': Damage_show_Query,
            'request_body_model': None,
            'field_model': Damage_Fields,
            'summary': 'Return a specific Damage',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Damage',
        }
        cls.registry['Damage_update'] = {
            'path': '/damages/{id}.json',
            'method': 'PATCH',
            'query_model': Damage_update_Query,
            'request_body_model': Damage_update_RequestBody,
            'field_model': Damage_Fields,
            'summary': 'Updating a Damage',
            'description': 'Outlines the parameters and data fields used when updating a single Damage',
        }
        cls.registry['Damage_destroy'] = {
            'path': '/damages/{id}.json',
            'method': 'DELETE',
            'query_model': Damage_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Deleting a Damage',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Damage',
        }
        cls.registry['Expensecategory_index'] = {
            'path': '/expense_categories.json',
            'method': 'GET',
            'query_model': Expensecategory_index_Query,
            'request_body_model': None,
            'field_model': ExpenseCategory_Fields,
            'summary': 'Return the data for all ExpenseCategories',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ExpenseCategories',
        }
        cls.registry['Expensecategory_create'] = {
            'path': '/expense_categories.json',
            'method': 'POST',
            'query_model': Expensecategory_create_Query,
            'request_body_model': Expensecategory_create_RequestBody,
            'field_model': ExpenseCategory_Fields,
            'summary': 'Create a new ExpenseCategory',
            'description': 'Outlines the parameters and data fields used when creating a new ExpenseCategory',
        }
        cls.registry['Expensecategory_show'] = {
            'path': '/expense_categories/{id}.json',
            'method': 'GET',
            'query_model': Expensecategory_show_Query,
            'request_body_model': None,
            'field_model': ExpenseCategory_Fields,
            'summary': 'Return the data for a single ExpenseCategory',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ExpenseCategory',
        }
        cls.registry['Expensecategory_update'] = {
            'path': '/expense_categories/{id}.json',
            'method': 'PATCH',
            'query_model': Expensecategory_update_Query,
            'request_body_model': Expensecategory_update_RequestBody,
            'field_model': ExpenseCategory_Fields,
            'summary': 'Update a single ExpenseCategory',
            'description': 'Outlines the parameters and data fields used when updating a single ExpenseCategory',
        }
        cls.registry['Expensecategory_destroy'] = {
            'path': '/expense_categories/{id}.json',
            'method': 'DELETE',
            'query_model': Expensecategory_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single ExpenseCategory',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single ExpenseCategory',
        }
        cls.registry['Grant_index'] = {
            'path': '/grants.json',
            'method': 'GET',
            'query_model': Grant_index_Query,
            'request_body_model': None,
            'field_model': Grant_Fields,
            'summary': 'Return the data for all grants',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Grants',
        }
        cls.registry['Grant_create'] = {
            'path': '/grants.json',
            'method': 'POST',
            'query_model': Grant_create_Query,
            'request_body_model': Grant_create_RequestBody,
            'field_model': Grant_Fields,
            'summary': 'Create a new grant',
            'description': 'Outlines the parameters and data fields used when creating a new Grant',
        }
        cls.registry['Grant_show'] = {
            'path': '/grants/{id}.json',
            'method': 'GET',
            'query_model': Grant_show_Query,
            'request_body_model': None,
            'field_model': Grant_Fields,
            'summary': 'Return the data for a single grant',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Grant',
        }
        cls.registry['Grant_update'] = {
            'path': '/grants/{id}.json',
            'method': 'PATCH',
            'query_model': Grant_update_Query,
            'request_body_model': Grant_update_RequestBody,
            'field_model': Grant_Fields,
            'summary': 'Update a single grant',
            'description': 'Outlines the parameters and data fields used when updating a single Grant',
        }
        cls.registry['Grant_destroy'] = {
            'path': '/grants/{id}.json',
            'method': 'DELETE',
            'query_model': Grant_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Deletes a single grant',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Grant',
        }
        cls.registry['Grantfundingsource_index'] = {
            'path': '/grant_funding_sources.json',
            'method': 'GET',
            'query_model': Grantfundingsource_index_Query,
            'request_body_model': None,
            'field_model': GrantFundingSource_Fields,
            'summary': 'Return the data for all grant funding sources',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all GrantFundingSources',
        }
        cls.registry['Grantfundingsource_create'] = {
            'path': '/grant_funding_sources.json',
            'method': 'POST',
            'query_model': Grantfundingsource_create_Query,
            'request_body_model': Grantfundingsource_create_RequestBody,
            'field_model': GrantFundingSource_Fields,
            'summary': 'Create a new grant funding source',
            'description': 'Outlines the parameters and data fields used when creating a new GrantFundingSource',
        }
        cls.registry['Grantfundingsource_update'] = {
            'path': '/grant_funding_sources/{id}.json',
            'method': 'PATCH',
            'query_model': Grantfundingsource_update_Query,
            'request_body_model': Grantfundingsource_update_RequestBody,
            'field_model': GrantFundingSource_Fields,
            'summary': 'Update a single grant funding source',
            'description': 'Outlines the parameters and data fields used when updating a single GrantFundingSource',
        }
        cls.registry['Grantfundingsource_destroy'] = {
            'path': '/grant_funding_sources/{id}.json',
            'method': 'DELETE',
            'query_model': Grantfundingsource_destroy_Query,
            'request_body_model': Grantfundingsource_destroy_RequestBody,
            'field_model': GrantFundingSource_Fields,
            'summary': 'Delete a single grant funding source',
            'description': 'Outlines the parameters and data fields used when updating a single GrantFundingSource',
        }
        cls.registry['Group_index'] = {
            'path': '/groups.json',
            'method': 'GET',
            'query_model': Group_index_Query,
            'request_body_model': None,
            'field_model': Group_Fields,
            'summary': 'Return the data for all Groups',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Groups',
        }
        cls.registry['Group_create'] = {
            'path': '/groups.json',
            'method': 'POST',
            'query_model': Group_create_Query,
            'request_body_model': Group_create_RequestBody,
            'field_model': Group_Fields,
            'summary': 'Create a new Group',
            'description': 'Outlines the parameters and data fields used when creating a new Group',
        }
        cls.registry['Group_show'] = {
            'path': '/groups/{id}.json',
            'method': 'GET',
            'query_model': Group_show_Query,
            'request_body_model': None,
            'field_model': Group_Fields,
            'summary': 'Return the data for a single Group',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Group',
        }
        cls.registry['Group_update'] = {
            'path': '/groups/{id}.json',
            'method': 'PATCH',
            'query_model': Group_update_Query,
            'request_body_model': Group_update_RequestBody,
            'field_model': Group_Fields,
            'summary': 'Update a single Group',
            'description': 'Outlines the parameters and data fields used when updating a single Group',
        }
        cls.registry['Group_destroy'] = {
            'path': '/groups/{id}.json',
            'method': 'DELETE',
            'query_model': Group_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Group',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Group',
        }
        cls.registry['Eventmetrics_index'] = {
            'path': '/internal_notifications/event_metrics.json',
            'method': 'GET',
            'query_model': Eventmetrics_index_Query,
            'request_body_model': None,
            'field_model': EventMetrics_Fields,
            'summary': 'Unread in-app notification events',
            'description': 'Outlines the parameters, optional and required, used when requesting Event Metrics',
        }
        cls.registry['Myevent_index'] = {
            'path': '/internal_notifications/my_events.json',
            'method': 'GET',
            'query_model': Myevent_index_Query,
            'request_body_model': None,
            'field_model': MyEvent_Fields,
            'summary': 'Return the data for all of my in-app notification events',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all MyEvents',
        }
        cls.registry['Myevent_update'] = {
            'path': '/internal_notifications/my_events/{id}.json',
            'method': 'PATCH',
            'query_model': Myevent_update_Query,
            'request_body_model': Myevent_update_RequestBody,
            'field_model': MyEvent_Fields,
            'summary': 'Mark a single in-app notification event as read/unread',
            'description': 'Outlines the parameters and data fields used when updating a single MyEvent',
        }
        cls.registry['Myevent_destroy'] = {
            'path': '/internal_notifications/my_events/{id}.json',
            'method': 'DELETE',
            'query_model': Myevent_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Clear (delete) a single in-app notification event',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single MyEvent',
        }
        cls.registry['Interestcharge_index'] = {
            'path': '/interest_charges.json',
            'method': 'GET',
            'query_model': Interestcharge_index_Query,
            'request_body_model': None,
            'field_model': InterestCharge_Fields,
            'summary': 'Return the data for all InterestCharges',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all InterestCharges',
        }
        cls.registry['Interestcharge_destroy'] = {
            'path': '/interest_charges/{id}.json',
            'method': 'DELETE',
            'query_model': Interestcharge_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single InterestCharge',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single InterestCharge',
        }
        cls.registry['Lineitem_index'] = {
            'path': '/line_items.json',
            'method': 'GET',
            'query_model': Lineitem_index_Query,
            'request_body_model': None,
            'field_model': LineItem_Fields,
            'summary': 'Return the data for all LineItems',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LineItems',
        }
        cls.registry['Lineitem_update'] = {
            'path': '/line_items/{id}.json',
            'method': 'PATCH',
            'query_model': Lineitem_update_Query,
            'request_body_model': Lineitem_update_RequestBody,
            'field_model': LineItem_Fields,
            'summary': 'Update a single LineItem',
            'description': 'Outlines the parameters and data fields used when updating a single LineItem',
        }
        cls.registry['Lineitem_destroy'] = {
            'path': '/line_items/{id}.json',
            'method': 'DELETE',
            'query_model': Lineitem_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single LineItem',
            'description': "A LineItem can not be deleted if it's Bill is not editable",
        }
        cls.registry['Logentry_index'] = {
            'path': '/log_entries.json',
            'method': 'GET',
            'query_model': Logentry_index_Query,
            'request_body_model': None,
            'field_model': LogEntry_Fields,
            'summary': 'Return the data for all LogEntries',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LogEntries',
        }
        cls.registry['Client_show'] = {
            'path': '/matters/{matter_id}/client.json',
            'method': 'GET',
            'query_model': Client_show_Query,
            'request_body_model': None,
            'field_model': Client_Fields,
            'summary': 'Return the client data for a single matter',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Client',
        }
        cls.registry['Relatedcontacts_index'] = {
            'path': '/matters/{matter_id}/related_contacts.json',
            'method': 'GET',
            'query_model': Relatedcontacts_index_Query,
            'request_body_model': None,
            'field_model': RelatedContacts_Fields,
            'summary': 'Return the related contact data for a single matter',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all RelatedContacts',
        }
        cls.registry['Mattercontacts_index'] = {
            'path': '/matters/{matter_id}/contacts.json',
            'method': 'GET',
            'query_model': Mattercontacts_index_Query,
            'request_body_model': None,
            'field_model': MatterContacts_Fields,
            'summary': 'Return the related contact data for a single matter',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all MatterContacts',
        }
        cls.registry['Matter_index'] = {
            'path': '/matters.json',
            'method': 'GET',
            'query_model': Matter_index_Query,
            'request_body_model': None,
            'field_model': Matter_Fields,
            'summary': 'Return the data for all Matters',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Matters',
        }
        cls.registry['Matter_create'] = {
            'path': '/matters.json',
            'method': 'POST',
            'query_model': Matter_create_Query,
            'request_body_model': Matter_create_RequestBody,
            'field_model': Matter_Fields,
            'summary': 'Create a new Matter',
            'description': 'Outlines the parameters and data fields used when creating a new Matter',
        }
        cls.registry['Matter_show'] = {
            'path': '/matters/{id}.json',
            'method': 'GET',
            'query_model': Matter_show_Query,
            'request_body_model': None,
            'field_model': Matter_Fields,
            'summary': 'Return the data for a single Matter',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Matter',
        }
        cls.registry['Matter_update'] = {
            'path': '/matters/{id}.json',
            'method': 'PATCH',
            'query_model': Matter_update_Query,
            'request_body_model': Matter_update_RequestBody,
            'field_model': Matter_Fields,
            'summary': 'Update a single Matter',
            'description': 'Outlines the parameters and data fields used when updating a single Matter',
        }
        cls.registry['Matter_destroy'] = {
            'path': '/matters/{id}.json',
            'method': 'DELETE',
            'query_model': Matter_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Matter',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Matter',
        }
        cls.registry['Matterstage_index'] = {
            'path': '/matter_stages.json',
            'method': 'GET',
            'query_model': Matterstage_index_Query,
            'request_body_model': None,
            'field_model': MatterStage_Fields,
            'summary': 'Return the data for all MatterStages',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all MatterStages',
        }
        cls.registry['Medicalrecord_update'] = {
            'path': '/medical_records/{id}.json',
            'method': 'PATCH',
            'query_model': Medicalrecord_update_Query,
            'request_body_model': Medicalrecord_update_RequestBody,
            'field_model': MedicalRecord_Fields,
            'summary': 'Updating a Medical Record',
            'description': 'Outlines the parameters and data fields used when updating a single MedicalRecord',
        }
        cls.registry['Medicalrecord_destroy'] = {
            'path': '/medical_records/{id}.json',
            'method': 'DELETE',
            'query_model': Medicalrecord_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Destroying a Medical Record',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single MedicalRecord',
        }
        cls.registry['Medicalrecordsrequest_index'] = {
            'path': '/medical_records_details.json',
            'method': 'GET',
            'query_model': Medicalrecordsrequest_index_Query,
            'request_body_model': None,
            'field_model': MedicalRecordsRequest_Fields,
            'summary': 'Return the data for all Medical Records Details',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Medical Records Details\n',
        }
        cls.registry['Medicalrecordsrequest_create'] = {
            'path': '/medical_records_details.json',
            'method': 'POST',
            'query_model': Medicalrecordsrequest_create_Query,
            'request_body_model': Medicalrecordsrequest_create_RequestBody,
            'field_model': MedicalRecordsRequest_Fields,
            'summary': 'Creating a Medical Records Detail, Medical Records and Medical Bills',
            'description': 'This endpoint allows a creation of a Medical Records Detail, multiple Medical Records and Medical Bills.\nMedical Liens can also be created as a property under Medical Bills.\n\nReference the payload to see how the records are being passed in.\n',
        }
        cls.registry['Medicalrecordsrequest_show'] = {
            'path': '/medical_records_details/{id}.json',
            'method': 'GET',
            'query_model': Medicalrecordsrequest_show_Query,
            'request_body_model': None,
            'field_model': MedicalRecordsRequest_Fields,
            'summary': 'Return the data for a single Medical Records Detail',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Medical Records Details\n',
        }
        cls.registry['Medicalrecordsrequest_update'] = {
            'path': '/medical_records_details/{id}.json',
            'method': 'PATCH',
            'query_model': Medicalrecordsrequest_update_Query,
            'request_body_model': Medicalrecordsrequest_update_RequestBody,
            'field_model': MedicalRecordsRequest_Fields,
            'summary': 'Updating a Medical Records Detail',
            'description': 'If there are records being passed into the Medical Records or Medical Bills parameter they will be treated\nas new records and new Medical Records / Medical Bills will be created.\n',
        }
        cls.registry['Medicalrecordsrequest_destroy'] = {
            'path': '/medical_records_details/{id}.json',
            'method': 'DELETE',
            'query_model': Medicalrecordsrequest_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Destroying a Medical Records Detail',
            'description': 'When a Medical Records Detail is destroyed, the child records, such as Medical Records, Medical Bills and Liens\nwill also be destroyed in the same transaction.\n',
        }
        cls.registry['Medicalbill_update'] = {
            'path': '/medical_bills/{id}.json',
            'method': 'PATCH',
            'query_model': Medicalbill_update_Query,
            'request_body_model': Medicalbill_update_RequestBody,
            'field_model': MedicalBill_Fields,
            'summary': 'Updating a Medical Bill',
            'description': 'Outlines the parameters and data fields used when updating a single Medical Bill\n',
        }
        cls.registry['Medicalbill_destroy'] = {
            'path': '/medical_bills/{id}.json',
            'method': 'DELETE',
            'query_model': Medicalbill_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Destroying a Medical Bill',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Medical Bill\n',
        }
        cls.registry['Note_index'] = {
            'path': '/notes.json',
            'method': 'GET',
            'query_model': Note_index_Query,
            'request_body_model': None,
            'field_model': Note_Fields,
            'summary': 'Return the data for all Notes',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Notes',
        }
        cls.registry['Note_create'] = {
            'path': '/notes.json',
            'method': 'POST',
            'query_model': Note_create_Query,
            'request_body_model': Note_create_RequestBody,
            'field_model': Note_Fields,
            'summary': 'Create a new Note',
            'description': 'Outlines the parameters and data fields used when creating a new Note',
        }
        cls.registry['Note_show'] = {
            'path': '/notes/{id}.json',
            'method': 'GET',
            'query_model': Note_show_Query,
            'request_body_model': None,
            'field_model': Note_Fields,
            'summary': 'Return the data for a single Note',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Note',
        }
        cls.registry['Note_update'] = {
            'path': '/notes/{id}.json',
            'method': 'PATCH',
            'query_model': Note_update_Query,
            'request_body_model': Note_update_RequestBody,
            'field_model': Note_Fields,
            'summary': 'Update a single Note',
            'description': 'Outlines the parameters and data fields used when updating a single Note',
        }
        cls.registry['Note_destroy'] = {
            'path': '/notes/{id}.json',
            'method': 'DELETE',
            'query_model': Note_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Note',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Note',
        }
        cls.registry['Outstandingclientbalance_index'] = {
            'path': '/outstanding_client_balances.json',
            'method': 'GET',
            'query_model': Outstandingclientbalance_index_Query,
            'request_body_model': None,
            'field_model': OutstandingClientBalance_Fields,
            'summary': 'Return the data for all OutstandingClientBalances',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all OutstandingClientBalances',
        }
        cls.registry['Practicearea_index'] = {
            'path': '/practice_areas.json',
            'method': 'GET',
            'query_model': Practicearea_index_Query,
            'request_body_model': None,
            'field_model': PracticeArea_Fields,
            'summary': 'Return the data for all PracticeAreas',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all PracticeAreas',
        }
        cls.registry['Practicearea_create'] = {
            'path': '/practice_areas.json',
            'method': 'POST',
            'query_model': Practicearea_create_Query,
            'request_body_model': Practicearea_create_RequestBody,
            'field_model': PracticeArea_Fields,
            'summary': 'Create a new PracticeArea',
            'description': 'Outlines the parameters and data fields used when creating a new PracticeArea',
        }
        cls.registry['Practicearea_show'] = {
            'path': '/practice_areas/{id}.json',
            'method': 'GET',
            'query_model': Practicearea_show_Query,
            'request_body_model': None,
            'field_model': PracticeArea_Fields,
            'summary': 'Return the data for a single PracticeArea',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single PracticeArea',
        }
        cls.registry['Practicearea_update'] = {
            'path': '/practice_areas/{id}.json',
            'method': 'PATCH',
            'query_model': Practicearea_update_Query,
            'request_body_model': Practicearea_update_RequestBody,
            'field_model': PracticeArea_Fields,
            'summary': 'Update a single PracticeArea',
            'description': 'Outlines the parameters and data fields used when updating a single PracticeArea',
        }
        cls.registry['Practicearea_destroy'] = {
            'path': '/practice_areas/{id}.json',
            'method': 'DELETE',
            'query_model': Practicearea_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single PracticeArea',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single PracticeArea',
        }
        cls.registry['Relationship_index'] = {
            'path': '/relationships.json',
            'method': 'GET',
            'query_model': Relationship_index_Query,
            'request_body_model': None,
            'field_model': Relationship_Fields,
            'summary': 'Return the data for all Relationships',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Relationships',
        }
        cls.registry['Relationship_create'] = {
            'path': '/relationships.json',
            'method': 'POST',
            'query_model': Relationship_create_Query,
            'request_body_model': Relationship_create_RequestBody,
            'field_model': Relationship_Fields,
            'summary': 'Create a new Relationship',
            'description': 'Outlines the parameters and data fields used when creating a new Relationship',
        }
        cls.registry['Relationship_show'] = {
            'path': '/relationships/{id}.json',
            'method': 'GET',
            'query_model': Relationship_show_Query,
            'request_body_model': None,
            'field_model': Relationship_Fields,
            'summary': 'Return the data for a single Relationship',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Relationship',
        }
        cls.registry['Relationship_update'] = {
            'path': '/relationships/{id}.json',
            'method': 'PATCH',
            'query_model': Relationship_update_Query,
            'request_body_model': Relationship_update_RequestBody,
            'field_model': Relationship_Fields,
            'summary': 'Update a single Relationship',
            'description': 'Outlines the parameters and data fields used when updating a single Relationship',
        }
        cls.registry['Relationship_destroy'] = {
            'path': '/relationships/{id}.json',
            'method': 'DELETE',
            'query_model': Relationship_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Relationship',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Relationship',
        }
        cls.registry['Reminder_index'] = {
            'path': '/reminders.json',
            'method': 'GET',
            'query_model': Reminder_index_Query,
            'request_body_model': None,
            'field_model': Reminder_Fields,
            'summary': 'Return the data for all Reminders',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Reminders',
        }
        cls.registry['Reminder_create'] = {
            'path': '/reminders.json',
            'method': 'POST',
            'query_model': Reminder_create_Query,
            'request_body_model': Reminder_create_RequestBody,
            'field_model': Reminder_Fields,
            'summary': 'Create a new Reminder',
            'description': 'Outlines the parameters and data fields used when creating a new Reminder',
        }
        cls.registry['Reminder_show'] = {
            'path': '/reminders/{id}.json',
            'method': 'GET',
            'query_model': Reminder_show_Query,
            'request_body_model': None,
            'field_model': Reminder_Fields,
            'summary': 'Return the data for a single Reminder',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Reminder',
        }
        cls.registry['Reminder_update'] = {
            'path': '/reminders/{id}.json',
            'method': 'PATCH',
            'query_model': Reminder_update_Query,
            'request_body_model': Reminder_update_RequestBody,
            'field_model': Reminder_Fields,
            'summary': 'Update a single Reminder',
            'description': 'Outlines the parameters and data fields used when updating a single Reminder',
        }
        cls.registry['Reminder_destroy'] = {
            'path': '/reminders/{id}.json',
            'method': 'DELETE',
            'query_model': Reminder_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Reminder',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Reminder',
        }
        cls.registry['Report_download'] = {
            'path': '/reports/{id}/download.json',
            'method': 'GET',
            'query_model': Report_download_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Download the completed Report',
            'description': 'Download the completed Report',
        }
        cls.registry['Report_index'] = {
            'path': '/reports.json',
            'method': 'GET',
            'query_model': Report_index_Query,
            'request_body_model': None,
            'field_model': Report_Fields,
            'summary': 'Return the data for all Reports',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Reports',
        }
        cls.registry['Report_create'] = {
            'path': '/reports.json',
            'method': 'POST',
            'query_model': Report_create_Query,
            'request_body_model': Report_create_RequestBody,
            'field_model': Report_Fields,
            'summary': 'Create a new Report',
            'description': 'Outlines the parameters and data fields used when creating a new Report',
        }
        cls.registry['Report_show'] = {
            'path': '/reports/{id}.json',
            'method': 'GET',
            'query_model': Report_show_Query,
            'request_body_model': None,
            'field_model': Report_Fields,
            'summary': 'Return the data for a single Report',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Report',
        }
        cls.registry['Reportpreset_generate_report'] = {
            'path': '/report_presets/{id}/generate_report.json',
            'method': 'POST',
            'query_model': Reportpreset_generate_report_Query,
            'request_body_model': None,
            'field_model': Report_Fields,
            'summary': 'Generate a new report for a given preset',
            'description': 'Generate a new report for a given preset',
        }
        cls.registry['Reportpreset_index'] = {
            'path': '/report_presets.json',
            'method': 'GET',
            'query_model': Reportpreset_index_Query,
            'request_body_model': None,
            'field_model': ReportPreset_Fields,
            'summary': 'Return the data for all ReportPresets',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ReportPresets',
        }
        cls.registry['Reportpreset_create'] = {
            'path': '/report_presets.json',
            'method': 'POST',
            'query_model': Reportpreset_create_Query,
            'request_body_model': Reportpreset_create_RequestBody,
            'field_model': ReportPreset_Fields,
            'summary': 'Create a new ReportPreset',
            'description': 'Outlines the parameters and data fields used when creating a new ReportPreset',
        }
        cls.registry['Reportpreset_show'] = {
            'path': '/report_presets/{id}.json',
            'method': 'GET',
            'query_model': Reportpreset_show_Query,
            'request_body_model': None,
            'field_model': ReportPreset_Fields,
            'summary': 'Return the data for a single ReportPreset',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ReportPreset',
        }
        cls.registry['Reportpreset_update'] = {
            'path': '/report_presets/{id}.json',
            'method': 'PATCH',
            'query_model': Reportpreset_update_Query,
            'request_body_model': Reportpreset_update_RequestBody,
            'field_model': ReportPreset_Fields,
            'summary': 'Update a single ReportPreset',
            'description': 'Outlines the parameters and data fields used when updating a single ReportPreset',
        }
        cls.registry['Reportpreset_destroy'] = {
            'path': '/report_presets/{id}.json',
            'method': 'DELETE',
            'query_model': Reportpreset_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single ReportPreset',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single ReportPreset',
        }
        cls.registry['Reportschedule_index'] = {
            'path': '/report_schedules.json',
            'method': 'GET',
            'query_model': Reportschedule_index_Query,
            'request_body_model': None,
            'field_model': ReportSchedule_Fields,
            'summary': 'Return the data for all ReportSchedules',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all ReportSchedules',
        }
        cls.registry['Reportschedule_create'] = {
            'path': '/report_schedules.json',
            'method': 'POST',
            'query_model': Reportschedule_create_Query,
            'request_body_model': Reportschedule_create_RequestBody,
            'field_model': ReportSchedule_Fields,
            'summary': 'Create a new ReportSchedule',
            'description': 'Outlines the parameters and data fields used when creating a new ReportSchedule',
        }
        cls.registry['Reportschedule_show'] = {
            'path': '/report_schedules/{id}.json',
            'method': 'GET',
            'query_model': Reportschedule_show_Query,
            'request_body_model': None,
            'field_model': ReportSchedule_Fields,
            'summary': 'Return the data for a single ReportSchedule',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single ReportSchedule',
        }
        cls.registry['Reportschedule_update'] = {
            'path': '/report_schedules/{id}.json',
            'method': 'PATCH',
            'query_model': Reportschedule_update_Query,
            'request_body_model': Reportschedule_update_RequestBody,
            'field_model': ReportSchedule_Fields,
            'summary': 'Update a single ReportSchedule',
            'description': 'Outlines the parameters and data fields used when updating a single ReportSchedule',
        }
        cls.registry['Reportschedule_destroy'] = {
            'path': '/report_schedules/{id}.json',
            'method': 'DELETE',
            'query_model': Reportschedule_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single ReportSchedule',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single ReportSchedule',
        }
        cls.registry['Billingsetting_show'] = {
            'path': '/settings/billing.json',
            'method': 'GET',
            'query_model': Billingsetting_show_Query,
            'request_body_model': None,
            'field_model': BillingSetting_Fields,
            'summary': 'Return the billing settings',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single BillingSetting',
        }
        cls.registry['Textsnippet_index'] = {
            'path': '/settings/text_snippets.json',
            'method': 'GET',
            'query_model': Textsnippet_index_Query,
            'request_body_model': None,
            'field_model': TextSnippet_Fields,
            'summary': 'Return all text snippets',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all TextSnippets',
        }
        cls.registry['Textsnippet_create'] = {
            'path': '/settings/text_snippets.json',
            'method': 'POST',
            'query_model': Textsnippet_create_Query,
            'request_body_model': Textsnippet_create_RequestBody,
            'field_model': TextSnippet_Fields,
            'summary': 'Create a text snippet',
            'description': 'Outlines the parameters and data fields used when creating a new TextSnippet',
        }
        cls.registry['Textsnippet_show'] = {
            'path': '/settings/text_snippets/{id}.json',
            'method': 'GET',
            'query_model': Textsnippet_show_Query,
            'request_body_model': None,
            'field_model': TextSnippet_Fields,
            'summary': 'Return the data for the text snippet',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single TextSnippet',
        }
        cls.registry['Textsnippet_update'] = {
            'path': '/settings/text_snippets/{id}.json',
            'method': 'PATCH',
            'query_model': Textsnippet_update_Query,
            'request_body_model': Textsnippet_update_RequestBody,
            'field_model': TextSnippet_Fields,
            'summary': 'Update a text snippet',
            'description': 'Outlines the parameters and data fields used when updating a single TextSnippet',
        }
        cls.registry['Textsnippet_destroy'] = {
            'path': '/settings/text_snippets/{id}.json',
            'method': 'DELETE',
            'query_model': Textsnippet_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Destroy a text snippet',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single TextSnippet',
        }
        cls.registry['Task_index'] = {
            'path': '/tasks.json',
            'method': 'GET',
            'query_model': Task_index_Query,
            'request_body_model': None,
            'field_model': Task_Fields,
            'summary': 'Return the data for all Tasks',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Tasks',
        }
        cls.registry['Task_create'] = {
            'path': '/tasks.json',
            'method': 'POST',
            'query_model': Task_create_Query,
            'request_body_model': Task_create_RequestBody,
            'field_model': Task_Fields,
            'summary': 'Create a new Task',
            'description': 'Outlines the parameters and data fields used when creating a new Task',
        }
        cls.registry['Task_show'] = {
            'path': '/tasks/{id}.json',
            'method': 'GET',
            'query_model': Task_show_Query,
            'request_body_model': None,
            'field_model': Task_Fields,
            'summary': 'Return the data for a single Task',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Task',
        }
        cls.registry['Task_update'] = {
            'path': '/tasks/{id}.json',
            'method': 'PATCH',
            'query_model': Task_update_Query,
            'request_body_model': Task_update_RequestBody,
            'field_model': Task_Fields,
            'summary': 'Update a single Task',
            'description': 'Outlines the parameters and data fields used when updating a single Task',
        }
        cls.registry['Task_destroy'] = {
            'path': '/tasks/{id}.json',
            'method': 'DELETE',
            'query_model': Task_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Task',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Task',
        }
        cls.registry['Calendarvisibility_index'] = {
            'path': '/task_calendars.json',
            'method': 'GET',
            'query_model': Calendarvisibility_index_Query,
            'request_body_model': None,
            'field_model': CalendarVisibility_Fields,
            'summary': 'Return the data for all CalendarVisibilities',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all CalendarVisibilities',
        }
        cls.registry['Calendarvisibility_show'] = {
            'path': '/task_calendars/{id}.json',
            'method': 'GET',
            'query_model': Calendarvisibility_show_Query,
            'request_body_model': None,
            'field_model': CalendarVisibility_Fields,
            'summary': 'Return the data for a single CalendarVisibility',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single CalendarVisibility',
        }
        cls.registry['Calendarvisibility_update'] = {
            'path': '/task_calendars/{id}.json',
            'method': 'PATCH',
            'query_model': Calendarvisibility_update_Query,
            'request_body_model': Calendarvisibility_update_RequestBody,
            'field_model': CalendarVisibility_Fields,
            'summary': 'Update a single CalendarVisibility',
            'description': 'Outlines the parameters and data fields used when updating a single CalendarVisibility',
        }
        cls.registry['Tasktemplate_index'] = {
            'path': '/task_templates.json',
            'method': 'GET',
            'query_model': Tasktemplate_index_Query,
            'request_body_model': None,
            'field_model': TaskTemplate_Fields,
            'summary': 'Return the data for all TaskTemplates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all TaskTemplates',
        }
        cls.registry['Tasktemplate_create'] = {
            'path': '/task_templates.json',
            'method': 'POST',
            'query_model': Tasktemplate_create_Query,
            'request_body_model': Tasktemplate_create_RequestBody,
            'field_model': TaskTemplate_Fields,
            'summary': 'Create a new TaskTemplate',
            'description': 'Outlines the parameters and data fields used when creating a new TaskTemplate',
        }
        cls.registry['Tasktemplate_show'] = {
            'path': '/task_templates/{id}.json',
            'method': 'GET',
            'query_model': Tasktemplate_show_Query,
            'request_body_model': None,
            'field_model': TaskTemplate_Fields,
            'summary': 'Return the data for a single TaskTemplate',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single TaskTemplate',
        }
        cls.registry['Tasktemplate_update'] = {
            'path': '/task_templates/{id}.json',
            'method': 'PATCH',
            'query_model': Tasktemplate_update_Query,
            'request_body_model': Tasktemplate_update_RequestBody,
            'field_model': TaskTemplate_Fields,
            'summary': 'Update a single TaskTemplate',
            'description': 'Outlines the parameters and data fields used when updating a single TaskTemplate',
        }
        cls.registry['Tasktemplate_destroy'] = {
            'path': '/task_templates/{id}.json',
            'method': 'DELETE',
            'query_model': Tasktemplate_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single TaskTemplate',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single TaskTemplate',
        }
        cls.registry['Tasktemplatelist_copy'] = {
            'path': '/task_template_lists/{id}/copy.json',
            'method': 'POST',
            'query_model': Tasktemplatelist_copy_Query,
            'request_body_model': Tasktemplatelist_copy_RequestBody,
            'field_model': TaskTemplateList_Fields,
            'summary': 'Copy a TaskTemplateList',
            'description': 'Creates a copy of the TaskTemplateList identified by the `id` path parameter.\n',
        }
        cls.registry['Tasktemplatelist_index'] = {
            'path': '/task_template_lists.json',
            'method': 'GET',
            'query_model': Tasktemplatelist_index_Query,
            'request_body_model': None,
            'field_model': TaskTemplateList_Fields,
            'summary': 'Return the data for all TaskTemplateLists',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all TaskTemplateLists',
        }
        cls.registry['Tasktemplatelist_create'] = {
            'path': '/task_template_lists.json',
            'method': 'POST',
            'query_model': Tasktemplatelist_create_Query,
            'request_body_model': Tasktemplatelist_create_RequestBody,
            'field_model': TaskTemplateList_Fields,
            'summary': 'Create a new TaskTemplateList',
            'description': 'Outlines the parameters and data fields used when creating a new TaskTemplateList',
        }
        cls.registry['Tasktemplatelist_show'] = {
            'path': '/task_template_lists/{id}.json',
            'method': 'GET',
            'query_model': Tasktemplatelist_show_Query,
            'request_body_model': None,
            'field_model': TaskTemplateList_Fields,
            'summary': 'Return the data for a single TaskTemplateList',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single TaskTemplateList',
        }
        cls.registry['Tasktemplatelist_update'] = {
            'path': '/task_template_lists/{id}.json',
            'method': 'PATCH',
            'query_model': Tasktemplatelist_update_Query,
            'request_body_model': Tasktemplatelist_update_RequestBody,
            'field_model': TaskTemplateList_Fields,
            'summary': 'Update a single TaskTemplateList',
            'description': 'Outlines the parameters and data fields used when updating a single TaskTemplateList',
        }
        cls.registry['Tasktemplatelist_destroy'] = {
            'path': '/task_template_lists/{id}.json',
            'method': 'DELETE',
            'query_model': Tasktemplatelist_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single TaskTemplateList',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single TaskTemplateList',
        }
        cls.registry['Tasktype_index'] = {
            'path': '/task_types.json',
            'method': 'GET',
            'query_model': Tasktype_index_Query,
            'request_body_model': None,
            'field_model': TaskType_Fields,
            'summary': 'Return the data for all TaskTypes',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all TaskTypes',
        }
        cls.registry['Tasktype_create'] = {
            'path': '/task_types.json',
            'method': 'POST',
            'query_model': Tasktype_create_Query,
            'request_body_model': Tasktype_create_RequestBody,
            'field_model': TaskType_Fields,
            'summary': 'Create a new TaskType',
            'description': 'Outlines the parameters and data fields used when creating a new TaskType',
        }
        cls.registry['Tasktype_show'] = {
            'path': '/task_types/{id}.json',
            'method': 'GET',
            'query_model': Tasktype_show_Query,
            'request_body_model': None,
            'field_model': TaskType_Fields,
            'summary': 'Return the data for a single TaskType',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single TaskType',
        }
        cls.registry['Tasktype_update'] = {
            'path': '/task_types/{id}.json',
            'method': 'PATCH',
            'query_model': Tasktype_update_Query,
            'request_body_model': Tasktype_update_RequestBody,
            'field_model': TaskType_Fields,
            'summary': 'Update a single TaskType',
            'description': 'Outlines the parameters and data fields used when updating a single TaskType',
        }
        cls.registry['Timer_show'] = {
            'path': '/timer.json',
            'method': 'GET',
            'query_model': Timer_show_Query,
            'request_body_model': None,
            'field_model': Timer_Fields,
            'summary': 'Return the data for a single Timer',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Timer',
        }
        cls.registry['Timer_destroy'] = {
            'path': '/timer.json',
            'method': 'DELETE',
            'query_model': Timer_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Timer',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Timer',
        }
        cls.registry['Timer_create'] = {
            'path': '/timer.json',
            'method': 'POST',
            'query_model': Timer_create_Query,
            'request_body_model': Timer_create_RequestBody,
            'field_model': Timer_Fields,
            'summary': 'Create a new Timer',
            'description': 'Outlines the parameters and data fields used when creating a new Timer',
        }
        cls.registry['Trustlineitem_index'] = {
            'path': '/trust_line_items.json',
            'method': 'GET',
            'query_model': Trustlineitem_index_Query,
            'request_body_model': None,
            'field_model': TrustLineItem_Fields,
            'summary': 'Return the data for all TrustLineItems',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all TrustLineItems',
        }
        cls.registry['Trustlineitem_update'] = {
            'path': '/trust_line_items/{id}.json',
            'method': 'PATCH',
            'query_model': Trustlineitem_update_Query,
            'request_body_model': Trustlineitem_update_RequestBody,
            'field_model': TrustLineItem_Fields,
            'summary': 'Update a single TrustLineItem',
            'description': 'Outlines the parameters and data fields used when updating a single TrustLineItem',
        }
        cls.registry['Trustrequest_create'] = {
            'path': '/trust_requests.json',
            'method': 'POST',
            'query_model': Trustrequest_create_Query,
            'request_body_model': Trustrequest_create_RequestBody,
            'field_model': TrustRequest_Fields,
            'summary': 'Create a new TrustRequest',
            'description': 'Outlines the parameters and data fields used when creating a new TrustRequest',
        }
        cls.registry['User_who_am_i'] = {
            'path': '/users/who_am_i.json',
            'method': 'GET',
            'query_model': User_who_am_i_Query,
            'request_body_model': None,
            'field_model': User_Fields,
            'summary': 'Return the data for the current User',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single User',
        }
        cls.registry['User_index'] = {
            'path': '/users.json',
            'method': 'GET',
            'query_model': User_index_Query,
            'request_body_model': None,
            'field_model': User_Fields,
            'summary': 'Return the data for all Users',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Users',
        }
        cls.registry['User_show'] = {
            'path': '/users/{id}.json',
            'method': 'GET',
            'query_model': User_show_Query,
            'request_body_model': None,
            'field_model': User_Fields,
            'summary': 'Return the data for a single User',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single User',
        }
        cls.registry['Utbmsset_index'] = {
            'path': '/utbms/sets.json',
            'method': 'GET',
            'query_model': Utbmsset_index_Query,
            'request_body_model': None,
            'field_model': UtbmsSet_Fields,
            'summary': 'Return the data for all the utbms sets',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all UtbmsSets',
        }
        cls.registry['Utbmscode_index'] = {
            'path': '/utbms/codes.json',
            'method': 'GET',
            'query_model': Utbmscode_index_Query,
            'request_body_model': None,
            'field_model': UtbmsCode_Fields,
            'summary': 'Return the data for all UtbmsCodes',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all UtbmsCodes',
        }
        cls.registry['Utbmscode_show'] = {
            'path': '/utbms/codes/{id}.json',
            'method': 'GET',
            'query_model': Utbmscode_show_Query,
            'request_body_model': None,
            'field_model': UtbmsCode_Fields,
            'summary': 'Return the data for a single UtbmsCode',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single UtbmsCode',
        }
        cls.registry['Webhook_index'] = {
            'path': '/webhooks.json',
            'method': 'GET',
            'query_model': Webhook_index_Query,
            'request_body_model': None,
            'field_model': Webhook_Fields,
            'summary': 'Return the data for all Webhooks',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Webhooks',
        }
        cls.registry['Webhook_create'] = {
            'path': '/webhooks.json',
            'method': 'POST',
            'query_model': Webhook_create_Query,
            'request_body_model': Webhook_create_RequestBody,
            'field_model': Webhook_Fields,
            'summary': 'Create a new Webhook',
            'description': 'Outlines the parameters and data fields used when creating a new Webhook',
        }
        cls.registry['Webhook_show'] = {
            'path': '/webhooks/{id}.json',
            'method': 'GET',
            'query_model': Webhook_show_Query,
            'request_body_model': None,
            'field_model': Webhook_Fields,
            'summary': 'Return the data for a single Webhook',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Webhook',
        }
        cls.registry['Webhook_update'] = {
            'path': '/webhooks/{id}.json',
            'method': 'PATCH',
            'query_model': Webhook_update_Query,
            'request_body_model': Webhook_update_RequestBody,
            'field_model': Webhook_Fields,
            'summary': 'Update a single Webhook',
            'description': 'Outlines the parameters and data fields used when updating a single Webhook',
        }
        cls.registry['Webhook_destroy'] = {
            'path': '/webhooks/{id}.json',
            'method': 'DELETE',
            'query_model': Webhook_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Webhook',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Webhook',
        }
        cls.registry['Laukcivilcertificatedrate_index'] = {
            'path': '/lauk_civil_certificated_rates.json',
            'method': 'GET',
            'query_model': Laukcivilcertificatedrate_index_Query,
            'request_body_model': None,
            'field_model': LaukCivilCertificatedRate_Fields,
            'summary': 'List Civil Certificated Rates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LaukCivilCertificatedRates',
        }
        cls.registry['Laukcivilcontrolledrate_index'] = {
            'path': '/lauk_civil_controlled_rates.json',
            'method': 'GET',
            'query_model': Laukcivilcontrolledrate_index_Query,
            'request_body_model': None,
            'field_model': LaukCivilControlledRate_Fields,
            'summary': 'List Civil Controlled Rates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LaukCivilControlledRates',
        }
        cls.registry['Laukcriminalcontrolledrate_index'] = {
            'path': '/lauk_criminal_controlled_rates.json',
            'method': 'GET',
            'query_model': Laukcriminalcontrolledrate_index_Query,
            'request_body_model': None,
            'field_model': LaukCriminalControlledRate_Fields,
            'summary': 'List Criminal Controlled Rates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LaukCriminalControlledRates',
        }
        cls.registry['Laukexpensecategory_index'] = {
            'path': '/lauk_expense_categories.json',
            'method': 'GET',
            'query_model': Laukexpensecategory_index_Query,
            'request_body_model': None,
            'field_model': LaukExpenseCategory_Fields,
            'summary': 'List Expense Categories',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all LaukExpenseCategories',
        }
        cls.registry['Comment_index'] = {
            'path': '/comments.json',
            'method': 'GET',
            'query_model': Comment_index_Query,
            'request_body_model': None,
            'field_model': Comment_Fields,
            'summary': 'Return the data for all Comments',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Comments',
        }
        cls.registry['Comment_create'] = {
            'path': '/comments.json',
            'method': 'POST',
            'query_model': Comment_create_Query,
            'request_body_model': Comment_create_RequestBody,
            'field_model': Comment_Fields,
            'summary': 'Create a new Comment',
            'description': 'Outlines the parameters and data fields used when creating a new Comment',
        }
        cls.registry['Comment_show'] = {
            'path': '/comments/{id}.json',
            'method': 'GET',
            'query_model': Comment_show_Query,
            'request_body_model': None,
            'field_model': Comment_Fields,
            'summary': 'Return the data for a single Comment',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Comment',
        }
        cls.registry['Comment_update'] = {
            'path': '/comments/{id}.json',
            'method': 'PATCH',
            'query_model': Comment_update_Query,
            'request_body_model': Comment_update_RequestBody,
            'field_model': Comment_Fields,
            'summary': 'Update a single Comment',
            'description': 'Outlines the parameters and data fields used when updating a single Comment',
        }
        cls.registry['Comment_destroy'] = {
            'path': '/comments/{id}.json',
            'method': 'DELETE',
            'query_model': Comment_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Comment',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single Comment',
        }
        cls.registry['Documentarchive_download'] = {
            'path': '/document_archives/{id}/download.json',
            'method': 'GET',
            'query_model': Documentarchive_download_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Download the DocumentArchive',
            'description': 'Download the DocumentArchive',
        }
        cls.registry['Documentarchive_create'] = {
            'path': '/document_archives.json',
            'method': 'POST',
            'query_model': Documentarchive_create_Query,
            'request_body_model': Documentarchive_create_RequestBody,
            'field_model': DocumentArchive_Fields,
            'summary': 'Create a new DocumentArchive',
            'description': 'Outlines the parameters and data fields used when creating a new DocumentArchive',
        }
        cls.registry['Documentarchive_show'] = {
            'path': '/document_archives/{id}.json',
            'method': 'GET',
            'query_model': Documentarchive_show_Query,
            'request_body_model': None,
            'field_model': DocumentArchive_Fields,
            'summary': 'Return the data for a single DocumentArchive',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single DocumentArchive',
        }
        cls.registry['Document_download'] = {
            'path': '/documents/{id}/download.json',
            'method': 'GET',
            'query_model': Document_download_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Download the Document',
            'description': 'Download the Document',
        }
        cls.registry['Document_copy'] = {
            'path': '/documents/{id}/copy.json',
            'method': 'POST',
            'query_model': Document_copy_Query,
            'request_body_model': Document_copy_RequestBody,
            'field_model': Document_Fields,
            'summary': 'Copy a Document',
            'description': 'Copies the latest document version of a Document into a new Document. The parameters `filename` and `name` will be copied from the source Document if none are provided.\n',
        }
        cls.registry['Documentversion_index'] = {
            'path': '/documents/{id}/versions.json',
            'method': 'GET',
            'query_model': Documentversion_index_Query,
            'request_body_model': None,
            'field_model': DocumentVersion_Fields,
            'summary': 'Return the data for all DocumentVersions',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all DocumentVersions',
        }
        cls.registry['Document_index'] = {
            'path': '/documents.json',
            'method': 'GET',
            'query_model': Document_index_Query,
            'request_body_model': None,
            'field_model': Document_Fields,
            'summary': 'Return the data for all Documents',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Documents',
        }
        cls.registry['Document_create'] = {
            'path': '/documents.json',
            'method': 'POST',
            'query_model': Document_create_Query,
            'request_body_model': Document_create_RequestBody,
            'field_model': Document_Fields,
            'summary': 'Create a new Document',
            'description': 'Create a Document, or Create Document Version to an existing Document.\n',
        }
        cls.registry['Document_show'] = {
            'path': '/documents/{id}.json',
            'method': 'GET',
            'query_model': Document_show_Query,
            'request_body_model': None,
            'field_model': Document_Fields,
            'summary': 'Return the data for a single Document',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Document',
        }
        cls.registry['Document_update'] = {
            'path': '/documents/{id}.json',
            'method': 'PATCH',
            'query_model': Document_update_Query,
            'request_body_model': Document_update_RequestBody,
            'field_model': Document_Fields,
            'summary': 'Update a single Document',
            'description': 'Update Document, move Document to another Folder, and/or restore a trashed Document.\n',
        }
        cls.registry['Document_destroy'] = {
            'path': '/documents/{id}.json',
            'method': 'DELETE',
            'query_model': Document_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Document',
            'description': 'Deleting a Document using this method will move it to the trash instead of permanently deleting it. Trashed Documents are permanently deleted after 30 days. The following errors may be returned:\n\n- `409 Conflict`: The Document (or one of its ancestor folders) is currently being modified by another request, and cannot be trashed.\n',
        }
        cls.registry['Documentautomation_index'] = {
            'path': '/document_automations.json',
            'method': 'GET',
            'query_model': Documentautomation_index_Query,
            'request_body_model': None,
            'field_model': DocumentAutomation_Fields,
            'summary': 'Return the data for all DocumentAutomations',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all DocumentAutomations',
        }
        cls.registry['Documentautomation_create'] = {
            'path': '/document_automations.json',
            'method': 'POST',
            'query_model': Documentautomation_create_Query,
            'request_body_model': Documentautomation_create_RequestBody,
            'field_model': DocumentAutomation_Fields,
            'summary': 'Create a new DocumentAutomation',
            'description': 'Outlines the parameters and data fields used when creating a new DocumentAutomation',
        }
        cls.registry['Documentautomation_show'] = {
            'path': '/document_automations/{id}.json',
            'method': 'GET',
            'query_model': Documentautomation_show_Query,
            'request_body_model': None,
            'field_model': DocumentAutomation_Fields,
            'summary': 'Return the data for a single DocumentAutomation',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single DocumentAutomation',
        }
        cls.registry['Documentcategory_index'] = {
            'path': '/document_categories.json',
            'method': 'GET',
            'query_model': Documentcategory_index_Query,
            'request_body_model': None,
            'field_model': DocumentCategory_Fields,
            'summary': 'Return the data for all DocumentCategories',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all DocumentCategories',
        }
        cls.registry['Documentcategory_create'] = {
            'path': '/document_categories.json',
            'method': 'POST',
            'query_model': Documentcategory_create_Query,
            'request_body_model': Documentcategory_create_RequestBody,
            'field_model': DocumentCategory_Fields,
            'summary': 'Create a new DocumentCategory',
            'description': 'Outlines the parameters and data fields used when creating a new DocumentCategory',
        }
        cls.registry['Documentcategory_show'] = {
            'path': '/document_categories/{id}.json',
            'method': 'GET',
            'query_model': Documentcategory_show_Query,
            'request_body_model': None,
            'field_model': DocumentCategory_Fields,
            'summary': 'Return the data for a single DocumentCategory',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single DocumentCategory',
        }
        cls.registry['Documentcategory_update'] = {
            'path': '/document_categories/{id}.json',
            'method': 'PATCH',
            'query_model': Documentcategory_update_Query,
            'request_body_model': Documentcategory_update_RequestBody,
            'field_model': DocumentCategory_Fields,
            'summary': 'Update a single DocumentCategory',
            'description': 'Outlines the parameters and data fields used when updating a single DocumentCategory',
        }
        cls.registry['Documentcategory_destroy'] = {
            'path': '/document_categories/{id}.json',
            'method': 'DELETE',
            'query_model': Documentcategory_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single DocumentCategory',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single DocumentCategory',
        }
        cls.registry['Documenttemplate_download'] = {
            'path': '/document_templates/{id}/download.json',
            'method': 'GET',
            'query_model': Documenttemplate_download_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Get the contents of the DocumentTemplate',
            'description': 'Get the contents of the DocumentTemplate',
        }
        cls.registry['Documenttemplate_index'] = {
            'path': '/document_templates.json',
            'method': 'GET',
            'query_model': Documenttemplate_index_Query,
            'request_body_model': None,
            'field_model': DocumentTemplate_Fields,
            'summary': 'Return the data for all DocumentTemplates',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all DocumentTemplates',
        }
        cls.registry['Documenttemplate_create'] = {
            'path': '/document_templates.json',
            'method': 'POST',
            'query_model': Documenttemplate_create_Query,
            'request_body_model': Documenttemplate_create_RequestBody,
            'field_model': DocumentTemplate_Fields,
            'summary': 'Create a new DocumentTemplate',
            'description': 'Outlines the parameters and data fields used when creating a new DocumentTemplate',
        }
        cls.registry['Documenttemplate_show'] = {
            'path': '/document_templates/{id}.json',
            'method': 'GET',
            'query_model': Documenttemplate_show_Query,
            'request_body_model': None,
            'field_model': DocumentTemplate_Fields,
            'summary': 'Return the data for a single DocumentTemplate',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single DocumentTemplate',
        }
        cls.registry['Documenttemplate_update'] = {
            'path': '/document_templates/{id}.json',
            'method': 'PATCH',
            'query_model': Documenttemplate_update_Query,
            'request_body_model': Documenttemplate_update_RequestBody,
            'field_model': DocumentTemplate_Fields,
            'summary': 'Update a single DocumentTemplate',
            'description': 'Outlines the parameters and data fields used when updating a single DocumentTemplate',
        }
        cls.registry['Documenttemplate_destroy'] = {
            'path': '/document_templates/{id}.json',
            'method': 'DELETE',
            'query_model': Documenttemplate_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single DocumentTemplate',
            'description': 'Outlines the parameters, optional and required, used when deleting the record for a single DocumentTemplate',
        }
        cls.registry['Folder_list'] = {
            'path': '/folders/list.json',
            'method': 'GET',
            'query_model': Folder_list_Query,
            'request_body_model': None,
            'field_model': Item_Fields,
            'summary': 'Return the data of the contents of a Folder',
            'description': 'Return the data of the contents of a Folder.\n',
        }
        cls.registry['Folder_index'] = {
            'path': '/folders.json',
            'method': 'GET',
            'query_model': Folder_index_Query,
            'request_body_model': None,
            'field_model': Folder_Fields,
            'summary': 'Return the data for all Folders',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for all Folders',
        }
        cls.registry['Folder_create'] = {
            'path': '/folders.json',
            'method': 'POST',
            'query_model': Folder_create_Query,
            'request_body_model': Folder_create_RequestBody,
            'field_model': Folder_Fields,
            'summary': 'Create a new Folder',
            'description': 'Create a Folder to an existing folder.\n',
        }
        cls.registry['Folder_show'] = {
            'path': '/folders/{id}.json',
            'method': 'GET',
            'query_model': Folder_show_Query,
            'request_body_model': None,
            'field_model': Folder_Fields,
            'summary': 'Return the data for a single Folder',
            'description': 'Outlines the parameters, optional and required, used when requesting the data for a single Folder',
        }
        cls.registry['Folder_update'] = {
            'path': '/folders/{id}.json',
            'method': 'PATCH',
            'query_model': Folder_update_Query,
            'request_body_model': Folder_update_RequestBody,
            'field_model': Folder_Fields,
            'summary': 'Update a single Folder',
            'description': 'Update Folder, move Folder to another Folder, and/or restore a trashed Folder.\n',
        }
        cls.registry['Folder_destroy'] = {
            'path': '/folders/{id}.json',
            'method': 'DELETE',
            'query_model': Folder_destroy_Query,
            'request_body_model': None,
            'field_model': None,
            'summary': 'Delete a single Folder',
            'description': 'Deleting a Folder using this method will move it to the trash instead of permanently deleting it. Trashed Folders are permanently deleted after 30 days. The following errors may be returned:\n\n- `400 Bad Request`: The Folder cannot be trashed. The `type` of the error will be `DeleteFailed` and the `message` of the error will be one of the following:\n  - `Delete failed: This folder contains more than 100,000 items and cannot be trashed. Please trash some of the items inside it before trying again.`\n  - `Delete failed: This item contains locked items and cannot be deleted.`\n  - `Delete failed: The root folder cannot be trashed`\n- `409 Conflict`: The Folder (or one of its descendants) is currently being modified by another request, and cannot be trashed.\n',
        }

        # Initialize the registry
Endpoints.initialize_registry()
