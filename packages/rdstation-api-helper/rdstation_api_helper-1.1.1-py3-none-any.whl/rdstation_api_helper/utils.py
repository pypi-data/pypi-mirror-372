"""
Utility functions for the RD Station API driver module.
"""
import json
import logging
import os
import pandas as pd
import requests
import threading
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from sqlalchemy import Engine, create_engine, Table, MetaData, select
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Any, Optional

from .exceptions import ConfigurationError


def load_credentials(config_path: Optional[str] = None) -> dict[str, Any]:
    """
    Load RD Station API credentials from JSON file.

    Args:
        config_path (Optional[str]): Path to the credentials file. If None, tries default locations.

    Returns:
        dict[str, Any]: Loaded credentials configuration

    Raises:
        FileNotFoundError: If credentials file is not found
        json.JSONDecodeError: If JSON parsing fails
    """
    default_paths = [
        os.path.join("secrets", "fb_business_config.json"),
        os.path.join(os.path.expanduser("~"), ".fb_business_config.json"),
        "fb_business_config.json"
    ]

    if config_path:
        paths_to_try = [config_path]
    else:
        paths_to_try = default_paths

    for path in paths_to_try:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    credentials = json.load(f)

                if not credentials:
                    raise ConfigurationError(f"Credentials file {path} is empty")

                if not isinstance(credentials, dict):
                    raise ConfigurationError(f"Credentials file {path} must contain a JSON dictionary")

                return credentials

            except json.JSONDecodeError as e:
                logging.error(f"Error parsing JSON file {path}: {e}")
                raise ConfigurationError(
                    f"Invalid JSON format in credentials file {path}",
                    original_error=e
                ) from e
            except IOError as e:
                raise ConfigurationError(
                    f"Failed to read credentials file {path}",
                    original_error=e
                ) from e

    raise ConfigurationError(
        f"Could not find credentials file in any of these locations: {paths_to_try}"
    )


def create_output_directory(path: str) -> Path:
    """
    Create output directory if it doesn't exist.

    Args:
        path (str): Directory path to create

    Returns:
        Path: Path object for the created directory
    """
    output_path = Path(path)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def load_from_json_file(filepath: str) -> list[dict[str, Any]]:

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    logging.info(f"Data loaded from `{filepath}`")
    return data


def save_to_json_file(json_data: list[dict[str, Any]], filepath: str) -> None:

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)

    logging.info(f"Data saved to `{filepath}`")


def append_to_json_file(json_data: list[dict[str, Any]], filepath: str) -> None:
    try:
        if os.path.exists(filepath):
            with open(filepath, "r+", encoding="utf-8") as f:

                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logging.info(
                        "JSON decode error: File is empty or invalid. Aborting operation."
                    )
                    return

                if not isinstance(data, list):
                    logging.info("Existing JSON structure is not a list. Aborting operation.")
                    return
                logging.info(f"Found {len(data)} records in the file.")

                if isinstance(json_data, list):
                    data.extend(json_data)
                    logging.info(f"Appending {len(json_data)} record(s).")

                else:
                    data.append(json_data)
                    logging.info("Appending 1 record.")

                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            logging.info(
                f"Records [{len(data):,}] appended successfully to file `{filepath}`."
            )

        else:
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(json_data, list):
                    data = json_data
                    logging.info(
                        f"Creating new file `{filepath}` and adding {len(json_data)} record(s)."
                    )
                else:
                    data = [json_data]
                    logging.info(f"Creating new `{filepath}` file and adding 1 record.")
                json.dump(data, f, indent=2)
            logging.info("File created and records added successfully.")

    except Exception as e:
        logging.info("An error occurred:", e)


