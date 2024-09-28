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
        self.INTERVAL_DELAY = 10  # Интервал между каждым аккаунтом, 3 секунды дефолт
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

        with open("proxies.txt", "r") as file:
            proxies = file.read().splitlines()

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

                url = "https://major.bot/api/auth/tg/"
                payload = {"init_data": data}
                headers = self.base_headers.copy()
                proxy = proxies[no % len(proxies)] if proxies else None
                if proxy:
                    if len(proxies) != len(datas):
                        raise ValueError("Количество прокси и ключей не совпадает")
                    self.scraper.proxies = {
                        "http": proxy,
                        "https": proxy,
                    }
                    self.log(f"{Fore.LIGHTYELLOW_EX}Используется прокси: {proxy}")
                res = self.api_call(url, headers=headers, data=json.dumps(payload), method='POST')
                response_json = res.json()
                token = response_json["access_token"]
                squad_id = response_json["user"]["squad_id"]
                if squad_id is None:
                    headers = self.base_headers.copy()
                    headers["Authorization"] = f"Bearer {token}"
                    self.api_call("https://major.bot/api/squads/1943111151/join/?", headers=headers, method='POST')
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
        self.process_swipe(data)
        self.durov(data)
        self.task_daily(data)
        self.task_all(data)

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


                return res
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                self.log(f'{Fore.LIGHTRED_EX}Ошибка подключения соединения!')
                continue


    def streak(self, data: Data):
        url = "https://major.bot/api/user-visits/streak/"
        time.sleep(3)
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
        url = f"https://major.bot/api/users/{tele_id}/"
        time.sleep(3)
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
        url = f"https://major.bot/api/user-visits/visit/"
        time.sleep(3)
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
        url = "https://major.bot/api/bonuses/coins/"
        payload = {"coins": coins}
        time.sleep(3)
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
        url = "https://major.bot/api/roulette/"
        time.sleep(3)
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
            self.log(f"{Fore.LIGHTYELLOW_EX}Hold Coin: {Fore.LIGHTWHITE_EX}Выполнил {Fore.LIGHTWHITE_EX}+{coins}")
        else:
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Hold Coin: {Fore.LIGHTRED_EX}Еще не пришло время"
            )

    def process_spin(self, data: Data):
        point = self.spin(data)
        if point:
            self.log(f"{Fore.LIGHTYELLOW_EX}Roulette: {Fore.LIGHTWHITE_EX}Выполнил {Fore.LIGHTWHITE_EX}+{point:}")
        else:
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Roulette: {Fore.LIGHTRED_EX}Еще не пришло время"
            )

    def swipe_coin(self, data: Data, coins):
        url = "https://major.bot/api/swipe_coin/"
        payload = {"coins": coins}
        time.sleep(3)
        try:
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers, data=json.dumps(payload), method='POST')
            dat = res.json()
            status = dat["success"]

            return status
        except:
            return None

    def process_swipe(self, data: Data):
        coins = random.randint(2000, 3000)
        swipe_coin_status = self.swipe_coin(data, coins=coins)
        if swipe_coin_status:
            self.log(f"{Fore.LIGHTYELLOW_EX}Swipe Coin: {Fore.LIGHTWHITE_EX}Выполнил {Fore.LIGHTWHITE_EX}+{coins}")
        else:
            self.log(
                f"{Fore.LIGHTYELLOW_EX}Swipe Coin: {Fore.LIGHTRED_EX}Еще не пришло время"
            )

    def durov(self, data: Data):
        url = "https://raw.githubusercontent.com/GravelFire/TWFqb3JCb3RQdXp6bGVEdXJvdg/master/answer.py"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"
        time.sleep(3)
        res = self.api_call(url)

        status = res.status_code
        if status == 200:
            response_answer = json.loads(res.text)
            if response_answer.get('expires', 0) > int(time.time()):
                answer = response_answer.get('answer')
                urld = "https://major.bot/api/durov/"
                start = self.api_call(urld, headers=headers)

                if start:
                    time.sleep(3)
                    resd = self.api_call(urld, headers=headers, data=json.dumps(answer), method='POST')
                    statusd = resd.status_code
                    if statusd == 200 or statusd == 201:
                        self.log(f"{Fore.LIGHTYELLOW_EX}Puzzle Durov: {Fore.LIGHTWHITE_EX}Выполнил {Fore.LIGHTWHITE_EX}+5000")
            return None

    def do_task(self, data: Data, task_id):
        url = "https://major.bot/api/tasks/"
        try:
            time.sleep(3)
            headers = self.base_headers.copy()
            headers["Authorization"] = f"Bearer {data.token}"
            res = self.api_call(url, headers=headers, data=json.dumps({"task_id": task_id}), method='POST')
            dat = res.json()
            status = dat["is_completed"]

            return status
        except:
            return None


    def task_daily(self, data: Data):
        self.log(f"{Fore.LIGHTYELLOW_EX}Проверяю задания")
        url = "https://major.bot/api/tasks/?is_daily=true"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"
        res = self.api_call(url, headers=headers)

        for daily in reversed(res.json()):
            id = daily.get('id')
            title = daily.get('title')
            award = daily.get('award')
            time.sleep(3)
            data_done = self.do_task(data, task_id=id)
            time.sleep(5)

            if data_done :
                self.log(f"{Fore.LIGHTYELLOW_EX}Daily Task : {Fore.LIGHTWHITE_EX}{title} {Fore.LIGHTYELLOW_EX}Награда : {Fore.LIGHTWHITE_EX}{award}")

    def task_all(self, data: Data):
        url = "https://major.bot/api/tasks/?is_daily=false"
        headers = self.base_headers.copy()
        headers["Authorization"] = f"Bearer {data.token}"
        res = self.api_call(url, headers=headers)

        for task in res.json():
            id = task.get('id')
            title = task.get('title')
            award = task.get('award')
            if task.get('type') != 'subscribe_channel':
                time.sleep(3)
                data_done = self.do_task(data, task_id=id)
                time.sleep(5)

                if data_done:
                    self.log(f"{Fore.LIGHTYELLOW_EX}Task : {Fore.LIGHTWHITE_EX}{title} {Fore.LIGHTYELLOW_EX}Награда : {Fore.LIGHTWHITE_EX}{award}")

    def log(self, message):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{Fore.LIGHTBLACK_EX}[{now}]{Style.RESET_ALL} {message}")



if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
