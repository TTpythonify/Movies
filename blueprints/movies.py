import asyncio
import requests
from flask import Blueprint, render_template, request

movies_bp = Blueprint('movies_bp', __name__)

@movies_bp.route('/', methods=['POST', 'GET'])
async def index():
    image = ""
    error_message = ""
    details = {}

    if request.method.lower() == 'post':
        # Get user's prompt
        movie_name = request.form.get('movie_name')

        # Get the current event loop
        loop = asyncio.get_event_loop()

        # Run the functions asynchronously in separate threads
        image_task = loop.run_in_executor(None, search_for_movie, movie_name)
        details_task = loop.run_in_executor(None, movie_availability, movie_name)

        # Wait for functions to complete and retrieve their results

        image = await image_task
        details = await details_task

        
        # Check for errors in the results
        if not image or 'error' in details:
            error_message = "Movie not found"
            details = {}  # Ensure details is an empty dictionary to avoid template errors

        print(f"{image}\n\n{details}")

    return render_template('movies.html', image=image, details=details, error_message=error_message)


def search_for_movie(movie_name):

    # Rapidapi
    url = "https://imdb146.p.rapidapi.com/v1/find/"

    querystring = {"query": movie_name}
    headers = {
        "X-RapidAPI-Key": "1ae4654528msh82cf9d56f299a41p175eb1jsnebd34a46be13", # insert your api Key 
        "X-RapidAPI-Host": "imdb146.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()  # Convert to a dictionary

        if 'titleResults' in data and 'results' in data['titleResults'] and data['titleResults']['results']:
            # Access the IMAGE URL from the 'titlePosterImageModel' dictionary within the first result
            image_url = data['titleResults']['results'][0]['titlePosterImageModel']['url']

        else:
            print("Error occurred")

        return image_url
    
    except Exception as e:
        print(f"Error: {e}")

def movie_availability(movie_name):

    # Rapidapi
    url = "https://streaming-availability.p.rapidapi.com/shows/search/title"

    querystring = {"country": "gb", "title": movie_name, "output_language": "en", "show_type": "movie", "series_granularity": "show"}
    headers = {
        "X-RapidAPI-Key": "1ae4654528msh82cf9d56f299a41p175eb1jsnebd34a46be13", # insert your api
        "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
    }

    result = {}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json() # Convert to a dictionary
        
        # If dictionary is empty
        if not data:
            result['error'] = "No results found "
            return result
        
        response = data[0]
        info = {}
        """
        request.get allows for a default value. 
        incase the specified key doesnt have a value
        """
        movie_overview = response.get('overview', 'No overview available')
        movie_release_year = response.get('releaseYear', 'Unknown')
        movie_genre = [i['name'] for i in response.get('genres', [])]

        # Getting the top 3 available streaming options
        streaming_options = response.get('streamingOptions', {}).get('gb', [])[:3]
        
        for i in streaming_options:
            link = str(i.get('link', 'No link available'))
            price = str(i.get('price', {}).get('formatted', 'No price available'))
            info[link] = price

        # Assign values to result dictionary
        result['overview'] = movie_overview
        result['release_year'] = movie_release_year
        result['genre'] = movie_genre
        result['streaming_options'] = info

    # Returning the error
    except Exception as e:
        result['error'] = f"An error occurred: {e}"

    return result
