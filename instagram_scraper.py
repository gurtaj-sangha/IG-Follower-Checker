from datetime import datetime
import random
import time
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


INSTAGRAM_URL = "https://www.instagram.com"

app = Flask(__name__)
app.secret_key=os.urandom(24)


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

    time.sleep(60)

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
    """Write results to file"""
    filename = 'unfollowed_back.txt'
    with open(filename, 'w') as file:
        file.write('\n'.join(unfollowed_back))
    print("Data written to text file successfully.")
    return filename


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handle login form submission"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-software-rasterizer')

            user_data_dir = os.path.abspath('./chrome_user_data')
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir)
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
            service = webdriver.ChromeService()
            bot = webdriver.Chrome(options=options, service=service)
            
            if not login(bot, username, password):
                flash("Login failed. Please check your credentials.")
                bot.quit()
                return redirect(url_for('login_page'))
            
            followers = get_followers(bot, username)
            following = get_following(bot, username)
            
            unfollowed_back = compare_lists(followers, following)
            filename = write_to_txt(unfollowed_back)
            
            session['results'] = unfollowed_back
            session['filename'] = filename
            
            bot.quit()
            return redirect(url_for('results'))
            
        except Exception as e:
            print(f"[DEBUG] Error: {e}")
            flash("An error occurred. Please try again.")
            return redirect(url_for('login_page'))
            
    return render_template('login.html')

@app.route('/results')
def results():
    """Display results page"""
    if 'results' not in session:
        return redirect(url_for('login_page'))
    
    unfollowed_back = session['results']
    filename = session.get('filename', 'results.txt')
    return render_template('results.html', 
                         unfollowed_back=unfollowed_back,
                         filename=filename)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run(debug=True)
