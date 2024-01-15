import requests
from bs4 import BeautifulSoup
import sys
import time
from queue import Queue
from threading import Thread

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget


class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
        }

    def scrape_washington_post_world(self):
        url = "https://www.washingtonpost.com/world/"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')

        article = soup.find("div", class_="wpds-c-iMXAYL")
        if article:
            headline_element = article.find("h3")
            headline = headline_element.text.strip()

            annotation_element = article.find("p")
            annotation = annotation_element.text.strip()

            authors_elements = article.find("div", class_="story-headline pr-sm").find_all('span', class_='wpds-c-knSWeD')
            author_list = [span.text.strip() for span in authors_elements]
            authors_string = "".join(author_list)

            return {'Headline': headline, 'Annotation': annotation, 'Authors': authors_string}

        else:
            return {'Headline': "Headline not found", 'Annotation': "Annotation not found", 'Authors': "Authors not found"}

    def scrape_news_au_world(self):
        url = "https://www.news.com.au/world"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        article = soup.find("article")
        if article:
            headline_element = article.find("h4")
            author_url = headline_element.find('a').get("href")
            headline = headline_element.text.strip()
            
            annotation_element = article.find("p", class_ = "storyblock_standfirst g_font-body-s")
            annotation = annotation_element.text.strip()
            
            response_author_url = requests.get(author_url)
            soup = BeautifulSoup(response_author_url.text, 'lxml')
            authors_elements = soup.find("span", class_ = "author_name")
            author_list = [span.text.strip() for span in authors_elements]
            authors_string = " ".join(author_list)
            
            return {'Headline': headline, 'Annotation': annotation, 'Authors': authors_string}
        
        else:
            return {'Headline': "Headline not found", 'Annotation': "Annotation not found", 'Authors': "Authors not found"}

    def scrape_independent_world(self):
        url = "https://www.independent.co.uk/news/world"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')

        article = soup.find("div", id="sectionContent")
        if article:
            content = article.find('div', class_="content")

            headline_element = content.find("h2")
            headline = headline_element.text.strip()

            annotation_element = content.find("p")
            annotation = annotation_element.text.strip()

            author_url = "https://www.independent.co.uk" + headline_element.find('a').get("href")
            response_author_url = self.session.get(author_url, headers=self.headers)
            soup = BeautifulSoup(response_author_url.text, 'lxml')

            author_element = soup.find("a", class_="sc-1qz44j0-5 kHCTgx")
            author_list = [a.text.strip() for a in author_element]
            authors_string = " ".join(author_list)

            return {'Headline': headline, 'Annotation': annotation, 'Authors': authors_string}

        else:
            return {'Headline': "Headline not found", 'Annotation': "Annotation not found", 'Authors': "Authors not found"}

class NewsScraperGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("News Scraper")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        washington_post_label = QLabel("<b>Washington Post (World News)</b>")
        news_au_label = QLabel("<b>News AU (World News)</b>")
        independent_label = QLabel("<b>The Independent (World News)</b>")

        font = QFont()
        font.setPointSize(14)
        washington_post_label.setFont(font)
        news_au_label.setFont(font)
        independent_label.setFont(font)

        self.wp_headline_label = QLabel("")
        self.na_headline_label = QLabel("")
        self.in_headline_label = QLabel("")

        self.wp_annotation_label = QLabel("")
        self.na_annotation_label = QLabel("")
        self.in_annotation_label = QLabel("")

        self.wp_author_label = QLabel("")
        self.na_author_label = QLabel("")
        self.in_author_label = QLabel("")

        wp_headline_label = QLabel("Headline:")
        na_headline_label = QLabel("Headline:")
        in_headline_label = QLabel("Headline:")

        wp_annotation_label = QLabel("Annotation:")
        na_annotation_label = QLabel("Annotation:")
        in_annotation_label = QLabel("Annotation:")

        wp_author_label = QLabel("Authors:")
        na_author_label = QLabel("Authors:")
        in_author_label = QLabel("Authors:")

        self.main_layout.addWidget(washington_post_label)
        self.main_layout.addWidget(wp_headline_label)
        self.main_layout.addWidget(self.wp_headline_label)
        self.main_layout.addWidget(wp_annotation_label)
        self.main_layout.addWidget(self.wp_annotation_label)
        self.main_layout.addWidget(wp_author_label)
        self.main_layout.addWidget(self.wp_author_label)
        self.main_layout.addWidget(news_au_label)
        self.main_layout.addWidget(na_headline_label)
        self.main_layout.addWidget(self.na_headline_label)
        self.main_layout.addWidget(na_annotation_label)
        self.main_layout.addWidget(self.na_annotation_label)
        self.main_layout.addWidget(na_author_label)
        self.main_layout.addWidget(self.na_author_label)
        self.main_layout.addWidget(independent_label)
        self.main_layout.addWidget(in_headline_label)
        self.main_layout.addWidget(self.in_headline_label)
        self.main_layout.addWidget(in_annotation_label)
        self.main_layout.addWidget(self.in_annotation_label)
        self.main_layout.addWidget(in_author_label)
        self.main_layout.addWidget(self.in_author_label)

        self.scrape_button = QPushButton("Scrape")
        self.scrape_button.clicked.connect(self.scrape_news)
        self.main_layout.addWidget(self.scrape_button)

        self.setCentralWidget(self.main_widget)

        self.news_queue = Queue()

        self.background_thread = BackgroundThread(self.news_queue)
        self.background_thread.start()

    def scrape_news(self):
        self.scrape_button.setEnabled(False)

        wp_news = NewsScraper().scrape_washington_post_world()
        na_news = NewsScraper().scrape_news_au_world()
        in_news = NewsScraper().scrape_independent_world()

        self.wp_headline_label.setText(wp_news['Headline'])
        self.wp_annotation_label.setText(wp_news['Annotation'])
        self.wp_author_label.setText(wp_news['Authors'])

        self.na_headline_label.setText(na_news['Headline'])
        self.na_annotation_label.setText(na_news['Annotation'])
        self.na_author_label.setText(na_news['Authors'])

        self.in_headline_label.setText(in_news['Headline'])
        self.in_annotation_label.setText(in_news['Annotation'])
        self.in_author_label.setText(in_news['Authors'])

    def update_news(self):
        while True:
            wp_news, na_news, in_news = self.news_queue.get()

            if wp_news['Headline'] != self.wp_headline_label.text():
                self.wp_headline_label.setText(wp_news['Headline'])
                self.wp_annotation_label.setText(wp_news['Annotation'])
                self.wp_author_label.setText(wp_news['Authors'])

            if na_news['Headline'] != self.na_headline_label.text():
                self.na_headline_label.setText(na_news['Headline'])
                self.na_annotation_label.setText(na_news['Annotation'])
                self.na_author_label.setText(na_news['Authors'])

            if in_news['Headline'] != self.in_headline_label.text():
                self.in_headline_label.setText(in_news['Headline'])
                self.in_annotation_label.setText(in_news['Annotation'])
                self.in_author_label.setText(in_news['Authors'])

            time.sleep(30)

class BackgroundThread(QThread):
    wp_signal = pyqtSignal(dict)
    na_signal = pyqtSignal(dict)
    in_signal = pyqtSignal(dict)

    def __init__(self, news_queue):
        super().__init__()
        self.news_queue = news_queue

    def run(self):
        while True:
            wp_news = NewsScraper().scrape_washington_post_world()
            na_news = NewsScraper().scrape_news_au_world()
            in_news = NewsScraper().scrape_independent_world()

            self.wp_signal.emit(wp_news)
            self.na_signal.emit(na_news)
            self.in_signal.emit(in_news)

            time.sleep(30)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NewsScraperGUI()
    window.show()

    update_thread = Thread(target=window.update_news)
    update_thread.daemon = True
    update_thread.start()

    sys.exit(app.exec_())