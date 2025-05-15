# importing webdriver from selenium
from selenium import webdriver

# Here Chrome  will be used
driver = webdriver.Chrome('/workspaces/airflow/Task2/downloads')


# URL of website
url = "https://www.google.com/"

# Getting current URL source code
get_title = driver.title

# Printing the title of this URL
# Here it is null string
print(get_title, " ", len(get_title))

# Opening the website
driver.get(url)

# Getting current URL source code
get_title = driver.title

# Printing the title of this URL
print(get_title, "  ", len(get_title))
