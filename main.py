import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime
import ollama
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

st.title('Google Scholar論文検索アプリ')

# キーワード入力
keyword = st.text_input('検索キーワードを入力してください')

# オプション設定
col1, col2 = st.columns(2)
current_year = datetime.now().year

with col1:
    sort_by = st.selectbox('ソート方法', ['Citations', 'cit/year'])
    start_year = st.number_input('開始年', min_value=1900, max_value=2100, value=current_year - 2)

with col2:
    num_results = st.number_input('検索結果数', min_value=10, max_value=1000, value=20, step=10)
    end_year = st.number_input('終了年', min_value=1900, max_value=2100, value=current_year)

translate_option = st.checkbox('タイトルを日本語翻訳する')

# セッション変数の初期化
if 'searching' not in st.session_state:
    st.session_state['searching'] = False
if 'translated_texts' not in st.session_state:
    st.session_state['translated_texts'] = []

# 非同期翻訳関数
async def translate(text, model='aya:8b'):
    """
    ollamaライブラリを用いて英語→日本語翻訳を行う非同期関数。
    実運用ではエラー処理などを加味することを推奨。
    """
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"Please translate this text from English to Japanese and respond with only the translated text.\nText:{text}"
            }
        ],
        options={"cache": False}
    ))
    translated_text = response["message"]["content"]
    return translated_text

async def translate_and_update(df, df_placeholder):
    """
    DataFrameを1行ずつ翻訳し、その都度表示を更新する。
    """
    for i, row in df.iterrows():
        original_title = row['Title']
        # 非同期翻訳
        translated_text = await translate(original_title)

        # DataFrame更新
        df.at[i, 'タイトルの日本語訳'] = translated_text

        # 部分的にセッションステートに保存したければこちら
        st.session_state['translated_texts'][i] = translated_text

        # DataFrameを再描画
        df_placeholder.write(df)
        # 更新タイミングを作るため、少し待機（無くても可）
        await asyncio.sleep(0.1)

# メインの検索ボタン
if st.button('検索', disabled=st.session_state['searching']):
    st.session_state['searching'] = True
    st.session_state['translated_texts'] = [None] * num_results

    with st.spinner('検索中...'):
        if keyword:
            # sort-google-scholarコマンドの実行
            command = [
                'sortgs', keyword,
                '--sortby', sort_by,
                '--nresults', str(num_results),
                '--startyear', str(start_year),
                '--endyear', str(end_year)
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                # CSVファイルの読み込み
                csv_file = f"{keyword.replace(' ', '_')}.csv"
                if os.path.exists(csv_file):
                    df = pd.read_csv(csv_file)
                    df.drop(columns=['Rank'], inplace=True, errors='ignore')

                    if translate_option:
                        # まず翻訳前のDataFrameを表示
                        # 翻訳結果を格納する新しい列を作成しておく
                        df['タイトルの日本語訳'] = None

                        # 列の表示順序を調整（タイトル→タイトルの日本語訳→その他→著者）
                        cols = df.columns.tolist()
                        if 'Title' in cols and 'タイトルの日本語訳' in cols and 'Author' in cols:
                            new_cols = ['Title', 'タイトルの日本語訳'] + \
                                       [c for c in cols if c not in ['Title', 'タイトルの日本語訳', 'Author']] + \
                                       ['Author']
                            df = df[new_cols]

                        df_placeholder = st.empty()
                        df_placeholder.write(df)

                        # 非同期でタイトル翻訳して随時更新
                        start_time = time.time()
                        asyncio.run(translate_and_update(df, df_placeholder))
                        end_time = time.time()

                        st.write(f"翻訳にかかった時間: {end_time - start_time:.2f}秒")

                        st.write("最終的な翻訳済みDataFrame:")
                        st.dataframe(df)

                    else:
                        # 翻訳オプションを使わない場合はそのまま表示
                        st.dataframe(df)

                    # 表示後にCSVを削除
                    os.remove(csv_file)
                else:
                    st.error('検索結果が見つかりませんでした。')
            else:
                st.error('検索中にエラーが発生しました。')
        else:
            st.warning('キーワードを入力してください。')
    st.session_state['searching'] = False
