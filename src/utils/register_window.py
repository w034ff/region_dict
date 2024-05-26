import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox

from utils.json_manager import save_data_to_json
from utils.gui_helpers import create_sub_window, center_window
from utils.clipboard_utils import get_clipboard_content


# 辞書に登録するウィンドウを作成する関数
def open_register_window(app, event: tk.Event) -> None:
  # 単語探索ウィンドウを作成する
  app.sub_window = create_sub_window(app.root, app.icon_path, title="単語登録", width=500, height=300)

  # 単語の入力
  ttk.Label(app.sub_window, text="辞書に登録する単語名 :").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
  word_entry = ttk.Entry(app.sub_window, width=40)
  word_entry.grid(row=0, column=0, padx=140, pady=5, sticky=tk.W)

  # クラスの選択 (チェックボックス)
  ttk.Label(app.sub_window, text="クラス:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
  # 保存するクラスの選択状態を持つ変数を作成
  classes = ["全身", "頭部", "頭頚部", "胸部", "腹部", "その他"]
  class_vars = {cls: tk.BooleanVar(value=False) for cls in classes}
  num = 1
  for cls, var in class_vars.items():
    num += 1
    ttk.Checkbutton(app.sub_window, text=cls, variable=var).grid(row=num, column=0, sticky=tk.W, padx=40)

  # 備考の入力
  ttk.Label(app.sub_window, text="備考 :").grid(row=8, column=0, sticky=tk.W, padx=10, pady=15)
  note_text = ttk.Entry(app.sub_window, width=70)
  note_text.grid(row=8, column=0, padx=50, pady=15, sticky=tk.W)

  # 保存ボタンが押された際の処理
  def save_data() -> None:
    word = word_entry.get().replace("\n", "").replace("\t", "").replace(" ", "")  # 単語名のテキストを取得
    note = note_text.get().replace("\n", "").replace("\t", "").replace(" ", "")  # 備考のテキストを取得
    # 選択されているクラスを取得
    selected_classes = [cls for cls, var in class_vars.items() if var.get()]

    if not word:
      messagebox.showwarning("警告", "単語名が入力されていません。", parent=app.sub_window)
      return        
    if not selected_classes:
      messagebox.showwarning("警告", "クラスが選択されていません。", parent=app.sub_window)
      return
    if not note:
      note = "なし"

    # 複数クラスが選択された際に、それらのクラスを＆記号を用いて１つのクラスにする
    class_name = selected_classes[0]
    if len(selected_classes) > 1:
      class_name = "&".join(selected_classes)

    save_data_to_json(app.json_data, app.json_path, word, class_name, note)   # 単語を辞書に登録

    app.sub_window.destroy()
    app.sub_window = None
    get_clipboard_content(app, push_btn=True)

  # 保存＆キャンセルボタンの作成
  ttk.Button(app.sub_window, text="保存", command=save_data).grid(row=9, column=0, sticky=tk.E, padx=150, pady=10)
  ttk.Button(app.sub_window, text="キャンセル", command=app.sub_window.destroy).grid(row=9, column=0, sticky=tk.E, padx=50, pady=10)

  center_window(app.sub_window)  # ウィンドウを中央に配置
