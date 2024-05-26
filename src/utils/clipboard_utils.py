import time
import tkinter as tk
from tkinter import messagebox


"""
クリップボードの内容を基にjsonから辞書検索する関数
"""
# クリップボードの内容で辞書検索する関数
def get_clipboard_content(app, push_btn: bool=False) -> None:
  app.search_log.config(relief="raised", bg="white smoke")
  app.search_output.config(relief="sunken", bg="light gray")
  app.text_widget.config(state=tk.NORMAL)  # 書き込み可能にする
  app.text_widget.delete(1.0, tk.END)    # 以前の書き込みを消去する
  time.sleep(app.interval)   # 遅延の追加
  flag = 0
  try:
    content = app.root.clipboard_get() # クリップボードの内容を取得
    for item in app.json_data:
      for name_entry in item['names']:
        if content in name_entry['name']:  
          output = "\n該当する単語: "+ name_entry['name']+"    部位: "+ item['region'] +"    備考: "+name_entry['note']+"\n"
          app.text_widget.insert(tk.END, output)
          flag += 1

          # 検索結果出力ボタンを押すと、Ctrl+C以外の方法で単語がstackに追加される現象を防ぐ処理
          if not push_btn:
            app.stack.append(output)
    # 辞書に単語が無かった場合
    if flag < 1:
      app.text_widget.insert(tk.END, "\n該当する単語は辞書にありませんでした。")
    else:
      # 検索結果出力ボタンを押すと、Ctrl+C以外の方法で単語がstackに追加される現象を防ぐ処理
      if not push_btn:
        app.stack.append("\n----------検索履歴----------\n")
    app.text_widget.config(state=tk.DISABLED)  # 書き込み不可にする

  # クリップボードにテキストがない場合
  except tk.TclError:
    pass
  
  except Exception as e:
    print('type:' + str(type(e)))
    print('message:' + str(e))
    messagebox.showerror("エラー", "エラーが発生しました。\n詳細: " + str(e), parent=app.root)
    pass
