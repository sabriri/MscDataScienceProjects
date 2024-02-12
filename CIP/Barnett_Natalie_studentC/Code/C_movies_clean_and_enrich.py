import numpy as np
import pandas as pd

# Import data
movies = pd.read_csv('../../Barnett_Natalie_studentC/Data/C_movies_metadata_stage1.csv',
                     low_memory=False, encoding='utf-8') # encode at UTF-8 so that multiple language characters are read
# Low_memory is set to false because read_csv will by default try to determine the dtypes for each column. However,
# the data is not clean and will result in an error. We will clean the data and set the dtypes later.
movies = pd.DataFrame(data = movies)
#print(movies.head(10))
#print(movies.columns)

############################## Data Cleaning ######################################################################
# Remove irrelevant columns that are not important to the business question
movies = movies.drop(['adult', 'belongs_to_collection', 'homepage', 'imdb_id', 'original_language', 'overview', 'popularity',
                      'poster_path', 'production_countries', 'spoken_languages','status', 'tagline', 'video'], axis=1)
# We sppecify the columns in brackets and then tell python to drop with axis = 1. 1 means columns while 0 means rows
#print(movies.columns)

### Impurity 1: Duplicate columns
# There are two columns containing movie titles and we need to understand the difference between the two. We can compare
# original title column with title column with python operator == and it will result in a boolean
# comparison = movies['original_title'] == movies['title']
# print(comparison)
# The comparison result reveals many titles that do not match.
# A for loop is more efficient in this case to identify the specific index of titles that do not match.
#for index, row in movies.iterrows(): #iterate over the movies dataframe rows
#     if row['original_title'] != row['title']: #if original title does not match title column
#         print(str(row['original_title']) + "does not match " + str(row['title'])) #print the titles
#     else:
#         continue
# There are too many movie titles are produced to fix manually one by one.
# Instead we delete the original title column because it lists movies in other languages. Title column will remain.
movies = movies.drop('original_title', axis = 1)
#print(movies.head(10))

## Impurity 2: Incorrect datatypes
# In order to enhance the data later, it is important the dataframe columns are categorized in the correct dtypes.
#print(movies.dtypes)
movies = movies.convert_dtypes() #Allows python to convert dtypes for us
#print(movies.dtypes) #however this fails to convert the columns properly
#movies.astype({'budget': 'int64', 'genres': 'object', 'id': 'int64', 'production_companies': 'object',
#                'release_date': 'datetime64', 'revenue': 'int64', 'runtime': 'float64', 'title': 'object',
#                'vote_average': 'float64', 'vote_count': 'int64'}).dtypes
# With the .astype method we try to assign the dtypes manually by listing each column and its desired data type.
# An error appears though because 'budget', 'id' and 'release_date' have incompatible entries for the desired data types.

# The release date column can be converted to the datetime dtype with the to_datetime functionm in pandas.
# To convert properly though, the date format argument specifies the desired format for the date to be displayed.
# In this case, the format is set to match the current data formatting. The errors argument is set to coerce so that
#any invalid parsings will be set as NaN.
movies['release_date'] = pd.to_datetime(movies['release_date'], format='%Y-%m-%d', errors='coerce')
# Now the release date column is represented as a datetime

#N ext we convert the budget column to the integer data type with the to_numeric function. The downcast argment
# specifies the type of data type to convert to. The errors argument determines how to handle invalid parsing.
# Setting this to coerce ensures that any invalid values are set at NaN values.
movies['budget']= pd.to_numeric(movies['budget'], errors='coerce', downcast='integer')

# Using the same method as the budget column, we convert movie id to an integer
movies['id']= pd.to_numeric(movies['id'], errors='coerce', downcast='integer')
print(movies.dtypes)

## Impurity 3: Handling NaN values
# Any NaN that are produced from the id columne should now be removed from the dataset. A row that does not contain
# a movie title will not provide the necessary insights for the research questions and should be removed.
movies.dropna(axis = 0, subset=['id'], inplace=True)
# the dropna function easily removes rows with null values. You can specify the column to search for na's in the subset
# argument and then also comfirm how na's should be dropped - by row (0) or column (1). The inplace argument allows
# the original dataframe to be changed

