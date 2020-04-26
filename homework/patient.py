import logging
import csv
import re

# Определим логгер
def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fileHandler = logging.FileHandler(log_file, 'w')
    fileHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)

setup_logger('info_logger', 'info.log', logging.INFO)
setup_logger('error_logger', 'error.log', logging.ERROR)


class LogAndChange(object):
    """Дескриптор данных, в котором организована проверка полей
    из конструктора объекта Patient а также их изменение
    и логирование(логгер определим вне классов)"""

    # Проверка даты
    def _check_date(self,val):
        if len(val) == 10: # Количество символов, включая знаки препинания и цифры, в верном формате равно 10
            if not re.match('(\d{4})-(\d{2})-(\d{2})', val): # проверка на НЕсоответсвие паттерну 1994-10-12
                new_date = re.split('\.|/|-', val) # Сформируем список из чисел по разделителям . / -
                if len(new_date[2]) == 4:# если год стоит на последнем месте
                    new_date = new_date[::-1] #исправим это
                new_string = '-'.join(new_date)  # соберем все вместе в правильно формате 1994-10-12
                val = new_string
        else:
            self._error_logger.error('Неверный формат даты')
            raise ValueError('Неверный формат даты')
        return val

    # Проверка типа документа
    def _check_document_type(self, val):
        _valid_document_types = {
            'Паспорт' : ['Паспорт', 'паспорт'],
            'Водительские права' : ['Водительские права', 'водительские права', 'права'],
            'Заграничный паспорт' : ['Заграничный паспорт', 'заграничный паспорт', 'загран'],
        }
        found = False  # флаг найденного значения
        for key, valid_list in _valid_document_types.items():
            if val in valid_list: # Проверка нахождения подаваемого значения в списке допустимых значений
                val = key # В случае успеха приведем значение к человеческому виду
                found = True# соответственно флаг теперь тру
        if not found: # Если подаваемого значения в списке нет, то исключение
            self._error_logger.error('Неверный тип документа')
            raise ValueError('Неверный тип документа')
        return val

    # Проверка номера телефона
    def _check_phone(self,val):
        val = re.sub(r'[^0-9]+', r'', val)  # для начала удалим все лишнее(все то, что не цифра)
        if len(val) != 11: #количество цифр вместе с восьмеркой или семеркой
            self._error_logger.error('Неверное количество цифр в номере телефона')
            raise ValueError('Неверное количество цифр в номере телефона')
        return val

    # Проверка номера документа
    def _check_doc_id(self, val, doc_type): # в doc_type будем передавать значение из dict объекта по ключу document_type
        _valid_len = {
            'Паспорт' : 10,
            'Водительские права' : 10,
            'Заграничный паспорт' : 9,
        }
        v_len = _valid_len[doc_type] # Получим валидную длину указанного(doc_type) документа
        val = re.sub(r'[^0-9]+', r'', val)  # удалим все лишнее и непонятное

        if len(val) != v_len:
            self._error_logger.error('Неверное количество цифр в номере документа')
            raise ValueError('Неверное количество цифр в номере документа ')
        return val

    def __init__(self, name='название_атрибута'):
        self._info_logger = logging.getLogger('info_logger')
        self._error_logger = logging.getLogger('error_logger')
        self.name = name

    def __get__(self, obj, objtype):
        return obj.__dict__[self.name] # вернем значение атрибута по ключу(названию атрибута)

    def __set__(self, obj, val):
        if not isinstance(val, str):
            self._error_logger.error(f'Неверный тип {val} - {type(val)}')
            raise TypeError(f'Неверный тип {val} - {type(val)}')
        if self.name == 'birth_date':
            val = self._check_date(val)
        if self.name == 'phone':
            val = self._check_phone(val)
        if self.name == 'document_type':
            val = self._check_document_type(val)
        if self.name == 'document_id':
            val = self._check_doc_id(val, obj.__dict__.get('document_type')) #передаем номер документа и тип документа из dict объекта
        if self.name == 'first_name':
            if not val.isalpha():
                self._error_logger.error('Невалидное имя {val}')
                raise ValueError(f'Невалидное имя {val}')
            if self.name in obj.__dict__: #Если такое имя уже существует у объекта (позволяет избежать записи
                self._error_logger.error('Попытка изменить имя') # о смене фамилии или имени с None на текущую)
                raise AttributeError('Попытка изменить имя')
        elif self.name == 'last_name':
            if not val.isalpha():
                self._error_logger.error('Невалидная фамилия {val}')
                raise ValueError(f'Невалидная фамилия {val}')
            if self.name in obj.__dict__: # Если такая фамилия уже существует у объекта
                self._error_logger.error('Попытка изменить фамилию')
                raise AttributeError('Попытка изменить фамилию')
        else:
            if self.name in obj.__dict__: # изменяем только в том случае, когда объект существует
                self._info_logger.info(
                    f"Изменяю {self.name} у пациента {obj.first_name} {obj.last_name} c {obj.__dict__.get(self.name)} на {val}")
        obj.__dict__[self.name] = val




