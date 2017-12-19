# -*- coding: utf-8 -*-
import sys
print(sys.version_info)
sys.path.append('../site-packages')

import requests
import json
from bs4 import BeautifulSoup

CHANNEL = '#xxxxxxxx'
SLACK_TOKEN = 'xoxp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
FILE_API = 'https://slack.com/api/files.list'
SHARE_URL = 'https://slack.com/api/files.sharedPublicURL'
REVOKE_URL = 'https://slack.com/api/files.revokePublicURL'

# custom vision service image upload API
CUSTOM_VISION_URL = 'https://southcentralus.api.cognitive.microsoft.com/customvision/v1.0/Prediction/xxxxxxxxxxxxxxxxxxxxxxxxxx'
CUSTOM_VISION_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'

# slack
INCOMING_URL = 'https://hooks.slack.com/services/xxxxxxxxxxxxxxxxxxxxxxxxxxx'


def revoke_file_url(revoke_file_id):
    """
    対象ファイルのパブリック設定をクローズする
    :param revoke_file_id: 対象ファイルID
    :return:
    """
    requests.get(REVOKE_URL + '?token=' + SLACK_TOKEN + '&file=' + revoke_file_id + '&pretty=1')


def get_permalink_public():
    """
    パブリックなファイルURLを取得する
    :return: permalink_public
    """
    public_file_info = requests.get(SHARE_URL + '?token=' + SLACK_TOKEN + '&file=' + file_id + '&pretty=1').json()
    print(public_file_info)
    return public_file_info['file']['permalink_public']


def get_img_url(permalink_public):
    """
    画像URLの取得
    :param permalink_public: パブリック公開されたslack fileのURL
    :return: 画像URL
    """
    target_img = requests.get(permalink_public)
    img_soup = BeautifulSoup(target_img.text, 'html.parser')
    return img_soup.find('img')['src']


def image_download(image_name):
    """
    画像をローカルダウンロードする
    :param image_name:
    :return:
    """
    r = requests.get(image_url)
    f = open(image_name, 'wb', buffering=0)
    f.write(r.content)
    f.close()
    print('image downloaded!')


def execute_custom_vision(image_file):
    """
    カスタムビジョンサービスの実行
    :param image_file: 評価対象画像
    :return:
    """
    # azure_body = {
    #     'Url': target_img_url
    # }
    azure_header = {
        'Prediction-Key': CUSTOM_VISION_KEY,
        'Content-Type': 'application/octet-stream'
    }
    # return requests.post(CUSTOM_VISION_URL, headers=azure_header, data=json.dumps(azure_body)).json()
    print('azure run')
    return requests.post(CUSTOM_VISION_URL, headers=azure_header, data=image_file).json()


def create_message(azure_result):
    """
    カスタムビジョンサービス実行結果精査及びメッセージの生成
    :param azure_result:
    :return:
    """
    if azure_result['Predictions'] is None:
        return azure_result['Code']

    result_prediction = None
    for prediction in azure_result['Predictions']:
        probability = prediction['Probability']

        if probability > 0.2:
            if result_prediction is None:
                result_prediction = prediction
                continue

            if probability > result_prediction['Probability']:
                result_prediction = prediction

    if result_prediction is None:
        return 'ミッキーが見つからない・・・'
    else:
        tag_name = result_prediction['Tag']
        if tag_name == 'token':
            return 'このミッキーは' + str(result_prediction['Probability']) + '%の確率でトークン顔!!'
        else:
            return 'このミッキーは' + str(result_prediction['Probability']) + '%の確率で日本顔!!'


def post_slack(message):
    """
    slackへのポスト処理
    :param message: 送付したい
    :return:
    """
    incoming_body = {
        'text': message,
        'username': 'Mickey Face Bot',
        'icon_emoji': ':mouse:',
        'channel': CHANNEL
    }
    incoming_header = {
        'Content-Type': 'application/json'
    }
    requests.post(INCOMING_URL, headers=incoming_header, data=json.dumps(incoming_body))


# main処理スタート
# file情報取得
print('start')
file_list = requests.get(FILE_API + '?token=' + SLACK_TOKEN + '&channel=' + CHANNEL + '&count=1&types=images').json()
file_info = file_list['files'][0]
file_id = file_info['id']
file_name = file_info['title'] + file_info['filetype']

# file パブリックURLの取得
revoke_file_url(file_id)
download_url = get_permalink_public()

# azure custom vision service
image_url = get_img_url(download_url)
image_download(file_name)

image_file = open(file_name, 'rb', buffering=0)
response = execute_custom_vision(image_file.read())
image_file.close()
print(response)

# 評価結果の作成
post_message = create_message(response)
# slack通知
post_slack(post_message)

# fileパブリック設定のクローズ
revoke_file_url(file_id)

print('finish.')
