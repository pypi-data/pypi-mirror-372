from dataclasses import dataclass
from typing import Optional, List, Literal, Any
import datetime

@dataclass
class Comment_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class DocumentArchive_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    size: Optional[int] = None
    progress: Optional[float] = None
    state: Optional[Literal['not_started', 'queued', 'in_progress', 'completed', 'failed']] = None
    message: Optional[str] = None

@dataclass
class DocumentAutomation_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    state: Optional[Literal['not_started', 'queued', 'in_progress', 'empty', 'failed', 'completed']] = None
    export_formats: Optional[Literal['pdf', 'original']] = None
    filename: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class DocumentCategory_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Document_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None
    type: Optional[Literal['Document']] = None
    locked: Optional[bool] = None
    name: Optional[str] = None
    received_at: Optional[datetime.datetime] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None

@dataclass
class DocumentTemplate_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    filename: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class DocumentVersion_base:
    id: Optional[int] = None
    document_id: Optional[int] = None
    etag: Optional[str] = None
    uuid: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    version_number: Optional[int] = None
    content_type: Optional[str] = None
    received_at: Optional[datetime.datetime] = None
    put_url: Optional[str] = None
    fully_uploaded: Optional[bool] = None

@dataclass
class Folder_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None
    type: Optional[Literal['Folder']] = None
    locked: Optional[bool] = None
    name: Optional[str] = None
    root: Optional[bool] = None

@dataclass
class Item_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None
    type: Optional[Literal['Document', 'Folder']] = None
    locked: Optional[bool] = None
    name: Optional[str] = None

@dataclass
class Account_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class ActivityDescription_base_Currency:
    pass

@dataclass
class ActivityDescription_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    visible_to_co_counsel: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    default: Optional[bool] = None
    type: Optional[str] = None
    utbms_activity_id: Optional[int] = None
    utbms_task_name: Optional[str] = None
    utbms_task_id: Optional[int] = None
    xero_service_code: Optional[str] = None
    accessible_to_user: Optional[bool] = None
    category_type: Optional[str] = None
    currency: Optional[ActivityDescription_base_Currency] = None

@dataclass
class ActivityRate_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    rate: Optional[float] = None
    flat_rate: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    contact_id: Optional[int] = None
    co_counsel_contact_id: Optional[int] = None

@dataclass
class Activity_base_Currency:
    pass

@dataclass
class Activity_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['TimeEntry', 'ExpenseEntry', 'HardCostEntry', 'SoftCostEntry']] = None
    date: Optional[datetime.date] = None
    quantity_in_hours: Optional[float] = None
    rounded_quantity_in_hours: Optional[float] = None
    quantity: Optional[float] = None
    rounded_quantity: Optional[float] = None
    quantity_redacted: Optional[bool] = None
    price: Optional[float] = None
    note: Optional[str] = None
    flat_rate: Optional[bool] = None
    billed: Optional[bool] = None
    on_bill: Optional[bool] = None
    total: Optional[float] = None
    contingency_fee: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    reference: Optional[str] = None
    non_billable: Optional[bool] = None
    non_billable_total: Optional[float] = None
    no_charge: Optional[bool] = None
    tax_setting: Optional[Literal['no_tax', 'tax_1_only', 'tax_2_only', 'tax_1_and_tax_2']] = None
    currency: Optional[Activity_base_Currency] = None

@dataclass
class Activity_CalendarEntry_base:
    id: Optional[str] = None
    etag: Optional[str] = None
    calendar_owner_id: Optional[int] = None

@dataclass
class Activity_Task_base:
    id: Optional[int] = None
    etag: Optional[str] = None

@dataclass
class Activity_TextMessageConversation_base:
    id: Optional[int] = None
    etag: Optional[str] = None

