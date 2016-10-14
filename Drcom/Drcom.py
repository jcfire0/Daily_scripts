#!/usr/bin/env python
# encoding: utf-8

import os
import re
import csv
import sys
import time
import random
import logging
import contextlib
import ConfigParser

import requests

@contextlib.contextmanager
def ignored(*exceptions):
    try:
        yield
    except:
        pass

def log():
    logging.basicConfig(filename='drcom.log',
                        filemode='w',
                        level=logging.INFO,
                        filemode='w',
                        format='[%(levelname)s] [%(asctime)s]: %(message)s',
                        datefmt='%d/%b/%y %H:%M:%S')
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)-6s[%(asctime)s]] %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    return logging

def read_config(config_path):
    configs = ConfigParser.ConfigParser()
    configs.read(config_path)
    count = configs.get('userinfo', 'count')
    password = configs.get('userinfo', 'password')
    enpassword = configs.get('userinfo', 'enpassword')
    config_dict = {'count': count,
                   'password': password,
                   'enpassword': enpassword}
    return config_dict


sys_version = lambda: sys.platform


class Drcom:

    LOG = log()
    host = "http://202.112.208.3/"
    IS_LOGIN = False
    headers = {
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                       "(KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36")
    }

    def __init__(self):
        self.configs = read_config('config.ini')
        self.count = self.configs.get('count')
        self.password = self.configs.get('password')
        self.enpassword = self.configs.get('enpassword')
        self.sess = requests.Session()
        self.sess.headers = self.headers
        self.post_data = {
            "DDDDD": self.count,
            "upass": self.enpassword,
            "R1": "0",
            "R2": "1",
            "para": "00",
            "0MKKey": "123456"
        }


    def http_requests(self, method, action, headers=None, form_data=None,
                      timeout=60):
        if method == "GET":
            res = self.sess.get(action, timeout=timeout)
        elif method == "POST":
            res = self.sess.post(action, data=form_data, timeout=timeout)
        else:
            self.LOG.error("NOT FOUND METHOD {0}".format(method))
        return res


    def calc_flow(self, flow):
        flow0 = flow % 1024
        flow1 = flow - flow0
        flow0 = flow0 * 1000
        flow0 = flow0 - flow0 % 1024
        return float('{0}.{1}'.format(flow1 / 1024, flow0 / 1024))

    def get_user_message(self):
        if self.IS_LOGIN:
            message_html = self.http_requests("GET", self.host).content
            flow = int(re.findall("flow=\'(\d+)", message_html)[0])
            used = self.calc_flow(flow)
            balance = 25000 - used
            self.used , self.balance = used, balance
            return True

    def login(self):
        if not self.IS_LOGIN:
            res = self.http_requests("POST",
                                     self.host,
                                     form_data=self.post_data).content
            self.IS_LOGIN = 'You have successfully logged into our system' in res
            self.get_user_message() if self.IS_LOGIN else None
            return self.IS_LOGIN
        else:
            self.LOG.error("YOU ARE ALDEARY LOGIN.")

    def logout(self):
        if self.IS_LOGIN():
            res = self.http_requests("GET", self.host+"F.htm").content
            self.IS_LOGIN = "can not modify" in res
            return self.IS_LOGIN
        else:
            self.LOG.error("YOU ARE NOT LOGIN.")

def get_count_pswd(path):
    symbol = '\\' if 'win' in sys_version() else '/'
    college = random.choice(os.listdir(path))
    _class = path + symbol + college + symbol + random.choice(
        os.listdir(path+symbol+college))
    with open(_class, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        random_list = random.choice(list(reader)[1:])
        return [random_list[1], random_list[2][-6:]]


def write_conf(count, password):
    if 'linux' in sys_version():
        os.system("./encrypt {0} {1}".format(count, password))
    elif 'win' in sys.platform:
        os.system(".\encrypt.exe {0} {1}".format(count, password))

def abu_login():
    main = Drcom()
    main.login()
    if main.IS_LOGIN:
        main.LOG.info("Loged in as count: {0}, password: {1}".format(
            main.count, main.password))
        main.LOG.info('Used {0} MBytes, {1} MBytes balanced'.format(
            main.used, main.balance))
    else:
        main.IS_LOGIN = False
        main.LOG.warn('Login failed...')

    return main.IS_LOGIN, main

def start():
    LOGED_IN = False
    while not LOGED_IN:
        count, password = get_count_pswd("CUMTB-16")
        write_conf(count, password)
        LOGED_IN, sess = abu_login()
    return LOGED_IN, sess


if __name__ == "__main__":
    CONTINUE = True
    while CONTINUE:
        status, sess = start()
        start_time = time.time()
        while (time.time() - start_time) < 2700 and CONTINUE:
            time.sleep(1)
            try:
                sess.get_user_message()
            except IndexError:
                break
            except KeyboardInterrupt:
                CONTINUE = False
                start()[1].LOG.warn("Bye.")
