# -*- coding: utf-8 -*-
import argparse
import requests
import json
import pymongo
import re
import getpass
import os
from bs4 import BeautifulSoup as bs

sls = os.linesep
ans_page_error = 0
ans_topic_error = 0
topic_error = 0
# constants
database = 'zhihu'
collection = 'answers'
votes_lowerbound = 1000

# replace later
username = ''
password = ''
db = ''


def get_topics_by_page(page_num):
    global topic_error, sls
    offset = (page_num - 1) * 20
    url = 'https://www.zhihu.com/node/TopicsPlazzaListV2'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'referer': 'https://www.zhihu.com/topics',
    }
    param = '{"topic_id":1761,"offset":' + str(offset) + ',"hash_id":"f3d92bcb241e7cd4a2205cdf362eb3ed"}'
    data = {
        'method': 'next',
        'params': param
    }
    result = []
    try:
        respond = requests.post(url, headers=headers, data=data)
        topic_divs = json.loads(respond.content)['msg']
        for topic_div in topic_divs:
            topic_id = re.search(r'href="/topic/(\d+)', topic_div, re.M)
            result.append(topic_id.group(1))
    except Exception as e:
        topic_error += 1
        with open('log.txt', 'a') as log:
            log.write('===============================================================' + sls)
            log.write('Invalid respond found while getting topics ' + str(topic_id) + sls)
            log.write(str(e) + sls)
    return result

def get_topics():
    result = []
    page_num = 1;
    while True:
        print("collecting page " + str(page_num) + "\'s topics... ", end='')
        topics = get_topics_by_page(page_num)
        if not topics:
            print("empty, reached end")
            break
        result.extend(topics)
        print('done')
        page_num += 1
    return result

def get_answers_by_page(topic_id, page):
    global db, collection, votes_lowerbound
    offset = (page - 1) * 10
    url = 'https://www.zhihu.com/api/v4/topics/{}/feeds/essence?include=data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dquestion%29%5D.target.annotation_detail%2Ccomment_count%3B&limit=10&offset={}'.format(topic_id, offset)
    headers = {
        'referer': 'https://www.zhihu.com/topic/19550453/top-answers',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    content = res.content.decode('utf-8')
    res = json.loads(content, encoding='utf-8')
    stop = False
    for answer in res['data']:
        answer_type = answer['target']['type']
        if answer_type != 'answer':
            continue
        votes_count = answer['target']['voteup_count']
        if votes_count < votes_lowerbound:
            stop = True
            break
        db[collection].insert_one(answer)
        print(votes_count)

    is_end = res['paging']['is_end']
    stop = stop or is_end
    return stop

def get_answers_by_topic(topic_id, start_num=1):
    global ans_page_error, sls
    page_num = start_num
    while True:
        print("id", topic_id, "page", page_num)
        stop = False
        try:
            stop = get_answers_by_page(topic_id, page_num)
        except Exception as e:
            ans_page_error += 1
            with open('log.txt', 'a') as log:
                log.write('===============================================================' + sls)
                log.write('Error getting answers from topic id: ' + str(topic_id) + ' page ' + str(page_num) + sls)
                log.write(str(e) + sls)
            print('Failed to get answers from topic id: ' + str(topic_id) + ' page ' + str(page_num))
        if stop:
            break
        page_num += 1


def get_all_answers_from_topics(topics):
    global ans_topic_error, ans_page_error, topic_error
    total = len(topics)
    for index, id in enumerate(topics):
        print("Collecting answers from id "+ str(id) + " ", end='')
        print(index + 1, '/', total)
        try:
            get_answers_by_topic(id)
        except Exception as e:
            ans_topic_error += 1
            with open('log.txt', 'a') as log:
                log.write('===============================================================' + sls)
                log.write('Unhandled error while getting answers from topic id: ' + str(id) + sls)
                log.write(str(e) + sls)
    print("topic error:" + str(topic_error) + " answer page error: " + str(ans_page_error) + " answer topic error: " + str(ans_topic_error))
    print("Finished. saved in mongodb > "+ database +" > "+ collection)

### use this method to continue crawling if you have ended unexpectedly
def recover_from_topic_and_page(topic_id, page_num):
    topics = get_topics()
    topics = topics[topics.index(topic_id)+1:]
    print("Recovering from topic", topic_id, "page", page_num)
    get_answers_by_topic(topic_id, page_num)
    print("finished with topic", topic_id)
    print("Restarting")
    get_all_answers_from_topics(topics)

def get_answers_by_len(length=50):
    answers = db[collection].aggregate([
    {'$addFields': {'answer_len': {'$strLenCP': '$target.content'}}},
    {'$match': {'answer_len': {'$lte': length}}}
    ])
    count = 0
    for answer in answers:
        votes = answer['target']['voteup_count']
        content = answer['target']['content']
        author = answer['target']['author']['name']
        question = answer['target']['question']['title']
        content = bs(content, 'html.parser').text
        res = str(votes) + " " + question + " " + author + " " + content + " " + sls
        with open('res.txt', encoding='utf-8', mode='a') as writer:
            writer.write(res)
        count += 1
    print('done. total', count)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--crawl', help=('crawl answer >= ' + str(votes_lowerbound) +' votes on zhihu and save to mongo db'), action='store_true', dest='crawl')
    parser.add_argument('--query', help='extract answer which length is <= 50', action='store_true', dest='query')

    username = input('Enter your Mongodb username: ').strip()
    password = getpass.getpass(prompt='Enter your Mongodb password: ')
    client = pymongo.MongoClient("mongodb+srv://" + username' + ":" + password + "@dbcluster-iaoeo.mongodb.net/test?retryWrites=true&w=majority")
    db = client[database]

    args = parser.parse_args()
    if args.crawl:
        get_all_answers_from_topics(get_topics())
    if args.query:
        get_answers_by_len()
