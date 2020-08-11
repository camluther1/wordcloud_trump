# This tool will simply convert data from the CSV format I've downloaded it in,
# into a format legible by other tools (like NLTK or the word cloud generator)

# The following code takes manually downloaded CSV data from
# http://www.trumptwitterarchive.com/archive and turns it into a text file.
# NOTE: need to automate file name generation somehow
import csv
with open("trump_8-4.csv", "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    lines = list()
    count = 0
    for line in csv_reader:
        if line['is_retweet']=="TRUE":
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
from wordcloud import WordCloud

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

# take out boring words
f = open('trump_words.txt','r')
if f.mode == 'r':
    full = f.read()
d = WordCloud().process_text(full) # wordcloud maintains its own
# list of boring words to reject with the process_text module
# print(d)

# Generate wordcloud
wordcloud = WordCloud().generate_from_frequencies(d)

# All of the following is directly copied from the wordcloud documentation here:
# https://github.com/amueller/word_cloud/blob/master/examples/simple.py
# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(max_font_size=40).generate_from_frequencies(d)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# image = wordcloud.to_image()
# image.show()
