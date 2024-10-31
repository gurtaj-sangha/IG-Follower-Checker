import random
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains

INSTAGRAM_URL = "https://www.instagram.com"

def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

def save_credentials(username, password):
    with open('credentials.txt', 'w') as file:
        file.write(f"{username}\n{password}")

def load_credentials():
    if not os.path.exists('credentials.txt'):
        return None
    with open('credentials.txt', 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()
    return None

def prompt_credentials():
    username = input("Enter your Instagram username: ")
    password = input("Enter your Instagram password: ")
    save_credentials(username, password)
    return username, password

def slow_typing(element, text):
    for char in text:
        element.send_keys(char)
        random_sleep(0.1, 0.3)

def login(bot, username, password):
    bot.get('https://www.instagram.com/accounts/login/')
    random_sleep(2, 4)
    try:
        element = bot.find_element(By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")
        element.click()
    except NoSuchElementException:
        print("[Info] - Instagram did not require to accept cookies this time.")

    print("[Info] - Logging in...")
    try:
        username_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
        password_input = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))
    except TimeoutException:
        print("[Error] - Could not find the username or password fields.")
        return False

    username_input.clear()
    slow_typing(username_input, username)
    random_sleep(1, 2)
    password_input.clear()
    slow_typing(password_input, password)

    login_button = WebDriverWait(bot, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()
    random_sleep(10, 15)

    try:
        not_now_button = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
        not_now_button.click()
        print("[Info] - Clicked 'Not Now' on 'Save Your Login Info' pop-up.")
    except TimeoutException:
        print("[Info] - 'Save Your Login Info' pop-up did not appear.")

    try:
        not_now_button = WebDriverWait(bot, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]")))
        not_now_button.click()
        print("[Info] - Clicked 'Not Now' on 'Turn on Notifications' pop-up.")
    except TimeoutException:
        print("[Info] - 'Turn on Notifications' pop-up did not appear.")

    return True

def wait_for_user_to_scroll(duration=60):
    print(f"[Info] - Waiting for {duration} seconds to allow user to scroll and load all usernames...")
    time.sleep(duration)

def get_followers_or_following(bot, username, follow_type):
    bot.get(f'{INSTAGRAM_URL}/{username}/')
    random_sleep(3.5, 5)

    try:
        link = bot.find_element(By.XPATH, f'//a[contains(@href, "/{follow_type}")]')
        link.click()
        print(f"[Info] - Clicked on {follow_type} link.")
    except NoSuchElementException:
        print(f"[Error] - Could not find {follow_type} link for {username}.")
        return []

    random_sleep(2, 3)
    print(f"[Info] - Navigated to {follow_type} screen.")

    wait_for_user_to_scroll()

    users = set()
    elements = bot.find_elements(By.XPATH, '//span[@class="_ap3a _aaco _aacw _aacx _aad7 _aade"]')
    for element in elements:
        users.add(element.text)

    print(f"{follow_type.capitalize()}: {len(users)}")
    return list(users)

def get_followers(bot, username):
    return get_followers_or_following(bot, username, "followers")

def get_following(bot, username):
    return get_followers_or_following(bot, username, "following")

def compare_lists(followers, following):
    unfollowed_back = [user for user in following if user not in followers]
    return unfollowed_back

def write_to_txt(unfollowed_back):
    with open('unfollowed_back.txt', 'w') as file:
        file.write('\n'.join(unfollowed_back))
    print("Data written to text file successfully.")

def main():
    credentials = load_credentials()
    if credentials is None:
        username, password = prompt_credentials()
    else:
        username, password = credentials

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-cache")
    options.add_argument('--user-data-dir=./User_Data')  # Use a persistent user data directory

    bot = webdriver.Chrome(options=options)

    try:
        if not login(bot, username, password):
            print("[Error] - Login failed.")
            return
        
        print("Navigating to profile to get followers and following lists.")
        
        followers = get_followers(bot, username)
        print(f"Followers: {len(followers)}")
        
        following = get_following(bot, username)
        print(f"Following: {len(following)}")
        
        unfollowed_back = compare_lists(followers, following)
        write_to_txt(unfollowed_back)
        
    finally:
        try:
            bot.quit()
        except Exception as e:
            print(f"Error closing the browser: {e}")

if __name__ == "__main__":
    main()