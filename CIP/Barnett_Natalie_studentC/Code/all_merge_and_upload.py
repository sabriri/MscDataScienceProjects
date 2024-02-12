# Imprort modules
import mariadb
import numpy as np
import sys
import pandas as pd

# Import files
movies = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_movies_stage3.csv', low_memory=False, encoding='utf-8')
genres = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_genres_stage3.csv', low_memory=False, encoding='utf-8')
genre_ids = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_genre_ids_stage3.csv', low_memory=False, encoding='utf-8')
production_companies = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_production_companies_stage3.csv', low_memory=False, encoding='utf-8')
company_ids = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_company_ids_stage3.csv', low_memory=False, encoding='utf-8')
movies_studa = pd.read_csv('../../Isik_Esin_Handenur_studentA/Data/A_stage3.csv')
oscars_studb = pd.read_csv('./../Rigo_Sabrina_studentB/Data/B_stage3.csv')
oscar_wins = pd.read_csv('./../Rigo_Sabrina_studentB/Data/B_stage3.csvB_sum_df.csv')

############### Merging Files ########################
# Print and check column names
print(movies)
print(movies.dtypes)
print(movies_studa)
print(movies_studa.dtypes)
print(oscar_wins)
print(oscar_wins.dtypes)

# Convert all titles columns to string data type
movies['title'] = movies['title'].astype(str)
movies_studa['Title'] = movies_studa['Title'].astype(str)
oscar_wins['film_title'] = oscar_wins['film_title'].astype(str)
#
# Find matches between studa and studb
#Checking how many titles match

titles_c = movies['title'].unique()
titles_a = movies_studa['Title'].unique()
titles_b = oscar_wins['film_title'].unique()

matches_ca = np.intersect1d(titles_c, titles_a)
matches_cb = np.intersect1d(titles_c, titles_b)
#print(matches_ca)
print(len(matches_ca)) # 778 matches

#print(matches_cb)
print(len(matches_cb)) # 955 matches

# Perform the merge based on movie titles
# A left join works best here because we want to keep the all keys on the movies dataframe
mergedca = movies.merge(movies_studa, left_on='title', right_on='Title', how='left')
merged_all = mergedca.merge(oscar_wins, left_on='title', right_on='film_title', how='left')

# Drop duplicate title columns
merged_all.drop(['Title', 'Year', 'film_title'], axis=1, inplace=True)
# Drop rows with majority null values
merged_all.dropna(subset=['budget_rank', 'budget', 'revenue', 'gross_profit',
       'release_date', 'release_season', 'runtime', 'vote_average',
       'vote_count', 'Revenue Rank', 'Profit Rank', 'Budget',
       'Gross Revenue', 'R:B Ratio', 'Gross Profit', 'oscar_total'], how='all', axis=0, inplace=True)
print(merged_all.columns)

# We also need to join oscars_studb file with the movies file in order to include the movie_id column. The movie_id will
# become the foreign key for this table which will be separate from the main table
merged_movies_oscars = movies.merge(oscars_studb, left_on='title', right_on='film_title', how='left')
print(merged_movies_oscars.columns)

# Drop all columns from the movies file except for movie_id
merged_movies_oscars.drop(['title', 'budget_rank', 'budget', 'revenue', 'gross_profit', 'release_date',
                           'release_season', 'runtime', 'vote_average','vote_count'], axis=1, inplace=True)
# Drop columns with null indexes
merged_movies_oscars.dropna(subset=['index'], axis=0, inplace=True)

print(merged_movies_oscars.columns)
print(merged_movies_oscars.dtypes)
# Reorder columns
col_order = ['movie_id', 'index', 'year', 'oscars_held', 'category', 'name', 'film_title',
             'character_name', 'honorary_statement',  'description', 'note', 'act_dir',
             'winner_type']
merged_movies_oscars = merged_movies_oscars[col_order]

