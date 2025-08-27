from dataclasses import dataclass
from typing import Optional, List, Literal
import datetime

@dataclass
class Activity_create_RequestBody_Data_Activity_description:
    id: Optional[int] = None
    utbms_task_id: Optional[int] = None
    utbms_activity_id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Calendar_entry:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Client_portal:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Communication:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Contact_note:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Expense_category:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Matter_note:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Task:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Text_message_conversation:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_User:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Utbms_expense:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data_Vendor:
    id: Optional[int] = None

@dataclass
class Activity_create_RequestBody_Data:
    date: datetime.date
    type: Literal['TimeEntry', 'ExpenseEntry', 'HardCostEntry', 'SoftCostEntry']
    activity_description: Optional[Activity_create_RequestBody_Data_Activity_description] = None
    calendar_entry: Optional[Activity_create_RequestBody_Data_Calendar_entry] = None
    client_portal: Optional[Activity_create_RequestBody_Data_Client_portal] = None
    communication: Optional[Activity_create_RequestBody_Data_Communication] = None
    contact_note: Optional[Activity_create_RequestBody_Data_Contact_note] = None
    expense_category: Optional[Activity_create_RequestBody_Data_Expense_category] = None
    matter: Optional[Activity_create_RequestBody_Data_Matter] = None
    matter_note: Optional[Activity_create_RequestBody_Data_Matter_note] = None
    no_charge: Optional[bool] = None
    non_billable: Optional[bool] = None
    note: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    reference: Optional[str] = None
    start_timer: Optional[bool] = None
    task: Optional[Activity_create_RequestBody_Data_Task] = None
    tax_setting: Optional[Literal['no_tax', 'tax_1_only', 'tax_2_only', 'tax_1_and_tax_2']] = None
    text_message_conversation: Optional[Activity_create_RequestBody_Data_Text_message_conversation] = None
    user: Optional[Activity_create_RequestBody_Data_User] = None
    utbms_expense: Optional[Activity_create_RequestBody_Data_Utbms_expense] = None
    vendor: Optional[Activity_create_RequestBody_Data_Vendor] = None

@dataclass
class Activity_create_RequestBody:
    data: Activity_create_RequestBody_Data

@dataclass
class Activity_update_RequestBody_Data_Activity_description:
    id: Optional[int] = None
    utbms_task_id: Optional[int] = None
    utbms_activity_id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Calendar_entry:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Client_portal:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Communication:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Contact_note:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Expense_category:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Matter_note:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Task:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Text_message_conversation:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_User:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Utbms_expense:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data_Vendor:
    id: Optional[int] = None

@dataclass
class Activity_update_RequestBody_Data:
    activity_description: Optional[Activity_update_RequestBody_Data_Activity_description] = None
    calendar_entry: Optional[Activity_update_RequestBody_Data_Calendar_entry] = None
    client_portal: Optional[Activity_update_RequestBody_Data_Client_portal] = None
    communication: Optional[Activity_update_RequestBody_Data_Communication] = None
    contact_note: Optional[Activity_update_RequestBody_Data_Contact_note] = None
    date: Optional[datetime.date] = None
    expense_category: Optional[Activity_update_RequestBody_Data_Expense_category] = None
    matter: Optional[Activity_update_RequestBody_Data_Matter] = None
    matter_note: Optional[Activity_update_RequestBody_Data_Matter_note] = None
    no_charge: Optional[bool] = None
    non_billable: Optional[bool] = None
    note: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    reference: Optional[str] = None
    start_timer: Optional[bool] = None
    task: Optional[Activity_update_RequestBody_Data_Task] = None
    tax_setting: Optional[Literal['no_tax', 'tax_1_only', 'tax_2_only', 'tax_1_and_tax_2']] = None
    text_message_conversation: Optional[Activity_update_RequestBody_Data_Text_message_conversation] = None
    type: Optional[Literal['TimeEntry', 'ExpenseEntry', 'HardCostEntry', 'SoftCostEntry']] = None
    user: Optional[Activity_update_RequestBody_Data_User] = None
    utbms_expense: Optional[Activity_update_RequestBody_Data_Utbms_expense] = None
    vendor: Optional[Activity_update_RequestBody_Data_Vendor] = None

@dataclass
class Activity_update_RequestBody:
    data: Activity_update_RequestBody_Data

@dataclass
class Activityrate_create_RequestBody_Data:
    co_counsel_contact_id: Optional[int] = None
    contact_id: Optional[int] = None
    flat_rate: Optional[bool] = None
    rate: Optional[float] = None

@dataclass
class Activityrate_create_RequestBody:
    data: Activityrate_create_RequestBody_Data

@dataclass
class Activityrate_update_RequestBody_Data:
    co_counsel_contact_id: Optional[int] = None
    contact_id: Optional[int] = None
    flat_rate: Optional[bool] = None
    rate: Optional[float] = None

@dataclass
class Activityrate_update_RequestBody:
    data: Activityrate_update_RequestBody_Data

@dataclass
class Activitydescription_create_RequestBody_Data_Currency:
    pass

@dataclass
class Activitydescription_create_RequestBody_Data_Rate:
    amount: Optional[float] = None
    non_billable_amount: Optional[float] = None
    type: Optional[Literal['User', 'FlatRate', 'Custom']] = None

@dataclass
class Activitydescription_create_RequestBody_Data:
    name: str
    currency: Optional[Activitydescription_create_RequestBody_Data_Currency] = None
    default: Optional[bool] = None
    groups: Optional[List[dict]] = None
    rate: Optional[Activitydescription_create_RequestBody_Data_Rate] = None
    visible_to_co_counsel: Optional[bool] = None

@dataclass
class Activitydescription_create_RequestBody:
    data: Activitydescription_create_RequestBody_Data

@dataclass
class Activitydescription_update_RequestBody_Data_Currency:
    pass

@dataclass
class Activitydescription_update_RequestBody_Data_Rate:
    amount: Optional[float] = None
    non_billable_amount: Optional[float] = None
    type: Optional[Literal['User', 'FlatRate', 'Custom']] = None

@dataclass
class Activitydescription_update_RequestBody_Data:
    currency: Optional[Activitydescription_update_RequestBody_Data_Currency] = None
    default: Optional[bool] = None
    groups: Optional[List[dict]] = None
    name: Optional[str] = None
    rate: Optional[Activitydescription_update_RequestBody_Data_Rate] = None
    visible_to_co_counsel: Optional[bool] = None

@dataclass
class Activitydescription_update_RequestBody:
    data: Activitydescription_update_RequestBody_Data

@dataclass
class Bankaccount_create_RequestBody_Data:
    currency: str
    type: Literal['Operating', 'Trust']
    account_number: Optional[str] = None
    balance: Optional[float] = None
    controlled_account: Optional[bool] = None
    default_account: Optional[bool] = None
    domicile_branch: Optional[str] = None
    general_ledger_number: Optional[str] = None
    holder: Optional[str] = None
    institution: Optional[str] = None
    name: Optional[str] = None
    swift: Optional[str] = None
    transit_number: Optional[str] = None

@dataclass
class Bankaccount_create_RequestBody:
    data: Bankaccount_create_RequestBody_Data

@dataclass
class Bankaccount_update_RequestBody_Data:
    account_number: Optional[str] = None
    controlled_account: Optional[bool] = None
    currency: Optional[str] = None
    default_account: Optional[bool] = None
    domicile_branch: Optional[str] = None
    general_ledger_number: Optional[str] = None
    holder: Optional[str] = None
    institution: Optional[str] = None
    name: Optional[str] = None
    swift: Optional[str] = None
    transit_number: Optional[str] = None

@dataclass
class Bankaccount_update_RequestBody:
    data: Bankaccount_update_RequestBody_Data

@dataclass
class Billtheme_update_RequestBody_Data:
    config: Optional[str] = None
    name: Optional[str] = None

@dataclass
class Billtheme_update_RequestBody:
    data: Billtheme_update_RequestBody_Data

@dataclass
class Bill_update_RequestBody_Data_Bill_theme:
    id: Optional[int] = None

@dataclass
class Bill_update_RequestBody_Data_Discount:
    rate: Optional[float] = None
    type: Optional[Literal['percentage', 'money']] = None
    note: Optional[str] = None

@dataclass
class Bill_update_RequestBody_Data_Interest:
    rate: Optional[float] = None
    type: Optional[Literal['simple', 'compound']] = None
    period: Optional[int] = None

@dataclass
class Bill_update_RequestBody_Data:
    bill_theme: Optional[Bill_update_RequestBody_Data_Bill_theme] = None
    currency_id: Optional[int] = None
    discount: Optional[Bill_update_RequestBody_Data_Discount] = None
    due_at: Optional[datetime.date] = None
    interest: Optional[Bill_update_RequestBody_Data_Interest] = None
    issued_at: Optional[datetime.date] = None
    memo: Optional[str] = None
    number: Optional[str] = None
    purchase_order: Optional[str] = None
    secondary_tax_rate: Optional[float] = None
    state: Optional[Literal['draft', 'awaiting_approval', 'awaiting_payment', 'paid', 'void', 'deleted']] = None
    subject: Optional[str] = None
    tax_rate: Optional[float] = None
    use_grace_period: Optional[bool] = None

@dataclass
class Bill_update_RequestBody:
    data: Bill_update_RequestBody_Data

@dataclass
class Calendarentry_create_RequestBody_Data_Calendar_owner:
    id: int

@dataclass
class Calendarentry_create_RequestBody_Data_Calendar_entry_event_type:
    id: Optional[int] = None

@dataclass
class Calendarentry_create_RequestBody_Data_Conference_meeting:
    type: Optional[Literal['zoom']] = None

@dataclass
class Calendarentry_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Calendarentry_create_RequestBody_Data:
    calendar_owner: Calendarentry_create_RequestBody_Data_Calendar_owner
    end_at: datetime.datetime
    start_at: datetime.datetime
    summary: str
    _deleted: Optional[Literal['single', 'future']] = None
    all_day: Optional[bool] = None
    attendees: Optional[List[dict]] = None
    calendar_entry_event_type: Optional[Calendarentry_create_RequestBody_Data_Calendar_entry_event_type] = None
    conference_meeting: Optional[Calendarentry_create_RequestBody_Data_Conference_meeting] = None
    description: Optional[str] = None
    external_properties: Optional[List[dict]] = None
    location: Optional[str] = None
    matter: Optional[Calendarentry_create_RequestBody_Data_Matter] = None
    recurrence_rule: Optional[str] = None
    send_email_notification: Optional[bool] = None

@dataclass
class Calendarentry_create_RequestBody:
    data: Calendarentry_create_RequestBody_Data

@dataclass
class Calendarentry_update_RequestBody_Data_Calendar_entry_event_type:
    id: Optional[int] = None

@dataclass
class Calendarentry_update_RequestBody_Data_Calendar_owner:
    id: Optional[int] = None

