import mysql.connector  # MySQL과 연동하기 위한 모듈
from datetime import datetime  # 시간 처리
from apscheduler.schedulers.background import BackgroundScheduler  # 백그라운드에서 작업 스케줄링
from selenium.webdriver.common.action_chains import ActionChains  # Selenium에서 액션 체인 (마우스, 키보드 동작) 사용
from selenium.webdriver.common.keys import Keys  # 키보드 동작 제어
from selenium.common.exceptions import NoSuchElementException  # Selenium에서 요소를 찾지 못했을 때 발생하는 예외 처리
from selenium import webdriver  # 웹 드라이버를 실행하기 위한 모듈
from selenium.webdriver.chrome.service import Service  # ChromeDriver 서비스 관리
from selenium.webdriver.chrome.options import Options  # Chrome 옵션 설정
from selenium.webdriver.common.by import By  # 요소 찾기를 위한 By 클래스
from selenium.webdriver.support.ui import WebDriverWait  # 요소 로딩을 대기하기 위한 모듈
from selenium.webdriver.support import expected_conditions as EC  # 조건을 만족할 때까지 대기

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify  # Flask 웹 프레임워크 기본 모듈
from flask_bcrypt import Bcrypt  # 비밀번호 해싱 및 검증을 위한 Bcrypt 모듈
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required  # 사용자 세션 관리를 위한 Flask-Login

import time  # 시간 지연 처리
import requests  # HTTP 요청 처리
import pandas as pd  # 데이터 처리 (주로 DataFrame 사용)
# from sqlalchemy import create_engine  # SQLAlchemy 엔진을 사용하여 MySQL 연동
import os  # 운영 체제와의 상호작용 (파일 경로 등)
from datetime import timedelta
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'  # 고유한 비밀 키 설정

# 세션 유지 기간 설정 (선택 사항)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

# Bcrypt 인스턴스 생성
bcrypt = Bcrypt(app)

# ChromeDriver 경로 (프로젝트 내)
chrome_driver_path = 'webdriver/chromedriver.exe'

# 환경 변수에서 JAWSDB_URL 가져오기
db_url = "mysql://hau6sieypomd6xs2:nghsejnpxnillvft@jsk3f4rbvp8ayd7w.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/fyzws9bbv09772be"
url = urlparse(db_url)

# JawsDB MySQL 연결 설정
db_config = {
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'database': url.path[1:],  # URL 경로에서 '/'를 제거한 데이터베이스 이름
    'port': url.port
}

# MySQL 연결 테스트 (연결 확인)
def test_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        result = cursor.fetchall()
        print("Database connected. Tables:", result)
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# 로그인 관리 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 로그인 페이지로 리다이렉트 설정
login_manager.remember_cookie_duration = timedelta(days=7)  # 쿠키 세션 유지 기간 설정

# 사용자 클래스
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
# 사용자 등록 API
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    plain_password = request.form.get('password')

    # 비밀번호 해싱
    hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    # DB에 저장하는 로직 추가
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                   (username, hashed_password, 'admin'))  # 'admin' 역할로 저장
    conn.commit()
    cursor.close()
    conn.close()

    return "User registered successfully"


# 사용자 로드
@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return User(user['id'], user['username'], user['password'], user['role']) if user else None


# 로그인 페이지
# 로그인 페이지
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')
#
#         # 데이터베이스에서 사용자 조회
#         conn = mysql.connector.connect(**db_config)
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()
#
#         if user and bcrypt.check_password_hash(user['password'], password):
#             login_user(User(user['id'], user['username'], user['password'], user['role']), remember=True)
#
#             # 관리자 또는 매니저가 로그인 시 각각의 대시보드로 리다이렉트
#             if user['role'] == 'admin':
#                 return redirect(url_for('admin_dashboard'))
#             elif user['role'] == 'manager':
#                 return redirect(url_for('manager_dashboard', manager_id=user['id']))
#         else:
#             flash('Invalid username or password', 'danger')
#             return redirect(url_for('login'))
#
#     return render_template('login.html')

