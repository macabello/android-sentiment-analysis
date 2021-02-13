
# Deploy as aws lambda, runs periodically:
# Upload to s3 bucket ccdd-lambda-code/android-app-sentiment
# Parse google android reviews.
# Filter them by date.
# Group comments for app version and sent them to aws comprehend to retrieve sentiment.
# Sent report to microsoft teams.
# Packed following as: https://dev.to/razcodes/how-to-create-a-lambda-using-python-with-dependencies-4846
from google_play_scraper import reviews_all
import json 
import datetime
import boto3
import os


client = boto3.client('comprehend')
LANG = os.environ['LANG']
DAYS_BACK_REVIEW = int(os.environ['DAYS_BACK_REVIEW'])
MICROSOFT_TEAMS_URL = os.environ['MICROSOFT_TEAMS_URL']
DATE_TO_LAST_REVIEWS = datetime.datetime.now() - datetime.timedelta(DAYS_BACK_REVIEW)
APP_VERSION_FIELD = 'reviewCreatedVersion'
CONTENT_FIELD = 'content'
AT_FIELD = 'at'
SCORE_FIELD = 'score'
SENTIMENT_FIELD = 'Sentiment'
APP_PACKAGE = '<to_be_included>'

def get_reviews():
  result = reviews_all(
      APP_PACKAGE,
      lang=LANG
  )
  return [review for review in result if (DATE_TO_LAST_REVIEWS < review[AT_FIELD])]

#last_comments = [review[CONTENT_FIELD] for review in last_reviews]

def get_version_grouped_comments(reviews):
  grouped_reviews = {}
  for review in reviews:
    if review[APP_VERSION_FIELD] not in grouped_reviews:
      grouped_reviews[review[APP_VERSION_FIELD]] = []        
    
    grouped_reviews[review[APP_VERSION_FIELD]].append(review[CONTENT_FIELD])
  return grouped_reviews


def retrieve_comment_sentiment(comment):
  return client.detect_sentiment(
      Text=comment,
      LanguageCode=LANG
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

def lambda_handler(event, context):
  last_reviews = get_reviews()
  num_last_reviews = len(last_reviews)
  mmessage_initial = 'Android, lang ' + LANG + ',sentiment report for the last ' + str(DAYS_BACK_REVIEW) + ' days'
  message = mmessage_initial + '. No reviews'
  if (num_last_reviews > 0):
    medium_score = retrieve_medium_score(last_reviews)
    message = mmessage_initial + ' with a total of ' + str(num_last_reviews) + ' reviews and a medium score of ' + str(medium_score) + '.\n'
    
    grouped_reviews = get_version_grouped_comments(last_reviews)
    for version, comments in grouped_reviews.items():
      print(comments)
      sentiment_ocurrences = {}
      for comment in comments:
        sentiment = retrieve_comment_sentiment(comment)
        #print(sentiment)
        sentiment_ocurrences[sentiment] = sentiment_ocurrences.get(sentiment, 0) + 1
      #print(sentiment_ocurrences)  
      message += ' Version: ' + str(version) + ' with a total of ' + format_sentiments_result(sentiment_ocurrences) + '.'
  print(message)   
