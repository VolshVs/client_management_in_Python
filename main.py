import random
import psycopg2


class ClientManagement:
    '''Класс позволяет удалять базу данных,
    создавать структуру базы данных,
    создавать клиента по его данным:
    имени, фамилии, email и телефону.'''

    def __init__(self, last_name: str, first_name: str,
                 email: str, phone_number: None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone_number = phone_number
        self.client_id = int
        self.phone_number_id = []

    def clear_db(self):
        '''Функция очищает базу данных (удаляет таблицы).'''
        with psycopg2.connect(database='customer_base',
                              user='postgres',
                              password='postgres') as conn:
            with conn.cursor() as cur:
                cur.execute('''
                DROP TABLE client_phone_number;
                DROP TABLE client;
                DROP TABLE phone_number;
                ''')
                conn.commit()
                return print('База данных очищена.')

    def create_db(self):
        '''Функция создает структуру базы данных (таблицы).'''
        with psycopg2.connect(database='customer_base',
                              user='postgres',
                              password='postgres') as conn:
            with conn.cursor() as cur:
                cur.execute('''
                CREATE TABLE IF NOT EXISTS client(
                    client_id SERIAL PRIMARY KEY,
                    last_name VARCHAR(20) NOT NULL,
                    first_name VARCHAR(20) NOT NULL,
                    email VARCHAR(30) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS phone_number(
                    phone_number_id SERIAL PRIMARY KEY,
                    phone_number CHAR(11) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS client_phone_number(
                    client_phone_number_id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL 
                    REFERENCES client(client_id),
                    phone_number_id INTEGER NOT NULL UNIQUE
                    REFERENCES phone_number(phone_number_id)
                );
                ''')
                conn.commit()
                return print('База данных создана.')

    def add_new_client(self):
        '''Функция, позволяющая добавить нового клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    INSERT INTO client(last_name, first_name, email) 
                    VALUES('{self.last_name}', '{self.first_name}', 
                    '{self.email}') RETURNING client_id;
                    ''')
                num_client_id = cur.fetchone()[0]
                self.client_id = num_client_id
                return print(f'Данные клиента {self.first_name} '
                             f'{self.last_name} добавлены в базу.')

    def add_new_phone_number(self):
        '''Функция, позволяющая добавить телефон для существующего клиента.'''
        if isinstance(self.phone_number, int | str):
            with psycopg2.connect(database='customer_base',
                                  user='postgres',
                                  password='postgres'
                                  ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f'''
                        INSERT INTO phone_number(phone_number) 
                        VALUES({self.phone_number}) RETURNING phone_number_id
                        ;
                        ''')
                    num_phone_id = cur.fetchone()[0]
                    conn.commit()
                    self.phone_number_id.append(num_phone_id)
                    return ClientManagement.unification_client_phone_number(self)
        elif isinstance(self.phone_number, list):
            for number in self.phone_number:
                if number is not None:
                    with psycopg2.connect(database='customer_base',
                                          user='postgres',
                                          password='postgres'
                                          ) as conn:
                        with conn.cursor() as cur:
                            cur.execute(f'''
                                INSERT INTO phone_number(phone_number) 
                                VALUES({number}) RETURNING phone_number_id
                                ;
                                ''')
                            num_phone_id = cur.fetchone()[0]
                            conn.commit()
                            self.phone_number_id.append(num_phone_id)
            return ClientManagement.unification_client_phone_number(self)

    def unification_client_phone_number(self):
        '''Функция, объединяющая базу клиента с его номерами телефонов.'''
        for num in self.phone_number_id:
            with psycopg2.connect(database='customer_base', user='postgres',
                                  password='postgres'
                                  ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f'''
                                INSERT INTO client_phone_number(client_id,
                                phone_number_id)
                                VALUES({self.client_id}, {num}) 
                                RETURNING client_phone_number_id;
                                ''')
                    conn.commit()


