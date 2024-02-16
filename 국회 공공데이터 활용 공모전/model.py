# ========================= 요약분석 =========================
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re

def replace_special_characters(text):
    # '~'와 ','를 제외한 모든 특수문자를 '.'으로 대체
    cleaned_text = re.sub(r'[^\w\s,~.]', '\n', text)
    return cleaned_text

def generate_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("korean"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count=1)
    
    result = ' '.join([str(sentence) for sentence in summary])
   
    return result

# ========================= ner =========================
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
def sentence(text):
    tokenizer = AutoTokenizer.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
    model = AutoModelForTokenClassification.from_pretrained("Leo97/KoELECTRA-small-v3-modu-ner")
    ner = pipeline("ner", model=model, tokenizer=tokenizer)
    ner_results = ner(text)

    li = [ner_results[i]['word'] for i in range(len(ner_results)) if (ner_results[i]['entity'][0] == 'B' and ner_results[i]['entity'] != 'B-DT' and ner_results[i]['entity'] != 'B-TI')]
    li = [i for i in li if len(i) != 1 and i != '브리' and '#' not in i and not i.isdigit()]


    return li


def historySentence(word, text):

    word_ = ',' + word
    target_word = word
    
    # Replace occurrences of the target word in the text
    text = re.sub(re.escape(word_), target_word, text)
    pattern = r'[^.]*{}[^.]*\.'.format(word)
    
    # Find all occurrences of the modified target word in the text
    matching_sentences = re.findall(pattern, text)
    # Print the matching sentences
    historyList = []
    for sentence in matching_sentences:
        historyList.append(sentence.strip())
    return '\n'.join(historyList)



# ========================= 키워드 =========================
from konlpy.tag import Hannanum 
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
def keyword(text):
    han = Hannanum()
    text=han.nouns(text)
    text = ' '.join(text)

    tfidf_ = TfidfVectorizer(ngram_range=(1,2), min_df=0.1, stop_words=['부문', '정부', '활용', '000', '제출', '제안', '디지털정부혁신', '정부혁신',
                            '디지털 서비스', '국민', '일반국민', '0000', '선정', '2차', '1차', '정부3', '서비스', '정보', '이용', '제공', '2017년', '확인',
                            '유용', '자신', '실시', '작성', '제안자', '실시 예정', '02', '예정', '제안서', '행정기관', '개정', '17', '완료', '발급', '신청',
                            '주민', '변경', '기술'])
    tfidf_matrix = tfidf_.fit_transform([text])
    feature_names = tfidf_.get_feature_names_out()
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    top_features = df_tfidf.sum().nlargest(5).index.tolist()
    df_tfidf_top = df_tfidf[top_features]

    # 데이터프레임 중요단어 + 비율
    return df_tfidf_top

# ================ 뉴스 기사 =====================
import requests 
from bs4 import BeautifulSoup
import webbrowser
def crawling(word):
    url = f'https://search.naver.com/search.naver?ssc=tab.news.all&where=news&sm=tab_jum&query={word}'
    html = requests.get(url).text
    html = BeautifulSoup(html)
    result = html.find('div', class_='news_contents').find('a', class_='news_tit')['href']

    return result