@dataclass
class Address_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    name: Optional[Literal['Work', 'Home', 'Billing', 'Other']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    primary: Optional[bool] = None

@dataclass
class Allocation_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    date: Optional[datetime.date] = None
    amount: Optional[float] = None
    interest: Optional[bool] = None
    voided_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    description: Optional[str] = None
    has_online_payment: Optional[bool] = None
    destroyable: Optional[bool] = None
    payment_type: Optional[str] = None

@dataclass
class Balance_base:
    id: Optional[int] = None
    amount: Optional[float] = None
    type: Optional[Literal['Matter', 'Client']] = None
    interest_amount: Optional[float] = None
    due: Optional[float] = None

@dataclass
class BankAccount_base:
    account_number: Optional[str] = None
    balance: Optional[float] = None
    bank_transactions_count: Optional[int] = None
    clio_payment_page_link: Optional[str] = None
    clio_payment_page_qr_code: Optional[str] = None
    clio_payments_enabled: Optional[bool] = None
    controlled_account: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    currency: Optional[str] = None
    currency_symbol: Optional[str] = None
    currency_id: Optional[float] = None
    default_account: Optional[bool] = None
    domicile_branch: Optional[str] = None
    etag: Optional[str] = None
    general_ledger_number: Optional[str] = None
    holder: Optional[str] = None
    id: Optional[int] = None
    institution: Optional[str] = None
    name: Optional[str] = None
    swift: Optional[str] = None
    transit_number: Optional[str] = None
    type: Optional[Literal['Operating', 'Trust']] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class BankTransaction_base:
    id: Optional[int] = None
    type: Optional[str] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    bank_account_id: Optional[int] = None
    source: Optional[str] = None
    confirmation: Optional[str] = None
    date: Optional[datetime.date] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    currency_id: Optional[int] = None
    description: Optional[str] = None
    exchange_rate: Optional[float] = None
    transaction_type: Optional[str] = None
    funds_in: Optional[float] = None
    funds_out: Optional[float] = None
    clio_payments_transaction: Optional[bool] = None
    current_account_balance: Optional[float] = None
    read_only_confirmation: Optional[bool] = None

@dataclass
class BankTransfer_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime.datetime] = None
    description: Optional[str] = None
    primary_authorizer: Optional[str] = None
    secondary_authorizer: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Bill_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    number: Optional[str] = None
    issued_at: Optional[datetime.date] = None
    created_at: Optional[datetime.datetime] = None
    due_at: Optional[datetime.date] = None
    tax_rate: Optional[float] = None
    secondary_tax_rate: Optional[float] = None
    updated_at: Optional[datetime.datetime] = None
    subject: Optional[str] = None
    purchase_order: Optional[str] = None
    type: Optional[Literal['MatterBill', 'ClientBill']] = None
    memo: Optional[str] = None
    start_at: Optional[datetime.date] = None
    end_at: Optional[datetime.date] = None
    balance: Optional[float] = None
    state: Optional[Literal['draft', 'awaiting_approval', 'awaiting_payment', 'paid', 'void', 'deleted']] = None
    kind: Optional[Literal['revenue_kind', 'summary_kind', 'trust_kind', 'aggregate_all', 'aggregate_split', 'aggregate_services', 'aggregate_expenses']] = None
    total: Optional[float] = None
    paid: Optional[float] = None
    paid_at: Optional[datetime.datetime] = None
    pending: Optional[float] = None
    due: Optional[float] = None
    discount_services_only: Optional[str] = None
    can_update: Optional[bool] = None
    credits_issued: Optional[float] = None
    shared: Optional[bool] = None
    last_sent_at: Optional[datetime.datetime] = None
    services_secondary_tax: Optional[float] = None
    services_sub_total: Optional[float] = None
    services_tax: Optional[float] = None
    services_taxable_sub_total: Optional[int] = None
    services_secondary_taxable_sub_total: Optional[int] = None
    taxable_sub_total: Optional[int] = None
    secondary_taxable_sub_total: Optional[int] = None
    sub_total: Optional[float] = None
    tax_sum: Optional[float] = None
    secondary_tax_sum: Optional[float] = None
    total_tax: Optional[float] = None
    available_state_transitions: Optional[List[Literal['awaiting_approval', 'awaiting_payment', 'paid', 'void', 'deleted']]] = None

@dataclass
class BillTheme_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    account_id: Optional[int] = None
    default: Optional[bool] = None
    name: Optional[str] = None
    config: Optional[str] = None

@dataclass
class BillableClient_base:
    id: Optional[int] = None
    unbilled_hours: Optional[float] = None
    unbilled_amount: Optional[float] = None
    amount_in_trust: Optional[float] = None
    name: Optional[str] = None
    billable_matters_count: Optional[int] = None

@dataclass
class BillableMatter_base:
    currency_code: Optional[str] = None
    currency_id: Optional[int] = None
    id: Optional[int] = None
    unbilled_hours: Optional[float] = None
    unbilled_amount: Optional[float] = None
    amount_in_trust: Optional[float] = None
    display_number: Optional[str] = None

@dataclass
class CalendarEntryEventType_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    name: Optional[str] = None

@dataclass
class CalendarEntry_base:
    id: Optional[str] = None
    etag: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_at: Optional[datetime.datetime] = None
    end_at: Optional[datetime.datetime] = None
    all_day: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    parent_calendar_entry_id: Optional[int] = None
    court_rule: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    permission: Optional[str] = None
    calendar_owner_id: Optional[int] = None
    start_at_time_zone: Optional[str] = None
    time_entries_count: Optional[int] = None

@dataclass
class Calendar_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    light_color: Optional[Literal['#5DA5C7', '#F95957', '#209412', '#FF7715', '#DE649D', '#FF6B02', '#56C4FC', '#00B177', '#50D19B', '#F14A8C', '#A3A2A2', '#84AB3B', '#B091EE', '#BD9E69', '#F2A000', '#00A5CA', '#CB5A3D', '#959CD0', '#B0B0B0', '#7BA6CD']] = None
    court_rules_default_calendar: Optional[bool] = None
    name: Optional[str] = None
    permission: Optional[Literal['owner', 'editor', 'viewer', 'limited_viewer', 'none']] = None
    type: Optional[Literal['AccountCalendar', 'AdhocCalendar', 'UserCalendar']] = None
    visible: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    source: Optional[Literal['web', 'mobile']] = None

@dataclass
class ClioPaymentsLink_base:
    active: Optional[bool] = None
    amount: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    email_address: Optional[str] = None
    etag: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None
    id: Optional[int] = None
    is_allocated_as_revenue: Optional[bool] = None
    redirect_url: Optional[str] = None
    url: Optional[str] = None

@dataclass
class ClioPaymentsPayment_base:
    amount: Optional[float] = None
    confirmation_number: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    currency: Optional[str] = None
    deposit_as_revenue: Optional[bool] = None
    description: Optional[str] = None
    email_address: Optional[str] = None
    id: Optional[int] = None
    state: Optional[Literal['pending', 'authorized', 'completed', 'voided', 'failed', 'canceled', 'requires_confirmation', 'completed_requiring_allocation']] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Communication_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    type: Optional[Literal['EmailCommunication', 'PhoneCommunication']] = None
    date: Optional[datetime.date] = None
    time_entries_count: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    received_at: Optional[datetime.datetime] = None

@dataclass
class Contact_base_Currency:
    pass

