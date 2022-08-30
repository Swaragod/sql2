import psycopg2
print('''Введите команду:
        new_db          + Функция, создающая структуру БД (таблицы)
        add_client      + Функция, позволяющая добавить нового клиента
        add_phone       + Функция, позволяющая добавить телефон для существующего клиента
        change_client   +- Функция, позволяющая изменить данные о клиенте
        del_phone       + Функция, позволяющая удалить телефон для существующего клиента (удаляет только выбранный номер)
        del_client      + Функция, позволяющая удалить существующего клиента
        find_client     - Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)''')


def create_db(conn):



    cur.execute("DROP TABLE IF EXISTS phones;")
    cur.execute("DROP TABLE IF EXISTS emails;")
    cur.execute("DROP TABLE IF EXISTS clients;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id_client SERIAL PRIMARY KEY,
            name VARCHAR(60) NOT NULL,
            surname VARCHAR(60)
            );
            """)

    cur.execute("""       
        CREATE TABLE IF NOT EXISTS emails(
            email VARCHAR(254) UNIQUE PRIMARY KEY,
            id_client INTEGER REFERENCES clients(id_client)
            );
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            phone VARCHAR(20) UNIQUE PRIMARY KEY,
            id_client INTEGER REFERENCES clients(id_client)
            );
        """)

    conn.commit()


def add_client(add_name, add_surname=None, add_phone=None, add_email=None):
    cur.execute("""
        INSERT INTO clients(name, surname)
        VALUES (%s, %s) RETURNING id_client, name, surname;
        """, (add_name, add_surname))
    returning_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO emails(email, id_client)
        VALUES (%s, %s);
        """, (add_email, returning_id))

    cur.execute("""
        INSERT INTO phones(phone, id_client)
        VALUES (%s, %s);
        """, (add_phone, returning_id))

    conn.commit()


def add_phone(client_id, add_phone):
    cur.execute(""" 
        INSERT INTO phones(phone, id_client)
        VALUES (%s, %s);
        """, (add_phone, client_id))


    conn.commit()


def change_client(client_id, name=None, surname=None, phone=None, email=None):
    cur.execute("""
        UPDATE clients SET name = %s, surname = %s WHERE id_client = %s;
        """,(name, surname, client_id,))

    cur.execute("""
        UPDATE phones SET phone = %s WHERE id_client = %s;
            """, (phone, client_id))
    cur.execute("""
            UPDATE emails SET email = %s WHERE id_client = %s;
                """, (email, client_id))


    conn.commit()


def delete_phone(client_id, del_phone):
    cur.execute(""" 
        DELETE FROM phones
        WHERE phone=%s AND id_client=%s;
        """, (str(del_phone), client_id))
    conn.commit()


def delete_client(client_id):
    cur.execute("""
        DELETE FROM emails WHERE id_client = %s;
        """, (client_id,))
    cur.execute("""
           DELETE FROM phones WHERE id_client = %s;
           """, (client_id,))
    cur.execute("""
           DELETE FROM clients WHERE id_client = %s;
           """, (client_id,))
    conn.commit()


def find_client(name=None, surname=None, email=None, phone=None):
    cur.execute("""
               SELECT c.id_client, name, surname FROM clients c
               LEFT JOIN emails e ON c.id_client = e.id_client
               LEFT JOIN phones p ON c.id_client = p.id_client
               WHERE c.name = %s OR c.surname = %s OR e.email = %s  OR p.phone = %s;
               """, (name, surname, email, str(phone)))
    print(cur.fetchall())


conn = psycopg2.connect(database="taskdb", user="postgres", password="111")

with conn.cursor() as cur:

    create_db(conn)

    add_client('Эрик', 'Айд', 89222723723, 'someone@mail.ru')
    add_client('Терри', 'Джонс', 89025368574, 'terry@email.ru')
    add_client('Терри', 'Гиллиам', 89990253696, 'TG@undermail.un')
    add_phone(3, 89000111222)
    add_phone(2, 89994562369)
    delete_phone(2, 89994562369)
    change_client(2, 'Грэм', 'Чепмен', 123123123, 'Gram@gmail.com')
    delete_client(3)
    find_client(None, None, 'Gram@gmail.com', '123123123')


conn.close()

