#!/usr/bin/env python3
"""
Test script to verify all API keys are working correctly
"""
import os
import sys
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class APITester:
    def __init__(self):
        self.results = {}
        self.api_keys = {
            'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY'),
            'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
            'ALPACA_SECRET_KEY': os.getenv('ALPACA_SECRET_KEY')
        }

    def test_alpha_vantage(self):
        """Test Alpha Vantage API key"""
        print("\n📊 Testing Alpha Vantage API...")
        api_key = self.api_keys['ALPHA_VANTAGE_API_KEY']

        if not api_key:
            self.results['alpha_vantage'] = {
                'status': 'FAILED',
                'error': 'API key not found in environment'
            }
            print("❌ Alpha Vantage API key not set")
            return False

        try:
            # Test with NEWS_SENTIMENT endpoint
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": "GME",
                "apikey": api_key,
                "limit": 5
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "Note" in data:
                self.results['alpha_vantage'] = {
                    'status': 'RATE_LIMITED',
                    'message': data['Note']
                }
                print(f"⚠️ Alpha Vantage rate limited: {data['Note']}")
                return False
            elif "Error Message" in data:
                self.results['alpha_vantage'] = {
                    'status': 'ERROR',
                    'message': data['Error Message']
                }
                print(f"❌ Alpha Vantage error: {data['Error Message']}")
                return False
            elif "feed" in data:
                article_count = len(data.get('feed', []))
                self.results['alpha_vantage'] = {
                    'status': 'SUCCESS',
                    'articles_found': article_count,
                    'sample': data['feed'][0]['title'] if data['feed'] else None
                }
                print(f"✅ Alpha Vantage working! Found {article_count} news articles")
                if data['feed']:
                    print(f"   Sample: {data['feed'][0]['title'][:60]}...")
                return True
            else:
                self.results['alpha_vantage'] = {
                    'status': 'UNKNOWN',
                    'response': str(data)[:200]
                }
                print(f"⚠️ Unexpected Alpha Vantage response: {str(data)[:100]}")
                return False

        except Exception as e:
            self.results['alpha_vantage'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            print(f"❌ Alpha Vantage test failed: {e}")
            return False

    def test_finnhub(self):
        """Test Finnhub API key"""
        print("\n📈 Testing Finnhub API...")
        api_key = self.api_keys['FINNHUB_API_KEY']

        if not api_key:
            self.results['finnhub'] = {
                'status': 'FAILED',
                'error': 'API key not found in environment'
            }
            print("❌ Finnhub API key not set")
            return False

        try:
            # Test with company news endpoint
            url = "https://finnhub.io/api/v1/company-news"

            # Use a date range that should have data
            today = datetime.now()
            from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')

            params = {
                'symbol': 'GME',
                'from': from_date,
                'to': to_date,
                'token': api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 401:
                self.results['finnhub'] = {
                    'status': 'INVALID_KEY',
                    'error': 'Invalid API key'
                }
                print("❌ Finnhub API key is invalid")
                return False
            elif response.status_code == 429:
                self.results['finnhub'] = {
                    'status': 'RATE_LIMITED',
                    'error': 'Rate limit exceeded'
                }
                print("⚠️ Finnhub rate limit exceeded")
                return False
            elif response.status_code == 200:
                data = response.json()

                if isinstance(data, list):
                    article_count = len(data)
                    self.results['finnhub'] = {
                        'status': 'SUCCESS',
                        'articles_found': article_count,
                        'date_range': f"{from_date} to {to_date}",
                        'sample': data[0]['headline'] if data else None
                    }
                    print(f"✅ Finnhub working! Found {article_count} news articles from {from_date} to {to_date}")
                    if data:
                        print(f"   Sample: {data[0]['headline'][:60]}...")
                    return True
                else:
                    self.results['finnhub'] = {
                        'status': 'UNKNOWN',
                        'response': str(data)[:200]
                    }
                    print(f"⚠️ Unexpected Finnhub response: {str(data)[:100]}")
                    return False
            else:
                self.results['finnhub'] = {
                    'status': 'ERROR',
                    'status_code': response.status_code,
                    'response': response.text[:200]
                }
                print(f"❌ Finnhub error (status {response.status_code})")
                return False

        except Exception as e:
            self.results['finnhub'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            print(f"❌ Finnhub test failed: {e}")
            return False

    def test_alpaca(self):
        """Test Alpaca API keys"""
        print("\n📊 Testing Alpaca API...")
        api_key = self.api_keys['ALPACA_API_KEY']
        secret_key = self.api_keys['ALPACA_SECRET_KEY']

        if not api_key or not secret_key:
            self.results['alpaca'] = {
                'status': 'FAILED',
                'error': 'API key or secret not found in environment'
            }
            print("❌ Alpaca API key or secret not set")
            return False

        try:
            # Test with account endpoint (paper trading)
            url = "https://paper-api.alpaca.markets/v2/account"
            headers = {
                'APCA-API-KEY-ID': api_key,
                'APCA-API-SECRET-KEY': secret_key
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 401:
                self.results['alpaca'] = {
                    'status': 'INVALID_KEY',
                    'error': 'Invalid API credentials'
                }
                print("❌ Alpaca API credentials are invalid")
                return False
            elif response.status_code == 200:
                data = response.json()
                self.results['alpaca'] = {
                    'status': 'SUCCESS',
                    'account_status': data.get('status'),
                    'buying_power': data.get('buying_power'),
                    'equity': data.get('equity')
                }
                print(f"✅ Alpaca working!")
                print(f"   Account Status: {data.get('status')}")
                print(f"   Buying Power: ${float(data.get('buying_power', 0)):,.2f}")
                return True
            else:
                self.results['alpaca'] = {
                    'status': 'ERROR',
                    'status_code': response.status_code,
                    'response': response.text[:200]
                }
                print(f"❌ Alpaca error (status {response.status_code})")
                return False

        except Exception as e:
            self.results['alpaca'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            print(f"❌ Alpaca test failed: {e}")
            return False

    def test_historical_data_for_date(self, date_str):
        """Test if we can get historical sentiment data for a specific date"""
        print(f"\n🔍 Testing sentiment data availability for {date_str}...")

        # Test Alpha Vantage for this date
        if self.api_keys['ALPHA_VANTAGE_API_KEY']:
            try:
                url = "https://www.alphavantage.co/query"
                date_formatted = date_str.replace("-", "")
                params = {
                    "function": "NEWS_SENTIMENT",
                    "tickers": "GME",
                    "apikey": self.api_keys['ALPHA_VANTAGE_API_KEY'],
                    "time_from": f"{date_formatted}T0000",
                    "time_to": f"{date_formatted}T2359",
                    "limit": 10
                }

                response = requests.get(url, params=params, timeout=10)
                data = response.json()

                if "feed" in data and data["feed"]:
                    print(f"   ✅ Alpha Vantage has {len(data['feed'])} articles for {date_str}")
                else:
                    print(f"   ⚠️ Alpha Vantage has no data for {date_str}")
            except:
                pass

        # Test Finnhub for this date
        if self.api_keys['FINNHUB_API_KEY']:
            try:
                url = "https://finnhub.io/api/v1/company-news"
                params = {
                    'symbol': 'GME',
                    'from': date_str,
                    'to': date_str,
                    'token': self.api_keys['FINNHUB_API_KEY']
                }

                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        print(f"   ✅ Finnhub has {len(data)} articles for {date_str}")
                    else:
                        print(f"   ⚠️ Finnhub has no data for {date_str}")
            except:
                pass

    def run_all_tests(self):
        """Run all API tests"""
        print("=" * 60)
        print("🚀 API KEY VERIFICATION TEST")
        print("=" * 60)

        # Show which keys are set
        print("\n📋 Environment Check:")
        for key_name, key_value in self.api_keys.items():
            if key_value:
                masked = key_value[:4] + "..." + key_value[-4:] if len(key_value) > 8 else "***"
                print(f"   {key_name}: ✅ Set ({masked})")
            else:
                print(f"   {key_name}: ❌ Not set")

        # Run individual API tests
        alpha_ok = self.test_alpha_vantage()
        finnhub_ok = self.test_finnhub()
        alpaca_ok = self.test_alpaca()

        # Test historical data availability
        print("\n" + "=" * 60)
        print("📅 HISTORICAL DATA AVAILABILITY TEST")
        print("=" * 60)

        test_dates = [
            datetime.now().strftime('%Y-%m-%d'),  # Today
            (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Yesterday
            (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),  # Week ago
            '2024-10-01',  # Recent 2024
            '2023-10-01',  # 2023
            '2022-10-01',  # 2022
            '2021-01-28',  # GME squeeze date
        ]

        for date in test_dates:
            self.test_historical_data_for_date(date)

        # Summary
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        all_ok = alpha_ok and finnhub_ok and alpaca_ok

        if all_ok:
            print("✅ All API keys are working correctly!")
        else:
            print("⚠️ Some API keys are not working:")
            if not alpha_ok:
                print("   - Alpha Vantage: Fix needed")
            if not finnhub_ok:
                print("   - Finnhub: Fix needed")
            if not alpaca_ok:
                print("   - Alpaca: Fix needed")

        # Save results to file
        with open('api_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to api_test_results.json")

        return all_ok

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)