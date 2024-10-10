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

from flask import Flask, render_template, redirect, url_for, flash, request, session  # Flask 웹 프레임워크 기본 모듈
from flask_bcrypt import Bcrypt  # 비밀번호 해싱 및 검증을 위한 Bcrypt 모듈
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required  # 사용자 세션 관리를 위한 Flask-Login

import time  # 시간 지연 처리
import requests  # HTTP 요청 처리
import pandas as pd  # 데이터 처리 (주로 DataFrame 사용)
from sqlalchemy import create_engine  # SQLAlchemy 엔진을 사용하여 MySQL 연동
import os  # 운영 체제와의 상호작용 (파일 경로 등)

app = Flask(__name__)

# ChromeDriver 경로 (프로젝트 내)
chrome_driver_path = 'webdriver/chromedriver.exe'

# MySQL 연결 설정
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'your_database_name'
}

# 로그인 관리 설정
login_manager = LoginManager(app)
login_manager.login_view = 'login'


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


# 사용자 클래스
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role


# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            login_user(User(user['id'], user['username'], user['password'], user['role']))
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('manager_dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')


# 관리자 대시보드
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE role = 'manager'")
    managers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', managers=managers)


# 비밀번호 변경
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Password updated successfully!', 'success')
        return redirect(url_for('manager_dashboard'))

    return render_template('change_password.html')


# 담당자 대시보드
@app.route('/manager_dashboard')
@login_required
def manager_dashboard():
    if current_user.role != 'manager':
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM businesses WHERE manager_id = %s", (current_user.id,))
    businesses = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('manager_dashboard.html', businesses=businesses)


# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


# SQLAlchemy를 사용하여 MySQL 데이터베이스 연결
def get_sqlalchemy_engine():
    engine = create_engine('mysql+mysqlconnector://root:1234@localhost/your_database_name')
    return engine

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

# 이제 필요할 때 driver를 생성하고 마지막에만 종료


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
            # 스크롤을 약간 내리는 코드 추가
            driver.execute_script("window.scrollBy(0, 400);")  # 300px 정도 아래로 스크롤
            print("스크롤을 400px 내렸습니다.")

            # 첫 번째 더보기 버튼을 찾기 위한 CSS 선택자 두 개를 사용
            click_more_button(driver, "a.YORrF span.Jtn42")  # 기존 CSS 선택자
            print("첫 번째 더보기 버튼 클릭됨 (a.YORrF span.Jtn42).")
            time.sleep(5)

            # 만약 첫 번째 선택자에서 버튼을 찾지 못하면 class="FtXwJ"로 시도
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
            # div.dAsGb > span:nth-child(1)와 span:nth-child(2)를 모두 가져옴
            review_spans = driver.find_elements(By.CSS_SELECTOR, 'div.zD5Nm > div.dAsGb > span')

            # 첫 번째 span의 텍스트에 '방문자'가 있으면 방문자 리뷰, 그렇지 않으면 블로그 리뷰로 처리
            first_review_text = review_spans[0].text
            if '방문자' in first_review_text:
                # 방문자 리뷰로 처리
                visitor_review_count = int(''.join(filter(str.isdigit, first_review_text)))
                print(f"방문자 리뷰 발견: {visitor_review_count}")

                # 두 번째 span은 블로그 리뷰
                if len(review_spans) > 1:
                    second_review_text = review_spans[1].text
                    blog_review_count = int(''.join(filter(str.isdigit, second_review_text)))
                    print(f"블로그 리뷰 발견: {blog_review_count}")
            else:
                # 첫 번째 span은 블로그 리뷰로 처리
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
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM keywords WHERE id IS NOT NULL")
    rows = cursor.fetchall()

    try:
        for row in rows:
            try:
                # 반환값을 5개로 받도록 수정
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
                    이전순위 = int(row['현재순위']) if row['현재순위'] is not None and row['현재순위'] != '' else rank
                    변동이력 = rank - 이전순위
                    변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

                    now = datetime.now().strftime('%Y-%m-%d %H:%M')

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


