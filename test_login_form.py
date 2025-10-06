# tests/test_login_form.py — Tác giả: NGUYEN DO TU MAI (N23DCPT091)
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ĐỔI tên file ở đây nếu bạn dùng frmlogin.html
HTML_FILE = "login.html"
BASE_URL = Path(__file__).resolve().parents[1].joinpath(HTML_FILE).resolve().as_uri()

def shot(driver, name):
    out = Path(__file__).resolve().parents[1] / "screenshots"
    out.mkdir(exist_ok=True)
    driver.save_screenshot(str(out / f"{name}.png"))

@pytest.fixture(scope="module")
def driver():
    opts = Options()
    # Muốn chạy ẩn trình duyệt thì bỏ dấu # ở dòng dưới
    # opts.add_argument("--headless=new")
    service = Service(ChromeDriverManager().install())
    d = webdriver.Chrome(service=service, options=opts)
    d.set_window_size(1200, 900)
    yield d
    d.quit()

def open_form(d):
    d.get(BASE_URL)
    WebDriverWait(d, 5).until(EC.presence_of_element_located((By.ID, "login-btn")))

def msg(d):
    return d.find_element(By.ID, "message").text.strip()

def login(d, u="", p=""):
    d.find_element(By.ID, "username").clear(); d.find_element(By.ID, "username").send_keys(u)
    d.find_element(By.ID, "password").clear(); d.find_element(By.ID, "password").send_keys(p)
    d.find_element(By.ID, "login-btn").click()

def wait_hash(d, h, t=2):
    WebDriverWait(d, t).until(lambda x: x.current_url.endswith(h))

def test_tc01_login_success(driver):
    open_form(driver)
    login(driver, "student", "Secret123!")
    WebDriverWait(driver, 3).until(lambda d: "Login success" in msg(d))
    wait_hash(driver, "#/dashboard")
    shot(driver, "TC01_login_success")

def test_tc02_wrong_password(driver):
    open_form(driver)
    login(driver, "student", "wrong")
    WebDriverWait(driver, 3).until(lambda d: "Invalid username or password" in msg(d))
    assert not driver.current_url.endswith("#/dashboard")
    shot(driver, "TC02_wrong_password")

@pytest.mark.parametrize("u,p,err_id,txt", [
    ("", "Secret123!", "usernameError", "Please enter username."),
    ("student", "", "passwordError", "Please enter password.")
])
def test_tc03_empty(driver, u, p, err_id, txt):
    open_form(driver)
    login(driver, u, p)
    WebDriverWait(driver, 3).until(EC.text_to_be_present_in_element((By.ID, err_id), txt))
    assert "Please fill all required fields." in msg(driver)
    shot(driver, f"TC03_{err_id}")

def test_tc04_forgot(driver):
    open_form(driver)
    driver.find_element(By.ID, "forgot-link").click()
    wait_hash(driver, "#/forgot")
    assert "Forgot Password" in msg(driver)
    shot(driver, "TC04_forgot")

def test_tc05_signup(driver):
    open_form(driver)
    driver.find_element(By.ID, "signup-link").click()
    wait_hash(driver, "#/signup")
    assert "Sign Up" in msg(driver)
    shot(driver, "TC05_signup")

def test_tc06_social(driver):
    open_form(driver)
    for bid, name in [("social-facebook","Facebook"),("social-twitter","Twitter"),("social-google","Google")]:
        b = driver.find_element(By.ID, bid)
        assert b.is_displayed() and b.is_enabled()
        b.click()
        WebDriverWait(driver, 3).until(lambda d: f"Social login with {name}" in msg(d))
    shot(driver, "TC06_social")