# 로그인 후 매니저 대시보드로 리디렉트
# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 데이터베이스에서 사용자 조회
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['password'], user['role']), remember=True)

            # 역할에 따른 리디렉트
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))  # 관리자는 admin 대시보드로
            elif user['role'] == 'manager':
                return redirect(url_for('manager_dashboard', manager_name=user['username']))  # 매니저 대시보드로
        else:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# 비밀번호 변경
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    new_password = request.form.get('new_password')

    # 비밀번호 해싱
    hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()



# @app.route('/manager_dashboard/<int:manager_id>')
# @login_required
# def manager_dashboard(manager_id):
#     # 관리자나 해당 담당자만 접근 가능하도록 설정
#     if current_user.role != 'admin' and current_user.id != manager_id:
#         return redirect(url_for('login'))  # 관리자가 아니면 로그인 페이지로 리다이렉트
#
#     # MySQL에서 해당 manager의 데이터를 가져옴
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     # 해당 담당자의 정보 가져오기
#     cursor.execute("SELECT * FROM users WHERE id = %s", (manager_id,))
#     manager = cursor.fetchone()
#
#     # 해당 담당자가 관리하는 tasks 또는 businesses 가져오기 (업무에 따라 변경 가능)
#     cursor.execute("SELECT * FROM businesses WHERE manager_id = %s", (manager_id,))
#     businesses = cursor.fetchall()
#
#     cursor.close()
#     conn.close()
#
#     # 디버깅용 출력
#     print(f"Manager: {manager}")
#     print(f"Businesses: {businesses}")
#
#     # manager_dashboard.html로 데이터 전달
#     return render_template('manager_dashboard.html', manager=manager, businesses=businesses)

# 관리자용: 특정 manager_id의 대시보드에 접근
# 매니저 대시보드 (관리자도 접근 가능)
# @app.route('/manager_dashboard/<string:manager_name>')
# @login_required
# def manager_dashboard(manager_name):
#     if current_user.role != 'manager' and current_user.username != manager_name and current_user.role != 'admin':
#         return redirect(url_for('login'))  # 접근 권한 확인
#
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     # 해당 manager_name과 연결된 businesses 가져오기
#     query = """
#         SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드,
#                k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력,
#                k.블로그리뷰, k.방문자리뷰, k.최신일자
#         FROM businesses b
#         JOIN keywords k ON b.플레이스번호 = k.플레이스번호
#         WHERE b.담당자 = %s
#     """
#     cursor.execute(query, (manager_name,))
#     businesses = cursor.fetchall()
#
#     cursor.close()
#     conn.close()
#
#     return render_template('manager_dashboard.html', businesses=businesses, manager_name=manager_name)

@app.route('/manager_dashboard/<string:manager_name>')
@login_required
def manager_dashboard(manager_name):
    # 접근 권한 확인: 매니저 본인 또는 관리자만 접근 가능
    if current_user.role != 'admin' and current_user.username != manager_name:
        return redirect(url_for('login'))  # 권한 없을 시 로그인 페이지로 리다이렉트

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 해당 manager_name과 연결된 businesses 정보 가져오기
    query = """
        SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
               k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, 
               k.블로그리뷰, k.방문자리뷰, k.최신일자
        FROM businesses b
        JOIN keywords k ON b.플레이스번호 = k.플레이스번호
        WHERE b.담당자 = %s
    """
    cursor.execute(query, (manager_name,))
    businesses = cursor.fetchall()

    cursor.close()
    conn.close()

    # manager_dashboard.html 템플릿으로 데이터 전달
    return render_template('manager_dashboard.html', businesses=businesses, manager_name=manager_name)


