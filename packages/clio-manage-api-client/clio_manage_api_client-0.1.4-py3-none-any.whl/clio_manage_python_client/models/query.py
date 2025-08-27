from dataclasses import dataclass
from typing import Optional, List, Literal
import datetime

@dataclass
class Activity_index_Query:
    X_API_VERSION: Optional[str] = None
    activity_description_id: Optional[int] = None
    calendar_entry_id: Optional[int] = None
    communication_id: Optional[int] = None
    contact_note_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    expense_category_id: Optional[int] = None
    fields: Optional[str] = None
    flat_rate: Optional[bool] = None
    grant_id: Optional[int] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    matter_note_id: Optional[int] = None
    only_unaccounted_for: Optional[bool] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'display_number(asc)', 'display_number(desc)', 'user.name(asc)', 'user.name(desc)', 'price(asc)', 'price(desc)', 'total(asc)', 'total(desc)', 'type(asc)', 'type(desc)', 'date(asc)', 'date(desc)', 'note(asc)', 'note(desc)', 'updated_at(asc)', 'updated_at(desc)', 'vendor.name(asc)', 'vendor.name(desc)', 'expense_category.name(asc)', 'expense_category.name(desc)', 'non_billable(asc)', 'non_billable(desc)', 'non_billable_total(asc)', 'non_billable_total(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    start_date: Optional[datetime.datetime] = None
    status: Optional[Literal['billed', 'draft', 'unbilled', 'non_billable', 'billable', 'written_off']] = None
    task_id: Optional[int] = None
    type: Optional[Literal['TimeEntry', 'ExpenseEntry', 'HardCostEntry', 'SoftCostEntry']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Activity_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activity_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activity_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activity_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Activityrate_index_Query:
    X_API_VERSION: Optional[str] = None
    co_counsel_contact_id: Optional[int] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Activityrate_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activityrate_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activityrate_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activityrate_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Activitydescription_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    flat_rate: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    rate_for__matter_id: Optional[int] = None
    rate_for__user_id: Optional[int] = None
    type: Optional[Literal['utbms', 'clio']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Activitydescription_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activitydescription_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activitydescription_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Activitydescription_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Allocation_index_Query:
    X_API_VERSION: Optional[str] = None
    bill_id: Optional[int] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'date(asc)', 'date(desc)']] = None
    page_token: Optional[str] = None
    parent_id: Optional[int] = None
    parent_type: Optional[int] = None
    status: Optional[Literal['valid', 'invalid']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Allocation_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Bankaccount_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'institution(asc)', 'institution(desc)', 'account_number(asc)', 'account_number(desc)', 'transit_number(asc)', 'transit_number(desc)', 'currency(asc)', 'currency(desc)', 'updated_at(asc)', 'updated_at(desc)', 'type(asc)', 'type(desc)']] = None
    page_token: Optional[str] = None
    show_empty_accounts: Optional[bool] = None
    type: Optional[Literal['OperatingAccount', 'TrustAccount']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Bankaccount_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Bankaccount_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Bankaccount_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Bankaccount_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Banktransaction_index_Query:
    X_API_VERSION: Optional[str] = None
    bank_account_id: Optional[int] = None
    client_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[str] = None
    page_token: Optional[str] = None
    type: Optional[Literal['asset', 'liability']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Banktransaction_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Banktransfer_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Billtheme_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Billtheme_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Billableclient_index_Query:
    X_API_VERSION: Optional[str] = None
    client_id: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    end_date: Optional[datetime.date] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    originating_attorney_id: Optional[int] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    responsible_attorney_id: Optional[int] = None
    start_date: Optional[datetime.date] = None

@dataclass
class Billablematter_ids_Query:
    X_API_VERSION: Optional[str] = None
    client_id: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    end_date: Optional[datetime.date] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    originating_attorney_id: Optional[int] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    responsible_attorney_id: Optional[int] = None
    start_date: Optional[datetime.date] = None

@dataclass
class Billablematter_index_Query:
    X_API_VERSION: Optional[str] = None
    client_id: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    end_date: Optional[datetime.date] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    originating_attorney_id: Optional[int] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    responsible_attorney_id: Optional[int] = None
    start_date: Optional[datetime.date] = None

@dataclass
class Bill_preview_Query:
    id: int

@dataclass
class Bill_index_Query:
    X_API_VERSION: Optional[str] = None
    client_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    currency_id: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    due_after: Optional[datetime.date] = None
    due_at: Optional[datetime.date] = None
    due_before: Optional[datetime.date] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    issued_after: Optional[datetime.date] = None
    issued_before: Optional[datetime.date] = None
    last_sent_end_date: Optional[datetime.date] = None
    last_sent_start_date: Optional[datetime.date] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'due_at(asc)', 'due_at(desc)', 'issued_at(asc)', 'issued_at(desc)', 'paid_at(asc)', 'paid_at(desc)', 'last_sent_at(asc)', 'last_sent_at(desc)', 'client_name(asc)', 'client_name(desc)', 'matter_display_number(asc)', 'matter_display_number(desc)', 'balance(asc)', 'balance(desc)', 'number(asc)', 'number(desc)']] = None
    originating_attorney_id: Optional[int] = None
    overdue_only: Optional[bool] = None
    page_token: Optional[str] = None
    query: Optional[int] = None
    responsible_attorney_id: Optional[int] = None
    state: Optional[Literal['draft', 'awaiting_approval', 'awaiting_payment', 'paid', 'void', 'deleted']] = None
    status: Optional[Literal['all', 'overdue']] = None
    type: Optional[Literal['revenue', 'trust']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Bill_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None
    navigation_next: Optional[int] = None
    navigation_previous: Optional[int] = None

@dataclass
class Bill_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Bill_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Calendarentry_index_Query:
    X_API_VERSION: Optional[str] = None
    calendar_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    expanded: Optional[bool] = None
    external_property_name: Optional[str] = None
    external_property_value: Optional[str] = None
    fields: Optional[str] = None
    from_: Optional[datetime.datetime] = None
    has_court_rule: Optional[bool] = None
    ids__: Optional[int] = None
    is_all_day: Optional[bool] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    owner_entries_across_all_users: Optional[bool] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    source: Optional[Literal['web', 'mobile']] = None
    to: Optional[datetime.datetime] = None
    updated_since: Optional[datetime.datetime] = None
    visible: Optional[bool] = None

@dataclass
class Calendarentry_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentry_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentry_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentry_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Calendarentryeventtype_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Calendarentryeventtype_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentryeventtype_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentryeventtype_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarentryeventtype_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Calendar_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    filter_inactive_users: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'id(asc)', 'id(desc)']] = None
    owner: Optional[bool] = None
    page_token: Optional[str] = None
    source: Optional[Literal['web', 'mobile']] = None
    type: Optional[Literal['AccountCalendar', 'AdhocCalendar', 'UserCalendar']] = None
    updated_since: Optional[datetime.datetime] = None
    visible: Optional[bool] = None
    writeable: Optional[bool] = None

