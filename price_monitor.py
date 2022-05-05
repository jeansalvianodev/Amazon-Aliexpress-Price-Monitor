import os
import re
import json
import smtplib
import validators
import configparser
from email.message import EmailMessage
from multiprocessing.pool import ThreadPool
from playwright.sync_api import sync_playwright
from PySimpleGUI import PySimpleGUI as sg
from convert_numbers import numbers


class Shops:
    config = configparser.ConfigParser()  # load email information
    config.read('config.ini')

    def __init__(self, values, users_input):
        self.__values = values
        self.__users_input = users_input
        self.__amazon_locator = '#corePrice_feature_div > div > span > span.a-offscreen'
        self.__amazon_locator2 = '#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center > span > span:nth-child(2) > span.a-price-whole'
        self.__aliexpress_locator = '#root > div > div.product-main > div > div.product-info > div.product-price > div.product-price-current > span'
        self.__aliexpress_locator2 = '#root > div > div.product-main > div > div.product-info > div.uniform-banner > div.uniform-banner-box > div:nth-child(1) > span.uniform-banner-box-price'
        self.__EMAIL_ADDRESS = Shops.config['gmail']['email']
        self.__PASSWORD = Shops.config['gmail']['password']

    def call_shop(self):  # scrape the product price and title
         
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_default_timeout(60000)
            page.route("**/*.svg", lambda route: route.abort())  # cancels loading images, as it is not necessary

            if self.__values['amazon']:
                try:
                    page.goto(self.__values['url_input'])
                    title = page.title()
                    handle = page.locator(self.__amazon_locator).inner_text()
                    return {"pag": title, "price": handle}
                except:
                    page.goto(self.__values['url_input'])
                    title = page.title()
                    handle = page.locator(self.__amazon_locator2)
                    return {"pag": title, "price": handle}

            if self.__values['aliexpress']:
                try:
                    page.goto(self.__values['url_input'])
                    title = page.title()
                    handle = page.locator(self.__aliexpress_locator).inner_text()
                    return {"pag": title, "price": handle}
                except:
                    page.goto(self.__values['url_input'])
                    title = page.title()
                    handle = page.locator(self.__aliexpress_locator2).inner_text()
                    return {"pag": title, "price": handle}

    def convert_values(self):  
        """converts string scraping values to any numeric type using the numbers module 
           which was copied from the systemtools module"""
        results = self.call_shop()
        title = results['pag']
        price = results['price'][2:]
        convert_price = numbers.parseNumber(price)
        convert_input = numbers.parseNumber(self.__users_input['price_input'])

        return {"pag": title, "price_float": convert_price, "price_full": price, "user_price_input": convert_input}

    def send_email(self):
        values_user = self.convert_values()
        email_shipping = self.__users_input['email_input']
        msg = EmailMessage()
        msg['Subject'] = 'Atualização do preço do produto - Price Monitor'
        msg['From'] = self.__EMAIL_ADDRESS
        msg['To'] = email_shipping

        msg.set_content(
            f'O seu produto: {values_user["pag"]} | está com o valor abaixo de: R$ {values_user["user_price_input"]}!!\n\nVeja: {self.__values["url_input"]}')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.__EMAIL_ADDRESS, self.__PASSWORD)
            smtp.send_message(msg)

        return

    def show_values(self):  
        """ format all values to appear in the last GUI window and check if the price 
           of the product is lower than the user input, if so, send the email
        """
        values = self.convert_values()
        product_value = values["price_float"]
        inputed_price = values["user_price_input"]

        if product_value <= inputed_price:
            self.send_email()
            os.remove('window_values.json')

        return f'{values["pag"]}\nR${values["price_full"]}'


def url_check(values):
    valid = validators.url(values['url_input'])  # validators to check if the link is valid

    if valid == True:
        """checks if the inserted links belong to the selected stores"""
        valid_urls = ['https://www.amazon.com.br/', 'https://pt.aliexpress.com/']

        if values['amazon'] and valid_urls[0] not in values['url_input']:
            sg.popup_error('URL Error', 'Por favor, especifique uma URL da loja selecionada.')
            raise ValueError('URL incorreta.')

        if values['aliexpress'] and valid_urls[1] not in values['url_input']:
            sg.popup_error('URL Error', 'Por favor, especifique uma URL da loja selecionada.')
            raise ValueError('URL incorreta.')

        for url in valid_urls:
            if url in values['url_input']:
                return

    sg.popup_error('URL Error', 'Por favor, especifique a URL do produto desejado')
    raise ValueError('URL não especificada')


def check_price(values):
    number_filter = numbers.parseNumber(values['price_input'])

    if number_filter == None:
        sg.popup_error('Erro de valor', 'O valor digitado não são números!')
        raise ValueError('O valor digitado não são números')