@dataclass
class Calendarentry_update_RequestBody_Data_Conference_meeting:
    type: Optional[Literal['zoom']] = None

@dataclass
class Calendarentry_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Calendarentry_update_RequestBody_Data:
    _deleted: Optional[Literal['single', 'future']] = None
    all_day: Optional[bool] = None
    attendees: Optional[List[dict]] = None
    calendar_entry_event_type: Optional[Calendarentry_update_RequestBody_Data_Calendar_entry_event_type] = None
    calendar_owner: Optional[Calendarentry_update_RequestBody_Data_Calendar_owner] = None
    conference_meeting: Optional[Calendarentry_update_RequestBody_Data_Conference_meeting] = None
    description: Optional[str] = None
    end_at: Optional[datetime.datetime] = None
    external_properties: Optional[List[dict]] = None
    location: Optional[str] = None
    matter: Optional[Calendarentry_update_RequestBody_Data_Matter] = None
    recurrence_rule: Optional[str] = None
    send_email_notification: Optional[bool] = None
    start_at: Optional[datetime.datetime] = None
    summary: Optional[str] = None

@dataclass
class Calendarentry_update_RequestBody:
    data: Calendarentry_update_RequestBody_Data

@dataclass
class Calendarentryeventtype_create_RequestBody_Data:
    color: Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']
    name: str

@dataclass
class Calendarentryeventtype_create_RequestBody:
    data: Calendarentryeventtype_create_RequestBody_Data

@dataclass
class Calendarentryeventtype_update_RequestBody_Data:
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    name: Optional[str] = None

@dataclass
class Calendarentryeventtype_update_RequestBody:
    data: Calendarentryeventtype_update_RequestBody_Data

@dataclass
class Calendar_create_RequestBody_Data:
    name: str
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    source: Optional[Literal['web', 'mobile']] = None
    visible: Optional[bool] = None

@dataclass
class Calendar_create_RequestBody:
    data: Calendar_create_RequestBody_Data

@dataclass
class Calendar_update_RequestBody_Data:
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    name: Optional[str] = None
    source: Optional[Literal['web', 'mobile']] = None
    visible: Optional[bool] = None

@dataclass
class Calendar_update_RequestBody:
    data: Calendar_update_RequestBody_Data

@dataclass
class Cliopaymentslink_create_RequestBody_Data_Destination_account:
    id: int

@dataclass
class Cliopaymentslink_create_RequestBody_Data_Subject:
    id: int
    type: Literal['BankAccount', 'Bill', 'Contact']

@dataclass
class Cliopaymentslink_create_RequestBody_Data_Destination_contact:
    id: Optional[int] = None

@dataclass
class Cliopaymentslink_create_RequestBody_Data:
    currency: str
    description: str
    destination_account: Cliopaymentslink_create_RequestBody_Data_Destination_account
    duration: int
    subject: Cliopaymentslink_create_RequestBody_Data_Subject
    amount: Optional[float] = None
    destination_contact: Optional[Cliopaymentslink_create_RequestBody_Data_Destination_contact] = None
    email_address: Optional[str] = None
    is_allocated_as_revenue: Optional[bool] = None

@dataclass
class Cliopaymentslink_create_RequestBody:
    data: Cliopaymentslink_create_RequestBody_Data

@dataclass
class Cliopaymentslink_update_RequestBody_Data:
    expired: Optional[bool] = None

@dataclass
class Cliopaymentslink_update_RequestBody:
    data: Cliopaymentslink_update_RequestBody_Data

@dataclass
class Communication_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Communication_create_RequestBody_Data:
    body: str
    received_at: str
    subject: str
    type: Literal['PhoneCommunication', 'EmailCommunication']
    external_properties: Optional[List[dict]] = None
    matter: Optional[Communication_create_RequestBody_Data_Matter] = None
    notification_event_subscribers: Optional[List[dict]] = None
    receivers: Optional[List[dict]] = None
    senders: Optional[List[dict]] = None

@dataclass
class Communication_create_RequestBody:
    data: Communication_create_RequestBody_Data

@dataclass
class Communication_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Communication_update_RequestBody_Data:
    body: Optional[str] = None
    external_properties: Optional[List[dict]] = None
    matter: Optional[Communication_update_RequestBody_Data_Matter] = None
    notification_event_subscribers: Optional[List[dict]] = None
    received_at: Optional[str] = None
    receivers: Optional[List[dict]] = None
    senders: Optional[List[dict]] = None
    subject: Optional[str] = None
    type: Optional[Literal['PhoneCommunication', 'EmailCommunication']] = None

@dataclass
class Communication_update_RequestBody:
    data: Communication_update_RequestBody_Data

@dataclass
class Contact_create_RequestBody_Data_Avatar:
    image: Optional[str] = None
    _destroy: Optional[bool] = None

@dataclass
class Contact_create_RequestBody_Data_Co_counsel_rate:
    rate: Optional[float] = None

@dataclass
class Contact_create_RequestBody_Data_Company:
    id: Optional[int] = None

@dataclass
class Contact_create_RequestBody_Data_Currency:
    pass

@dataclass
class Contact_create_RequestBody_Data:
    name: str
    type: Literal['Person', 'Company']
    addresses: Optional[List[dict]] = None
    avatar: Optional[Contact_create_RequestBody_Data_Avatar] = None
    clio_connect_email: Optional[str] = None
    co_counsel_rate: Optional[Contact_create_RequestBody_Data_Co_counsel_rate] = None
    company: Optional[Contact_create_RequestBody_Data_Company] = None
    currency: Optional[Contact_create_RequestBody_Data_Currency] = None
    custom_field_set_associations: Optional[List[dict]] = None
    custom_field_values: Optional[List[dict]] = None
    date_of_birth: Optional[datetime.date] = None
    email_addresses: Optional[List[dict]] = None
    first_name: Optional[str] = None
    instant_messengers: Optional[List[dict]] = None
    last_name: Optional[str] = None
    ledes_client_id: Optional[str] = None
    middle_name: Optional[str] = None
    phone_numbers: Optional[List[dict]] = None
    prefix: Optional[str] = None
    sales_tax_number: Optional[str] = None
    title: Optional[str] = None
    web_sites: Optional[List[dict]] = None

@dataclass
class Contact_create_RequestBody:
    data: Contact_create_RequestBody_Data

@dataclass
class Contact_update_RequestBody_Data_Avatar:
    image: Optional[str] = None
    _destroy: Optional[bool] = None

@dataclass
class Contact_update_RequestBody_Data_Co_counsel_rate:
    rate: Optional[float] = None

@dataclass
class Contact_update_RequestBody_Data_Company:
    id: Optional[int] = None

@dataclass
class Contact_update_RequestBody_Data_Currency:
    pass

@dataclass
class Contact_update_RequestBody_Data:
    addresses: Optional[List[dict]] = None
    avatar: Optional[Contact_update_RequestBody_Data_Avatar] = None
    clio_connect_email: Optional[str] = None
    co_counsel_rate: Optional[Contact_update_RequestBody_Data_Co_counsel_rate] = None
    company: Optional[Contact_update_RequestBody_Data_Company] = None
    currency: Optional[Contact_update_RequestBody_Data_Currency] = None
    custom_field_set_associations: Optional[List[dict]] = None
    custom_field_values: Optional[List[dict]] = None
    date_of_birth: Optional[datetime.date] = None
    email_addresses: Optional[List[dict]] = None
    first_name: Optional[str] = None
    instant_messengers: Optional[List[dict]] = None
    last_name: Optional[str] = None
    ledes_client_id: Optional[str] = None
    middle_name: Optional[str] = None
    name: Optional[str] = None
    phone_numbers: Optional[List[dict]] = None
    prefix: Optional[str] = None
    sales_tax_number: Optional[str] = None
    title: Optional[str] = None
    type: Optional[Literal['Person', 'Company']] = None
    web_sites: Optional[List[dict]] = None

@dataclass
class Contact_update_RequestBody:
    data: Contact_update_RequestBody_Data

@dataclass
class Conversationmessage_create_RequestBody_Data_Attachment:
    document_id: Optional[int] = None
    document_version_id: Optional[int] = None

@dataclass
class Conversationmessage_create_RequestBody_Data_Conversation:
    id: Optional[int] = None

@dataclass
class Conversationmessage_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Conversationmessage_create_RequestBody_Data:
    body: str
    receivers: List[dict]
    subject: str
    attachment: Optional[Conversationmessage_create_RequestBody_Data_Attachment] = None
    conversation: Optional[Conversationmessage_create_RequestBody_Data_Conversation] = None
    matter: Optional[Conversationmessage_create_RequestBody_Data_Matter] = None

@dataclass
class Conversationmessage_create_RequestBody:
    data: Conversationmessage_create_RequestBody_Data

@dataclass
class Conversation_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Conversation_update_RequestBody_Data:
    archived: Optional[bool] = None
    matter: Optional[Conversation_update_RequestBody_Data_Matter] = None
    read: Optional[bool] = None

@dataclass
class Conversation_update_RequestBody:
    data: Conversation_update_RequestBody_Data

@dataclass
class Matterdocket_create_RequestBody_Data_Jurisdiction:
    id: int

@dataclass
class Matterdocket_create_RequestBody_Data_Trigger:
    id: int

@dataclass
class Matterdocket_create_RequestBody_Data:
    jurisdiction: Matterdocket_create_RequestBody_Data_Jurisdiction
    name: str
    start_date: datetime.date
    trigger: Matterdocket_create_RequestBody_Data_Trigger
    start_time: Optional[datetime.datetime] = None

@dataclass
class Matterdocket_create_RequestBody:
    data: Matterdocket_create_RequestBody_Data

@dataclass
class Customfield_create_RequestBody_Data:
    field_type: Literal['checkbox', 'contact', 'currency', 'date', 'time', 'email', 'matter', 'numeric', 'picklist', 'text_area', 'text_line', 'url']
    name: str
    parent_type: Literal['Contact', 'Matter']
    display_order: Optional[int] = None
    displayed: Optional[bool] = None
    picklist_options: Optional[List[dict]] = None
    required: Optional[bool] = None

@dataclass
class Customfield_create_RequestBody:
    data: Customfield_create_RequestBody_Data

@dataclass
class Customfield_update_RequestBody_Data:
    display_order: Optional[int] = None
    displayed: Optional[bool] = None
    name: Optional[str] = None
    picklist_options: Optional[List[dict]] = None
    required: Optional[bool] = None

@dataclass
class Customfield_update_RequestBody:
    data: Customfield_update_RequestBody_Data

@dataclass
class Customfieldset_create_RequestBody_Data:
    name: str
    displayed: Optional[bool] = None
    parent_type: Optional[Literal['Contact', 'Matter']] = None

@dataclass
class Customfieldset_create_RequestBody:
    data: Customfieldset_create_RequestBody_Data

