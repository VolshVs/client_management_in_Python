import os
import random
import psycopg2
from psycopg2 import sql


class ClientManagement:
    '''Класс позволяет удалять базу данных,
    создавать структуру базы данных,
    создавать клиента с данными:
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
        with conn.cursor() as cur:
            cur.execute('''
            DROP TABLE phone_number;
            DROP TABLE client;
            ''')
            conn.commit()
            return print('База данных очищена.')

    def create_db(self):
        '''Функция создает структуру базы данных (таблицы).'''
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
                client_ph_id INTEGER NOT NULL REFERENCES client(client_id),
                phone_number CHAR(11) UNIQUE NOT NULL
            );
            ''')
            conn.commit()
            return print('База данных создана.')

    def add_new_client(self):
        '''Функция, позволяющая добавить нового клиента.'''
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO client(last_name, first_name, email)
                VALUES(%(last_name)s, %(first_name)s, %(email)s) 
                RETURNING client_id
                ;
                ''', {
                'last_name': self.last_name,
                'first_name': self.first_name,
                'email': self.email
            })
            conn.commit()
            num_client_id = cur.fetchone()[0]
            self.client_id = num_client_id
            return print(f'Данные клиента {self.first_name} '
                         f'{self.last_name} добавлены '
                         f'в базу. Клиент id: {self.client_id}.')

    def add_new_phone_number(self):
        '''Функция, позволяющая добавить телефон для существующего клиента.'''
        if isinstance(self.phone_number, int | str):
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO phone_number(client_ph_id, phone_number)
                    VALUES(%s, %s) 
                    RETURNING phone_number_id
                    ;
                    ''', (self.client_id, self.phone_number))
                num_phone_id = cur.fetchone()[0]
                conn.commit()
                self.phone_number_id.append(num_phone_id)
                return print(f'Номер {self.phone_number} добавлен '
                             f'к клиенту с id {self.client_id}')
        elif isinstance(self.phone_number, list):
            for number in self.phone_number:
                if number is not None:
                    with conn.cursor() as cur:
                        cur.execute('''
                            INSERT INTO phone_number(client_ph_id, 
                            phone_number)
                            VALUES(%s, %s) 
                            RETURNING phone_number_id
                            ;
                            ''', (self.client_id, number))
                        num_phone_id = cur.fetchone()[0]
                        conn.commit()
                        self.phone_number_id.append(num_phone_id)
            return print(f"Номера {', '.join(self.phone_number)} добавлены "
                         f"к клиенту с id {self.client_id}")


class ClearChangeInfo(ClientManagement):
    '''Класс позволяет изменить данные клиента,
    удалить номер телефона клиента, удалить клиента.'''

    def __init__(self, client_id: None, phone_number_id: None,
                 target: None, new_info: None):
        self.client_id = client_id
        self.phone_number_id = phone_number_id
        self.target = target
        self.new_info = new_info

    def delete_client_phone_number(self):
        '''Функция, позволяющая удалить номер
        телефона существующего клиента.'''
        with conn.cursor() as cur:
            number = self.new_info or self.phone_number
            cur.execute('''
            DELETE 
            FROM phone_number 
            WHERE phone_number = %s
            ;
            ''', (number,))
            cur.execute('''
            SELECT * FROM phone_number
            ;
            ''')
            conn.commit()
            return print(f'Телефонный номер {number} удален.')

    def delete_client(self):
        '''Функция, позволяющая удалить существующего клиента.'''
        with conn.cursor() as cur:
            cur.execute('''
            SELECT client_id
            FROM client
            WHERE client_id = %s
            ;
            ''', (self.client_id,))
            req = cur.fetchone()
            if isinstance(req, None | str):
                return print(f'Клиента с id {self.client_id} в БД нет.')
            elif isinstance(req, tuple):
                cur.execute('''
                SELECT phone_number
                FROM phone_number
                WHERE client_ph_id = %s
                ;
                ''', (self.client_id,))
                phone_num_list = cur.fetchall()
                for id in phone_num_list:
                    self.phone_number = id[0]
                    ClearChangeInfo.delete_client_phone_number(self)
                cur.execute('''
                DELETE 
                FROM client 
                WHERE client_id = %s
                ;
                ''', (self.client_id,))
                cur.execute('''
                SELECT * FROM client;
                ''')
                conn.commit()
                return print(f'Клиент с id {self.client_id} из БД удален.')

    def change_client(self):
        '''Функция, позволяющая изменить данные клиента.'''
        with conn.cursor() as cur:
            request = sql.SQL('''
                UPDATE client 
                SET {target} = {new_info} 
                WHERE client_id = {client_id};
                ''').format(
                target=sql.Identifier(self.target),
                new_info=sql.Literal(self.new_info),
                client_id=sql.Literal(self.client_id)
            )
            cur.execute(request)
            cur.execute('''
                SELECT * FROM client;
                ''')
            db_info = cur.fetchall()
            conn.commit()
            return print(f'Произошла замена {self.target} '
                         f'в строке БД {db_info[-1]}')

    def change_client_phone_number(self):
        '''Функция, позволяющая изменить номер телефона клиента.'''
        with conn.cursor() as cur:
            cur.execute('''
                UPDATE phone_number
                SET phone_number=%s
                WHERE phone_number_id=%s;
                ''', (self.new_info, self.phone_number_id))
            cur.execute('''
            SELECT * FROM phone_number;
            ''')
            db_info = cur.fetchall()
            conn.commit()
            return print(f'Произошла замена номера телефона '
                         f'на {db_info[-1][-1]}')


