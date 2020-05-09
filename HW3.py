import logging
import re
import psycopg2
from log import logging_decor
from conf import DATA_BASE, LOGIN, PASSWD, HST, NPORT

conn = psycopg2.connect(database=DATA_BASE, user=LOGIN,
    password=PASSWD, host=HST, port=NPORT)

cur = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS patients")
cur.execute("CREATE TABLE IF NOT EXISTS patients (patient_id SERIAL PRIMARY KEY,first_name VARCHAR(64), " + "last_name VARCHAR(64), birth_date VARCHAR(64), phone VARCHAR(64), " +"document_type VARCHAR(64), document_id VARCHAR(64))")
conn.commit()



class LogAndChange(object):
    """Дескриптор данных, в котором организована проверка полей
    из конструктора объекта Patient а также их изменение
    и логирование(логгер определим вне классов)"""

    # Проверка даты
    def _check_date(self, val):
        if len(val) == 10:  # Количество символов, включая знаки препинания и цифры, в верном формате равно 10
            if not re.match('(\d{4})-(\d{2})-(\d{2})', val):  # проверка на НЕсоответсвие паттерну 1994-10-12
                new_date = re.split('\.|/|-', val)  # Сформируем список из чисел по разделителям . / -
                if len(new_date[2]) == 4:  # если год стоит на последнем месте
                    new_date = new_date[::-1]  # исправим это
                new_string = '-'.join(new_date)  # соберем все вместе в правильно формате 1994-10-12
                val = new_string
        else:
            # self._error_logger.error('Неверный формат даты')
            raise ValueError('Неверный формат даты')
        return val

    # Проверка типа документа
    def _check_document_type(self, val):
        _valid_document_types = {
            'Паспорт': ['Паспорт', 'паспорт'],
            'Водительские права': ['Водительские права', 'водительские права', 'права'],
            'Заграничный паспорт': ['Заграничный паспорт', 'заграничный паспорт', 'загран'],
        }
        found = False  # флаг найденного значения
        for key, valid_list in _valid_document_types.items():
            if val in valid_list:  # Проверка нахождения подаваемого значения в списке допустимых значений
                val = key  # В случае успеха приведем значение к человеческому виду
                found = True  # соответственно флаг теперь тру
        if not found:  # Если подаваемого значения в списке нет, то исключение
            # self._error_logger.error('Неверный тип документа')
            raise ValueError('Неверный тип документа')
        return val

    # Проверка номера телефона
    def _check_phone(self, val):
        val = re.sub(r'[^0-9]+', r'', val)  # для начала удалим все лишнее(все то, что не цифра)
        if len(val) != 11:  # количество цифр вместе с восьмеркой или семеркой
            # self._error_logger.error('Неверное количество цифр в номере телефона')
            raise ValueError('Неверное количество цифр в номере телефона')
        return val

    # Проверка номера документа
    def _check_doc_id(self, val, obj):  # в doc_type будем передавать значение из dict объекта по ключу document_type
        _valid_len = {
            'Паспорт': 10,
            'Водительские права': 10,
            'Заграничный паспорт': 9,
        }
        doc_type = obj.__dict__.get('document_type')
        v_len = _valid_len[doc_type]  # Получим валидную длину указанного(doc_type) документа
        val = re.sub(r'[^0-9]+', r'', val)  # удалим все лишнее и непонятное

        if len(val) != v_len:
            # self._error_logger.error('Неверное количество цифр в номере документа')
            raise ValueError('Неверное количество цифр в номере документа ')
        return val

    def _check_name(self, val, obj):
        if not val.isalpha():
            # self._error_logger.error(f'Невалидное {self.name} {val}')
            raise ValueError(f'Невалидное {self.name} {val}')
        if self.name in obj.__dict__:  # Если такое имя уже существует у объекта (позволяет избежать записи
            # self._error_logger.error(f'Попытка изменить {self.name}')  # о смене фамилии или имени с None на текущую)
            raise AttributeError(f'Попытка изменить {self.name}')
        return val

    def __init__(self, name='название_атрибута'):
        # self._info_logger = logging.getLogger('info_logger')
        # self._error_logger = logging.getLogger('error_logger')
        self.name = name

    def __get__(self, obj, objtype):
        return obj.__dict__[self.name]  # вернем значение атрибута по ключу(названию атрибута)

    @logging_decor
    def __set__(self, obj, val):
        if not isinstance(val, str):  #
            # self._error_logger.error(f'Неверный тип {val} - {type(val)}')
            raise TypeError(f'Неверный тип {val} - {type(val)}')

        if self.name in ['first_name', 'last_name']:
            val = self._check_name(val, obj)
        elif self.name == 'birth_date':
            val = self._check_date(val)
        elif self.name == 'phone':
            val = self._check_phone(val)
        elif self.name == 'document_type':
            val = self._check_document_type(val)
        elif self.name == 'document_id':
            val = self._check_doc_id(val, obj)  # передаем объект для получения типа документа

        if self.name in obj.__dict__:  # изменяем только в том случае, когда объект существует
            pass
            # self._info_logger.info(
            #     f"Изменяю {self.name} у пациента {obj.first_name} {obj.last_name} c {obj.__dict__.get(self.name)} на {val}")
        obj.__dict__[self.name] = val