class ChangeInfoClearClient:
    '''Класс позволяет изменить данные клиента,
    удалить номер телефона клиента, удалить клиента.'''

    def __init__(self, client_id: None, phone_number_id: None,
                 target: None, new_info: None):
        self.client_id = client_id
        self.phone_number_id = phone_number_id
        self.target = target
        self.new_info = new_info

    def choice_target(self):
        '''Функция, определяющая выбранные изменения в данных клиента.'''
        if self.target == 'last_name':
            ChangeInfoClearClient.change_client_last_name(self)
        elif self.target == 'first_name':
            ChangeInfoClearClient.change_client_first_name(self)
        elif self.target == 'email':
            ChangeInfoClearClient.change_client_email(self)
        elif self.target == 'phone_number':
            ChangeInfoClearClient.change_client_phone_number(self)
        elif self.target == 'delete_phone_number':
            ChangeInfoClearClient.delete_client_phone_number(self)
        elif self.target == 'delete_client':
            ChangeInfoClearClient.delete_client(self)
        else:
            pass

    def change_client_last_name(self):
        '''Функция, позволяющая изменить фамилию клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    UPDATE client SET last_name=%s WHERE client_id=%s;
                    ''', (f'{self.new_info}', self.client_id))
                cur.execute('''
                SELECT * FROM client;
                ''')
                db_info = cur.fetchall()
                return print(db_info[-1])

    def change_client_first_name(self):
        '''Функция, позволяющая изменить имя клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    UPDATE client SET first_name=%s WHERE client_id=%s;
                    ''', (f'{self.new_info}', self.client_id))
                cur.execute('''
                SELECT * FROM client;
                ''')
                db_info = cur.fetchall()
                return print(db_info[-1])

    def change_client_email(self):
        '''Функция, позволяющая изменить почту клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    UPDATE client 
                    SET email=%s 
                    WHERE client_id=%s;
                    ''', (f'{self.new_info}', self.client_id))
                cur.execute('''
                SELECT * FROM client;
                ''')
                db_info = cur.fetchall()
                return print(db_info[-1])

    def change_client_phone_number(self):
        '''Функция, позволяющая изменить номер телефона клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    UPDATE phone_number 
                    SET phone_number=%s 
                    WHERE phone_number_id=%s;
                    ''', (f'{self.new_info}', self.phone_number_id))
                cur.execute('''
                SELECT * FROM phone_number;
                ''')
                db_info = cur.fetchall()
                return print(db_info[-1])

    def delete_client_phone_number(self):
        '''Функция, позволяющая удалить номер
        телефона существующего клиента.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                DELETE FROM client_phone_number WHERE phone_number_id=%s;
                ''', (self.phone_number_id,))
                cur.execute(f'''
                DELETE FROM phone_number WHERE phone_number_id=%s;
                ''', (self.phone_number_id,))
                cur.execute('''
                SELECT * FROM phone_number;
                ''')
                db_info = cur.fetchall()
                return print(db_info)

    def delete_client(self):
        '''Функция, позволяющая удалить существующего клиента.'''
        with (psycopg2.connect(database='customer_base', user='postgres',
                               password='postgres'
                               ) as conn):
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT phone_number_id 
                FROM client_phone_number 
                WHERE client_id=%s
                ''', (self.client_id,))
                phone_id_list = cur.fetchall()
                for id in phone_id_list:
                    self.phone_number_id = id
                    ChangeInfoClearClient.delete_client_phone_number(self)
                cur.execute(f'''
                DELETE FROM client WHERE client_id=%s;
                ''', (self.client_id,))
                cur.execute('''
                SELECT * FROM client;
                ''')
                db_info = cur.fetchall()
                return print(db_info)


class ClientSearch:
    '''Класс позволяет найти клиента по его данным: имени,
    фамилии, email или телефону.'''

    def __init__(self, last_name: None, first_name: None,
                 email: None, phone_number: None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone_number = phone_number

    def find_client_last_name(self):
        '''Функция ищет клиента по фамилии и сообщает о результате.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT last_name FROM client WHERE last_name=%s;
                    ''', (self.last_name,))
                if cur.fetchone() is None:
                    print(f'Клиента с фамилией {self.last_name} нет в БД')
                else:
                    print(f'{self.last_name} есть в БД')

    def find_client_first_name(self):
        '''Функция ищет клиента по имени и сообщает о результате.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT first_name FROM client WHERE first_name=%s;
                    ''', (self.first_name,))
                if cur.fetchone() is None:
                    print(f'Клиента с именем {self.first_name} нет в БД')
                else:
                    print(f'{self.first_name} есть в БД')

    def find_client_email(self):
        '''Функция ищет клиента по почте и сообщает о результате.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT email FROM client WHERE email=%s;
                    ''', (self.email,))
                if cur.fetchone() is None:
                    return print(f'Адреса почты {self.email} нет в БД')
                else:
                    return print(f'{self.email} есть в БД')

    def find_client_phone_number(self):
        '''Функция ищет клиента по номеру телефона и сообщает о результате.'''
        with psycopg2.connect(database='customer_base', user='postgres',
                              password='postgres'
                              ) as conn:
            with conn.cursor() as cur:
                cur.execute(f'''
                    SELECT phone_number FROM phone_number 
                    WHERE phone_number=%s;
                    ''', (self.phone_number,))
                if cur.fetchone() is None:
                    print(f'Телефонный номер {self.phone_number} '
                          f'отсутствует в БД')
                else:
                    print(f'{self.phone_number} есть в БД')


if __name__ == '__main__':
    last_name_list = ['Шмитс', 'Стиллавин', 'Толстой', 'Пушкин']
    first_name_list = ['Алекс', 'Валера', 'Олег', 'Святослав']
    email_list = ['8901@mail.ru', 'netology@mail.ru', 'minimi@yandex.ru',
                  'chupakabra@ya.ru', 'none@none.ru', None,
                  '0124221', '11111']
    phone_number_list = ['89015817740',
                         ['89015817743', '89015817744', '89015817'],
                         '89015817747', '890158177', None]
    new_last_name = ['Путин', 'Медведев', 'Жириновский']
    new_first_name = ['Владимир', 'Дмитрий', 'Сергей']
    new_email = ['099@mail.ru', '111@mail.ru', '222@mail.ru']
    new_phone_number = ['799999999', '7000000000', '7111111111']

    # Проверка по 5 клиентам (имя и фамилия выбираются случайным образом)
    new_client_1 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[0],
                                    phone_number_list[0])
    new_client_1.clear_db()  # Очищаем ранее созданную БД
    new_client_1.create_db()  # Создаем БД
    new_client_1.add_new_client()
    new_client_1.add_new_phone_number()

    new_client_2 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[1],
                                    phone_number_list[1])
    new_client_2.add_new_client()
    new_client_2.add_new_phone_number()  # Передается список телефонов клиента

    new_client_3 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[2],
                                    phone_number_list[2])
    new_client_3.add_new_client()
    new_client_3.add_new_phone_number()

    new_client_4 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[3],
                                    phone_number_list[3])
    new_client_4.add_new_client()
    new_client_4.add_new_phone_number()

    new_client_5 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[4],
                                    phone_number_list[4])
    new_client_5.add_new_client()
    new_client_5.add_new_phone_number()  # Телефон у клиента отсутствует

    # Проверка по last_name
    find_client_last_name = ClientSearch(random.choice(last_name_list),
                                         None, None, None)
    find_client_last_name.find_client_last_name()

    # Проверка по first_name
    find_client_first_name = ClientSearch(None,
                                          random.choice(first_name_list),
                                          None, None)
    find_client_first_name.find_client_first_name()

    # Проверка по email
    find_client_email = ClientSearch(None, None,
                                     random.choice(email_list), None)
    find_client_email.find_client_email()

    # Проверка по phone_number
    find_client_phone_number_1 = ClientSearch(None, None, None,
                                              '89015817740')  # Номер есть
    find_client_phone_number_1.find_client_phone_number()
    find_client_phone_number_2 = ClientSearch(None, None, None,
                                              '8901581740')  # Номера нет
    find_client_phone_number_2.find_client_phone_number()

    # Проверка внесения изменений
    change_1 = ChangeInfoClearClient(1, None, 'last_name', random.choice(new_last_name))
    change_1.choice_target()
    change_2 = ChangeInfoClearClient(1, None, 'first_name', random.choice(new_first_name))
    change_2.choice_target()
    change_3 = ChangeInfoClearClient(1, None, 'email', random.choice(new_email))
    change_3.choice_target()
    change_4 = ChangeInfoClearClient(None, 1, 'phone_number', random.choice(new_phone_number))
    change_4.choice_target()
    change_5 = ChangeInfoClearClient(None, 5, 'delete_phone_number', None)
    change_5.choice_target()
    change_6 = ChangeInfoClearClient(5, None, 'delete_client', None)
    change_6.choice_target()
