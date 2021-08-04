import requests
# import pprint


class Wage:
    def __init__(self):
        self.average_salary = 0
        self.salary = 0
        self.v_currency = ''        # валюта ЗП, указанная в вакансии
        self.text = ''
        self.city = ''

    def get_vacancies_json(self):
        data_vacancies = []
        url = 'https://api.hh.ru/vacancies'
        params = {'text': 'Python',
                  'area': '1',  # нас интересует Москва
                  'only_with_salary': 'true',  # ищем только с указанной ЗП
                  }
        self.text = params['text']
        pages_req = requests.get(url, params=params).json()
        pages_number = pages_req['pages']  # количество страниц по запросу с нашими параметрами
        # for i in range(2):      ### тест!
        for i in range(pages_number):
            params = {'text': 'Python',
                      'area': '1',
                      'only_with_salary': 'true',
                      'page': i,
                      'per_page': pages_req['per_page']
                      # количество вакансий на страницу такое же, как в предыдущем запросе
                      }
            result = requests.get(url, params=params).json()
            data_vacancies.append(result)  # постранично добавляем результаты в список
        return data_vacancies

    def currency_exchange(self):
        dictionaries = requests.get('https://api.hh.ru/dictionaries').json()
        for currency in dictionaries['currency']:
            if currency['code'] == self.v_currency:
                self.salary = round(self.salary/currency['rate'], 2)   # округляем до копеек
        return self.salary

    def get_salary(self):
        vacancies_count = 0
        NDFL = 0.13
        salary_sum = 0
        vacancies_list = self.get_vacancies_json()
        for page in vacancies_list:
            items = page['items']
            # pprint.pprint(items)                  # печать вакансий
            for vacancy in items:
                self.city = vacancy['area']['name']
                if vacancy['salary']['from']:       # берем нижнюю границу зарплатной вилки
                    vacancies_count += 1
                    self.salary = vacancy['salary']['from']
                    self.v_currency = vacancy['salary']['currency']
                    if self.v_currency == "RUR":
                        pass
                    else:   # если ЗП указана в валюте, применяем перевод в рубли
                        self.currency_exchange()
                    if vacancy['salary']['gross']:
                        self.salary = round(self.salary*(1 - NDFL), 2)
                        # считаем зарплату "на руки", то есть за вычетом налога, округлив до копеек
                    salary_sum += self.salary
                else:
                    pass    # вакансии без указания нижней границы не рассматриваем
        self.average_salary = salary_sum // vacancies_count
        return self.average_salary

    def result(self):
        self.get_vacancies_json()
        self.get_salary()
        return print(f'Средняя ЗП по запросу "{self.text}" в городе {self.city} '
                     f'по консервативному расчету составляет {self.get_salary()} ₽')


if __name__ == "__main__":
    data = Wage()
    data.result()
