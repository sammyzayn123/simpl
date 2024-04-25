from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
import csv
from urllib.parse import quote_plus

app = Flask(__name__)

@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search_string = request.form['content']
            encoded_search_string = quote_plus(search_string)
            flipkart_url = f"https://www.flipkart.com/search?q={encoded_search_string}"
            response = requests.get(flipkart_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            flipkart_html = bs(response.text, "html.parser")
            big_boxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            if big_boxes:
                del big_boxes[0:3]
                box = big_boxes[0]
                product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
                product_response = requests.get(product_link)
                product_response.encoding = 'utf-8'
                product_html = bs(product_response.text, "html.parser")
                comment_boxes = product_html.find_all('div', {'class': "_16PBlm"})

                filename = f"{search_string}.csv"
                with open(filename, "w", newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Product", "Customer Name", "Rating", "Heading", "Comment"])
                    for commentbox in comment_boxes:
                        try:
                            name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                        except:
                            name = 'No Name'

                        try:
                            rating = commentbox.div.div.div.div.text
                        except:
                            rating = 'No Rating'

                        try:
                            comment_head = commentbox.div.div.div.p.text
                        except:
                            comment_head = 'No Comment Heading'

                        try:
                            comtag = commentbox.div.div.find_all('div', {'class': ''})
                            cust_comment = comtag[0].div.text
                        except Exception as e:
                            print("Exception while creating dictionary: ", e)
                            cust_comment = ''

                        writer.writerow([search_string, name, rating, comment_head, cust_comment])

                with open(filename, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    reviews = list(reader)

                return render_template('results.html', reviews=reviews)
            else:
                return render_template('no_results.html')
        except Exception as e:
            print('The Exception message is: ', e)
            return 'Something went wrong. Please try again later.'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
