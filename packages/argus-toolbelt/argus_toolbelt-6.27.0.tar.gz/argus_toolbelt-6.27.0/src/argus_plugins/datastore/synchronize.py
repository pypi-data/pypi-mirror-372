from copy import copy
from csv import DictReader, reader
from json import dumps
from pathlib import Path
from sys import exit
from typing import Callable, Dict, Optional
from urllib.parse import quote_plus

from argus_api.api.customers.v2.customer import get_customer
from argus_api.api.datastores.v1.store.store import (
    delete_data_store_entries,
    get_entries_from_store,
    put_data_store_entries,
)

from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins import argus_cli_module


def get_buffered_data(func: Callable) -> Callable:
    """

    :param func: The getter function for the data to be buffered.
    :return: A generator with the data, where the data is the ["data"] parameter of the response.
    """

    def ann(*args, **kwargs):
        buffer_size = 200

        offset = 0
        response = func(*args, limit=buffer_size, offset=offset, **kwargs)
        while offset < response["count"]:
            yield from response["data"]
            offset += buffer_size

            response = func(*args, limit=buffer_size, offset=offset, **kwargs)

    return ann


def set_data_with_buffer(func: Callable, buffered_argument: str) -> Callable:
    """
    Decorator to send data in multiple batches.

    Large requests might be eaten by a proxy or the service itself.
    Because of this, we're setting the batch size to 4k. This is half of the
    max size of a URL according to the HTTP RFC, and should be well within a
    safe limit to assure that our request is delivered.

    :param func: The function to buffer.
    :param buffered_argument: The kwarg that is going to be split into
                              multiple requests. The key that this is
                              referencing has to be an iterable.
    :return: The decorated function.
    """

    def buffered_arguments(args, kwargs):
        buffer = kwargs.pop(buffered_argument)
        buffer_size = len(buffer)

        if any(len(quote_plus(str(item))) > 4000 for item in buffer):
            raise ValueError(
                "One of the arguments to {} is over the 4K "
                "characters. This exceeds the maximum limit and "
                "is not allowed."
            )

        offset = 0
        while offset < buffer_size:
            current_end = offset + 1
            while (
                sum(
                    len(str(s).encode("unicode_escape"))
                    for s in buffer[offset : current_end + 1]
                )
                < 4000
                and buffer_size >= current_end + 1 > offset
            ):
                current_end += 1

            kwargs[buffered_argument] = buffer[offset:current_end]
            offset = current_end

            yield args, kwargs

    def buffered_function(*args, **kwargs):
        response = None
        for args, kwargs in buffered_arguments(args, kwargs):
            response = func(*args, **kwargs)

        return response

    return buffered_function


def datastore_data(
    data: str,
    csv_key: str = "key",
    lowercase_key: bool = False,
    lowercase_value: bool = False,
    default_value: str = "N/A",
) -> Dict[str, str]:
    """Turns a CSV string into key:value pairs."""

    try:
        with open(data, "r") as fp:
            data = fp.readlines()
    except IOError:
        data = data.split("\n")

    # Remove any comments
    data = filter(
        lambda line: not line.startswith("#") and len(line) and not line.isspace(), data
    )
    csv_reader = reader(data)

    entries = {}
    for row in csv_reader:
        key = row[0].strip()

        if lowercase_key:
            key = key.lower()

        value = (
            format_value(row[1], lowercase_value, default_value)
            if len(row) > 1
            else format_value(default_value, lowercase_value, default_value)
        )

        if key in entries:
            log.warning(
                f'The key "{key}" exists multiple times in the data. Overriding with new value'
            )
        if key == csv_key:
            log.warning(
                f"You appear to be using an unformatted CSV file without using the --csv-json argument "
                f"""({'{'}"{key}": "{value}"{'}'} will be added to the datastore)"""
            )

        entries[key] = value

    return entries


