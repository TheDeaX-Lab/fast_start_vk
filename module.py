import sqlite3
import random
from vk_api import VkApi, Captcha
import json
from selenium.webdriver import Chrome


class VKManager:
    def __init__(self):
        with open("login.json", "r") as f:
            data = json.load(f)
        self.session = VkApi(**data, auth_handler=self.auth_handler, captcha_handler=self.captcha_handler)
        self.session.auth()
        self.vk = self.session.get_api()

    def auth_handler(self):
        key = input("Напишите код безопасности: ")
        remember_device = True
        return key, remember_device

    def captcha_handler(self, captcha: Captcha):
        self.br.get(captcha.get_url().strip())
        self.br.execute_script("document.body.style.zoom='750%'")
        key = input("Введите каптчу: ")
        return captcha.try_again(key)

    def get_browser(self):
        self.br = Chrome()
        return self.br

    def get_api(self):
        return self.vk


# Самая простая библиотека на основе sqlite3 без зависимостей, для хранения id
class Database:
    def exec(self, command):
        r = self.cursor.execute(command)
        self.connection.commit()
        return r

    def __init__(self, name):
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()
        self.exec("create table if not exists prea (i unsigned integer)")

    def __len__(self):
        return self.exec("select count(i) from prea").fetchone()[0]

    def __contains__(self, item):
        r = self.exec("select i from prea where i={}".format(str(item))).fetchone()
        return (r is not None) and (item in r)

    def __iter__(self):
        r = self.exec("select i from prea")
        r = [k for i in r for k in i]
        return iter(r)

    def delete(self, item):
        self.exec("delete from prea where i={}".format(item))

    def set(self, item):
        if item not in self:
            self.exec("insert into prea values ({})".format(item))
        else:
            raise ValueError("{} уже существует!!!".format(item))

    def clear(self):
        r = set(str(self).split("\n"))
        for i in r:
            self.delete(i)

    def clean_duplicate(self):
        r = set(str(self).split("\n"))
        for i in r:
            self.delete(i)
            self.set(i)

    def __str__(self):
        if len(self) > 0:
            return "\n".join([str(k) for i in self.exec("select i from prea").fetchall() for k in i])
        else:
            return "None"
