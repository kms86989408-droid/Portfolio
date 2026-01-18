from flask import Flask, render_template, jsonify, request

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client.portfolio_db

linkmemo_col = db["linkmemo_memos"]
linkmemo_col.create_index("url", unique=True) # URL 중복 방지 인덱스 생성

# --------------MainPages--------------
@app.route('/')
def home():
    return render_template('index.html')

# --------------LinkMemoPages--------------
@app.route('/linkmemo')
def linkmemo():
    return render_template('linkmemo.html')

# --------------MovieStarPages--------------
@app.route('/moviestar')
def moviestar():
    return render_template('moviestar.html')

# --------------LinkMemo API--------------
@app.route('/linkmemo/memo', methods=['POST'])
def saving():
		# 1. 클라이언트로부터 데이터를 받기
        url_receive = request.form['url_give'] #클라이언트에서 url 받는 부분
        comment_receive = request.form['comment_give']
		# 2. meta tag를 스크래핑하기
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
        data = requests.get(url_receive, headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')

        og_image = soup.select_one('meta[property="og:image"]')
        og_title = soup.select_one('meta[property="og:title"]')
        og_description = soup.select_one('meta[property="og:description"]')

        article = {'url': url_receive, 
                    'title': og_title['content'] if og_title else 'No title', 
                    'desc': og_description['content'] if og_description else 'No description',
                    'image': og_image['content'] if og_image else 'No image',
                    'comment': comment_receive}
        
		# 3. mongoDB에 데이터 넣기
        try:
            linkmemo_col.insert_one(article)
            return jsonify({'result': 'success', 'msg': '저장 완료!'})
        except DuplicateKeyError:
            return jsonify({'result': 'fail', 'msg': '이미 저장된 URL입니다.'})
        
@app.route('/linkmemo/memo', methods=['GET'])
def read_articles():
    # 1. mongoDB에서 _id 값을 제외한 모든 데이터 조회해오기 (Read)
    result = list(linkmemo_col.find({}, {'_id': 0}))
    # 2. articles라는 키 값으로 article 정보 보내주기
    return jsonify({'result': 'success', 'articles': result})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
