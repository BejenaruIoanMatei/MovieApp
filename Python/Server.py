import socket
import json
from server_utils import search_movie, search_database, insert_movie_into_db, delete_movies_with_zero_rating, search_movies_by_actor, get_movies_by_actor_from_database, get_movie_trailer, get_movie_reviews

def main():
    HOST = "127.0.0.1"
    PORT = 65432
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(65536)
                if not data:
                        print("Clientul s-a deconectat.")
                        break
                
                message = data.decode('utf-8')
                if message == "quit":
                        print("Serverul se va opri.")
                        conn.sendall(b"Serverul s a oprit.")
                        return
                
                """PARTEA DE FILME"""
                if message.startswith("title:"):
                    movie_name = message.split(':')[1]
                    
                    """Cautarea filmului in DB"""
                    
                    search_result = search_database('../Database/movie_database.db',movie_name)
                                        
                    if search_result:
                        formatted_database_results = []
                        for movie in search_result:
                            database_movie = {
                                "id": movie[0],
                                "title": movie[1],
                                "release_date": movie[2],
                                "rating": movie[3]
                            }
                            formatted_database_results.append(database_movie)
                            
                        print(formatted_database_results)
                        return_data = json.dumps({
                            "status": "found",
                            "data": formatted_database_results
                        }).encode('utf-8')
                        print(f"DA, se gaseste '{movie_name}' in DB")
                        
                    else:
                        print(f"Nu se gaseste '{movie_name}' in DB")
                        
                        """Cautarea filmului in TMDB API"""
                        
                        api_results = search_movie(movie_name)
                        
                        if api_results:
                            formatted_results =[]
                            for movie in api_results:
                                if movie.get("vote_average") != 0.0:
                                    movie_data = {
                                        "id": movie.get("id"),
                                        "title": movie.get("title"),
                                        "release_date": movie.get("release_date"),
                                        "rating": movie.get("vote_average")
                                    }
                                    formatted_results.append(movie_data) 
                                    insert_movie_into_db('../Database/movie_database.db', movie_data)
                                    delete_movies_with_zero_rating('../Database/movie_database.db')
                            
                            return_data = json.dumps({
                                "status": "found_in_api",
                                "data" : formatted_results
                            }).encode('utf-8')
                            
                        else:
                            
                            """Filmul nu se gaseste nici in BD, nici in TMDB API"""
                            
                            return_data = json.dumps({
                                "status": "not_found",
                                "message" : f"Filmul '{movie_name}' nu a fost gasit nici in DB, nici in API TMDB"
                            }).encode('utf-8')
                            print(f"Filmul '{movie_name}' nu a fost gasit nici in DB, nici in API TMDB.")

                
                elif message.startswith("actor:"):
                    
                    """PARTEA DE ACTORI"""
                    
                    actor_name = message.split(':', 1)[1]
                    """DATABASE"""
                    search_result_database = get_movies_by_actor_from_database('../Database/movie_database.db', actor_name)
                    if search_result_database:
                        formatted_results = [
                            {"title": movie[0], "release_date": movie[1], "rating": movie[2]}
                            for movie in search_result_database
                        ]
                        return_data = json.dumps({
                            "status": "found",
                            "data": formatted_results
                        }).encode('utf-8')
                        print(f"FOUND IN DATABASE")
                    else:
                        """API"""
                        search_result = search_movies_by_actor(actor_name, '../Database/movie_database.db')
                        if search_result:
                            formatted_results = [
                                {"title": movie["title"], "release_date": movie["release_date"], "rating": movie["rating"]}
                                for movie in search_result
                            ]
                            return_data = json.dumps({
                                "status": "found",
                                "data": formatted_results
                            }).encode('utf-8')
                            print(f"FOUND IN API")
                        else:
                            return_data = json.dumps({
                                "status": "not_found",
                                "message": f"Nu s au gasit filme pentru actorul '{actor_name}' in baza de date."
                            }).encode('utf-8')
                            print(f"NOT FOUND")
                            
                elif message.startswith("trailer:"):
                    """Partea de trailers"""
                    
                    movie_name = message.split(":", 1)[1].strip()
                    print(f"Caut trailer pentru '{movie_name}'...")
                    trailer_url = get_movie_trailer(movie_name)
                    
                    return_data = json.dumps({
                        "status": "trailer",
                        "url": trailer_url
                    }).encode('utf-8')
                    print(return_data)
                    
                elif message.startswith("reviews:"):
                    """Partea de recenzii"""
                    try:
                        movie_name = message.split(":", 1)[1].strip()
                        api_results = search_movie(movie_name)
                        
                        if api_results:
                            movie_id = api_results[0].get('id')
                            print(f"id ul filmului {movie_name} este {movie_id}")
                            
                            print(f"Caut recenzii pentru filmul cu ID ul '{movie_id}'...")
                            
                            reviews = get_movie_reviews(movie_id)
                            print(reviews)
                            if reviews:
                                formatted_reviews = [
                                    {"author": review.get("author", "Anonim"), "content": review.get("content"), "url": review.get("url")}
                                    for review in reviews
                                ]
                                return_data = json.dumps({
                                    "status": "reviews_found",
                                    "data": formatted_reviews
                                }).encode('utf-8')
                                
                                print(f"Recenzii gasite pentru filmul cu ID-ul '{movie_id}'.")
                            else:
                                return_data = json.dumps({
                                    "status": "no_reviews",
                                    "message": f"Nu s au gasit recenzii pentru filmul cu ID-ul '{movie_id}'."
                                }).encode('utf-8')
                                print(f"Nu s au gasit recenzii pentru filmul cu ID-ul '{movie_id}'.")
                        else:
                            return_data =json.dumps({
                                "status": "inexistent_movie_to_review",
                                "message": f"Nu am putut gasi recenzii pentru filmul {movie_name}"
                            }).encode('utf-8')
                            print(f"Filmul {movie_name} nu exista, deci nu are recenzii")
                    except Exception as e:
                        return_data = json.dumps({
                            "status": "error",
                            "message": f"Eroare la preluarea recenziilor: {str(e)}"
                        }).encode('utf-8')
                        print(f"Eroare la preluarea recenziilor: {str(e)}")
   
                else:
                    """Comanda invalida"""
                    return_data = json.dumps({
                        "status": "error",
                        "message": "Comanda necunoscuta."
                    }).encode('utf-8')
                
                conn.sendall(return_data)

                
if __name__ == '__main__':
    main()
            

