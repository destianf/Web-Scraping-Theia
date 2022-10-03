from tkinter import Y
from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-list'})

table1 = table.find_all('div', attrs={'class':'lister-item mode-advanced'})

row_length = len(table1)

temp = [] #initiating a list 

imdb_rating = table.find_all('div', attrs={'class':"ratings-bar"})

for i in range(0, row_length):
	
    #get movie_title
    movie_title = table.find_all("h3", attrs = {"class":"lister-item-header"})[i]
    movie_title = movie_title.find('a').text
    movie_title = movie_title.strip()

    ## get movie rating
    movie_rating = imdb_rating[i].find('div', attrs ={'class':"inline-block ratings-imdb-rating"}).text
    movie_rating = movie_rating.strip()
    
    ## get metascore
    movie_metascore = imdb_rating[i].find('div', attrs={'class':"inline-block ratings-metascore"})
    meta_score = 0
    
    if movie_metascore is not None:
        meta_score = movie_metascore.find('span', attrs={'class': "metascore"}).text.strip()

	#get votes
    votes = table.find_all('meta', attrs = {'itemprop':'ratingCount'})[i]['content']
#insert the scrapping process here
    
    temp.append((movie_title,movie_rating,meta_score,votes))
temp

temp = temp[::-1]

#change into dataframed
imdb = pd.DataFrame(temp, columns = ('movie_title','movie_rating','meta_score','votes'))

#insert data wrangling here
imdb['movie_title'] = imdb['movie_title'].astype('category')
imdb['movie_rating'] = imdb['movie_rating'].astype('float64')
imdb['meta_score'] = imdb['meta_score'].astype('int64')
imdb['votes'] = imdb['votes'].astype('int64')

imdb.dtypes

imdb = imdb.set_index('movie_title')

based_movie_rating = imdb.reset_index().sort_values('movie_rating', ascending = False)\
                [['movie_title','movie_rating']]
based_movie_rating.head(7)

based_movie_rating = imdb.sort_values(by = "movie_rating", ascending = False).head(7)
based_movie_rating.reset_index().plot.bar(x='movie_title', y='movie_rating')

based_votes = imdb.reset_index().sort_values('votes', ascending = False)\
                [['movie_title','votes']]
based_votes.head(7)

based_votes = imdb.sort_values(by = "votes", ascending = False).head(7)
based_votes.reset_index().plot.barh(x='movie_title', y='votes')

Based_metascore = imdb.reset_index().sort_values('meta_score', ascending = False)\
                [['movie_title','meta_score']]
Based_metascore.head(7)

based_metascore = imdb.sort_values(by = "meta_score", ascending = False).head(7)
based_metascore.reset_index().plot.bar(x='movie_title', y='meta_score')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = imdb.sort_values(by = "votes", ascending = False).head(7)
	card_data.reset_index().plot.barh(x='movie_title', y='votes')

	# generate plot
	ax = card_data.plot.barh(figsize = (10,5)) 

	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)