class Patient:
    header = ['Имя', 'Фамилия', 'Дата рождения', 'Телефон', 'Вид документа', 'Номер документа']
    is_header_written = False # флаг, определяющий существование заголовка

    first_name = LogAndChange('first_name')
    last_name = LogAndChange('last_name')
    birth_date = LogAndChange('birth_date')
    phone = LogAndChange('phone')
    document_type = LogAndChange('document_type')
    document_id = LogAndChange('document_id')
    current_row_idx = 1 #указатель на текущую строку

    def __init__(self,first_name,last_name, birth_date, phone, document_type, document_id):
        self._info_logger = logging.getLogger('info_logger')

        if not(first_name and last_name and birth_date
        and phone and document_type and document_id):
            raise TypeError('Заполнены не все поля')

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.document_type = document_type
        self.document_id = document_id

        self._saved = False # флаг, позволяющий узнать сохранен ли объект
                            # в начале объектов у нас нет
        self._row_idx = None # индекс объекта
        self._info_logger.info(f'Создан объект {self.first_name} {self.last_name} '
                    f'{self.birth_date} {self.phone} {self.document_type} {self.document_id}')

    @classmethod
    def create(cls, first_name, last_name, birth_date, phone, document_type, document_id):
        return cls(first_name, last_name, birth_date, phone, document_type, document_id)

        # Сохраняем пациента в csv таблицу
    def save(self):
        data = [self.first_name,
                self.last_name,
                self.birth_date,
                self.phone,
                self.document_type,
                self.document_id]
        if self._saved: #Если пациент уже существует
            with open('patient.csv', 'r', newline='') as f:
                reader = csv.reader(f, delimiter=';')
                rows = [row for row in reader]  # список списков с полями пациента
                rows[self._row_idx] = data # элементу списка со всеми пациентами присваются данные конкретного пациента
            with open('patient.csv', 'w', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(rows)  # записываем данные в файл с измененными данными одного пациента
        else:
            self._saved = True # Теперь пациент существует
            self._row_idx = Patient.current_row_idx  # конкретном объекту присвается номер строки в файле
            Patient.current_row_idx += 1  # после этого для следующего объекта счетчик +1

            with open('patient.csv', "a", newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                if not Patient.is_header_written:  # Пишем заголовок в файл, он должен быть записан всего один раз, поэтому вот так
                    writer.writerow(Patient.header)
                    Patient.is_header_written = True
                writer.writerow(data)

    def __str__(self):
        return (f'{self.first_name} {self.last_name} {self.birth_date} '
                f'{self.phone} {self.document_type} {self.document_id}')


class PatientCollection:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.patient_list = []
        with open(self.path_to_file) as csv_fd:
            reader = csv.reader(csv_fd, delimiter=';')
            next(reader)  # пропускаем заголовок
            for ind, row in enumerate (reader,1):
                p = Patient(*row) # Распакуем данные пациента из файла для создания объекта
                p._saved = True # Теперь объект сохранен
                p._row_idx = ind # Индекс объекта
                self.patient_list.append(p) # Добавим пациента в список
            Patient.current_row_idx = len(self.patient_list)
            Patient.is_header_written = True

    def __iter__(self):
        with open(self.path_to_file, 'rb', buffering=0) as fp:
            # next(fp)
            for line in fp:
                row = line.decode().split(';')
                p = Patient(*row)
                yield p

    def limit(self,num):
        with open(self.path_to_file, 'rb', buffering=0) as fp:

            for i, l in enumerate(fp):
                if i > num:
                    break
                row = l.decode().split(';')
                p = Patient(*row)
                yield p

