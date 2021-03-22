# SpotifyURICollector
A python dataset builder that uses the Spotipy API library and publicly available lists to build a large table of Spotify Artists, their genres, and their unique Spotify URIs.

## How It Works

Quite simply, the build() method combines public datasets from music dataAPIs (musicbrainz, lastFM, etc), creates a list of "names" from these datasets and penultimately performs search calls to the Spotify API with each name as the search query. The Spotify API only allows a few thousand results per search query so the code collects the name, genres and URIs for each search result and saves it to a pandas dataframe. Lastly, it saves the completed dataset to a csv file with a timestamp to a directory within the ./datasets/final directory contained in the package file. If this folder goes missing for some reason, it'll simply create a new one.

## How To Use:

In terminal (or cmd line), navigate to the folder containing the "builder.py" file. Start python. It would be best to use Python 3.6+. In the python interpreter, import the build method from the builder file (as a module). 

`python3`

`from builder import build`

the build() method takes two parameters: a starting index and an ending index. With the default datasets included in this repository, there are approximately 1.7 million names to search through. This would take forever. Instead, you can compile the dataset incrementally by passing a range of indexes to search through. 

### Example:

`build(100000,200000)`

For reference, parsing through 100,000 entries takes anywhere from 8 to 10 hours. I'm sure it could be faster, but that'll have to wait until I'm a better programmer! 