# The revenue avalues from movies_studa and movies file appear to be similar which was not the original intention.
# The revenue from the movies file was supposed to be only box office revenue while movies_studa was a LIFETIME revenue.
# Instead, we will combine the values to provide a more complete and accurate depicition of lifetime revenue with the
# combine_first function. The values from movies_studa will take precendence because the source is more credible.
merged_all["Gross Revenue"] = merged_all["Gross Revenue"].combine_first(merged_all["revenue"])

# We will do the same with the budget column to provide the most complete and accurate values.
merged_all["Budget"] = merged_all["Budget"].combine_first(merged_all["budget"])

# Recaluclate gross profit with the complete columns only beneficial if both columns are filled with values to get an accurate calculation.
# Create a boolean mask to identify rows where 'revenue' and 'budget' are non-zero.  If any of the 'revenue' or
# 'budget' values are NaN, the result of the comparison (!=) will be False, and those rows will not be included in the calculation.
notzero_rev = merged_all['Gross Revenue'] != 0 #save all values that do not equal zero in a variable
notzero_bud = merged_all['Budget'] != 0
# Perform the calculation on the selected rows using boolean indexing. ".loc" can access a group of rows and columns by boolean array
merged_all['Gross Profit'] = merged_all.loc[notzero_rev, 'Gross Revenue'] - merged_all.loc[notzero_bud, 'Budget']
#check to make sure the calculation works
print(merged_all['Gross Profit'])

# Drop the duplicate revenue and budget columns
merged_all.drop(['revenue', 'budget', 'gross_profit'], axis=1, inplace=True)

# Recalculate ranks for budget, revenue and profit
# ties are assigned the highest rank in the group.
merged_all['budget_rank'] = merged_all['Budget'].rank(ascending=False, na_option='keep', axis=0, method='max')
merged_all['Revenue Rank'] = merged_all['Gross Revenue'].rank(ascending=False, na_option='keep', axis=0, method='max')
merged_all['Profit Rank'] = merged_all['Gross Profit'].rank(ascending=False, na_option='keep', axis=0, method='max')

# Recalculate revenue to budget ratio
ratios = []
for x,y in zip(merged_all["Gross Revenue"], merged_all["Budget"]): # use for loop to calculate ratio and to be able to handle NaN exeptions
    try:
        ratio = round(x / y, 2) # round to 2 decimals
        ratios.append(ratio)
    except:
        ratio = np.nan
        ratios.append(ratio)

print(len(ratios))
merged_all["R:B Ratio"] = pd.Series(ratios) # add list of ratios as column "Ratio" to df

# Rename columns
merged_all.rename(columns={'Revenue Rank':'revenue_rank'}, inplace=True)
merged_all.rename(columns={'Profit Rank':'profit_rank'}, inplace=True)
merged_all.rename(columns={'Budget':'budget'}, inplace=True)
merged_all.rename(columns={'Gross Revenue':'revenue'}, inplace=True)
merged_all.rename(columns={'R:B Ratio':'revenue_budget_ratio'}, inplace=True)
merged_all.rename(columns={'Gross Profit':'profit'}, inplace=True)

# Reorder columns
col_order = ['movie_id', 'title', 'budget_rank', 'budget', 'revenue_rank', 'revenue',
             'revenue_budget_ratio', 'profit_rank',  'profit', 'release_date', 'release_season',
             'runtime', 'vote_average', 'vote_count', 'oscar_total']
merged_all = merged_all[col_order]
print(merged_all.columns)
print(merged_all.dtypes)

# save to csv file
merged_all.to_csv('../../Barnett_Natalie_studentC/Data/C_all_merged.csv', encoding='utf-8', index=False)
merged_movies_oscars.to_csv('/../../Barnett_Natalie_studentC/Data/C_oscars_movies_merged.csv', encoding='utf-8', index=False)

