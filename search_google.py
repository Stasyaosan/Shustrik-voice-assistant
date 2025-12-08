from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time


class Search_google:
    def __init__(self):
        self.driver = None

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')
        chrome_options.page_load_strategy = 'eager'
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def search(self, query, max_results=10, timeout=5):
        try:
            if not self.driver:
                self.setup_driver()
            wait = WebDriverWait(self.driver, timeout)
            self.driver.get('https://www.google.com')
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.g, div.MjjYud')))
            results = []
            last_count = 0
            start_time = time.time()
            while len(results) < max_results and (time.time() - start_time) < timeout:
                try:
                    result_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.g, div.MjjYud')
                    if len(result_elements) > last_count:
                        for i in range(last_count, min(len(result_elements), max_results)):
                            try:
                                result = self.extract_result_info(result_elements[i])
                                if result and result not in results:
                                    results.append(result)
                            except StaleElementReferenceException:
                                continue
                        last_count = len(result_elements)
                    if len(results) >= 3:
                        break
                    time.sleep(0.3)
                except Exception as e:
                    print(f"Ошибка при сборе результатов: {e}")
                    break
            if len(results) < max_results:
                self.scroll_for_more_results(max_results - len(results))
                result_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.g, div.MjjYud')
                for i in range(len(results), min(len(result_elements), max_results)):
                    try:
                        result = self.extract_result_info(result_elements[i])
                        if result and result not in results:
                            results.append(result)
                    except (StaleElementReferenceException, IndexError):
                        continue
            return results[:max_results]
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            return []

    def extract_result_info(self, result_element):
        try:
            result_data = {}
            try:
                title_elem = result_element.find_element(By.CSS_SELECTOR, 'h3, .DKV0Md, .LC20lb')
                result_data['title'] = title_elem.text
            except:
                result_data['title'] = ''
            try:
                link_elem = result_element.find_element(By.CSS_SELECTOR, 'a')
                result_data['url'] = link_elem.get_attribute('href')
            except:
                result_data['url'] = ''
            try:
                desc_elem = result_element.find_element(By.CSS_SELECTOR, '.VwiC3b, .IsZvec, .MUxGbd')
                result_data['description'] = desc_elem.text[:200]
            except:
                result_data['description'] = ''
            return result_data
        except Exception as e:
            print(f"Ошибка при извлечении данных: {e}")
            return None

    def scroll_for_more_results(self, count_needed):
        try:
            for _ in range(count_needed // 5 + 1):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                try:
                    more_results = self.driver.find_elements(By.CSS_SELECTOR,
                                                             '.RVQdVd, .mye4qd, a[aria-label^="More results"]')
                    if more_results:
                        more_results[0].click()
                        time.sleep(1)
                except:
                    pass
        except Exception as e:
            print(f"Ошибка при прокрутке: {e}")

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __del__(self):
        self.close()
