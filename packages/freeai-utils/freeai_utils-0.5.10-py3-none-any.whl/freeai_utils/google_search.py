from googlesearch import search #need pip install googlesearch-python
import requests #need pip install requests
from bs4 import BeautifulSoup # need pip install beautifulsoup4
from readability import Document # need pip install readability-lxml
from freeai_utils.log_set_up import setup_logging
class WebScraper:
    def __init__(self, user_agent: str = "Mozilla/5.0", num_results: int = 5, limit_word_per_url : int = 500):
        self.__enforce_type(user_agent, str, "user_agent")
        self.__enforce_type(num_results, int, "num_results")
        self.__enforce_type(limit_word_per_url, int, "limit_word_per_url")
        self.user_agent = user_agent
        self.num_results = num_results
        self.limit_word = limit_word_per_url
        #for logging only this class rather
        self.logger = setup_logging(self.__class__.__name__)
        
    def _url_search(self, query) -> list:
        """helper function that performs a search based on a query and returns a list of URLs from the top results"""
        #return the first num_results url
        self.logger.debug("Trying to return the list of urls")
        return list(search(query, num_results= self.num_results))

    def _fetch_html(self, url : str) -> str:
        """helper function that downloads the HTML content of a given URL."""
        headers = {"User-Agent": self.user_agent}  #mimic a real browser
        resp = requests.get(url, headers=headers)  # GET the page
        resp.raise_for_status()
        if not resp.text.strip():
            self.logger.warning(f"Empty response from URL: {url}")
            
        self.logger.debug("Fetching html completed")
        return resp.text

    def _extract_with_readability(self, html : str) -> str:
        """ helper function that takes the HTML content of a web page and extracts its main, readable text."""
        doc = Document(html)          # build readability DOM
        summary_html = doc.summary()  # HTML content
        # BeautifulSoup to get plain text
        self.logger.debug("Trying to get the text from html")
        return BeautifulSoup(summary_html, "html.parser").get_text()

    def search(self, prompt : str = None, reduce_length : bool = False) -> str:
        """Performs a full web search for a given prompt. Return the extracted text"""
        self.__enforce_type(prompt, str, "prompt")
        
        answer = ""
        urls = self._url_search(prompt)
        for url in urls:
            try:
                result = self._fetch_html(url)
                text = self._extract_with_readability(result)
                answer += text[:self.limit_word]
            except Exception:
                pass #ignore
            
        if reduce_length:
            return answer.replace("\n", " ") #this to reduce the token use if calls API
        
        return answer.replace("\n\n", "\n")
    
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")