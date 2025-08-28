import requests
import time
from datetime import datetime, timedelta
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configuration
url = "http://52.24.104.170:8086/RestSimulator?Operation=getActiveResolutions&country={}"
headers = {"User-Agent": "android-async-http"}
PROXY_USERNAME = "OffensiveES"
PROXY_PASSWORD = "8es6tmdfh1g5"

# Proxy list
proxy_text = """45.117.55.38:6684
154.36.110.129:6783
31.58.9.75:6148
138.128.148.180:6740
138.128.148.1:6561
45.150.176.238:6111
82.22.234.234:8084
194.113.119.88:6762
45.117.55.56:6702
31.58.24.8:6079
91.223.126.2:6614
154.36.110.40:6694
91.223.126.31:6643
138.128.148.135:6695
45.150.176.42:5915
154.36.110.214:6868
45.150.176.207:6080
45.159.53.38:7410
45.159.53.147:7519
45.159.53.212:7584
154.36.110.161:6815
31.58.9.205:6278
45.117.55.93:6739
91.223.126.19:6631
45.150.176.204:6077
138.128.148.50:6610
45.150.176.106:5979
154.36.110.27:6681
154.36.110.186:6840
91.223.126.55:6667
45.159.53.61:7433
154.36.110.11:6665
45.117.55.89:6735
91.223.126.100:6712
82.22.234.134:7984
82.22.234.126:7976
31.58.24.248:6319
82.22.234.20:7870
82.22.234.96:7946
31.58.24.34:6105
91.223.126.16:6628
31.58.9.98:6171
31.58.9.216:6289
138.128.148.105:6665
45.117.55.253:6899
45.117.55.111:6757
138.128.148.179:6739
138.128.148.156:6716
194.113.119.197:6871
45.150.176.208:6081
154.36.110.136:6790
45.150.176.151:6024
31.58.9.156:6229
82.22.234.24:7874
138.128.148.113:6673
154.36.110.212:6866
82.22.234.86:7936
154.36.110.22:6676
31.58.24.218:6289
194.113.119.16:6690
194.113.119.92:6766
31.58.24.122:6193
154.36.110.185:6839
194.113.119.109:6783
82.22.234.175:8025
45.150.176.134:6007
31.58.9.134:6207
31.58.9.74:6147
31.58.9.71:6144
154.36.110.89:6743
31.58.24.173:6244
194.113.119.23:6697
82.22.234.44:7894
31.58.9.204:6277
91.223.126.131:6743
45.150.176.32:5905
138.128.148.80:6640
45.117.55.5:6651
31.58.9.23:6096
45.117.55.173:6819
138.128.148.163:6723
31.58.9.180:6253
45.150.176.29:5902
31.58.24.233:6304
91.223.126.37:6649
194.113.119.3:6677
31.58.9.169:6242
82.22.234.119:7969
194.113.119.105:6779
45.150.176.188:6061
82.22.234.150:8000
138.128.148.236:6796
45.117.55.123:6769
91.223.126.127:6739
194.113.119.113:6787
91.223.126.36:6648
45.159.53.248:7620
82.22.234.50:7900
138.128.148.226:6786
154.36.110.221:6875"""

# Parse proxies and create a cycle iterator
proxies_list = [f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{proxy}" for proxy in proxy_text.split()]
proxy_pool = cycle(proxies_list) if proxies_list else None

# Proxy usage tracking - need thread-safe access
proxy_usage = {proxy: {'count': 0, 'last_reset': datetime.now()} for proxy in proxies_list}
proxy_lock = Lock()

def get_available_proxy():
    """Get an available proxy that hasn't been used more than 3 times in the last 20 seconds"""
    if not proxy_pool:
        return None
    
    with proxy_lock:
        current_time = datetime.now()
        
        # Check all proxies to find one that's available
        for _ in range(len(proxies_list)):
            proxy = next(proxy_pool)
            usage_data = proxy_usage[proxy]
            
            # Reset count if more than 20 seconds have passed
            if current_time - usage_data['last_reset'] > timedelta(seconds=20):
                usage_data['count'] = 0
                usage_data['last_reset'] = current_time
            
            # Use this proxy if it has less than 3 requests
            if usage_data['count'] < 3:
                usage_data['count'] += 1
                return proxy
        
        # If no proxy is available, wait 2 seconds and try again
        print("No proxies available. Waiting 2 seconds...")
        time.sleep(2)
        return get_available_proxy()

def ESResolutionScanner(target_country):
    """Scan for resolutions related to the specified target country"""
    # Read countries
    with open("countries.text", "r") as f:
        countries = [line.strip() for line in f.readlines() if line.strip()]

    def process_country(country):
        formatted_url = url.format(country)
        
        # Get proxy for this request
        proxy = get_available_proxy()
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None
        
        #print(f"Scanning {country} using proxy: {proxy.split('@')[1] if proxy else 'No proxy'}")
        
        try:
            response = requests.get(
                formatted_url, 
                headers=headers, 
                proxies=proxy_dict,
                timeout=1000
            )
            
            data = response.json()
            for resolution in data['resolutions']:
                if resolution['country_name'] == target_country or resolution['country_to_attack'] == target_country:
                    if resolution['country_name'] != target_country:
                        print(f"ID: {resolution['id']} == scanned in {country}")
                    elif resolution['country_to_attack'] != target_country:
                        print(f"ID: {resolution['id']} == scanned in {country}")
                    else:
                        print(f"Both fields reference same country, ID: {resolution['id']}")
                        
        except requests.exceptions.RequestException as e:
            print(f"Error for {country}: {e}")
        except ValueError as e:
            print(f"JSON parsing error for {country}: {e}")

    # Process each country with concurrency
    with ThreadPoolExecutor(max_workers=100) as executor:
        # Submit all tasks to the executor
        futures = {executor.submit(process_country, country): country for country in countries}
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            country = futures[future]
            try:
                future.result()  # This will re-raise any exceptions that occurred
            except Exception as e:
                print(f"Unexpected error processing {country}: {e}")

    print("Scanning completed.")