# 로그인된 매니저가 자신의 대시보드에 접근
@app.route('/my_dashboard')
@login_required
def my_dashboard():
    if current_user.role != 'manager':
        return redirect(url_for('login'))  # 매니저가 아닌 경우 로그인 페이지로 리디렉트

    # 현재 로그인된 manager가 관리하는 데이터 가져오기
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT DISTINCT b.id AS ID, k.등록일, k.상호명, k.플레이스번호, k.키워드, 
               k.카테고리, k.최초순위, k.최고순위, k.현재순위, k.담당자, k.변동이력, 
               k.블로그리뷰, k.방문자리뷰, k.최신일자
        FROM businesses b
        JOIN keywords k ON b.플레이스번호 = k.플레이스번호
        WHERE b.manager_id = %s
    """
    cursor.execute(query, (current_user.id,))
    keywords_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('manager_dashboard.html', businesses=keywords_data)




# 로그아웃
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()  # 로그아웃 처리
    return redirect(url_for('login'))  # 로그인 페이지로 리다이렉트


# SQLAlchemy를 사용하여 MySQL 데이터베이스 연결
# def get_sqlalchemy_engine():
#     engine = create_engine('mysql+mysqlconnector://root:1234@localhost/your_database_name')
#     return engine


# MySQL 연결
def get_db_connection():
    return mysql.connector.connect(**db_config)


# MySQL에서 데이터를 가져오는 함수
def fetch_data_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(""" 
        SELECT id, 등록일, 상호명, 플레이스번호, 키워드, 카테고리, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 블로그리뷰, 방문자리뷰, 최신일자 
        FROM keywords 
        ORDER BY id DESC  -- ID를 내림차순으로 정렬
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data



# 글로벌 드라이버 변수
driver = None


def setup_driver():
    global driver
    if driver is None:  # 드라이버가 없을 때만 생성
        service = Service(executable_path=chrome_driver_path)
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(service=service, options=options)
    return driver


def close_driver():
    global driver
    if driver is not None:
        driver.quit()
        driver = None


