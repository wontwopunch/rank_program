from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from urllib.parse import quote
from fake_useragent import UserAgent
import pandas as pd
from sqlalchemy import create_engine
import os

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
    cursor.execute("SELECT id, 등록일, 상호명, 플레이스번호, 키워드, 최초순위, 최고순위, 현재순위, 담당자, 변동이력, 최신일자 FROM keywords")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# ChromeDriver 설정에 타임아웃 추가
def setup_driver():
    service = Service(executable_path=chrome_driver_path)
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--headless')  # 필요시 headless 모드 사용
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(300)  # 300초 타임아웃 설정
    return driver


# def fetch_places_data(keyword, start):
#     ua = UserAgent()
#     # URL에 있는 한글을 URL 인코딩
#     encoded_keyword = quote(keyword)
#     url = f"https://m.place.naver.com/place/list?query={encoded_keyword}&start={start}&display=100"
#
#     headers = {
#         "User-Agent": ua.random,  # 랜덤한 User-Agent
#         "Accept": "application/json",
#         "Referer": f"https://m.place.naver.com/place/list?query={encoded_keyword}"
#     }
#
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to fetch data: {e}")
#         return None
#
#
# # 예시로 사용
# keyword = "강남청소"
# start = 1
#
# # 여러 페이지에 걸쳐 데이터를 크롤링
# for i in range(10):
#     data = fetch_places_data(keyword, start)
#     if data:
#         # 데이터를 사용해 필요한 정보 추출
#         print(data)
#     else:
#         break
#
#     # 각 요청 사이에 10초 대기
#     time.sleep(10)
#
#     # 다음 페이지로 이동
#     start += 100


def crawl_all_data(keyword, max_pages=10):
    all_data = []
    start = 1

    for i in range(max_pages):
        data = fetch_places_data(keyword, start)
        if data:
            all_data.extend(data["places"])  # "places"는 응답 데이터 구조에 맞게 수정해야 합니다.
        else:
            break

        start += 100  # start 값을 페이지 단위로 증가

    return all_data


# 예시로 사용
keyword = "강남청소"
all_places = crawl_all_data(keyword)
print(all_places)

# 크롤링 함수
# def find_rank(index, keyword, place_id):
#     driver = setup_driver()  # setup_driver()를 사용하여 드라이버 설정
#     try:
#         print(f"크롤링 시작: index={index}, keyword={keyword}, place_id={place_id}")
#
#         search_link = f"https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}"
#         driver.get(search_link)
#         print(f"검색 페이지 로드 완료: {search_link}")
#         place_id_str = str(place_id)
#
#         # 페이지가 완전히 로드될 때까지 기다림
#         WebDriverWait(driver, 20).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#loc-main-section-root"))
#         )
#
#         # 1. 리스트에서 더보기 없이 순위를 찾는 경우
#         no_more_button_selector = "#loc-main-section-root > div > div.rdX0R > ul > li"
#         list_items = driver.find_elements(By.CSS_SELECTOR, no_more_button_selector)
#         if list_items:
#             print(f"리스트에서 찾기 시작: {place_id_str}")
#             rank = 1
#             for item in list_items:
#                 try:
#                     link = item.find_element(By.CSS_SELECTOR, "a")
#                     href = link.get_attribute("href")
#                     if place_id_str in href:
#                         print(f"리스트에서 순위 발견: {href}, 현재 순위: {rank}")
#                         return index, rank  # 순위 반환
#                 except Exception as e:
#                     print(f"리스트 항목에서 링크 찾기 오류: {e}")
#                 rank += 1
#
#         # 2. 첫 번째 더보기 버튼 클릭 후 순위를 찾는 경우
#         print("첫 번째 더보기 버튼을 클릭 시도")
#         try:
#             click_more_button(driver, "a.YORrF span.Jtn42")
#         except Exception as e:
#             print(f"첫 번째 더보기 버튼 클릭 실패: {e}")
#             return index, None
#
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#place-main-section-root"))
#         )
#
#         list_items = driver.find_elements(By.CSS_SELECTOR,
#                                           "#place-main-section-root > div.place_section.Owktn > div.rdX0R.POx9H > ul > li")
#         print(f"리스트에서 순위 확인: {len(list_items)} 항목 발견")
#         rank = 1
#         for item in list_items:
#             try:
#                 link = item.find_element(By.CSS_SELECTOR, "a")
#                 href = link.get_attribute("href")
#                 if place_id_str in href:
#                     print(f"리스트에서 순위 발견: {href}, 현재 순위: {rank}")
#                     return index, rank  # 순위 반환
#             except Exception as e:
#                 print(f"리스트 항목에서 링크 찾기 오류: {e}")
#             rank += 1
#
#         # 3. 두 번째 더보기 버튼 클릭 후 스크롤을 끝까지 내리면서 순위를 찾는 경우
#         print("두 번째 더보기 버튼 클릭 시도")
#         try:
#             click_more_button(driver, "a.cf8PL")
#         except Exception as e:
#             print(f"두 번째 더보기 버튼 클릭 실패: {e}")
#             return index, None
#
#         # 페이지가 로드될 때까지 기다림 (두 번째 더보기 후)
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "div.qbGlu"))
#         )
#
#         rank = 1
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         same_height_count = 0
#         max_same_height_count = 3
#
#         while same_height_count < max_same_height_count:
#             # 새로 바뀐 구조에 맞춰 list_items 선택자 수정
#             list_items = driver.find_elements(By.CSS_SELECTOR, "div.qbGlu a.P7gyV")
#             print(f"스크롤 후 리스트에서 확인: {len(list_items)} 항목 발견")
#
#             for item in list_items:
#                 try:
#                     href = item.get_attribute("href")
#                     if place_id_str in href:
#                         print(f"스크롤 후 리스트에서 순위 발견: {href}, 현재 순위: {rank}")
#                         return index, rank  # 순위 반환
#                 except Exception as e:
#                     print(f"리스트 항목에서 링크 찾기 오류: {e}")
#                 rank += 1
#
#             # 스크롤을 내림
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(3)  # 스크롤 후 페이지 로딩을 기다림
#             new_height = driver.execute_script("return document.body.scrollHeight")
#
#             if new_height == last_height:
#                 same_height_count += 1
#             else:
#                 same_height_count = 0
#
#             last_height = new_height
#
#         print(f"{keyword}에서 {place_id}의 순위를 찾을 수 없습니다.")
#         return index, None  # 순위를 찾지 못한 경우 None 반환
#
#     except Exception as e:
#         print(f"크롤링 오류 발생: {e}")
#         return index, None  # 오류가 발생한 경우에도 None 반환
#
#     finally:
#         driver.quit()

