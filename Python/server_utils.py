import requests
import sqlite3

def search_movie(title):
    """Cauta filmul in TMDB API (ret orice film ce contine title in nume)"""
    
    API_KEY = "your_api_key_here" 
    BASE_URL = "https://api.themoviedb.org/3"
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": title,
        "language": "en-US",  
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        return results
    else:
        print(f"Eroare: {response.status_code}")
        return None
    
def search_database(database, movie_name):
    """Cauta in database numele filmului"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        movie_name = movie_name.strip().replace('\n', '').upper()

        query = "SELECT * FROM movies WHERE UPPER(TRIM(title)) LIKE ?"
        cursor.execute(query, ('%' + movie_name + '%',))

        result = cursor.fetchall()

        
        if result:
            return result
        else:
            print(f"Nu s au gasit filme care contin '{movie_name}' in baza de date.")
            return []
            
    except sqlite3.Error as e:
        print(f"Eroare la conexiunea la baza de date: {e}")
        return []
    finally:
        if conn:
            conn.close()
            
def insert_movie_into_db(database, movie):
    """Insereaza filmul in tabela movies din database"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        query_check = "SELECT id FROM movies WHERE id = ?"
        cursor.execute(query_check, (movie.get("id"),))
        result = cursor.fetchone()
        
        if result:
            print(f"Filmul '{movie.get('title')}' exista deja in baza de date.")
            return
        
        query = """
        INSERT INTO movies (id, title, release_date, rating)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (
            movie.get("id"),
            movie.get("title"),
            movie.get("release_date"),
            movie.get("rating")
        ))
        conn.commit()
        print(f"Filmul '{movie.get('title')}' a fost adaugat in baza de date.")
    except sqlite3.Error as e:
        print(f"Eroare la inserarea filmului în baza de date: {e}")
    finally:
        if conn:
            conn.close()
            
def delete_movies_with_zero_rating(database):
    """Functie care sterge filmele cu 0.0 rating"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        query = "DELETE FROM movies WHERE rating = 0.0;"
        cursor.execute(query)
        
        conn.commit()
        
        print(f"S au eliminat {cursor.rowcount} filme cu rating 0.0")
    except sqlite3.Error as e:
        print(f"Eroare la eliminarea filmelor cu rating 0.0: {e}")
    finally:
        if conn:
            conn.close()
            