def email_check(values):
    if not values['email_input']:
        sg.popup_error('Nenhum e-mail encontrado!',
                       'Por favor, digite um e-mail para receber as atualizações sobre o produto')
        raise ValueError('Nenhum valor encontrado!')

    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if (re.search(regex, values['email_input'])):
        pass
    else:
        sg.popup_error('E-mail inválido!',
                       'Por favor, digite um e-mail válido para receber as atualizações sobre o produto')
        raise ValueError('invalid e-mail')


def create_layout():
    sg.theme('Reddit')

    def show_msg():
        pool = ThreadPool(processes=1)
        shop = Shops(window1_values, window2_values)
        async_call = pool.apply_async(shop.show_values)

        layout = [
            [sg.Text(async_call.get())],
            [sg.Text(
                f"Você receberá um e-mail de aviso quando o preço do produto for menor que o valor: R${values['price_input']}!")],
            [sg.Text('Recomece se quiser escolher outro produto')],
            [sg.Button('Resetar')]
        ]
        return sg.Window('Concluído', layout=layout, finalize=True)

    def price_input():
        layout = [
            [sg.Text(
                'Digite o valor que deseja ser avisado quando o produto atingir')],
            [sg.Text('R$: '), sg.Input(key='price_input', size=(10, 1))],
            [sg.Text('Digite um e-mail válido para receber as atualizações')],
            [sg.Input(key='email_input')],
            [sg.Button('Enviar')],
            [sg.Text('Após enviar, aguarde um instânte até a tela confirmação.')]
        ]
        return sg.Window('Escolha o preço e preencha o E-mail', layout=layout, finalize=True)

    def infos_window():
        cbox_layout = [
            [sg.Radio('Amazon Brasil', 'ecommerce', default=True, enable_events=True, key='amazon')],
            [sg.Radio('AliExpress', 'ecommerce', enable_events=True, key='aliexpress')]
        ]
        layout = [
            [sg.Text('Escolha a loja desejada: ')],
            [sg.Column(cbox_layout)],
            [sg.Text('Cole a URL completa do produto desejado: '), sg.Input(key='url_input', size=(50, 1))],
            [sg.Button('Continuar')]
        ]

        return sg.Window('Price Monitor', layout, finalize=True)

    def save_data(window1_values, window2_values):
        with open('window_values.json', 'w') as file:
            json.dump(window1_values, file)

        with open('window_values.json', 'r') as file:
            data = json.load(file)
            data['price'] = window2_values['price_input']
            data['email'] = window2_values['email_input']

        with open('window_values.json', 'w') as file:
            json.dump(data, file)

    window1, window2, window3 = infos_window(), None, None

    while True:
        window, events, values = sg.read_all_windows()

        if window == window1 and events == sg.WIN_CLOSED:
            break
        elif window == window2 and events == sg.WIN_CLOSED:
            break
        elif window == window3 and events == sg.WIN_CLOSED:
            break

        if window == window1 and events == 'Continuar':
            window1_values = values

            try:
                url_check(window1_values)
            except ValueError:
                continue

            window1.hide()
            window2 = price_input()

        if window == window2 and events == 'Enviar':
            window2_values = values

            try:
                check_price(window2_values)
                email_check(window2_values)
                save_data(window1_values, window2_values)
            except ValueError:
                continue

            window2.hide()
            window3 = show_msg()
        if window == window3 and events == 'Resetar':
            try:
                os.remove('window_values.json')
                break
            except FileNotFoundError:
                pass


def init():
    def reopening_message():
        def layout():
            pool = ThreadPool(processes=1)
            shop = Shops(window1_values, window2_values)
            async_call = pool.apply_async(shop.show_values)

            layout = [
                [sg.Text(async_call.get())],
                [sg.Text(
                    f"Você receberá um e-mail de aviso quando o preço do produto for menor que o valor R${window2_values['price_input']}!")],
                [sg.Text('Recomece se quiser escolher outro produto')],
                [sg.Button('Resetar')]
            ]
            return sg.Window('Concluído', layout=layout, finalize=True)

        with open('window_values.json', 'r') as data:
            values = json.load(data)
            window1_values = {'amazon': values['amazon'], 'aliexpress': values['aliexpress'],
                              'url_input': values['url_input']}
            window2_values = {'price_input': values['price'], 'email_input': values['email']}

        sg.theme('Reddit')
        window1 = layout()

        while True:
            events, values = window1.read()
            if events == sg.WIN_CLOSED:
                break
            if events == 'Resetar':
                try:
                    os.remove('window_values.json')
                    break
                except FileNotFoundError:
                    pass

    try:
        reopening_message()
    except FileNotFoundError:
        create_layout()


init()