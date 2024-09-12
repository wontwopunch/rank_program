from flask import Flask, render_template, request, jsonify
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
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


# def find_rank(keyword, place_id):
#     try:
#         service = Service(executable_path=chrome_driver_path)
#         driver = webdriver.Chrome(service=service)
#         search_link = f"https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}"
#         print(f"검색 링크: {search_link}")
#         driver.get(search_link)
#
#         # 플레이스 섹션에서 먼저 ID를 찾기
#         print("더보기 탭을 누르기 전에 플레이스에서 ID를 찾습니다.")
#         place_id_selector = f"a[href*='/{place_id}?entry=pll']"
#         place_elements = driver.find_elements(By.CSS_SELECTOR, place_id_selector)
#
#         if place_elements:
#             print(f"플레이스 섹션에서 업체 ID {place_id}를 찾았습니다.")
#             # 플레이스 섹션에서의 순위를 계산
#             all_list_selector = "#_list_scroll_container > div > div > div:nth-child(2) > ul > li"
#             all_list_elements = driver.find_elements(By.CSS_SELECTOR, all_list_selector)
#
#             print(f"플레이스 섹션에서 찾은 리스트 항목 개수: {len(all_list_elements)}")
#
#             rank = 1
#             for ele in all_list_elements:
#                 try:
#                     link = ele.find_element(By.CSS_SELECTOR, "a")
#                     href = link.get_attribute("href")
#                     if place_id in href:
#                         print(f"{place_id}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
#                         return rank
#                 except Exception as e:
#                     print(f"순위를 찾는 도중 예외 발생: {e}")
#                 rank += 1
#
#             print(f"{keyword}에서 플레이스 섹션 순위를 찾지 못했습니다.")
#         else:
#             print(f"플레이스 섹션에서 업체 ID {place_id}를 찾지 못했습니다. 더보기 탭을 클릭합니다.")
#
#         # 첫 번째 더보기 탭 클릭 시도
#         more_tab_found = False
#         try:
#             more_tab = "a.YORrF span.Jtn42"
#             first_more_element = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, more_tab))
#             )
#             first_more_element.click()
#             print("첫 번째 더보기 버튼 클릭됨.")
#             more_tab_found = True
#         except Exception as e:
#             print(f"첫 번째 더보기 탭 없음 또는 클릭 실패: {e}")
#
#         # 두 번째 더보기 탭 클릭
#         if more_tab_found:
#             try:
#                 second_more_tab = "a.cf8PL"
#                 second_more_element = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, second_more_tab))
#                 )
#                 second_more_element.click()
#                 print("두 번째 더보기 버튼 클릭됨.")
#             except Exception as e:
#                 print(f"두 번째 더보기 탭 없음 또는 클릭 실패: {e}")
#
#         # 두 번째 더보기 클릭 후 스크롤 필요할 수 있음
#         print("두 번째 더보기 클릭 후 추가 스크롤 시작.")
#         scroll_pause_time = 3  # 대기 시간을 늘림
#         last_height = driver.execute_script("return document.body.scrollHeight")
#
#         max_scrolls = 20  # 스크롤 횟수를 늘림
#         found_place = False
#
#         for _ in range(max_scrolls):
#             # ID가 있는지 확인
#             place_elements = driver.find_elements(By.CSS_SELECTOR, place_id_selector)
#             if place_elements:
#                 print(f"업체 ID {place_id}를 찾았습니다.")
#                 found_place = True
#                 break
#
#             # 더 스크롤할 곳이 없으면 중지
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 print("더 이상 스크롤할 곳이 없습니다.")
#                 break
#             last_height = new_height
#
#             driver.execute_script("window.scrollBy(0, 2000);")
#             time.sleep(scroll_pause_time)
#
#         # 찾은 요소가 없으면 종료
#         if not found_place:
#             print(f"{keyword}에서 업체 ID를 찾지 못했습니다.")
#             return None
#
#         # 찾은 ID의 순위 확인
#         all_list_selector = "#_list_scroll_container > div > div > div:nth-child(2) > ul > li"
#         all_list_elements = driver.find_elements(By.CSS_SELECTOR, all_list_selector)
#
#         print(f"스크롤 후 리스트에서 찾은 항목 개수: {len(all_list_elements)}")
#
#         rank = 1
#         for ele in all_list_elements:
#             try:
#                 link = ele.find_element(By.CSS_SELECTOR, "a")
#                 href = link.get_attribute("href")
#                 print(f"리스트 내 링크: {href}")
#                 if place_id in href:
#                     print(f"{place_id}를 포함한 링크 발견: {href}")
#                     return rank
#             except Exception as e:
#                 print(f"순위를 찾는 도중 예외 발생: {e}")
#             rank += 1
#
#         print(f"{keyword} 순위를 찾을 수 없습니다.")
#         return None
#
#     except Exception as e:
#         print(f"Error occurred during rank finding: {e}")
#         return None
#     finally:
#         driver.quit()


