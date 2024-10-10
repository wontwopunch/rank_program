from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import shutil

app = Flask(__name__)

# 엑셀 파일 읽기 (파일 경로를 프로그램 내 엑셀 경로로 지정)
df = pd.read_excel('C:/workspace/rank_program/data/keywords.xlsx')

# # 데이터 확인
# print(df.head())

# ChromeDriver 경로 (프로젝트 내)
chrome_driver_path = 'webdriver/chromedriver.exe'

# MySQL 연결 설정
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'your_database_name'
}

# MySQL 연결
def get_db_connection():
    return mysql.connector.connect(**db_config)

# MySQL에서 데이터를 가져오는 함수
def fetch_data_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, 등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 최신일자 FROM keywords")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# def insert_data_from_excel():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#
#     insert_query = """
#     INSERT INTO keywords ( 등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 최신일자)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#
#     for index, row in df.iterrows():
#         cursor.execute(insert_query, (
#             row['등록일'], row['상호명'], row['플레이스번호'], row['키워드'],
#             row['최초순위'], row['최고순위'], row['현재순위'], row['담당자'],
#             row['변동이력'], row['최신일자']
#         ))
#
#     conn.commit()  # 커밋하여 DB에 변경사항 반영
#     cursor.close()
#     conn.close()
#     print("엑셀 데이터 삽입 완료")


# 메인 페이지 라우팅
@app.route('/')
def index():
    data = fetch_data_from_db()  # MySQL에서 데이터를 가져옴
    return render_template('index.html', data=data)  # 데이터를 템플릿에 전달

# 글로벌 드라이버 변수
driver = None

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
            click_more_button(driver, "a.YORrF span.Jtn42")
            print("첫 번째 더보기 버튼 클릭됨.")
            time.sleep(5)

            list_items = driver.find_elements(By.CSS_SELECTOR, "#place-main-section-root > div.place_section.Owktn > div.rdX0R.POx9H > ul > li")
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

# 더보기 버튼 클릭 함수
# 네트워크 속도에 맞춰 대기 시간을 조정하는 함수
def click_more_button(driver, css_selector, timeout=30):
    try:
        # 버튼이 나타날 때까지 기다림 (최대 timeout 초 대기)
        more_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        driver.execute_script("arguments[0].scrollIntoView(true);", more_element)  # 요소를 화면에 스크롤
        time.sleep(2)  # 약간의 대기 시간 추가
        driver.execute_script("arguments[0].click();", more_element)  # 클릭
        print(f"더보기 버튼 ({css_selector}) 클릭됨.")
        time.sleep(5)  # 네트워크 대기 시간 고려
    except Exception as e:
        print(f"더보기 버튼 클릭 실패: {e}")

# 크롤링 작업을 수행하는 함수 (DB 업데이트)
def start_crawling_and_update_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # MySQL 데이터에서 순차 크롤링 진행
    cursor.execute("SELECT * FROM keywords")
    rows = cursor.fetchall()

    for row in rows:
        index = row['id']
        keyword = row['키워드']
        place_id = row['플레이스번호']
        rank = find_rank(index, keyword, place_id)

        if rank is not None:
            # 최초순위 설정
            if row['최초순위'] is None:
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            # 최고순위 업데이트
            if row['최고순위'] is None or rank < row['최고순위']:
                cursor.execute("UPDATE keywords SET 최고순위 = %s WHERE id = %s", (rank, index))

            # 현재 순위 및 변동이력 업데이트
            최고순위 = row['최고순위'] if row['최고순위'] is not None else rank
            변동이력 = rank - 최고순위  # 최고순위와 현재순위(새로운 rank) 비교
            변동이력_str = f"+{변동이력}" if 변동이력 < 0 else f"-{abs(변동이력)}"  # 부호 적용

            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            cursor.execute(""" 
                UPDATE keywords
                SET 현재순위 = %s, 변동이력 = %s, 최신일자 = %s
                WHERE id = %s
            """, (rank, 변동이력_str, now, index))

    conn.commit()
    conn.close()
    print("DB 업데이트 완료")

# 예약 작업 추가
def schedule_crawling_task(hour, minute):
    scheduler.add_job(start_crawling_and_update_db, 'cron', hour=hour, minute=minute)
    scheduler.start()
    print(f"{hour}:{minute}에 크롤링 작업이 예약되었습니다.")

# 스케줄러 설정
scheduler = BackgroundScheduler()
schedule_crawling_task(23, 17)

