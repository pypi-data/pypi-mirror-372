# Easy to use python client for the Clio Manage API 

This API client is designed to interact with the Clio API, providing robust handling for HTTP request methods, query parameters, payload validation, and dynamic endpoint management.

### Installation

```bash
pip install clio-manage-api-client
```

### Initialization
```python
import clio-manage-api-client as Clio

client = Clio.Manage(access_token="your_access_token") # 'store_responses=True' for sqlite response handler
```
## Key Features

1. **Dynamic Endpoint Management**:
   - Dynamically initializes and manages endpoints using metadata from the `models.endpoints` module.
   - Supports operations like `index`, `show`, `post`, `patch`, `delete` as well as sub-methods for relational endpoints (Explained Below)
   - Endpoints that return content can use the `download` method. Output path can be provided in the call or set within the client

2. **Integrated Query Parameter and Payload Handling**:
   - Automatically validates, converts, and processes query parameters and payload data.
   - Ensures type safety and required field validation for all inputs.
   - Query parameters are processed first and removed from `kwargs`. Remaining `kwargs` are processed for payload data.

3. **Pagination Support**:
   - Handles paginated responses seamlessly when using the `all` method.
   - Automatically appends results from all pages.

4. **Reserved Keywords and Parameter Mappings**:
   - Handles reserved keywords and endpoint-specific parameters via a `mappings` dictionary.
   - Reserved keywords such as `from` and `X-API-VERSION` are mapped to their correct representations (e.g., `from_` to `from`).
   - Parameters like `matter_id` and `id` are interchangeable, ensuring ease of use for endpoints that deviate from the general schema.

5. **Dynamic Endpoint Resolution**:
   - Determines whether to call the `index` or `show` endpoint based on the presence of `id` in `kwargs`.
   - For example:
     - `client.get.matters(id=123)` calls the `show` endpoint.
     - `client.get.matters(limit=10)` calls the `index` endpoint.

6. **Rate Limiting**:
   - Enforces rate limits using the `RateMonitor` class to ensure compliance with API restrictions.

7. **Error Reporting**:
   - Provides detailed validation error messages when inputs do not meet the expected types or requirements.

---
# Examples
- **Models are now generated when the client is first ran directly from the latest API documentation**
- **The Openapi spec file that is used to generate the dataclasses is now stored in the models/ subdirectory**
- **Get the latest changes made to the API by using the update.py script. Existing model classes will be backed up**

### Single Request Example

```python
response = client.get.matters() # Default limit is 200
print(json.dumps(response, indent=2))
```

### Relational Endpoint Example

```python
related_contacts = client.get.matters.related_contacts(id=12345, fields="id,name")
print(json.dumps(related_contacts, indent=2))
```

### Fetch All Paginated Results

```python
response_all = client.all.matters(fields="id,name")
print(f"Total items retrieved: {len(response_all['data'])}")
print(json.dumps(response_all, indent=2))
```

### Request With Generated Fields

**Using all**
```python
# Returns data from all available non nested fields
response = client.get.matters(fields="all", limit=10)
print(json.dumps(response, indent=2))

# With nested fields
response = client.get.matters(fields="all,client{all}", limit=10)
print(json.dumps(response, indent=2))

# Returns the id and etag of every nested resource within the endpoint
response = client.get.matters(fields="all_ids", limit=10)
print(json.dumps(response, indent=2))

```

### Datetime and Timedeltas

```python
# Absolute dates
one_year_ago = date.today() - timedelta(days=365)
response = client.all.matters(limit=200, open_date__= f'>={one_year_ago}', order="open_date(asc)", fields="all,client{name},practice_area{name,category},responsible_attorney{name}")
print(json.dumps(response, indent=2))

# Helper functions: end_of_the_month()
entries = client.all.calendar_entries(fields="start_at,end_at,all_day,location,description,summary,attendees{name}", from_=datetime.now(), to=end_of_the_month())
print(json.dumps(response, indent=2))
```

### Exporting

**To Excel Spreadsheet:**

**Requires pandas < 2.0 and openpyxl**
```python
save_to_xlsx(client.all.contacts(fields="all,custom_field_values{field_name,value}"), "contacts.xlsx")
```
---

## Logical Argument and Type Conversion

**Example Endpoint**:
- **`https://app.clio.com/api/v4/matters/{matter_id}/client.json`**
- **`https://app.clio.com/api/v4/matters/{id}.json`**

Both `matter_id` and `id` can be used interchangeably. The client automatically maps `matter_id` to `id` for consistency.

## Example Usage

```python
# Calls the 'show' endpoint for a specific matter
response = client.get.matters(id=123)

# Calls the 'client' relation endpoint for a specific matter
response = client.get.matters.client(matter_id=123)

# Calls the 'client' relation endpoint for a specific matter
response = client.get.matters.client(id=123)
```

## Arrays(Needs more testing):
- **Can be provided using by including a double underscore**
- **Any text after the underscores get converted into a query parameter keyword**
   - **`ids__ = [123,456,789]` gets converted to `ids[]=123&ids[]=456&ids[]=789`**
   - **`jurisdiction__id = 123` gets converted to `jurisdiction[id]=123`**

---


## Reserved Keywords and Mapping

The client automatically handles reserved keywords and non-standard endpoint parameters through a predefined `mappings` dictionary. This ensures compatibility and ease of use for all endpoints.

### Example Mappings

```python
mappings = {
    "X_API_VERSION": "X-API-VERSION",
    "from_": "from", 
    "ids__": "ids",
    "jurisdiction__id": "jurisdiction[id]",
    "service_type__id": "service_type[id]",
    "trigger__id": "trigger[id]",
}
```

## Internal Design

### Endpoint Resolution

- The `show` endpoint is prioritized if `id` is present in the `kwargs`.
- The `index` endpoint is called if `id` is not provided.

### `_request_handler`

Handles requests, including:
- Pagination support.
- Query parameter and payload validation.
- Dynamic path formatting with provided arguments.

---

## Known Issues

- On some endpoints, DELETE throws an HTTPEXCEPTION but the command completes successfully in Clio. This can be circumvented by using a try/except block inside the running loop
  
## License

This project is licensed under the MIT License.
