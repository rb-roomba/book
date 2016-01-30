#! /usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import datetime
import sys
import os
import urllib
import requests


def prev_month():
    """ Return tuple of the previous month."""
    now_y = datetime.date.today().year
    now_m = datetime.date.today().month
    if now_m == 1:
        return now_y-1, 12
    else:
        return now_y, now_m-1



def maybe_download(url):
    """ Download HTML from bookmeter.com if not present."""  
    html_name = "bookmeter_matome_%d%d.html" % (prev_month()[0], 
                                                prev_month()[1])
    # Download if not present
    if not os.path.exists(html_name):
        urllib.urlretrieve(url, html_name)
        print "File " + html_name + " downloaded!"
    else:
        print "File " + html_name + " already exists!"
    return html_name



def parse_matome(matome_filename):
    """ Parse HTML from downloaded file. """
    book_list = [] # return this list
    soup = BeautifulSoup(open(matome_filename,'r').read(), "lxml")

    # Number of books
    book_num = int(soup.find("div", class_="matome_month_top_info_right_list_body").span.string)

    # div for each book
    book_divs = soup.find_all("div", class_="log_list_detail")[2:]
    for d in book_divs:
        # div for review of the book
        review_div = d.find("div", class_="log_list_comment")
        # str of review. trim space with strip()
        review_str = review_div.string.strip()
        # URL of the book
        book_url = d.find_all("a")[1].get("href")
        # ID of the book
        book_id = book_url[book_url.rfind("/")+1:]
        # title of the book
        book_title = d.find("div", class_="log_list_thumb_detail_title").a.string
        # append dict to the list
        book_list.append(dict(review=review_str, 
                              id=book_id, 
                              title=book_title))
    return book_list, book_num



def generate_hatena(booklist, booknum):
    """ Generate Hatena blog body & title from booklist, # of books
    """
    # Introduction text
    text1 = """
* はじめに
{0}年{1}月に読んだ{2}冊です。


各本について、タイトル・リンク・読書メーターに書いた感想（一部追加・修正あり・非ですます調）の順に記します。気に入った文の引用も。↓↓↓
====

* {1}月に読んだ本（タイトル一覧）
""".format(prev_month()[0], prev_month()[1], booknum)

    # Summaly text
    text2 = """
* おわりに

今月の個人的ランキングは、
- 
- 
- 
- 
- 
です。


先月分はこちら↓
"""    
    # write body file
    body_name = "body_%d%d.txt" % (prev_month()[0], prev_month()[1])
    with open(body_name, "w") as file:
        file.write(text1)
        # Title list
        for book in reversed(booklist):
            file.write("■" + book["title"].encode('utf-8')+"\n")

        file.write("\n以下詳細↓\n\n")
        # Review list
        for book in reversed(booklist):
            file.write("■" + book["title"].encode('utf-8') + "\n")
            file.write("[asin:" + book["id"] + ":detail]\n")
            file.write(book["review"].encode('utf-8') + "\n\n\n")
        file.write(text2)

    # write title file
    title_name = "title_%d%d.txt" % (prev_month()[0], prev_month()[1])
    with open(title_name, "w") as file:
        title_txt = "%d年%d月に読んだ本まとめ" % (prev_month()[0], 
                                                  prev_month()[1])
        file.write(title_txt)

    return body_name, title_name



if __name__ == "__main__":
    my_id = ***YOUR ID*** # Your ID of bookmeter.com
    url = "http://bookmeter.com/u/%d/matome" % my_id # URL of matome
    
    # download html
    filename = maybe_download(url)

    # parse html
    book_list, book_num = parse_matome(filename)

    # generate hatena blog body
    body_name, title_name = generate_hatena(book_list, book_num)
    print "Generated " + body_name + "!"
    print "Generated " + title_name + "!"
    
    # post to hatena blog
    post_command = "python ***YOUR post-hatena PATH***/post-hatena.py " + title_name + " " + body_name
    print "Executing: " + post_command + " ..."
    os.system(post_command)

    # send notification by IFTTT
    requests.post("https://maker.ifttt.com/trigger/***Your_event_name***/with/key/***Your_key***")
