import requests
# import pprint
from collections import Counter


class Skills:
    def __init__(self):
        self.skill_request = 'Python'
        self.vacancies_number = 0
        self.text = ''
        self.list_common = []
        self.final_skills = []

    def get_vacancies_json(self):   # выгружаем вакансии по параметрам
        raw_data = []
        url = 'https://api.hh.ru/vacancies'
        for i in range(20):     # если ввести 100, будет долго обрабатываться (по умолчанию 'per_page': 20)
            params = {'text': self.skill_request,
                      'page': i}
            req = requests.get(url, params=params).json()
            raw_data.append(req)  # страницы с вакансиями
        return raw_data

    def select(self):       # отбираем текст требований
        data = self.get_vacancies_json()
        re_re = []  # requirements & responsibilities
        selected = []
        for page in data:
            items = page['items']  # список вакансий в форме словарей
            for vacancy in items:
                re_re.append(vacancy['snippet'])  # выбираем в вакансиях словари с требованиями
                self.vacancies_number += 1
            for element in re_re:
                selected.extend(list(element.values()))  # требования вносим в общий список
                for no_el in selected:
                    if no_el is None:  # отбрасываем пустые элементы (не str)
                        selected.remove(no_el)
        # print('Содержание всех вакансий:', selected)
        return selected

    def general_text(self):     # очищаем текст
        exclude = ['<highlighttext>', '</highlighttext>', '*', ',', '(', ')']
        change_into_space = ['...', '.', '  ']
        data = self.select()
        for i in data:
            self.text += i.lower()
        for el in change_into_space:
            self.text = self.text.replace(el, ' ')
        for el in exclude:
            self.text = self.text.replace(el, '')
        # print('Общий текст строчными буквами: ', self.text)
        return self.text

    def counter(self):      # отбираем частотные слова
        data = self.general_text()
        data_new = []
        data = data.split()
        exclude = ['для', 'and', 'или']
        for word in data:
            if word not in exclude and len(word) > 2:    # убираем предлоги и служебные слова их списка
                data_new.append(word)
        common_words = Counter(data_new).most_common(20)
        print(common_words)       # для наглядности
        for i in common_words:
            self.list_common.append(i[0])
        return self.list_common

    def skills_suggest(self):       # из частотных слов отбираем навыкм по подсказкам в API
        data = self.list_common
        skills_raw = []
        skills_list = []
        url = 'https://api.hh.ru/suggests/skill_set'
        for i in data:
            result = requests.get(url, params={'text': i}).json()
            skills_raw.append(result)
        for i in skills_raw:
            items = i['items']      # list of dicts
            for el in items:
                skill = el['text']
                skills_list.append(skill.lower())
        return skills_list

    def compare(self):      # проверяем, содержится ли навык в такой формулировке в исходном тексте вакансии
        data = self.skills_suggest()
        final_skills = []
        for el in data:
            if self.text.count(el):
                final_skills.append(el)
        print('Список навыков:', final_skills)
        return final_skills

    def frequency(self):
        common_skills = []
        for skill in self.compare():
            percent = 100 * self.text.count(skill)//self.vacancies_number
            count = (skill, percent)
            common_skills.append(count)
        print('Средний процент встречи навыка на одну вакансию:')
        common_skills.sort(key=lambda x: x[1], reverse=True)
        common_10_skills = common_skills[:10]
        print(common_10_skills)
        return common_10_skills


if __name__ == "__main__":
    sk = Skills()
    sk.counter()
    sk.frequency()