# 순위 찾기 함수
def find_rank(index, keyword, place_id):
    global driver  # 드라이버 변수를 글로벌로 선언

    if driver is None:  # 드라이버가 None일 경우 새로 생성
        service = Service(executable_path=chrome_driver_path)
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(service=service, options=options)

    try:
        search_link = f"https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}"
        driver.get(search_link)
        place_id_str = str(place_id)
        time.sleep(5)

        # 1. 리스트에서 더보기 없이 순위를 찾는 경우
        no_more_button_selector = "#loc-main-section-root > div > div.rdX0R > ul > li"
        list_items = driver.find_elements(By.CSS_SELECTOR, no_more_button_selector)
        if list_items:
            print(f"더보기 없이 리스트에서 {place_id_str}를 찾습니다.")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    if place_id_str in href:
                        print(f"{place_id_str}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1

        # 2. 첫 번째 더보기 버튼 클릭 후 순위를 찾는 경우
        try:
            driver.execute_script("window.scrollBy(0, 400);")  # 300px 정도 아래로 스크롤
            print("스크롤을 400px 내렸습니다.")
            click_more_button(driver, "a.YORrF span.Jtn42")  # 기존 CSS 선택자
            print("첫 번째 더보기 버튼 클릭됨 (a.YORrF span.Jtn42).")
            time.sleep(5)

            if not driver.find_elements(By.CSS_SELECTOR, "a.YORrF span.Jtn42"):
                click_more_button(driver, "a.FtXwJ span.PNozS")  # 새로운 선택자 사용
                print("첫 번째 더보기 버튼 클릭됨 (a.FtXwJ span.PNozS).")
                time.sleep(5)

            list_items = driver.find_elements(By.CSS_SELECTOR,
                                              "#place-main-section-root > div.place_section.Owktn > div.rdX0R.POx9H > ul > li")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    if place_id_str in href:
                        print(f"{place_id_str}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1
        except Exception as e:
            print(f"첫 번째 더보기 버튼 없음 또는 클릭 실패: {e}")

        # 3. 두 번째 더보기 버튼 클릭 후 순위를 찾는 경우
        try:
            click_more_button(driver, "a.cf8PL")
            print("두 번째 더보기 버튼 클릭됨.")
            time.sleep(5)

            list_items = driver.find_elements(By.CSS_SELECTOR, "#_list_scroll_container > div > div > div.place_business_list_wrapper > ul > li")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    if place_id_str in href:
                        print(f"{place_id_str}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1
        except Exception as e:
            print(f"두 번째 더보기 버튼 없음 또는 클릭 실패: {e}")

        print(f"{keyword}에서 {place_id}의 순위를 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"오류 발생: {e}")
        return None

    finally:
        if driver is not None:
            driver.quit()  # 크롤링이 끝난 후 브라우저 종료
            driver = None  # 드라이버를 None으로 초기화


# 카테고리 크롤링 함수
def get_category(driver, place_id):
    if driver is None:
        print("Driver is None, setting up driver again.")
        driver = setup_driver()  # 드라이버 재설정

    try:
        print(f"카테고리 크롤링을 위해 URL 접근 중: https://m.place.naver.com/nailshop/{place_id}/home?entry=pll")
        category_url = f"https://m.place.naver.com/nailshop/{place_id}/home?entry=pll"
        driver.get(category_url)
        time.sleep(5)

        # 카테고리 요소 찾기
        category_element = driver.find_element(By.CSS_SELECTOR, 'span.lnJFt')
        category = category_element.text
        print(f"카테고리 발견: {category}")
        return category

    except NoSuchElementException:
        print(f"카테고리를 찾을 수 없습니다. '미정'으로 설정됩니다. place_id: {place_id}")
        return "미정"

    except Exception as e:
        print(f"카테고리 로직에서 오류 발생: {e}")
        return "미정"


def get_reviews(place_id):
    global driver  # 글로벌 드라이버 변수 사용

    try:
        # 리뷰 페이지로 이동
        review_url = f"https://m.place.naver.com/nailshop/{place_id}/home?entry=pll"
        driver.get(review_url)
        time.sleep(5)  # 페이지 로딩 대기

        visitor_review_count = 0
        blog_review_count = 0

        try:
            # 첫 번째 케이스: 방문자 리뷰와 블로그 리뷰가 모두 있는 경우
            review_spans = driver.find_elements(By.CSS_SELECTOR, 'div.zD5Nm > div.dAsGb > span')

            first_review_text = review_spans[0].text
            if '방문자' in first_review_text:
                visitor_review_count = int(''.join(filter(str.isdigit, first_review_text)))
                print(f"방문자 리뷰 발견: {visitor_review_count}")

                if len(review_spans) > 1:
                    second_review_text = review_spans[1].text
                    blog_review_count = int(''.join(filter(str.isdigit, second_review_text)))
                    print(f"블로그 리뷰 발견: {blog_review_count}")
            else:
                blog_review_count = int(''.join(filter(str.isdigit, first_review_text)))
                print(f"블로그 리뷰 발견: {blog_review_count}")

        except NoSuchElementException:
            print("리뷰 요소를 찾을 수 없습니다. place_id={place_id}")

        return blog_review_count, visitor_review_count  # 리뷰 수 반환

    except Exception as e:
        print(f"리뷰 크롤링 중 오류 발생: {e}")
        return 0, 0  # 오류 발생 시 0으로 반환

    finally:
        if driver is not None:
            driver.quit()  # 크롤링이 끝난 후 브라우저 종료
            driver = None  # 드라이버를 None으로 초기화


def find_rank_and_reviews(index, keyword, place_id):
    rank = find_rank(index, keyword, place_id)
    if rank is not None:
        print(f"순위 {rank}를 찾았습니다. 이제 카테고리와 리뷰를 크롤링합니다.")

        # 카테고리 크롤링
        category = get_category(driver, place_id)
        print(f"카테고리: {category}")

        # 리뷰 크롤링
        blog_review, visitor_review = get_reviews(place_id)
        print(f"블로그 리뷰: {blog_review}, 방문자 리뷰: {visitor_review}")

        return rank, category, blog_review, visitor_review, index  # 5개의 값 반환
    else:
        print("순위를 찾지 못했습니다.")
    return None, '미정', 0, 0, index  # None일 때도 5개의 값 반환


def click_more_button(driver, selector):
    try:
        more_button = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script("arguments[0].click();", more_button)
        time.sleep(2)  # 클릭 후 페이지 로드 대기
    except NoSuchElementException:
        print(f"더보기 버튼 {selector}를 찾을 수 없습니다.")


# 순차적으로 크롤링 및 DB 업데이트 함수
def start_crawling_and_update_db():
    conn = get_db_connection()  # DB 연결
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM keywords WHERE id IS NOT NULL")
    rows = cursor.fetchall()

    try:
        for row in rows:
            try:
                # 반환값을 5개로 받도록 수정 (rank, category, blog_review, visitor_review, index)
                rank, category, blog_review, visitor_review, index = find_rank_and_reviews(row['id'], row['키워드'], row['플레이스번호'])

                if rank is not None:
                    # 데이터 재조회
                    cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
                    row = cursor.fetchone()

                    # 문자열로 된 순위 값을 정수로 변환
                    최고순위 = int(row['최고순위']) if row['최고순위'] is not None and row['최고순위'] != '' else 0
                    rank = int(rank)

                    # 최초순위 업데이트
                    if row['최초순위'] is None or row['최초순위'] == '':
                        cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

                    # 최고순위 업데이트 (정수 값으로 비교)
                    if row['최고순위'] is None or 최고순위 == 0 or rank < 최고순위:
                        최고순위 = rank

                    # 변동이력 계산 (정수 값으로 계산)
                    최초순위 = int(row['최초순위']) if row['최초순위'] is not None and row['최초순위'] != '' else 0
                    변동이력 = 최초순위 - rank  # 최초순위와 현재 순위 비교
                    변동이력_str = f"{변동이력}" if 변동이력 != 0 else "0"  # 변동이 0일 경우도 처리

                    now = datetime.now().strftime('%Y-%m-%d %H:%M')  # 현재 시간

                    # DB 업데이트
                    cursor.execute("""
                        UPDATE keywords 
                        SET 최고순위 = %s, 현재순위 = %s, 변동이력 = %s, 최신일자 = %s, 카테고리 = %s, 블로그리뷰 = %s, 방문자리뷰 = %s 
                        WHERE id = %s
                    """, (최고순위, rank, 변동이력_str, now, category, blog_review, visitor_review, index))

                    print(f"DB 업데이트 완료: {index}")

                else:
                    print(f"순위를 찾지 못함: index={index}")

            except Exception as e:
                print(f"DB 업데이트 중 오류 발생: {e}")
                conn.rollback()  # 오류 발생 시 해당 트랜잭션만 롤백

        conn.commit()  # 모든 작업 완료 후 한 번에 커밋

    except Exception as e:
        print(f"전체 처리 중 오류 발생: {e}")
        conn.rollback()

    finally:
        conn.close()  # 리소스 해제

    print("DB 업데이트 완료")

    # 크롤링 후 엑셀 파일 저장 (백업용)
    save_to_excel()


def save_to_excel():
    try:
        # mysql.connector를 통해 MySQL에서 데이터를 읽어옴
        conn = mysql.connector.connect(**db_config)
        query = "SELECT * FROM keywords"
        df = pd.read_sql(query, conn)  # pandas를 사용해 MySQL 데이터를 DataFrame으로 변환

        # 파일명에 날짜를 포함하여 백업 파일 생성
        now = datetime.now().strftime('%Y%m%d_%H%M%S')  # 날짜와 시간을 포함하여 고유한 파일명 생성
        excel_path = f"C:/workspace/rank_program/data/keywords_backup_{now}.xlsx"

        # 데이터프레임을 엑셀 파일로 저장
        df.to_excel(excel_path, index=False)

        print(f"엑셀 파일 저장 완료: {excel_path}")

        conn.close()  # MySQL 연결 종료

    except Exception as e:
        print(f"엑셀 파일 저장 오류: {e}")

# 예약 작업 추가
def schedule_crawling_task(hour, minute):
    scheduler.add_job(start_crawling_and_update_db, 'cron', hour=hour, minute=minute)
    scheduler.start()
    print(f"{hour}:{minute}에 크롤링 작업이 예약되었습니다.")


# 스케줄러 설정
scheduler = BackgroundScheduler()
schedule_crawling_task(1, 0)

# 순위 조회 후 업데이트 처리
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()

    # 'index' 값이 없는 경우 처리
    if 'index' not in data or not data['index']:
        return jsonify({'error': 'No index provided'}), 400

    try:
        # 'index' 값을 정수로 변환
        index = int(data['index'])
    except ValueError:
        return jsonify({'error': 'Invalid index value'}), 400

    # 나머지 입력 값 추출
    keyword = data.get('keyword')
    place_id = data.get('place_id')
    place_name = data.get('place_name')

    # MySQL 연결
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 데이터베이스에서 해당 'index' 값으로 검색
        cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
        row = cursor.fetchone()

        # 해당 'index' 값이 없을 때
        if row is None:
            return jsonify({'error': '순위가 110순위권 밖입니다.'}), 404

        # 순위, 카테고리, 리뷰 정보를 가져오는 함수 호출
        rank, category, blog_review, visitor_review, index = find_rank_and_reviews(index, keyword, place_id)

        # 순위가 존재할 경우 처리
        if rank is not None:
            # 최초 순위가 없으면 설정
            if row['최초순위'] is None or row['최초순위'] == '':
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            # 최고 순위를 업데이트 (현재 순위가 더 낮을 경우)
            최고순위 = int(row['최고순위']) if row['최고순위'] else 0
            rank = int(rank)

            if row['최고순위'] is None or 최고순위 == 0 or rank < 최고순위:
                최고순위 = rank

            # 변동 이력 계산
            이전순위 = int(row['현재순위']) if row['현재순위'] is not None and row['현재순위'] != '' else rank
            변동이력 = rank - 이전순위
            변동이력_str = f"+{변동이력}" if 변동이력 > 0 else str(변동이력)

            # 최신일자 업데이트
            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 현재순위, 최고순위, 변동이력, 최신일자, 카테고리, 리뷰 정보 업데이트
            cursor.execute("""
                UPDATE keywords 
                SET 현재순위 = %s, 최고순위 = %s, 변동이력 = %s, 최신일자 = %s, 카테고리 = %s, 블로그리뷰 = %s, 방문자리뷰 = %s 
                WHERE id = %s
            """, (rank, 최고순위, 변동이력_str, now, category, blog_review, visitor_review, index))

            # 변경 사항 커밋
            conn.commit()

            # 업데이트된 데이터를 JSON으로 반환
            return jsonify({
                'rank': rank,
                'category': category,
                'blog_review': blog_review,
                'visitor_review': visitor_review,
                'index': index
            })

        else:
            # 순위가 없을 경우
            return jsonify({'error': '순위가 110순위권 밖입니다.'}), 404

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500

    finally:
        # 데이터베이스 연결 종료
        conn.close()



# 메인 페이지 렌더링
# @app.route('/')
# def index():
#     data = fetch_data_from_db()  # MySQL에서 데이터를 가져옴
#     return render_template('index.html', data=data)  # index.html 템플릿을 렌더링

# 메인 페이지 렌더링
@app.route('/')
def main():
    if current_user.is_authenticated:  # 사용자가 로그인된 상태라면
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))  # 관리자 대시보드로 리다이렉트
        else:
            return redirect(url_for('manager_dashboard', manager_name=current_user.username))  # 영업자 대시보드로 리다이렉트
    else:
        return redirect(url_for('login'))  # 로그인되지 않았다면 로그인 페이지로 리다이렉트


# 순위 조회 API
@app.route('/get_rank', methods=['POST'])
def get_rank():
    data = request.get_json()

    place_name = data.get('place_name')
    place_id = data.get('place_id')
    keyword = data.get('keyword')

    rank, category, blog_review, visitor_review, index = find_rank_and_reviews(0, keyword, place_id)

    if rank is not None:
        return jsonify({
            'rank': rank,
            'category': category,
            'blog_review': blog_review,
            'visitor_review': visitor_review
        })
    else:
        return jsonify({'error': '순위가 110순위권 밖입니다.'}), 404


# 실시간 검색 페이지 렌더링
@app.route('/search')
def search():
    return render_template('search.html', is_admin=current_user.role == 'admin')

@app.route('/manager_management')
@login_required
def manager_management():
    if current_user.role != 'admin':
        return redirect(url_for('login'))  # 관리자가 아니면 로그인 페이지로 리다이렉트

    # MySQL 연결 및 'users' 테이블에서 중복 없는 'username'과 'password' 데이터 가져오기
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 'manager' 역할을 가진 사용자만 가져오기
    cursor.execute("SELECT id, username, password FROM users WHERE role = 'manager'")
    managers = cursor.fetchall()

    cursor.close()
    conn.close()

    # 관리자 데이터를 템플릿으로 전달
    return render_template('manager_management.html', managers=managers)

@app.route('/delete_manager/<int:manager_id>', methods=['DELETE'])
@login_required
def delete_manager(manager_id):
    # 관리자가 아닌 사용자는 삭제 불가
    if current_user.role != 'admin':
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 관리자가 담당하고 있는 업무는 그대로 유지되므로 businesses 테이블은 건드리지 않음
        # users 테이블에서 관리자를 삭제
        cursor.execute("DELETE FROM users WHERE id = %s AND role = 'manager'", (manager_id,))
        conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# @app.route('/create_manager_account', methods=['POST'])
# @login_required
# def create_manager_account():
#     if current_user.role != 'admin':
#         return jsonify({'error': 'Unauthorized access'}), 403
#
#     data = request.get_json()
#     manager_id = data.get('id')
#     username = data.get('username')
#     password = data.get('password')
#
#     if not username or not password:
#         return jsonify({'error': 'Username and password required'}), 400
#
#     hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         # 특정 관리자의 계정을 업데이트 또는 새로 생성
#         cursor.execute("UPDATE users SET username = %s, password = %s WHERE id = %s AND role = 'manager'",
#                        (username, hashed_password, manager_id))
#         conn.commit()
#         return jsonify({'success': True})
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'error': str(e)})
#     finally:
#         cursor.close()
#         conn.close()
@app.route('/create_manager_account', methods=['POST'])
@login_required
def create_manager_account():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Invalid input'}), 400

    # 비밀번호 해싱
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 새로운 매니저 계정 추가
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'manager')",
                       (username, hashed_password))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


