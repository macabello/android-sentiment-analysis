# Deploy as aws lambda, runs periodically:
# Upload to s3 bucket ccdd-lambda-code/android-app-sentiment
# Parse google android reviews.
# Filter them by date.
# Group comments for app version and sent them to aws comprehend to retrieve sentiment.
# Sent report to microsoft teams.
# Packed following as: https://dev.to/razcodes/how-to-create-a-lambda-using-python-with-dependencies-4846
from google_play_scraper import reviews_all
import requests
import json
import datetime
import boto3
import os
import pymsteams
 

 
client = boto3.client('comprehend')
APP_VERSION_FIELD = 'reviewCreatedVersion'
CONTENT_FIELD = 'content'
AT_FIELD = 'at'
SCORE_FIELD = 'score'
SENTIMENT_FIELD = 'Sentiment'
APP_PACKAGE = 'com.verisure.securitasdirect.owa'
 
def get_reviews(lang, days_back_review):
 date_to_last_reviews = datetime.datetime.now() - datetime.timedelta(days_back_review) 
 result = reviews_all(
     APP_PACKAGE,
     lang=lang
 )
 return [review for review in result if (date_to_last_reviews < review[AT_FIELD])]
 
def get_version_grouped_comments(reviews):
 grouped_reviews = {}
 for review in reviews:
   if review[APP_VERSION_FIELD] not in grouped_reviews:
     grouped_reviews[review[APP_VERSION_FIELD]] = []       
  
   grouped_reviews[review[APP_VERSION_FIELD]].append(review[CONTENT_FIELD])
 return grouped_reviews
 
 
def retrieve_comment_sentiment(lang, comment):
  ####for test local 
  #import random
  #sentiment_list = ('NEUTRAL','POSITIVE','NEGATIVE','MIXED')
  #return (random.choice(sentiment_list))

  return client.detect_sentiment(
     Text=comment,
     LanguageCode=lang
     )[SENTIMENT_FIELD]

def retrieve_medium_score(reviews):
 sum = 0
 num_reviews = 0
 for review in reviews:
   num_reviews += 1
   sum += review[SCORE_FIELD]
 
 return sum/num_reviews
 
def format_sentiments_result(sentiments_result):
 format = ''
 concatenate = ' and '
 for sentiment, ocurrences in sentiments_result.items():
   format += str(ocurrences) + ' times ' + sentiment + concatenate
 return format[:-len(concatenate)]


def send_message_to_teams(lang,days,num_last_reviews,medium_score,versions,url):
  myTeamsMessage = pymsteams.connectorcard(url)
  myTeamsMessage.title("Google Play Sentiment , Language: " + lang)

  if medium_score is not None:
    myTeamsMessage.text("Medium Score: " + str(medium_score) + 
                    ". " + str(num_last_reviews) + 
                    " reviews in the last " + days + " days")
    if medium_score < 3.4: 
        if medium_score < 2:
            myTeamsMessage.color("#FF0000")
        else:
            myTeamsMessage.color("#FFFF00")
    else:
        myTeamsMessage.color("#00FF00")
      #create sections by version
    i = 0
    for version,resume in versions.items():
      Section = "Section" + str(i)
      Section = pymsteams.cardsection()
      if version is None:
        Section.addFact("Version", "Not Available")
      else:
        Section.addFact("Version", version)
      Section.addFact("Resume", resume)
      myTeamsMessage.addSection(Section)
      i += 1
  else:
    myTeamsMessage.text("No reviews in the last " + days + " days")

  myTeamsMessage.send()


def lambda_handler(event, context):
  print(event)
  lang = event['LANG']
  days_back_review = int(os.environ['DAYS_BACK_REVIEW'])
  microsoft_teams_url = os.environ['MICROSOFT_TEAMS_URL']

 
  last_reviews = get_reviews(lang, days_back_review)
  num_last_reviews = len(last_reviews)
  if (num_last_reviews > 0):
    medium_score = retrieve_medium_score(last_reviews)

    grouped_reviews = get_version_grouped_comments(last_reviews)
    dict_versions = {}
    for version, comments in grouped_reviews.items():
      print (comments)
      sentiment_ocurrences = {}
      for comment in comments:
        sentiment = retrieve_comment_sentiment(lang, comment)
        sentiment_ocurrences[sentiment] = sentiment_ocurrences.get(sentiment, 0) + 1
      dict_versions[version] = format_sentiments_result(sentiment_ocurrences)
  else:
    medium_score = None
    dict_versions = None
  send_message_to_teams(lang,str(days_back_review),num_last_reviews,medium_score,dict_versions,microsoft_teams_url)