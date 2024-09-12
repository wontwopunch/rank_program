from flask import Flask, render_template, request, jsonify
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import time

app = Flask(__name__)

# 엑셀 파일 경로
excel_file = 'data/keywords.xlsx'

# 엑셀 파일 불러오기
df = pd.read_excel(excel_file)

# ChromeDriver 경로 (프로젝트 내)
chrome_driver_path = 'webdriver/chromedriver.exe'


# 더보기 버튼을 클릭하는 함수
def find_rank(index, keyword, place_id):
    try:
        service = Service(executable_path=chrome_driver_path)
        options = Options()
        options.add_argument('--ignore-certificate-errors')
        driver = webdriver.Chrome(service=service, options=options)

        search_link = f"https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}"
        driver.get(search_link)

        place_id_selector = f"a[href*='/{place_id}?entry=pll']"

        # 케이스 1: 더보기 버튼 없이 리스트에서 id를 찾는 경우
        no_more_button_selector = "#loc-main-section-root > div > div.rdX0R > ul > li"
        list_items = driver.find_elements(By.CSS_SELECTOR, no_more_button_selector)
        if list_items:
            print(f"더보기 버튼 없이 리스트에서 {place_id}를 찾습니다.")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    print(f"리스트 항목 링크: {href}")
                    if place_id in href:
                        print(f"{place_id}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1

        # 케이스 2: 첫 번째 더보기 버튼을 클릭한 후 리스트에서 찾는 경우
        try:
            click_more_button(driver, "a.YORrF span.Jtn42")
            print("첫 번째 더보기 버튼 클릭됨.")
            list_items = driver.find_elements(By.CSS_SELECTOR,
                                              "#place-main-section-root > div.place_section.Owktn > div.rdX0R.POx9H > ul > li")
            print(f"첫 번째 더보기 클릭 후 리스트 항목 개수: {len(list_items)}")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    print(f"리스트 항목 링크: {href}")
                    if place_id in href:
                        print(f"{place_id}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1
        except Exception as e:
            print(f"첫 번째 더보기 버튼 없음 또는 클릭 실패: {e}")

        # 케이스 3: 두 번째 더보기 버튼을 클릭한 후 리스트에서 찾는 경우
        try:
            click_more_button(driver, "a.cf8PL")
            print("두 번째 더보기 버튼 클릭됨.")

            # 대기 시간을 추가하여 리스트가 로드되도록 함
            time.sleep(5)  # 추가 대기 시간

            list_items = driver.find_elements(By.CSS_SELECTOR,
                                              "#_list_scroll_container > div > div > div.place_business_list_wrapper > ul > li")
            print(f"두 번째 더보기 클릭 후 리스트 항목 개수: {len(list_items)}")
            rank = 1
            for item in list_items:
                try:
                    link = item.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    print(f"리스트 항목 링크: {href}")
                    if place_id in href:
                        print(f"{place_id}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank  # 순위 반환
                except Exception as e:
                    print(f"리스트 항목에서 링크 찾기 오류: {e}")
                rank += 1
        except Exception as e:
            print(f"두 번째 더보기 버튼 없음 또는 클릭 실패: {e}")

        print(f"{keyword}에서 업체 ID {place_id}의 순위를 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"Error occurred during rank finding: {e}")
        return None

    finally:
        driver.quit()


# 더보기 버튼을 클릭하는 함수
def click_more_button(driver, css_selector):
    try:
        # 더보기 버튼이 로드되었는지, 클릭 가능한지 확인
        more_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", more_element)  # 스크롤
        time.sleep(1)  # 스크롤 후 대기
        driver.execute_script("arguments[0].click();", more_element)  # JavaScript로 클릭
        print(f"더보기 버튼 ({css_selector}) 클릭됨.")
        time.sleep(2)  # 페이지 업데이트 대기
    except Exception as e:
        print(f"더보기 버튼 클릭 실패: {e}. CSS 선택자가 맞는지 또는 버튼이 제대로 로드되었는지 확인.")


# 메인 페이지 라우팅
@app.route('/')
def index():
    return render_template('index.html', df=df)


# 순위 조회 후 업데이트 처리
@app.route('/fetch', methods=['POST'])
def fetch():
    data = request.get_json()

    # 인덱스 값이 있는지 확인
    if 'index' not in data:
        return jsonify({'error': 'No index provided'}), 400

    index = int(data['index'])  # 조회 버튼을 클릭한 행의 인덱스 번호를 받아옴
    keyword = data['keyword']
    place_id = data['place_id']

    # 네이버 검색 결과 페이지로 이동
    rank = find_rank(index, keyword, place_id)

    if rank is not None:
        # 기존 최고순위와 비교해서 더 높은 순위면 업데이트
        if pd.isna(df.at[index, '최고순위']) or rank < df.at[index, '최고순위']:
            df.at[index, '최고순위'] = rank

        # 현재 순위와 최신일자 업데이트
        df.at[index, '순위'] = rank
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        df.at[index, '최신일자'] = now

        # 업데이트된 엑셀 저장
        df.to_excel(excel_file, index=False)

        return jsonify({'rank': rank})
    else:
        return jsonify({'error': '순위를 찾을 수 없습니다.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
