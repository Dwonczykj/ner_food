import sys
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import QUrl, QCoreApplication
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import bs4 as bs

from PyQt5 import QtWebKit

class Client():

    def __init__(self, url):
        self.webpage = QtWebEngine()
        self.webpage.initialize()

        self.app = QGuiApplication(sys.argv)

        self.engine = QQmlApplicationEngine()
        self.engine.load(QUrl(url))

        self.app.exec()
        # QWebEnginePage.__init__(self) # super().__init()
        # self.loadFinished().connect(self.on_page_load)
        
        # self.webpage.load(QUrl(url))
        # self.webpage.app.exec_()
        
    def on_page_load(self):
        self.webpage.app.quit()

    
        
# url = 'https://pythonprogramming.net/parsememcparseface/'
# client_response = Client(url)
# source = client_response.webpage.mainFrame().toHtml()
# soup = bs.BeautifulSoup(source, 'lxml')
# js_test = soup.find('p', class_='jstest')
# print(js_test.text)
# client_response.on_page_load()

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))

        self.setCentralWidget(self.browser)

        self.show()

app = QApplication(sys.argv)
window = MainWindow()

app.exec_()