def find_rank(keyword, place_id):
    try:
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        search_link = f"https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query={keyword}"
        print(f"검색 링크: {search_link}")
        driver.get(search_link)

        # 플레이스 섹션에서 ID를 찾기
        place_id_selector = f"a[href*='/{place_id}?entry=pll']"

        # 페이지 로딩 완료 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, place_id_selector))
        )
        place_elements = driver.find_elements(By.CSS_SELECTOR, place_id_selector)

        if place_elements:
            print(f"플레이스 섹션에서 업체 ID {place_id}를 찾았습니다.")
            # 플레이스 섹션에서의 순위를 계산
            all_list_selector = "#_list_scroll_container > div > div > div:nth-child(2) > ul > li"
            all_list_elements = driver.find_elements(By.CSS_SELECTOR, all_list_selector)

            print(f"플레이스 섹션에서 찾은 리스트 항목 개수: {len(all_list_elements)}")

            rank = 1
            for ele in all_list_elements:
                try:
                    link = ele.find_element(By.CSS_SELECTOR, "a")
                    href = link.get_attribute("href")
                    if place_id in href:
                        print(f"{place_id}를 포함한 링크 발견: {href}, 현재 순위: {rank}")
                        return rank
                except Exception as e:
                    print(f"순위를 찾는 도중 예외 발생: {e}")
                rank += 1

            print(f"{keyword}에서 플레이스 섹션 순위를 찾지 못했습니다.")
        else:
            print(f"플레이스 섹션에서 업체 ID {place_id}를 찾지 못했습니다. 더보기 탭을 클릭합니다.")

            # 첫 번째 더보기 탭 클릭 시도
            more_tab_found = False
            try:
                more_tab = "a.YORrF span.Jtn42"
                first_more_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, more_tab))
                )
                first_more_element.click()
                print("첫 번째 더보기 버튼 클릭됨.")
                more_tab_found = True
            except Exception as e:
                print(f"첫 번째 더보기 탭 없음 또는 클릭 실패: {e}")

            # 두 번째 더보기 탭 클릭
            if more_tab_found:
                try:
                    second_more_tab = "a.cf8PL"
                    second_more_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, second_more_tab))
                    )
                    second_more_element.click()
                    print("두 번째 더보기 버튼 클릭됨.")
                except Exception as e:
                    print(f"두 번째 더보기 탭 없음 또는 클릭 실패: {e}")

            # 두 번째 더보기 클릭 후 스크롤 필요할 수 있음
            print("두 번째 더보기 클릭 후 추가 스크롤 시작.")
            scroll_pause_time = 3  # 대기 시간을 늘림
            last_height = driver.execute_script("return document.body.scrollHeight")

            max_scrolls = 20  # 스크롤 횟수를 늘림
            found_place = False

            for _ in range(max_scrolls):
                # ID가 있는지 확인
                place_elements = driver.find_elements(By.CSS_SELECTOR, place_id_selector)
                if place_elements:
                    print(f"업체 ID {place_id}를 찾았습니다.")
                    found_place = True
                    break

                # 더 스크롤할 곳이 없으면 중지
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("더 이상 스크롤할 곳이 없습니다.")
                    break
                last_height = new_height

                driver.execute_script("window.scrollBy(0, 2000);")
                time.sleep(scroll_pause_time)

            # 찾은 요소가 없으면 종료
            if not found_place:
                print(f"{keyword}에서 업체 ID를 찾지 못했습니다.")
                return None

        # 찾은 ID의 순위 확인
        all_list_selector = "#_list_scroll_container > div > div > div:nth-child(2) > ul > li"
        all_list_elements = driver.find_elements(By.CSS_SELECTOR, all_list_selector)

        print(f"스크롤 후 리스트에서 찾은 항목 개수: {len(all_list_elements)}")

        rank = 1
        for ele in all_list_elements:
            try:
                link = ele.find_element(By.CSS_SELECTOR, "a")
                href = link.get_attribute("href")
                print(f"리스트 내 링크: {href}")
                if place_id in href:
                    print(f"{place_id}를 포함한 링크 발견: {href}")
                    return rank
            except Exception as e:
                print(f"순위를 찾는 도중 예외 발생: {e}")
            rank += 1

        print(f"{keyword} 순위를 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"Error occurred during rank finding: {e}")
        return None
    finally:
        driver.quit()




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
    rank = find_rank(keyword, place_id)

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