def find_rank(index, keyword, place_id, place_name=None):
    driver = setup_driver()
    try:
        print(f"크롤링 시작: index={index}, keyword={keyword}, place_id={place_id}")
        place_id_str = str(place_id)
        start = 1
        rank = 1

        while True:
            # 페이지 URL 생성 (캐시 무효화 위해 임시 파라미터 추가)
            search_link = f"https://m.place.naver.com/place/list?query={keyword}&x=126.9783882&y=37.5666103&start={start}&display=100&_={int(time.time())}"
            driver.get(search_link)
            print(f"검색 페이지 로드 완료: {search_link}")

            # 페이지의 특정 요소가 로드될 때까지 대기
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.qbGlu"))
            )

            # 현재 리스트 항목을 가져옴
            previous_items = driver.find_elements(By.CSS_SELECTOR, "div.qbGlu a.P7gyV")
            print(f"리스트에서 확인: {len(previous_items)} 항목 발견")

            if len(previous_items) == 0:
                print(f"더 이상 항목이 없음. 크롤링 종료.")
                break

            found_by_name = False
            for item in previous_items:
                try:
                    href = item.get_attribute("href")
                    print(f"아이템 href 확인: {href}")

                    # place_id로 검색
                    if place_id_str in href:
                        print(f"place_id로 순위 발견: {href}, 현재 순위: {rank}")
                        return index, rank
                    # place_name으로 검색
                    elif place_name:
                        name_element = item.find_element(By.XPATH, './/div/div/span[1]')
                        name_text = name_element.text.strip()
                        print(f"[{rank}] 상호명 선택자에서 발견된 텍스트: {name_text}")
                        if place_name in name_text:
                            print(f"상호명으로 순위 발견: {name_text}, 현재 순위: {rank}")
                            found_by_name = True
                            return index, rank
                except Exception as e:
                    print(f"리스트 항목에서 링크/상호명 찾기 오류: {e}")
                rank += 1

            # 다음 페이지로 이동
            start += 100
            print(f"다음 페이지로 넘어갑니다. 현재 start 값: {start}")

            # 페이지 끝으로 스크롤 (스크롤이 필요 없을 수도 있으나 추가)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)  # 페이지 로드 대기

    except Exception as e:
        print(f"크롤링 오류 발생: {e}")
        return index, None

    finally:
        driver.quit()



