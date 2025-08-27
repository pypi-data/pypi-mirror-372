import requests
from bs4 import BeautifulSoup
from datetime import datetime as dt
from plexflow.core.metadata.providers.imdb.datatypes import ImdbMovie, ImdbShow
from typing import Union
import json

def search_movie_by_imdb(imdb_id: str) -> Union[ImdbMovie, None]:
    """
    Search for a movie using its IMDB ID.

    Args:
        imdb_id (str): The IMDB ID of the movie.

    Returns:
        Union[ImdbMovie, None]: An instance of the ImdbMovie class representing the movie if found, 
        or None if the movie is not found.

    Raises:
        RuntimeError: If an HTTP error, connection error, timeout error, or request exception occurs.
    """
    url = f"https://www.imdb.com/title/{imdb_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise RuntimeError("An error occurred during the request.") from err

    soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.select("script[type='application/json']")

    for script in scripts:
        content = script.text
        data = json.loads(content)
        imdb_id = data.get("props", {}).get("pageProps", {}).get("tconst")
        data = data.get("props", {}).get("pageProps", {}).get("aboveTheFoldData")

        if data:
            title = data.get("originalTitleText", {}).get("text")
            release_day = data.get("releaseDate", {}).get("day")
            release_month = data.get("releaseDate", {}).get("month")
            release_year = data.get("releaseDate", {}).get("year")
            date_str = f"{release_year:04d}-{release_month:02d}-{release_day:02d}"
            release_date = dt.strptime(date_str, "%Y-%m-%d")

            runtime = data.get("runtime", {}).get("seconds")
            rating = data.get("ratingsSummary", {}).get("aggregateRating")
            votes = data.get("ratingsSummary", {}).get("voteCount")
            rank = data.get("meterRanking", {}).get("currentRank")

            return ImdbMovie(imdb_id, title, release_date, runtime, rating, votes, rank)

    return None


def search_show_by_imdb(imdb_id: str) -> Union[ImdbShow, None]:
    """
    Search for a TV show on IMDb using the IMDb ID.

    Args:
        imdb_id (str): The IMDb ID of the TV show.

    Returns:
        Union[ImdbShow, None]: An instance of the ImdbShow class representing the TV show if found, 
        or None if the TV show is not found.

    Raises:
        RuntimeError: If an HTTP error, connection error, timeout error, or request exception occurs.
    """
    url = f"https://www.imdb.com/title/{imdb_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise RuntimeError("An error occurred during the request.") from err

    soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.select("script[type='application/json']")

    for script in scripts:
        content = script.text
        data = json.loads(content)
        imdb_id = data.get("props", {}).get("pageProps", {}).get("tconst")
        main_data = data.get("props", {}).get("pageProps", {}).get("mainColumnData")
        data = data.get("props", {}).get("pageProps", {}).get("aboveTheFoldData")

        if data:
            title = data.get("originalTitleText", {}).get("text")
            release_day = data.get("releaseDate", {}).get("day")
            release_month = data.get("releaseDate", {}).get("month")
            release_year = data.get("releaseDate", {}).get("year")
            date_str = f"{release_year:04d}-{release_month:02d}-{release_day:02d}"
            release_date = dt.strptime(date_str, "%Y-%m-%d")
            episodes = main_data.get("episodes", {}).get("episodes", {}).get("total")
            seasons = len(set(map(lambda s: s.get("number"), main_data.get("episodes", {}).get("seasons", []))))

            runtime = data.get("runtime", {}).get("seconds")
            rating = data.get("ratingsSummary", {}).get("aggregateRating")
            votes = data.get("ratingsSummary", {}).get("voteCount")
            rank = data.get("meterRanking", {}).get("currentRank")

            return ImdbShow(imdb_id, title, release_date, runtime, rating, votes, rank, episodes, seasons)

    return None