# Any zero values in runtime, vote_average and vote_count should be replaced with NaN
movies['runtime'].replace(0, np.nan, inplace=True)
movies['vote_average'].replace(0, np.nan, inplace=True)
movies['vote_count'].replace(0, np.nan, inplace=True)

## Impurity 4: Removing Duplicates
# Now that movie id is converted to an integer, we should check the column for duplicates. Its important that each movie
# has its own unique identifier and that a movie is not listed more than once.
# We can check if a movie id contain duplicates with the duplicated function in pandas. This function returns boolean
# series denoting duplicate rows. The keep argument determines which duplicates to mark. Here is it listed as false
# to mark all duplicates as true, even for the first occurrence. We save this as a variable id_duplicates
id_duplicates = movies.duplicated(subset=['id'], keep=False)
# Now we use a for loop to count how many duplicates were counted in the column. We iterate over id_duplicates and for
# every true, the counter will add one to its tally.
counter = 0
for i in id_duplicates:
    if i == True:
        counter += 1
print("There are " + str(counter) + " duplicates in the movie id column")
# The movie id column has 59 duplicated values!

# Now we must identify if the values are truly duplicated or if two different movies have the same id number.
# To do this, we index the movies database with the duplicated variable from above and save it as a new variable, ids.
# Ids is a dataframe that can be viewed so we can visually detect the type of duplicates we are dealing with.
ids = movies[id_duplicates]
# To be able to view the entire dataframe easily, the dataframe can be exported to a csv file.
#ids.to_csv('../../Barnett_Natalie_studentC/Data/ids.csv', encoding='utf-8', index=False)
# Otherwise we can also print the id and title columns from the id variable and sort them by id number to produce a
# clear view. Now we can determine if the movies are truly duplicated.
print(ids[['id','title']].sort_values(by=['id']))

# After reviewing the data, it is clear the movies are duplicated by id and title. The duplicates should first be
# removed by using the drop_duplicates method focusing on the subset 'id'. Inplace=True again allows the original
# dataframe to be changed.
movies.drop_duplicates(subset=['id'], inplace=True)

# We can check to make sure all duplicates are gone using the same for loop as earlier.
id_duplicates2 = movies.duplicated(subset=['id'], keep=False)
counter2 = 0
for i in id_duplicates2:
    if i == True:
        counter2 += 1
print("There are " + str(counter2) + " duplicates in the movie id column")
#This shows that there are no duplicates in the movie id column :)

## Impurity 5
# There are numbers in the budget and revenue column that do not make sense. For instance, here is an example:
print(movies.iloc[[180]]) # printing a locating based on integer index
# In this row, the budget is 2 which does not make sense for a movie budget. We need to remove out all values that are
# too low. However, since the movie dataset includes movies from as far back as 1900, the budgets and revenues shoould
# only be removed after 1960, a conservative value, to account for inflation. Some movies in the early 1900s were
# actually filmed on a budget of $10
# We use a python operator to index all movies after 31 December 1959
movies_after_1960 = movies[(movies['release_date']>'1959-12-31')]
print(movies_after_1960['release_date']) # print to make sure it works
# Index movies with budget below 1000
budget_below_1000 = movies_after_1960[movies_after_1960['budget'] < 1000]
# Index movies with revenue below 1000
revenue_below_1000 = movies_after_1960[movies_after_1960['revenue'] < 1000]
# Replace values below 1000 with NaN in the 'budget' column
movies.loc[budget_below_1000.index, 'budget'] = np.nan #np.nan replaces values as missing or indefined (NaN)
# Replace values below 1000 with NaN in the 'revenue' column
movies.loc[revenue_below_1000.index, 'revenue'] = np.nan\
# We check that it worked by referencing the same row the used to have a budget of 2
print(movies.iloc[[180]])
# it worked because now the budget shows NaN

# We rename the id column so that it is clear we are talking about movie id and not genre id or company id
movies = movies.rename(columns={'id':'movie_id'})

## Impurity 6 is listed after the enhancement section

