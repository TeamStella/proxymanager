import concurrent.futures
import requests
import random
import os

class ProxyManager:
    def __init__(self, file_path="proxies.txt"):
        self.file_path = file_path
        self.proxies_raw = []
        self.proxies_alive = []
        self.test_url = "https://www.google.com/generate_204"
        self._initialize()

    def _initialize(self):
        self.proxies_raw = self._load_proxies()
        if not self.proxies_raw:
            return

        normalized = [self._normalize_proxy_scheme(p) for p in self.proxies_raw]

        with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
            results = list(executor.map(self._check_proxy, normalized))

        self.proxies_alive = [p for p in results if p]

    def _load_proxies(self):
        if not os.path.exists(self.file_path):
            return []
        return [ln.strip() for ln in open(self.file_path, "r", encoding="utf-8") if ln.strip() and not ln.startswith("#")]

    def _normalize_proxy_scheme(self, raw):
        raw = raw.strip()
        low = raw.lower()

        if any(low.startswith(p) for p in ["socks5h://", "socks5://", "socks4://", "http://", "https://"]):
            return raw
        if "@" in raw or ":" in raw:
            return "http://" + raw

        return raw

    def _proxy_dict(self, proxy_url):
        return {"http": proxy_url, "https": proxy_url}

    def _check_proxy(self, proxy_url):
        try:
            r = requests.get(self.test_url, proxies=self._proxy_dict(proxy_url), timeout=5)
            if r.status_code in (200, 204):
                return proxy_url
            else:
                pass
        except Exception as e:
            pass
        return None

    def get_random_proxy(self):
        if not self.proxies_alive:
            return {}
        proxy_url = random.choice(self.proxies_alive)
        return self._proxy_dict(proxy_url)
    
    def get_all_proxies(self):
        return [self._proxy_dict(p) for p in self.proxies_alive]
    
    def count_all(self):
        return len(self.proxies_raw)

    def count_alive(self):
        return len(self.proxies_alive)

    def refresh_and_count(self, max_threads=80):

        self.proxies_raw = self._load_proxies()
        if not self.proxies_raw:
            return 0, 0
        normalized = [self._normalize_proxy_scheme(p) for p in self.proxies_raw]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            results = list(executor.map(self._check_proxy, normalized))
        self.proxies_alive = [p for p in results if p]
        return len(self.proxies_raw), len(self.proxies_alive)
    def return_captcha(self):
        if not self.proxies_alive:
            return None

        proxy_url = random.choice(self.proxies_alive)

        for scheme in ("http://", "https://", "socks5://", "socks5h://", "socks4://"):
            if proxy_url.startswith(scheme):
                proxy_url = proxy_url[len(scheme):]
                break

        return proxy_url
    
def save_alive_proxies(proxy_manager, output_file="alive_proxies.txt"):
    alive_proxies = proxy_manager.get_all_proxies()
    with open(output_file, "w", encoding="utf-8") as f:
        for proxy in alive_proxies:
            f.write(proxy['http'] + "\n")
    
ascii = ("""
███╗   ██╗███████╗████████╗██╗███╗   ██╗ █████╗ ██╗     
████╗  ██║██╔════╝╚══██╔══╝██║████╗  ██║██╔══██╗██║     
██╔██╗ ██║█████╗     ██║   ██║██╔██╗ ██║███████║██║     
██║╚██╗██║██╔══╝     ██║   ██║██║╚██╗██║██╔══██║██║     
██║ ╚████║███████╗   ██║   ██║██║ ╚████║██║  ██║███████╗
╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ 
                      ⓒ copyright 2026, all rights reserved owned by TeamStella / github.com/TeamStella/proxymanager                                                                            
""")

if __name__ == "__main__":
    print(ascii)
    print("Checking proxies, This may take a while...")
    pm = ProxyManager()
    total, alive = pm.refresh_and_count()
    print(f"Total Proxies: {total}, Alive Proxies: {alive}")
    print("Random Alive Proxy:", pm.get_random_proxy())
    save_alive_proxies(pm)
    print("Alive proxies saved to 'alive_proxies.txt'")
    print("Press Enter to exit...")
    input()
    