# 관리자 추가 API
@app.route('/add_manager', methods=['POST'])
@login_required
def add_manager():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Invalid input'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'manager')",
                       (username, hashed_password))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()




# 데이터베이스 연결 테스트 API
@app.route('/test_db_connection')
def test_db_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        cursor.close()
        conn.close()

        return f"MySQL 연결 성공! 현재 데이터베이스: {db_name[0]}"
    except mysql.connector.Error as err:
        return f"MySQL 연결 실패: {err}"


@app.route('/add_row', methods=['POST'])
def add_row():
    data = request.get_json()

    new_date = data.get('date')
    place_name = data.get('place_name')
    place_id = data.get('place_id')
    keyword = data.get('keyword')
    manager = data.get('manager')
    current_rank = data.get('current_rank')

    print(f"Received data: {data}")

    try:
        # MySQL 연결
        conn = get_db_connection()
        cursor = conn.cursor()

        # Step 1: 새로운 데이터를 마지막 ID로 삽입 (AUTO_INCREMENT를 이용하여 자동으로 ID 할당)
        cursor.execute(""" 
            INSERT INTO keywords (등록일, 상호명, 플레이스번호, 키워드, 현재순위, 담당자) 
            VALUES (%s, %s, %s, %s, %s, %s) 
        """, (new_date, place_name, place_id, keyword, current_rank, manager))

        conn.commit()

        # Step 2: 새로 추가된 데이터의 ID 가져오기
        cursor.execute("SELECT LAST_INSERT_ID()")
        new_id = cursor.fetchone()[0]  # 새로운 ID 값

        return jsonify({'success': True, 'new_id': new_id})
    except Exception as e:
        conn.rollback()
        print(f"Error adding new row: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/add_business', methods=['POST'])
def add_business():
    data = request.get_json()

    name = data.get('name')
    manager_id = data.get('manager_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 중복 확인: 플레이스번호와 키워드를 기준으로 중복을 확인
    check_query = """
        SELECT * FROM businesses b
        JOIN keywords k ON b.플레이스번호 = k.플레이스번호
        WHERE k.키워드 = %s AND k.플레이스번호 = %s
    """
    cursor.execute(check_query, (data.get('keyword'), data.get('place_id')))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # 중복된 데이터가 있으면 추가하지 않고 메시지 반환
        cursor.close()
        conn.close()
        return jsonify({'error': 'Duplicate entry found, business not added.'}), 409

    # 중복이 없으면 새로운 business 추가
    insert_query = "INSERT INTO businesses (name, manager_id) VALUES (%s, %s)"
    cursor.execute(insert_query, (name, manager_id))

    # 플레이스번호 연동
    update_query = """
        UPDATE businesses b
        JOIN keywords k ON b.name = k.상호명
        SET b.플레이스번호 = k.플레이스번호
        WHERE b.name = %s
    """
    cursor.execute(update_query, (name,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'success': 'Business added successfully!'})


# def create_admin_user():
#     username = "root"
#     plain_password = "1234"  # 실제 비밀번호
#     hashed_password = bcrypt.generate_password_hash(plain_password).decode('utf-8')
#
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
#                    (username, hashed_password, 'admin'))
#     conn.commit()
#     cursor.close()
#     conn.close()
#
#     print("Admin user created successfully.")

@app.route('/check_hash', methods=['GET'])
def check_hash():
    plain_password = "1234"  # 원래 비밀번호
    hashed_password = "$2b$12$ZuGXrXZF4CJScpFKacQVRenXEVpqS/4J/keimfTPn1soOLl5IFEU2"  # 해시된 비밀번호
    if bcrypt.check_password_hash(hashed_password, plain_password):
        return "Password is valid!"
    else:
        return "Invalid password."


# Admin Dashboard 라우트
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':  # 관리자가 아닌 경우
        return redirect(url_for('login'))  # 로그인 페이지로 리다이렉트
    data = fetch_data_from_db()  # 데이터베이스에서 데이터 가져오기
    return render_template('admin_dashboard.html', data=data)



@app.route('/check_rank', methods=['POST'])
def check_rank():
    return jsonify({'message': 'Rank checked successfully'})


# 키워드 삭제 라우트
@app.route('/delete_keyword', methods=['POST'])
@login_required
def delete_keyword():
    data = request.get_json()
    keyword_id = data.get('id')

    if not keyword_id:
        return jsonify({'error': 'No keyword ID provided'}), 400

    try:
        # DB 연결
        conn = get_db_connection()
        cursor = conn.cursor()

        # 해당 키워드를 DB에서 삭제
        cursor.execute("DELETE FROM keywords WHERE id = %s", (keyword_id,))
        conn.commit()

        return jsonify({'success': True, 'message': 'Keyword deleted successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# 담당자 등록
# def register_managers():
#     managers = [
#         {'username': '오경주', 'password': 'password1', 'role': 'manager'},
#         {'username': '한시은', 'password': 'password2', 'role': 'manager'},
#         {'username': '박찬규', 'password': 'password3', 'role': 'manager'},
#         {'username': '김주성', 'password': 'password4', 'role': 'manager'},
#         {'username': '서지우', 'password': 'password5', 'role': 'manager'},
#         {'username': '심재진', 'password': 'password6', 'role': 'manager'},
#     ]
#
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#
#     for manager in managers:
#         hashed_password = bcrypt.generate_password_hash(manager['password']).decode('utf-8')
#         cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
#                        (manager['username'], hashed_password, manager['role']))
#
#     conn.commit()
#     cursor.close()
#     conn.close()
#
#     print("All managers have been registered successfully.")
#
# # 등록 함수 호출
# register_managers()


# @app.route('/test_password', methods=['GET'])
# def test_password():
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT password FROM users WHERE username = '오경주'")
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
#
#     # '오경주'라는 텍스트가 데이터베이스에 저장된 해싱된 비밀번호와 일치하는지 확인
#     if bcrypt.check_password_hash(user['password'], '오경주'):
#         return "Password is valid!"
#     else:
#         return "Invalid password."

# @app.route('/reset_password', methods=['GET'])
# def reset_password():
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor()
#
#     # 새로운 비밀번호를 해싱
#     hashed_password = bcrypt.generate_password_hash('오경주').decode('utf-8')
#
#     # 비밀번호를 다시 업데이트
#     cursor.execute("UPDATE users SET password = %s WHERE username = '오경주'", (hashed_password,))
#     conn.commit()
#
#     cursor.close()
#     conn.close()
#
#     return "Password reset successfully!"


if __name__ == '__main__':
    test_db_connection()  # MySQL 연결 확인
    app.run(debug=True)