###################################### Enhancing the Data ###########################################################
## Enhancement 1
# We are adding a  column that ranks movie budgets from highest to lowest.
# We must keep in mind that here are many NaN values in the budget column so we must specify how we want the rank function
# to handle these values. Na_option is set to "keep" so that is assigns an NaN rank to NaN values. We also want to
# specify how to handle records that have the same value with the method argument. Here it is set to max so that all
# ties are assigned the highest rank in the group.
movies['budget_rank'] = movies['budget'].rank(ascending=False, na_option='keep', axis=0, method='max')
# Make sure the budget rank column is an integer.
#movies['budget_rank']= movies.astype({'budget_rank': 'int64'}).dtypes
movies['budget_rank']= pd.to_numeric(movies['budget_rank'], errors='coerce', downcast='integer')
# print(movies.dtypes)
# print(movies['budget_rank'])

## Enahncement 2
# We are also creating a season column based on movie's release date
# With the function dt.month, we are telling python to interpret the months in the release date column as numbers 1 - 12
# to represent the 12 months of the year. Then the map function is used to assign values to the month numbers. In this
# case, the months are interpreted as winter, spring, summer or fall using a dictionary.
movies['release_season'] = movies['release_date'].dt.month.map({
    12: 'Winter',
    1: 'Winter',
    2: 'Winter',
    3: 'Spring',
    4: 'Spring',
    5: 'Spring',
    6: 'Summer',
    7: 'Summer',
    8: 'Summer',
    9: 'Fall',
    10: 'Fall',
    11: 'Fall'
})
print(movies['release_season']) #print to make sure that the new column assigned the values properly

## Enhancement 3
# The last data enahncement is calculating the gross profit of a movie by subtracting budget from revenue. Because
# there are a lot of 0 values in both columns, we need to exclude these value from the calculations. Gross profit is
# only beneficial if both columns are filled to get an accurate calculation.
# Create a boolean mask to identify rows where 'revenue' and 'budget' are non-zero.  If any of the 'revenue' or
# ccc'budget' values are NaN, the result of the comparison (!=) will be False, and those rows will not be included in the calculation.
notzero_rev = movies['revenue'] != 0 #save all values that do not equal zero in a variable
notzero_bud = movies['budget'] != 0
# Perform the calculation on the selected rows using boolean indexing. ".loc" can access a group of rows and columns
# by a boolean array
movies['gross_profit'] = movies.loc[notzero_rev, 'revenue'] - movies.loc[notzero_bud, 'budget']
#check to make sure the calculation works
print(movies['gross_profit'])

# change values with 0 as NaN so that future calculations will not include these values or calculate using 0
movies['budget'].replace(0, np.nan, inplace=True)
movies['revenue'].replace(0, np.nan, inplace=True)
movies['gross_profit'].replace(0, np.nan, inplace=True)
print(movies)

# We rearrange column order so that movie id and title are in the first 2 columns and so that the new calculated values
# are next to their corresponding values. First we save the desired column order by listing the column names in a variable.
col_order = ['movie_id', 'title', 'budget_rank', 'budget', 'revenue', 'gross_profit', 'genres', 'production_companies',
              'release_date', 'release_season', 'runtime', 'vote_average', 'vote_count']
# Then index the movies dataframe with the new variable and save it as a new variable.
movies = movies[col_order]
print(movies.columns)

############################# Normalize json columns in the dataframe ##############################################
# Impurity 6: Dealing with JSON
# Genres and production company columns are in Json format which is not ideal for data analysis. Normalizing these
# columns will put key info into seperate columns rather than being in one column in a dictionary format.
#print(movies['genres'])
#print(movies['production_companies'])

# First, we create new variables that just contains information about movie genres and movie production companies.
# Movie id remains in order to connect the resulting dataframe to the main movie dataframe in a dataframe join
# Drop columns not needed for genre and production companies tables.
genres = movies.drop(['title', 'budget_rank', 'budget', 'revenue', 'gross_profit', 'production_companies',
              'release_date', 'release_season', 'runtime', 'vote_average', 'vote_count'], axis=1)
production_companies = movies.drop(['title', 'budget_rank', 'budget', 'revenue', 'gross_profit', 'genres',
              'release_date', 'release_season', 'runtime', 'vote_average', 'vote_count'], axis=1)

