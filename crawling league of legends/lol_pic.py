import requests
import json
import re
import urllib.request
import os

sls = os.linesep
# constants
headers =  {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}
folder = 'lol_champs_pics'

def get_champs_names():
  global headers
  url='https://ddragon.leagueoflegends.com/cdn/9.12.1/data/en_AU/champion.json'
  res = requests.get(url, headers=headers)
  res = json.loads(res.content)
  return [champ for champ in res['data']]

def get_all_pics_from_champ(champ_name):
    global headers, folder, sls
    print('loading', champ_name, 'skins')
    url = 'https://ddragon.leagueoflegends.com/cdn/9.12.1/data/en_AU/champion/{}.json'.format(champ_name)
    res = requests.get(url, headers=headers)
    res = json.loads(res.content)
    champ_skins_data = res['data'][champ_name]['skins']
    for data in champ_skins_data:
      # can get skin id from here but no way to use it
      skin_name = data['name']
      skin_num = data['num']
      pic_url = 'https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{}_{}.jpg'.format(champ_name, skin_num)
      skin_name = skin_name.replace('/', '') # replace for K/DA skins
      if skin_num == 0:
          skin_file = folder + '/' + skin_name + ' ' + champ_name + '.jpg'
      else:
          skin_file = folder + '/' + skin_name + '.jpg'
      try:
          urllib.request.urlretrieve(pic_url, skin_file)
      except Exception as e:
          print("Error while attemp to retrieve", skin_name, 'from', pic_url)
          with open('lol_pics_log.txt', 'a') as log:
              log.write('=============================================================' + sls)
              log.write("Error while attemp to retrieve " + skin_name + ' from ' + pic_url + '' + sls)
              log.write('=============================================================' + sls)
              log.write(str(e) + sls)
          print(skin_file, 'NOT SAVED')
      else:
          print(skin_file, 'saved')

def get_all_champs_pics(champ_names=get_champs_names()):
    total = len(champ_names)
    for index, champ_name in enumerate(champ_names):
        print('current champion', champ_name, str(index) + '/' + str(total))
        get_all_pics_from_champ(champ_name)
    urllib.request.urlcleanup()
    print('Finished')

def recover_from_champ(champ_name):
    print('Recovering from:', champ_name)
    champ_names = get_champs_names()
    champ_names = champ_names[champ_names.index(champ_name):]
    get_all_champs_pics(champ_names)

if __name__ == '__main__':
    get_all_champs_pics()
