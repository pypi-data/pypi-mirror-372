# Generated Data That Makes Sense (GDTMS)

A Python library for generating realistic, relational test data with referential integrity. GDTMS creates meaningful data for database testing, development, and prototyping by maintaining relationships between tables and generating contextually appropriate values.

## Features

- **Relational data generation** with foreign key relationships
- **Multiple data types** including names, emails, addresses, phone numbers, dates, and more
- **Composite data types** for complex field generation
- **Unique constraints** support to prevent duplicate values
- **Self-referencing tables** for hierarchical data structures
- **MySQL output format** with proper SQL syntax
- **Configurable record counts** per table
- **Null value support** with configurable probability

## Installation

```bash
pip install generated-data-that-makes-sense
```

## Quick Start

```python
from gdtms.entities.schema import Schema
from gdtms.entities.table import Table
from gdtms.entities.field import Field
from gdtms.data_types.autoincrement import Autoincrement
from gdtms.data_types.first_name import FirstName
from gdtms.data_types.last_name import LastName
from gdtms.data_types.email import Email
from gdtms.views.mysql import Mysql

# Create a schema
schema = Schema()

# Create a users table
users_table = Table(name="users", num_records_to_generate=10)
users_table.add_fields([
    Field("id", Autoincrement()),
    Field("first_name", FirstName()),
    Field("last_name", LastName()),
    Field("email", Email())
])

schema.add_table(users_table)

# Generate SQL output
view = Mysql()
sql_output = schema.dump(view)
print(sql_output)
```

## Supported Data Types

- `Autoincrement` - Auto-incrementing integers
- `FirstName` - Realistic first names
- `LastName` - Realistic last names  
- `Email` - Valid email addresses
- `PhoneNumber` - Formatted phone numbers
- `Address` - Street addresses
- `City` - City names
- `ZipPostal` - ZIP/postal codes
- `Date` - Date values
- `Number` - Numeric ranges
- `Url` - Valid URLs
- `DomainName` - Domain names
- `Adjective` - Descriptive adjectives
- `Noun` - Common nouns
- `Verb` - Action verbs
- `HardcodedValue` - Fixed values
- `Reference` - Foreign key relationships
- `Composite` - Combinations of multiple data types

## Advanced Usage

### Creating Related Tables

```python
# Create parent table
countries = Table(name="countries", num_records_to_generate=5)
countries.add_fields([
    Field("id", Autoincrement()),
    Field("name", Noun())
])

# Create child table with foreign key
users = Table(name="users", num_records_to_generate=20)
users.add_fields([
    Field("id", Autoincrement()),
    Field("country_id", Reference(countries)),
    Field("name", FirstName())
])
```

### Unique Constraints

```python
from gdtms.entities.unique_key import UniqueKey

username_field = Field("username", Email())
users_table.add_field(username_field)
users_table.add_unique_key(UniqueKey([username_field]))
```

### Composite Data Types

```python
from gdtms.data_types.composite import Composite

# Generate questions like "What red car do you drive?"
question_field = Field("question", Composite([
    HardcodedValue("What"),
    Adjective(),
    Noun(),
    Verb(),
    HardcodedValue("?")
]))
```

## License

MIT License