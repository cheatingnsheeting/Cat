
import subprocess
import os.path
import argparse
import requests
import time

RED = "\033[91m"
BRIGHT_WHITE = "\033[97m"
LIGHT_BLUEISH_GREEN = "\033[96m"
EOL = "\033[0m"

# Config
MAX_RETRIES = 1000

class Roblox(object):
    def __init__(self, cookie: str):
        self.cookie = cookie
        response = (requests.get(
            "https://users.roblox.com/v1/users/authenticated",
            headers={ 
                "Cookie": f".ROBLOSECURITY={self.cookie}",
                "X-Csrf-Token": self._fetch_csrf()
            }
        )).json() # {'id': str, 'name': str, 'displayName': str}

        if "id" not in response:
            raise RuntimeError("Authentication failed.")
        
        self.account = response


    def favorite(self, assetId: str) -> {
        "status": int,
        "body": dict
    }:
        retries, completed = 0, False
        while not completed or retries < MAX_RETRIES:
            response = requests.post(
                f"https://catalog.roblox.com/v1/favorites/users/{self.account['id']}/assets/{assetId}/favorite",
                headers={
                    "Cookie": f".ROBLOSECURITY={self.cookie}",
                    "X-Csrf-Token": self._fetch_csrf()
                }
            )

            print(response.status_code, response.json())

            if response.status_code == 429:
                print(RED + f"Rate limit exceeded. Waiting for 60 seconds (Attempt {retries + 1}/{MAX_RETRIES})..." + EOL)
                time.sleep(60)
                retries += 1
            
            completed = True
            

        return {
            "status": response.status_code,
            "body": response.json()
        }
    

    def _fetch_csrf(self):
        response = requests.post(
            "https://auth.roblox.com/v2/logout",
            headers={ "Cookie": f".ROBLOSECURITY={self.cookie}" }
        )

        return response.headers.get('x-csrf-token')


class Oseet(object):
    def __init__(self, asset_id: int, cookies_file: str):
        self.asset_id = asset_id
        self.cookies_file = cookies_file
    

    def __call__(self):
        with open(self.cookies_file) as cf:
            list(map(lambda cookie: self._per_cookie(cookie.strip()), cf)) # .map is lazy so wrap in list() to execute


    def _per_cookie(self, cookie: str):
        try:
            roblox_user = Roblox(cookie)
            print(LIGHT_BLUEISH_GREEN + f"Successfully authenticated as {roblox_user.account['name']}, ID: {roblox_user.account['id']}" + EOL)

            favorite_outcome = roblox_user.favorite(self.asset_id)

            if favorite_outcome["status"] != 200:
                return print(RED + f"Error: {favorite_outcome['body']['errors'][0]['message']}" + EOL)
            
            print("Asset Favorited")
        except RuntimeError as _:
            print(RED + "Authentication error..." + EOL)


def main():
    parser = argparse.ArgumentParser(description='Asset favoriting script')
    parser.add_argument('--asset', type=int, help='Asset ID')
    parser.add_argument('--file', type=str, help='File name')

    args = parser.parse_args()

    subprocess.run("clear")
    print(BRIGHT_WHITE + """
    _______                        __   
    \   _  \   ______ ______ _____/  |_ 
    /  /_\  \ /  ___//  ___// __ \   __\\
    \  \_/   \\\___ \ \___ \\\  ___/|  |  
     \_____  /____  >____  >\___  >__|  
           \/     \/     \/     \/      

    """ + LIGHT_BLUEISH_GREEN + "asset favoriting at its cutest >_<" + EOL)
    print("-" * 50 + "\n")

    if not args.asset or not args.file:
        return print(RED + "Please provide both --asset and --file arguments." + EOL)
    
    
    if not os.path.isfile(args.file):
         return print(RED + f"File '{args.file}' does not exist." + EOL)

    Oseet(args.asset, args.file)()

if __name__ == "__main__":
    main()
