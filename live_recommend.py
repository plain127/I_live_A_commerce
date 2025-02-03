import os
import urllib.request
import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
    
load_dotenv
client_id = os.getenv('NAVER_API_CLIENT_ID')
client_secret = os.getenv('NAVER_API_CLIENT_SECRET')

def get_search_url(search_txt, start_pg, disp_num):
    base = 'https://openapi.naver.com/v1/search/shop.json'
    query = '?query=' + urllib.parse.quote(search_txt)
    start = f'&start={start_pg}'
    disp = f'&display={disp_num}'
    url = base + query + disp + start    
    return url 

def get_search_result(url):
    request = urllib.request.Request(url)
    request.add_header('X-Naver-Client-Id', client_id)
    request.add_header('X-Naver-Client-Secret', client_secret)
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))

def delete_tag(input_str):
    input_str = input_str.replace('<b>', '')
    input_str = input_str.replace('</b>', '')
    input_str = input_str.replace('\xa0', '')
    return input_str

def get_frame(json_data):
    title = [delete_tag(each['title']) for each in json_data['items']]
    lprice = [each['lprice'] for each in json_data['items']]
    link = [each['link'] for each in json_data['items']]
    mall_name = [each['mallName'] for each in json_data['items']]
    product_type = [each['productType'] for each in json_data['items']]
    brand = [each['brand'] for each in json_data['items']]
    category1 = [each['category1'] for each in json_data['items']]
    category2 = [each['category2'] for each in json_data['items']]
    category3 = [each['category3'] for each in json_data['items']]
    category4 = [each['category4'] for each in json_data['items']]
       
    df = pd.DataFrame({
        'title':title,
        'lprice':lprice,
        'link':link,
        'mall':mall_name,
        'category':product_type,
        'brand':brand,
        'category1':category1,
        'category2':category2,
        'category3':category3,
        'category4':category4,        
    }, columns=['title', 'lprice', 'link', 'mall', 'brand', 'category', 'category1', 'category2', 'category3', 'category4'])
    
    return df

def recommend(category, channel_num, entire_topic, detail_topic):
    df = pd.DataFrame({}, columns=['title', 'lprice', 'link', 'mall', 'brand', 'category', 'category1', 'category2', 'category3', 'category4']) 
    for idx in range(1,100):
        url = get_search_url(entire_topic, idx, 100)
        json_data = get_search_result(url)
        try_df = get_frame(json_data)
        df = pd.concat([df, try_df])
    
    
    df['lprice'] = df['lprice'].astype(int)
    comparison = df['title'] + ' ' + df['mall'] + ' ' + df['brand'] + ' ' + df['category'] + ' ' + df['category1'] + ' ' + df['category2'] + ' ' + df['category3'] + ' ' + df['category4']
    vector = CountVectorizer()
    matrix =  vector.fit_transform(comparison)

    for_user = vector.transform([detail_topic])
    
    similarity_scores = cosine_similarity(for_user, matrix).flatten()
    
    df['similarity'] = similarity_scores
    recommendations = df.sort_values(by='similarity', ascending=False)
    
    file_path = f'DB/{category}_{channel_num}/recommend_file.csv'
    
    recommendations.to_csv(file_path,index=False, encoding='utf-8-sig')