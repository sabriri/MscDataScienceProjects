#############################
# Approach 2: Scraping Top 1000 Lifetime Gross Revenue and Budgets from Box Office Mojo - with Selenium
# (Approach 1 can be found at the end of the file in comment.)
# Author: Esin Handenur Isik
# CIP.FS23 Project HSLU
#############################

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import numpy as np


start_time = time.time()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless=new')                               # headless runs faster by approx. 1.5 minutes

driver = webdriver.Chrome(options=chrome_options)

def get_budget_data(title_URL, driver):

    driver.get(title_URL)
    soup = BeautifulSoup(driver.page_source, 'lxml') # using lxml, the more efficient parser in bs4

    try:
        summary_table = soup.find("div", class_="a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile")  # identical parent class of all elements in relevant summary table

        try:
            budget = summary_table.find_all("span", class_="money")[1].text  # second element in summary table with class "money" is the budget
        except:
            budget = np.nan  # budget is NaN if not available

    except:
        print("no summary table available..") # using try - except to prevent errors for any unforseen reasons
        budget = np.nan

    return budget


def crawlRevenueBudget():

    home_url = 'https://www.boxofficemojo.com'
    movie_link_extension = ["", "&offset=200", "&offset=400", "&offset=600", "&offset=800"]

    df_revenues = pd.DataFrame()
    movie_budgets_total = []
    count_movie = 1
    for extension in movie_link_extension:
        # loop over all 5 URL's of the Lifetime Gross Revenue table
        movie_link_complete = 'https://www.boxofficemojo.com/chart/top_lifetime_gross/?area=XWW' + extension

        get_rev_section = pd.read_html(movie_link_complete) # use pandas read_html to extract the data that is given in table form
        df_revenues = pd.concat([df_revenues, get_rev_section[0]], ignore_index=True) # append each continuation that results in 1 large dataframe

        driver.get(movie_link_complete) # webdriver loads webpage 1-5

        soup = BeautifulSoup(driver.page_source, 'lxml') # using lxml, the more efficient parser in bs4

        # (optional to scrape): Scrape links of movie summary pages:
        MoviesOnPage = soup.find_all('td', class_='a-text-left mojo-field-type-title') # pointing to the title fields in the table

        for movie in MoviesOnPage:     # loop over each of the 200 titles per URL
            for link in movie.find_all('a', href=True):  # extract link from movie title field
                title_URL = home_url + link['href'] # concatenate link extension for full URL
                movie_budget = get_budget_data(title_URL, driver)   # call get_budget_data function to scrape budgets
                movie_budgets_total.append(movie_budget)                          # append the infos
                count_movie += 1
                if count_movie%25 == 0:
                    print(count_movie, " movie budgets scraped...") # show scraping progress in 25- steps

    print("Scraping complete!")
    print("Appending budgets...")

    df_revenues['Budget'] = pd.Series(movie_budgets_total) # add budgets column to final table

    header_list = ['Rank', 'Title', "Budget", 'Lifetime Gross', 'Year'] #reorder columns for better visual interpretation
    df_revenues = df_revenues.reindex(columns=header_list)

    return df_revenues


def main():
    print("Start scraping..")
    topRevenueMovies = crawlRevenueBudget()
    print("Resulting dataframe containing Rank, Movie Title, Budget, Gross Revenue, Release Year: ")
    print(topRevenueMovies)
    print()
    print("Process complete")

    path = "../Data/A_stage1.csv"
    topRevenueMovies.to_csv(path, index = False)

if __name__=="__main__":
    main()


driver.quit()
usedTime1 = time.time() - start_time
print("Runtime of the program: ", usedTime1 , " seconds. ") # Runtime of the program:  861.1482963562012  seconds (headless) (14min), 945.9972093105316  seconds (head) (15min).



#############################
# Approach 1: Scraping Top 1000 Lifetime Gross Revenue and Budgets from Box Office Mojo - without Selenium
# Author: Esin Handenur Isik
# CIP.FS23 Project HSLU
#############################
#
# import requests
# from bs4 import BeautifulSoup
# import time
# import pandas as pd
# import numpy as np
#
#
# start_time = time.time()
#
# myheaders = {'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64)"
#              "AppleWebKit/537.36 (KHTML, like Gecko)"
#              "Chrome/110.0.0.0 Safari/537.36"}
#
# def get_budget_data(movielink):
#
#     get_budget = requests.get(movielink, headers=myheaders)  # request website content of all movie summary pages
#     soup = BeautifulSoup(get_budget.content, 'lxml')  # using lxml, the more efficient parser in bs4
#
#     try:
#         summary_table = soup.find("div", class_="a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile")  # identical parent class of all elements in relevant summary table
#
#         try:
#             budget = summary_table.find_all("span", class_="money")[1].text  # second element in summary table with class "money" is the budget
#         except:
#             budget = np.nan  # budget is null if not available
#
#     except:
#         print("no summary table available..") # using try - except to prevent errors for any unforseen reasons
#         budget = np.nan
#
#     return budget
#
#
# def crawlRevenueBudget():
#
#     home_url = 'https://www.boxofficemojo.com'
#     movie_link_extension = ["", "&offset=200", "&offset=400", "&offset=600", "&offset=800"]
#
#     df_revenues = pd.DataFrame()
#     movie_budgets_total = []
#     count_movie = 1
#     for extension in movie_link_extension:
#         # loop over all 5 URL's of the Lifetime Gross Revenue table
#         movie_link_complete = 'https://www.boxofficemojo.com/chart/top_lifetime_gross/?area=XWW' + extension
#
#         get_rev_section = pd.read_html(movie_link_complete) # use pandas read_html to extract the data that is given in table form
#         df_revenues = pd.concat([df_revenues, get_rev_section[0]], ignore_index=True) # append each continuation that results in 1 large dataframe
#
#         # use read_html to extract links as recommended by prof.:
#         get_budget_link = pd.read_html(movie_link_complete, extract_links="all")[0] # use pandas read_html with extract_links argument set to "all". Includes the budget link extensions
#         get_budget_link.columns = [x[0] for x in get_budget_link.columns] # where e.g., x = ("Title", None)
#
#         for record in get_budget_link["Title"]:     # loop over each of the 200 titles per URL
#             title_URL = home_url + record[1] # concatenate link extension for full URL
#             movie_budget = get_budget_data(title_URL)   # call get_budget_data function to scrape budgets
#             movie_budgets_total.append(movie_budget)     # append the infos
#             count_movie += 1
#             if count_movie%25 == 0:
#                 print(count_movie, " movie budgets scraped...") # show scraping progress in 25- steps
#
#     print("Scraping complete!")
#     print("Appending budgets...")
#
#     df_revenues['Budget'] = pd.Series(movie_budgets_total) # add budgets column to final table
#
#     header_list = ['Rank', 'Title', "Budget", 'Lifetime Gross', 'Year'] #reorder columns for better visual interpretation
#     df_revenues = df_revenues.reindex(columns=header_list)
#
#     return df_revenues
#
#
# def main():
#     print("Start scraping..")
#     topRevenueMovies = crawlRevenueBudget()
#     print("Resulting dataframe containing Rank, Movie Title, Budget, Gross Revenue, Release Year: ")
#     print(topRevenueMovies)
#     print()
#     print("Process complete")
#
#     path = "../Data/A_stage1.csv"
#     topRevenueMovies.to_csv(path, index = False)
#
# if __name__=="__main__":
#     main()
#
# usedTime1 = time.time() - start_time
# print("Runtime of the program: ", usedTime1 , " seconds. ") # Runtime of the program:  1199.2922322750092  seconds. (20min)
#
