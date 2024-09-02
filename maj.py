import sys
import json
import time
import requests
from datetime import datetime
from colorama import init, Fore, Style
from urllib.parse import unquote
import cloudscraper
import random
init(autoreset=True)


class Data:
    def __init__(self, token, username):
        self.token = token
        self.username = username






class PixelTod:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.DEFAULT_COUNTDOWN = (8 * 3600) + (5 * 60)  # Интервал между повтором скрипта, 8 часов 5 минут дефолт
        self.INTERVAL_DELAY = 3  # Интервал между каждым аккаунтом, 3 секунды дефолт
        self.base_headers = {
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://major.glados.app",
            "Referer": "https://major.glados.app/",
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-mobile': '?1',
            'Sec-Ch-Ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36',
        }





    def data_parsing(self, data):
        return {key: value for key, value in (i.split('=') for i in unquote(data).split('&'))}

    def main(self):
        with open("initdata.txt", "r") as file:
            datas = file.read().splitlines()

        self.log(f'{Fore.LIGHTYELLOW_EX}Обнаружено аккаунтов: {len(datas)}')
        if not datas:
            self.log(f'{Fore.LIGHTYELLOW_EX}Пожалуйста, введите свои данные в initdata.txt')
            sys.exit()
        print('-' * 50)
        while True:
            for no, data in enumerate(datas):
                self.log(f'{Fore.LIGHTYELLOW_EX}Номер аккаунта: {Fore.LIGHTWHITE_EX}{no + 1}')
                data_parse = self.data_parsing(data)
                user = json.loads(data_parse['user'])
                username = user.get('username')
                self.log(f'{Fore.LIGHTYELLOW_EX}Аккаунт: {Fore.LIGHTWHITE_EX}{username} ')

                url = "https://major.glados.app/api/auth/tg/"
                payload = {"init_data": data}
                headers = self.base_headers.copy()
                res = self.api_call(url, headers=headers, data=json.dumps(payload), method='POST')
                response_json = res.json()
                token = response_json["access_token"]

                new_data = Data(token, username)



                self.process_account(new_data)
                print('-' * 50)
                self.countdown(self.INTERVAL_DELAY)
            self.countdown(self.DEFAULT_COUNTDOWN)

    def process_account(self, data):
        self.get_balance(data)
        self.process_check_in(data)
        self.process_hold_coin(data)
        self.process_spin(data)
    def countdown(self, t):
        while t:
            one, two = divmod(t, 3600)
            three, four = divmod(two, 60)
            print(f"{Fore.LIGHTWHITE_EX}Ожидание до {one:02}:{three:02}:{four:02} ", flush=True, end="\r")
            t -= 1
            time.sleep(1)
        print("                          ", flush=True, end="\r")

    def api_call(self, url, data=None, headers=None, method='GET'):
        while True:
            try:
                if method == 'GET':
                    res = self.scraper.get(url, headers=headers)
                elif method == 'POST':
                    res = self.scraper.post(url, headers=headers, data=data)
                else:
                    raise ValueError(f'Не поддерживаемый метод: {method}')

                if res.status_code == 401:
                    self.log(f'{Fore.LIGHTRED_EX}{res.text}')

                open('.http.log', 'a', encoding='utf-8').write(f'{res.text}\n')
                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                self.log(f'{Fore.LIGHTRED_EX}Ошибка подключения соединения!')
                continue

    def streak(self, data: Data):
        url = "https://major.glados.app/api/user-visits/streak/"

        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers)
            data = res.json()
            user_id = data["user_id"]
            streak = data["streak"]
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Streak: {Fore.LIGHTWHITE_EX}{streak}"
            )
            return user_id
        except:
            return None

    def balance(self, tele_id, data: Data):
        url = f"https://major.glados.app/api/users/{tele_id}/"

        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers)
            data = res.json()
            rating = data["rating"]
            return rating
        except:
            return None

    def get_balance(self, data: Data):
        tele_id = self.streak(data)

        current_balance = self.balance(tele_id=tele_id, data=data)

        if current_balance is not None:
            self.log(f"{Fore.LIGHTYELLOW_EX}Баланс: {Fore.LIGHTWHITE_EX}{current_balance:}")
        else:
            self.log(f"{Fore.LIGHTRED_EX}Не удалось получить баланс. Возможно, проблема с учетными данными.")


    def check_in(self, data: Data):
        url = f"https://major.glados.app/api/user-visits/visit/"

        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers, method='POST')
            dat = res.json()
            status = dat["is_increased"]

            return status
        except:
            return None


    def process_check_in(self, data: Data):
        check_in_status = self.check_in(data)
        if check_in_status:
            self.log(f"{Fore.LIGHTYELLOW_EX}Чек-ин: {Fore.LIGHTWHITE_EX}Выполнил")
        else:
            self.log(f"{Fore.LIGHTYELLOW_EX}Чек-ин: {Fore.LIGHTRED_EX}Уже делал")



    def hold_coin(self, data: Data, coins):
        url = "https://major.glados.app/api/bonuses/coins/"
        payload = {"coins": coins}

        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers, data=json.dumps(payload), method='POST')
            dat = res.json()
            status = dat["success"]

            return status
        except:
            return None

    def spin(self, data: Data):
        url = "https://major.glados.app/api/roulette"

        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers, method='POST')
            dat = res.json()
            point = dat["rating_award"]

            return point
        except:
            return None

    def process_hold_coin(self, data: Data):
        coins = random.randint(800, 900)
        hold_coin_status = self.hold_coin(data, coins=coins)
        if hold_coin_status:
            self.log(f"{Fore.LIGHTYELLOW_EX}Hold Coin: {Fore.LIGHTWHITE_EX}Выполнил +{coins}")
        else:
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Hold Coin: {Fore.LIGHTRED_EX}Еще не пришло время"
            )

    def process_spin(self, data: Data):
        point = self.spin(data)
        if point:
            self.log(f"{Fore.LIGHTYELLOW_EX}Барабан: {Fore.LIGHTWHITE_EX}Выполнил +{point:}")
        else:
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Барабан: {Fore.LIGHTRED_EX}Еще не пришло время"
            )

    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {message}")



if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
