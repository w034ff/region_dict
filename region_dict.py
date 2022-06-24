import json
from tkinter.font import names
import tkinter as tk
from tkinter import ttk

json_open = open('region_dict.json', 'r', encoding="utf-8_sig")
json_load = json.load(json_open)

# rootメインウィンドウの設定
root = tk.Tk()
root.title("辞書アプリ")
w = root.winfo_screenwidth()    #モニター横幅取得
h = root.winfo_screenheight()   #モニター縦幅取得
print(h)
w1= int(w - 0.3 * w)                     #メイン画面横幅分調整
h1 = int(h - 0.8 * h)                     #メイン画面縦幅分調整
print(h1)
root.geometry(str(int(0.29*w))+"x"+str(int(0.7*h))+"+"+str(w1)+"+"+str(h1))    #位置設定

# メインフレームの作成と設置
frame = tk.Frame(root)
frame.pack(padx=20,pady=10)



# print(json_load[0]['names'][1]['name'])
# print(type(json_load[0]))

# for i in json_load:
#     print(i)

for i in range(len(json_load)):
    for j in range(len(json_load[i]) - 1):
        # print(json_load[i]['names'][j]['name'])

        if json_load[i]['names'][j]['name'] == '貧血':
            print(json_load[i]['region'], json_load[i]['names'][j]['name'],
                "備考："+json_load[i]['names'][j]['note'])

root.mainloop()