# First we will be normalizing genres. The genres column contained a genre id and the genre name in a dictionary.
# We can normalize these fields with the pandas json_normalize function. Within the function we specify the column to
# perform the action which is the 'genres' column. Then apply(eval) applies the eval function to each element in genres
# to evaluate the string representation of a list into an actual list object. sum() concatenates all the lists obtained
# from applying eval into a single list.
genre_id = pd.json_normalize(genres['genres'].apply(eval).sum())
# Then we rename id to genre id so that it is clear which id is being referenced
genre_id = genre_id.rename(columns={'id':'genre_id'})
print(genre_id.columns)
print(genre_id)

# Now we want to match the genre ids with the movies they are describing. Most movies are a combination of multiple
# genres. Therefor, we want each movie to show all the genres in a long format.
import ast # Abstract Syntax Trees: It provides functions to safely evaluate and parse Python expressions or literals
def extract_genreid(row): # We are defining a function called extract_genreid that takes a row as an input
    genres = ast.literal_eval(row['genres']) # This line extracts the value of the 'genres' column from the current
    # row and uses ast.literal_eval() to evaluate it as a Python expression. The result is assigned to 'genres'
    genre_id = [genre['id'] for genre in genres] # This line uses a list comprehension to iterate over the genres list
    # and extract the value of the 'id' key from each dictionary. The resulting 'id' values are stored in the genre_id list
    return genre_id # Returns the generated list
genres['genre_id'] = genres.apply(extract_genreid, axis=1) # Now we apply the defined extract_genreid function and use
# apply() method to make sure the function applies to each row on the column.
genres= genres.drop(['genres'], axis = 1) # We drop the original genres column because it is still in json format
print(genres)
# Now there is one dataframe genre_id that has the genre id number with the genre name and the other dataframe.
# genres has the genre id in relation to the movie id. Although this may not have been the most direct path, we now have
# the data in seperate columns that can be easily analyzed.

# With genres normalized, next we must normalize the production companies column.
# First, we extract production company ids with movie ids.
def extract_production_company(row): # defining a funtion called exrtact_production_company
    companies = ast.literal_eval(row['production_companies']) if pd.notna(row['production_companies']) else [] # This line
    # gets the value of the 'production_companies' column from the input row. If the value is not missing, it uses
    # ast.literal_eval() to evaluate the string of the production companies and turns it into a list of dictionaries.
    # If the value is NaN, it returns an empty list.
    if isinstance(companies, list): # checks to make it is of type list
        company_id = [company['id'] for company in companies] # list comprehension to to extract id values from each dictionary
    else:
        company_id = [] # if not a list, it assigns an empty list to the variable
    return company_id
# Below we apply the extract_production_company function to each row of the production_companies dataframe using the apply()
# function on the column.The new column is called 'production_company_id' and assigns the returned values from the function to this column.
production_companies['production_company_id'] = production_companies.apply(extract_production_company, axis=1)

# Now that we have company id with movie id, we need to extract company id with the production company name.
# First we must drop rows with missing values in the 'production_companies' column.
production_companies = production_companies.dropna(subset=['production_companies'])
# Second we evaluate the string representation of the list in 'production_companies' column and convert to a python object.
production_companies['production_companies'] = production_companies['production_companies'].apply(ast.literal_eval)
# Flatten the 'production_companies' column and normalize it with json_normalize
company_id = pd.json_normalize(production_companies['production_companies'].explode()) # explode converts a column with
# list-like elements into multiple rows, duplicating the other column values for each element in the list.
# We rename id to be production_comapny_id
company_id = company_id.rename(columns={'id': 'production_company_id'})
print(company_id)
# Now there is a dataframe called production_companies that includes the company id with the movie ids and the another
# dataframe called company_id that lists the company ids with the production companny names
# Remove the production company column from the dataframe because it is in a json format.
production_companies = production_companies.drop(['production_companies'], axis = 1)

# 'genres' columns are movie id and genre id
# 'production_companies' columns are production company id and movie id
# Both genres and production companies dataframes show the movie ids as a list when long format is desired.
# We use explode again to place production company ids in seperate rows.
production_companies = production_companies.explode('production_company_id')
# We reset the index with the reset_index function. The previous index values are no longer helpful and must be reset.
production_companies = production_companies.reset_index(drop=True)
print(production_companies)
# We use explode to place genre ids in seperate rows.
genres = genres.explode('genre_id')
# Reset the index.
genres = genres.reset_index(drop=True)
genres['genre_id']= pd.to_numeric(genres['genre_id'], errors='coerce', downcast='integer')
print(genres.dtypes)