def csv_to_json(
    csv_file_path: Path,
    csv_key: str = "key",
    lowercase_key: bool = False,
    lowercase_value: bool = False,
) -> dict:
    """Convert CSV file WITH headers to dict where the CSV column
    specified in the `csv_key` parameter is left intact, and the rest
    of the columns are converted to a stringified dict with the column name as key.

    :param csv_file_path: Filepath of the CSV file.
    :param csv_key: Column to use as keys in the dict.
    """

    csv_data = {}

    with open(csv_file_path, "r") as csv_in:
        # DictReader formats each row from the CSV file to {csv_key: row_key, header1: row_val1, header2: row_val2, ...}
        for row in DictReader(csv_in):
            # If `csv_key` does not exist in the CSV headers, raise ValueError
            if csv_key not in row.keys():
                raise ValueError(f"No column `{csv_key}` in CSV file")

            # Check if the row is commented out
            if list(row.values())[0].startswith("#"):
                log.info(f"Skipping key starting with #: {row}")
                continue

            # Convert row to format:  row_key: "{'header1': 'row_val1', 'header2': 'row_val2', ...}"
            value = copy(row)
            del value[csv_key]

            if lowercase_value:
                value = {header: v.lower() for header, v in value.items()}

            key = row[csv_key]

            if lowercase_key:
                key = key.lower()

            # Serialize the value to a JSON formatted string
            csv_data[key] = dumps(value)

    return csv_data


def validate_csv_options(csv_json: bool, csv_key: str) -> None:
    """Verify that the csv_json option is True if the csv_key option is provided.

    :param csv_json: Flag to enable formatting of the input CSV file.
    :param csv_key: String corresponding to a column in the CSV file to use as keys in the Argus datastore.
    :raises AttributeError: When csv_json is False and the csv_key option is provided with a different value than `key`.
    """

    if csv_key != "key" and not csv_json:
        raise AttributeError(
            "--csv-key is only valid when the --csv-json option is also provided."
        )


def validate_data_format(data: str) -> None:
    """Verify that the data argument is a valid CSV file or a dict.

    :param data: String corresponding to a CSV file, or a python dict.
    :raises FileNotFoundError: If data is not a dict and does not point to a file.
    """

    if isinstance(data, dict):
        return

    if not Path(data).is_file():
        raise FileNotFoundError(f"File not found: '{data}'")


@register_command(extending="datastores", module=argus_cli_module)
def delete(datastore: str, keys: list, customer: str = None) -> None:
    """Deletes given entries from the datastore.

    :param datastore: The datastore to modify.
    :param customer: The customer to affect.
    :param keys: Keys to delete. A file can be provided with the @-prefix
                 (eg. @/tmp/datastore_delete.txt).
    """

    if customer:
        customer_id = get_customer(idOrShortName=customer.lower())["data"]["id"]
    else:
        customer_id = None

    buffered_delete = set_data_with_buffer(
        delete_data_store_entries, buffered_argument="key"
    )
    buffered_delete(dataStore=datastore, customerID=customer_id, key=keys)

    print(f"Successfully deleted {len(keys)} entries")


def format_value(
    value: Optional[str], lowercase_value: bool, default_value: str
) -> str:
    """Handle default values, so the value is always stripped and lowecased (if flag is set)

    :param value: Value
    :param lowercase_value: Return lowercase of value
    :param default_value: Return this value if value is not truthy
    :return: formatted value
    """
    if not value:
        value = default_value

    if lowercase_value:
        return value.lower().strip()

    return value.strip()


