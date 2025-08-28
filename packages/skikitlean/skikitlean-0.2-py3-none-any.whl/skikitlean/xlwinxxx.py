from ftplib import FTP
import io
import os
import sys
from pathlib import Path
import time



def check_ftp_for_new_files(ftp, last_files):
    current_files = set(ftp.nlst())
    new_files = current_files.difference(last_files)
    return new_files


def get():
    ftp = FTP('hvostoew.beget.tech')
    ftp.login(user='hvostoew_hvostov', passwd='Qwerty123321!')
    ftp.encoding = 'utf-8'

    downloads_path = str(Path.home() / "Downloads")
    last_files = set(ftp.nlst())

    while True:
        method = input("Выберите метод (write или read): ")

        if method.lower() == "write":
            upload_choice = input("Вы хотите загрузить файл с компьютера на FTP сервер? (да/нет): ")

            if upload_choice.lower() == "да":
                local_file_path = input("Введите путь к локальному файлу: ")
                filename = os.path.basename(local_file_path)
                remote_file_path = f'/{filename}'

                if os.path.isfile(local_file_path):
                    with open(local_file_path, 'rb') as local_file:
                        ftp.storbinary(f'STOR {remote_file_path}', local_file)
                        print(f"Файл {filename} успешно загружен в корневой каталог FTP сервера")
                else:
                    print(f"Файл {local_file_path} не найден.")
            else:
                filename = input("Введите имя для нового файла (с расширением): ")
                remote_file_path = f'/{filename}'
                print("Введите текст для сохранения на FTP сервер. Для окончания ввода нажмите Enter на пустой строке.")
                data = ''
                line = input()
                while line:
                    data += line + '\n'
                    line = input()

                data_ftp = io.BytesIO(data.encode())
                ftp.storbinary(f'STOR {remote_file_path}', data_ftp)
                print(f"Файл {filename} успешно создан в корневом каталоге FTP сервера")
        elif method.lower() == "read":
            files = ftp.nlst()
            print("Список файлов на FTP сервере:")
            for idx, file in enumerate(files):
                print(f"{idx + 1}. {file}")
            choice = int(input("Выберите файл для чтения (введите номер): "))
            if 1 <= choice <= len(files):
                filename = files[choice - 1]
                data = bytearray()

                def write_data(buf):
                    data.extend(buf)

                try:
                    ftp.retrbinary(f"RETR {filename}", write_data)
                    content = data.decode('utf-8')
                    print(f"Содержимое файла {filename}:")
                    print(content)
                    print(f"Файл {filename} успешно скачан с FTP сервера")

                    local_save_path = os.path.join(downloads_path, filename)
                    with open(local_save_path, 'wb') as local_file:
                        local_file.write(data)
                    print(f"Файл {filename} успешно сохранён на локальный компьютер по пути {local_save_path}")

                    

                except Exception as e:
                    print(f"Ошибка при скачивании файла: {e}")
            else:
                print("Неверный выбор файла.")
        else:
            print("Неверный метод. Пожалуйста, выберите write или read.")

        time.sleep(5)
        new_files = check_ftp_for_new_files(ftp, last_files)
        if new_files:
            print(f"Новые файлы на FTP сервере: {', '.join(new_files)}")
            last_files.update(new_files)

            

    ftp.quit()


get()
input("Press Enter to exit...")
