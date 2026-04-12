import winreg
import os


def find_programs():
    # Пути в реестре, где Windows хранит данные об установках
    registry_locations = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    found_apps = {}

    for root, path in registry_locations:
        try:
            with winreg.OpenKey(root, path) as key:
                # Исправлено: берем 0-й элемент кортежа (количество подразделов)
                subkeys_count = winreg.QueryInfoKey(key)[0]

                for i in range(subkeys_count):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            # Извлекаем имя программы
                            try:
                                name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            except:
                                continue

                            # Ищем путь к исполняемому файлу (DisplayIcon — самый точный источник EXE)
                            path_exe = ""
                            try:
                                raw_path, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                                # Очищаем путь от индекса иконки (например, ",0") и лишних кавычек
                                path_exe = str(raw_path).split(',')[0].strip('"')
                            except:
                                # Если DisplayIcon нет, пробуем InstallLocation
                                try:
                                    path_exe, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                except:
                                    continue

                            # Добавляем в список, если путь похож на правду
                            if path_exe:
                                found_apps[name] = path_exe

                    except:
                        continue
        except OSError:
            continue

    return found_apps
