from flask import Flask, render_template, request, url_for, redirect
import os
import model

app = Flask(__name__)
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# ====================== api로 데이터 불러오기 =========================
# ====================== 공문서 추출 함수 ======================

from datetime import datetime
import requests
import json
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

def searchNews(date, title=' ') :
    from urllib import parse

    try:
        title = parse.unquote(title)
        url = f'https://apis.data.go.kr/1741000/publicDoc/getDocPress?serviceKey=s4fsUzU59XOwt6T4L7gT%2BxUVP6nr67R95E1C0hzjmpqEg5xNZdFdsqSb%2Fdm6KFXvpLGkY4xK%2FR9hBC5z6A4Ujg%3D%3D&numOfRows=100&pageNo=1&format=json&title={title}&date={date}&manager=%EA%B3%BC'
        response = requests.get(url)
        contents = response.text    

        json_ob = json.loads(contents)
        body = json_ob['response']['body']['resultList']
        df = pd.json_normalize(body)
        
        df.reset_index(drop=True, inplace=True)
        df['data.text'] = df['data.text'].apply(lambda x: BeautifulSoup(x).text)
        df.sort_values(by='meta.date', ascending=False,inplace=True)

    except Exception :
        df = '해당 기간 데이터는 존재하지 않습니다.'
    
    return df

# =================================================================================================

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/main.html')
def main_page():
    return render_template('main.html')

@app.route('/sub.html', methods=['GET', 'POST'])
def sub_page():
    if request.method == 'POST':
        date_input = request.form.get('date_input')
        keyword_input = request.form.get('keyword_input')

        # Process the form data as needed, e.g., pass it to the searchNews function
        result = searchNews(date_input, keyword_input)
        print(result)
        # Pass the dataframe to the template
        return render_template('sub.html', date_input = date_input, keyword_input=keyword_input, result=result)
    else:
        return render_template('sub.html')

# ================= 공문서 선택 목록 화면 =======================
@app.route("/submit",methods=["POST"])
def receive_submit():
    _date_input = request.form.get("date_input")
    _keyword_input = request.form.get("keyword_input")
    
    result = searchNews(_date_input, _keyword_input)
    result = result[['meta.title','data.text']]
    import json

    from urllib import parse
    
    _list=[]    
    for x in result.iloc:
        _meta_title = x['meta.title']
        _data_text =  parse.quote(x['data.text'])
        _list.append([_meta_title,_data_text])

    print(_list)

    return render_template('DoCument.html', date_input = _date_input, keyword_input=_keyword_input, result=_list)    

# ========================== 요약 분석 ==========================
@app.route("/summary.html")
def iframe1():
    
    from urllib import parse
    encrypted_vart = request.args.get("title")
    decrypted_vart = parse.unquote(encrypted_vart)

    encrypted_var = request.args.get("text")
    decrypted_var = parse.unquote(encrypted_var)

    result = model.generate_summary(model.replace_special_characters(decrypted_var))

    print(result)
        
    return render_template('summary.html', title=decrypted_vart, result= result, original=decrypted_var)

# ========================== 키워드 ==========================
@app.route("/keyword.html")
def iframe2():
    from urllib import parse
    encrypted_vart = request.args.get("title")
    decrypted_vart = parse.unquote(encrypted_vart)


    encrypted_var = request.args.get("text")
    decrypted_var = parse.unquote(encrypted_var)

    result = model.keyword(decrypted_var) 
    print(result)

    return render_template('keyword.html',title=decrypted_vart, result= result.columns.tolist(), original=decrypted_var, image=None)

# ========================== ner ==========================
@app.route("/ner_tagging.html")
def iframe3():
    from urllib import parse
    encrypted_vart = parse.quote(request.args.get("title"))
    decrypted_vart = parse.unquote(encrypted_vart)


    encrypted_var = parse.quote(request.args.get("text"))
    decrypted_var = parse.unquote(encrypted_var)

    result1 = model.sentence(decrypted_var)

    
    
    keyword = request.args.get("keyword")
    keyword_result=None
    if(keyword!=None):
        print("처리 : " , keyword +"함...")
        result2 = model.historySentence(keyword, decrypted_var)
        print(result2)
        keyword_result=result2

    return render_template('ner_tagging.html',
                           title=decrypted_vart, 
                           etitle = encrypted_vart,
                           etext= encrypted_var,
                           keyword_result= keyword_result,
                             keywords = result1)

# ========================== 뉴스 추천 =================================
@app.route("/news_recommend.html")
def iframe4():
    from urllib import parse

    encrypted_var = parse.quote(request.args.get("text"))
    decrypted_var = parse.unquote(encrypted_var)

    result1 = model.sentence(decrypted_var)


    return render_template('news_recommend.html', result= result1)


@app.route("/getlink")
def getlinkframe():
    keyword = request.args.get("keyword")
    _link = model.crawling(keyword)

    return "<script> location.href='" + str(_link) + "'</script>"

# ==================== 서비스 4개 선택 화면 ===========================
@app.route("/document_result.html")
def result1():

    from urllib import parse
    title = parse.quote(request.args.get("title",None))
    text = parse.quote(request.args.get("text",None))
    
    
    return render_template('document_result.html', result_data="가나다",text = text,title = title)

if __name__ == '__main__':
    app.run(port=5005, debug=True)