def parallel_decorator(max_workers: int = 5, sleep_time: float = 10, key_parameter: str = "uuid"):
    """
    Decorator to parallelize a functions that fetches data for a single item (uuid).
    The decorated function should return (status_code, data).
    The decorated function can be called with a list of dicts (each with key_parameter),
    and will return a list of results, handling 429/5xx/network errors with a barrier.
    """
    def decorator(inner_method):
        @wraps(inner_method)
        def wrapper(self, key_list, *args, **kwargs):
            """
            key_list: list of key values (e.g., uuids or emails)
            """
            all_results = []
            item_count = 0
            list_length = len(key_list)

            # Shared event and lock for barrier
            sleep_event = threading.Event()
            sleep_lock = threading.Lock()
            sleep_until = [0]  # mutable container for timestamp

            def barrier(wait_time):
                with sleep_lock:
                    now = time.time()
                    target = now + wait_time
                    if target > sleep_until[0]:
                        sleep_until[0] = target
                    sleep_event.set()
                while True:
                    now = time.time()
                    remaining = sleep_until[0] - now
                    if remaining <= 0:
                        break
                    time.sleep(min(1, remaining))
                sleep_event.clear()

            def fetch(key_value):
                while True:
                    try:
                        code, data = inner_method(self, key_value, *args, **kwargs)
                        status_code = int(code)
                    except requests.exceptions.RequestException as e:
                        logging.warning(
                            f"Network error for {key_value}: {e}. Sleeping all workers for {sleep_time} sec."
                        )
                        barrier(sleep_time)
                        continue
                    except Exception as e:
                        logging.warning(f"Unexpected error for {key_value}: {e}")
                        return None

                    if status_code == 200:
                        if data:
                            if isinstance(data, dict):
                                data[key_parameter] = key_value
                            elif isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict):
                                        item[key_parameter] = key_value
                        return data

                    elif status_code == 429 or (500 <= status_code < 600):
                        logging.warning(
                            f"Worker for {key_value} got status {status_code}, sleeping all workers for {sleep_time} sec."  # noqa
                        )
                        barrier(sleep_time)
                    else:
                        logging.info(
                            f"Failed to fetch {key_value}, HTTP {status_code}. Skipping."
                        )
                        return None

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(fetch, str(key_value)): key_value for key_value in key_list}
                for future in as_completed(futures):
                    result = future.result()

                    contact_id = None

                    if result:
                        if isinstance(result, dict):
                            all_results.append(result)
                            contact_id = result.get(key_parameter, 'N/A')
                        elif isinstance(result, list):
                            all_results.extend(result)
                            contact_id = result[0].get(key_parameter, 'N/A')

                    item_count += 1

                    logging.info(
                        f"{item_count}/{list_length} - fetched {inner_method.__name__} for contact '{contact_id}'")

            logging.info(f"Fetched {len(all_results)} total items.")

            return None, all_results
        return wrapper
    return decorator