# 더보기 버튼 클릭 함수
def click_more_button(driver, css_selector, timeout=30):
    try:
        # 스크롤하면서 버튼을 찾음
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            try:
                more_element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", more_element)
                time.sleep(10)  # 스크롤 후 대기
                driver.execute_script("arguments[0].click();", more_element)
                print(f"더보기 버튼 ({css_selector}) 클릭됨.")
                time.sleep(10)  # 클릭 후 페이지 로딩 대기
                break  # 버튼을 찾고 클릭했다면 루프 종료
            except Exception as e:
                # 페이지 스크롤을 내리면서 다시 시도
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(10)  # 스크롤 후 대기
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print(f"더보기 버튼 ({css_selector})을 찾을 수 없습니다.")
                    break  # 더 이상 스크롤이 되지 않으면 종료
                last_height = new_height
    except Exception as e:
        print(f"더보기 버튼 클릭 실패: {e}")

# 순차적으로 크롤링 및 DB 업데이트 함수
def start_crawling_and_update_db():
    # MySQL에서 데이터 가져오기
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM keywords WHERE id IS NOT NULL")

    rows = cursor.fetchall()

    for row in rows:
        try:
            index, rank = find_rank(row['id'], row['키워드'], row['플레이스번호'], row.get('상호명'))  # place_name 추가
            if rank is not None:
                cursor.execute("SELECT * FROM keywords WHERE id = %s", (index,))
                row = cursor.fetchone()

                # 최초순위 업데이트
                if row['최초순위'] is None:
                    cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

                # 최고순위 업데이트
                if row['최고순위'] is None or row['최고순위'] == 0 or rank < row['최고순위']:
                    최고순위 = rank
                else:
                    최고순위 = row['최고순위']

                # 변동이력 계산
                이전순위 = row['현재순위'] if row['현재순위'] is not None else rank
                변동이력 = rank - 이전순위
                변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

                # 최신일자 업데이트
                now = datetime.now().strftime('%Y-%m-%d %H:%M')

                # DB 업데이트
                cursor.execute("""
                    UPDATE keywords 
                    SET 최고순위 = %s, 현재순위 = %s, 변동이력 = %s, 최신일자 = %s 
                    WHERE id = %s
                """, (최고순위, rank, 변동이력_str, now, index))
                conn.commit()  # 각 작업 완료 후 커밋
                print(f"순위 업데이트 성공: index={index}, rank={rank}, 최고순위={최고순위}, 변동이력={변동이력_str}, 최신일자={now}")
            else:
                print(f"순위를 찾지 못함: index={index}")
        except Exception as e:
            print(f"DB 업데이트 중 오류 발생: {e}")
            conn.rollback()  # 오류 발생 시 롤백

    conn.close()
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
schedule_crawling_task(13,13)
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

        # 먼저 place_id로 순위 찾기 시도
        index, rank = find_rank(index, keyword, place_id)

        # place_id로 찾지 못하면 place_name으로 다시 찾기
        if rank is None and place_name:
            print(f"place_id로 찾지 못했습니다. 상호명({place_name})으로 재검색 시도.")
            index, rank = find_rank(index, keyword, place_id, place_name)

        if rank is not None:
            # 최초순위가 없으면 최초순위로 설정
            if row['최초순위'] is None:
                cursor.execute("UPDATE keywords SET 최초순위 = %s WHERE id = %s", (rank, index))

            # 최고순위가 없거나 현재순위가 최고순위보다 높으면 최고순위 업데이트
            if row['최고순위'] is None or row['최고순위'] == 0 or rank < row['최고순위']:
                최고순위 = rank
            else:
                최고순위 = row['최고순위']

            # 변동이력 계산
            이전순위 = row['현재순위'] if row['현재순위'] is not None else rank
            변동이력 = rank - 이전순위
            변동이력_str = f"+{변동이력}" if 변동이력 > 0 else f"{변동이력}"

            # 최신일자 업데이트
            now = datetime.now().strftime('%Y-%m-%d %H:%M')

            # 현재순위, 최고순위, 변동이력, 최신일자 업데이트
            print(f"Updating: 현재순위={rank}, 최고순위={최고순위}, 변동이력={변동이력_str}, 최신일자={now}")
            cursor.execute("""
                UPDATE keywords
                SET 현재순위 = %s, 최고순위 = %s, 변동이력 = %s, 최신일자 = %s
                WHERE id = %s
            """, (rank, 최고순위, 변동이력_str, now, index))

            conn.commit()
            return jsonify({'rank': rank})
        else:
            return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred.'}), 500
    finally:
        conn.close()


@app.route('/')
def index():
    data = fetch_data_from_db()  # MySQL에서 데이터를 가져옴
    return render_template('index.html', data=data)  # index.html 템플릿을 렌더링

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
