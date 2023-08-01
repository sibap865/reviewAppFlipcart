from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import os
logging.basicConfig(filename="logs.log",format="%(asctime)s: %(levelname)s: %(lineno)d: %(message)s",level=logging.INFO)
application = Flask(__name__)
app =application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin() #we are able to hit the url from different region
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            logging.info(f"searchstring :{searchString}")
            reviews_result_list =[]
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            print("flipcart_url" , flipkart_url)
            logging.info(f"flipkart_url :{flipkart_url}")
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box =bigboxes[1]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            print("productLink" , productLink)
            logging.info(f"productLink :{productLink}")
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            reviews =prod_html.find_all('div',{'class','col JOpGWq'})
            
            try:
                reviews=reviews[0].find_all('a',{"class":""})[-1]
            except Exception as e:
                logging.info(e)
                reviews =prod_html.find_all('div',{'class','col JOpGWq _33R3aa'})
                reviews=reviews[0].find_all('a',{"class":""})[-1]

            reviewpage="https://www.flipkart.com"+reviews["href"]
            print("reviewpage",reviewpage)
            logging.info(f"review page link: {reviewpage}")
            prodRes = requests.get(reviewpage)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            all_review =prod_html.find_all("div",{"class","_2MImiq _1Qnn1K"})[0].nav
            del all_review[-1]
            product_review_page =all_review.find_all("a",{"class":"ge-49M"})
            for page in product_review_page:
                review_page =( "https://www.flipkart.com"+page["href"])
                logging.info(f"all review pages (1-n): {review_page}")
                print("review_page",review_page)
                prodRes = requests.get(review_page)
                prodRes.encoding='utf-8'
                prod_htmls = bs(prodRes.text, "html.parser")
                reviews=prod_htmls.find_all("div",{"class","col _2wzgFH K0kLPL"})
                if(reviews ==[]):
                    reviews=prod_htmls.find_all("div",{"class","col _2wzgFH K0kLPL _1QgsS5"})
                reviews_results=[]
                price=(prod_htmls.find_all("div",{"class":"_30jeq3"})[0].text)
                logging.info("finding reviews bro")
                product=searchString
                for review in reviews:
                    logging.info("finding review")
                    rating =(review.div.div.text[0])
                    try: 
                        name=(review.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text) 
                    except Exception as e:
                        logging.info(e)
                        try:
                            name=(review.find_all("p",{"class":"_2sc7ZR _2V5EHH _1QgsS5"})[0].text)
                        except:
                            name="None"
                    try:
                        title=(review.div.p.text)
                    except Exception as e:
                        logging.info(e)
                        title="None"
                    try:
                        message=(review.find_all("div",{"class":"t-ZTKy"})[0].div.div.text)
                    except Exception as e:
                        logging.info(e)
                        message="None"
                    reviews_result ={"name":name,"rating":rating,"title":title,"message":message}
                    reviews_results.append(reviews_result)
                reviews_result_list.extend(reviews_results)
            return render_template('results.html', reviews=reviews_result_list,product =product,price =price,product_link =productLink)
        except Exception as e:
            print('The Exception message is: ',e)
            logging.info(f"exception occured {e}")
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8000)
	# app.run(debug=True)