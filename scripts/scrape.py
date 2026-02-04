#!/usr/bin/env python3
"""
Two-stage bus data scraper for Ayna.gov.az API
Stage 1: Fetch list of all buses
Stage 2: Fetch detailed data for each bus including routes and coordinates
Output: Single JSON file with all bus data
"""

import requests
import json
import time
from typing import List, Dict, Any
from pathlib import Path


class BusScraper:
    """Scraper for Ayna bus data with two-stage API calls"""

    BASE_URL = "https://map-api.ayna.gov.az/api/bus"
    HEADERS = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Origin': 'https://map.ayna.gov.az',
        'Referer': 'https://map.ayna.gov.az/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
    }

    def __init__(self, output_file: str = "data/bus_data.json"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_bus_list(self) -> List[Dict[str, Any]]:
        """
        Stage 1: Fetch list of all buses from getBusList endpoint
        Returns: List of buses with id and number
        """
        print("Stage 1: Fetching bus list...")
        try:
            response = self.session.get(f"{self.BASE_URL}/getBusList", timeout=30)
            response.raise_for_status()
            buses = response.json()
            print(f"✓ Found {len(buses)} buses")
            return buses
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching bus list: {e}")
            raise

    def get_bus_details(self, bus_id: int) -> Dict[str, Any]:
        """
        Stage 2: Fetch detailed data for a specific bus by ID
        Returns: Complete bus data including routes, stops, and coordinates
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/getBusById",
                params={"id": bus_id},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching bus {bus_id}: {e}")
            raise

    def scrape_all_buses(self, delay: float = 0.5) -> List[Dict[str, Any]]:
        """
        Execute two-stage scraping for all buses
        Args:
            delay: Delay between requests in seconds (to be respectful to the server)
        Returns: List of all bus details
        """
        # Stage 1: Get list of all buses
        bus_list = self.get_bus_list()

        # Stage 2: Fetch detailed data for each bus
        print(f"\nStage 2: Fetching detailed data for {len(bus_list)} buses...")
        all_bus_data = []

        for idx, bus in enumerate(bus_list, 1):
            bus_id = bus['id']
            bus_number = bus['number']

            try:
                print(f"  [{idx}/{len(bus_list)}] Fetching bus #{bus_number} (ID: {bus_id})...", end=' ')
                bus_details = self.get_bus_details(bus_id)
                all_bus_data.append(bus_details)
                print("✓")

                # Validate data integrity
                self._validate_bus_data(bus_details, bus_id, bus_number)

                # Be respectful to the server
                if idx < len(bus_list):
                    time.sleep(delay)

            except Exception as e:
                print(f"✗ FAILED")
                print(f"    Error: {e}")
                # Continue with other buses even if one fails
                continue

        print(f"\n✓ Successfully scraped {len(all_bus_data)}/{len(bus_list)} buses")

        if len(all_bus_data) < len(bus_list):
            print(f"⚠ Warning: {len(bus_list) - len(all_bus_data)} buses failed to scrape")

        return all_bus_data

    def _validate_bus_data(self, bus_data: Dict[str, Any], bus_id: int, bus_number: str):
        """Validate that critical data fields are present"""
        critical_fields = ['id', 'number', 'stops', 'routes']
        missing_fields = [field for field in critical_fields if field not in bus_data]

        if missing_fields:
            print(f"    ⚠ Warning: Missing fields {missing_fields}")

        # Check if we have coordinate data
        if 'stops' in bus_data:
            stops_with_coords = sum(1 for stop in bus_data['stops']
                                   if 'stop' in stop and stop['stop'].get('latitude') and stop['stop'].get('longitude'))
            if stops_with_coords == 0:
                print(f"    ⚠ Warning: No stop coordinates found")

        if 'routes' in bus_data:
            routes_with_coords = sum(1 for route in bus_data['routes']
                                    if route.get('flowCoordinates'))
            if routes_with_coords == 0:
                print(f"    ⚠ Warning: No route flow coordinates found")

    def save_data(self, data: List[Dict[str, Any]]):
        """
        Save all bus data to a single JSON file
        Uses pretty printing for readability and data verification
        """
        print(f"\nSaving data to {self.output_file}...")

        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            file_size = self.output_file.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"✓ Data saved successfully")
            print(f"  File: {self.output_file}")
            print(f"  Size: {file_size:.2f} MB")
            print(f"  Buses: {len(data)}")

            # Calculate statistics
            total_stops = sum(len(bus.get('stops', [])) for bus in data)
            total_routes = sum(len(bus.get('routes', [])) for bus in data)
            total_coords = sum(
                sum(len(route.get('flowCoordinates', [])) for route in bus.get('routes', []))
                for bus in data
            )

            print(f"\nData Statistics:")
            print(f"  Total stops: {total_stops}")
            print(f"  Total routes: {total_routes}")
            print(f"  Total flow coordinates: {total_coords}")

        except IOError as e:
            print(f"✗ Error saving data: {e}")
            raise

    def run(self):
        """Execute the complete scraping pipeline"""
        print("=" * 60)
        print("Bus Data Scraper - Ayna.gov.az")
        print("=" * 60)

        try:
            # Scrape all bus data
            all_bus_data = self.scrape_all_buses()

            if not all_bus_data:
                print("\n✗ No data collected. Exiting.")
                return

            # Save to JSON file
            self.save_data(all_bus_data)

            print("\n" + "=" * 60)
            print("✓ Scraping completed successfully!")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n⚠ Scraping interrupted by user")
            if hasattr(self, 'all_bus_data') and self.all_bus_data:
                save = input("Save partial data? (y/n): ")
                if save.lower() == 'y':
                    self.save_data(self.all_bus_data)
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            raise


def main():
    """Main entry point"""
    scraper = BusScraper(output_file="data/bus_data.json")
    scraper.run()


if __name__ == "__main__":
    main()
