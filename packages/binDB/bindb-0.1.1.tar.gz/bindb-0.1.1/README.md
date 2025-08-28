# binDB

A Python library for retrieving BIN (Bank Identification Number) information.

## Installation

You can install `binDB` using pip:

```bash
pip install binDB
```

## Usage

```python
from binDB.smartdb import SmartBinDB

db = SmartBinDB()

# Get BIN information
bin_info = db.get_bin_info("45717360")
print(bin_info)

# Get BINs by bank name
bank_bins = db.get_bins_by_bank("JPMorgan Chase", limit=5)
print(bank_bins)

# Get BINs by country code
country_bins = db.get_bins_by_country("US", limit=5)
print(country_bins)
```

## API Endpoints (if exposed via a web framework)

This library provides core functionality. If you wish to expose this as a web API, you would integrate it with a framework like Flask or FastAPI.

## Data

The library uses JSON files located in the `data/` directory for BIN information.

## Contributing

Feel free to contribute to this project by opening issues or pull requests on GitHub.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
