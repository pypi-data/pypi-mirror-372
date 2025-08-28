import json
import os
import time
import pycountry
import pycountry_convert
from typing import Optional, List, Dict

class SmartBinDB:
    def __init__(self):
        self.COUNTRY_JSON_DIR = os.path.join(os.path.dirname(__file__), "data")
        self.BIN_INDEX = {}
        self.COUNTRY_DATA = {}
        self.START_TIME = time.time()
        self.load_data() # Load data synchronously on initialization

    def load_file(self, file_path: str, country_code: str) -> bool:
        for attempt in range(3):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                self.COUNTRY_DATA[country_code] = data
                for entry in data:
                    if 'bin' in entry:
                        self.BIN_INDEX[entry['bin']] = entry
                return True
            except Exception as e:
                print(f"Error loading {file_path} (attempt {attempt + 1}): {str(e)}")
                time.sleep(0.1)
        return False

    def load_data(self):
        if not os.path.exists(self.COUNTRY_JSON_DIR):
            print(f"Directory {self.COUNTRY_JSON_DIR} does not exist")
            return
        
        for filename in os.listdir(self.COUNTRY_JSON_DIR):
            if filename.lower().endswith('.json'):
                country_code = filename.replace('.json', '').upper()
                file_path = os.path.join(self.COUNTRY_JSON_DIR, filename)
                self.load_file(file_path, country_code)
        
        # No need for async.gather or results processing here, as it's synchronous now.
        # The original code had a 'failed' count, but for synchronous loading,
        # individual load_file calls will print errors.

    def get_country_info(self, country_code: str) -> dict:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if not country:
            return {
                "A2": country_code.upper(),
                "A3": "",
                "N3": "",
                "Name": "",
                "Cont": ""
            }
        try:
            continent_code = pycountry_convert.country_alpha2_to_continent_code(country.alpha_2)
            continent = pycountry_convert.convert_continent_code_to_continent_name(continent_code)
        except Exception as e:
            print(f"Error getting continent for {country_code}: {str(e)}")
            continent = ""
        return {
            "A2": country.alpha_2,
            "A3": country.alpha_3,
            "N3": country.numeric,
            "Name": country.name,
            "Cont": continent
        }

    def format_entry(self, entry: dict) -> dict:
        country_code = entry.get('country_code', '').upper()
        country_info = self.get_country_info(country_code)
        return {
            "bin": entry.get('bin', ''),
            "brand": entry.get('brand', ''),
            "category": entry.get('category', ''),
            "CardTier": f"{entry.get('category', '')} {entry.get('brand', '')}".strip(),
            "country_code": country_code,
            "Type": entry.get('type', ''),
            "country_code_alpha3": entry.get('country_code_alpha3', ''),
            "Country": country_info,
            "issuer": entry.get('issuer', ''),
            "phone": entry.get('phone', ''),
            "type": entry.get('type', ''),
            "website": entry.get('website', '')
        }

    def get_bins_by_bank(self, bank: str, limit: Optional[int] = None) -> dict:
        # Data is loaded in __init__, so no need to check self.COUNTRY_DATA here
        if not self.COUNTRY_DATA:
            return {
                "status": "error",
                "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        matching_bins = []
        for data in self.COUNTRY_DATA.values():
            for entry in data:
                if 'issuer' in entry and bank.lower() in entry['issuer'].lower():
                    matching_bins.append(self.format_entry(entry))
        if not matching_bins:
            return {
                "status": "error",
                "message": f"No matches found for bank: {bank}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        if limit is not None:
            matching_bins = matching_bins[:limit]
        return {
            "status": "SUCCESS",
            "data": matching_bins,
            "count": len(matching_bins),
            "filtered_by": "bank",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev",
            "Luhn": True
        }

    def get_bins_by_country(self, country: str, limit: Optional[int] = None) -> dict:
        # Data is loaded in __init__, so no need to check self.COUNTRY_DATA here
        if not self.COUNTRY_DATA:
            return {
                "status": "error",
                "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        country = country.upper()
        if country == 'US':
            matching_bins = []
            for country_code in ['US', 'US1', 'US2']:
                if country_code in self.COUNTRY_DATA:
                    matching_bins.extend([self.format_entry(entry) for entry in self.COUNTRY_DATA[country_code]])
            if not matching_bins:
                return {
                    "status": "error",
                    "message": "No data found for country code: US",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            if limit is None:
                limit = 1000
            if limit > 8000:
                return {
                    "status": "error",
                    "message": "Maximum limit allowed for US is 8000",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            matching_bins = matching_bins[:limit]
            return {
                "status": "SUCCESS",
                "data": matching_bins,
                "count": len(matching_bins),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        else:
            if country not in self.COUNTRY_DATA:
                return {
                    "status": "error",
                    "message": f"No data found for country code: {country}",
                    "api_owner": "@ISmartCoder",
                    "api_channel": "@TheSmartDev"
                }
            data = [self.format_entry(entry) for entry in self.COUNTRY_DATA[country]]
            if limit is not None:
                data = data[:limit]
            return {
                "status": "SUCCESS",
                "data": data,
                "count": len(data),
                "filtered_by": "country",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }

    def get_bin_info(self, bin: str) -> dict:
        # Data is loaded in __init__, so no need to check self.BIN_INDEX here
        if not self.BIN_INDEX:
            return {
                "status": "error",
                "message": f"Data directory not found or empty: {self.COUNTRY_JSON_DIR}",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev"
            }
        if bin in self.BIN_INDEX:
            return {
                "status": "SUCCESS",
                "data": [self.format_entry(self.BIN_INDEX[bin])],
                "count": 1,
                "filtered_by": "bin",
                "api_owner": "@ISmartCoder",
                "api_channel": "@TheSmartDev",
                "Luhn": True
            }
        return {
            "status": "error",
            "message": f"No matches found for BIN: {bin}",
            "api_owner": "@ISmartCoder",
            "api_channel": "@TheSmartDev"
        }
