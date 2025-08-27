# ULID Dates

A Python utility to determine ULID prefixes for date ranges.

This can be useful for querying databases or logs for ULIDs that fall within a specific time period.

For example by finding the prefixes for the start and end of a time range, you can efficiently scan for records within that range.

If `id` is a ULID, you can then fine items between two time prefixes `... WHERE id >= 'start_prefix' AND id < 'end_prefix'`.



## Installation

Install the package using `pip`:

```bash
pip install ulid-dates
```

Alternatively, using `uv`:

```bash
uv pip install ulid-dates
```

## Usage

### Basic Usage

```python
from datetime import datetime, timedelta
from ulid_dates import ulid_prefix_range_for_dates

start_date = datetime(2023, 1, 1)
end_date = start_date + timedelta(days=1)

start_prefix, end_prefix = ulid_prefix_range_for_dates(start_date, end_date)

print(f"ULID prefix for {start_date}: {start_prefix}")
print(f"ULID prefix for {end_date}: {end_prefix}")
```

### Advanced Usage: Querying a DynamoDB GSI

A use case for this library is to query a database for records that have UUIDs within a specific time range. If you are using ULIDs as sort keys in a DynamoDB Global Secondary Index (GSI), you can use the generated prefixes to efficiently query for records created within a certain period.

Here is an example of how you might query a GSI in a DynamoDB table where logs for orders are stored within the PKI but with a common `lookup` value and a `sort` that contains a UUID.

```python
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
from ulid_dates import ulid_prefix_range_for_dates

# 1. Configure DynamoDB table and GSI query parameters
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('my-application-single-table')
gsi_name = 'lookup-index'

# 2. Generate the ULID prefixes for the date range
start_date = datetime.now() - timedelta(days=7)
end_date = datetime.now()
start_prefix, end_prefix = ulid_prefix_range_for_dates(start_date, end_date)

# 3. Query the GSI using the ULID prefixes
#    This assumes the GSI partition key is 'logs' and the sort key is 'created_at' (a ULID).
response = table.query(
    IndexName=gsi_name,
    KeyConditionExpression=Key('lookup').eq('Order#Logs#') 
    & Key('sort').between(
        f"Order#Log#{start_prefix}",
        f"Order#Log#{end_prefix}"
    )
)

# 4. Print the results
items = response.get('Items', [])
print(f"Found {len(items)} logs.")
```

## Development

To set up the development environment:

1. Clone the repository.
2. Create a virtual environment and activate it.
3. Install the dependencies in editable mode.

Using `pip`:
```bash
pip install -e .[dev]
```

Alternatively, using `uv`:

```bash
uv pip install -e .[dev]
```

### Running Tests

To run the tests, use `pytest`:

```bash
pytest
```