@dataclass
class Contact_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    type: Optional[Literal['Company', 'Person']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    prefix: Optional[str] = None
    title: Optional[str] = None
    initials: Optional[str] = None
    clio_connect_email: Optional[str] = None
    locked_clio_connect_email: Optional[bool] = None
    client_connect_user_id: Optional[int] = None
    primary_email_address: Optional[str] = None
    secondary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    ledes_client_id: Optional[str] = None
    has_clio_for_clients_permission: Optional[bool] = None
    is_client: Optional[bool] = None
    is_clio_for_client_user: Optional[bool] = None
    is_co_counsel: Optional[bool] = None
    is_bill_recipient: Optional[bool] = None
    sales_tax_number: Optional[str] = None
    currency: Optional[Contact_base_Currency] = None

@dataclass
class ConversationMessage_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    date: Optional[str] = None
    body: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Conversation_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    archived: Optional[bool] = None
    read_only: Optional[bool] = None
    current_user_is_member: Optional[bool] = None
    subject: Optional[str] = None
    message_count: Optional[int] = None
    time_entries_count: Optional[int] = None
    read: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Jurisdiction_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    system_id: Optional[int] = None
    description: Optional[str] = None
    default: Optional[bool] = None
    display_timezone: Optional[str] = None
    valid_subscription: Optional[bool] = None
    is_local_timezone: Optional[bool] = None

@dataclass
class JurisdictionsToTrigger_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    system_id: Optional[int] = None
    description: Optional[str] = None
    do_not_recalculate: Optional[bool] = None
    is_served: Optional[bool] = None
    is_requirements_required: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MatterDocket_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    start_date: Optional[datetime.date] = None
    start_time: Optional[datetime.datetime] = None
    status: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None

@dataclass
class ServiceType_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    system_id: Optional[int] = None
    description: Optional[str] = None
    default: Optional[bool] = None

@dataclass
class CreditMemo_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    date: Optional[datetime.date] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    discount: Optional[bool] = None
    voided_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Currency_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    code: Optional[str] = None
    sign: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class CustomAction_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    label: Optional[str] = None
    target_url: Optional[str] = None
    ui_reference: Optional[Literal['activities/show', 'documents/show', 'contacts/show', 'matters/show', 'folders/show']] = None

@dataclass
class CustomField_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    parent_type: Optional[Literal['Contact', 'Matter']] = None
    field_type: Optional[Literal['checkbox', 'contact', 'currency', 'date', 'time', 'email', 'matter', 'numeric', 'picklist', 'text_area', 'text_line', 'url']] = None
    displayed: Optional[bool] = None
    deleted: Optional[bool] = None
    required: Optional[bool] = None
    display_order: Optional[int] = None

@dataclass
class CustomFieldSet_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    parent_type: Optional[Literal['Contact', 'Matter']] = None
    displayed: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class EmailAddress_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    address: Optional[str] = None
    name: Optional[str] = None
    primary: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class ExpenseCategory_base_Currency:
    pass

@dataclass
class ExpenseCategory_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[int] = None
    entry_type: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    xero_expense_code: Optional[str] = None
    accessible_to_user: Optional[bool] = None
    tax_setting: Optional[str] = None
    currency: Optional[ExpenseCategory_base_Currency] = None

@dataclass
class GrantFundingSource_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Grant_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    funding_code: Optional[str] = None
    funding_code_and_name: Optional[str] = None
    funding_source_name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    balance: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None

@dataclass
class Group_base:
    client_connect_user: Optional[bool] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[Literal['UserGroup', 'AdhocGroup', 'AccountGroup', 'TeamGroup']] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class InterestCharge_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    total: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Interest_base:
    balance: Optional[float] = None
    period: Optional[int] = None
    rate: Optional[float] = None
    total: Optional[float] = None
    type: Optional[Literal['simple', 'compound']] = None

@dataclass
class EventMetrics_base:
    unread_mobile_events: Optional[int] = None
    unread_web_events: Optional[int] = None
    unread_secure_messages: Optional[int] = None
    unread_client_portal_messages: Optional[int] = None
    unread_text_messages: Optional[int] = None

@dataclass
class MyEvent_base:
    pass

@dataclass
class Event_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    message: Optional[str] = None
    icon: Optional[str] = None
    title: Optional[str] = None
    title_url: Optional[str] = None
    description: Optional[str] = None
    description_url: Optional[str] = None
    primary_detail: Optional[str] = None
    primary_detail_url: Optional[str] = None
    secondary_detail: Optional[str] = None
    secondary_detail_url: Optional[str] = None
    occurred_at: Optional[datetime.datetime] = None
    mobile_icon: Optional[str] = None
    subject_type: Optional[str] = None
    subject_id: Optional[int] = None

@dataclass
class LaukCivilCertificatedRate_base:
    id: Optional[int] = None
    activity: Optional[str] = None
    activity_sub_category: Optional[str] = None
    activity_type: Optional[str] = None
    attended_several_hearings_for_multiple_clients: Optional[bool] = None
    category_of_law: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    change_of_solicitor: Optional[bool] = None
    court: Optional[str] = None
    eligible_for_sqm: Optional[bool] = None
    exceptional: Optional[float] = None
    exceptional_warning: Optional[str] = None
    etag: Optional[str] = None
    fee: Optional[float] = None
    fee_scheme: Optional[str] = None
    first_conducting_solicitor: Optional[bool] = None
    key: Optional[str] = None
    number_of_clients: Optional[str] = None
    party: Optional[str] = None
    post_transfer_clients_represented: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None
    session_type: Optional[str] = None
    user_type: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LaukCivilControlledRate_base:
    id: Optional[int] = None
    activity: Optional[str] = None
    activity_type: Optional[str] = None
    category_of_law: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    exceptional: Optional[float] = None
    fee: Optional[float] = None
    fee_scheme: Optional[str] = None
    key: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LaukCriminalControlledRate_base:
    id: Optional[int] = None
    activity: Optional[str] = None
    activity_type: Optional[str] = None
    category_of_law: Optional[str] = None
    counsel: Optional[str] = None
    court: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    exceptional: Optional[float] = None
    fee: Optional[float] = None
    fee_scheme: Optional[str] = None
    post_nov_24_exceptional: Optional[float] = None
    post_nov_24_fee: Optional[float] = None
    post_sept_22_exceptional: Optional[float] = None
    post_sept_22_fee: Optional[float] = None
    key: Optional[str] = None
    rate_type: Optional[str] = None
    region: Optional[str] = None
    solicitor_type: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LaukExpenseCategory_base:
    certificated: Optional[bool] = None
    civil: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    criminal: Optional[bool] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    key: Optional[str] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LineItem_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['ActivityLineItem', 'LineItem', 'NoChargeLineItem', 'SummaryLineItem']] = None
    description: Optional[str] = None
    date: Optional[datetime.date] = None
    price: Optional[float] = None
    taxable: Optional[bool] = None
    kind: Optional[Literal['Service', 'Expense']] = None
    note: Optional[str] = None
    secondary_taxable: Optional[bool] = None
    total: Optional[float] = None
    tax: Optional[float] = None
    secondary_tax: Optional[float] = None
    sub_total: Optional[float] = None
    quantity: Optional[float] = None
    group_ordering: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LogEntry_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['MatterLogEntry', 'ContactLogEntry']] = None
    accessed_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Matter_base_Currency:
    pass