@dataclass
class Calendar_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendar_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendar_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendar_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Cliopaymentslink_index_Query:
    X_API_VERSION: Optional[str] = None
    active: Optional[bool] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Cliopaymentslink_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Cliopaymentslink_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Cliopaymentslink_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Cliopaymentspayment_index_Query:
    X_API_VERSION: Optional[str] = None
    bill_id: Optional[int] = None
    contact_id: Optional[int] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    state: Optional[Literal['pending', 'authorized', 'completed', 'voided', 'failed', 'canceled', 'requires_confirmation', 'completed_requiring_allocation']] = None

@dataclass
class Cliopaymentspayment_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Communication_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    date: Optional[datetime.date] = None
    external_property_name: Optional[str] = None
    external_property_value: Optional[str] = None
    fields: Optional[str] = None
    having_time_entries: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'date(asc)', 'date(desc)', 'received_at(asc)', 'received_at(desc)', 'matter(asc)', 'matter(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    received_at: Optional[datetime.datetime] = None
    received_before: Optional[datetime.datetime] = None
    received_since: Optional[datetime.datetime] = None
    type: Optional[Literal['EmailCommunication', 'PhoneCommunication']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Communication_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Communication_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Communication_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Communication_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Emailaddress_index_Query:
    contact_id: int
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Phonenumber_index_Query:
    contact_id: int
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Contact_index_Query:
    X_API_VERSION: Optional[str] = None
    client_only: Optional[bool] = None
    clio_connect_only: Optional[bool] = None
    created_since: Optional[datetime.datetime] = None
    custom_field_ids__: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    email_only: Optional[bool] = None
    exclude_ids__: Optional[int] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    initial: Optional[Literal['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'shared_at(asc)', 'shared_at(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    shared_resource_id: Optional[int] = None
    type: Optional[Literal['Company', 'Person']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Contact_create_Query:
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Contact_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Contact_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Contact_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Conversationmessage_index_Query:
    conversation_id: int
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Conversationmessage_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Conversationmessage_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Conversation_index_Query:
    X_API_VERSION: Optional[str] = None
    archived: Optional[bool] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    date: Optional[datetime.date] = None
    fields: Optional[str] = None
    for_user: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'last_message_id(asc)', 'last_message_id(desc)', 'matter_id(asc)', 'matter_id(desc)']] = None
    page_token: Optional[str] = None
    read_status: Optional[bool] = None
    time_entries: Optional[bool] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Conversation_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Conversation_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Jurisdictionstotrigger_index_Query:
    jurisdiction_id: int
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    is_requirements_required: Optional[bool] = None
    is_served: Optional[bool] = None
    limit: Optional[int] = None
    order: Optional[Literal['description(asc)', 'description(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Jurisdictionstotrigger_show_Query:
    id: int
    jurisdiction_id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Jurisdiction_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    for_current_account: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['description(asc)', 'description(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Jurisdiction_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Matterdocket_preview_Query:
    jurisdiction__id: int
    service_type__id: int
    start_date: datetime.datetime
    start_time: datetime.datetime
    trigger__id: int
    event_prefix: Optional[str] = None

@dataclass
class Matterdocket_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    matter_status: Optional[Literal['open', 'closed', 'pending']] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'date(asc)', 'date(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    service_type_id: Optional[int] = None
    status: Optional[Literal['not_started,', 'in_progress,', 'failed,', 'completed']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Matterdocket_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Matterdocket_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Matterdocket_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Servicetype_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['description(asc)', 'description(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Servicetype_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Creditmemo_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'date(asc)', 'date(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Creditmemo_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Currency_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Customfield_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    deleted: Optional[bool] = None
    field_type: Optional[Literal['checkbox', 'contact', 'currency', 'date', 'time', 'email', 'matter', 'numeric', 'picklist', 'text_area', 'text_line', 'url']] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'display_order(asc)', 'display_order(desc)']] = None
    page_token: Optional[str] = None
    parent_type: Optional[Literal['matter', 'contact']] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None
    visible_and_required: Optional[bool] = None

@dataclass
class Customfield_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfield_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfield_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfield_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Customfieldset_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    displayed: Optional[bool] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'id(asc)', 'id(desc)', 'parent_type(asc)', 'parent_type(desc)']] = None
    page_token: Optional[str] = None
    parent_type: Optional[Literal['Matter', 'Contact']] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Customfieldset_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfieldset_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfieldset_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customfieldset_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Customaction_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Customaction_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customaction_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customaction_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Customaction_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Damage_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Damage_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Damage_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Damage_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Damage_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Expensecategory_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    entry_type: Optional[Literal['hard_cost', 'soft_cost', 'unassociated']] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'rate(asc)', 'rate(desc)', 'entry_type(asc)', 'entry_type(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Expensecategory_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Expensecategory_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Expensecategory_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Expensecategory_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Grant_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Grant_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Grant_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Grant_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Grant_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Grantfundingsource_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Grantfundingsource_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Grantfundingsource_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Grantfundingsource_destroy_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Group_index_Query:
    X_API_VERSION: Optional[str] = None
    archived: Optional[bool] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    type: Optional[Literal['AccountGroup', 'AdhocGroup', 'UserGroup']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Group_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Group_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Group_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Group_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Eventmetrics_index_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Myevent_index_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None

@dataclass
class Myevent_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Myevent_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Interestcharge_index_Query:
    X_API_VERSION: Optional[str] = None
    bill_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    exclude_ids__: Optional[int] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Interestcharge_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Lineitem_index_Query:
    X_API_VERSION: Optional[str] = None
    activity_id: Optional[int] = None
    bill_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    display: Optional[bool] = None
    exclude_ids__: Optional[int] = None
    fields: Optional[str] = None
    group_ordering: Optional[int] = None
    ids__: Optional[int] = None
    kind: Optional[str] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Lineitem_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Lineitem_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Logentry_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'accessed_at(asc)', 'accessed_at(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Client_show_Query:
    matter_id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Relatedcontacts_index_Query:
    matter_id: int
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None

@dataclass
class Mattercontacts_index_Query:
    matter_id: int
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None
    limit: Optional[int] = None
    order: Optional[Literal['is_client(asc)', 'is_client(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None

@dataclass
class Matter_index_Query:
    X_API_VERSION: Optional[str] = None
    billable: Optional[bool] = None
    client_id: Optional[int] = None
    close_date__: Optional[Literal['>DATE', '>=DATE', '=DATE', '<=DATE', '<DATE']] = None
    created_since: Optional[datetime.datetime] = None
    currency_id: Optional[int] = None
    custom_field_ids__: Optional[int] = None
    custom_field_values: Optional[Literal['=', '<', '>', '<=', '>=']] = None
    fields: Optional[str] = None
    grant_id: Optional[int] = None
    group_id: Optional[int] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    notification_event_subscriber_user_id: Optional[int] = None
    open_date__: Optional[Literal['>DATE', '>=DATE', '=DATE', '<=DATE', '<DATE']] = None
    order: Optional[Literal['display_number(asc)', 'display_number(desc)', 'custom_number(asc)', 'custom_number(desc)', 'id(asc)', 'id(desc)', 'client.name(asc)', 'client.name(desc)', 'open_date(asc)', 'open_date(desc)', 'practice_area.name(asc)', 'practice_area.name(desc)', 'matter_stage.name(asc)', 'matter_stage.name(desc)', 'responsible_attorney.name(asc)', 'responsible_attorney.name(desc)', 'close_date(asc)', 'close_date(desc)', 'pending_date(asc)', 'pending_date(desc)', 'updated_at(asc)', 'updated_at(desc)', 'created_at(asc)', 'created_at(desc)', 'statute_of_limitations.due_at(asc)', 'statute_of_limitations.due_at(desc)', 'originating_attorney.name(asc)', 'originating_attorney.name(desc)', 'grants(asc)', 'grants(desc)', 'matter_stage_updated_at(asc)', 'matter_stage_updated_at(desc)']] = None
    originating_attorney_id: Optional[int] = None
    page_token: Optional[str] = None
    pending_date__: Optional[Literal['>DATE', '>=DATE', '=DATE', '<=DATE', '<DATE']] = None
    practice_area_id: Optional[int] = None
    query: Optional[str] = None
    responsible_attorney_id: Optional[int] = None
    responsible_staff_id: Optional[int] = None
    status: Optional[Literal['open', 'closed', 'pending']] = None
    subscriber_user_id: Optional[int] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Matter_create_Query:
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Matter_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Matter_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    custom_field_ids__: Optional[int] = None
    fields: Optional[str] = None

@dataclass
class Matter_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Matterstage_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    practice_area_id: Optional[int] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Medicalrecord_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Medicalrecord_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Medicalrecordsrequest_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    treatment_end_date: Optional[datetime.datetime] = None
    treatment_start_date: Optional[datetime.datetime] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Medicalrecordsrequest_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Medicalrecordsrequest_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Medicalrecordsrequest_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Medicalrecordsrequest_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Medicalbill_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Medicalbill_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Note_index_Query:
    type: Literal['Matter', 'Contact']
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    has_time_entries: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'date(asc)', 'date(desc)', 'author(asc)', 'author(desc)', 'updated_at(asc)', 'updated_at(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Note_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Note_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Note_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Note_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Outstandingclientbalance_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    fields: Optional[str] = None
    last_paid_end_date: Optional[datetime.date] = None
    last_paid_start_date: Optional[datetime.date] = None
    limit: Optional[int] = None
    newest_bill_due_end_date: Optional[datetime.date] = None
    newest_bill_due_start_date: Optional[datetime.date] = None
    originating_attorney_id: Optional[int] = None
    page_token: Optional[str] = None
    responsible_attorney_id: Optional[int] = None

@dataclass
class Practicearea_index_Query:
    X_API_VERSION: Optional[str] = None
    code: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    name: Optional[str] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'category(asc)', 'category(desc)', 'code(asc)', 'code(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Practicearea_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Practicearea_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Practicearea_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Practicearea_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Relationship_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Relationship_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Relationship_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Relationship_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Relationship_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Reminder_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    notification_method_id: Optional[int] = None
    order: Optional[Literal['next_delivery_at(asc)', 'next_delivery_at(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    state: Optional[Literal['initializing', 'scheduling', 'rescheduling', 'scheduled', 'attempting_delivery', 'delivery_failed', 'delivered', 'delivery_skipped', 'invalid_user']] = None
    subject_id: Optional[int] = None
    subject_type: Optional[Literal['calendar_entry', 'task']] = None
    updated_since: Optional[datetime.datetime] = None
    user_id: Optional[int] = None

@dataclass
class Reminder_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reminder_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reminder_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reminder_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Report_download_Query:
    id: int

@dataclass
class Report_index_Query:
    X_API_VERSION: Optional[str] = None
    category: Optional[str] = None
    created_before: Optional[datetime.datetime] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    kind: Optional[Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']] = None
    limit: Optional[int] = None
    output_format: Optional[str] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    source: Optional[str] = None
    state: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Report_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Report_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportpreset_generate_report_Query:
    id: int

@dataclass
class Reportpreset_index_Query:
    X_API_VERSION: Optional[str] = None
    category: Optional[Literal['billing', 'client', 'compliance', 'financial', 'matter', 'online_payments', 'productivity', 'revenue', 'task']] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    has_schedule: Optional[bool] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['created_at(asc)', 'created_at(desc)', 'last_generated_at(asc)', 'last_generated_at(desc)', 'last_modified_at(asc)', 'last_modified_at(desc)', 'name(asc)', 'name(desc)', 'next_scheduled_date(asc)', 'next_scheduled_date(desc)']] = None
    output_format: Optional[str] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    schedule_frequency: Optional[Literal['daily', 'weekly', 'monthly']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Reportpreset_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportpreset_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportpreset_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportpreset_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Reportschedule_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Reportschedule_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportschedule_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportschedule_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Reportschedule_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Billingsetting_show_Query:
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    duration: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Textsnippet_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'snippet(asc)', 'snippet(desc)', 'phrase(asc)', 'phrase(desc)', 'whole_word(asc)', 'whole_word(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Textsnippet_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Textsnippet_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Textsnippet_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Textsnippet_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Task_index_Query:
    X_API_VERSION: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_type: Optional[Literal['user', 'contact']] = None
    assigner_id: Optional[int] = None
    cascading_source_id: Optional[int] = None
    client_id: Optional[int] = None
    complete: Optional[bool] = None
    created_since: Optional[datetime.datetime] = None
    due_at_from: Optional[datetime.date] = None
    due_at_present: Optional[bool] = None
    due_at_to: Optional[datetime.date] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'task_type.name(asc)', 'task_type.name(desc)', 'id(asc)', 'id(desc)', 'priority(asc)', 'priority(desc)', 'matter.display_number(asc)', 'matter.display_number(desc)', 'due_at(asc)', 'due_at(desc)', 'due_at_strict(asc)', 'due_at_strict(desc)', 'completed_at(asc)', 'completed_at(desc)']] = None
    page_token: Optional[str] = None
    permission: Optional[Literal['private', 'public']] = None
    priority: Optional[Literal['high', 'normal', 'low']] = None
    query: Optional[str] = None
    responsible_attorney_id: Optional[int] = None
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    statuses__: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    statute_of_limitations: Optional[bool] = None
    task_type_id: Optional[int] = None
    time_entries_present: Optional[bool] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Task_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Task_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Task_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Task_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Calendarvisibility_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Calendarvisibility_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Calendarvisibility_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplate_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['assignee.name(asc)', 'assignee.name(desc)', 'days_from_assignment(asc)', 'days_from_assignment(desc)', 'id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'permission(asc)', 'permission(desc)', 'priority(asc)', 'priority(desc)']] = None
    page_token: Optional[str] = None
    priority: Optional[Literal['high', 'normal', 'low']] = None
    query: Optional[str] = None
    task_template_list_id: Optional[int] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Tasktemplate_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplate_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplate_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplate_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Tasktemplatelist_copy_Query:
    id: int
    fields: Optional[str] = None

@dataclass
class Tasktemplatelist_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    empty: Optional[bool] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'practice_area.name(asc)', 'practice_area.name(desc)']] = None
    page_token: Optional[str] = None
    practice_area_id: Optional[int] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Tasktemplatelist_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplatelist_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplatelist_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktemplatelist_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Tasktype_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    enabled: Optional[bool] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Tasktype_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktype_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Tasktype_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Timer_show_Query:
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Timer_destroy_Query:
    X_API_VERSION: Optional[str] = None

@dataclass
class Timer_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Trustlineitem_index_Query:
    X_API_VERSION: Optional[str] = None
    bill_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Trustlineitem_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Trustrequest_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class User_who_am_i_Query:
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class User_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    enabled: Optional[bool] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    include_co_counsel: Optional[bool] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    order: Optional[Literal['email(asc)', 'email(desc)', 'enabled(asc)', 'enabled(desc)', 'id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'first_name(asc)', 'first_name(desc)', 'last_name(asc)', 'last_name(desc)', 'initials(asc)', 'initials(desc)', 'subscription_type(asc)', 'subscription_type(desc)']] = None
    page_token: Optional[str] = None
    pending_setup: Optional[bool] = None
    role: Optional[Literal['admin', 'accounts', 'billing', 'reports']] = None
    subscription_type: Optional[Literal['attorney', 'nonattorney']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class User_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Utbmsset_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Utbmscode_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['name(asc)', 'name(desc)', 'id(asc)', 'id(desc)', 'set(asc)', 'set(desc)']] = None
    page_token: Optional[str] = None
    type: Optional[Literal['UtbmsTask', 'UtbmsActivity', 'UtbmsExpense']] = None
    updated_since: Optional[datetime.datetime] = None
    utbms_set_id: Optional[int] = None

@dataclass
class Utbmscode_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Webhook_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Webhook_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Webhook_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Webhook_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Webhook_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Laukcivilcertificatedrate_index_Query:
    X_API_VERSION: Optional[str] = None
    activity: Optional[str] = None
    activity_sub_category: Optional[str] = None
    attended_several_hearings_for_multiple_clients: Optional[bool] = None
    category_of_law: Optional[str] = None
    change_of_solicitor: Optional[bool] = None
    court: Optional[str] = None
    eligible_for_sqm: Optional[bool] = None
    fee_scheme: Optional[str] = None
    fields: Optional[str] = None
    first_conducting_solicitor: Optional[bool] = None
    key: Optional[str] = None
    limit: Optional[int] = None
    number_of_clients: Optional[str] = None
    page_token: Optional[str] = None
    party: Optional[str] = None
    post_transfer_clients_represented: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None
    session_type: Optional[str] = None
    user_type: Optional[str] = None

@dataclass
class Laukcivilcontrolledrate_index_Query:
    X_API_VERSION: Optional[str] = None
    activity: Optional[str] = None
    category_of_law: Optional[str] = None
    fields: Optional[str] = None
    key: Optional[str] = None
    limit: Optional[int] = None
    matter_type_1: Optional[int] = None
    matter_type_2: Optional[int] = None
    page_token: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None

@dataclass
class Laukcriminalcontrolledrate_index_Query:
    X_API_VERSION: Optional[str] = None
    activity: Optional[str] = None
    category_of_law: Optional[str] = None
    counsel: Optional[str] = None
    court: Optional[str] = None
    fields: Optional[str] = None
    key: Optional[str] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None
    solicitor_type: Optional[str] = None
    standard_fee_category: Optional[str] = None

@dataclass
class Laukexpensecategory_index_Query:
    region: str
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None
    key: Optional[str] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    page_token: Optional[str] = None
    practice_area: Optional[str] = None

@dataclass
class Comment_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    item_id: Optional[int] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Comment_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Comment_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Comment_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Comment_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Documentarchive_download_Query:
    id: int

@dataclass
class Documentarchive_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentarchive_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Document_download_Query:
    id: int
    document_version_id: Optional[int] = None

@dataclass
class Document_copy_Query:
    id: int
    fields: Optional[str] = None

@dataclass
class Documentversion_index_Query:
    id: int
    id: int
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None
    fully_uploaded: Optional[bool] = None
    limit: Optional[int] = None
    page_token: Optional[str] = None

@dataclass
class Document_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    document_category_id: Optional[int] = None
    external_property_name: Optional[str] = None
    external_property_value: Optional[str] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    include_deleted: Optional[bool] = None
    limit: Optional[int] = None
    locked: Optional[bool] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['created_at(asc)', 'created_at(desc)', 'document_number(asc)', 'document_number(desc)', 'id(asc)', 'id(desc)', 'name(asc)', 'name(desc)', 'received_at(asc)', 'received_at(desc)', 'updated_at(asc)', 'updated_at(desc)']] = None
    page_token: Optional[str] = None
    parent_id: Optional[int] = None
    query: Optional[str] = None
    scope: Optional[Literal['descendants', 'children']] = None
    show_uncompleted: Optional[bool] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Document_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Document_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Document_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Document_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Documentautomation_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Documentautomation_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentautomation_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentcategory_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)']] = None
    page_token: Optional[str] = None
    query: Optional[Literal['name']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Documentcategory_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentcategory_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentcategory_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documentcategory_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Documenttemplate_download_Query:
    id: int

@dataclass
class Documenttemplate_index_Query:
    X_API_VERSION: Optional[str] = None
    created_since: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    limit: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'filename(asc)', 'filename(desc)', 'category.name(asc)', 'category.name(desc)', 'last_modified(asc)', 'last_modified(desc)', 'last_modified_by.name(asc)', 'last_modified_by.name(desc)']] = None
    page_token: Optional[str] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Documenttemplate_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documenttemplate_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documenttemplate_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Documenttemplate_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

@dataclass
class Folder_list_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    document_category_id: Optional[int] = None
    external_property_name: Optional[str] = None
    external_property_value: Optional[str] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    include_deleted: Optional[bool] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'document_number(asc)', 'document_number(desc)', 'name(asc)', 'name(desc)', 'updated_at(asc)', 'updated_at(desc)', 'created_at(asc)', 'created_at(desc)', 'received_at(asc)', 'received_at(desc)']] = None
    page_token: Optional[str] = None
    parent_id: Optional[int] = None
    query: Optional[str] = None
    scope: Optional[Literal['descendants', 'children']] = None
    show_uncompleted: Optional[bool] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Folder_index_Query:
    X_API_VERSION: Optional[str] = None
    contact_id: Optional[int] = None
    created_since: Optional[datetime.datetime] = None
    document_category_id: Optional[int] = None
    external_property_name: Optional[str] = None
    external_property_value: Optional[str] = None
    fields: Optional[str] = None
    ids__: Optional[int] = None
    include_deleted: Optional[bool] = None
    limit: Optional[int] = None
    matter_id: Optional[int] = None
    order: Optional[Literal['id(asc)', 'id(desc)', 'name(asc)', 'name(desc)']] = None
    page_token: Optional[str] = None
    parent_id: Optional[int] = None
    query: Optional[str] = None
    scope: Optional[Literal['descendants', 'children']] = None
    updated_since: Optional[datetime.datetime] = None

@dataclass
class Folder_create_Query:
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Folder_show_Query:
    id: int
    IF_MODIFIED_SINCE: Optional[datetime.date] = None
    IF_NONE_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Folder_update_Query:
    id: int
    IF_MATCH: Optional[str] = None
    X_API_VERSION: Optional[str] = None
    fields: Optional[str] = None

@dataclass
class Folder_destroy_Query:
    id: int
    X_API_VERSION: Optional[str] = None

