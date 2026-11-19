import getpass
import logging
import os
import random
import sys
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys




logging.basicConfig(
    filename='7745_logs.log',
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True,
    encoding='utf-8'
)



class Parser:
    def __init__(self, link):
        self.link = link
        self.driver = webdriver.Chrome()
        self.driver.get(self.link)
        self.username = getpass.getuser()
        self.info_list = []
        self.links_list = []
        self.sort_ads = []
        self.date_dict = {}

    def switchOptions(self):
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass

                
                proxies = [
                'http://13.80.134.180:80',
                'http://37.120.189.106:80',
                'http://51.38.231.41:80',
                'http://104.248.207.60:80'
                ]
                proxy = random.choice(proxies)
                logging.info(f"Использую прокси: {proxy}")

                options = Options()
                options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.8103.78 Safari/537.36')
                options.add_argument(f'--proxy-server={proxy}')
                self.driver = webdriver.Chrome(options=options)
                self.driver.get(self.link)

                    # ПРЕДВАРИТЕЛЬНАЯ РАБОТА

    def Cockie_closet(self):
        logging.info(f"запуск программы | Пользователь: {self.username}  ")
        try:
            Button_element= WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "dldkdAccept"))) #locator = (By.ID, "dldkdAccept")  # Создаём один кортеж из двух данных # clickable_element = WebDriverWait(self.driver, 2).until(     EC.element_to_be_clickable(locator)  # Передаём его как один аргумент )
            Button_element.click()
            logging.info('Приняли куки')
        except Exception: logging.exception('Неудалось зыкрыть куки банер')

    def Filtrs(self):
        logging.info('Применяю фильтры')
        try:
            electro_button =WebDriverWait(self.driver, 5).until(
             EC.presence_of_element_located((By.XPATH, "//label[.//input[@name='feature[13196][]'] and contains(., 'электрический')]")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", electro_button)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", electro_button)
            logging.info("Фильтр 'Электрический' применён") 

        except Exception: logging.exception("Ошибка применения фильтра 'электрический'")
        time.sleep(3)


        logging.info("применеие фильтра 'управление через приложение' ")
        try:
            clickable_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, "feature[7821][]")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_element)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", clickable_element)
            logging.info("Фильтр 'управление через приложение' применён")


        except Exception: logging.exception("Ошибка при выборе фильтра 'управление через приложение'")
        time.sleep(3)


        logging.info('Настраиваем фильтр мощности')
        try:
            power_input = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,  "//*[@id='catalog-filter-form']//input[@name='feature[2683][max]']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", power_input)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", power_input)
            power_input.send_keys(str(2000))
            power_input.send_keys(Keys.ENTER)
            logging.info("Фильтр мощности установен и применены все фильтры ")
            
        except Exception:
            logging.exception("Ошибка при вводе фильтра мощности")
            time.sleep(3)

    #    ПАРСИНГ

    def get_all_links_on_page(self):
        logging.info("Собираю ссылки со страницы")
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, value='block')
        except Exception:
            logging.exception("Не удалось получить элементы со страницы")
            return []

        self.links_list = []
        for element in elements:
            href = element.get_attribute('href')
            if href is not None:
                self.links_list.append(href)

        self.sort_ads = [item for item in self.links_list
                        if item is not None and '/product/' in item]
        self.sort_ads = list(dict.fromkeys(self.sort_ads))[1:]

        logging.info(f"Всего ссылок найдено: {len(self.links_list)} | "
                    f"товаров после фильтрации: {len(self.sort_ads)}")
        return self.sort_ads

    def get_info(self):
        words = ['Основные характеристики', 'Особенности', 'Функции',
                'Защита', 'Габариты и вес', 'Габариты упаковки']

        total = len(self.sort_ads)
        logging.info(f"Начинаю парсинг объявлений: {total} шт.")

        for link in self.sort_ads:
            self.info_list = []
            logging.info(f"Обрабатываю: {link}")

            try:
                self.driver.get(link)
                time.sleep(3)

                tabble_list = self.driver.find_elements(By.TAG_NAME, 'td')
                for table in tabble_list:
                    try:
                        tabblee_list = table.find_element(By.TAG_NAME, 'span')
                        if tabblee_list.text:
                            self.info_list.append(tabblee_list.text)
                    except Exception:
                        if table.text:
                            self.info_list.append(table.text)

                self.info_list = [i for i in self.info_list if i not in words]

                self.date_dict[link] = {}
                for i in range(0, len(self.info_list)):
                    if i % 2 == 0 and i + 1 < len(self.info_list):
                        self.date_dict[link][self.info_list[i]] = self.info_list[i + 1]

                print(self.date_dict[link])

            except Exception:
                logging.exception(f"Ошибка при обработке {link}")
                continue

            time.sleep(3)

        logging.info(f"Парсинг завершён. Успешно обработано: {len(self.date_dict)} из {total}")

    def creating_csv_file(self):
        logging.info("Формирую CSV-файл")
        try:
            df_1 = pd.DataFrame(self.date_dict).T
            df_1.index.name = "link"
            df_1.to_csv("var.csv", index=True, encoding='utf-8-sig')
            logging.info(f"CSV сохранён: var.csv | строк: {len(df_1)} | колонок: {len(df_1.columns)}")

        except Exception:
            logging.exception("Не удалось сохранить CSV")

def main():
    parser = Parser('https://7745.by/catalog/obogrevateli')
    parser.Cockie_closet()
    time.sleep(5)
    try:
            parser.Filtrs()
            time.sleep(3)

            all_links = parser.get_all_links_on_page()
            for link in all_links:
                print(link)

            parser.get_info()
            print(parser.info_list)

            parser.creating_csv_file()
            
    except Exception:
            parser.switchOptions()



if __name__ == "__main__":
    main()