# 순위 조회 후 업데이트 처리
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()

    if 'index' not in data:
        return jsonify({'error': 'No index provided'}), 400

    index = int(data['index'])
    keyword = data['keyword']
    place_id = data['place_id']

    # MySQL 연결 및 데이터 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # index 값을 통해 데이터베이스에서 데이터 조회
        cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({'error': 'No data found for the given index.'}), 404

        # 순위 계산 로직
        rank = find_rank(index, keyword, place_id)

        if rank is not None:
            # 최초순위, 최고순위, 현재순위, 변동이력 업데이트
            if row['최초순위'] is None:
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            if row['최고순위'] is None or rank < row['최고순위']:
                cursor.execute("UPDATE keywords SET 최고순위 = %s WHERE id = %s", (rank, index))

            이전순위 = row['현재순위'] if row['현재순위'] is not None else rank
            변동이력 = rank - 이전순위
            변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 현재순위 및 최신일자 업데이트
            print(f"Updating: 현재순위={rank}, 변동이력={변동이력_str}, 최신일자={now}")  # 로그 추가
            cursor.execute("""
                UPDATE keywords
                SET 현재순위 = %s, 변동이력 = %s, 최신일자 = %s
                WHERE id = %s
            """, (rank, 변동이력_str, now, index))

            conn.commit()  # 변경 사항 저장
            return jsonify({'rank': rank})
        else:
            return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    finally:
        conn.close()


@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/get_rank', methods=['POST'])
def get_rank():
    data = request.get_json()

    place_name = data.get('place_name')
    place_id = data.get('place_id')
    keyword = data.get('keyword')

    rank = find_rank(0, keyword, place_id)

    if rank is not None:
        return jsonify({'rank': rank})
    else:
        return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

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

if __name__ == '__main__':
    # insert_data_from_excel()
    app.run(debug=True)














# 2

from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import shutil

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

# MySQL 연결
def get_db_connection():
    return mysql.connector.connect(**db_config)

# MySQL에서 데이터를 가져오는 함수
def fetch_data_from_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, 등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 최신일자 FROM keywords")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# 메인 페이지 라우팅
@app.route('/')
def index():
    data = fetch_data_from_db()  # MySQL에서 데이터를 가져옴
    return render_template('index.html', data=data)  # 데이터를 템플릿에 전달

# 글로벌 드라이버 변수
driver = None

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
            click_more_button(driver, "a.YORrF span.Jtn42")
            print("첫 번째 더보기 버튼 클릭됨.")
            time.sleep(5)

            list_items = driver.find_elements(By.CSS_SELECTOR, "#place-main-section-root > div.place_section.Owktn > div.rdX0R.POx9H > ul > li")
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

        # 3. 두 번째 더보기 버튼 클릭 후 스크롤을 끝까지 내리면서 순위를 찾는 경우
        try:
            click_more_button(driver, "a.cf8PL")
            print("두 번째 더보기 버튼 클릭됨.")
            time.sleep(5)

            # 스크롤 끝까지 내리면서 ID를 찾기 위한 반복
            rank = 1
            last_height = driver.execute_script("return document.body.scrollHeight")  # 현재 페이지 높이
            while True:
                # 현재 화면에 표시된 목록 아이템들 확인
                list_items = driver.find_elements(By.CSS_SELECTOR,
                                                  "#_list_scroll_container > div > div > div.place_business_list_wrapper > ul > li")

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

                # 페이지 끝까지 스크롤
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # 스크롤 후 대기 시간 추가

                # 새로운 페이지 높이를 가져옴
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break  # 더 이상 스크롤할 내용이 없으면 종료
                last_height = new_height

            print(f"{keyword}에서 {place_id}의 순위를 찾을 수 없습니다.")
            return None

        except Exception as e:
            print(f"두 번째 더보기 버튼 없음 또는 클릭 실패: {e}")
            return None

    finally:
        if driver is not None:
            driver.quit()  # 크롤링이 끝난 후 브라우저 종료
            driver = None  # 드라이버를 None으로 초기화

# 더보기 버튼 클릭 함수
def click_more_button(driver, css_selector, timeout=30):
    try:
        # 버튼이 나타날 때까지 기다림 (최대 timeout 초 대기)
        more_element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        driver.execute_script("arguments[0].scrollIntoView(true);", more_element)  # 요소를 화면에 스크롤
        time.sleep(2)  # 약간의 대기 시간 추가
        driver.execute_script("arguments[0].click();", more_element)  # 클릭
        print(f"더보기 버튼 ({css_selector}) 클릭됨.")
        time.sleep(5)  # 네트워크 대기 시간 고려
    except Exception as e:
        print(f"더보기 버튼 클릭 실패: {e}")


