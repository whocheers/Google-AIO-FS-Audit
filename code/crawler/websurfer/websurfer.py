import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebSurfer:
    """Selenium class that navigates the web using Chrome with immediate location spoofing"""

    def __init__(self,
            profile: str = "selenium_profiles/default",
            user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            location: Optional[Dict[str, float]] = None,
            headless: bool = False,
        ):

        # Settings
        self.profile = profile        # Path to Selenium profile directory
        self.user_agent = user_agent  # User agent string
        self.location = location      # Dict with location coordinates
        self.headless = headless      # Run Selenium in headless mode (no visible browser window)

        # # Output data
        # self.session = datetime.now(timezone.utc).isoformat()
        # self.fp_output = os.path.join('data', f"{self.session}.json")
        
        ## Output folder for the SERP html files
        self.session = datetime.now(timezone.utc).isoformat().replace(':', '-')
        self.output_dir = os.path.join('html_output_no_login_First_New_Office_WIFI', self.session)
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_chrome()

    def start_chrome(self):
        """Launch Chrome browser with Selenium and options"""
        chrome_options = self._configure_chrome_options()
        self.browser = webdriver.Chrome(options=chrome_options)
        self.set_user_agent()
        self.set_navigator_null()
        self.set_location()

    def _configure_chrome_options(self):
        """Configure Chrome options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        if self.profile:
            chrome_options.add_argument(f'user-data-dir={self.profile}')

        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        return chrome_options

    def set_user_agent(self):
        """Set the user agent for the browser"""
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.user_agent})

    def set_navigator_null(self):
        """Inject JavaScript to remove navigator.webdriver property"""
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
                })
            """
        })

    def set_location(self):
        """Set the location for the browser"""
        if self.location:
            latitude = self.location.get('latitude', 0)
            longitude = self.location.get('longitude', 0)
            accuracy = self.location.get('accuracy', 100)
            print(f'Setting location: Latitude {latitude}, Longitude {longitude}, Accuracy {accuracy}')

            # Not as reliable as JS injection, but not a bad redundancy to keep
            # https://chromedevtools.github.io/devtools-protocol/tot/Emulation/#method-setGeolocationOverride
            self.browser.execute_cdp_cmd("Emulation.setGeolocationOverride", {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            })

            # Inject JavaScript to override geolocation API
            js_code = f"""
            var latitude = {latitude};
            var longitude = {longitude};
            var accuracy = {accuracy};

            navigator.geolocation.getCurrentPosition = function(success, failure) {{
                success({{
                    coords: {{
                        latitude: latitude,
                        longitude: longitude,
                        accuracy: accuracy,
                        altitude: null,
                        altitudeAccuracy: null,
                        heading: null,
                        speed: null
                    }},
                    timestamp: Date.now()
                }});
            }};
            
            navigator.geolocation.watchPosition = function(success, failure) {{
                success({{
                    coords: {{
                        latitude: latitude,
                        longitude: longitude,
                        accuracy: accuracy,
                        altitude: null,
                        altitudeAccuracy: null,
                        heading: null,
                        speed: null
                    }},
                    timestamp: Date.now()
                }});
                return 0;
            }};
            """
            self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": js_code
            })

    # def navigate_to(self, url: str):
    #     self.browser.get(url)
    #     WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    #     self.current_window = self.browser.current_window_handle

    
    def navigate_to(self, url: str, query_index: str = "test", save_html: bool = False, output_dir: str = 'html_output_no_login_First_New_Office_WIFI'):
        self.browser.get(url)
        #WebDriverWait(self.browser, 50).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        try:
            #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "rPeykc"))) # 
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "fx92l"))) # 
            time.sleep(2)
            #sleep
        except:
            print("an exception for this query_index as no AI overview text: ", query_index)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        #WebDriverWait(self.browser, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        self.current_window = self.browser.current_window_handle

        if save_html:
            timestamp = datetime.now(timezone.utc).isoformat().replace(':', '-')
            file_path = os.path.join(self.output_dir, f"{query_index}_{timestamp}.html")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.browser.page_source)
            print(f"Saved HTML to {file_path}")


    def shutdown(self):
        self.browser.quit()
