import os, socket, getpass, csv, random,  datetime



# класс сервера

class Server():
    # основные параметры

    # значения по-умолчанию
    HOST = '127.0.0.1'
    PORT = 65333

    # ключ для шифрования данных
    # letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


    key = ''.join([random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')for _ in range(random.randint(1, 10))])

    # файлы
    file_name = 'log.txt'
    users_data = 'inf_users.csv'

    listen_ = True
    # передаем параметры в логи
    log_inf = {1: 'Сервер начал работу', 2: 'Порт слушает',3: 'Соединение установлено', 4: 'Получение данных', 5: 'Клиент был отсоединен',
               6: 'Сервер был отключен', 7: 'Смена порта', 8: 'Отображение команд', 9:'Отправка данных', 10:'Повтор ввода пароля',
               11:'показ логов'}

    all_commands = ['listen to', 'shutdown', 'help', 'show log']
    all_help_commands = ['listen_to - прослушивание порта', 'quit - отключение сервера', 'show log -показ логов', 'help - все команды']

    def __init__(self, open_port, host):
        self.open_port = open_port
        self.host = host


    # cмена порта для пользователей
    def change_port(self, port):
        self.open_port = port


    # запись лог файла
    @staticmethod
    def log_text(code):
        with open(Server.file_name, 'a') as file:
            file.write(str(datetime.datetime.now()) + '\t' + Server.log_inf[code]+'\n')

    @staticmethod
    def identify_users(ip, sock):
        comm = []
        with open(Server.users_data) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                comm.append(row)
        for i, row in enumerate(comm):
            if row[0] == ip:
                if row[3] == 'True':
                    sock.send(f'Приветствую пользователя {row[1]}'.encode())
                    break
                else:
                    count_pass = 1
                    while True:
                        sock.send(f'check {row[1]}'.encode())
                        answer = sock.recv(1024).decode()
                        data = Server.vernam(row[4], answer)
                        if data == row[2]:
                            sock.send(f'Приветствую пользователя {row[1]}'.encode())
                            comm[i][3] = 'True'
                            break
                        else:
                            if count_pass == 3:
                                Server.log_text(5)
                                sock.send(f'again {count_pass}'.encode())
                                break
                            count_pass +=1
                            Server.log_text(10)
                            # sock.send(f'Введен неправильно пароль, повторите еще'.encode())

                    break
        else:
            sock.send('name'.encode())
            name = sock.recv(1024).decode()
            sock.send('password'.encode())
            answer = sock.recv(1024).decode()
            key = Server.key
            password = Server.vernam(key, answer)
            sock.send(f'Приветствую пользователя {name}'.encode())
            comm.append([ip, name, password, 'True', key])
        # запись данных пользователя
        with open(Server.users_data, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(comm)

    # для кодировки пароля и информации
    @staticmethod
    def vernam(k, m):
        k = k*(len(m)//len(k)) + k[-(len(m) % len(k)):]
        return ''.join(map(chr, [i ^ x for i, x in zip(map(ord, m), map(ord, k))]))

    # команды
    def running_func(self):
        Server.log_text(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            while True:
                try:
                    # привязка хоста и порта
                    s.bind((Server.HOST, self.open_port))
                    break
                except:
                    # если порт занят, то он меняется
                    Server.log_text(7)
                    self.change_port(self.open_port+1)
            s.listen(5)
            print(f'Слушает порт: {self.open_port}')
            Server.log_text(2)
            while True:
                # получаем команды
                command = input('Введите команду (help - список команд): ')
                if command == 'shutdown':
                    Server.log_text(6)
                    raise SystemExit
                elif command == 'help':
                    Server.log_text(8)
                    print(' '.join(Server.all_help_commands))
                elif command == 'show log':
                    print('Логи: ')
                    Server.log_text(11)
                    with open(Server.file_name, 'r') as ss:
                        text = ss.read()
                        print(text)

                elif command == 'listen to':
                    print(f'Слушает порт: {self.open_port}')
                    if Server.listen_:
                        try:
                            conn, addr = s.accept()
                            Server.log_text(3)
                            Server.identify_users(addr[0], conn)
                            with conn:
                                while True:
                                    text = Server.s_recv(conn)
                                    if text == 'exit':
                                        comm = []
                                        # чтение и запись файла
                                        with open(Server.users_data, 'r') as file:
                                            reader = csv.reader(file, delimiter=',')
                                            for i, row in enumerate(reader):
                                                comm.append(row)
                                                if row[0] == addr[0]:
                                                    comm[i][3] = 'False'
                                                    break
                                        with open(Server.users_data, 'w') as file:
                                            writer = csv.writer(file, delimiter=',')
                                            writer.writerows(comm)
                                    elif text:
                                        Server.s_send(conn, text)
                                    else:
                                        break
                        except:
                            break
                    # s.listen()
                    # Server.log_text(2)
                    # print(f'Слушает порт: {self.open_port}')
                    # # новый сокет и адресс
                    # conn, addr = s.accept()
                    # Server.log_text(3)
                    # пытаемся идентифицировать пользователя
                    # Server.identify_users(addr[0], conn)
                    # with conn:
                    #     while True:
                    #         text = Server.s_recv(conn)
                    #         if text == 'exit':
                    #             comm = []
                    #             # чтение и запись файла
                    #             with open(Server.users_data, 'r') as file:
                    #                 reader = csv.reader(file, delimiter=',')
                    #                 for i, row in enumerate(reader):
                    #                     comm.append(row)
                    #                     if row[0] == addr[0]:
                    #                         comm[i][3] = 'False'
                    #                         break
                    #             with open(Server.users_data, 'w') as file:
                    #                 writer = csv.writer(file, delimiter=',')
                    #                 writer.writerows(comm)
                    #         elif text:
                    #             Server.s_send(conn, text)
                    #         else:
                    #             break
                elif command != '':
                    print('Такой команды нет')

    @staticmethod
    def check(port_user):
        try:
            port_user = int(port_user) if port_user != '' else Server.PORT
            port_user = port_user if 1 < port_user < 65537 else Server.PORT
            return port_user
        except:
            return False
    @staticmethod
    def main_programm():
        # Server.file_user()
        # Создание файла для хранение данных о пользователей
        if Server.users_data in os.listdir(os.getcwd()):
            pass
        else:
            a = open(Server.users_data, 'w')
            a.close()

        port_user = getpass.getpass(prompt="Введите порт (Enter -- по-умолчанию): ", stream=None)
        port_user = Server.check(port_user)
        if port_user == False:
            while port_user == False:
                print('Неверный ввод порта')
                port_user = getpass.getpass(prompt="Введите порт (Enter -- по-умолчанию): ", stream=None)
                port_user = Server.check(port_user)
                if port_user != False:
                    break
        a = Server(port_user, Server.HOST)
        a.running_func()


    def file_user(self):
        # Создание файла для хранение данных о пользователей
        if Server.users_data in os.listdir(os.getcwd()):
            pass
        else:
            a = open(Server.users_data, 'w')
            a.close()



    # отправка данных
    @staticmethod
    def s_send(sock, data):
        Server.log_text(9)
        text = bytearray(f'Данные: {data}\n(Длина сообщение: {len(data)})'.encode('utf-8')) # массив байт
        sock.send(text)

    # принимаем данные
    @staticmethod
    def s_recv(sock):
        text = sock.recv(1024)
        # смотрим, чтобы были данные, иначе клиент отсоединяется
        if text:
            Server.log_text(4)
            print(text.decode('utf-8'))
            text = text.decode('utf-8').split('\t')[0]
            return text
        else:
            Server.log_text(5)
            return False


if __name__ == '__main__':
    Server.main_programm()
