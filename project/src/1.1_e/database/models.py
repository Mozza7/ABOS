from db_settings import def_conn
conn = def_conn()
cursor = conn.cursor()
cursor.execute("""SELECT * FROM customers""")
db_data = list(cursor.fetchall())


def process_all(db_id):
    count_i = db_id
    print(db_data)
    try:
        ncust, url, sysusername, syspassword = db_data[count_i]
        print(f'Customer: {ncust}\nAddress: {url}\nUsername: {sysusername}')
    except IndexError:
        print(db_data[count_i], "indexerror")
        ncust = None
        url = None
        sysusername = None
        syspassword = None
    return ncust, url, sysusername, syspassword


def counter_num():
    print(func.counter)
    db_id = func.counter
    func()
    return db_id


def count(func):
    def wrapper(*args, **kwargs):
        wrapper.counter += 1
        return func(*args, **kwargs)
    wrapper.counter = 0     # set to 0 to start from beginning of table
    return wrapper


@count
def func():
    pass


def return_id():
    cursor.execute("""SELECT rowid FROM customers""")
    id_list = list(cursor.fetchall())
    return id_list
