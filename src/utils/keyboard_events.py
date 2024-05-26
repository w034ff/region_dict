import keyboard
import tkinter.messagebox as messagebox

from utils.clipboard_utils import get_clipboard_content


# scan_codeでCtrl + Cのキーバインドを追加する
def trigger_function(e: keyboard.KeyboardEvent, app) -> None:
  # eがKeyboardEventオブジェクトで、scan_codeやnameなどの属性を持つ
  if e.scan_code == 46 and e.event_type == 'down':
    # Ctrlキーが押されているかどうかをチェック
    if keyboard.is_pressed('ctrl'):
      get_clipboard_content(app)


# キーボードのキーが押された際の処理
def bind_keyboard_events(app) -> None:
  try:
    keyboard.on_press(lambda e: trigger_function(e, app)) # scan_codeでCtrl + Cを検知する
  except Exception as e:
    print('type:' + str(type(e)))
    print('message:' + str(e))
    messagebox.showwarning("警告", "Ctrl + Cのキーバインドに失敗しました。\n詳細: " + str(e), parent=app.root)