# 크롤링 작업을 수행하는 함수 (DB 업데이트)
def start_crawling_and_update_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # MySQL 데이터에서 순차 크롤링 진행
    cursor.execute("SELECT * FROM keywords")
    rows = cursor.fetchall()

    for row in rows:
        index = row['id']
        keyword = row['키워드']
        place_id = row['플레이스번호']
        rank = find_rank(index, keyword, place_id)

        if rank is not None:
            # 최초순위 설정
            if row['최초순위'] is None or row['최초순위'] == 0:
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            # 최고순위 업데이트
            if row['최고순위'] is None or row['최고순위'] == 0 or rank < row['최고순위']:
                최고순위 = rank
                cursor.execute("UPDATE keywords SET 최고순위 = %s WHERE id = %s", (rank, index))
            else:
                최고순위 = row['최고순위']

            # 현재 순위 및 변동이력 업데이트
            이전순위 = row['현재순위'] if row['현재순위'] is not None else rank
            변동이력 = rank - 이전순위

            # 부호 적용: 양수일 때는 "+" 표시, 음수일 때는 "-" 표시
            if 변동이력 > 0:
                변동이력_str = f"+{변동이력}"
            elif 변동이력 < 0:
                변동이력_str = f"{변동이력}"  # 음수는 자동으로 "-" 표시됨
            else:
                변동이력_str = "0"  # 변동이 없을 때는 "0" 표시

            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            cursor.execute("""
                UPDATE keywords
                SET 현재순위 = %s, 변동이력 = %s, 최신일자 = %s
                WHERE id = %s
            """, (rank, 변동이력_str, now, index))

    conn.commit()
    conn.close()
    print("DB 업데이트 완료")

    # 크롤링 후 엑셀 파일 저장
    save_to_excel()

# 엑셀 파일로 저장하는 함수
def save_to_excel():
    conn = get_db_connection()
    df = pd.read_sql('SELECT * FROM keywords', conn)
    now = datetime.now().strftime('%Y%m%d')
    excel_path = f"C:/workspace/rank_program/data/keywords_{now}.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"엑셀 파일 저장 완료: {excel_path}")
    conn.close()

# 예약 작업 추가
def schedule_crawling_task(hour, minute):
    scheduler.add_job(start_crawling_and_update_db, 'cron', hour=hour, minute=minute)
    scheduler.start()
    print(f"{hour}:{minute}에 크롤링 작업이 예약되었습니다.")

# 스케줄러 설정
scheduler = BackgroundScheduler()
schedule_crawling_task(12, 30)

# 순위 조회 후 업데이트 처리
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()

    if 'index' not in data:
        return jsonify({'error': 'No index provided'}), 400

    index = int(data['index'])
    keyword = data['keyword']
    place_id = data['place_id']

    # MySQL 연결 및 데이터 조회
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # index 값을 통해 데이터베이스에서 데이터 조회
        cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({'error': 'No data found for the given index.'}), 404

        # 순위 계산 로직
        rank = find_rank(index, keyword, place_id)

        if rank is not None:
            # 최초순위, 최고순위, 현재순위, 변동이력 업데이트
            if row['최초순위'] is None:
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            if row['최고순위'] is None or rank < row['최고순위']:
                cursor.execute("UPDATE keywords SET 최고순위 = %s WHERE id = %s", (rank, index))

            이전순위 = row['현재순위'] if row['현재순위'] is not None else rank
            변동이력 = rank - 이전순위
            변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 현재순위 및 최신일자 업데이트
            print(f"Updating: 현재순위={rank}, 변동이력={변동이력_str}, 최신일자={now}")  # 로그 추가
            cursor.execute("""
                UPDATE keywords
                SET 현재순위 = %s, 변동이력 = %s, 최신일자 = %s
                WHERE id = %s
            """, (rank, 변동이력_str, now, index))

            conn.commit()  # 변경 사항 저장
            return jsonify({'rank': rank})
        else:
            return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    finally:
        conn.close()


@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/get_rank', methods=['POST'])
def get_rank():
    data = request.get_json()

    place_name = data.get('place_name')
    place_id = data.get('place_id')
    keyword = data.get('keyword')

    rank = find_rank(0, keyword, place_id)

    if rank is not None:
        return jsonify({'rank': rank})
    else:
        return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

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

if __name__ == '__main__':
    app.run(debug=True)

