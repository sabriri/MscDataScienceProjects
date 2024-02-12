# Imprort modules
import mariadb
import sys
import pandas as pd

# Connect to MariaDB
try:
    conn = mariadb.connect(
        user="cip_user",
        password="cip_pw",
        host="127.0.0.1",
        port=3306,
        database="CIP"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Getting Cursor
cur = conn.cursor()

# Drop the table if it exists
#cur.execute("DROP TABLE C_movies_stage3;")
cur.execute("DROP TABLE IF EXISTS C_genres_stage3;")
cur.execute("DROP TABLE IF EXISTS C_genre_ids_stage3;")
cur.execute("DROP TABLE IF EXISTS C_production_companies_stage3;")
cur.execute("DROP TABLE IF EXISTS C_company_ids_stage3;")
cur.execute("DROP TABLE IF EXISTS C_movies_stage3;")

# Create a table
cur.execute("CREATE TABLE C_movies_stage3 ("
            "movie_id INTEGER PRIMARY KEY,"
            "title VARCHAR(255),"
            "budget_rank FLOAT,"
            "budget INTEGER,"
            "revenue BIGINT,"
            "gross_profit BIGINT,"
            "release_date DATE,"
            "release_season VARCHAR(255),"
            "runtime INTEGER,"
            "vote_average FLOAT,"
            "vote_count BIGINT"
            ");")
print("Table is created")

cur.execute("CREATE TABLE C_genre_ids_stage3 ("
            "genre_id FLOAT PRIMARY KEY,"
            "genre_name VARCHAR(255)"
            ");")
print("Table is created")

cur.execute("CREATE TABLE C_genres_stage3 ("
            "movie_id INTEGER,"
            "genre_id FLOAT,"
            "PRIMARY KEY (movie_id, genre_id),"
            "FOREIGN KEY (genre_id) REFERENCES C_genre_ids_stage3 (genre_id)"
            ");")
print("Table is created")

cur.execute("CREATE TABLE C_company_ids_stage3 ("
            "production_company_id INTEGER PRIMARY KEY,"
            "production_company_name VARCHAR(255)"
            ");")
print("Table is created")

cur.execute("CREATE TABLE C_production_companies_stage3 ("
            "movie_id INTEGER,"
            "production_company_id INTEGER,"
            "PRIMARY KEY (movie_id, production_company_id),"
            "FOREIGN KEY (production_company_id) REFERENCES C_company_ids_stage3 (production_company_id)"
            ");")
print("Table is created")

# Load dataframes
movies = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_movies_stage3.csv', low_memory=False, encoding='utf-8')
genres = pd.read_csv('../../Barnett_Natalie_studentC/Data//C_genres_stage3.csv', low_memory=False, encoding='utf-8')
genre_ids = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_genre_ids_stage3.csv', low_memory=False, encoding='utf-8')
production_companies = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_production_companies_stage3.csv', low_memory=False, encoding='utf-8')
company_ids = pd.read_csv('/../../Barnett_Natalie_studentC/Data/C_company_ids_stage3.csv', low_memory=False, encoding='utf-8')

# Replace NaN values with None
movies = movies.astype(object).where(pd.notnull(movies), None)
# genres = genres.astype(object).where(pd.notnull(genres), None)
# production_companies = production_companies.astype(object).where(pd.notnull(production_companies), None)

# Looping through the data frame and adding each row to MariaDB
# movies
for i, row in movies.iterrows():
    sql = "INSERT INTO C_movies_stage3 (movie_id, title, budget_rank, budget, revenue, gross_profit, release_date, " \
          "release_season, runtime, vote_average, vote_count) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")
conn.commit()

# genre_id
for i, row in genre_ids.iterrows():
    sql = "INSERT INTO C_genre_ids_stage3 (genre_id, genre_name) "\
          "VALUES (%s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")                                                                                                                              
conn.commit()

# genres
for i, row in genres.iterrows():
    sql = "INSERT INTO C_genres_stage3 (movie_id, genre_id) "\
          "VALUES (%s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")
conn.commit()

# company_ids
for i, row in company_ids.iterrows():
    sql = "INSERT INTO C_company_ids_stage3 (production_company_id, production_company_name) "\
          "VALUES (%s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")
conn.commit()

# production_companies
for i, row in production_companies.iterrows():
    sql = "INSERT INTO C_production_companies_stage3 (movie_id, production_company_id) "\
          "VALUES (%s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")
conn.commit()

# Check connection
# Selecting first 10 rows in the MariaDB
cur.execute(
    "SELECT movie_id, title, budget_rank, budget, revenue, gross_profit, release_date, release_season, runtime, "
    "vote_average, vote_count "
    "FROM C_movies_stage3 LIMIT 10")

# #Printing this result-set as a check
for (movie_id, title, budget_rank, budget, revenue, gross_profit, release_date, release_season, runtime,
     vote_average, vote_count) in cur:
    print(
        f"Movie_id: {movie_id}, Title: {title}, Budget_Rank: {budget_rank}, Budget: {budget}, Revenue: {revenue}, "
        f"Gross_Profit: {gross_profit}, Release_Date: {release_date}, Release_Season: {release_season}, "
        f"Runtime: {runtime}, Vote_Average: {vote_average}, Vote_Count: {vote_count}")

# Closing the connection
conn.close()