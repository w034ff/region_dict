"""
ダブルクォーテーションで囲まれている部分を変更すれば、別の辞書アプリにすることができる
"""
import json
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import time
from collections import deque
from functools import partial
import configparser
import sys
import os

import requests
import keyboard

# Constants and Configurations
CONFIG_FILE_PATH = 'settings.ini'
JSON_FILE_PATH = 'region_dict.json'
ICON_PATH = 'icons8-book-96.ico'


class DictionaryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.interval = 0.1
        self.front_display = True
        self.stack = deque()

        self._initialize()

    def _initialize(self) -> None:
        self._set_base_paths()
        self._load_config()
        self._load_data()
        self._setup_main_window()
        self._create_menu_buttons()
        self._bind_keyboard_events()

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

    # 設定ファイルの読み込み
    def _load_config(self) -> None:
        try:
            config = configparser.ConfigParser()
            config.read(self.ini_path)
            self.interval = config.getfloat('INTERVAL_TIME', 'time')
            self.front_display = config['FRONT_DISPLAY'].get('front')
            self.root.attributes('-topmost', self.front_display)

        except Exception as e:
            print("Error:", e)
            messagebox.showwarning("警告", "settings.iniの読み込みに失敗しました。\n詳細: " + str(e), parent=self.root)
            self.root.attributes('-topmost', True)
            pass

    # ローカルのJSONデータの読み込み
    def _load_data(self) -> None:
        with open(self.json_path, 'r', encoding="utf-8_sig") as f:
            self.json_data = json.load(f)

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
        self.search_output = self.create_menu_button(self.menubar_frame, "検索結果出力")
        self.search_output.config(relief="sunken", bg="light gray")
        self.search_log = self.create_menu_button(self.menubar_frame, "検索履歴")
        self.register = self.create_menu_button(self.menubar_frame, "単語登録")
        self.setting = self.create_menu_button(self.menubar_frame, "設定")

        # ボタンにクリックイベントをバインド
        self.search_output.bind("<Button-1>", partial(self.on_search_click, cls=0))
        self.search_log.bind("<Button-1>", partial(self.on_search_click, cls=1))
        self.register.bind("<Button-1>", self.open_register_window)
        self.setting.bind("<Button-1>", self.open_setting_window)
    
    # メニューバーに配置するボタンを作成
    def create_menu_button(self, parent: tk.Frame, label: str) -> tk.Menubutton:
        menu_button = tk.Menubutton(parent, text=label, relief="raised", bg="white smoke")
        menu_button.pack(fill=tk.X, expand=True, side="left") 
        return menu_button
    

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
            self.get_clipboard_content(push_btn=True)


    """
    辞書に登録するウィンドウと設定ウィンドウを作成する際に、必要な関数
    """
    # 単語検索＆設定ウィンドウを作成する関数
    def create_sub_window(self, title: str, width: int, height: int) -> tk.Toplevel:
        sub_window = tk.Toplevel(self.root)
        sub_window.title(title)
        sub_window.iconbitmap(self.icon_path)
        # ウィンドウをモーダルに設定
        sub_window.grab_set()
        # ウィンドウを最前面に表示する
        sub_window.attributes('-topmost', True)
        # ウィンドウの最大サイズを制限する
        sub_window.minsize(width, height)
        sub_window.maxsize(width, height)

        return sub_window

    # 単語検索＆設定ウィンドウを画面中央少し上に配置する関数
    def center_window(self, win: tk.Toplevel) -> None:
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 4) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # AutoHideについての関数
    def auto_hide_check(self, check: bool) -> None:
        # ウィンドウの表示方法（最前面）についての設定
        self.root.attributes('-topmost', not check)
        self.root.update()
        self.root.attributes('-topmost', check)

    """
    jsonをリモート先から更新 & 新しくjsonに単語を登録
    """
    # 単語を辞書（json）に登録する関数
    def save_data_to_json(self, word: str, class_name: str, note: str) -> None:
        # 入力データを適切な構造に整形し、該当する"region"が既存のJSONデータに存在するか確認する
        region_exists = False
        for entry in self.json_data:
            if entry['region'] == class_name:
                region_exists = True
                # 既存の"region"が存在する場合、その"names"リストに新しいデータを追加する
                entry['names'].append({"name": word, "note": note})
                break
        
        # 既存の"region"が存在しない場合、新しい"region"としてデータを追加する
        if not region_exists:
            new_entry = {
                "region": class_name,
                "names": [{"name": word, "note": note}]
            }
            self.json_data.append(new_entry)
        # 変更したJSONデータをファイルに保存する
        with open(self.json_path, 'w', encoding="utf-8_sig") as f:
            json.dump(self.json_data, f, indent=4, ensure_ascii=False)

    # 辞書（json）をリモート先（GitHub上）から更新する関数
    def update_json_from_github(self, github_url: str) -> None:
        try:
            # GitHubからのJSONデータの取得
            response = requests.get(github_url)
            github_data = response.json()

            updated = False  # 更新が行われたかどうかを追跡
            # 差分の確認とマージ
            for g_item in github_data:
                # 同じregionのエントリをjson_dataから見つける
                j_item = next((item for item in self.json_data if item["region"] == g_item["region"]), None)

                # もし同じregionのエントリがjson_dataに存在しない場合、エントリ全体を追加
                if not j_item:
                    self.json_data.append(g_item)
                    updated = True
                else:
                    # 同じregionのエントリが存在する場合、namesリスト内の各nameをチェック
                    for g_name in g_item["names"]:
                        if g_name not in j_item["names"]:
                            j_item["names"].append(g_name)
                            updated = True

            # 更新されたデータの保存
            if updated:
                with open(self.json_path, 'w', encoding="utf-8_sig") as f:
                    json.dump(self.json_data, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("成功", "更新に成功しました", parent=self.sub_window)
            else:
                messagebox.showinfo("成功", "更新は必要ありません", parent=self.sub_window)
        except Exception as e:
            print("Error:", e)
            messagebox.showerror("失敗", "更新に失敗しました\n詳細: " + str(e), parent=self.sub_window)
            pass
    

    """
    辞書に登録するウィンドウと設定ウィンドウを作成する関数
    """
    # 単語を辞書に登録するウィンドウを作成する関数
    def open_register_window(self, event: tk.Event) -> None:
        # 単語探索ウィンドウを作成する
        self.sub_window = self.create_sub_window(title="単語登録", width=500, height=300)

        # 単語の入力
        ttk.Label(self.sub_window, text="辞書に登録する単語名 :").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        word_entry = ttk.Entry(self.sub_window, width=40)
        word_entry.grid(row=0, column=0, padx=140, pady=5, sticky=tk.W)

        # クラスの選択 (チェックボックス)
        ttk.Label(self.sub_window, text="クラス:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        # 保存するクラスの選択状態を持つ変数を作成
        classes = ["全身", "頭部", "頭頚部", "胸部", "腹部", "その他"]
        class_vars = {cls: tk.BooleanVar(value=False) for cls in classes}
        num = 1
        for cls, var in class_vars.items():
            num += 1
            ttk.Checkbutton(self.sub_window, text=cls, variable=var).grid(row=num, column=0, sticky=tk.W, padx=40)

        # 備考の入力
        ttk.Label(self.sub_window, text="備考 :").grid(row=8, column=0, sticky=tk.W, padx=10, pady=15)
        note_text = ttk.Entry(self.sub_window, width=70)
        note_text.grid(row=8, column=0, padx=50, pady=15, sticky=tk.W)

        # 保存ボタンが押された際の処理
        def save_data() -> None:
            word = word_entry.get().replace("\n", "").replace("\t", "").replace(" ", "")  # 単語名のテキストを取得
            note = note_text.get().replace("\n", "").replace("\t", "").replace(" ", "")  # 備考のテキストを取得
            # 選択されているクラスを取得
            selected_classes = [cls for cls, var in class_vars.items() if var.get()]
            
            if not word:
                messagebox.showwarning("警告", "単語名が入力されていません。", parent=self.sub_window)
                return        
            if not selected_classes:
                messagebox.showwarning("警告", "クラスが選択されていません。", parent=self.sub_window)
                return
            if not note:
                note = "なし"

            # 複数クラスが選択された際に、それらのクラスを＆記号を用いて１つのクラスにする
            class_name = selected_classes[0]
            if len(selected_classes) == 1:
                pass
            else:
                for i in range(1, len(selected_classes)):
                    class_name += "&"+ selected_classes[i]
            self.save_data_to_json(word, class_name, note)   # 単語を辞書に登録
            
            self.sub_window.destroy()
            self.sub_window = None
            self.get_clipboard_content(push_btn=True)
        
        # 保存＆キャンセルボタンの作成
        ttk.Button(self.sub_window, text="保存", command=save_data).grid(row=9, column=0, sticky=tk.E, padx=150, pady=10)
        ttk.Button(self.sub_window, text="キャンセル", command=self.sub_window.destroy).grid(row=9, column=0, sticky=tk.E, padx=50, pady=10)
        
        self.center_window(self.sub_window)  # ウィンドウを中央に配置

    # 設定ウィンドウを作成する関数
    def open_setting_window(self, event: tk.Event) -> None:
        class CustomOptionMenu(ttk.Combobox):
            def __init__(self, master, variable, options, initial_value=None, **kwargs) -> None:
                super().__init__(master, textvariable=variable, values=options, **kwargs)
                if initial_value:
                    self.set(initial_value)
                self.configure(state='readonly')
        
        # 設定ウィンドウの作成
        self.sub_window = self.create_sub_window(title="設定", width=480, height=135)

        # configparser インスタンスの作成
        config = configparser.ConfigParser()
        config.read(self.ini_path)
        self.interval = config.getfloat('INTERVAL_TIME', 'time')
        self.front_display = config.getboolean('FRONT_DISPLAY', 'front', fallback=False)
        url = config['GITHUB_URL'].get('url')

        # 遅延時間の設定
        options = ["0.01", "0.05", "0.1", "0.2", "0.3"]
        selected_option = tk.StringVar()
        selected_option.set(str(self.interval))  # デフォルト値を設定
        option_menu_label1 = ttk.Label(self.sub_window, text="検索時、遅延させる時間 :")
        option_menu_label1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        option_menu = CustomOptionMenu(self.sub_window, selected_option, options, initial_value=self.interval, width=5)
        option_menu.grid(row=0, column=1, padx=0, pady=10, sticky=tk.W)
        option_menu_label2 = ttk.Label(self.sub_window, text="秒")
        option_menu_label2.grid(row=0, column=1, padx=60, pady=10, sticky=tk.W)
        ttk.Button(self.sub_window, text="    region_dict.jsonの更新確認    ", command=lambda: self.update_json_from_github(url)).grid(row=0, column=2, padx=0, pady=10, sticky=tk.W)

        # AutoHideの設定
        checkbox_var = tk.BooleanVar(value=self.front_display)
        chk = ttk.Checkbutton(self.sub_window, text="メインウィンドウを最前面表示する", variable=checkbox_var)
        chk.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)

        # OKボタンが押された際の処理
        def save_setting() -> None:
            # 選択されたプルダウンメニューの項目を取得
            chosen_option = selected_option.get()
            self.interval = float(chosen_option)
            # チェックボックスの状態を取得
            is_checked = checkbox_var.get()        
            self.front_display = is_checked
            self.auto_hide_check(is_checked)

            config['INTERVAL_TIME'] = {
                'TIME': chosen_option
            }
            config['FRONT_DISPLAY'] = {
                'FRONT': is_checked
            }
            with open(self.ini_path, 'w') as configfile:
                config.write(configfile)    # 設定を.iniに保存
                self.sub_window.destroy()
            self.sub_window = None
            self.get_clipboard_content(push_btn=True)
        
        # OK＆キャンセルボタンの作成
        ttk.Button(self.sub_window, text="OK", command=save_setting).grid(row=2, column=2, sticky=tk.W, padx=0, pady=10)
        ttk.Button(self.sub_window, text="キャンセル", command=self.sub_window.destroy).grid(row=2, column=2, sticky=tk.W, padx=100, pady=10)
        
        self.center_window(self.sub_window)  # ウィンドウを中央に配置


    """
    クリップボードの内容でjsonから辞書検索する関数
    """
    # クリップボードの内容で辞書検索する関数
    def get_clipboard_content(self, push_btn: bool=False) -> None:
        self.search_log.config(relief="raised", bg="white smoke")
        self.search_output.config(relief="sunken", bg="light gray")
        self.text_widget.config(state=tk.NORMAL)  # 書き込み可能にする
        self.text_widget.delete(1.0, tk.END)    # 以前の書き込みを消去する
        time.sleep(self.interval)   # 遅延の追加
        flag = 0
        try:
            content = self.root.clipboard_get() # クリップボードの内容を取得
            for item in self.json_data:
                for name_entry in item['names']:
                    if content in name_entry['name']:  
                        output = "\n該当する単語: "+ name_entry['name']+"    部位: "+ item['region'] +"    備考: "+name_entry['note']+"\n"
                        self.text_widget.insert(tk.END, output)
                        flag += 1

                        # 検索結果出力ボタンを押すと、Ctrl+C以外の方法で単語がstackに追加される現象を防ぐ処理
                        if not push_btn:
                            self.stack.append(output)
            # 辞書に単語が無かった場合
            if flag < 1:
                self.text_widget.insert(tk.END, "\n該当する単語は辞書にありませんでした。")
            else:
                # 検索結果出力ボタンを押すと、Ctrl+C以外の方法で単語がstackに追加される現象を防ぐ処理
                if not push_btn:
                    self.stack.append("\n----------検索履歴----------\n")
            self.text_widget.config(state=tk.DISABLED)  # 書き込み不可にする

        # クリップボードにテキストがない場合
        except tk.TclError:
            pass
        
        except Exception as e:
            print('type:' + str(type(e)))
            print('message:' + str(e))
            messagebox.showerror("エラー", "エラーが発生しました。\n詳細: " + str(e), parent=self.root)
            pass


    # scan_codeでCtrl + Cのキーバインドを追加する
    def trigger_function(self, e: keyboard.KeyboardEvent) -> None:
        # eがKeyboardEventオブジェクトで、scan_codeやnameなどの属性を持つ
        if e.scan_code == 46 and e.event_type == 'down':
            # Ctrlキーが押されているかどうかをチェック
            if keyboard.is_pressed('ctrl'):
                self.get_clipboard_content()
    
    # キーボードのキーが押された際の処理
    def _bind_keyboard_events(self) -> None:
        try:
            keyboard.on_press(self.trigger_function)    # scan_codeでCtrl + Cを検知する
        except Exception as e:
            print('type:' + str(type(e)))
            print('message:' + str(e))
            messagebox.showwarning("警告", "Ctrl + Cのキーバインドに失敗しました。\n詳細: " + str(e), parent=self.root)

    def run(self) -> None:
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("アノテーション補助アプリ") # アプリ名を指定する
    app = DictionaryApp(root)
    root.mainloop()