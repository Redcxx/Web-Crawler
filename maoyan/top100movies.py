import requests, re, os, sys, time

# sys.stdout.reconfigure(encoding='utf-8') # fix unicode error when use '>' in powershell

sls = os.linesep

def get_page(page_num):
  global sls
  offset = (page_num - 1) * 10
  url='https://maoyan.com/board/4?offset=' + str(offset)
  headers={
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
  }
  respond = requests.get(url, headers=headers)
  if respond.status_code == 200:
    return respond.text
  else:
    with open('log.txt', 'a') as log:
      log.write('Error while getting page from: ' + url + sls)
    return None

def get_data_by_page(html):
  global sls
  result = []
  if html:
    datas = re.findall('<p class="name"><a.*?title=.*?>(.*?)</a>.*?<p class="star">(.*?)</p>.*?<p class="releasetime">(.*?)</p>.*?<p class="score">(.*?)</p>', html, re.S)
    for data in datas:
      data = list(data)
      data[3] = re.sub('</i>|<i class=".*?">', '', data[3])
      result.append([data[0], data[1].strip(), data[2].strip(), data[3]])
    return result
  else:
    with open('log.txt', 'a') as log:
      log.write('Received None in get_data_by_page, skipped' + sls)
    return None

def get_all_movies():
  movie_num = 0
  for page_num in range(1,11): # from 1 to 10 inclusive, 10 movies per page
    datas = get_data_by_page(get_page(page_num))
    if datas:
      for movie in datas:
        title = movie[0]
        actors = movie[1]
        release_time = movie[2]
        rating = movie[3]
        movie_num += 1
        print(movie_num, title, actors, release_time, '评分：' + str(rating))
    else:
      with open('log.txt', 'a') as log:
        log.write('Failed to get movies from page' + page_num + sls)
    time.sleep(1) # dont make request too fast
  print('done')

if __name__ =='__main__':
  get_all_movies()