@register_command(extending="datastores", module=argus_cli_module)
def update(
    datastore: str,
    data: str,
    customer: str = None,
    default_value: str = "N/A",
    csv_json: bool = False,
    csv_key: str = "key",
    lowercase_key: bool = False,
    lowercase_value: bool = False,
):
    """Adds or updates entries from the data.

    :param datastore: The Argus datastore.
    :param data: CSV file/python dict. The Argus datastore will be updated to match the data in this file/dict.
    :param customer: Specifies which customer to update entries for in the datastore.
    :param default_value: Value inserted for missing values in the Argus datastore.
    :param csv_json: Flag which when set makes the script convert input CSV file to a dict using column specified in
    `csv_key` as keys and residual fields in each row as stringified values.
    :param csv_key: String corresponding to the column in the CSV file to use as keys in the Argus datastore.
    :param lowercase_key: Flag which when set will lowercase the key when reading from CSV
    :param lowercase_value: Flag which when set will lowercase the values when reading from CSV
    """

    validate_csv_options(csv_json=csv_json, csv_key=csv_key)
    validate_data_format(data=data)

    if csv_json:
        try:
            data = csv_to_json(
                csv_file_path=Path(data),
                csv_key=csv_key,
                lowercase_key=lowercase_key,
                lowercase_value=lowercase_value,
            )
        except (ValueError, FileNotFoundError) as e:
            log.exception(e)
            exit(1)
    elif isinstance(data, str):
        # Only call datastore_data if update was invoked from the cli (not from the sync method)
        data = datastore_data(
            data,
            csv_key,
            lowercase_key=lowercase_key,
            lowercase_value=lowercase_value,
            default_value=default_value,
        )

    if customer:
        customer_id = get_customer(idOrShortName=customer.lower())["data"]["id"]
    else:
        customer_id = None

    entries = [
        {
            csv_key: key.lower() if lowercase_key else key,
            "value": format_value(value, lowercase_value, default_value),
        }
        for key, value in data.items()
    ]
    buffered_put = set_data_with_buffer(
        put_data_store_entries, buffered_argument="entries"
    )
    response = buffered_put(
        dataStore=datastore, entries=entries, customerID=customer_id
    )

    print(f"Successfully updated {len(entries)} entries")


@register_command(extending="datastores", module=argus_cli_module)
def sync(
    datastore: str,
    data: str,
    customer: str = None,
    default_value: str = "N/A",
    csv_json: bool = False,
    csv_key: str = "key",
    lowercase_key: bool = False,
    lowercase_value: bool = False,
):
    """Makes sure the datastore is a 1:1 match with the given data (for a given customer, if any).

    :param datastore: The Argus datastore.
    :param data: CSV file. The Argus datastore will be updated to match the data in this file.
    :param customer: Specifies which customer to update entries for in the datastore.
    :param default_value: Value inserted for missing values in the Argus datastore.
    :param csv_json: Flag which when set makes the script convert input CSV file to a dict using column specified in
    `csv_key` as keys and residual fields in each row as stringified values.
    :param csv_key: String corresponding to the column in the CSV file to use as keys in the Argus datastore.
    :param lowercase_key: Flag which when set will lowercase the key when reading from CSV
    :param lowercase_value: Flag which when set will lowercase the values when reading from CSV
    """

    validate_csv_options(csv_json=csv_json, csv_key=csv_key)
    validate_data_format(data=data)

    if csv_json:
        try:
            data = csv_to_json(
                csv_file_path=Path(data),
                csv_key=csv_key,
                lowercase_key=lowercase_key,
                lowercase_value=lowercase_value,
            )
        except (ValueError, FileNotFoundError) as e:
            log.exception(e)
            exit(1)
    else:
        data = datastore_data(
            data,
            csv_key,
            lowercase_key=lowercase_key,
            lowercase_value=lowercase_value,
            default_value=default_value,
        )

    if customer:
        customer_id = get_customer(idOrShortName=customer.lower())["data"]["id"]
    else:
        customer_id = None

    delete_entries = []  # Items to delete
    update_entries = {}  # Items to update/add
    existing_entries = {}  # Entries that already exist

    fetched_entries = get_buffered_data(get_entries_from_store)(datastore)

    for entry in fetched_entries:
        if customer_id and entry["customer"]["id"] != customer_id:
            continue

        key = entry[csv_key]
        value = entry["value"] or None

        existing_entries[key] = value
        if key not in data:
            delete_entries.append(key)

    for key, value in data.items():
        if value != existing_entries.get(key):
            update_entries[key] = value

    # Delete entries before we update, since it looks like deletes are not
    # case sensitive, so we will drop entries if we are changing case on an entry
    if delete_entries:
        delete(datastore, delete_entries, customer)

    if update_entries:
        update(datastore, update_entries, customer)
