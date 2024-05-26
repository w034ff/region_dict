import json
import tkinter as tk
import tkinter.messagebox as messagebox
import requests


# ローカルのJSONデータの読み込み
def load_data(json_path: str) -> dict:
  with open(json_path, 'r', encoding="utf-8_sig") as f:
    return json.load(f)

  
"""
jsonをリモート先から更新 & 新しくjsonに単語を登録
"""
# 単語を辞書（json）に登録する関数
def save_data_to_json(json_data: dict, json_path: str, word: str, class_name: str, note: str) -> None:
  # 入力データを適切な構造に整形し、該当する"region"が既存のJSONデータに存在するか確認する
  region_exists = False
  for entry in json_data:
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
    json_data.append(new_entry)

  # 変更したJSONデータをファイルに保存する
  with open(json_path, 'w', encoding="utf-8_sig") as f:
    json.dump(json_data, f, indent=4, ensure_ascii=False)


# 辞書（json）をリモート先（GitHub上）から更新する関数
def update_json_from_github(json_data: dict, json_path: str, github_url: str, parent_window: tk.Toplevel) -> None:
  try:
    # GitHubからのJSONデータの取得
    response = requests.get(github_url)
    response.raise_for_status() # HTTPエラーをチェック
    # UTF-8 with BOMエンコーディングを使用してJSONデータを読み込む
    remote_data = response.content.decode('utf-8_sig')
    remote_json = json.loads(remote_data)

    updated = False # 更新が行われたかどうかを追跡
    # 差分の確認とマージ
    for g_item in remote_json:
      # 同じregionのエントリをjson_dataから見つける
      j_item = next((item for item in json_data if item["region"] == g_item["region"]), None)

      # もし同じregionのエントリがjson_dataに存在しない場合、エントリ全体を追加
      if not j_item:
        json_data.append(g_item)
        updated = True
      else:
        # 同じregionのエントリが存在する場合、namesリスト内の各nameをチェック
        for g_name in g_item["names"]:
          if g_name not in j_item["names"]:
            j_item["names"].append(g_name)
            updated = True

     # 更新されたデータの保存
    if updated:
      with open(json_path, 'w', encoding="utf-8_sig") as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
      messagebox.showinfo("成功", "更新に成功しました", parent=parent_window)
    else:
      messagebox.showinfo("成功", "更新は必要ありません", parent=parent_window)
  except Exception as e:
    print("Error:", e)
    messagebox.showerror("失敗", "更新に失敗しました\n詳細: " + str(e), parent=parent_window)
