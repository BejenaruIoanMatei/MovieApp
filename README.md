# MovieApp

## Project Requirements

Client-server graphical application that:

- Takes a movie title as input from the client
- The server returns the movie rating from a database
- If the movie is not found, the server will:
  - Fetch the rating from TMDB API (if available)
  - Add the movie to the database for future queries
- Returns additional info such as:
  - Movie trailer from Youtube
  - A list of reviews from TMDB API
- App supports:
  - Searching by movie name
  - Actor name (actors integrated in the database)

## What did i use ?

- Python, tkinter for the GUI
- SQLite for the database
- Additional: Html for the reviews page and a bash script for running the app

### Make sure before trying to execute the script

- Database:
  - In Database create "movie_database.db"
  - Run the queries in "--SQLite.sql"
- TMDB API:
  - Get your API key from TMDB (mandatory)
- Bash:
  - Give execution permission to "script.sh" -> _chmod +x script.sh_ in terminal
  - Run the script -> _./script.sh_
