import json
import pyperclip
import time
import threading
import sys, os
import tkinter as tk
from tkinter import ttk
from tkinter import E, W, X, Y, Widget

json_open = open('region_dict.json', 'r', encoding="utf-8_sig")
json_load = json.load(json_open)


def ctrl_C():

    clip_tmp = pyperclip.paste()

    while True:
        if clip_tmp == pyperclip.paste():
            pass

        else:
            clip_tmp = pyperclip.paste()
            text_widget.configure(state='normal')
            text_widget.delete('1.0', 'end')
            count = 1.0

            for i in range(len(json_load)):
                for j in range(len(json_load[i]['names'])):

                    if clip_tmp in json_load[i]['names'][j]['name']:
                        print(json_load[i]['region'], json_load[i]['names'][j]['name'],
                            "備考："+json_load[i]['names'][j]['note'])
                        text_widget.insert('{}'.format(count), '{}\n\n'.format(json_load[i]['names'][j]['name']))
                        text_widget.insert('{}'.format(count+2.0),'部位：{}\n\n'.format(json_load[i]['region']) )
                        text_widget.insert('{}'.format(count+4.0),'備考：{}\n\n\n'.format(json_load[i]['names'][j]['note']) )

                        count += 7.0
                    
                    # else:
                    #     print(1)
                        

            text_widget.configure(state='disabled')
            # text_widget.insert('1.0', '{}'.format(clip_tmp))
    
        time.sleep(0.3)


if __name__ == '__main__':

    thread = threading.Thread(target=ctrl_C)
    thread.start()

    # rootメインウィンドウの設定
    root = tk.Tk()
    root.title("辞書アプリ")
    w = root.winfo_screenwidth()    #モニター横幅取得
    h = root.winfo_screenheight()   #モニター縦幅取得
    w1= int(w - 0.3 * w)                     #メイン画面横幅分調整
    h1 = int(h - 0.8 * h)                     #メイン画面縦幅分調整
    w2 = int(0.29*w)
    h2 = int(0.7*h)
    root.geometry(str(w2)+"x"+str(h2)+"+"+str(w1)+"+"+str(h1))    #位置設定

    # メインフレームの作成と設置
    toolbar = tk.Frame(root)
    Output = tk.Button(toolbar, text='結果メモ出力')
    Output.pack(side=tk.LEFT, padx=0, pady=0, fill=X, expand=True)
    AutoHide = tk.Button(toolbar, text='AutoHide=ON')
    AutoHide.pack(side=tk.LEFT, padx=0, pady=0, fill=X, expand=True)
    History = tk.Button(toolbar, text="検索履歴")
    History.pack(side=tk.LEFT, padx=0, pady=0, fill=X, expand=True)

    toolbar.pack(padx=0,pady=0,fill=tk.X)

    textbox = tk.Frame(root)
    textbox.columnconfigure(0, weight=1)
    textbox.rowconfigure(0, weight=1)
    text_widget = tk.Text(textbox, height=35)
    text_widget.configure(state='disabled')
    text_widget.columnconfigure(0, weight=1)
    text_widget.rowconfigure(0, weight=1)
    text_widget.grid(column=0, row=0, sticky='nsew')
    scrollbar = tk.Scrollbar(textbox, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget['yscrollcommand'] = scrollbar.set
    scrollbar.grid(column=1, row=0, sticky='ns')
    textbox.pack(padx=5, pady=10, fill=tk.Y)

    root.attributes("-topmost", True)
    root.resizable(0, 0)
    root.mainloop()
    os._exit(1)
