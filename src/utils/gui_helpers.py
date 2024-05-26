import tkinter as tk


# メニューバーに配置するボタンを作成
def create_menu_button(parent: tk.Frame, label: str) -> tk.Menubutton:
  menu_button = tk.Menubutton(parent, text=label, relief="raised", bg="white smoke")
  menu_button.pack(fill=tk.X, expand=True, side="left")
  return menu_button

 # AutoHideについての関数
def auto_hide_check(app, check: bool) -> None:
  # ウィンドウの表示方法（最前面）についての設定
  app.root.attributes('-topmost', not check)
  app.root.update()
  app.root.attributes('-topmost', check)


"""
辞書に登録するウィンドウと設定ウィンドウを作成する際に、必要な関数
"""
# 単語検索＆設定ウィンドウを作成する関数
def create_sub_window(root: tk.Tk, icon_path: str, title: str, width: int, height: int) -> tk.Toplevel:
  sub_window = tk.Toplevel(root)
  sub_window.title(title)
  sub_window.iconbitmap(icon_path)
  # ウィンドウをモーダルに設定
  sub_window.grab_set()
  # ウィンドウを最前面に表示する
  sub_window.attributes('-topmost', True)
  # ウィンドウの最大サイズを制限する
  sub_window.minsize(width, height)
  sub_window.maxsize(width, height)
  return sub_window

# 単語検索＆設定ウィンドウを画面中央少し上に配置する関数
def center_window(win: tk.Toplevel) -> None:
  win.update_idletasks()
  width = win.winfo_width()
  height = win.winfo_height()
  x = (win.winfo_screenwidth() // 2) - (width // 2)
  y = (win.winfo_screenheight() // 4) - (height // 2)
  win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
