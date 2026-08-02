from dotenv import dotenv_values

# load_dotenv()


def search(query, media_type):
    if media_type == "movie":
        search_movie(query)
    elif media_type == "show":
        search_show(query)
    else:
        raise ValueError(f'Invalid media type given to search -> "{media_type}"')


def search_movie(query):
    pass


def search_show(query):
    pass
