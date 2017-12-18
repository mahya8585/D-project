# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup

CHANNEL = '#CHANNEL'
SLACK_TOKEN = 'xoxp-xxxxxxxxxxxxxxxxxxxxxxx'
FILE_API = 'https://slack.com/api/files.list'
SHARE_URL = 'https://slack.com/api/files.sharedPublicURL'
REVOKE_URL = 'https://slack.com/api/files.revokePublicURL'

# custom vision service image URL API
CUSTOM_VISION_URL = 'https://southcentralus.api.cognitive.microsoft.com/customvision/v1.0/Prediction/xxxxxxxxxxxxxxxxx/url?iterationId=xxxxxxxxxxxxxxxxxx3'
CUSTOM_VISION_KEY = 'xxxxxxxxxxxxxxxx'

# slack
INCOMING_URL = 'https://hooks.slack.com/services/xxxxxxxxxxxxxxxxxxxx'


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
    return public_file_info['file']['permalink_public']


def get_img_url(permalink_public):
    """
    画像URLの取得
    :param permalink_public: パブリック公開されたslack fileのURL
    :return: 画像URL
    """
    target_img = requests.get(permalink_public, stream=True)
    img_soup = BeautifulSoup(target_img.text, 'html.parser')
    return img_soup.find('img')['src']


def execute_custom_vision(target_img_url):
    """
    カスタムビジョンサービスの実行
    :param target_img_url: 評価対象画像URL
    :return:
    """
    azure_body = {
        'Url': target_img_url
    }
    azure_header = {
        'Prediction-Key': CUSTOM_VISION_KEY,
        'Content-Type': 'application/json'
    }
    return requests.post(CUSTOM_VISION_URL, headers=azure_header, data=json.dumps(azure_body)).json()


def create_message(azure_result):
    """
    カスタムビジョンサービス実行結果精査及びメッセージの生成
    :param azure_result:
    :return:
    """
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
file_list = requests.get(FILE_API + '?token=' + SLACK_TOKEN + '&channel=' + CHANNEL + '&count=1&types=images').json()
file_info = file_list['files'][0]
file_id = file_info['id']
title = file_info['title']
file_type = file_info['filetype']

# file パブリックURLの取得
revoke_file_url(file_id)
download_url = get_permalink_public()

# azure custom vision service
response = execute_custom_vision(get_img_url())

# 評価結果の作成
# slack通知
post_slack(create_message(response))

# fileパブリック設定のクローズ
revoke_file_url(file_id)