class Patient:
    first_name = LogAndChange('first_name')
    last_name = LogAndChange('last_name')
    birth_date = LogAndChange('birth_date')
    phone = LogAndChange('phone')
    document_type = LogAndChange('document_type')
    document_id = LogAndChange('document_id')
    current_row_idx = 1  # указатель на текущую строку

    @logging_decor
    def __init__(self, first_name, last_name, birth_date, phone, document_type, document_id):
        # self._info_logger = logging.getLogger('info_logger')

        if not (first_name and last_name and birth_date
                and phone and document_type and document_id):
            raise TypeError('Заполнены не все поля')

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.document_type = document_type
        self.document_id = document_id

        self._saved = False  # флаг, позволяющий узнать сохранен ли объект
        # в начале объектов у нас нет
        self._row_idx = None  # индекс объекта
        # self._info_logger.info(f'Создан объект {self.first_name} {self.last_name} '
        #                        f'{self.birth_date} {self.phone} {self.document_type} {self.document_id}')
        #ретурн строка выше

    @staticmethod
    def create(first_name, last_name, birth_date, phone, document_type, document_id):
        return Patient(first_name, last_name, birth_date, phone, document_type, document_id)

        # Сохраняем пациента в csv таблицу

    def save(self):
        data = [self.first_name,
                self.last_name,
                self.birth_date,
                self.phone,
                self.document_type,
                self.document_id]
        if self._saved:  # Если пациент уже существует
            #получаем его индекс cur.fetchall()[self._row_idx][0] и меняем данные пациента

            #
            # cur.execute("SELECT * FROM patients") #смотрим на пациентов
            # cur.fetchall()[self._row_idx][0] # индекс пациента
            # где-нибудь здесь получим индекс и сделаем UPDATE распакуем пациента в БД
            cur.execute(f"UPDATE patients SET first_name = '{self.first_name}', last_name = '{self.last_name}',"
                        f" birth_date = '{self.birth_date}',"
                        f"phone = '{self.phone}', document_type = '{self.document_type}',"
                        f" document_id = '{self.document_id}' WHERE patient_id = {self._row_idx}")
            conn.commit()

            # элементу списка со всеми пациентами присваются данные конкретного пациента

        else:
            self._saved = True  # Теперь пациент существует
            self._row_idx = Patient.current_row_idx  # конкретном объекту присвается номер строки в файле
            Patient.current_row_idx += 1  # после этого для следующего объекта счетчик +1

            # БД covid
            cur.execute("INSERT INTO patients (first_name, last_name, birth_date, "
                        "phone, document_type, document_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (self.first_name,
                self.last_name,
                self.birth_date,
                self.phone,
                self.document_type,
                self.document_id)) # распакуем пациента
            conn.commit()
    def __str__(self):
        return (f'{self.first_name} {self.last_name} {self.birth_date} '
                f'{self.phone} {self.document_type} {self.document_id}')


class PatientCollection:
    # def __init__(self, path_to_file):
    #     self.path_to_file = path_to_file


    def __iter__(self):
        #создать курсор, установить размер буфера на одну запись и итерироваться по курсору
        cur.execute("SELECT * FROM patients ORDER BY patient_id")
        for i in cur.fetchall():
            # print(i)
            row = [i[1], i[2], i[3], i[4], i[5], i[6]]
            p = Patient(*row)
            # p._saved = True  # пациент сохранен
            # p._row_idx = i  # в строке i
            yield p

    def limit(self, num):
        cur.execute("SELECT * FROM patients ORDER BY patient_id")
        for i in cur.fetchall():
            # print(i)
            if i[0]> num:
                break

            row = [i[1], i[2], i[3], i[4], i[5], i[6]]
            p = Patient(*row)
            # p._saved = True  # пациент сохранен
            # p._row_idx = i  # в строке i
            yield p

    # def __str__(self):
    #     return (f'{Patient.first_name} {Patient.last_name} {Patient.birth_date} '
    #             f'{Patient.phone} {Patient.document_type} {Patient.document_id}')


if __name__ == "__main__":


    # p = Patient('Vasya', 'Pupkin','08-04-1994','89126116381','паспорт','5162333666')
    # p.save()
    # p.birth_date = '12-10-1994'
    # p.save()
    #
    # p = Patient('Pip', 'Lil','08-04-1995','89126116456','паспорт','5162444666')
    # p.save()
    # p = Patient('Lil', 'Nas','08-04-1984','89126456891','паспорт','5162555666')
    # p.save()
    #
    p = Patient('kek', 'shpek', '08-04-1995', '89126116456', 'паспорт', '5162444666')
    p.save()
    p = Patient('mem', 'kekov', '08-04-1984', '89126456891', 'паспорт', '5162555666')
    p.save()

    p = Patient('Peton', 'ivanov', '08-04-1984', '89126456891', 'паспорт', '5162555666')
    p.save()
    p = Patient('Vasiliii', 'Petrov', '08-04-1984', '89126456891', 'паспорт', '5162555666')
    p.save()
    # p = Patient('Bill', 'Gates', '08-04-1984', '89126456891', 'паспорт', '51555666')
    # p.save()

    # pc = PatientCollection()
    # for i in pc:
    #     print(i)
    # print()
    #
    #
    # for x in pc.limit(5):
    #     print(x)