@dataclass
class Matter_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    number: Optional[int] = None
    display_number: Optional[str] = None
    custom_number: Optional[str] = None
    currency: Optional[Matter_base_Currency] = None
    description: Optional[str] = None
    status: Optional[Literal['Pending', 'Open', 'Closed']] = None
    location: Optional[str] = None
    client_reference: Optional[str] = None
    client_id: Optional[int] = None
    billable: Optional[bool] = None
    maildrop_address: Optional[str] = None
    billing_method: Optional[Literal['flat', 'contingency', 'hourly']] = None
    open_date: Optional[datetime.date] = None
    close_date: Optional[datetime.date] = None
    pending_date: Optional[datetime.date] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    shared: Optional[bool] = None
    has_tasks: Optional[bool] = None
    last_activity_date: Optional[datetime.date] = None
    matter_stage_updated_at: Optional[datetime.datetime] = None

@dataclass
class MatterStage_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    practice_area_id: Optional[str] = None
    name: Optional[str] = None
    order: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Client_base:
    id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[Literal['Company', 'Person']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    prefix: Optional[str] = None
    title: Optional[str] = None
    initials: Optional[str] = None
    is_matter_client: Optional[bool] = None
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    client_connect_user_id: Optional[int] = None
    date_of_birth: Optional[datetime.date] = None

@dataclass
class MatterContacts_base:
    contact_created_at: Optional[datetime.datetime] = None
    contact_updated_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    description: Optional[str] = None
    etag: Optional[str] = None
    first_name: Optional[str] = None
    id: Optional[int] = None
    initials: Optional[str] = None
    is_client: Optional[bool] = None
    last_name: Optional[str] = None
    matter_id: Optional[int] = None
    matter_number: Optional[str] = None
    middle_name: Optional[str] = None
    name: Optional[str] = None
    prefix: Optional[str] = None
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    relationship_name: Optional[str] = None
    secondary_email_address: Optional[str] = None
    secondary_phone_number: Optional[str] = None
    title: Optional[str] = None
    type: Optional[Literal['Company', 'Person']] = None
    updated_at: Optional[datetime.datetime] = None
    client_connect_user_id: Optional[int] = None

@dataclass
class RelatedContacts_base:
    id: Optional[int] = None
    contact_id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[Literal['Company', 'Person']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    prefix: Optional[str] = None
    title: Optional[str] = None
    initials: Optional[str] = None
    is_matter_client: Optional[bool] = None
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    client_connect_user_id: Optional[int] = None

@dataclass
class Note_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['Matter', 'Contact']] = None
    subject: Optional[str] = None
    detail: Optional[str] = None
    detail_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    date: Optional[datetime.date] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    time_entries_count: Optional[int] = None

@dataclass
class OutstandingClientBalance_base:
    associated_matter_ids: Optional[List[int]] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    last_payment_date: Optional[datetime.date] = None
    last_shared_date: Optional[datetime.date] = None
    newest_issued_bill_due_date: Optional[datetime.date] = None
    pending_payments_total: Optional[float] = None
    reminders_enabled: Optional[bool] = None
    total_outstanding_balance: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Payment_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    description: Optional[str] = None
    reference: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime.date] = None
    source_fund_type: Optional[Literal['Client', 'Matter']] = None
    payment_source_type: Optional[Literal['bank_account', 'credit_card', 'echeck', 'direct_payment', 'check', 'cash', 'interac_etransfer', 'wire_transfer', 'ach', 'eft', 'lawpay', 'paypal', 'cash_app', 'zelle', 'venmo', 'other']] = None
    voided_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Damage_base:
    id: Optional[int] = None
    amount: Optional[float] = None
    damage_type: Optional[Literal['special', 'general', 'other']] = None
    description: Optional[str] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MedicalBill_base:
    id: Optional[int] = None
    adjustment: Optional[float] = None
    amount: Optional[float] = None
    bill_date: Optional[datetime.date] = None
    bill_received_date: Optional[datetime.date] = None
    damage_type: Optional[str] = None
    document_id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MedicalRecord_base:
    id: Optional[int] = None
    document_id: Optional[int] = None
    etag: Optional[str] = None
    end_date: Optional[datetime.datetime] = None
    start_date: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MedicalRecordsRequest_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    bills_follow_up_date: Optional[datetime.datetime] = None
    bills_request_date: Optional[datetime.datetime] = None
    bills_status: Optional[Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']] = None
    description: Optional[str] = None
    in_treatment: Optional[bool] = None
    records_follow_up_date: Optional[datetime.datetime] = None
    records_request_date: Optional[datetime.datetime] = None
    records_status: Optional[Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']] = None
    treatment_end_date: Optional[datetime.datetime] = None
    treatment_start_date: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class PhoneNumber_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    number: Optional[str] = None
    name: Optional[Literal['Work', 'Personal', 'Other']] = None
    primary: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class PracticeArea_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    category: Optional[Literal['administrative', 'admiralty_and_maritime', 'anti_trust_and_competition', 'appellate', 'banking_and_finance', 'bankruptcy', 'business_formation_and_compliance', 'civil_litigation', 'civil_rights_and_constitutional', 'collections_and_debt', 'commercial_and_sale_of_goods', 'commercial_litigation', 'construction', 'consumer_protection', 'contracts', 'corporate_litigation', 'criminal', 'disability_and_social_security', 'education', 'elder', 'employment_and_labor', 'energy_and_environmental', 'ethics', 'family', 'food_and_drug', 'general_practice', 'government', 'healthcare', 'immigration', 'in_house_counsel', 'insurance', 'intellectual_property', 'international', 'juvenile', 'legal_aid', 'mediation_and_arbitration', 'medical_malpractice', 'military', 'multi_practice', 'non_profit_and_pro_bono', 'other', 'personal_injury', 'privacy_and_information_security', 'private_client', 'product_liability', 'real_estate', 'science_and_technology', 'securities_and_mergers_and_acquisitions', 'small_claims', 'sports_and_entertainment_and_gaming', 'tax', 'telecommunications', 'traffic_offenses', 'transportation', 'tribal', 'trusts', 'wills_and_estates', 'workers_compensation']] = None
    code: Optional[str] = None

@dataclass
class Relationship_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Reminder_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    duration: Optional[int] = None
    next_delivery_at: Optional[datetime.datetime] = None
    state: Optional[Literal['initializing', 'scheduling', 'rescheduling', 'scheduled', 'attempting_delivery', 'delivery_failed', 'delivered', 'delivery_skipped', 'invalid_user']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class ReportPreset_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    kind: Optional[Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']] = None
    format: Optional[Literal['csv', 'html', 'json', 'pdf', 'xlsx', 'zip']] = None
    last_generated_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    category: Optional[Literal['billing', 'client', 'compliance', 'financial', 'matter', 'online_payments', 'productivity', 'revenue', 'task']] = None
    options: Optional[str] = None

@dataclass
class ReportSchedule_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    time_of_day: Optional[datetime.datetime] = None
    frequency: Optional[Literal['daily', 'weekly', 'monthly']] = None
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    status: Optional[Literal['initial', 'queued', 'processing', 'failed', 'completed']] = None
    status_updated_at: Optional[datetime.datetime] = None
    next_scheduled_date: Optional[datetime.datetime] = None
    time_zone: Optional[str] = None
    report_preset_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    every_no_of_months: Optional[int] = None
    effective_from: Optional[datetime.date] = None

@dataclass
class Report_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    state: Optional[Literal['not_started', 'queued', 'in_progress', 'failed', 'completed', 'empty']] = None
    kind: Optional[Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']] = None
    format: Optional[Literal['csv', 'html', 'json', 'pdf', 'xlsx', 'zip']] = None
    progress: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    category: Optional[Literal['billing', 'client', 'compliance', 'financial', 'matter', 'online_payments', 'productivity', 'revenue', 'task']] = None
    source: Optional[Literal['reports', 'presets', 'scheduled']] = None

@dataclass
class BillingSetting_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    rounded_duration: Optional[float] = None
    rounding: Optional[int] = None
    use_decimal_rounding: Optional[bool] = None
    currency: Optional[str] = None
    currency_sign: Optional[str] = None
    tax_rate: Optional[float] = None
    tax_name: Optional[str] = None
    apply_tax_by_default: Optional[bool] = None
    time_on_flat_rate_contingency_matters_is_non_billable: Optional[bool] = None
    use_secondary_tax: Optional[bool] = None
    secondary_tax_rate: Optional[float] = None
    secondary_tax_rule: Optional[Literal['Pre', 'Post']] = None
    secondary_tax_name: Optional[str] = None
    notify_after_bill_created: Optional[bool] = None
    use_utbms_codes: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    multi_currency_billing: Optional[bool] = None
    billing_currencies: Optional[List[dict]] = None

@dataclass
class TextSnippet_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    snippet: Optional[str] = None
    phrase: Optional[str] = None
    whole_word: Optional[bool] = None

@dataclass
class CalendarVisibility_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    color: Optional[Literal['#658CDA', '#DA6666', '#49B050', '#E7804C', '#8C66DA', '#C4A882', '#64AD88', '#84AAA5', '#56BFB3', '#E77399', '#BFBF4B', '#8BBF3C', '#B473B4', '#A7A77D', '#F2A53D', '#658CB3', '#BE9494', '#A992A9', '#8897A5', '#93A2BE']] = None
    light_color: Optional[Literal['#5DA5C7', '#F95957', '#209412', '#FF7715', '#DE649D', '#FF6B02', '#56C4FC', '#00B177', '#50D19B', '#F14A8C', '#A3A2A2', '#84AB3B', '#B091EE', '#BD9E69', '#F2A000', '#00A5CA', '#CB5A3D', '#959CD0', '#B0B0B0', '#7BA6CD']] = None
    visible: Optional[bool] = None
    name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Task_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    description: Optional[str] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    due_at: Optional[datetime.date] = None
    permission: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None
    notify_completion: Optional[bool] = None
    statute_of_limitations: Optional[bool] = None
    time_estimated: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    time_entries_count: Optional[int] = None

@dataclass
class TaskTemplateList_base:
    created_at: Optional[datetime.datetime] = None
    description: Optional[str] = None
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    templates_count: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class TaskTemplate_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    private: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class TaskType_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    deleted_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Timer_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    start_time: Optional[datetime.datetime] = None
    elapsed_time: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class TrustLineItem_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    date: Optional[datetime.date] = None
    total: Optional[float] = None
    note: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class TrustRequest_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class User_base:
    account_owner: Optional[bool] = None
    clio_connect: Optional[bool] = None
    court_rules_default_attendee: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    default_calendar_id: Optional[int] = None
    email: Optional[str] = None
    enabled: Optional[bool] = None
    etag: Optional[str] = None
    first_name: Optional[str] = None
    id: Optional[int] = None
    initials: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    rate: Optional[float] = None
    roles: Optional[List[str]] = None
    subscription_type: Optional[Literal['Attorney', 'NonAttorney']] = None
    time_zone: Optional[str] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class UtbmsCode_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    type: Optional[Literal['UtbmsTask', 'UtbmsExpense', 'UtbmsActivity']] = None
    utbms_set_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class UtbmsSet_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    enabled: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Webhook_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    url: Optional[str] = None
    fields: Optional[str] = None
    shared_secret: Optional[str] = None
    model: Optional[Literal['activity', 'bill', 'calendar_entry', 'clio_payments_payment', 'communication', 'contact', 'document', 'folder', 'matter', 'task']] = None
    status: Optional[Literal['pending', 'enabled', 'suspended']] = None
    events: Optional[List[Literal['created', 'updated', 'deleted', 'matter_opened', 'matter_pended', 'matter_closed']]] = None
    expires_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class LinkedFolder_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    deleted_at: Optional[datetime.datetime] = None
    type: Optional[Literal['Folder']] = None
    locked: Optional[bool] = None
    name: Optional[str] = None
    root: Optional[bool] = None

@dataclass
class MultipartHeader_base:
    name: Optional[str] = None
    value: Optional[str] = None

@dataclass
class Multipart_base:
    part_number: Optional[int] = None
    put_url: Optional[str] = None

@dataclass
class AccountBalance_base:
    id: Optional[int] = None
    balance: Optional[float] = None
    type: Optional[str] = None
    name: Optional[str] = None
    currency_id: Optional[int] = None

@dataclass
class ActivityDescriptionRate_base:
    amount: Optional[float] = None
    non_billable_amount: Optional[float] = None
    type: Optional[Literal['User', 'FlatRate', 'Custom']] = None
    hierarchy: Optional[Literal['Default', 'Activity', 'Matter', 'Client']] = None

@dataclass
class Attendee_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['Contact', 'Calendar']] = None
    name: Optional[str] = None
    enabled: Optional[bool] = None
    email: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class AttorneyAllocation_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    account_id: Optional[int] = None
    resource_id: Optional[int] = None
    resource_type: Optional[str] = None
    originating_attorney_allocation: Optional[float] = None
    responsible_attorney_allocation: Optional[float] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Avatar_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    url: Optional[str] = None
    _destroy: Optional[bool] = None

@dataclass
class BillRecipient_base:
    created_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    on_all_matters: Optional[bool] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class CascadingTask_base:
    pass

@dataclass
class CascadingTaskTemplate_base:
    id: Optional[int] = None
    name: Optional[str] = None

@dataclass
class ClientPortal_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    unread_count: Optional[int] = None
    unread_notifiable_count: Optional[int] = None

@dataclass
class ClioCreator_base:
    account_owner: Optional[bool] = None
    clio_connect: Optional[bool] = None
    court_rules_default_attendee: Optional[bool] = None
    default_calendar_id: Optional[int] = None
    email: Optional[str] = None
    enabled: Optional[bool] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    type: Optional[Literal['ManageUser', 'ClientUser']] = None
    initials: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    rate: Optional[float] = None
    subscription_type: Optional[Literal['Attorney', 'NonAttorney']] = None
    time_zone: Optional[str] = None
    roles: Optional[List[str]] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class CommunicationEmlFile_base:
    id: Optional[int] = None

@dataclass
class ConferenceMeeting_base:
    conference_id: Optional[int] = None
    conference_password: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    join_url: Optional[str] = None
    type: Optional[str] = None
    source_id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class ContingencyFee_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    show_contingency_award: Optional[bool] = None

@dataclass
class ConversationMembership_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    read: Optional[bool] = None
    archived: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class PicklistOption_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    option: Optional[str] = None
    deleted_at: Optional[datetime.datetime] = None

@dataclass
class CustomFieldSetAssociation_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    display_order: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class CustomFieldValue_base:
    id: Optional[str] = None
    etag: Optional[str] = None
    field_name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    field_type: Optional[Literal['checkbox', 'contact', 'currency', 'date', 'time', 'email', 'matter', 'numeric', 'picklist', 'text_area', 'text_line', 'url']] = None
    field_required: Optional[bool] = None
    field_displayed: Optional[bool] = None
    field_display_order: Optional[int] = None
    value: Optional[str] = None
    soft_deleted: Optional[bool] = None

@dataclass
class Discount_base:
    rate: Optional[float] = None
    type: Optional[Literal['percentage', 'money']] = None
    note: Optional[str] = None
    early_payment_rate: Optional[int] = None
    early_payment_period: Optional[int] = None

@dataclass
class EvergreenRetainer_base:
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    minimum_threshold: Optional[float] = None

@dataclass
class ExternalProperty_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class InstantMessenger_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    address: Optional[str] = None
    name: Optional[Literal['Work', 'Personal', 'Other']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class JobTitle_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None
    initials: Optional[str] = None

@dataclass
class LegalAidUkActivity_base:
    activity_sub_category: Optional[str] = None
    advocacy: Optional[int] = None
    base_rate: Optional[float] = None
    bolt_ons: Optional[str] = None
    bolt_ons_summary: Optional[str] = None
    court: Optional[int] = None
    eligible_for_sqm: Optional[bool] = None
    expert: Optional[int] = None
    form_of_civil_legal_service: Optional[int] = None
    id: Optional[int] = None
    is_custom_rate: Optional[bool] = None
    json_key: Optional[str] = None
    region: Optional[int] = None
    tax_exclusive: Optional[bool] = None
    uplift: Optional[float] = None
    user_type: Optional[int] = None

@dataclass
class LegalAidUkBill_base:
    additional_travel_payment: Optional[bool] = None
    adjourned_hearing_fee: Optional[str] = None
    advocacy_costs: Optional[float] = None
    advice_time: Optional[int] = None
    bill_type: Optional[int] = None
    case_concluded: Optional[datetime.date] = None
    case_stage_level: Optional[int] = None
    cla_exemption_code: Optional[str] = None
    cla_reference: Optional[str] = None
    cmrh_oral: Optional[int] = None
    cmrh_telephone: Optional[int] = None
    cost_of_counsel: Optional[str] = None
    costs_are_those_of: Optional[int] = None
    court_location: Optional[str] = None
    date_of_claim: Optional[datetime.date] = None
    designated_accredited_representative: Optional[int] = None
    detention_travel_and_waiting_costs: Optional[str] = None
    disbursements_vat: Optional[float] = None
    exceptional_case_funding_reference: Optional[str] = None
    exemption_criteria_satisfied: Optional[int] = None
    follow_on_work: Optional[int] = None
    ho_interview: Optional[int] = None
    ho_ucn: Optional[int] = None
    id: Optional[int] = None
    independent_medical_reports_claimed: Optional[str] = None
    jr_form_filling: Optional[str] = None
    maat_id: Optional[str] = None
    meetings_attended: Optional[int] = None
    mht_ref_no: Optional[str] = None
    net_disbursements: Optional[float] = None
    net_profit_costs: Optional[float] = None
    niat_disbursement_prior_authority_number: Optional[str] = None
    number_of_attendances: Optional[int] = None
    outcome_for_the_client: Optional[int] = None
    profit_costs_ex_vat: Optional[int] = None
    prior_authority_reference: Optional[str] = None
    representation_order_date: Optional[datetime.date] = None
    stage_reached: Optional[int] = None
    substantive_hearing: Optional[int] = None
    travel_and_waiting_costs: Optional[float] = None
    travel_time: Optional[int] = None
    value_of_costs: Optional[str] = None
    waiting_time: Optional[int] = None

@dataclass
class LegalAidUkContact_base:
    id: Optional[int] = None
    disability: Optional[int] = None
    disability_code: Optional[str] = None
    ethnicity: Optional[int] = None
    ethnicity_title: Optional[str] = None
    financially_eligible: Optional[bool] = None
    gender: Optional[int] = None
    gender_title: Optional[str] = None
    national_insurance_number: Optional[str] = None

@dataclass
class LegalAidUkMatter_base:
    access_point: Optional[str] = None
    laa_office_number: Optional[str] = None
    ait_hearing_centre: Optional[int] = None
    attended_several_hearings_acting_for_multiple_clients: Optional[bool] = None
    bill_ho_ucn: Optional[str] = None
    bill_number_of_attendances: Optional[int] = None
    bill_outcome_for_the_client_code: Optional[int] = None
    bill_stage_reached_code: Optional[int] = None
    case_reference: Optional[str] = None
    case_start_date: Optional[datetime.date] = None
    category: Optional[int] = None
    category_as_string: Optional[str] = None
    certificate_effective_date: Optional[datetime.date] = None
    certificate_expiration_date: Optional[datetime.date] = None
    certificate_number: Optional[str] = None
    certificate_scope: Optional[str] = None
    certification_type: Optional[int] = None
    change_of_solicitor: Optional[bool] = None
    client_equal_opportunity_monitoring: Optional[str] = None
    client_type: Optional[int] = None
    clr_start_date: Optional[datetime.date] = None
    clr_total_profit_costs: Optional[str] = None
    cost_limit: Optional[str] = None
    counsel: Optional[int] = None
    court: Optional[int] = None
    court_id: Optional[int] = None
    court_id_code: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    delivery_location: Optional[str] = None
    dscc_number: Optional[str] = None
    duty_solicitor: Optional[bool] = None
    etag: Optional[str] = None
    exceptional_case_funding_reference: Optional[str] = None
    expense_limit: Optional[str] = None
    fee_scheme: Optional[int] = None
    first_conducting_solicitor: Optional[bool] = None
    id: Optional[int] = None
    irc_surgery: Optional[str] = None
    legacy_case: Optional[str] = None
    legal_representation_number: Optional[str] = None
    lh_total_disbursements: Optional[str] = None
    lh_start_date: Optional[str] = None
    lh_total_profit_costs: Optional[str] = None
    linked_matter_id: Optional[int] = None
    local_authority_number: Optional[str] = None
    maat_id: Optional[str] = None
    matter_type: Optional[int] = None
    matter_type_code: Optional[str] = None
    matter_type_1: Optional[int] = None
    matter_type_1_code: Optional[str] = None
    matter_type_1_title: Optional[str] = None
    matter_type_2: Optional[int] = None
    matter_type_2_code: Optional[str] = None
    matter_type_2_title: Optional[str] = None
    matter_types_combined: Optional[str] = None
    number_of_clients_seen_at_surgery: Optional[int] = None
    number_of_clients: Optional[int] = None
    party: Optional[int] = None
    police_station: Optional[str] = None
    post_transfer_clients_represented: Optional[int] = None
    postal_application_accepted: Optional[str] = None
    prior_authority_reference: Optional[str] = None
    prison_id: Optional[int] = None
    prison_law_prior_approval_number: Optional[str] = None
    procurement_area: Optional[str] = None
    region: Optional[int] = None
    related_claims_number: Optional[str] = None
    representation_order_date: Optional[datetime.date] = None
    schedule_reference_number: Optional[str] = None
    scheme_id: Optional[str] = None
    session_type: Optional[int] = None
    solicitor_type: Optional[int] = None
    standard_fee_category: Optional[int] = None
    surgery_clients_resulting_in_a_legal_help_matter_opened: Optional[int] = None
    surgery_clients: Optional[int] = None
    surgery_date: Optional[datetime.date] = None
    transfer_date: Optional[datetime.date] = None
    type_of_advice: Optional[int] = None
    type_of_service: Optional[str] = None
    ucn: Optional[str] = None
    ufn: Optional[str] = None
    undesignated_area_court: Optional[bool] = None
    updated_at: Optional[datetime.datetime] = None
    user_type: Optional[int] = None
    youth_court: Optional[bool] = None

@dataclass
class LineItemTotals_base:
    quantity: Optional[float] = None
    price: Optional[float] = None
    discount_percent: Optional[float] = None
    total: Optional[float] = None
    sub_total: Optional[float] = None

@dataclass
class MatterBillRecipient_base:
    created_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MatterBudget_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    budget: Optional[float] = None
    include_expenses: Optional[bool] = None
    notification_threshold: Optional[int] = None
    notify_users: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class MatterCustomRate_base:
    type: Optional[Literal['FlatRate', 'HourlyRate', 'ContingencyFee']] = None
    on_invoice: Optional[bool] = None

@dataclass
class MatterBalance_base:
    id: Optional[int] = None
    amount: Optional[float] = None

@dataclass
class NotificationEventSubscriber_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class NotificationMethod_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    type: Optional[Literal['Email', 'Popup', 'SMS']] = None
    email_address: Optional[str] = None
    is_default_email_address: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class Participant_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    type: Optional[Literal['Person', 'Company', 'User']] = None
    identifier: Optional[str] = None
    secondary_identifier: Optional[str] = None
    enabled: Optional[bool] = None
    name: Optional[str] = None
    initials: Optional[str] = None
    job_title_name: Optional[str] = None

@dataclass
class PaymentProfile_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    billing_setting_id: Optional[int] = None
    name: Optional[str] = None
    terms: Optional[int] = None
    discount_rate: Optional[float] = None
    discount_period: Optional[int] = None
    interest_rate: Optional[float] = None
    interest_period: Optional[int] = None
    interest_type: Optional[Literal['simple', 'compound']] = None

@dataclass
class Lien_base:
    id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    etag: Optional[str] = None
    lien_type: Optional[Literal['general', 'medical_payer', 'medical_provider']] = None
    mark_as_lien: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class PolymorphicObject_base:
    id: Optional[int] = None
    type: Optional[Literal['Task', 'CalendarEntry', 'MatterNote', 'ContactNote', 'Matter', 'Contact', 'User', 'CreditMemo', 'Payment']] = None
    identifier: Optional[str] = None
    secondary_identifier: Optional[str] = None
    tertiary_identifier: Optional[str] = None

@dataclass
class ReminderTemplate_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    duration: Optional[int] = None
    notification_type: Optional[Literal['Email', 'Popup']] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class SplitInvoicePayer_base:
    id: Optional[int] = None
    contact_id: Optional[int] = None
    matter_id: Optional[int] = None
    send_to_bill_recipients: Optional[bool] = None
    split_portion: Optional[float] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class SplitInvoice_base:
    id: Optional[int] = None
    bill_id: Optional[int] = None
    linked_invoices_display_numbers: Optional[List[str]] = None
    linked_invoices_ids: Optional[List[int]] = None
    split_connection_id: Optional[str] = None
    split_portion: Optional[float] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class TaskTemplateListInstace_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class UnredactedParticipant_base:
    pass

@dataclass
class WebSite_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    address: Optional[str] = None
    name: Optional[Literal['Work', 'Personal', 'Twitter', 'Facebook', 'LinkedIn', 'Instant Messenger', 'Other']] = None
    default_web_site: Optional[bool] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

@dataclass
class BillRecipient_Contact_base:
    id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    type: Optional[Literal['Company', 'Person']] = None
    primary_email_address: Optional[str] = None

@dataclass
class CustomFieldMatterSelection_base:
    id: Optional[int] = None
    display_number: Optional[str] = None

@dataclass
class PolymorphicCustomRate_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    rate: Optional[float] = None
    award: Optional[float] = None
    note: Optional[str] = None
    date: Optional[datetime.date] = None

@dataclass
class PolymorphicCustomRate_User_base:
    enabled: Optional[bool] = None
    etag: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None

@dataclass
class PolymorphicCustomRate_Group_base:
    etag: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None

@dataclass
class PolymorphicCustomRate_ActivityDescription_base:
    id: Optional[int] = None
    etag: Optional[str] = None
    name: Optional[str] = None

