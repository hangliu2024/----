from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
driver = webdriver.Chrome(options=options)
driver.maximize_window()

# 先打开登录页
driver.get("http://10.5.192.253:5001/auth/login")
print("正在打开登录页面...")

try:
    # 等待登录表单加载
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    
    # 填写登录信息
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    
    username_input.clear()
    username_input.send_keys("admin")
    password_input.clear()
    password_input.send_keys("admin123")
    
    # 点击登录按钮
    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_btn.click()
    
    print("已提交登录...")
    time.sleep(2)
    
    # 登录后跳转到AI助手页面
    driver.get("http://10.5.192.253:5001/ai-assistant")
    print("浏览器已打开: http://10.5.192.253:5001/ai-assistant")
    
except Exception as e:
    print(f"登录过程出错: {e}")
    # 即使登录失败，也尝试直接打开AI助手页面
    driver.get("http://10.5.192.253:5001/ai-assistant")
    print("已尝试直接打开AI助手页面")

input("按回车键关闭浏览器...")
driver.quit()