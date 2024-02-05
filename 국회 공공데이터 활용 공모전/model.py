
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
    li = [i for i in li if len(i) != 1]
    li = ['브리핑' if i == '브리' else i for i in li  ]
    li = set(li)

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
def trend(text):
    han = Hannanum()
    text=han.nouns(text)
    text = ' '.join(text)

    tfidf_ = TfidfVectorizer(ngram_range=(1,2), min_df=0.1, stop_words=['100','우리','국민','국민들','여러분','기술','참석','기념','발전','오늘','지속','추진','통해','가까이','격려','문제','생각','여러분들','고민','26',
                                                                        '또한','계획','공유','답변','지난','정부','제2회','지능형','제안','자리','기관','혁신','참여','다양한','출범','각종','이용','지역','나','시나리오',
                                                                       '청사','개소','디지털','2년','4차','각국','과정','구현','2022년','2021년','2020년','2023년','19','2020','2021','2022','2023','그동안','국가','부처',
                                                                       '정부혁신제안','정부혁신','사례들','의원님','위원님','역할','11','대한민국','계기','정부세종','20','2005년','감사','수상자','전자정부','한국','관계',
                                                                       '사례','100년','24','50년'])
    tfidf_matrix = tfidf_.fit_transform([text])
    feature_names = tfidf_.get_feature_names_out()
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    top_features = df_tfidf.sum().nlargest(4).index.tolist()
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

