import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime
import ollama

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

plot_results = st.checkbox('結果をプロットする')
translate_option = st.checkbox('タイトルを日本語翻訳する')

if 'searching' not in st.session_state:
    st.session_state['searching'] = False

if st.button('検索', disabled=st.session_state['searching']):
    st.session_state['searching'] = True
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
                    if translate_option:

                        def translate_with_elyza(text):
                            response  = ollama.chat(model='aya:8b', messages=[
                                {
                                    "role": "user",
                                    "content": f"Please translate this text from English to Japanese and respond with only the translated text.\nText:{text}"
                                }
                            ])
                            return response["message"]["content"]

                        df['タイトルの日本語訳'] = df['Title'].apply(translate_with_elyza)

                    st.dataframe(df)
                    os.remove(csv_file)  # 表示後に削除

                else:
                    st.error('検索結果が見つかりませんでした。')
                    
            else:
                st.error('検索中にエラーが発生しました。')
        else:
            st.warning('キーワードを入力してください。')
    st.session_state['searching'] = False
