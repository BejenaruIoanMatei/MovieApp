# MovieApp

### Project Overview

MovieApp is a client-server application that allows users to search for movies and view detailed information, including ratings, trailers, and reviews.
> **Watch the Demo here**: [MovieAppDemo](https://drive.google.com/file/d/1Sn_-GdpRzhfsbNuOk6TOWTRLCI3-pvML/view?usp=sharing)

## Technologies Used

- Python, tkinter for the GUI
- SQLite for the database
- Additional:
  - HTML for the reviews page
  - Bash script to streamline app execution

### Features

- Takes a movie title as input from the client
- Server returns the movie's rating from a local SQLite database
- If the movie is not found, the server will:
  - Fetch the rating from TMDB API (if available)
  - Add the movie to the database for future queries
- Returns additional info such as:
  - Movie trailer from Youtube
  - A list of reviews from TMDB API
- App supports:
  - Searching by movie name
  - Actor name (actors integrated in the database)

### Setup Instructions

- Database:
  - In Database create "movie_database.db"
  - Run the queries in "--SQLite.sql"
- TMDB API:
  - Get your API key from TMDB (mandatory)
- Bash:
  - Give execution permission to "script.sh" -> _chmod +x script.sh_ in terminal
  - Run the script -> _./script.sh_
