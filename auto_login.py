"""使用Selenium自动登录资产管理系统并打开AI助手页面"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions

BASE_URL = 'http://10.5.192.253:5001'

print("正在启动浏览器...")

options = EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)

driver = None
try:
    driver = webdriver.Edge(options=options)
except Exception as e:
    print(f"Edge启动失败: {e}")
    try:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e2:
        print(f"Chrome也启动失败: {e2}")
        exit(1)

try:
    # 打开登录页面
    print("正在打开登录页面...")
    driver.get(f'{BASE_URL}/login')
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    time.sleep(2)
    
    # 输入邮箱
    email_input = wait.until(EC.presence_of_element_located((By.ID, 'email')))
    email_input.clear()
    for char in 'admin@example.com':
        email_input.send_keys(char)
        time.sleep(0.03)
    
    # 输入密码
    password_input = wait.until(EC.presence_of_element_located((By.ID, 'password')))
    password_input.clear()
    for char in 'Admin123!':
        password_input.send_keys(char)
        time.sleep(0.03)
    
    # 勾选"记住我"
    try:
        remember_checkbox = driver.find_element(By.ID, 'remember')
        if not remember_checkbox.is_selected():
            remember_checkbox.click()
    except:
        pass
    
    time.sleep(0.5)
    
    # 点击登录按钮
    submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')))
    submit_btn.click()
    print("已点击登录按钮，等待登录完成...")
    
    time.sleep(3)
    
    # 跳转到AI助手页面
    driver.get(f'{BASE_URL}/ai-assistant')
    time.sleep(2)
    print(f"✅ 已打开AI助手页面: {driver.current_url}")
    
    input("\n按回车键关闭浏览器...")

except Exception as e:
    print(f"\n操作出错: {e}")
    import traceback
    traceback.print_exc()