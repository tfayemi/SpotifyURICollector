"""
Uses various large source datasets, builds a large dataset of Spotify URIs.
"""
import time, gc, datetime, os
# from google.cloud import bigquery
from alive_progress import alive_bar
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

__author__='Toluwa Fayemi'
__copyright__='Copyright (C) Toluwa Fayemi, Riff'
__license__='GNU General Public License v3.0 '
__contact__='toluwa.fayemi@gmail.com'
__status__='production'
__version__='0.0.1'
__date__='2021/03/03'
__deprecated__=False

#IMPORTANT: Spotipy Spotify client. Needed for API calls.
spotify=spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def cleverboy(dataframe,start,finish):
    """
    This method recieves a list of -names-, creates search queries using these names,
    and uses the query results to compile and return a list of Artists and their repctive Spotify URIs.

    """
    omega=pd.DataFrame()
    timestamp=datetime.datetime.now()
    dump_truck=0
    dataframe.drop_duplicates(inplace=True)
    dataframe=dataframe[start:finish]

    with alive_bar(int(dataframe.count())) as bar:
        for name in dataframe:
        #search for the artist's name in spotify
        #TO-FIX: Should probably check here to see if there are no meaningful results from the search,
        #bump to the next iteration if so.
        #Fixed (lazinly)
            results=None
            #Retry loop; in case we get a bad response.
            for attempt in range(0,10):
                try:
                    results=spotify.search(q=name,type='artist')
                except Exception:
                    time.sleep(0.1)
                    continue
                break
            #Get the total number of results
            total=results['artists']['total']
            #use the total number of results to determine the number of pages
            if total>0:
                #use the total number of results to determine the number of pages
                pages=(total/50)
                #In my tests, I learned that after 1000 results, Spotify cuts you off and throws you a 404.
                #Classic big tech.
                #So, if the number of pages exceeds 19 (20pages x 50results/page = 1000, our limit)
                #Set the number of pages to 19. And we'll work from there.
                if pages>19:
                    pages=19
                #now, for each of the pages...
                current=0
                while(current<=pages):
                    data=None
                    page=None
                    #make another request to the spotify API...
                    #Retry loop; in case we get a bad response.
                    for attempt in range(0,10):
                        try:
                            page=spotify.search(q=name, offset=current*50, limit=50, type='artist')
                        except Exception:
                            time.sleep(0.1)
                            continue
                        break
                    #now let's get all the information from the results on the page.
                    for artist in page['artists']['items']:
                        try:
                            data=pd.DataFrame({'name': [artist['name']],
                                               'genres':[artist['genres']],
                                               'spotify_uri':[artist['uri']]
                                               })
                        except:
                            continue
                        omega=omega.append(data)
                        dump_truck+=1
                    if dump_truck>100000:
                        #TO-FIX:
                        #Dir
                        omega.to_csv('./datasets/Spotify_URI_list{}.csv'.format(timestamp),index=False,mode="a+")
                        omega=pd.DataFrame()
                        gc.collect()
                        dump_truck=0
                    current+=1
            bar()
        #TO-FIX:
        #Dir
    omega.to_csv('./datasets/Spotify_URI_list{}.csv'.format(timestamp),index=False,mode="a+")
    omega=pd.read_csv('./datasets/Spotify_URI_list{}.csv'.format(timestamp))
    omega.drop_duplicates(inplace=True)
    omega.to_csv('./datasets/final/Spotify_URI_list{}-final.csv'.format(timestamp),index=False)

def compile():
    """
    Combines multiple build-intervals into a single, large dataset.
    """
    df=pd.DataFrame()
    dir=os.fsdecode("./datasets/final/")
    for file in os.listdir(dir):
        hol=pd.read_csv('./datasets/final/'+file)
        df=df.append(hol)
    df.drop_duplicates(inplace=True)
    #Temporary.
    df.to_csv('./datasets/final/BIG_OL_DATASET.csv', index=False)

def build(start=0,finish=2000000):
    """
    This function will process your existing source datasets.

    """
    musicbrainz=pd.read_csv('./datasets/mb/artist',
                            header=None,
                            sep='\t',
                            usecols=[1,2,13])
    musicbrainz.columns = ['mbid','name','tags']
    kaggle=pd.read_csv('./datasets/lfm_kaggle/artists.csv', usecols=[0,1,3,4,5,6])
    kaggle.columns=['mbid','name', 'country_mb', 'country_lastfm', 'tags_mb','tags_lastfm']
    #First strategy; combine the large datasets, using merge
    megaSet=pd.merge(musicbrainz,kaggle,how='outer',on='mbid', suffixes=('','_lfm'))
    #Fill in empty 'name' cells.
    megaSet.loc[megaSet['name'].isnull(),'name']=megaSet['name_lfm']
    #Create a DataFrame that only contains the -names- of artsits
    # psi => search_list
    psi=megaSet['name']
    #creating THIRD dataset - contains a list of names, genres and spotify URIs compiled
    #from spotify API search results.
    #omega => names-genres-URIs dataset
    cleverboy(psi,start,finish)