class ClientSearch(ClientManagement):
    '''Класс позволяет найти клиента по его данным: имени,
    фамилии, email или телефону.'''

    def __init__(self, last_name: None, first_name: None,
                 email: None, phone_number: None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.phone_number = phone_number
        self.target = last_name or first_name or email or phone_number
        self.result = None
        self.tab = None

    def find_client(self):
        '''Функция ищет клиента по фамилии,
        имени, почте, номеру телефона
        и сообщает о результате.'''
        if self.last_name is None:
            pass
        else:
            self.result = 'last_name'
            self.tab = 'Фамилия'
        if self.first_name is None:
            pass
        else:
            self.result = 'first_name'
            self.tab = 'Имя'
        if self.email is None:
            pass
        else:
            self.result = 'email'
            self.tab = 'Почта'
        if self.phone_number is None:
            pass
        else:
            self.result = 'phone_number'
            self.tab = 'Телефонный номер'
        with conn.cursor() as cur:
            request = sql.SQL('''
                SELECT client_id
                FROM client AS cl
                JOIN phone_number AS ph ON cl.client_id = ph.client_ph_id
                WHERE {column} = {target}
                ;
                ''').format(
                column=sql.Identifier(self.result),
                target=sql.Literal(self.target)
            )
            cur.execute(request)
            client_list = list(cur.fetchall())
            if len(client_list) == 0:
                return print(f'Клиент с данными {self.tab} {self.target} '
                             f'в БД отсутствует.')
            else:
                for client in list(set(client_list)):
                    return print(f'{self.tab} {self.target} у клиента '
                                 f'с id {client[0]}.')


if __name__ == '__main__':
    last_name_list = ['Шмитс', 'Стиллавин', 'Толстой', 'Пушкин']
    first_name_list = ['Алекс', 'Валера', 'Олег', 'Святослав']
    email_list = ['8901@mail.ru', 'netology@mail.ru', 'minimi@yandex.ru',
                  'chupakabra@ya.ru', 'none@none.ru',
                  '0124221', '11111']
    phone_number_list = ['89015817740',
                         ['89015817743', '89015817744', '89015817'],
                         '89015817747', '890158177', '80912223']
    new_last_name = ['Путин', 'Медведев', 'Жириновский']
    new_first_name = ['Владимир', 'Дмитрий', 'Сергей']
    new_email = ['099@mail.ru', '111@mail.ru', '222@mail.ru']
    new_phone_number = ['799999999', '7000000000', '7111111111']

    with psycopg2.connect(database='customer_base',
                          user='postgres',
                          password='12345') as conn:
        pass
    # Проверка по 5 клиентам (имя и фамилия выбираются случайным образом)
    new_client_1 = ClientManagement(random.choice(last_name_list),
                                    random.choice(first_name_list),
                                    email_list[0],
                                    phone_number_list[0])
    new_client_1.clear_db()  # Очищаем ранее созданную БД
    new_client_1.create_db()  # Создаем БД
    print()
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
    print()

    # Проверка по last_name
    find_client_last_name = ClientSearch(random.choice(last_name_list),
                                         None, None, None)
    find_client_last_name.find_client()

    # Проверка по first_name
    find_client_first_name = ClientSearch(None,
                                          random.choice(first_name_list),
                                          None, None)
    find_client_first_name.find_client()

    # Проверка по email
    find_client_email = ClientSearch(None, None,
                                     random.choice(email_list), None)
    find_client_email.find_client()

    # Проверка по phone_number
    find_client_phone_number_1 = ClientSearch(None, None, None,
                                              '89015817740')  # Номер есть
    find_client_phone_number_1.find_client()
    find_client_phone_number_2 = ClientSearch(None, None, None,
                                              '8901581740')  # Номера нет
    find_client_phone_number_2.find_client()
    #
    #     # Проверка внесения изменений
    change_1 = ClearChangeInfo(3, None, 'last_name', random.choice(new_last_name))
    change_1.change_client()
    change_2 = ClearChangeInfo(1, None, 'first_name', random.choice(new_first_name))
    change_2.change_client()
    change_3 = ClearChangeInfo(1, None, 'email', random.choice(new_email))
    change_3.change_client()
    change_4 = ClearChangeInfo(None, 1, 'phone_number', random.choice(new_phone_number))
    change_4.change_client_phone_number()
    print()
    change_5 = ClearChangeInfo(None, None, None, '799999999')
    change_5.delete_client_phone_number()
    change_6 = ClearChangeInfo(40, None, None, None)
    change_6.delete_client()
    change_7 = ClearChangeInfo(2, None, None, None)
    change_7.delete_client()
    conn.close()
