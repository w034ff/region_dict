import os
import sys
import tkinter as tk
from tkinter import ttk
from collections import deque
from functools import partial

from utils.config_loader import load_config
from utils.json_manager import load_data
from utils.gui_helpers import create_menu_button
from utils.register_window import open_register_window
from utils.setting_window import open_setting_window
from utils.clipboard_utils import get_clipboard_content
from utils.keyboard_events import bind_keyboard_events

# file PATH
CONFIG_FILE_PATH = './assets/settings.ini'
JSON_FILE_PATH = './assets/region_dict.json'
ICON_PATH = './assets/icons8-book-96.ico'


class DictionaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.stack = deque()

        self._initialize()

    def _initialize(self) -> None:
        self._set_base_paths()
        self.config, self.interval, self.front_display, self.github_url = load_config(self.ini_path, self.root)
        self.json_data = load_data(self.json_path)
        self._setup_main_window()
        self._create_menu_buttons()
        bind_keyboard_events(self)

    # jsonなどの必要なファイルのパスを設定する
    def _set_base_paths(self) -> None:
        if getattr(sys, 'frozen', False):
            # PyInstallerでパッケージ化された場合
            self.base_path = sys._MEIPASS
        else:
            # 通常のPythonスクリプトとして実行された場合
            self.base_path = os.path.dirname(__file__)

        self.json_path = os.path.join(self.base_path, JSON_FILE_PATH)
        self.icon_path = os.path.join(self.base_path, ICON_PATH)
        self.ini_path = os.path.join(self.base_path, CONFIG_FILE_PATH)


    # メインウィンドウをセットアップする
    def _setup_main_window(self) -> None:        
        w = self.root.winfo_screenwidth()     #モニター横幅取得
        h = self.root.winfo_screenheight()   # モニター縦幅取得
        w1= int(w - 0.3 * w)    # メイン画面横幅分調整
        h1 = int(h - 0.8 * h)   # メイン画面縦幅分調整

        self.root.geometry(str(int(0.29*w))+"x"+str(int(0.7*h))+"+"+str(w1)+"+"+str(h1)) # 位置設定
        self.root.iconbitmap(self.icon_path)

        # メインフレームの作成と設置
        frame = tk.Frame(self.root, bg="ghost white", height=0.8*h, width=w1)
        frame.pack_propagate(0)
        frame.pack(padx=0, pady=0)

        # メニューバーのようなフレームを作成
        self.menubar_frame = tk.Frame(frame, bg="white smoke")
        self.menubar_frame.pack(fill="x")

        # TextウィジェットとScrollbarウィジェットを追加するための新しいフレームを作成
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Textウィジェットを作成してtext_frameに追加
        self.text_widget = tk.Text(text_frame, font=("Arial", 12), state=tk.DISABLED)
        self.text_widget.grid(row=0, column=0, sticky=tk.NSEW)
        
        # Scrollbarウィジェットを作成してtext_frameに追加
        scrollbar = ttk.Scrollbar(text_frame, command=self.text_widget.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # Textウィジェットと Scrollbarウィジェットを関連付け
        self.text_widget.config(yscrollcommand=scrollbar.set)
        
        # text_frameのgridの重みを設定
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
    
    # メニューバーに４つのボタンを作成＆ボタンにクリックイベントをバインド
    def _create_menu_buttons(self) -> None:
        self.search_output = create_menu_button(self.menubar_frame, "検索結果出力")
        self.search_output.config(relief="sunken", bg="light gray")
        self.search_log = create_menu_button(self.menubar_frame, "検索履歴")
        self.register = create_menu_button(self.menubar_frame, "単語登録")
        self.setting = create_menu_button(self.menubar_frame, "設定")

        # ボタンにクリックイベントをバインド
        self.search_output.bind("<Button-1>", partial(self.on_search_click, cls=0))
        self.search_log.bind("<Button-1>", partial(self.on_search_click, cls=1))
        self.register.bind("<Button-1>", lambda event: open_register_window(self, event))
        self.setting.bind("<Button-1>", lambda event: open_setting_window(self, event))
    

    # 検索結果出力＆検索履歴ボタンが押された際の処理
    def on_search_click(self, event: tk.Event, cls: int) -> None:
        if cls == 0:
            current_text = self.search_output.cget("text")
        elif cls == 1:
            current_text = self.search_log.cget("text")
        else:
            current_text = ""

        if current_text == "検索履歴":
            self.text_widget.config(state=tk.NORMAL)    # 書き込み可能にする
            self.text_widget.delete(1.0, tk.END)    # 以前の書き込みを消去する
            # stackの内容をコピーする。
            stack_copy = self.stack.copy()
            # 検索履歴をTextウィジェットに表示
            for _ in range(len(stack_copy)):
                self.text_widget.insert(tk.END, stack_copy.pop())
            self.text_widget.config(state=tk.DISABLED)  # 書き込み不可にする
            self.search_output.config(relief="raised", bg="white smoke")
            self.search_log.config(relief="sunken", bg="light gray")
        else:
            get_clipboard_content(self, push_btn=True)


    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("アノテーション補助アプリ") # アプリ名を指定する
    app = DictionaryApp(root)
    root.mainloop()
