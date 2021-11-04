import socket, getpass, re


# Значение по-умолчанию

HOST = '127.0.0.1'
PORT = 65333

# проверяем данные ip, port
def check_inf(ip, port):
    try:
        ip = ip.group() if ip else HOST
        port = int(port) if port != '' else PORT
        port = port if -1 < port < 65537 else PORT
        return ip, port
    except:
        print("Что-то не так с данными")
        return False, False
# получаем данные ip, port
def inf_user():
    ip = re.search(r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$', getpass.getpass(prompt='Введите ip для подключения: '))
    port = getpass.getpass(prompt='Введите порт для подключения: ')
    ip, port = check_inf(ip, port)
    if ip != False or port!=False:
        return ip, port
    else:
        while ip == False or port == False:
            ip = re.search(r'^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$',getpass.getpass(prompt='Введите ip для подключения: '))
            port = getpass.getpass(prompt='Введите порт для подключения: ')
            ip, port = check_inf(ip, port)
            if ip != False and port != False:
                break
    return ip, port
# отправка данных
def s_send(sock, data):
    text = bytearray(f'{data}\t(Длина сообщения: {len(data)})'.encode('utf-8'))  #  массив байт
    sock.send(text)

# получение данных
def s_recv(sock):
    text = sock.recv(1024)
    if text:
        return text.decode('utf-8') # если все успешно, то декодируем данные
    else:
        return False

# запуск клиента
def main_func():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # получаем данные ip, port
        ip, port = inf_user()
        try_connect = 0
        log = False
        try:
            while try_connect < 5 and not log:
                if not log:
                    # пытаемся подсоединиться
                    try:
                        s.connect((ip, port))
                        print('Соединение успешно было установлено')
                        log = True
                    except:
                        print('Соединение не установлено, повторная попытка')
                        try_connect += 1

        except:
            print('Сервер недоступен, было сделано 5 попыток')
            exit()


        try:
            while True:
                # проверка пользователя/регистрация
                msg = s.recv(1024).decode()
                if 'check' in msg:
                    s.send(input(f'Введите пароль пользователя {msg.split()[1]}: ').encode())
                elif 'again' in msg:
                    print('Был введен несколько раз неправильный пароль, свзяь с клиентом разорвана')
                    exit()
                elif 'name' in msg:
                    s.send(input('Введите имя: ').encode())
                elif 'password' in msg:
                    s.send(input('Введите пароль: ').encode())
                else:
                    print(msg)
                    break
            while True:
                # текст для сервера
                text = str(input('Введите текст: '))
                # чтобы отключить клиента
                if text == 'exit':
                    s.send('exit'.encode())
                    break
                # кодируем текст в байты
                s_send(s, text)
                print('Отправляем данные!')
                # получаем данные от сервера и декодируем их
                data = s_recv(s)
                print('Получаем данные!')
                print(data)
        except:
            print('Соединение было утеряно')


if __name__ == '__main__':
    main_func()
