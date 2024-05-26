import configparser
import tkinter as tk
import tkinter.messagebox as messagebox


# 設定ファイルの読み込み
def load_config(ini_path: str, root: tk.Tk) -> tuple[configparser.ConfigParser, float, bool, str]:
  try:
    # configparser インスタンスの作成
    config = configparser.ConfigParser()
    config.read(ini_path)
    interval = config.getfloat('INTERVAL_TIME', 'time')
    front_display = config.getboolean('FRONT_DISPLAY', 'front', fallback=False)
    url = config['GITHUB_URL'].get('url')
    root.attributes('-topmost', front_display)
    return config, interval, front_display, url
  except Exception as e:
    print("Error:", e)
    messagebox.showwarning("警告", "settings.iniの読み込みに失敗しました。\n詳細: " + str(e), parent=root)
    root.attributes('-topmost', True)
    default_config = configparser.ConfigParser()
    return default_config, 0.1, True, ""
