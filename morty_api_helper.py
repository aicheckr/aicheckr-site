#!/usr/bin/env python3
"""
Morty API Helper - Utility script for API token management and testing

This script helps with:
- Requesting API tokens
- Testing API connectivity
- Quick status checks
- Running single test trips
"""

import requests
import argparse
import json
import os
from typing import Optional


class MortyAPIHelper:
    """Helper class for Morty Rescue API operations"""

    BASE_URL = "https://challenge.sphinxhq.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get('MORTY_API_TOKEN')
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def request_token(self, name: str, email: str):
        """
        Request a new API token

        Args:
            name: Your name
            email: Your email address

        The token will be sent to your email.
        """
        print(f"📧 Requesting API token for {name} ({email})...")

        response = requests.post(
            f"{self.BASE_URL}/api/auth/request-token/",
            json={"name": name, "email": email}
        )

        if response.status_code == 200:
            print("✅ Token request successful!")
            print("📬 Check your email for the API token.")
            print("\nOnce you receive it, set it as an environment variable:")
            print("   export MORTY_API_TOKEN='your_token_here'")
            return True
        else:
            print(f"❌ Token request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    def test_connection(self):
        """Test API connectivity and authentication"""
        if not self.token:
            print("❌ No API token found!")
            print("Set MORTY_API_TOKEN environment variable or use --token")
            return False

        print("🔌 Testing API connection...")

        try:
            response = requests.get(
                f"{self.BASE_URL}/api/mortys/status/",
                headers=self.headers
            )

            if response.status_code == 200:
                print("✅ API connection successful!")
                data = response.json()
                print(f"\n📊 Current Episode Status:")
                print(f"   Morties in Citadel: {data.get('morties_in_citadel', 'N/A')}")
                print(f"   Morties on Planet Jessica: {data.get('morties_on_planet_jessica', 'N/A')}")
                print(f"   Morties Lost: {data.get('morties_lost', 'N/A')}")
                print(f"   Steps Taken: {data.get('steps_taken', 'N/A')}")
                print(f"   Status: {data.get('status_message', 'N/A')}")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - invalid or expired token")
                return False
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

    def start_new_episode(self):
        """Start a new rescue episode"""
        if not self.token:
            print("❌ No API token found!")
            return False

        print("🎬 Starting new rescue episode...")

        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/start/",
                headers=self.headers
            )

            if response.status_code == 200:
                print("✅ New episode started!")
                data = response.json()
                print(f"\n📊 Initial State:")
                print(f"   Morties in Citadel: {data['morties_in_citadel']}")
                print(f"   Ready to rescue!")
                return True
            else:
                print(f"❌ Failed to start episode: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

    def send_test_trip(self, planet: int, morty_count: int):
        """
        Send a single test trip

        Args:
            planet: 0 (On a Cob), 1 (Cronenberg), or 2 (Purge)
            morty_count: 1, 2, or 3
        """
        if not self.token:
            print("❌ No API token found!")
            return False

        planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

        print(f"🚀 Sending {morty_count} Morty(s) through {planet_names[planet]}...")

        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/portal/",
                headers=self.headers,
                json={"planet": planet, "morty_count": morty_count}
            )

            if response.status_code == 200:
                data = response.json()
                survived = data.get('survived', False)

                if survived:
                    print(f"✅ SUCCESS! {morty_count} Morty(s) survived!")
                else:
                    print(f"💀 FAILED! {morty_count} Morty(s) lost...")

                print(f"\n📊 Updated Status:")
                print(f"   Morties in Citadel: {data['morties_in_citadel']}")
                print(f"   Morties on Planet Jessica: {data['morties_on_planet_jessica']}")
                print(f"   Morties Lost: {data['morties_lost']}")
                print(f"   Steps Taken: {data['steps_taken']}")

                return survived

            else:
                print(f"❌ Trip failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return False

    def get_status(self):
        """Get current episode status"""
        if not self.token:
            print("❌ No API token found!")
            return None

        print("📊 Fetching current status...")

        try:
            response = requests.get(
                f"{self.BASE_URL}/api/mortys/status/",
                headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                print("\n📊 Current Episode Status:")
                print(f"   Morties in Citadel: {data['morties_in_citadel']}")
                print(f"   Morties on Planet Jessica: {data['morties_on_planet_jessica']}")
                print(f"   Morties Lost: {data['morties_lost']}")
                print(f"   Steps Taken: {data['steps_taken']}")
                print(f"   Message: {data.get('status_message', 'N/A')}")

                # Calculate statistics
                total_sent = data['morties_on_planet_jessica'] + data['morties_lost']
                if total_sent > 0:
                    success_rate = data['morties_on_planet_jessica'] / total_sent * 100
                    print(f"\n📈 Statistics:")
                    print(f"   Success Rate: {success_rate:.1f}%")
                    print(f"   Remaining: {data['morties_in_citadel']} / 1000")

                return data

            else:
                print(f"❌ Failed to get status: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            return None

    def quick_exploration(self, trips_per_combo: int = 5):
        """
        Run a quick exploration of all planet/group combinations

        Args:
            trips_per_combo: Number of trips to test per combination
        """
        if not self.token:
            print("❌ No API token found!")
            return

        print(f"🔬 Running quick exploration ({trips_per_combo} trips per combination)...")

        results = {}
        planet_names = ["On a Cob", "Cronenberg", "Purge"]

        for planet in range(3):
            for morty_count in range(1, 4):
                key = f"P{planet}_{morty_count}M"
                survived_count = 0

                print(f"\n📡 Testing {planet_names[planet]} with {morty_count} Morty(s)...")

                for i in range(trips_per_combo):
                    try:
                        response = requests.post(
                            f"{self.BASE_URL}/api/mortys/portal/",
                            headers=self.headers,
                            json={"planet": planet, "morty_count": morty_count}
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if data.get('survived', False):
                                survived_count += 1
                                print(f"   Trip {i+1}: ✅")
                            else:
                                print(f"   Trip {i+1}: 💀")
                        else:
                            print(f"   Trip {i+1}: ❌ API Error")

                    except Exception as e:
                        print(f"   Trip {i+1}: ❌ {e}")

                survival_rate = survived_count / trips_per_combo
                results[key] = {
                    'planet': planet,
                    'morty_count': morty_count,
                    'survived': survived_count,
                    'total': trips_per_combo,
                    'rate': survival_rate
                }

                print(f"   Survival Rate: {survival_rate:.1%}")

        # Summary
        print("\n" + "="*60)
        print("📊 EXPLORATION SUMMARY")
        print("="*60 + "\n")

        sorted_results = sorted(results.items(), key=lambda x: x[1]['rate'], reverse=True)

        for key, data in sorted_results:
            print(f"{key}: {data['rate']:.1%} "
                  f"({data['survived']}/{data['total']}) "
                  f"[EV: {data['rate'] * data['morty_count']:.2f}]")

        # Save results
        output_file = '/home/user/aicheckr-site/quick_exploration_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Morty Rescue API Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Request a token:
    python morty_api_helper.py --request-token --name "Your Name" --email "you@example.com"

  Test connection:
    python morty_api_helper.py --test

  Start new episode:
    python morty_api_helper.py --start

  Send a test trip:
    python morty_api_helper.py --trip --planet 2 --count 3

  Quick exploration:
    python morty_api_helper.py --explore --trips 10

  Check status:
    python morty_api_helper.py --status
        """
    )

    parser.add_argument('--token', '-t', help='API token (or set MORTY_API_TOKEN env var)')
    parser.add_argument('--request-token', action='store_true', help='Request a new API token')
    parser.add_argument('--name', help='Your name (for token request)')
    parser.add_argument('--email', help='Your email (for token request)')
    parser.add_argument('--test', action='store_true', help='Test API connection')
    parser.add_argument('--start', action='store_true', help='Start a new episode')
    parser.add_argument('--status', '-s', action='store_true', help='Get current status')
    parser.add_argument('--trip', action='store_true', help='Send a test trip')
    parser.add_argument('--planet', '-p', type=int, choices=[0, 1, 2], help='Planet for test trip')
    parser.add_argument('--count', '-c', type=int, choices=[1, 2, 3], help='Morty count for test trip')
    parser.add_argument('--explore', '-e', action='store_true', help='Quick exploration of all combinations')
    parser.add_argument('--trips', type=int, default=5, help='Trips per combination for exploration')

    args = parser.parse_args()

    helper = MortyAPIHelper(args.token)

    print("🛸 MORTY RESCUE API HELPER")
    print("="*60 + "\n")

    if args.request_token:
        if not args.name or not args.email:
            print("❌ Please provide --name and --email for token request")
            return
        helper.request_token(args.name, args.email)

    elif args.test:
        helper.test_connection()

    elif args.start:
        helper.start_new_episode()

    elif args.status:
        helper.get_status()

    elif args.trip:
        if args.planet is None or args.count is None:
            print("❌ Please provide --planet and --count for test trip")
            return
        helper.send_test_trip(args.planet, args.count)

    elif args.explore:
        helper.quick_exploration(args.trips)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