def save_backup_files(engine: Engine) -> None:

    output_path = Path("backups")
    output_path.mkdir(parents=True, exist_ok=True)

    df = pd.read_sql_table("rd_segmentations", engine, schema="public")
    data = df.to_dict(orient="records")
    with open("./backups/rd_segmentations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_segmentation_contacts", engine, schema="public")
    data = df.to_dict(orient="records")
    with open("./backups/rd_segmentation_contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_contacts", engine, schema="public")
    data = df.to_dict(orient="records")
    with open("./backups/rd_contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_contact_funnel_status", engine, schema="public")
    data = df.to_dict(orient="records")
    with open("./backups/rd_contact_funnel_status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)


@dataclass
class PgConfig:
    """
    PostgreSQL database configuration dataclass.

    This class encapsulates all PostgreSQL connection parameters, automatically
    loading them from environment variables with sensible defaults where applicable.

    Attributes:
        host: PostgreSQL server hostname or IP address
        port: PostgreSQL server port number (default: "5432")
        user: Database username for authentication
        password: Database password for authentication
        dbname: Name of the target database

    Environment Variables:
        PGHOST: Sets the host attribute
        PGPORT: Sets the port attribute (default: "5432")
        PGDATABASE: Sets the dbname attribute
        PGUSER: Sets the user attribute
        PGPASSWORD: Sets the password attribute

    Example:
        >>> config = PgConfig()
        >>> print(config.uri())
        'postgresql+psycopg2://user:pass@localhost:5432/mydb'

    Note:
        The port is stored as a string to match the format expected by
        database URI construction and environment variable parsing.
    """
    host: str = os.getenv('PGHOST', '')
    port: str = os.getenv('PGPORT', '5432')
    dbname: str = os.getenv('PGDATABASE', '')
    user: str = os.getenv('PGUSER', '')
    password: str = os.getenv('PGPASSWORD', '')

    def uri(self) -> str:
        """
        Generate a PostgreSQL connection URI string (Uniform Resource Identifier).

        Constructs a SQLAlchemy-compatible PostgreSQL connection URI using the
        psycopg2 driver from the configured connection parameters.

        Returns:
            A PostgreSQL connection URI string in the format:
            'postgresql+psycopg2://user:password@host:port/database'

        Example:
            >>> config = PgConfig()
            >>> config.host = "localhost"
            >>> config.dbname = "mydb"
            >>> config.user = "myuser"
            >>> config.password = "mypass"
            >>> config.uri()
            'postgresql+psycopg2://myuser:mypass@localhost:5432/mydb'

        Note:
            This method does not perform any validation of the connection
            parameters. Ensure all required fields (host, user, password, dbname)
            are set before using the returned URI for database connections.
        """
        return f'postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}'

    def __str__(self) -> str:
        """
        Return a string representation of the configuration.

        Returns a formatted string showing the connection details with
        the password masked for security.

        Returns:
            A string representation with masked password.

        Example:
            >>> config = PgConfig()
            >>> str(config)
            'PgConfig(host=localhost, port=5432, user=myuser, password=****, dbname=mydb)'
        """
        masked_password = '****' if self.password else ''
        return (f'PgConfig(host={self.host}, port={self.port}, user={self.user}, '
                f'password={masked_password}, dbname={self.dbname})')


class PostgresDB():

    def __init__(self, config: Optional[PgConfig] = None, engine: Optional[Engine] = None) -> None:
        """
        Initialize PostgreSQL upsert client.

        Args:
            config: PostgreSQL configuration object. If None, default config will be used.
            engine: SQLAlchemy engine instance. If provided, config will be ignored.
            debug: Enable debug logging for detailed operation information.

        Raises:
            ValueError: If neither config nor engine is provided and default config fails.
            PermissionError: If database user lacks CREATE TEMP TABLE privileges.
        """
        if engine:
            self.engine = engine
            logging.info("PostgreSQL upsert client initialized with provided engine")
        else:
            self.config = config or PgConfig()
            self.engine = create_engine(self.config.uri())
            logging.info(f"PostgreSQL upsert client initialized with config: {self.config.host}:{self.config.port}")

        self.Base = declarative_base()

    def create_engine(self) -> Engine:
        """
        Create a new SQLAlchemy engine using default configuration.

        Returns:
            SQLAlchemy Engine instance configured with default PostgreSQL settings.
        """
        uri = PgConfig().uri()
        logging.debug(f"Creating new database engine with URI: {uri}")
        return create_engine(uri)

    def create_tables(self) -> None:
        self.Base.metadata.create_all(self.engine)

    def save_to_sql(self, json_data: list[dict[str, Any]], dataclass,
                    upsert_values: bool = False, flatten: bool = False) -> None:

        logging.info(f"Inserting data for {dataclass.__name__}...")

        if not json_data:
            logging.info(f"No data to insert for {dataclass.__name__}. Skipping.")
            return

        # If flatten is True, normalize the JSON structure
        df = pd.json_normalize(json_data, sep="_") if flatten else pd.DataFrame(json_data)

        # Replace all NaN/NaT with None so they become SQL NULL
        df = df.where(pd.notnull(df), None)

        allowed_keys = {c.name for c in dataclass.__table__.columns}
        extra_keys = set(df.columns) - allowed_keys
        primary_keys = [key.name for key in dataclass.__table__.primary_key]

        # Drop duplicates based on primary_keys
        if primary_keys:
            df = df.drop_duplicates(subset=primary_keys)

        if extra_keys:
            logging.info(f"Keys in json_data not in allowed_keys: {extra_keys}")

        bulk_data = [
            {str(k): v for k, v in row.items() if str(k) in allowed_keys}
            for row in df.to_dict(orient="records")
        ]

        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            if upsert_values:
                from sqlalchemy.dialects.postgresql import insert

                stmt = insert(dataclass).values(bulk_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=primary_keys,
                    set_={
                        c.name: getattr(stmt.excluded, c.name)
                        for c in dataclass.__table__.columns
                        if c.name not in primary_keys
                    },
                )
                session.execute(stmt)
            else:
                session.bulk_insert_mappings(dataclass, bulk_data)
            session.commit()
            logging.info(f"Data successfully inserted {len(df)} rows on {dataclass.__tablename__}.")

        except Exception as e:
            session.rollback()
            logging.error(f"An error occurred: {e}")

        finally:
            session.close()

    def _get_unique_segmentation_contacts(self, name_pattern: str) -> list:
        """Fetch unique contacts from the database efficiently."""
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # Define the table dynamically
        metadata = MetaData()
        table = Table("rd_segmentation_contacts", metadata, autoload_with=self.engine)

        try:
            # Use a faster search method instead of LOWER()
            name_pattern = "%" if name_pattern is None else f"%{name_pattern}%"

            # Properly reference table columns instead of raw strings
            query = (
                select(table.c.uuid, table.c.email)
                .distinct()
                .where(
                    table.c.segmentation_name.ilike(name_pattern)  # Case-insensitive search
                )
            )

            result = session.execute(query)
            unique_contacts = [
                {"uuid": row.uuid, "email": row.email} for row in result.fetchall()
            ]

        finally:
            session.close()

        logging.info(f"Query returned {len(unique_contacts):,} unique contacts.")

        return unique_contacts
