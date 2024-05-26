import tkinter as tk
from tkinter import ttk

from utils.json_manager import update_json_from_github
from utils.gui_helpers import auto_hide_check, create_sub_window, center_window
from utils.clipboard_utils import get_clipboard_content


# 設定ウィンドウを作成する関数
def open_setting_window(app, event: tk.Event) -> None:
  class CustomOptionMenu(ttk.Combobox):
    def __init__(app, master, variable, options, initial_value=None, **kwargs) -> None:
      super().__init__(master, textvariable=variable, values=options, **kwargs)
      if initial_value:
        app.set(initial_value)
      app.configure(state='readonly')
  
  # 設定ウィンドウの作成
  app.sub_window = create_sub_window(app.root, app.icon_path, title="設定", width=480, height=135)


  # 遅延時間の設定
  options = ["0.01", "0.05", "0.1", "0.2", "0.3"]
  selected_option = tk.StringVar()
  selected_option.set(str(app.interval))  # デフォルト値を設定
  option_menu_label1 = ttk.Label(app.sub_window, text="検索時、遅延させる時間 :")
  option_menu_label1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
  option_menu = CustomOptionMenu(app.sub_window, selected_option, options, initial_value=app.interval, width=5)
  option_menu.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
  option_menu_label2 = ttk.Label(app.sub_window, text="秒")
  option_menu_label2.grid(row=0, column=1, padx=60, pady=10, sticky=tk.W)
  ttk.Button(app.sub_window, text="    region_dict.jsonの更新確認    ", command=lambda: update_json_from_github(app.json_data, app.json_path, app.github_url, app.sub_window)).grid(row=0, column=2, padx=0, pady=10, sticky=tk.W)

  # AutoHideの設定
  checkbox_var = tk.BooleanVar(value=app.front_display)
  chk = ttk.Checkbutton(app.sub_window, text="メインウィンドウを最前面表示する", variable=checkbox_var)
  chk.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)

  # OKボタンが押された際の処理
  def save_setting() -> None:
    # 選択されたプルダウンメニューの項目を取得
    chosen_option = selected_option.get()
    app.interval = float(chosen_option)
    # チェックボックスの状態を取得
    is_checked = checkbox_var.get()        
    app.front_display = is_checked
    auto_hide_check(app, is_checked)

    app.config['INTERVAL_TIME'] = {
      'TIME': chosen_option
    }
    app.config['FRONT_DISPLAY'] = {
      'FRONT': is_checked
    }
    with open(app.ini_path, 'w') as configfile:
      app.config.write(configfile)    # 設定を.iniに保存
      app.sub_window.destroy()
    app.sub_window = None
    get_clipboard_content(app, push_btn=True)
  
  # OK＆キャンセルボタンの作成
  ttk.Button(app.sub_window, text="OK", command=save_setting).grid(row=2, column=2, sticky=tk.W, padx=0, pady=10)
  ttk.Button(app.sub_window, text="キャンセル", command=app.sub_window.destroy).grid(row=2, column=2, sticky=tk.W, padx=100, pady=10)
  
  center_window(app.sub_window)  # ウィンドウを中央に配置