def search_actor_id(actor_name):
    """TMDB API pentru ID ul unui actor"""
    
    API_KEY = "your_api_key_here"
    BASE_URL = "https://api.themoviedb.org/3"
    url = f"{BASE_URL}/search/person"
    params = {
        "api_key": API_KEY,
        "query": actor_name,
        "language": "en-US"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            actor_id = results[0].get("id")
            return actor_id
        else:
            print(f"Nu s-a gasit niciun actor cu numele '{actor_name}'.")
            return None
    else:
        print(f"Eroare la cautarea actorului '{actor_name}': {response.status_code}")
        return None
    
def get_actor_movies(actor_id):
    """Filmele in care joaca actorul cu ID ul dat ca param"""
    
    API_KEY = "your_api_key_here"
    BASE_URL = "https://api.themoviedb.org/3"
    url = f"{BASE_URL}/person/{actor_id}/movie_credits"
    params = {"api_key": API_KEY}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        movies = data.get("cast", [])
        return [{"id": movie["id"], "title": movie["title"], "release_date": movie["release_date"], "rating": movie.get("vote_average")} for movie in movies]
    else:
        print(f"Eroare la obtinerea filmelor pentru actorul cu ID-ul {actor_id}: {response.status_code}")
        return []
    
def insert_actor_into_db(database, actor_name):
    """Adauga actorul in baza de date, daca nu exista deja"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM actors WHERE UPPER(name) = UPPER(?)", (actor_name,))
        actor = cursor.fetchone()
        
        if actor:
            return actor[0]
        else:
            cursor.execute("INSERT INTO actors (name) VALUES (?)", (actor_name,))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Eroare la inserarea actorului '{actor_name}': {e}")
        return None
    finally:
        if conn:
            conn.close()


def insert_movie_actor_relation(database, movie_id, actor_id):
    """Functie pentru legatura dintre tabelele actors si movie_actors din DB"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM movie_actors WHERE movie_id = ? AND actor_id = ?",
            (movie_id, actor_id)
        )
        existing_relation = cursor.fetchone()
        
        if not existing_relation:
            cursor.execute(
                "INSERT INTO movie_actors (movie_id, actor_id) VALUES (?, ?)",
                (movie_id, actor_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Eroare la inserarea relatiei dintre film si actor: {e}")
    finally:
        if conn:
            conn.close()


def search_movies_by_actor(actor_name, database='../Database/movie_database.db'):
    """Functia folosita pentru a returna top 10 filme dupa rating in care joaca actorul cautat"""
    
    actor_id = search_actor_id(actor_name)
    if actor_id:
        movies = get_actor_movies(actor_id)
        if movies:
            sorted_movies = sorted(movies, key=lambda x: x['rating'] if x['rating'] is not None else 0, reverse=True)
            top_movies = sorted_movies[:10]

            db_actor_id = insert_actor_into_db(database, actor_name)
            for movie in top_movies:
                movie_id = movie["id"]
                movie_title = movie["title"]
                release_date = movie["release_date"]
                rating = movie["rating"]

                insert_movie_into_db(database, {
                    "id": movie_id,
                    "title": movie_title,
                    "release_date": release_date,
                    "rating": rating
                })

                insert_movie_actor_relation(database, movie_id, db_actor_id)

            print(f"Top 10 filme ale actorului '{actor_name}' au fost salvate in baza de date.")
            return top_movies
        else:
            print(f"Nu s au gasit filme pentru actorul '{actor_name}'.")
            return []
    else:
        print(f"Actorul '{actor_name}' nu a fost gasit.")
        return []

def get_movies_by_actor_from_database(database, actor_name):
    """Functie pentru a cauta in DB un actor cu numele dat ca param"""
    
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        query_actor = "SELECT id FROM actors WHERE UPPER(name) = UPPER(?)"
        cursor.execute(query_actor, (actor_name,))
        actor = cursor.fetchone()

        if not actor:
            print(f"Actorul '{actor_name}' nu exista in baza de date")
            return []

        actor_id = actor[0]

        query_movies = """
        SELECT movies.title, movies.release_date, movies.rating
        FROM movies
        INNER JOIN movie_actors ON movies.id = movie_actors.movie_id
        WHERE movie_actors.actor_id = ?
        ORDER BY movies.rating DESC
        """
        cursor.execute(query_movies, (actor_id,))
        movies = cursor.fetchall()

        if movies:
            print(f"Filmele in care joaca actorul '{actor_name}':")
            for movie in movies:
                print(f"- {movie[0]} (Data lansarii: {movie[1]}, Rating: {movie[2]})")
            return movies
        else:
            print(f"Actorul '{actor_name}' nu are filme in baza de date.")
            return []

    except sqlite3.Error as e:
        print(f"Eroare la interogarea bazei de date: {e}")
        return []
    finally:
        if conn:
            conn.close()
            
def get_movie_trailer(movie_name):
    """Cauta trailerul unui film pe TMDB"""
    
    API_KEY = "your_api_key_here"
    try:
        search_url = "https://api.themoviedb.org/3/search/movie"
        search_params = {
            "api_key": API_KEY,
            "query": movie_name
        }
        search_response = requests.get(search_url, params=search_params)
        search_data = search_response.json()
        
        if not search_data["results"]:
            return f"Nu s au gasit rezultate pentru filmul '{movie_name}'."
        
        movie_id = search_data["results"][0]["id"]
        
        videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
        videos_params = {
            "api_key": API_KEY
        }
        videos_response = requests.get(videos_url, params=videos_params)
        videos_data = videos_response.json()
        
        trailers = [video for video in videos_data["results"] if video["type"] == "Trailer" and video["site"] == "YouTube"]
        
        if not trailers:
            return f"Nu exista trailere disponibile pentru filmul '{movie_name}'."
        
        trailer = trailers[0]
        trailer_url = f"https://www.youtube.com/watch?v={trailer['key']}"
        return f"Trailer pentru '{movie_name}': {trailer_url}"
    
    except Exception as e:
        return f"A aparut o eroare: {e}"

def get_movie_reviews(movie_id):
    API_KEY = "your_api_key_here"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews"
    params = {"api_key": API_KEY, "language": "en-US", "page": 1}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        reviews = data.get("results", [])
        return reviews
    else:
        print("Failed to fetch reviews:", response.status_code, response.text)
        return None