# 엑셀 파일로 저장하는 함수
def save_to_excel():
    try:
        # SQLAlchemy 엔진을 통해 MySQL에서 데이터를 읽어옴
        engine = get_sqlalchemy_engine()

        # MySQL에서 데이터 가져오기 (DataFrame 형태)
        df = pd.read_sql('SELECT * FROM keywords', engine)

        # 파일명에 날짜를 포함하여 백업 파일 생성
        now = datetime.now().strftime('%Y%m%d_%H%M%S')  # 날짜와 시간을 포함하여 고유한 파일명 생성
        excel_path = f"C:/workspace/rank_program/data/keywords_backup_{now}.xlsx"

        # 데이터프레임을 엑셀 파일로 저장
        df.to_excel(excel_path, index=False)

        print(f"엑셀 파일 저장 완료: {excel_path}")

        # SQLAlchemy 엔진 종료
        engine.dispose()

    except Exception as e:
        print(f"엑셀 파일 저장 오류: {e}")

# 예약 작업 추가
def schedule_crawling_task(hour, minute):
    scheduler.add_job(start_crawling_and_update_db, 'cron', hour=hour, minute=minute)
    scheduler.start()
    print(f"{hour}:{minute}에 크롤링 작업이 예약되었습니다.")

# 스케줄러 설정
scheduler = BackgroundScheduler()
schedule_crawling_task(20,13)

# 순위 조회 후 업데이트 처리
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()

    if 'index' not in data:
        return jsonify({'error': 'No index provided'}), 400

    index = int(data['index'])
    keyword = data['keyword']
    place_id = data['place_id']
    place_name = data.get('place_name')  # place_name 추가

    # MySQL 연결 및 데이터 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # index 값을 통해 데이터베이스에서 데이터 조회
        cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({'error': 'No data found for the given index.'}), 404

        # 순위와 리뷰를 가져오는 함수 호출
        rank, category, blog_review, visitor_review, index = find_rank_and_reviews(index, keyword, place_id)

        if rank is not None:
            # 최초순위가 없으면 최초순위로 설정
            if row['최초순위'] is None or row['최초순위'] == '':
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            # 최고순위가 없거나 현재순위가 최고순위보다 높으면 최고순위 업데이트
            최고순위 = int(row['최고순위']) if row['최고순위'] else 0
            rank = int(rank)

            if row['최고순위'] is None or 최고순위 == 0 or rank < 최고순위:
                최고순위 = rank

            # 변동이력 계산
            이전순위 = int(row['현재순위']) if row['현재순위'] is not None and row['현재순위'] != '' else rank
            변동이력 = rank - 이전순위
            변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

            # 최신일자 업데이트
            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 현재순위, 최고순위, 변동이력, 최신일자, 카테고리, 리뷰 업데이트
            cursor.execute("""
                UPDATE keywords
                SET 현재순위 = %s, 최고순위 = %s, 변동이력 = %s, 최신일자 = %s, 카테고리 = %s, 블로그리뷰 = %s, 방문자리뷰 = %s
                WHERE id = %s
            """, (rank, 최고순위, 변동이력_str, now, category, blog_review, visitor_review, index))

            conn.commit()

            # 커밋 후 업데이트된 데이터를 응답으로 반환
            return jsonify({
                'rank': rank,
                'category': category,
                'blog_review': blog_review,
                'visitor_review': visitor_review,
                'index': index
            })

        else:
            return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    finally:
        conn.close()


# 메인 페이지 렌더링
@app.route('/')
def index():
    data = fetch_data_from_db()  # MySQL에서 데이터를 가져옴
    return render_template('index.html', data=data)  # index.html 템플릿을 렌더링

# 실시간 검색 페이지 렌더링
@app.route('/search')
def search_page():
    return render_template('search.html')

# 순위 조회 API
@app.route('/get_rank', methods=['POST'])
def get_rank():
    data = request.get_json()

    place_name = data.get('place_name')
    place_id = data.get('place_id')
    keyword = data.get('keyword')

    index, rank, category, blog_review, visitor_review = find_rank_and_reviews(0, keyword, place_id)

    if rank is not None:
        return jsonify({'rank': rank})
    else:
        return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

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

# 새로운 데이터 추가 API
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

        # 새로운 데이터 추가 (id는 AUTO_INCREMENT로 자동 설정)
        cursor.execute("""
            INSERT INTO keywords (등록일, 상호명, 플레이스번호, 키워드, 현재순위, 담당자)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (new_date, place_name, place_id, keyword, current_rank, manager))

        conn.commit()

        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        print(f"Error adding new row: {e}")
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()




if __name__ == '__main__':
    app.run(debug=True)
