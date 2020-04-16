# -*- coding: utf-8 -*-
from underthesea import pos_tag
from underthesea import word_tokenize
from underthesea import sent_tokenize
from underthesea import chunk
from underthesea import ner
import csv
import collections
def getDataFromCSV(filename="data.csv"):
    with open(filename, "r") as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)] 
    return a
listbook = getDataFromCSV()

def getBookFromName(name):
    list_ans = []
    list_book_return = []
#     print(category.lower().split())
#     print(len(category.lower().split()))
    search_split = name.lower().split()
    try:
        if len(search_split) == 1:
            for book in listbook:
                if search_split[0] in book["name"].lower():
                    list_ans.append(book["name"])
        else:
            for word in search_split:
                for book in listbook:
                    if word in book["name"].lower():
                        list_ans.append(book["name"])
    #         print(list_ans)
        if len(list_ans) > 0:
            list_ans=collections.Counter(list_ans)
    #             print(list_ans.most_common()[0][1])
            most_occurence_number = list_ans.most_common()[0][1]
    #             print(most_occurence_number)
            list_ans_ = [i for i in list_ans.most_common() if int(i[1]) >= most_occurence_number]

            for bookname in list_ans_:
                for book in listbook:
                    if bookname[0] in book["name"]:
                        list_book_return.append(book)
            return list_book_return
        else:
            return []
    except Exception as e:
        print(e)
        return []

def getBookFromCategory(category):
    list_ans = []
    list_book_return = []
    search_split = category.lower().split()
    try:
        if len(search_split) == 1:
            for book in listbook:
                if search_split[0] in book["product_category"].lower():
                    list_ans.append(book["name"])
        else:
            for word in search_split:
                for book in listbook:
                    if word in book["product_category"].lower():
                        list_ans.append(book["name"])
    #         print(list_ans)
        if len(list_ans) > 0:
            list_ans=collections.Counter(list_ans)
    #             print(list_ans.most_common()[0][1])
            most_occurence_number = list_ans.most_common()[0][1]
    #             print(most_occurence_number)
            list_ans_ = [i for i in list_ans.most_common() if int(i[1]) >= most_occurence_number]

            for bookname in list_ans_:
                for book in listbook:
                    if bookname[0] in book["name"]:
                        list_book_return.append(book)
            return list_book_return
        else:
            return []
    except Exception as e:
        print(e)
        return []


def getBookFromAuthor(author):
    list_ans = []
    list_book_return = []
#     print(category.lower().split())
#     print(len(category.lower().split()))
    search_split = author.lower().split()
    try:
        if len(search_split) == 1:
            for book in listbook:
                if search_split[0] in book["author"].lower():
                    list_ans.append(book["name"])
        else:
            for word in search_split:
                for book in listbook:
                    if word in book["author"].lower():
                        list_ans.append(book["name"])
    #         print(list_ans)
        if len(list_ans) > 0:
            list_ans=collections.Counter(list_ans)
    #             print(list_ans.most_common()[0][1])
            most_occurence_number = list_ans.most_common()[0][1]
    #             print(most_occurence_number)
            list_ans_ = [i for i in list_ans.most_common() if int(i[1]) >= most_occurence_number]

            for bookname in list_ans_:
                for book in listbook:
                    if bookname[0] in book["name"]:
                        list_book_return.append(book)
            return list_book_return
        else:
            return []
    except Exception as e:
        print(e)
        return []

def getFromAuthor(user_input):
    chunk_list = ner(user_input)
    search_seed = ""
    for words in chunk_list:
        if (words[1]== 'Np'):
            search_seed += words[0] + " "
    # print(search_seed)
    return (getBookFromAuthor(search_seed))

def getListCategory():
    category = []
    for book in listbook:
        temp = book['product_category'].replace(">", "").replace("&","").replace("'s","").replace(",","")
        category+=temp.split()
    return set(category)

def outputProcess(listbook):
    try:
        if listbook != None:
            for book in listbook:
                print("\tTên sách: "+book['name'])
                print("\tGiá: " + book['sale_price'] + " "+book['currency'])
                print("\tTác giả:"+book['author'])
                print("\tThể loại: "+book['product_category'])
                print("_"*32)
            pass
    except Exception as e:
        print(e)
        return None


categories = ['Activities', 'Animals', 'Arts', 'Bibles', 'Books',
 'Children', 'Christian', 'Cookbooks', 'Crafts', 'Criticism',
 'Design', 'Education', 'Facts', 'Fiction', 'Food', 'Games',
 'Gardening', 'Genre', 'Government', 'Growing Up', 'History',
 'Hobbies', 'Home', 'International', 'Landscape', 'Life',
 'Literature', 'Living', 'Music', 'Photography', 'Politics',
 'Reference', 'Regional', 'Sciences', 'Social', 'Wine', 'Cookbooks, Food & Wine']
def getFromCategory(user_input):
    list_categories_in_input = [i for i in categories if i.lower() in user_input.lower()]
    if len(list_categories_in_input) == 0:
        return 0
    else:
#         print(" ".join(list_categories_in_input))
        return (getBookFromCategory(" ".join(list_categories_in_input)))

def getFromName(user_input):
    blacklist = ["bao nhiêu", "tiền", "giá của", "tác phẩm", "cuốn" ,"sách", "thế", "giá", "là"]
    pchunk = chunk(user_input)
#     print(pchunk)
    list_names_in_input = [i[0] for i in pchunk if i[0].lower() not in blacklist] 
    if len(list_names_in_input) == 0 :
        return None
    else:
        return (getBookFromName(" ".join(list_names_in_input)))
threshold_n = 4

def handle(user_input, seq_answer):
    print(">>>", seq_answer)
    if "thể loại" in user_input:
        list_book = getFromCategory(user_input)
        if len(list_book) > 0:
            return (list_book, "Các sách thể loại này là:")
        return (list_book, "Bạn muốn tìm theo thể loại nào vậy?")

    
    elif "những tác phẩm của" in seq_answer:
        list_book = getFromAuthor(user_input)
        if len(list_book) > 0:
            return (list_book, "Các tác phẩm của nhà văn là:")
        return (list_book, "Bạn muốn tìm theo tác giả nào vậy?")

    elif "giá của sản phẩm là" in seq_answer:
        list_book = getFromName(user_input)
        # print(list_book)
        if len(list_book) > 0:
            return (list_book, "Giá của sản phẩm là")
        return (list_book, "Bạn muốn tìm giá của sản phẩm nào vậy?")


    elif len(user_input.split()) <= threshold_n:
        print(">>>case", "threshold_n")
        list_book = getBookFromName(user_input)
        if len(list_book) > 0:
            return list_book, "Có phải bạn muốn tìm sách tên:"
            
        list_book = getBookFromAuthor(user_input)
        if len(list_book) > 0:
            return list_book, "Có phải bạn muốn tìm sách theo tác giả:"

        list_book = getBookFromCategory(user_input)
        if len(list_book) > 0:
            return list_book, "Có phải bạn muốn tìm sách theo thể loại:"


        return [], seq_answer

    else:
        # print("case", "?")
        return([], seq_answer)


# print(getFromAuthor("Các tác phẩm của nhà văn Brown?"))