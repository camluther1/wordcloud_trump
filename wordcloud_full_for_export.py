import json
import urllib.request, urllib.parse, urllib.error
import ssl
import datetime
import dateutil
from pytz import timezone
import pytz
import pandas as pd
import time
import sys
import os

# Set file directory
os.chdir(os.path.dirname(sys.argv[0]))

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("Retrieving https://www.thetrumparchive.com/latest-tweets")
data = urllib.request.urlopen("https://www.thetrumparchive.com/latest-tweets", context=ctx).read()

info = json.loads(data)
print('User count:', len(info))

columns = set()
allowed_types = [str, int, bool]
tweets_data = []
eastern = timezone('US/Eastern')
now = eastern.localize(datetime.datetime.now())
start_delta = datetime.timedelta(weeks=1)
last_week = now - start_delta
# print(last_week)

for tweet in info:
    # print(tweet)
    tweet_time = dateutil.parser.isoparse(tweet['date'])
    # Is tweet older than 1 wk?
    # print(tweet_time)
    if tweet_time < last_week: #minus a week
        break #this method won't work if tweets aren't arranged by date...
        # which they are..
    else:
        single_tweet_data = {}
        keys = tweet.keys()
        for k in keys:
            try:
                v_type = type(tweet[k])
            except:
                v_type = None
            if v_type != None:
                if v_type in allowed_types:
                    single_tweet_data[k] = tweet[k]
                    columns.add(k)
        tweets_data.append(single_tweet_data)


header_cols = list(columns)

# print(header_cols)
# print(tweets_data)

now_secs = time.time()
df = pd.DataFrame(tweets_data, columns=header_cols)
current_date_time = time.strftime('%Y_%m_%d_%H_%M',time.gmtime(now_secs))
csv_title = ('/archive_exports/archive_export' + current_date_time + '.csv')
df.to_csv(csv_title)

# ------------------------------------------------------------------------------
#  BEGIN ANALYSIS
# ------------------------------------------------------------------------------

# The following code takes downloaded CSV data from
# http://www.trumptwitterarchive.com/archive and turns it into a text file.
import csv

with open(csv_title, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    lines = list()
    count = 0
    for line in csv_reader:
        if line['isRetweet']=="TRUE":
            continue
        else:
            lines.append(line['text'])
            count +=1

## This code simply prints all tweets along with a count
# for line in lines:
#     print(line)
# print(count, 'original tweets found')

# Now to build code that simplifies text inputs and writes it to a txt file
# (because txt is preferred input for wordcloud)
import string
import re

d = dict() #dict is for storing final word counts
f = open('trump_words.txt','w+')
for line in lines:
    # Edit out tags
    line = re.sub('@\S+',"",line)
    # Edit out ampersands
    line = re.sub('&\S+',"",line)
    # Edit out links
    line = re.sub('https://\S+',"",line)

    # Edit out any leftover retweets
    if re.findall('^RT', line) != []:
        continue

    # Edit out unicode quotation marks
    line = line.replace('\u201d','')
    line = line.replace('\u201c','')


    # make text generally parsible
    line = line.lower()
    line = line.strip()
    line = line.translate(line.maketrans("","",string.punctuation))
    line = line.translate(line.maketrans("","",string.digits))
    line = line + '\r\n'
    f.write(line)
    # print(line)
f.close()

import numpy as np
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
from os import path

# take out boring words
f = open('trump_words.txt','r')
if f.mode == 'r':
    full = f.read()
d = WordCloud().process_text(full) # wordcloud maintains its own
# list of boring words to reject with the process_text module
# print(d)

# get data directory (using getcwd() is needed to support running example in generated IPython notebook)
dir = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

# Adding Color
trump_coloring = np.array(Image.open(path.join(dir, "trump_yell_3.png")))

# Erasing inexplicable "wa" result
stopwords = set(STOPWORDS)
stopwords.add("was")
stopwords.add("wa")

# Generate wordcloud
wordcloud = WordCloud(background_color = 'white',stopwords=stopwords, mask = trump_coloring,max_words=400,repeat = True)

wordcloud.generate_from_frequencies(d)

image_colors = ImageColorGenerator(trump_coloring)

# Generating image with MatPlotLib
import matplotlib.pyplot as plt

# Trying something here - layer image with the WordCloud
# make these smaller to increase the resolution
dx, dy = 0.05, 0.05

x = np.arange(-3.0, 3.0, dx)
y = np.arange(-3.0, 3.0, dy)
X, Y = np.meshgrid(x, y)

extent = np.min(x), np.max(x), np.min(y), np.max(y)
fig = plt.figure(frameon=False)

# recolor wordcloud and show
# plt.figure()
plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
plt.imshow(trump_coloring, cmap=plt.cm.gray, alpha=.5,interpolation="bilinear")
plt.axis("off")
# plt.show()

now_secs = time.time()
current_date_time = time.strftime('%Y_%m_%d_%H_%M',time.gmtime(now_secs))
filename = 'test_img/trump_wordcloud_' + current_date_time + '.png'
plt.savefig(filename, dpi=1000)
