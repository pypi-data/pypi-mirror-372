import os
import sys
import json
import threading
import queue
import sqlite3
import logging

import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# Set of SQL reserved keywords to check against
SQL_RESERVED_KEYWORDS = {
    "default", "order", "group", "index", "table", "values", "key", "primary"
}
    
from ..models.fields import *
from ..models.components import *
from .db_generator import generate_database

def escape_identifier(identifier):
    """
    Escapes SQL reserved keywords by surrounding them with double quotes.
    """
    return f'"{identifier}"' if identifier.lower() in SQL_RESERVED_KEYWORDS else identifier


class ResponseWriter:
    def __init__(self, db_path="database.sqlite"):
        """Initialize the database connection and create table if it doesn't exist."""
        self.db_path = db_path
        self._ensure_db_exists()
        self._initialize_db()

    def _ensure_db_exists(self):
        """Check if the database path exists; if not, generate the database."""
        db_dir = os.path.dirname(self.db_path)
        db_name = os.path.basename(self.db_path)
        
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)  # Ensure directory exists
        
        if not os.path.exists(self.db_path):
            generate_database(db_name=db_name)
            
    def _initialize_db(self):
        """Creates the responses table if it does not exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                status_code INTEGER,
                response_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def process_response(self, response_model, response_data):
        """
        Processes the API response by first writing non-nested fields and then handling nested fields separately.

        Args:
            response_model: The dataclass model representing the response structure.
            response_data: A list of dictionaries received from the API.
        """
        if not isinstance(response_data, list):
            raise ValueError(f"Expected response_data to be a list of dictionaries, got {type(response_data).__name__}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Write non-nested fields (write_data will handle filtering internally)
                main_table_name = str(response_model.__name__).replace("Fields", "base")
                self.write_data(main_table_name, response_data, conn, cursor)
                
                # Process nested fields
                for idx, item in enumerate(response_data):
                    for key, value in item.items():
                        try:
                            if not isinstance(value, (dict, list)):
                                continue  # Skip non-nested fields
                        
                            nested_model = getattr(response_model, key, None)

                            if nested_model is None:
                                # print(f"Skipping unknown nested field: {key}")
                                continue

                            nested_table_name = str(nested_model.__name__)

                            # Handle list of dictionaries (nested data)
                            if isinstance(value, list) and all(isinstance(entry, dict) for entry in value):
                                self.write_data(nested_table_name, value, conn, cursor)

                                # Process the endpoint relationships
                                for sub_item in value:
                                    if "id" in sub_item:
                                        self._update_endpoint_relationships(main_table_name, item["id"], key, sub_item["id"], conn, cursor)

                            # Handle single dictionary (nested data)
                            elif isinstance(value, dict):
                                self.write_data(nested_table_name, [value], conn, cursor)

                                if "id" in value:
                                    self._update_endpoint_relationships(main_table_name, item["id"], key, value["id"], conn, cursor)

                            else:
                                print(f"Warning: Unexpected data type for key '{key}': {type(value).__name__}")

                        except sqlite3.Error as e:
                            logging.error(f"Database error occurred: {e}")
                        except Exception as e:
                            logging.error(f"Unexpected error: {e}")
                
                print("Committing to db")
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Error accessing SQLite database: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")    
                     
    def _filter_data(self, data):
        """
        Removes nested keys and null (None) values from the dictionary.
        """
        return {k: v for k, v in data.items() if not isinstance(v, dict) and v is not None}

    def write_data(self, table_name, response_json_list, conn, cursor):
        """
        Requires list of dictionaries.
        """
        if not response_json_list:
            return "No data to write."

        # Escape table name if necessary
        table_name = escape_identifier(table_name)

        # Filter records to remove nested keys and null values
        filtered_data_list = []

        for record in response_json_list:
            filtered = self._filter_data(record)

            # Serialize list or dict fields to strings for SQLite TEXT columns
            for k, v in filtered.items():
                if isinstance(v, (list, dict)):
                    filtered[k] = json.dumps(v)

            filtered_data_list.append(filtered)
    
        cursor.execute(f'PRAGMA table_info({table_name})')
        table_info = cursor.fetchall()

        if not table_info:
            raise ValueError(f"Table '{table_name}' does not exist.")

        primary_key = None
        columns = []
        for col in table_info:
            col_id, col_name, col_type, nullable, default_value, is_primary = col
            escaped_col_name = escape_identifier(col_name)
            columns.append(escaped_col_name)
            if is_primary == 1:
                primary_key = escaped_col_name

        if not primary_key:
            raise ValueError(f"Table '{table_name}' does not have a primary key.")

        # Get existing records in a single query
        record_ids = [record.get(primary_key.strip('"')) for record in filtered_data_list if record.get(primary_key.strip('"'))]
        existing_data_map = {}

        if record_ids:
            placeholders = ', '.join(['?'] * len(record_ids))
            query = f'SELECT * FROM {table_name} WHERE {primary_key} IN ({placeholders})'
            cursor.execute(query, record_ids)
            existing_rows = cursor.fetchall()
            existing_data_map = {row[columns.index(primary_key)]: dict(zip(columns, row)) for row in existing_rows}

        update_queries = []
        insert_queries = []
        for record in filtered_data_list:
            record_id = record.get(primary_key.strip('"'))
            if not record_id:
                logging.warning(f"Skipping record without primary key: {record}")
                continue

            escaped_columns = [escape_identifier(col) for col in record.keys()]

            if record_id in existing_data_map:
                existing_row = existing_data_map[record_id]

                # Merge existing data with new data (only update provided fields if different)
                updated_data = {
                    escape_identifier(key): value for key, value in record.items()
                    if value is not None and existing_row.get(key) != value and key in columns
                }

                if updated_data:
                    updated_columns = list(updated_data.keys())
                    update_placeholders = ", ".join(f"{col} = ?" for col in updated_columns)
                    update_values = list(updated_data.values()) + [record_id]

                    update_sql = f"""
                        UPDATE {table_name}
                        SET {update_placeholders}
                        WHERE {primary_key} = ?
                    """
                    update_queries.append((update_sql, update_values))
                    logging.debug(f"Updating record with {primary_key}={record_id}")

            else:
                provided_columns = [escape_identifier(col) for col in record if col in columns]
                placeholders = ", ".join([":" + col.strip('"') for col in provided_columns])


                column_names = ", ".join(provided_columns)

                sql_query = f"""
                    INSERT INTO {table_name} ({column_names})
                    VALUES ({placeholders})
                """
                insert_queries.append((sql_query, record))
                logging.debug(f"Inserting new record with {primary_key}={record_id}")

        for sql, values in update_queries:
            cursor.executemany(sql, [values])
        for sql, values in insert_queries:
            cursor.executemany(sql, [values])

        conn.commit()
        return f"Successfully processed {len(filtered_data_list)} records for {table_name}."

    def _update_endpoint_relationships(self, table_name, record_id, nested_key, nested_id, conn, cursor):
        if not record_id or not nested_id:
            logging.warning(f"Skipping invalid record_id={record_id} or nested_id={nested_id} for '{nested_key}' in '{table_name}'.")
            return

        # Convert record_id and nested_id to string for consistency
        record_id_str, nested_id_str = str(record_id), str(nested_id)

        # Fetch existing JSON field
        cursor.execute("SELECT endpoint_relationships FROM {} WHERE id = ?".format(table_name), (record_id_str,))
        row = cursor.fetchone()

        if row is None:
            logging.debug(f"No record found with ID {record_id} in table {table_name}, creating new record.")
            new_relationships = {nested_key: [nested_id_str]}
            cursor.execute(f"""
                INSERT INTO {table_name} (id, endpoint_relationships)
                VALUES (?, ?)
            """, (record_id_str, json.dumps(new_relationships)))
            logging.debug(f"Inserted new record with ID {record_id} and endpoint_relationships {new_relationships}")

        else:
            current_json = row[0] or '{}'
            relationships = json.loads(current_json)

            # Ensure the nested key exists
            if nested_key not in relationships:
                relationships[nested_key] = []

            # Check if the nested_id is already present
            if nested_id_str not in map(str, relationships[nested_key]):
                relationships[nested_key].append(nested_id if isinstance(nested_id, (int, float)) else nested_id_str)
                updated_json = json.dumps(relationships)

                cursor.execute(f"""
                    UPDATE {table_name}
                    SET endpoint_relationships = ?
                    WHERE id = ?
                """, (updated_json, record_id_str))

                logging.debug(f"Updated {table_name} (ID: {record_id}) with key '{nested_key}' and value '{nested_id}'")
            else:
                logging.debug(f"Nested ID '{nested_id}' already exists for key '{nested_key}', skipping update.")

class ResponseHandler:
    def __init__(self, db_path="database.sqlite"):
        
        self.db_path = db_path
        self.response_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.response_writer = ResponseWriter(db_path)
        
        self.processing_count = 0  # Track active processing count
        self.lock = threading.Lock()
        
        self.thread = threading.Thread(target=self._process_responses, daemon=True)
        self.thread.start()

    def add_response(self, response, endpoint_metadata):
        with self.lock:
            self.processing_count += 1
        self.response_queue.put((response, endpoint_metadata))

    def _process_responses(self):
        """Continuously processes responses from the queue while the thread is alive."""
        while not self.stop_event.is_set():
            try:
                response_item = self.response_queue.get(timeout=5)
                if response_item:
                    response, metadata = response_item

                    try:
                        self._handle_response(response, metadata)
                    except Exception as e:
                        print(f"Error while processing response: {e}")

                    finally:
                        with self.lock:
                            self.processing_count -= 1  # Always decrement, even on errors
                        self.response_queue.task_done()  # Ensure task is marked as done

            except queue.Empty:
                if self.stop_event.is_set():
                    break  # Exit when stop event is set
                continue
            except Exception as e:
                print(f"Error while processing response: {e}")

    def _handle_response(self, response, metadata):
        """
        Handles API response, only raising exceptions for actual errors.
        
        Args:
            response: The API response object.
            metadata: Additional metadata related to the request.
        
        Returns:
            None
        """
        # Successful response
        if 200 <= response.status_code < 300:
            response_model = metadata.get('field_model')
            data = response.json().get('data')

            # Ensure `data` is always a list
            if isinstance(data, dict):
                data = [data]
            print("Success:", response_model)
            self.response_writer.process_response(response_model, data)
        
        # Handle known non-error responses that shouldn't raise exceptions
        elif response.status_code in {204, 202, 304}:  # No Content, Accepted, Not Modified
            print(f"Non-error response received: {response.status_code} - {response.reason}")

        # Raise an exception only for actual error status codes (4xx, 5xx)
        elif 400 <= response.status_code < 600:
            print("Error:", response.status_code, response.text)
            response.raise_for_status()  # Raises an HTTPError exception

        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")

    def wait_for_completion(self):
        print("Waiting for all database operations to complete...")
        self.response_queue.join()  # Ensures the queue is fully processed
        while True:
            with self.lock:
                if self.processing_count == 0:
                    break
            threading.Event().wait(0.5)  # Small wait to reduce CPU usage
        print("All processing completed.")
        
    def export_to_excel(self, output_path="database_export.xlsx"):
        """
        Exports an SQLite database to an Excel spreadsheet with each table in a separate sheet.
        """
        self.wait_for_completion()
        print("Exporting database to Excel...")
        
        db_path = self.db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file '{db_path}' not found.")

        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get the list of all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            if not tables:
                print("No tables found in the database.")
                return

            # Create an Excel writer object
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                for table in tables:
                    table_name = table[0]
                    print(table_name)
                    print(f"Exporting table: {table_name}")

                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    
                    if df.empty:
                        print(f"Skipping empty table: {table_name}")
                        continue  # Skip this table if it's empty
        
                    #Format table name
                    table_name = table_name.replace("_base", "")
                    
                    #Resize if name contains more than 31 characters
                    if len(table_name) > 31:
                        table_name = table_name[:31]
                        
                    df.to_excel(writer, sheet_name=table_name, index=False)

                    # Apply formatting to the column headers
                    workbook  = writer.book
                    worksheet = writer.sheets[table_name]
                    header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)

            print(f"Database exported successfully to {output_path}")

        except sqlite3.Error as e:
            print(f"Error accessing SQLite database: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            conn.close()
        
    def stop_processing(self):
        print("Stopping response handler...")
        self.stop_event.set()
        self.response_queue.put(None)  # Wake up the thread if it's waiting
        self.thread.join()
        print("Response handler stopped.")