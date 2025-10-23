from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from faker import Faker
import time
import random
import csv  # Để CSV export
import os  # Để check file tồn tại

# Khởi tạo Faker cho data random US
fake = Faker('en_US')

# Config browser
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def generate_random_username():
    """Generate valid password: ≥8 chars, case-sensitive, no spaces, ≥3/4 types (upper, lower, digit, special)"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    base_pass = ''.join(random.choices(chars, k=8))  # Base 8 chars (min length)
    
    # Force ≥3 types (append nếu thiếu)
    has_upper = any(c.isupper() for c in base_pass)
    has_lower = any(c.islower() for c in base_pass)
    has_digit = any(c.isdigit() for c in base_pass)
    has_special = any(c in '!@#$%^&*' for c in base_pass)
    
    appends = []
    if not has_upper:
        appends.append('A')  # Upper
    if not has_lower:
        appends.append('a')  # Lower
    if not has_digit:
        appends.append('1')  # Digit
    if not has_special:
        appends.append('!')  # Special
    
    # Append để đảm bảo ≥3 types (nếu thiếu nhiều, append đủ)
    missing_count = 4 - sum([has_upper, has_lower, has_digit, has_special])
    if missing_count > 1:
        # Nếu thiếu nhiều, append thêm random để cân bằng
        for _ in range(missing_count - 1):
            appends.append(random.choice(chars))
    
    password = base_pass + ''.join(appends)
    
    # Randomize vị trí append (shuffle appends rồi insert random pos)
    if len(appends) > 0:
        random.shuffle(appends)  # Shuffle list appends
        insert_pos = random.randint(2, len(password) - 2)  # Insert giữa, tránh đầu/cuối
        password = password[:insert_pos] + ''.join(appends) + password[insert_pos:]
    
    # Final check: Đảm bảo ≥3 types
    final_has_upper = any(c.isupper() for c in password)
    final_has_lower = any(c.islower() for c in password)
    final_has_digit = any(c.isdigit() for c in password)
    final_has_special = any(c in '!@#$%^&*' for c in password)
    types_count = sum([final_has_upper, final_has_lower, final_has_digit, final_has_special])
    if types_count < 3:
        # Rare fallback: Append missing
        if not final_has_digit:
            password += '1'
        if not final_has_special:
            password += '!'
    
    return password  # Length ≥8, ≥3 types

def generate_valid_us_phone():
    """Generate valid US phone: 10 digits, area code 200-999 (không 0/1 đầu)"""
    for _ in range(5):  # Thử 5 lần
        phone_raw = fake.numerify('###-###-####').replace('-', '')  # 10 digits random
        area_code = int(phone_raw[:3])
        if 200 <= area_code <= 999 and phone_raw[0] != '0' and phone_raw[0] != '1':  # Valid area
            return phone_raw
    # Fallback nếu fail (dùng số test valid)
    return '2025550123'  # Area 202 OK

def save_to_csv(email, password, phone, full_name):
    """Lưu thông tin account thành công ra CSV"""
    file_path = 'accounts.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Email', 'Password', 'Phone', 'Full Name'])  # Header
        writer.writerow([email, password, phone, full_name])
    print(f"📁 Saved to {file_path}: {email}")

def create_account(num_accounts=1):
    signup_url = "https://www.staples.com/idm/com/createaccount"
    
    for i in range(num_accounts):
        print(f"Creating account {i+1}...")
        driver.get(signup_url)
        
        wait = WebDriverWait(driver, 20)
        
        # Generate data
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        email = f"{fake.user_name()}@{fake.domain_name()}"
        phone_raw = generate_valid_us_phone()  # Raw 10 digits valid
        phone_formatted = f"({phone_raw[:3]}) {phone_raw[3:6]}-{phone_raw[6:]}"
        password = generate_random_username()  # Fixed valid password
        
        print(f"Generated: {full_name}, {email}, {phone_formatted} (valid US), {password} (full, valid)")
        
        # Delays random
        delays = [random.uniform(3, 7) for _ in range(5)]
        
        try:
            # First Name
            time.sleep(delays[0])
            fn_field = wait.until(EC.presence_of_element_located((By.ID, "firstName")))
            fn_field.clear()
            fn_field.send_keys(first_name)
            print("✅ Filled First Name")
            
            # Last Name
            time.sleep(delays[1])
            ln_field = wait.until(EC.presence_of_element_located((By.ID, "lastName")))
            ln_field.clear()
            ln_field.send_keys(last_name)
            print("✅ Filled Last Name")
            
            # Email
            time.sleep(delays[2])
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.clear()
            email_field.send_keys(email)
            print("✅ Filled Email")
            
            # Phone - Fill formatted
            time.sleep(delays[3])
            phone_field = wait.until(EC.presence_of_element_located((By.ID, "mobileNumber")))
            phone_field.clear()
            phone_field.send_keys(phone_formatted)  # Format để valid ngay
            print("✅ Filled Phone (formatted)")
            
            # Password
            time.sleep(delays[4])
            pass_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            pass_field.clear()
            pass_field.send_keys(password)
            print("✅ Filled Password (valid)")
            
            # Shop type
            time.sleep(random.uniform(2, 4))
            try:
                business_radio = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='B']")))
                if not business_radio.is_selected():
                    business_radio.click()
                print("✅ Selected 'Business'")
            except:
                print("⚠️ Skip shop type")
            
            # Submit
            time.sleep(5)
            submit_btn = wait.until(EC.element_to_be_clickable((By.ID, "submitIdmCreateForm")))
            submit_btn.click()
            print("✅ Clicked Submit")
            
            # Wait result
            time.sleep(5)
            page_source = driver.page_source.lower()
            if any(word in page_source for word in ["welcome", "account created", "thank you", "sign in"]):
                print(f"🎉 Account {i+1} SUCCESS: {email}")
                save_to_csv(email, password, phone_raw, full_name)  # Lưu raw phone vào CSV
            elif any(word in page_source for word in ["error", "invalid", "already exists"]):
                print(f"❌ Error {i+1}: Check browser (e.g., duplicate email/phone).")
            else:
                print(f"⚠️ Unknown result {i+1}. Check browser manually.")
                
        except Exception as e:
            print(f"❌ Error {i+1}: {e}")
            print("Tip: Run manual once to verify selectors (F12 inspect).")
        
        # Delay giữa accounts
        if i < num_accounts - 1:
            print("Waiting 2-3 mins before next account...")
            time.sleep(60)
    
    driver.quit()

if __name__ == "__main__":
    create_account(5)  