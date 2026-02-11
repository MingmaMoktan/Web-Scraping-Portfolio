'''
We are learning to scrap the website using python.
We will be using the requests library to make HTTP requests and BeautifulSoup to parse the HTML content.
First, we need to install the required libraries:
pip install requests
pip install beautifulsoup4
pip install html5lib
Now, let's start with the basics of web scraping.
We will be scraping the website 'https://www.example.com' for demonstration purposes.
'''

# Here is the link to the documentation of BeautifulSoup:
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# And this is the link to the documentation of requests:
# https://docs.python-requests.org/en/latest/

import requests
from bs4 import BeautifulSoup

# Step 1: Make a GET request to the website
url = 'https://dm3339.pythonanywhere.com/'
r = requests.get(url)

html_content = r.content

'''
Step 2: Parse the HTML content using BeautifulSoup
This parsing also converts the HTML content into a BeautifulSoup object, 
which allows us to navigate and search the HTML tree easily.
'''
soup = BeautifulSoup(r.text, 'html.parser')

# Step 3: Extract and print the title of the webpage
title = soup.title
print(title)


'''
Types of used objects:
1. Tag: A Tag object corresponds to an HTML tag in the document. It has attributes
    like name, attributes, and contents. For example, <a href="https://www.example.com"> is a Tag object.
2. NavigableString: A NavigableString object represents the text within an HTML tag. For example, in <p>Hello World</p>, "Hello World" is a NavigableString object.
3. BeautifulSoup: The BeautifulSoup object represents the entire HTML document. It provides methods to
    navigate and search the HTML tree. For example, soup = BeautifulSoup(html_content, 'html.parser') creates a BeautifulSoup object.
4. Comment: A Comment object represents an HTML comment in the document. For example, <!-- This is a comment --> is a Comment object.
5. Doctype: A Doctype object represents the document type declaration in the HTML document. For example, <!DOCTYPE html> is a Doctype object.
6. ProcessingInstruction: A ProcessingInstruction object represents a processing instruction in the HTML document. For example, <?xml version="1.0" encoding="UTF-8"?> is a ProcessingInstruction object.
'''

'''
Types of used methods:
1. find(): This method is used to find the first occurrence of a tag in the HTML document. For example, soup.find('a') will return the first <a> tag in the document.

2. find_all(): This method is used to find all occurrences of a tag in the HTML
document. For example, soup.find_all('a') will return a list of all <a> tags in the document.

3. get_text(): This method is used to extract the text from a tag. For example
soup.find('p').get_text() will return the text inside the first <p> tag in the document.

4. attrs: This attribute is used to access the attributes of a tag. For example,soup.find('a').attrs will return a dictionary of attributes for the first <a> tag in the document.

5. name: This attribute is used to access the name of a tag. For example, soup.find('a').name will return 'a' for the first <a> tag in the document.

6. contents: This attribute is used to access the contents of a tag. For example, soup.find('p').contents will return a list of the contents inside the first <p> tag in the document.

7. parent: This attribute is used to access the parent tag of a tag. For example, soup.find('p').parent will return the parent tag of the first <p> tag in the document.

8. next_sibling: This attribute is used to access the next sibling tag of a tag. For example, soup.find('p').next_sibling will return the next sibling tag of the first <p> tag in the document.

9. previous_sibling: This attribute is used to access the previous sibling tag of a tag. For example, soup.find('p').previous_sibling will return the previous sibling tag of the first <p> tag in the document.

10. select(): This method is used to select tags using CSS selectors. For example, soup.select('a') will return a list of all <a> tags in the document.
'''

# Now lets practice all the methods and attributes mentioned above on the website 'https://www.example.com' and see how they work.

# 1. find()
first_a_tag = soup.find('a')
# print(first_a_tag)

# 2. find_all() and also use pretty print to make it more readable
all_a_tags = soup.find_all('a')
# print(all_a_tags)

# 3. get_text()
first_p_tag_text = soup.find('p').get_text()
# print(first_p_tag_text)

# 4. attrs
first_a_tag_attrs = soup.find('a').attrs
# print(first_a_tag_attrs)

# 5. name
first_a_tag_name = soup.find('a').name
# print(first_a_tag_name)

# 6. contents
first_p_tag_contents = soup.find('p').contents
# print(first_p_tag_contents)

# 7. parent
first_p_tag_parent = soup.find('p').parent
print(first_p_tag_parent)