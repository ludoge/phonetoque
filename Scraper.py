
# coding: utf-8

# In[41]:


from lxml import html
import requests
import re


# In[42]:


def pronunciations_from_wiktionary(word):
    page = requests.get('https://en.wiktionary.org/wiki/%s' %word)
    tree = html.fromstring(page.content)
    pronunciation = []
    for i in range(1,10):
        pronunciation = pronunciation + tree.xpath("//*[@id=\"mw-content-text\"]/div/ul[1]/li[%s]/span/text()" %i)
    regexp = re.compile(r'^/.*/$')
    pronunciation = [x for x in pronunciation if regexp.search(x)]
    return(pronunciation)


# In[43]:


print(pronunciations_from_wiktionary('python'))

