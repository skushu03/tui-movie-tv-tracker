import asyncio

import httpx
from dotenv import dotenv_values


async def search(query, media_type):
    try:
        if media_type == "movie":
            return await search_movie(query)
        elif media_type == "show":
            return await search_show(query)
        else:
            raise ValueError(f'Invalid media type given to search -> "{media_type}"')
    except httpx.ConnectError as e:
        raise Exception(f"Connection Error: {e}")
    except httpx.ConnectTimeout as e:
        raise Exception(f"Connection Timeout: {e}")
    except ValueError as e:
        raise Exception(f"Value Error: {e}")


async def search_movie(query):
    api_key = dotenv_values(".env")["TMDB_API_KEY"]
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page=1"

    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}

    normalized_results = []
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        results = response.json()
        for res in results["results"]:
            normalized_results.append(
                {
                    "title": res["title"],
                    "tmdb_id": res["id"],
                    "genre_ids": res["genre_ids"],
                    "overview": res["overview"],
                    "rating": str(round(res["vote_average"], 1)),
                    "num_ratings": res["vote_count"],
                    "release_date": res["release_date"],
                    "media_type": "movie",
                }
            )

    return results["page"], results["total_pages"], normalized_results


async def search_show(query):
    api_key = dotenv_values(".env")["TMDB_API_KEY"]
    url = f"https://api.themoviedb.org/3/search/tv?query={query}&include_adult=false&language=en-US&page=1"

    headers = {"Authorization": f"Bearer {api_key}", "accept": "application/json"}

    normalized_results = []
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        results = response.json()
        for res in results["results"]:
            normalized_results.append(
                {
                    "title": res["name"],
                    "tmdb_id": res["id"],
                    "overview": res["overview"],
                    "rating": str(round(res["vote_average"], 1)),
                    "num_ratings": res["vote_count"],
                    "release_date": res["first_air_date"],
                    "media_type": "movie",
                }
            )

    return results["page"], results["total_pages"], normalized_results