@dataclass
class Customfieldset_update_RequestBody_Data:
    displayed: Optional[bool] = None
    name: Optional[str] = None
    parent_type: Optional[Literal['Contact', 'Matter']] = None

@dataclass
class Customfieldset_update_RequestBody:
    data: Customfieldset_update_RequestBody_Data

@dataclass
class Customaction_create_RequestBody_Data:
    label: str
    target_url: str
    ui_reference: Literal['activities/show', 'documents/show', 'contacts/show', 'matters/show', 'folders/show']

@dataclass
class Customaction_create_RequestBody:
    data: Customaction_create_RequestBody_Data

@dataclass
class Customaction_update_RequestBody_Data:
    label: Optional[str] = None
    target_url: Optional[str] = None
    ui_reference: Optional[Literal['activities/show', 'documents/show', 'contacts/show', 'matters/show', 'folders/show']] = None

@dataclass
class Customaction_update_RequestBody:
    data: Customaction_update_RequestBody_Data

@dataclass
class Damage_create_RequestBody_Data:
    amount: float
    damage_type: Literal['special', 'general', 'other']
    description: str
    matter_id: int

@dataclass
class Damage_create_RequestBody:
    data: Damage_create_RequestBody_Data

@dataclass
class Damage_update_RequestBody_Data:
    amount: Optional[float] = None
    damage_type: Optional[Literal['special', 'general', 'other']] = None
    description: Optional[str] = None

@dataclass
class Damage_update_RequestBody:
    data: Damage_update_RequestBody_Data

@dataclass
class Expensecategory_create_RequestBody_Data_Currency:
    pass

@dataclass
class Expensecategory_create_RequestBody_Data_Utbms_code:
    id: Optional[int] = None

@dataclass
class Expensecategory_create_RequestBody_Data:
    name: str
    currency: Optional[Expensecategory_create_RequestBody_Data_Currency] = None
    entry_type: Optional[Literal['hard_cost', 'soft_cost', 'unassociated']] = None
    groups: Optional[List[dict]] = None
    rate: Optional[float] = None
    utbms_code: Optional[Expensecategory_create_RequestBody_Data_Utbms_code] = None

@dataclass
class Expensecategory_create_RequestBody:
    data: Expensecategory_create_RequestBody_Data

@dataclass
class Expensecategory_update_RequestBody_Data_Currency:
    pass

@dataclass
class Expensecategory_update_RequestBody_Data_Utbms_code:
    id: Optional[int] = None

@dataclass
class Expensecategory_update_RequestBody_Data:
    currency: Optional[Expensecategory_update_RequestBody_Data_Currency] = None
    entry_type: Optional[Literal['hard_cost', 'soft_cost', 'unassociated']] = None
    groups: Optional[List[dict]] = None
    name: Optional[str] = None
    rate: Optional[float] = None
    utbms_code: Optional[Expensecategory_update_RequestBody_Data_Utbms_code] = None

@dataclass
class Expensecategory_update_RequestBody:
    data: Expensecategory_update_RequestBody_Data

@dataclass
class Grant_create_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Grant_create_RequestBody:
    data: Grant_create_RequestBody_Data

@dataclass
class Grant_update_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Grant_update_RequestBody:
    data: Grant_update_RequestBody_Data

@dataclass
class Grantfundingsource_create_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Grantfundingsource_create_RequestBody:
    data: Grantfundingsource_create_RequestBody_Data

@dataclass
class Grantfundingsource_update_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Grantfundingsource_update_RequestBody:
    data: Grantfundingsource_update_RequestBody_Data

@dataclass
class Grantfundingsource_destroy_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Grantfundingsource_destroy_RequestBody:
    data: Grantfundingsource_destroy_RequestBody_Data

@dataclass
class Group_create_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Group_create_RequestBody:
    data: Group_create_RequestBody_Data

@dataclass
class Group_update_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Group_update_RequestBody:
    data: Group_update_RequestBody_Data

@dataclass
class Myevent_update_RequestBody_Data:
    marked_as_read: Optional[bool] = None

@dataclass
class Myevent_update_RequestBody:
    data: Myevent_update_RequestBody_Data

@dataclass
class Lineitem_update_RequestBody_Data_Activity:
    id: Optional[int] = None

@dataclass
class Lineitem_update_RequestBody_Data_Bill:
    id: Optional[int] = None

@dataclass
class Lineitem_update_RequestBody_Data_Discount:
    rate: Optional[float] = None
    type: Optional[bool] = None

@dataclass
class Lineitem_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Lineitem_update_RequestBody_Data:
    activity: Optional[Lineitem_update_RequestBody_Data_Activity] = None
    bill: Optional[Lineitem_update_RequestBody_Data_Bill] = None
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    discount: Optional[Lineitem_update_RequestBody_Data_Discount] = None
    group_ordering: Optional[int] = None
    kind: Optional[Literal['Expense', 'Service', 'Product']] = None
    matter: Optional[Lineitem_update_RequestBody_Data_Matter] = None
    note: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    secondary_taxable: Optional[bool] = None
    taxable: Optional[bool] = None
    update_original_record: Optional[bool] = None

@dataclass
class Lineitem_update_RequestBody:
    data: Lineitem_update_RequestBody_Data

@dataclass
class Matter_create_RequestBody_Data_Client:
    id: int

@dataclass
class Matter_create_RequestBody_Data_Currency:
    pass

@dataclass
class Matter_create_RequestBody_Data_Custom_rate:
    type: Literal['FlatRate', 'HourlyRate', 'ContingencyFee']
    rates: Optional[List[dict]] = None

@dataclass
class Matter_create_RequestBody_Data_Evergreen_retainer:
    minimum_threshold: Optional[float] = None
    recipients: Optional[List[dict]] = None

@dataclass
class Matter_create_RequestBody_Data_Group:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Matter_budget:
    _destroy: Optional[bool] = None
    budget: Optional[float] = None
    include_expenses: Optional[bool] = None
    notification_threshold: Optional[int] = None
    notify_users: Optional[bool] = None

@dataclass
class Matter_create_RequestBody_Data_Matter_stage:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Originating_attorney:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Responsible_attorney:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Responsible_staff:
    id: Optional[int] = None

@dataclass
class Matter_create_RequestBody_Data_Statute_of_limitations:
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    due_at: Optional[datetime.date] = None
    reminders: Optional[List[dict]] = None

@dataclass
class Matter_create_RequestBody_Data:
    client: Matter_create_RequestBody_Data_Client
    description: str
    billable: Optional[bool] = None
    client_reference: Optional[str] = None
    close_date: Optional[datetime.date] = None
    currency: Optional[Matter_create_RequestBody_Data_Currency] = None
    custom_field_set_associations: Optional[List[dict]] = None
    custom_field_values: Optional[List[dict]] = None
    custom_rate: Optional[Matter_create_RequestBody_Data_Custom_rate] = None
    display_number: Optional[str] = None
    evergreen_retainer: Optional[Matter_create_RequestBody_Data_Evergreen_retainer] = None
    group: Optional[Matter_create_RequestBody_Data_Group] = None
    location: Optional[str] = None
    matter_budget: Optional[Matter_create_RequestBody_Data_Matter_budget] = None
    matter_stage: Optional[Matter_create_RequestBody_Data_Matter_stage] = None
    open_date: Optional[datetime.date] = None
    originating_attorney: Optional[Matter_create_RequestBody_Data_Originating_attorney] = None
    pending_date: Optional[datetime.date] = None
    practice_area: Optional[Matter_create_RequestBody_Data_Practice_area] = None
    relationships: Optional[List[dict]] = None
    reset_matter_number: Optional[bool] = None
    responsible_attorney: Optional[Matter_create_RequestBody_Data_Responsible_attorney] = None
    responsible_staff: Optional[Matter_create_RequestBody_Data_Responsible_staff] = None
    split_invoice_payers: Optional[List[dict]] = None
    status: Optional[Literal['open', 'closed', 'pending']] = None
    statute_of_limitations: Optional[Matter_create_RequestBody_Data_Statute_of_limitations] = None
    task_template_list_instances: Optional[List[dict]] = None

@dataclass
class Matter_create_RequestBody:
    data: Matter_create_RequestBody_Data

@dataclass
class Matter_update_RequestBody_Data_Client:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Currency:
    pass

@dataclass
class Matter_update_RequestBody_Data_Custom_rate:
    type: Optional[Literal['FlatRate', 'HourlyRate', 'ContingencyFee']] = None
    rates: Optional[List[dict]] = None

@dataclass
class Matter_update_RequestBody_Data_Evergreen_retainer:
    minimum_threshold: Optional[float] = None
    _destroy: Optional[bool] = None
    recipients: Optional[List[dict]] = None

@dataclass
class Matter_update_RequestBody_Data_Group:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Matter_budget:
    _destroy: Optional[bool] = None
    budget: Optional[float] = None
    include_expenses: Optional[bool] = None
    notification_threshold: Optional[int] = None
    notify_users: Optional[bool] = None

@dataclass
class Matter_update_RequestBody_Data_Matter_stage:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Originating_attorney:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Responsible_attorney:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Responsible_staff:
    id: Optional[int] = None

@dataclass
class Matter_update_RequestBody_Data_Statute_of_limitations:
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    due_at: Optional[datetime.date] = None
    reminders: Optional[List[dict]] = None

@dataclass
class Matter_update_RequestBody_Data:
    billable: Optional[bool] = None
    client: Optional[Matter_update_RequestBody_Data_Client] = None
    client_reference: Optional[str] = None
    close_date: Optional[datetime.date] = None
    currency: Optional[Matter_update_RequestBody_Data_Currency] = None
    custom_field_set_associations: Optional[List[dict]] = None
    custom_field_values: Optional[List[dict]] = None
    custom_rate: Optional[Matter_update_RequestBody_Data_Custom_rate] = None
    description: Optional[str] = None
    display_number: Optional[str] = None
    evergreen_retainer: Optional[Matter_update_RequestBody_Data_Evergreen_retainer] = None
    group: Optional[Matter_update_RequestBody_Data_Group] = None
    location: Optional[str] = None
    matter_budget: Optional[Matter_update_RequestBody_Data_Matter_budget] = None
    matter_stage: Optional[Matter_update_RequestBody_Data_Matter_stage] = None
    open_date: Optional[datetime.date] = None
    originating_attorney: Optional[Matter_update_RequestBody_Data_Originating_attorney] = None
    pending_date: Optional[datetime.date] = None
    practice_area: Optional[Matter_update_RequestBody_Data_Practice_area] = None
    relationships: Optional[List[dict]] = None
    reset_matter_number: Optional[bool] = None
    responsible_attorney: Optional[Matter_update_RequestBody_Data_Responsible_attorney] = None
    responsible_staff: Optional[Matter_update_RequestBody_Data_Responsible_staff] = None
    split_invoice_payers: Optional[List[dict]] = None
    status: Optional[Literal['open', 'closed', 'pending']] = None
    statute_of_limitations: Optional[Matter_update_RequestBody_Data_Statute_of_limitations] = None
    task_template_list_instances: Optional[List[dict]] = None

