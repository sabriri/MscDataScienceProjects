##########################################
# Data scraping from the awardsdatabase.oscars.org with a specific link allows to access the data for all
# winners in all categories.
# CIP_FS23
# Student B: Sabrina Rigo
##########################################
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

start_time = time.time()
def extract_data(awards_website):
    print("Start scraping")
    #create empty list
    data = []
    # counter set to 0
    count = 0
    soup = BeautifulSoup(awards_website.content, 'lxml')
    result_groups = soup.find_all('div', class_='awards-result-chron result-group group-awardcategory-chron')

    #go through every year and extract all the data from it
    for year in result_groups:
        award_year = year.find('div', class_='result-group-title').text.strip()

        categories = year.find_all('div', class_='result-subgroup subgroup-awardcategory-chron')

        # iterates over each subgroup from the categories
        for subgroup in categories:
            category = subgroup.find('div', class_='result-subgroup-title').text.strip()

            nominations = subgroup.find_all('div', class_="awards-result-subgroup-items")

            # iterates over each nomination within the subgroup
            for nomination in nominations:
                names = nomination.find_all('div', class_="awards-result-nominationstatement")
                nomination_titles = []

                for name in names:
                    name_element = name.find('a', class_="nominations-link")
                    name_x = name_element.text.strip() if name_element else ""
                    nomination_titles.append(name_x)

                # Extract names from list and if no name available it will be empty
                name1 = nomination_titles[0] if len(nomination_titles) >= 1 else ""
                name2 = nomination_titles[1] if len(nomination_titles) >= 2 else ""
                name3 = nomination_titles[2] if len(nomination_titles) >= 3 else ""

                # check if there is a public note/ honorary statement / description and add it or leave empty
                public_note_element = nomination.find('div', class_='awards-result-publicnote')
                public_note = public_note_element.text.strip() if public_note_element else ""

                honorary_statements_element = nomination.find('div', class_='awards-result-citation')
                honorary_statements = honorary_statements_element.text.strip() if honorary_statements_element else ""

                description_element = nomination.find('div', class_='awards-result-description')
                descriptions = description_element.text.strip() if description_element else ""

                films = nomination.find_all('div', class_="awards-result-film-title")

                # create empty list
                film_titles = []

                # find and add all the films to the empty list above
                for film in films:
                    film_title_element = film.find('a', class_="nominations-link")
                    film_title = film_title_element.text.strip() if film_title_element else ""
                    film_titles.append(film_title)

                # extract film_title from list and if no title available it will be empty
                film_title1 = film_titles[0] if len(film_titles) >= 1 else ""
                film_title2 = film_titles[1] if len(film_titles) >= 2 else ""
                film_title3 = film_titles[2] if len(film_titles) >= 3 else ""
                film_title4 = film_titles[3] if len(film_titles) >= 4 else ""

                characters = nomination.find_all('div', class_="awards-result-character")

                # create empty list
                character_names = []

                # find and add character names to character_names list
                for character in characters:
                    character_name_element = character.find('div', class_="awards-result-character-name")
                    character_name = character_name_element.text.strip() if character_name_element else ""
                    character_names.append(character_name)

                # extract character_name from list
                character_name1 = character_names[0] if len(character_names) >= 1 else ""
                character_name2 = character_names[1] if len(character_names) >= 2 else ""
                character_name3 = character_names[2] if len(character_names) >= 3 else ""
                character_name4 = character_names[3] if len(character_names) >= 4 else ""

                # add all the gathered data to data list
                data.append({
                        'award_year': award_year,
                        'category': category,
                        'name1': name1,
                        'name2': name2,
                        'name3': name3,
                        'film_title': film_title1,
                        'character_name': character_name1,
                        'film_title2': film_title2,
                        'character_name2': character_name2,
                        'film_title3': film_title3,
                        'character_name3': character_name3,
                        'film_title4': film_title4,
                        'character_name4': character_name4,
                        'honorary_statement': honorary_statements,
                        'description': descriptions,
                        'note' : public_note})

        # Counter + 1 every loop
        count += 1
        # Check if the counter reaches 10
        if count % 10 == 0:
            print(f"Scraped {count} result groups.")
        # put in a time.sleep because the website wants us to put in a Crawl-delay
        time.sleep(10)
    df = pd.DataFrame(data)
    return df

# function containig the link to the website which is calling the function above
def main():
    url = "https://awardsdatabase.oscars.org/search/getresults?query=%7B%22SearchFieldFilters%22%3A%5B%5D%2C%22Sort%22%3A%223-Award%20Category-Chron%22%2C%22AwardShowNumberFrom%22%3A0%2C%22AwardShowNumberTo%22%3A0%2C%22Search%22%3A40%2C%22IsWinnersOnly%22%3Atrue%7D"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Crawl-delay": "10"}

    #request to get data from website
    awards_website = requests.get(url, headers=headers)
    #call function
    dataframe_awards = extract_data(awards_website)
    print(dataframe_awards)
    print()
    print("Scraping complete:")

    # Create csv file
    dataframe_awards.to_csv('../Data/B_stage1.csv', index=False)
    print("Data extracted and saved to B_stage_1.csv")

if __name__=="__main__":
    main()

scrape_time = time.time() - start_time
print("Runtime: ", scrape_time)












#Scraping complete:
#Data extracted and saved to B_stage_1.csv
#Runtime:  1020.7799456119537



#function created to make csv.file but decided to use another way
#def save_data_to_csv(awards_df, csv_file):
#    headers = ["year", "category", "name1", "film_title", "character_name"]

#    with open(csv_file, "w", newline="") as file:
#        writer = csv.writer(file)
#        writer.writerow(headers)
#        writer.writerows(awards_df)

#    print("Data extracted and saved to", csv_file)

# csv_file = "extracted_data.csv"