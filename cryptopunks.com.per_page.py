from bs4 import BeautifulSoup
import requests
import pandas as pd
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSlot
import re
import time as t
import os
from PIL import Image
from io import BytesIO

class Game(QMainWindow):
    def __init__(self):
        super().__init__()

        # Label for description
        self.qlabel_description = QLabel("This Program scrapes the cryptopunks.com internet site", self)
        self.qlabel_description.setFixedWidth(500)
        self.qlabel_description.move(50, 50)

        # Download button
        self.button = QPushButton('Download', self)
        self.button.move(100, 250)
        self.button.clicked.connect(self.run)

        # Status label
        self.label = QLabel(self)
        self.label.setGeometry(200, 200, 200, 30)
        
        self.lbl_page_showing = QLabel(f"Page Processing", self)
        self.lbl_page_showing.move(250, 80)

        self.lbl_download_image = QLabel(f"Downloading Image", self)
        self.lbl_download_image.move(250, 100)

        # Set main window properties
        self.setGeometry(50, 50, 500, 400)
        self.setWindowTitle("Web Mining Program")
        self.show()

    @pyqtSlot()
    def run(self):
        # content_type = self.combo_1.currentText()
        url = "https://cryptopunks.app/cryptopunks/details/"
        self.get_url(url)

    def download_image(self, image_url, file_name):
        # Create 'images' directory if it does not exist
        if not os.path.exists('images_single_page'):
            os.makedirs('images_single_page')

        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                # Open the image with Pillow
                img = Image.open(BytesIO(response.content)).convert("RGBA")
                
                # Define the background color to be removed (RGB)
                background_color = (99, 133, 150, 255)  # RGB + Alpha (255 for fully opaque)

                # Process the image to remove the background color
                datas = img.getdata()

                new_data = []
                for item in datas:
                    if item[0:3] == background_color[0:3]:
                        new_data.append((255, 255, 255, 0))  # Change the background to fully transparent
                    else:
                        new_data.append(item)

                img.putdata(new_data)

                # Save the processed image as PNG
                img.save(os.path.join('images_single_page', file_name), "PNG")
                print(f"Image saved as {file_name}")
                self.lbl_download_image.setText(f"Imager saved as : {file_name}")
                self.lbl_download_image.adjustSize()
            else:
                print(f"Failed to download image: {image_url}")
        except Exception as e:
            print(f"An error occurred while downloading image: {e}")

    def get_url(self, url):
        # content_type = self.combo_1.currentText()
        wFileNameXLSX = "cryptopunks.xlsx";
        wFileNameXLSX1 = "cryptopunks_1.xlsx";
        wFileNameXLSX2 = "cryptopunks_2.xlsx";

        df = pd.DataFrame(columns=['Url', 'Product Title', 'Image Front','Gender','Tags'])

        try:
            # wContent_type = self.combo_1.currentText()
            wCount = 0
            wSite_Path = "https://cryptopunks.app"


            for i in range(1, 10001):
                new_url = f"{url}{i}"
                wCount = i;
                # new_url = "https://cryptopunks.app/cryptopunks/details/54";
                response = requests.get(new_url)
                wMod = i % 5
                if  wMod == 0:
                    t.sleep(1)
                else:
                    t.sleep(0.3)

                if response.status_code != 200:
                    if response.status_code == 429:
                        t.sleep(2)
                        response = requests.get(new_url)
                    elif response.status_code == 524:
                        t.sleep(3)
                        response = requests.get(new_url)
                        t.sleep(1)
                    else:
                        print(f"Error: Unable to fetch data from URL. Status code: {response.status_code}")
                        df.to_excel(f'{wFileNameXLSX}', index=False)
                        print(f"Data saved to {wFileNameXLSX}")
                        break

                soup = BeautifulSoup(response.content, 'html.parser')

                Is_Not_Matched = soup.find('div', class_='index-section')
                if Is_Not_Matched:
                    QMessageBox.about(self, "Title", f"Continue exception : {e}, \n wCount : {wCount} ")
                    print(f"Error: Unable to fetch data from URL. Status code: {response.status_code}")
                    df.to_excel('cryptopunks.xlsx', index=False)
                    print("Data saved to cryptopunks.xlsx")
                    break

                #list_div = soup.find('div', class_='row row-flex')
                wProductTitle = soup.find('h1').text
                wPropertyAll = soup.find_all("div", class_="row detail-row")
                if wPropertyAll:
                    wAttributes_header = wPropertyAll[0].find('h3', string="Attributes")
                    if  wAttributes_header:
                        # Find all <a> tags within the HTML
                        a_tags = wPropertyAll[0].find_all('a')

                        # Extract href attributes and join them into a single string with commas
                        text_values = ', '.join([a.text for a in a_tags if 'attributes' not in a.text])

                self.lbl_page_showing.setText(f"Processing Record: {i}")
                self.lbl_page_showing.adjustSize()
                # self.show()
                

                # a_tags = soup.find_all('a')
                wHref = f"https://cryptopunks.app/cryptopunks/details/{i}"
                wImageFront = wSite_Path + soup.find('img', class_='img-responsive pixelated center-block')['src'];
                wGenderFirstStep  = soup.find('div', class_='col-md-10 col-md-offset-1 col-xs-12');
                wGender = wGenderFirstStep.find('a').getText();
    
                # Download image
                image_file_name = f"{wProductTitle.replace('/', '_')}.png"
                self.download_image(wImageFront, image_file_name)
                QApplication.processEvents() 

                

                # Append data to DataFrame
                df = pd.concat([df, pd.DataFrame({
                    'Url': [new_url],
                    'Product Title': [wProductTitle],
                    'Image Front': [wImageFront],
                    'Gender' : [wGender],
                    'Tags' : [text_values]
                })], ignore_index=True)
                


            df.to_excel(f'{wFileNameXLSX1}', index=False)
            print("Data saved to {wFileNameXLSX1}")
            QMessageBox.about(self, "Title", f"{wFileNameXLSX1} file written.: {wCount}")

        except Exception as e:
            df.to_excel(f'{wFileNameXLSX2}', index=False)
            print(f"Data saved to {wFileNameXLSX2}")
            print(f"An error occurred: {e}")
            QMessageBox.about(self, "Title", f"{wFileNameXLSX2} Last exception : \n {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())