####################### Upload to Maria DB #############################################

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
cur.execute("DROP TABLE IF EXISTS C_oscars_movies_merged")
cur.execute("DROP TABLE IF EXISTS C_genres_stage3;")
cur.execute("DROP TABLE IF EXISTS C_genre_ids_stage3;")
cur.execute("DROP TABLE IF EXISTS C_production_companies_stage3;")
cur.execute("DROP TABLE IF EXISTS C_company_ids_stage3;")
cur.execute("DROP TABLE IF EXISTS C_all_merged;")

# Create a table
cur.execute("CREATE TABLE C_all_merged ("
            "movie_id INTEGER PRIMARY KEY,"
            "title VARCHAR(255),"
            "budget_rank FLOAT,"
            "budget FLOAT,"
            "revenue_rank FLOAT,"
            "revenue FLOAT,"
            "revenue_budget_ratio FLOAT,"
            "profit_rank FLOAT,"
            "profit FLOAT,"
            "release_date DATE,"
            "release_season VARCHAR(255),"
            "runtime FLOAT,"
            "vote_average FLOAT,"
            "vote_count FLOAT,"
            "oscar_total FLOAT"
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

# Create a table
cur.execute("CREATE TABLE C_oscars_movies_merged ("
            "movie_id INTEGER,"
            "index_NR INT,"
            "year VARCHAR(255),"
            "oscars_held INT,"
            "category TEXT,"
            "name TEXT,"
            "title VARCHAR(255),"
            "character_name VARCHAR(255),"
            "honorary_statement TEXT,"
            "description TEXT,"
            "note TEXT,"
            "act_dir TEXT,"
            "winner_type TEXT,"
            "PRIMARY KEY (movie_id, index_NR),"
            "FOREIGN KEY (movie_id) REFERENCES C_all_merged (movie_id)"
            ");")
print("Table is created")

# Upload data to mariadb with for loops
# Replace NaN values with None
merged_all = merged_all.astype(object).where(pd.notnull(merged_all), None)
genres = genres.astype(object).where(pd.notnull(genres), None)
production_companies = production_companies.astype(object).where(pd.notnull(production_companies), None)
merged_movies_oscars = merged_movies_oscars.astype(object).where(pd.notnull(merged_movies_oscars), None)

# Looping through the data frame and adding each row to MariaDB
# movies
for i, row in merged_all.iterrows():
    sql = "INSERT INTO C_all_merged (movie_id, title, budget_rank, budget, " \
          "revenue_rank, revenue, revenue_budget_ratio, profit_rank, profit, release_date, " \
          "release_season, runtime, vote_average, vote_count, oscar_total) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

for i, row in merged_movies_oscars.iterrows():
    sql = "INSERT INTO C_oscars_movies_merged (movie_id, index_Nr, year, oscars_held, category, name, title, character_name, " \
          "honorary_statement, description, note, act_dir, winner_type) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, tuple(row))
    print(f"Record inserted {i}")
conn.commit()

# Check connection
# Selecting first 10 rows in the MariaDB
cur.execute(
    "SELECT movie_id, title, budget_rank, budget, revenue_rank, revenue, revenue_budget_ratio, profit_rank, profit, "
    "release_date, release_season, runtime, vote_average, vote_count, oscar_total "
    "FROM C_all_merged LIMIT 10")

# #Printing this result-set as a check
for (movie_id, title, budget_rank, budget, revenue_rank, revenue, revenue_budget_ratio, profit_rank, profit,
     release_date, release_season, runtime, vote_average, vote_count, oscar_total) in cur:
    print(
        f"Movie_id: {movie_id}, Title: {title}, Budget_Rank: {budget_rank}, Budget: {budget}, Revenue_Rank: {revenue_rank}, Revenue: {revenue}, "
        f"Revenue_Budget_Ratio: {revenue_budget_ratio}, Profit_Rank: {profit_rank}, Profit: {profit}, Release_Date: {release_date}, Release_Season: {release_season}, "
        f"Runtime: {runtime}, Vote_Average: {vote_average}, Vote_Count: {vote_count}, Total_Oscars_Won: {oscar_total}")

# Closing the connection
conn.close()





























