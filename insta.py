# "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:/Chrome_Session"
import psutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import random

def is_chrome_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'] in ['chrome.exe', 'chrome']:
            return True
    return False

def open_tabs_and_fetch_followers(profile_dict, df, port):
    options = Options()
    # Use different debugging ports based on the instance
    options.add_experimental_option("debuggerAddress", f"localhost:{port}")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)

        for person, link in tqdm(profile_dict.items(), desc="Opening Links", unit="link"):
            driver.get(link)

            try:
                # Wait for the page to load completely
                time.sleep(random.uniform(1, 3))  # Random delay to avoid detection

                # Save the page source to a variable
                page_source = driver.page_source
                
                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                button_class = "xat24cr"
                button = soup.find_all('span', class_=button_class)
                inner_html_list = [span.decode_contents() for span in button]

                # Ensure there are enough spans found
                if len(inner_html_list) > 1:
                    print(f"\n{person} : {inner_html_list[1]} Followers")
                    # Update the DataFrame with the follower count as a string
                    df.loc[df['Full Name'] == person, 'Number of Followers'] = str(inner_html_list[1])
                    # Save the updated DataFrame to CSV after each update
                    df.to_csv(file_path, index=False)  # Save changes
                else:
                    print(f"No follower count found for {person}")

            except Exception as e:
                print(f"Error fetching data from {link}: {e}")

            # Pause between opening profiles to avoid triggering anti-scraping measures
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    file_path = r"D:\Work\Scrapper Scripts\Scrape_600\insta-followers\insta.csv"
    pre = 31802
    next = 35000
    df = pd.read_csv(file_path)
    persons = df['Full Name'].to_list()
    links = df['Profile Link'].tolist()
    followers = df['Number of Followers'].tolist()
    followers = [f for f in followers if pd.notnull(f)]
    profile_dict = dict(zip(persons[pre:next], links[pre:next]))
    print(f"Total {len(followers)}\nLast Processed entries\n{persons[pre]}\n{links[pre]}")
    
    # Run with different debugging ports for different instances
    port = 9223  # Change this to 9223 or another port for the second instance
    open_tabs_and_fetch_followers(profile_dict, df, port)