@dataclass
class Matter_update_RequestBody:
    data: Matter_update_RequestBody_Data

@dataclass
class Medicalrecord_update_RequestBody_Data:
    end_date: Optional[datetime.datetime] = None
    start_date: Optional[datetime.datetime] = None

@dataclass
class Medicalrecord_update_RequestBody:
    data: Medicalrecord_update_RequestBody_Data

@dataclass
class Medicalrecordsrequest_create_RequestBody_Data:
    bills_status: Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']
    in_treatment: bool
    matter_id: int
    medical_provider_id: int
    records_status: Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']
    bills_follow_up_date: Optional[datetime.datetime] = None
    bills_request_date: Optional[datetime.datetime] = None
    description: Optional[str] = None
    medical_bills: Optional[List[dict]] = None
    medical_records: Optional[List[dict]] = None
    records_follow_up_date: Optional[datetime.datetime] = None
    records_request_date: Optional[datetime.datetime] = None
    treatment_end_date: Optional[datetime.datetime] = None
    treatment_start_date: Optional[datetime.datetime] = None

@dataclass
class Medicalrecordsrequest_create_RequestBody:
    data: Medicalrecordsrequest_create_RequestBody_Data

@dataclass
class Medicalrecordsrequest_update_RequestBody_Data:
    bills_follow_up_date: Optional[datetime.datetime] = None
    bills_request_date: Optional[datetime.datetime] = None
    bills_status: Optional[Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']] = None
    description: Optional[str] = None
    in_treatment: Optional[bool] = None
    medical_bills: Optional[List[dict]] = None
    medical_provider_id: Optional[int] = None
    medical_records: Optional[List[dict]] = None
    records_follow_up_date: Optional[datetime.datetime] = None
    records_request_date: Optional[datetime.datetime] = None
    records_status: Optional[Literal['not_yet_requested', 'requested', 'received', 'incomplete', 'certified']] = None
    treatment_end_date: Optional[datetime.datetime] = None
    treatment_start_date: Optional[datetime.datetime] = None

@dataclass
class Medicalrecordsrequest_update_RequestBody:
    data: Medicalrecordsrequest_update_RequestBody_Data

@dataclass
class Medicalbill_update_RequestBody_Data:
    adjustment: Optional[float] = None
    amount: Optional[float] = None
    balance: Optional[float] = None
    bill_date: Optional[datetime.date] = None
    bill_received_date: Optional[datetime.date] = None
    mark_balance_type_as: Optional[Literal['lien', 'outstanding_balance', 'neither']] = None
    name: Optional[str] = None
    payers: Optional[List[dict]] = None

@dataclass
class Medicalbill_update_RequestBody:
    data: Medicalbill_update_RequestBody_Data

@dataclass
class Note_create_RequestBody_Data_Contact:
    id: int

@dataclass
class Note_create_RequestBody_Data_Matter:
    id: int

@dataclass
class Note_create_RequestBody_Data:
    contact: Note_create_RequestBody_Data_Contact
    matter: Note_create_RequestBody_Data_Matter
    type: Literal['Matter', 'Contact']
    date: Optional[datetime.date] = None
    detail: Optional[str] = None
    detail_text_type: Optional[str] = None
    notification_event_subscribers: Optional[List[dict]] = None
    subject: Optional[str] = None

@dataclass
class Note_create_RequestBody:
    data: Note_create_RequestBody_Data

@dataclass
class Note_update_RequestBody_Data:
    date: Optional[datetime.date] = None
    detail: Optional[str] = None
    detail_text_type: Optional[str] = None
    notification_event_subscribers: Optional[List[dict]] = None
    subject: Optional[str] = None

@dataclass
class Note_update_RequestBody:
    data: Note_update_RequestBody_Data

@dataclass
class Practicearea_create_RequestBody_Data:
    name: str
    category: Optional[Literal['administrative', 'admiralty_and_maritime', 'anti_trust_and_competition', 'appellate', 'banking_and_finance', 'bankruptcy', 'business_formation_and_compliance', 'civil_litigation', 'civil_rights_and_constitutional', 'collections_and_debt', 'commercial_and_sale_of_goods', 'commercial_litigation', 'construction', 'consumer_protection', 'contracts', 'corporate_litigation', 'criminal', 'disability_and_social_security', 'education', 'elder', 'employment_and_labor', 'energy_and_environmental', 'ethics', 'family', 'food_and_drug', 'general_practice', 'government', 'healthcare', 'immigration', 'in_house_counsel', 'insurance', 'intellectual_property', 'international', 'juvenile', 'legal_aid', 'mediation_and_arbitration', 'medical_malpractice', 'military', 'multi_practice', 'non_profit_and_pro_bono', 'other', 'personal_injury', 'privacy_and_information_security', 'private_client', 'product_liability', 'real_estate', 'science_and_technology', 'securities_and_mergers_and_acquisitions', 'small_claims', 'sports_and_entertainment_and_gaming', 'tax', 'telecommunications', 'traffic_offenses', 'transportation', 'tribal', 'trusts', 'wills_and_estates', 'workers_compensation']] = None
    code: Optional[str] = None

@dataclass
class Practicearea_create_RequestBody:
    data: Practicearea_create_RequestBody_Data

@dataclass
class Practicearea_update_RequestBody_Data:
    category: Optional[Literal['administrative', 'admiralty_and_maritime', 'anti_trust_and_competition', 'appellate', 'banking_and_finance', 'bankruptcy', 'business_formation_and_compliance', 'civil_litigation', 'civil_rights_and_constitutional', 'collections_and_debt', 'commercial_and_sale_of_goods', 'commercial_litigation', 'construction', 'consumer_protection', 'contracts', 'corporate_litigation', 'criminal', 'disability_and_social_security', 'education', 'elder', 'employment_and_labor', 'energy_and_environmental', 'ethics', 'family', 'food_and_drug', 'general_practice', 'government', 'healthcare', 'immigration', 'in_house_counsel', 'insurance', 'intellectual_property', 'international', 'juvenile', 'legal_aid', 'mediation_and_arbitration', 'medical_malpractice', 'military', 'multi_practice', 'non_profit_and_pro_bono', 'other', 'personal_injury', 'privacy_and_information_security', 'private_client', 'product_liability', 'real_estate', 'science_and_technology', 'securities_and_mergers_and_acquisitions', 'small_claims', 'sports_and_entertainment_and_gaming', 'tax', 'telecommunications', 'traffic_offenses', 'transportation', 'tribal', 'trusts', 'wills_and_estates', 'workers_compensation']] = None
    code: Optional[str] = None
    name: Optional[str] = None

@dataclass
class Practicearea_update_RequestBody:
    data: Practicearea_update_RequestBody_Data

@dataclass
class Relationship_create_RequestBody_Data_Contact:
    id: Optional[int] = None

@dataclass
class Relationship_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Relationship_create_RequestBody_Data:
    contact: Optional[Relationship_create_RequestBody_Data_Contact] = None
    description: Optional[str] = None
    matter: Optional[Relationship_create_RequestBody_Data_Matter] = None

@dataclass
class Relationship_create_RequestBody:
    data: Relationship_create_RequestBody_Data

@dataclass
class Relationship_update_RequestBody_Data_Contact:
    id: Optional[int] = None

@dataclass
class Relationship_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Relationship_update_RequestBody_Data:
    contact: Optional[Relationship_update_RequestBody_Data_Contact] = None
    description: Optional[str] = None
    matter: Optional[Relationship_update_RequestBody_Data_Matter] = None

@dataclass
class Relationship_update_RequestBody:
    data: Relationship_update_RequestBody_Data

@dataclass
class Reminder_create_RequestBody_Data_Notification_method:
    id: int

@dataclass
class Reminder_create_RequestBody_Data_Subject:
    id: int
    type: Literal['CalendarEntry', 'Task']

@dataclass
class Reminder_create_RequestBody_Data:
    notification_method: Reminder_create_RequestBody_Data_Notification_method
    subject: Reminder_create_RequestBody_Data_Subject
    duration_unit: Optional[Literal['weeks', 'days', 'hours', 'minutes']] = None
    duration_value: Optional[int] = None

@dataclass
class Reminder_create_RequestBody:
    data: Reminder_create_RequestBody_Data

@dataclass
class Reminder_update_RequestBody_Data_Notification_method:
    id: Optional[int] = None

@dataclass
class Reminder_update_RequestBody_Data:
    duration_unit: Optional[Literal['weeks', 'days', 'hours', 'minutes']] = None
    duration_value: Optional[int] = None
    notification_method: Optional[Reminder_update_RequestBody_Data_Notification_method] = None

@dataclass
class Reminder_update_RequestBody:
    data: Reminder_update_RequestBody_Data

@dataclass
class Report_create_RequestBody_Data_Client:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data_Originating_attorney:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data_Responsible_attorney:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data_User:
    id: Optional[int] = None

@dataclass
class Report_create_RequestBody_Data:
    format: Literal['csv', 'html', 'json', 'pdf', 'xlsx', 'zip']
    kind: Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']
    client: Optional[Report_create_RequestBody_Data_Client] = None
    end_date: Optional[datetime.date] = None
    matter: Optional[Report_create_RequestBody_Data_Matter] = None
    originating_attorney: Optional[Report_create_RequestBody_Data_Originating_attorney] = None
    practice_area: Optional[Report_create_RequestBody_Data_Practice_area] = None
    responsible_attorney: Optional[Report_create_RequestBody_Data_Responsible_attorney] = None
    start_date: Optional[datetime.date] = None
    user: Optional[Report_create_RequestBody_Data_User] = None
    year: Optional[str] = None

@dataclass
class Report_create_RequestBody:
    data: Report_create_RequestBody_Data

@dataclass
class Reportpreset_create_RequestBody_Data:
    format: Literal['csv', 'html', 'json', 'pdf', 'xlsx', 'zip']
    kind: Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']
    name: str
    options: str

@dataclass
class Reportpreset_create_RequestBody:
    data: Reportpreset_create_RequestBody_Data

@dataclass
class Reportpreset_update_RequestBody_Data:
    format: Optional[Literal['csv', 'html', 'json', 'pdf', 'xlsx', 'zip']] = None
    kind: Optional[Literal['accounts_receivable', 'accounts_receivable_aging', 'bank_account_activity', 'billing_history', 'billing_rate', 'client_activity', 'client_ledger', 'clio_payments_deposit', 'clio_payments_ledger', 'clio_payments_monthly_statement', 'clio_payments_sales_tax', 'clio_payments_transaction', 'contact_information', 'disbursement_payment', 'fee_allocation', 'general_ledger', 'grant_matters', 'invoice_payments_v2', 'law_society_of_alberta', 'law_society_of_alberta_al', 'law_society_of_alberta_bar', 'law_society_of_alberta_tl', 'law_society_of_alberta_tt', 'matter', 'matter_balance_summary', 'matter_productivity_by_user', 'matters_by_responsible_attorney', 'originating_attorney_revenue', 'other_revenue', 'productivity_by_client', 'productivity_by_user', 'revenue', 'task_productivity_by_user', 'task_progress_by_user', 'trust_ledger', 'trust_ledger_nsw', 'trust_listing', 'trust_management', 'work_in_progress']] = None
    name: Optional[str] = None
    options: Optional[str] = None

@dataclass
class Reportpreset_update_RequestBody:
    data: Reportpreset_update_RequestBody_Data

@dataclass
class Reportschedule_create_RequestBody_Data:
    frequency: Literal['daily', 'weekly', 'monthly']
    report_preset_id: int
    time_of_day: datetime.datetime
    time_zone: Literal['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara', 'Africa/Asmera', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau', 'Africa/Blantyre', 'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Ceuta', 'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti', 'Africa/Douala', 'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali', 'Africa/Kinshasa', 'Africa/Lagos', 'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda', 'Africa/Lubumbashi', 'Africa/Lusaka', 'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru', 'Africa/Mbabane', 'Africa/Mogadishu', 'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena', 'Africa/Niamey', 'Africa/Nouakchott', 'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome', 'Africa/Timbuktu', 'Africa/Tripoli', 'Africa/Tunis', 'Africa/Windhoek', 'America/Adak', 'America/Anchorage', 'America/Anguilla', 'America/Antigua', 'America/Araguaina', 'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca', 'America/Argentina/ComodRivadavia', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/La_Rioja', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Salta', 'America/Argentina/San_Juan', 'America/Argentina/San_Luis', 'America/Argentina/Tucuman', 'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion', 'America/Atikokan', 'America/Atka', 'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados', 'America/Belem', 'America/Belize', 'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota', 'America/Boise', 'America/Buenos_Aires', 'America/Cambridge_Bay', 'America/Campo_Grande', 'America/Cancun', 'America/Caracas', 'America/Catamarca', 'America/Cayenne', 'America/Cayman', 'America/Chicago', 'America/Chihuahua', 'America/Ciudad_Juarez', 'America/Coral_Harbour', 'America/Cordoba', 'America/Costa_Rica', 'America/Coyhaique', 'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn', 'America/Dawson', 'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica', 'America/Edmonton', 'America/Eirunepe', 'America/El_Salvador', 'America/Ensenada', 'America/Fort_Nelson', 'America/Fort_Wayne', 'America/Fortaleza', 'America/Glace_Bay', 'America/Godthab', 'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe', 'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana', 'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox', 'America/Indiana/Marengo', 'America/Indiana/Petersburg', 'America/Indiana/Tell_City', 'America/Indiana/Vevay', 'America/Indiana/Vincennes', 'America/Indiana/Winamac', 'America/Indianapolis', 'America/Inuvik', 'America/Iqaluit', 'America/Jamaica', 'America/Jujuy', 'America/Juneau', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Knox_IN', 'America/Kralendijk', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Louisville', 'America/Lower_Princes', 'America/Maceio', 'America/Managua', 'America/Manaus', 'America/Marigot', 'America/Martinique', 'America/Matamoros', 'America/Mazatlan', 'America/Mendoza', 'America/Menominee', 'America/Merida', 'America/Metlakatla', 'America/Mexico_City', 'America/Miquelon', 'America/Moncton', 'America/Monterrey', 'America/Montevideo', 'America/Montreal', 'America/Montserrat', 'America/Nassau', 'America/New_York', 'America/Nipigon', 'America/Nome', 'America/Noronha', 'America/North_Dakota/Beulah', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Nuuk', 'America/Ojinaga', 'America/Panama', 'America/Pangnirtung', 'America/Paramaribo', 'America/Phoenix', 'America/Port-au-Prince', 'America/Port_of_Spain', 'America/Porto_Acre', 'America/Porto_Velho', 'America/Puerto_Rico', 'America/Punta_Arenas', 'America/Rainy_River', 'America/Rankin_Inlet', 'America/Recife', 'America/Regina', 'America/Resolute', 'America/Rio_Branco', 'America/Rosario', 'America/Santa_Isabel', 'America/Santarem', 'America/Santiago', 'America/Santo_Domingo', 'America/Sao_Paulo', 'America/Scoresbysund', 'America/Shiprock', 'America/Sitka', 'America/St_Barthelemy', 'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia', 'America/St_Thomas', 'America/St_Vincent', 'America/Swift_Current', 'America/Tegucigalpa', 'America/Thule', 'America/Thunder_Bay', 'America/Tijuana', 'America/Toronto', 'America/Tortola', 'America/Vancouver', 'America/Virgin', 'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat', 'America/Yellowknife', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Macquarie', 'Antarctica/Mawson', 'Antarctica/McMurdo', 'Antarctica/Palmer', 'Antarctica/Rothera', 'Antarctica/South_Pole', 'Antarctica/Syowa', 'Antarctica/Troll', 'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden', 'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr', 'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat', 'Asia/Ashkhabad', 'Asia/Atyrau', 'Asia/Baghdad', 'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek', 'Asia/Brunei', 'Asia/Calcutta', 'Asia/Chita', 'Asia/Choibalsan', 'Asia/Chongqing', 'Asia/Chungking', 'Asia/Colombo', 'Asia/Dacca', 'Asia/Damascus', 'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai', 'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Harbin', 'Asia/Hebron', 'Asia/Ho_Chi_Minh', 'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Istanbul', 'Asia/Jakarta', 'Asia/Jayapura', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kashgar', 'Asia/Kathmandu', 'Asia/Katmandu', 'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macao', 'Asia/Macau', 'Asia/Magadan', 'Asia/Makassar', 'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk', 'Asia/Omsk', 'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar', 'Asia/Qostanay', 'Asia/Qyzylorda', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Saigon', 'Asia/Sakhalin', 'Asia/Samarkand', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tel_Aviv', 'Asia/Thimbu', 'Asia/Thimphu', 'Asia/Tokyo', 'Asia/Tomsk', 'Asia/Ujung_Pandang', 'Asia/Ulaanbaatar', 'Asia/Ulan_Bator', 'Asia/Urumqi', 'Asia/Ust-Nera', 'Asia/Vientiane', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yangon', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary', 'Atlantic/Cape_Verde', 'Atlantic/Faeroe', 'Atlantic/Faroe', 'Atlantic/Jan_Mayen', 'Atlantic/Madeira', 'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley', 'Australia/ACT', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill', 'Australia/Canberra', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart', 'Australia/LHI', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/NSW', 'Australia/North', 'Australia/Perth', 'Australia/Queensland', 'Australia/South', 'Australia/Sydney', 'Australia/Tasmania', 'Australia/Victoria', 'Australia/West', 'Australia/Yancowinna', 'Brazil/Acre', 'Brazil/DeNoronha', 'Brazil/East', 'Brazil/West', 'CET', 'CST6CDT', 'Canada/Atlantic', 'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'Canada/Saskatchewan', 'Canada/Yukon', 'Chile/Continental', 'Chile/EasterIsland', 'Cuba', 'EET', 'EST', 'EST5EDT', 'Egypt', 'Eire', 'Etc/GMT', 'Etc/GMT+0', 'Etc/GMT+1', 'Etc/GMT+10', 'Etc/GMT+11', 'Etc/GMT+12', 'Etc/GMT+2', 'Etc/GMT+3', 'Etc/GMT+4', 'Etc/GMT+5', 'Etc/GMT+6', 'Etc/GMT+7', 'Etc/GMT+8', 'Etc/GMT+9', 'Etc/GMT-0', 'Etc/GMT-1', 'Etc/GMT-10', 'Etc/GMT-11', 'Etc/GMT-12', 'Etc/GMT-13', 'Etc/GMT-14', 'Etc/GMT-2', 'Etc/GMT-3', 'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6', 'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT0', 'Etc/Greenwich', 'Etc/UCT', 'Etc/UTC', 'Etc/Universal', 'Etc/Zulu', 'Europe/Amsterdam', 'Europe/Andorra', 'Europe/Astrakhan', 'Europe/Athens', 'Europe/Belfast', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Busingen', 'Europe/Chisinau', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar', 'Europe/Guernsey', 'Europe/Helsinki', 'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Kirov', 'Europe/Kyiv', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Luxembourg', 'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn', 'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow', 'Europe/Nicosia', 'Europe/Oslo', 'Europe/Paris', 'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino', 'Europe/Sarajevo', 'Europe/Saratov', 'Europe/Simferopol', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Tirane', 'Europe/Tiraspol', 'Europe/Ulyanovsk', 'Europe/Uzhgorod', 'Europe/Vaduz', 'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'Factory', 'GB', 'GB-Eire', 'GMT', 'GMT+0', 'GMT-0', 'GMT0', 'Greenwich', 'HST', 'Hongkong', 'Iceland', 'Indian/Antananarivo', 'Indian/Chagos', 'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro', 'Indian/Kerguelen', 'Indian/Mahe', 'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte', 'Indian/Reunion', 'Iran', 'Israel', 'Jamaica', 'Japan', 'Kwajalein', 'Libya', 'MET', 'MST', 'MST7MDT', 'Mexico/BajaNorte', 'Mexico/BajaSur', 'Mexico/General', 'NZ', 'NZ-CHAT', 'Navajo', 'PRC', 'PST8PDT', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk', 'Pacific/Easter', 'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Funafuti', 'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Johnston', 'Pacific/Kanton', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein', 'Pacific/Majuro', 'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue', 'Pacific/Norfolk', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn', 'Pacific/Pohnpei', 'Pacific/Ponape', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan', 'Pacific/Samoa', 'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Truk', 'Pacific/Wake', 'Pacific/Wallis', 'Pacific/Yap', 'Poland', 'Portugal', 'ROC', 'ROK', 'Singapore', 'Turkey', 'UCT', 'US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa', 'UTC', 'Universal', 'W-SU', 'WET', 'Zulu']
    day_of_month: Optional[int] = None
    days_of_week: Optional[List[int]] = None
    effective_from: Optional[datetime.date] = None
    every_no_of_months: Optional[int] = None

@dataclass
class Reportschedule_create_RequestBody:
    data: Reportschedule_create_RequestBody_Data

@dataclass
class Reportschedule_update_RequestBody_Data:
    day_of_month: Optional[int] = None
    days_of_week: Optional[List[int]] = None
    effective_from: Optional[datetime.date] = None
    every_no_of_months: Optional[int] = None
    frequency: Optional[Literal['daily', 'weekly', 'monthly']] = None
    report_preset_id: Optional[int] = None
    time_of_day: Optional[datetime.datetime] = None
    time_zone: Optional[Literal['Africa/Abidjan', 'Africa/Accra', 'Africa/Addis_Ababa', 'Africa/Algiers', 'Africa/Asmara', 'Africa/Asmera', 'Africa/Bamako', 'Africa/Bangui', 'Africa/Banjul', 'Africa/Bissau', 'Africa/Blantyre', 'Africa/Brazzaville', 'Africa/Bujumbura', 'Africa/Cairo', 'Africa/Casablanca', 'Africa/Ceuta', 'Africa/Conakry', 'Africa/Dakar', 'Africa/Dar_es_Salaam', 'Africa/Djibouti', 'Africa/Douala', 'Africa/El_Aaiun', 'Africa/Freetown', 'Africa/Gaborone', 'Africa/Harare', 'Africa/Johannesburg', 'Africa/Juba', 'Africa/Kampala', 'Africa/Khartoum', 'Africa/Kigali', 'Africa/Kinshasa', 'Africa/Lagos', 'Africa/Libreville', 'Africa/Lome', 'Africa/Luanda', 'Africa/Lubumbashi', 'Africa/Lusaka', 'Africa/Malabo', 'Africa/Maputo', 'Africa/Maseru', 'Africa/Mbabane', 'Africa/Mogadishu', 'Africa/Monrovia', 'Africa/Nairobi', 'Africa/Ndjamena', 'Africa/Niamey', 'Africa/Nouakchott', 'Africa/Ouagadougou', 'Africa/Porto-Novo', 'Africa/Sao_Tome', 'Africa/Timbuktu', 'Africa/Tripoli', 'Africa/Tunis', 'Africa/Windhoek', 'America/Adak', 'America/Anchorage', 'America/Anguilla', 'America/Antigua', 'America/Araguaina', 'America/Argentina/Buenos_Aires', 'America/Argentina/Catamarca', 'America/Argentina/ComodRivadavia', 'America/Argentina/Cordoba', 'America/Argentina/Jujuy', 'America/Argentina/La_Rioja', 'America/Argentina/Mendoza', 'America/Argentina/Rio_Gallegos', 'America/Argentina/Salta', 'America/Argentina/San_Juan', 'America/Argentina/San_Luis', 'America/Argentina/Tucuman', 'America/Argentina/Ushuaia', 'America/Aruba', 'America/Asuncion', 'America/Atikokan', 'America/Atka', 'America/Bahia', 'America/Bahia_Banderas', 'America/Barbados', 'America/Belem', 'America/Belize', 'America/Blanc-Sablon', 'America/Boa_Vista', 'America/Bogota', 'America/Boise', 'America/Buenos_Aires', 'America/Cambridge_Bay', 'America/Campo_Grande', 'America/Cancun', 'America/Caracas', 'America/Catamarca', 'America/Cayenne', 'America/Cayman', 'America/Chicago', 'America/Chihuahua', 'America/Ciudad_Juarez', 'America/Coral_Harbour', 'America/Cordoba', 'America/Costa_Rica', 'America/Coyhaique', 'America/Creston', 'America/Cuiaba', 'America/Curacao', 'America/Danmarkshavn', 'America/Dawson', 'America/Dawson_Creek', 'America/Denver', 'America/Detroit', 'America/Dominica', 'America/Edmonton', 'America/Eirunepe', 'America/El_Salvador', 'America/Ensenada', 'America/Fort_Nelson', 'America/Fort_Wayne', 'America/Fortaleza', 'America/Glace_Bay', 'America/Godthab', 'America/Goose_Bay', 'America/Grand_Turk', 'America/Grenada', 'America/Guadeloupe', 'America/Guatemala', 'America/Guayaquil', 'America/Guyana', 'America/Halifax', 'America/Havana', 'America/Hermosillo', 'America/Indiana/Indianapolis', 'America/Indiana/Knox', 'America/Indiana/Marengo', 'America/Indiana/Petersburg', 'America/Indiana/Tell_City', 'America/Indiana/Vevay', 'America/Indiana/Vincennes', 'America/Indiana/Winamac', 'America/Indianapolis', 'America/Inuvik', 'America/Iqaluit', 'America/Jamaica', 'America/Jujuy', 'America/Juneau', 'America/Kentucky/Louisville', 'America/Kentucky/Monticello', 'America/Knox_IN', 'America/Kralendijk', 'America/La_Paz', 'America/Lima', 'America/Los_Angeles', 'America/Louisville', 'America/Lower_Princes', 'America/Maceio', 'America/Managua', 'America/Manaus', 'America/Marigot', 'America/Martinique', 'America/Matamoros', 'America/Mazatlan', 'America/Mendoza', 'America/Menominee', 'America/Merida', 'America/Metlakatla', 'America/Mexico_City', 'America/Miquelon', 'America/Moncton', 'America/Monterrey', 'America/Montevideo', 'America/Montreal', 'America/Montserrat', 'America/Nassau', 'America/New_York', 'America/Nipigon', 'America/Nome', 'America/Noronha', 'America/North_Dakota/Beulah', 'America/North_Dakota/Center', 'America/North_Dakota/New_Salem', 'America/Nuuk', 'America/Ojinaga', 'America/Panama', 'America/Pangnirtung', 'America/Paramaribo', 'America/Phoenix', 'America/Port-au-Prince', 'America/Port_of_Spain', 'America/Porto_Acre', 'America/Porto_Velho', 'America/Puerto_Rico', 'America/Punta_Arenas', 'America/Rainy_River', 'America/Rankin_Inlet', 'America/Recife', 'America/Regina', 'America/Resolute', 'America/Rio_Branco', 'America/Rosario', 'America/Santa_Isabel', 'America/Santarem', 'America/Santiago', 'America/Santo_Domingo', 'America/Sao_Paulo', 'America/Scoresbysund', 'America/Shiprock', 'America/Sitka', 'America/St_Barthelemy', 'America/St_Johns', 'America/St_Kitts', 'America/St_Lucia', 'America/St_Thomas', 'America/St_Vincent', 'America/Swift_Current', 'America/Tegucigalpa', 'America/Thule', 'America/Thunder_Bay', 'America/Tijuana', 'America/Toronto', 'America/Tortola', 'America/Vancouver', 'America/Virgin', 'America/Whitehorse', 'America/Winnipeg', 'America/Yakutat', 'America/Yellowknife', 'Antarctica/Casey', 'Antarctica/Davis', 'Antarctica/DumontDUrville', 'Antarctica/Macquarie', 'Antarctica/Mawson', 'Antarctica/McMurdo', 'Antarctica/Palmer', 'Antarctica/Rothera', 'Antarctica/South_Pole', 'Antarctica/Syowa', 'Antarctica/Troll', 'Antarctica/Vostok', 'Arctic/Longyearbyen', 'Asia/Aden', 'Asia/Almaty', 'Asia/Amman', 'Asia/Anadyr', 'Asia/Aqtau', 'Asia/Aqtobe', 'Asia/Ashgabat', 'Asia/Ashkhabad', 'Asia/Atyrau', 'Asia/Baghdad', 'Asia/Bahrain', 'Asia/Baku', 'Asia/Bangkok', 'Asia/Barnaul', 'Asia/Beirut', 'Asia/Bishkek', 'Asia/Brunei', 'Asia/Calcutta', 'Asia/Chita', 'Asia/Choibalsan', 'Asia/Chongqing', 'Asia/Chungking', 'Asia/Colombo', 'Asia/Dacca', 'Asia/Damascus', 'Asia/Dhaka', 'Asia/Dili', 'Asia/Dubai', 'Asia/Dushanbe', 'Asia/Famagusta', 'Asia/Gaza', 'Asia/Harbin', 'Asia/Hebron', 'Asia/Ho_Chi_Minh', 'Asia/Hong_Kong', 'Asia/Hovd', 'Asia/Irkutsk', 'Asia/Istanbul', 'Asia/Jakarta', 'Asia/Jayapura', 'Asia/Jerusalem', 'Asia/Kabul', 'Asia/Kamchatka', 'Asia/Karachi', 'Asia/Kashgar', 'Asia/Kathmandu', 'Asia/Katmandu', 'Asia/Khandyga', 'Asia/Kolkata', 'Asia/Krasnoyarsk', 'Asia/Kuala_Lumpur', 'Asia/Kuching', 'Asia/Kuwait', 'Asia/Macao', 'Asia/Macau', 'Asia/Magadan', 'Asia/Makassar', 'Asia/Manila', 'Asia/Muscat', 'Asia/Nicosia', 'Asia/Novokuznetsk', 'Asia/Novosibirsk', 'Asia/Omsk', 'Asia/Oral', 'Asia/Phnom_Penh', 'Asia/Pontianak', 'Asia/Pyongyang', 'Asia/Qatar', 'Asia/Qostanay', 'Asia/Qyzylorda', 'Asia/Rangoon', 'Asia/Riyadh', 'Asia/Saigon', 'Asia/Sakhalin', 'Asia/Samarkand', 'Asia/Seoul', 'Asia/Shanghai', 'Asia/Singapore', 'Asia/Srednekolymsk', 'Asia/Taipei', 'Asia/Tashkent', 'Asia/Tbilisi', 'Asia/Tehran', 'Asia/Tel_Aviv', 'Asia/Thimbu', 'Asia/Thimphu', 'Asia/Tokyo', 'Asia/Tomsk', 'Asia/Ujung_Pandang', 'Asia/Ulaanbaatar', 'Asia/Ulan_Bator', 'Asia/Urumqi', 'Asia/Ust-Nera', 'Asia/Vientiane', 'Asia/Vladivostok', 'Asia/Yakutsk', 'Asia/Yangon', 'Asia/Yekaterinburg', 'Asia/Yerevan', 'Atlantic/Azores', 'Atlantic/Bermuda', 'Atlantic/Canary', 'Atlantic/Cape_Verde', 'Atlantic/Faeroe', 'Atlantic/Faroe', 'Atlantic/Jan_Mayen', 'Atlantic/Madeira', 'Atlantic/Reykjavik', 'Atlantic/South_Georgia', 'Atlantic/St_Helena', 'Atlantic/Stanley', 'Australia/ACT', 'Australia/Adelaide', 'Australia/Brisbane', 'Australia/Broken_Hill', 'Australia/Canberra', 'Australia/Currie', 'Australia/Darwin', 'Australia/Eucla', 'Australia/Hobart', 'Australia/LHI', 'Australia/Lindeman', 'Australia/Lord_Howe', 'Australia/Melbourne', 'Australia/NSW', 'Australia/North', 'Australia/Perth', 'Australia/Queensland', 'Australia/South', 'Australia/Sydney', 'Australia/Tasmania', 'Australia/Victoria', 'Australia/West', 'Australia/Yancowinna', 'Brazil/Acre', 'Brazil/DeNoronha', 'Brazil/East', 'Brazil/West', 'CET', 'CST6CDT', 'Canada/Atlantic', 'Canada/Central', 'Canada/Eastern', 'Canada/Mountain', 'Canada/Newfoundland', 'Canada/Pacific', 'Canada/Saskatchewan', 'Canada/Yukon', 'Chile/Continental', 'Chile/EasterIsland', 'Cuba', 'EET', 'EST', 'EST5EDT', 'Egypt', 'Eire', 'Etc/GMT', 'Etc/GMT+0', 'Etc/GMT+1', 'Etc/GMT+10', 'Etc/GMT+11', 'Etc/GMT+12', 'Etc/GMT+2', 'Etc/GMT+3', 'Etc/GMT+4', 'Etc/GMT+5', 'Etc/GMT+6', 'Etc/GMT+7', 'Etc/GMT+8', 'Etc/GMT+9', 'Etc/GMT-0', 'Etc/GMT-1', 'Etc/GMT-10', 'Etc/GMT-11', 'Etc/GMT-12', 'Etc/GMT-13', 'Etc/GMT-14', 'Etc/GMT-2', 'Etc/GMT-3', 'Etc/GMT-4', 'Etc/GMT-5', 'Etc/GMT-6', 'Etc/GMT-7', 'Etc/GMT-8', 'Etc/GMT-9', 'Etc/GMT0', 'Etc/Greenwich', 'Etc/UCT', 'Etc/UTC', 'Etc/Universal', 'Etc/Zulu', 'Europe/Amsterdam', 'Europe/Andorra', 'Europe/Astrakhan', 'Europe/Athens', 'Europe/Belfast', 'Europe/Belgrade', 'Europe/Berlin', 'Europe/Bratislava', 'Europe/Brussels', 'Europe/Bucharest', 'Europe/Budapest', 'Europe/Busingen', 'Europe/Chisinau', 'Europe/Copenhagen', 'Europe/Dublin', 'Europe/Gibraltar', 'Europe/Guernsey', 'Europe/Helsinki', 'Europe/Isle_of_Man', 'Europe/Istanbul', 'Europe/Jersey', 'Europe/Kaliningrad', 'Europe/Kiev', 'Europe/Kirov', 'Europe/Kyiv', 'Europe/Lisbon', 'Europe/Ljubljana', 'Europe/London', 'Europe/Luxembourg', 'Europe/Madrid', 'Europe/Malta', 'Europe/Mariehamn', 'Europe/Minsk', 'Europe/Monaco', 'Europe/Moscow', 'Europe/Nicosia', 'Europe/Oslo', 'Europe/Paris', 'Europe/Podgorica', 'Europe/Prague', 'Europe/Riga', 'Europe/Rome', 'Europe/Samara', 'Europe/San_Marino', 'Europe/Sarajevo', 'Europe/Saratov', 'Europe/Simferopol', 'Europe/Skopje', 'Europe/Sofia', 'Europe/Stockholm', 'Europe/Tallinn', 'Europe/Tirane', 'Europe/Tiraspol', 'Europe/Ulyanovsk', 'Europe/Uzhgorod', 'Europe/Vaduz', 'Europe/Vatican', 'Europe/Vienna', 'Europe/Vilnius', 'Europe/Volgograd', 'Europe/Warsaw', 'Europe/Zagreb', 'Europe/Zaporozhye', 'Europe/Zurich', 'Factory', 'GB', 'GB-Eire', 'GMT', 'GMT+0', 'GMT-0', 'GMT0', 'Greenwich', 'HST', 'Hongkong', 'Iceland', 'Indian/Antananarivo', 'Indian/Chagos', 'Indian/Christmas', 'Indian/Cocos', 'Indian/Comoro', 'Indian/Kerguelen', 'Indian/Mahe', 'Indian/Maldives', 'Indian/Mauritius', 'Indian/Mayotte', 'Indian/Reunion', 'Iran', 'Israel', 'Jamaica', 'Japan', 'Kwajalein', 'Libya', 'MET', 'MST', 'MST7MDT', 'Mexico/BajaNorte', 'Mexico/BajaSur', 'Mexico/General', 'NZ', 'NZ-CHAT', 'Navajo', 'PRC', 'PST8PDT', 'Pacific/Apia', 'Pacific/Auckland', 'Pacific/Bougainville', 'Pacific/Chatham', 'Pacific/Chuuk', 'Pacific/Easter', 'Pacific/Efate', 'Pacific/Enderbury', 'Pacific/Fakaofo', 'Pacific/Fiji', 'Pacific/Funafuti', 'Pacific/Galapagos', 'Pacific/Gambier', 'Pacific/Guadalcanal', 'Pacific/Guam', 'Pacific/Honolulu', 'Pacific/Johnston', 'Pacific/Kanton', 'Pacific/Kiritimati', 'Pacific/Kosrae', 'Pacific/Kwajalein', 'Pacific/Majuro', 'Pacific/Marquesas', 'Pacific/Midway', 'Pacific/Nauru', 'Pacific/Niue', 'Pacific/Norfolk', 'Pacific/Noumea', 'Pacific/Pago_Pago', 'Pacific/Palau', 'Pacific/Pitcairn', 'Pacific/Pohnpei', 'Pacific/Ponape', 'Pacific/Port_Moresby', 'Pacific/Rarotonga', 'Pacific/Saipan', 'Pacific/Samoa', 'Pacific/Tahiti', 'Pacific/Tarawa', 'Pacific/Tongatapu', 'Pacific/Truk', 'Pacific/Wake', 'Pacific/Wallis', 'Pacific/Yap', 'Poland', 'Portugal', 'ROC', 'ROK', 'Singapore', 'Turkey', 'UCT', 'US/Alaska', 'US/Aleutian', 'US/Arizona', 'US/Central', 'US/East-Indiana', 'US/Eastern', 'US/Hawaii', 'US/Indiana-Starke', 'US/Michigan', 'US/Mountain', 'US/Pacific', 'US/Samoa', 'UTC', 'Universal', 'W-SU', 'WET', 'Zulu']] = None

@dataclass
class Reportschedule_update_RequestBody:
    data: Reportschedule_update_RequestBody_Data

@dataclass
class Textsnippet_create_RequestBody_Data:
    phrase: str
    snippet: str
    whole_word: Optional[bool] = None

@dataclass
class Textsnippet_create_RequestBody:
    data: Textsnippet_create_RequestBody_Data

@dataclass
class Textsnippet_update_RequestBody_Data:
    phrase: Optional[str] = None
    snippet: Optional[str] = None
    whole_word: Optional[bool] = None

@dataclass
class Textsnippet_update_RequestBody:
    data: Textsnippet_update_RequestBody_Data

@dataclass
class Task_create_RequestBody_Data_Assignee:
    id: int
    type: Literal['User', 'Contact']

@dataclass
class Task_create_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Task_create_RequestBody_Data_Task_type:
    id: Optional[int] = None

@dataclass
class Task_create_RequestBody_Data:
    assignee: Task_create_RequestBody_Data_Assignee
    description: str
    name: str
    cascading: Optional[bool] = None
    cascading_offset: Optional[int] = None
    cascading_offset_polarity: Optional[Literal['CalendarDays', 'CalendarWeeks', 'CalendarMonths', 'CalendarYears', 'BusinessDays']] = None
    cascading_offset_type: Optional[Literal['Before', 'After']] = None
    cascading_source: Optional[int] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    due_at: Optional[datetime.datetime] = None
    matter: Optional[Task_create_RequestBody_Data_Matter] = None
    notify_assignee: Optional[bool] = None
    notify_completion: Optional[bool] = None
    permission: Optional[Literal['private', 'public']] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    statute_of_limitations: Optional[bool] = None
    task_type: Optional[Task_create_RequestBody_Data_Task_type] = None
    time_estimated: Optional[int] = None

@dataclass
class Task_create_RequestBody:
    data: Task_create_RequestBody_Data

@dataclass
class Task_update_RequestBody_Data_Assignee:
    id: Optional[int] = None
    type: Optional[Literal['User', 'Contact']] = None

@dataclass
class Task_update_RequestBody_Data_Matter:
    id: Optional[int] = None

@dataclass
class Task_update_RequestBody_Data_Task_type:
    id: Optional[int] = None

@dataclass
class Task_update_RequestBody_Data:
    assignee: Optional[Task_update_RequestBody_Data_Assignee] = None
    cascading: Optional[bool] = None
    cascading_offset: Optional[int] = None
    cascading_offset_polarity: Optional[Literal['CalendarDays', 'CalendarWeeks', 'CalendarMonths', 'CalendarYears', 'BusinessDays']] = None
    cascading_offset_type: Optional[Literal['Before', 'After']] = None
    cascading_source: Optional[int] = None
    description: Optional[str] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    due_at: Optional[datetime.datetime] = None
    matter: Optional[Task_update_RequestBody_Data_Matter] = None
    name: Optional[str] = None
    notify_assignee: Optional[bool] = None
    notify_completion: Optional[bool] = None
    permission: Optional[Literal['private', 'public']] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    status: Optional[Literal['pending', 'in_progress', 'in_review', 'complete', 'draft']] = None
    task_type: Optional[Task_update_RequestBody_Data_Task_type] = None
    time_estimated: Optional[int] = None

@dataclass
class Task_update_RequestBody:
    data: Task_update_RequestBody_Data

@dataclass
class Calendarvisibility_update_RequestBody_Data:
    color: Optional[Literal['#367B9C', '#FFA5A4', '#83D17F', '#FFAC7B', '#8E3F64', '#C75300', '#009CEC', '#62D6B1', '#9EEDCB', '#F9A2C4', '#616161', '#BBDA81', '#DFD3F8', '#D6C4A5', '#FFD478', '#6AC9DE', '#EABBB0', '#BFC2E1', '#DADADA', '#CDE2F5']] = None
    visible: Optional[str] = None

@dataclass
class Calendarvisibility_update_RequestBody:
    data: Calendarvisibility_update_RequestBody_Data

@dataclass
class Tasktemplate_create_RequestBody_Data_Cascading_source:
    id: Optional[int] = None

@dataclass
class Tasktemplate_create_RequestBody_Data_Task_template_list:
    id: Optional[int] = None

@dataclass
class Tasktemplate_create_RequestBody_Data:
    name: str
    cascading: Optional[bool] = None
    cascading_offset: Optional[int] = None
    cascading_offset_polarity: Optional[Literal['Before', 'After']] = None
    cascading_offset_type: Optional[Literal['CalendarDays', 'CalendarWeeks', 'CalendarMonths', 'CalendarYears', 'BusinessDays']] = None
    cascading_source: Optional[Tasktemplate_create_RequestBody_Data_Cascading_source] = None
    description: Optional[str] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    private: Optional[bool] = None
    reminder_templates: Optional[List[dict]] = None
    task_template_list: Optional[Tasktemplate_create_RequestBody_Data_Task_template_list] = None

@dataclass
class Tasktemplate_create_RequestBody:
    data: Tasktemplate_create_RequestBody_Data

@dataclass
class Tasktemplate_update_RequestBody_Data_Cascading_source:
    id: Optional[int] = None

@dataclass
class Tasktemplate_update_RequestBody_Data:
    cascading: Optional[bool] = None
    cascading_offset: Optional[int] = None
    cascading_offset_polarity: Optional[Literal['Before', 'After']] = None
    cascading_offset_type: Optional[Literal['CalendarDays', 'CalendarWeeks', 'CalendarMonths', 'CalendarYears', 'BusinessDays']] = None
    cascading_source: Optional[Tasktemplate_update_RequestBody_Data_Cascading_source] = None
    description: Optional[str] = None
    description_text_type: Optional[Literal['plain_text', 'rich_text']] = None
    name: Optional[str] = None
    priority: Optional[Literal['High', 'Normal', 'Low']] = None
    private: Optional[bool] = None
    reminder_templates: Optional[List[dict]] = None

@dataclass
class Tasktemplate_update_RequestBody:
    data: Tasktemplate_update_RequestBody_Data

@dataclass
class Tasktemplatelist_copy_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Tasktemplatelist_copy_RequestBody_Data:
    description: Optional[str] = None
    name: Optional[str] = None
    practice_area: Optional[Tasktemplatelist_copy_RequestBody_Data_Practice_area] = None

@dataclass
class Tasktemplatelist_copy_RequestBody:
    data: Tasktemplatelist_copy_RequestBody_Data

@dataclass
class Tasktemplatelist_create_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Tasktemplatelist_create_RequestBody_Data:
    description: str
    name: str
    practice_area: Optional[Tasktemplatelist_create_RequestBody_Data_Practice_area] = None

@dataclass
class Tasktemplatelist_create_RequestBody:
    data: Tasktemplatelist_create_RequestBody_Data

@dataclass
class Tasktemplatelist_update_RequestBody_Data_Practice_area:
    id: Optional[int] = None

@dataclass
class Tasktemplatelist_update_RequestBody_Data:
    description: Optional[str] = None
    name: Optional[str] = None
    practice_area: Optional[Tasktemplatelist_update_RequestBody_Data_Practice_area] = None

@dataclass
class Tasktemplatelist_update_RequestBody:
    data: Tasktemplatelist_update_RequestBody_Data

@dataclass
class Tasktype_create_RequestBody_Data:
    name: str
    deleted_at: Optional[datetime.date] = None

@dataclass
class Tasktype_create_RequestBody:
    data: Tasktype_create_RequestBody_Data

@dataclass
class Tasktype_update_RequestBody_Data:
    deleted_at: Optional[datetime.date] = None
    name: Optional[str] = None

@dataclass
class Tasktype_update_RequestBody:
    data: Tasktype_update_RequestBody_Data

@dataclass
class Timer_create_RequestBody_Data_Activity:
    id: int

@dataclass
class Timer_create_RequestBody_Data:
    activity: Timer_create_RequestBody_Data_Activity

@dataclass
class Timer_create_RequestBody:
    data: Timer_create_RequestBody_Data

@dataclass
class Trustlineitem_update_RequestBody_Data:
    date: Optional[datetime.date] = None
    note: Optional[str] = None
    total: Optional[float] = None

@dataclass
class Trustlineitem_update_RequestBody:
    data: Trustlineitem_update_RequestBody_Data

@dataclass
class Trustrequest_create_RequestBody_Data:
    approved: bool
    client_id: int
    due_date: datetime.date
    issue_date: datetime.date
    trust_amount: float
    trust_type: Literal['client', 'matter']
    currency_id: Optional[int] = None
    matter: Optional[List[dict]] = None
    note: Optional[str] = None

@dataclass
class Trustrequest_create_RequestBody:
    data: Trustrequest_create_RequestBody_Data

@dataclass
class Webhook_create_RequestBody_Data:
    fields: str
    model: Literal['activity', 'bill', 'calendar_entry', 'clio_payments_payment', 'communication', 'contact', 'document', 'folder', 'matter', 'task']
    url: str
    events: Optional[List[Literal['created', 'updated', 'deleted', 'matter_opened', 'matter_pended', 'matter_closed']]] = None
    expires_at: Optional[datetime.datetime] = None

@dataclass
class Webhook_create_RequestBody:
    data: Webhook_create_RequestBody_Data

@dataclass
class Webhook_update_RequestBody_Data:
    events: Optional[List[Literal['created', 'updated', 'deleted', 'matter_opened', 'matter_pended', 'matter_closed']]] = None
    expires_at: Optional[datetime.datetime] = None
    fields: Optional[str] = None
    model: Optional[Literal['activity', 'bill', 'calendar_entry', 'clio_payments_payment', 'communication', 'contact', 'document', 'folder', 'matter', 'task']] = None
    url: Optional[str] = None

@dataclass
class Webhook_update_RequestBody:
    data: Webhook_update_RequestBody_Data

@dataclass
class Comment_create_RequestBody_Data_Item:
    id: int

@dataclass
class Comment_create_RequestBody_Data:
    item: Comment_create_RequestBody_Data_Item
    message: str

@dataclass
class Comment_create_RequestBody:
    data: Comment_create_RequestBody_Data

@dataclass
class Comment_update_RequestBody_Data_Item:
    id: Optional[int] = None

@dataclass
class Comment_update_RequestBody_Data:
    item: Optional[Comment_update_RequestBody_Data_Item] = None
    message: Optional[str] = None

@dataclass
class Comment_update_RequestBody:
    data: Comment_update_RequestBody_Data

@dataclass
class Documentarchive_create_RequestBody_Data:
    items: List[dict]

@dataclass
class Documentarchive_create_RequestBody:
    data: Documentarchive_create_RequestBody_Data

@dataclass
class Document_copy_RequestBody_Data_Parent:
    id: int
    type: Literal['Document', 'Folder', 'Contact', 'Matter']

@dataclass
class Document_copy_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Document_copy_RequestBody_Data:
    parent: Document_copy_RequestBody_Data_Parent
    communication_id: Optional[int] = None
    document_category: Optional[Document_copy_RequestBody_Data_Document_category] = None
    external_properties: Optional[List[dict]] = None
    filename: Optional[str] = None
    name: Optional[str] = None
    received_at: Optional[datetime.datetime] = None

@dataclass
class Document_copy_RequestBody:
    data: Document_copy_RequestBody_Data

@dataclass
class Document_create_RequestBody_Data_Parent:
    id: int
    type: Literal['Document', 'Folder', 'Contact', 'Matter']

@dataclass
class Document_create_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Document_create_RequestBody_Data:
    name: str
    parent: Document_create_RequestBody_Data_Parent
    communication_id: Optional[int] = None
    content_type: Optional[str] = None
    document_category: Optional[Document_create_RequestBody_Data_Document_category] = None
    external_properties: Optional[List[dict]] = None
    filename: Optional[str] = None
    multiparts: Optional[List[dict]] = None
    received_at: Optional[datetime.datetime] = None

@dataclass
class Document_create_RequestBody:
    data: Document_create_RequestBody_Data

@dataclass
class Document_update_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Document_update_RequestBody_Data_Parent:
    id: Optional[int] = None
    type: Optional[Literal['Document', 'Folder', 'Contact', 'Matter']] = None

@dataclass
class Document_update_RequestBody_Data:
    communication_id: Optional[int] = None
    copy_version: Optional[bool] = None
    document_category: Optional[Document_update_RequestBody_Data_Document_category] = None
    external_properties: Optional[List[dict]] = None
    fully_uploaded: Optional[bool] = None
    multiparts: Optional[List[dict]] = None
    name: Optional[str] = None
    parent: Optional[Document_update_RequestBody_Data_Parent] = None
    received_at: Optional[datetime.datetime] = None
    restore: Optional[bool] = None
    uuid: Optional[str] = None

@dataclass
class Document_update_RequestBody:
    data: Document_update_RequestBody_Data

@dataclass
class Documentautomation_create_RequestBody_Data_Document_template:
    id: int

@dataclass
class Documentautomation_create_RequestBody_Data_Matter:
    id: int

@dataclass
class Documentautomation_create_RequestBody_Data:
    document_template: Documentautomation_create_RequestBody_Data_Document_template
    filename: str
    formats: List[Literal['pdf', 'original']]
    matter: Documentautomation_create_RequestBody_Data_Matter

@dataclass
class Documentautomation_create_RequestBody:
    data: Documentautomation_create_RequestBody_Data

@dataclass
class Documentcategory_create_RequestBody_Data:
    name: str

@dataclass
class Documentcategory_create_RequestBody:
    data: Documentcategory_create_RequestBody_Data

@dataclass
class Documentcategory_update_RequestBody_Data:
    name: Optional[str] = None

@dataclass
class Documentcategory_update_RequestBody:
    data: Documentcategory_update_RequestBody_Data

@dataclass
class Documenttemplate_create_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Documenttemplate_create_RequestBody_Data:
    file: str
    document_category: Optional[Documenttemplate_create_RequestBody_Data_Document_category] = None
    filename: Optional[str] = None

@dataclass
class Documenttemplate_create_RequestBody:
    data: Documenttemplate_create_RequestBody_Data

@dataclass
class Documenttemplate_update_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Documenttemplate_update_RequestBody_Data:
    document_category: Optional[Documenttemplate_update_RequestBody_Data_Document_category] = None
    file: Optional[str] = None
    filename: Optional[str] = None

@dataclass
class Documenttemplate_update_RequestBody:
    data: Documenttemplate_update_RequestBody_Data

@dataclass
class Folder_create_RequestBody_Data_Parent:
    id: int
    type: Literal['Folder', 'Contact', 'Matter']

@dataclass
class Folder_create_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Folder_create_RequestBody_Data:
    name: str
    parent: Folder_create_RequestBody_Data_Parent
    document_category: Optional[Folder_create_RequestBody_Data_Document_category] = None
    external_properties: Optional[List[dict]] = None
    restore: Optional[bool] = None

@dataclass
class Folder_create_RequestBody:
    data: Folder_create_RequestBody_Data

@dataclass
class Folder_update_RequestBody_Data_Document_category:
    id: Optional[int] = None

@dataclass
class Folder_update_RequestBody_Data_Parent:
    id: Optional[int] = None
    type: Optional[Literal['Folder', 'Contact', 'Matter']] = None

@dataclass
class Folder_update_RequestBody_Data:
    document_category: Optional[Folder_update_RequestBody_Data_Document_category] = None
    external_properties: Optional[List[dict]] = None
    name: Optional[str] = None
    parent: Optional[Folder_update_RequestBody_Data_Parent] = None
    restore: Optional[bool] = None

@dataclass
class Folder_update_RequestBody:
    data: Folder_update_RequestBody_Data