###################### Clean and Merge normalized data #################################
# Production_company_id is a float instead of integer. This needs to be changed so that it can connect with the other dataframes
company_id['production_company_id'] = company_id['production_company_id'].fillna(0).astype(int)
print(company_id.dtypes)

# We also must drop the unnormalized columns from the original movies dataframe.
movies = movies.drop(['genres', 'production_companies'], axis = 1)

# Company_id: remove duplicates, remove blank rows, sort numbers, change column order with id first, and remove rows with NaN
# We use dropna to remove all rows with NaN values
company_id.dropna(inplace=True)
# We use the duplicated method to identify duplicates of company id. The production company id only needs to be listed once.
company_id.drop_duplicates(subset=['production_company_id'], keep='first', inplace=True)
# We drop duplicates from company id making sure to keep the first entry. Inplace means the changes are made to original dataframe.
# Sorting ids in ascending order is easier to read
company_id = company_id.sort_values(by=['production_company_id'])
# We also change column order so that company id is first
col_order3 = ['production_company_id', 'name']
company_id = company_id[col_order3]
company_ids = company_id.rename(columns={'name': 'production_company_name'})
print(company_id)

# genre_id: remove duplicates, sort ids
# We use the duplicate method to identify duplicates of genre id. The genre id only needs to be listed once.
genre_id.drop_duplicates(subset=['genre_id'], keep='first', inplace=True)
# Again we sort ids to be in ascending order.
genre_id = genre_id.sort_values(by=['genre_id'])
#print(genre_id)
# After printing, it was clear that there are values in the genre name column that do not match the category
# First we want to see what are the unique values listed to determine which names do not belong.
print(genre_id['name'].unique())
# These returned values do not belong in the genre dataframe and should be removed:
#'Carousel Productions' 'Vision View Entertainment','Telescene Film Group Productions' 'Aniplex' 'GoHands' 'BROSTA TV'
# 'Mardock Scramble Production Committee' 'Sentai Filmworks', 'Odyssey Media' 'Pulser Productions' 'Rogue State' 'The Cartel'
# First, the values to be removed from the name column will be saved in a variable.
values_to_remove = ['Carousel Productions', 'Vision View Entertainment', 'Telescene Film Group Productions', 'Aniplex',
                    'GoHands', 'BROSTA TV', 'Mardock Scramble Production Committee', 'Sentai Filmworks', 'Odyssey Media',
                    'Pulser Productions', 'Rogue State', 'The Cartel']
# The isin() function checks if each value is present.
# Then the drop method is called again on the dataframe to remove the index of the values that are in the name column
genre_id.drop(genre_id[genre_id['name'].isin(values_to_remove)].index, inplace=True)
genres_to_keep = genre_id['genre_id']
print(genre_id)

# Rename columns for clarity and convert to integer
genre_ids = genre_id.rename(columns={'name': 'genre_name'})
genre_ids['genre_id']= pd.to_numeric(genre_ids['genre_id'], errors='coerce', downcast='integer')

# Remove any Null or NaN values from foreign keys in the file
genres.dropna(subset=['genre_id'], axis=0, inplace=True)
production_companies.dropna(subset=['production_company_id'], axis=0, inplace=True)

# Save the cleaned dataframes as a csv file
movies.to_csv('../../Barnett_Natalie_studentC/Data/C_movies_stage3.csv', encoding='utf-8', index=False)
genres.to_csv('../../Barnett_Natalie_studentC/Data/C_genres_stage3.csv', encoding='utf-8', index=False)
genre_ids.to_csv('../../Barnett_Natalie_studentC/Data/C_genre_ids_stage3.csv', encoding='utf-8', index=False)
production_companies.to_csv('../../Barnett_Natalie_studentC/Data/C_production_companies_stage3.csv', encoding='utf-8', index=False)
company_ids.to_csv('../../Barnett_Natalie_studentC/Data/C_company_ids_stage3.csv', encoding='utf-8', index=False)
