#!/usr/bin/python
# Filename: dl.py
# Execute cp ./dl.py /usr/bin/dl everytime a change was made.

import urllib2
import urllib
import re
import sys
import os

pdf_dir_default = '/home/xinxing/Documents/paper/pdf/'
bibtex_path_default = '/home/xinxing/Documents/paper/paperlib.bib'



class paper:
    def __init__(self, journal, volume, page):
        self.journal = journal
        self.volume = volume
        self.page = page
        self.search_url = ''
        self.journal_url = ''

    def set_query_args(self):
        self.query_args = {}
        self.query_args['journal'] = self.journal
        self.query_args['volume'] = self.volume
        self.query_args['article'] = self.page

    def get_abs_url(self, query_args):
        encoded_args = urllib.urlencode(query_args)
##for nature physics, this url should be: http://www.nature.com/search/executeSearch?sp-advanced=true&sp-q-9%5BNPHYS%5D=1&sp-q-4=10&sp-q-6=394
        self.abs_url = self.search_url + encoded_args

    def get_abs_html(self, abs_url):
        self.abs_html = urllib2.urlopen(abs_url).read()

    def get_pdf_path(self):
        self.pdf_name = self.journal + self.volume +'.'+ self.page + '.pdf'
        self.pdf_path = pdf_dir_default + self.pdf_name
    
    def get_pdf_url(self, abs_html):
        temp_str1 = re.search('href=\".*\">PDF', abs_html).group()[6:-5]
        self.pdf_url = self.journal_url + temp_str1

    def download_pdf(self, pdf_url, pdf_path):
        pdf_data = urllib2.urlopen(self.pdf_url).read()
        f = open(self.pdf_path, 'w')
        f.write(pdf_data)
        f.close()

    def get_bibtex_url(self, abs_html):
        temp_str1 = re.search('href=\".*\">Export Citation', abs_html).group()[6:-17]
        self.bibtex_url = self.journal_url + temp_str1

    def download_bibtex_data(self, bibtex_url):
        self.bibtex_data = urllib2.urlopen(bibtex_url).read()

    def download_bibtex_data_from_ris(self, ris_url):
        ris_data = urllib2.urlopen(ris_url).read()
        f = open('./temp.ris', 'w')
        f.write(ris_data)
        f.close()
        os.system('ris2xml ./temp.ris > ./temp.xml')
        os.system('xml2bib -w ./temp.xml > ./temp.bib')
        f = open('./temp.bib', 'r')
        self.bibtex_data = f.read()
        f.close()

    def insert_pdf_link(self, bibtex_data, pdf_name):
        bibtex_file_link = '  file =\t{:pdf/' + pdf_name + ':PDF},'
        bibtex_list =  bibtex_data.split('\n')
        bibtex_list.insert(-4,  bibtex_file_link)
        self.bibtex_data = '\n'.join(bibtex_list)

    def save_bibtex_data(self, bibtex_data):
        f = open(bibtex_path_default, 'a+')
        f.write(bibtex_data)
        f.close()

    def download(self):
        print 'Searching for the abstract page...'
        self.set_query_args()
        self.get_abs_url(self.query_args)
        self.get_abs_html(self.abs_url)
        print 'Downloading pdf file...'
        self.get_pdf_url(self.abs_html)
        self.get_pdf_path()
        self.download_pdf(self.pdf_url, self.pdf_path)
        print 'Downloading bibtex...'
        self.get_bibtex_url(self.abs_html)
        self.download_bibtex_data(self.bibtex_url)
        self.insert_pdf_link(self.bibtex_data, self.pdf_name)
        self.save_bibtex_data(self.bibtex_data)
        print 'Done.'


class PhysicalReview(paper):
    def __init__(self, journal, volume, page):
        paper.__init__(self, journal, volume, page)
        self.search_url = 'http://link.aps.org/citesearch?'
        self.journal_url = 'http://journals.aps.org'

class nature(paper):
    def __init__(self, journal, volume, page):
        paper.__init__(self, journal, volume, page)
        self.search_url = 'http://www.nature.com/search/executeSearch?'
        self.journal_url = 'http://www.nature.com'

    def set_query_args(self):
        self.query_args = {}
        self.query_args['sp-advanced'] = 'true'
        self.query_args['sp-q-4'] = self.volume
        self.query_args['sp-q-6'] = self.page

    def get_abs_url(self, query_args):
        paper.get_abs_url(self, query_args)
        if self.journal == 'nphys':
            self.abs_url = self.abs_url + '&sp-q-9%5BNPHYS%5D=1'
        abs_html_data = urllib2.urlopen(self.abs_url).read()
        temp_str1 = re.search('\n.*result-title.*', abs_html_data).group()
        temp_str2 = re.search('href=\"[^\"]*\"', temp_str1).group()[6:-1]
        self.abs_url = temp_str2

    def get_pdf_url(self, abs_html):
        temp_str1 = re.search('href=\"[^\"]*.pdf', abs_html).group()[6:]
        self.pdf_url = self.journal_url + temp_str1

    def get_bibtex_url(self, abs_html):
        temp_str1 = re.search('href=\"[^\"]*ris\"', abs_html).group()[6:-1]
        self.bibtex_url = self.journal_url + temp_str1

    def download_bibtex_data(self, bibtex_url):
        self.download_bibtex_data_from_ris(bibtex_url)

class science(paper):
    def __init__(self, journal, volume, page):
        paper.__init__(self, journal, volume, page)
        self.search_url = 'http://www.sciencemag.org/search?'
        self.journal_url = 'http://www.sciencemag.org'

    def set_query_args(self):
        self.query_args = {}
        self.query_args['submit'] = 'yes'
        self.query_args['volume'] = self.volume
        self.query_args['firstpage'] = self.page

    def get_abs_url(self, query_args):
        paper.get_abs_url(self, query_args)
        abs_html_data = urllib2.urlopen(self.abs_url).read()
        temp_str1 = re.search('href=\"[^\"]*abstract', abs_html_data).group()[6:]
        self.abs_url = self.journal_url + temp_str1

    def get_pdf_url(self, abs_html):
        temp_str1 = re.search('content=\"[^\"]*full.pdf', abs_html).group()[9:]
        self.pdf_url = temp_str1

    def get_bibtex_url(self, abs_html):
        temp_str1 = re.search('href=\"[^\"]*\">Download Citation', abs_html).group()[6:-19]
        self.bibtex_url = self.journal_url + temp_str1
        citation_html = urllib2.urlopen(self.bibtex_url).read()
        temp_str1 = re.search('gca=[^\"]*\">BibTeX', citation_html).group()[:-8]
        self.bibtex_url = self.journal_url + '/citmgr?type=bibtex&' + temp_str1

if __name__ == '__main__':
    download_flag = 1
    if len(sys.argv) == 2:
        if sys.argv[1] == '-h':
            print 'Article automatical download tool. Download both pdf file and bibtex. \nExample: dl JOURNAL VOLUME PAGE \nwhere JOURNAL could be:\n\tPRL\n\tPRA-E\n\tRMP\n\tnature\n\tnphys (nature physics)\n\tscience\n\t(to be continue)\n'
    elif len(sys.argv) == 4:
        journal = sys.argv[1]
        volume = sys.argv[2]
        page = sys.argv[3]
    
        if (journal == 'nature') | (journal == 'nphys'):
            newpaper = nature(journal, volume, page)
        elif (journal == 'PRL') | (journal == 'PRA') | (journal == 'PRB') | (journal == 'PRC') | (journal == 'PRD') | (journal == 'PRE') | (journal == 'RMP'):
            newpaper = PhysicalReview(journal, volume, page)
        elif (journal == 'science'):
            newpaper = science(journal, volume, page)
         
        else:
            print 'Invalid journal name!'
            download_flag = 0
 
        if download_flag == 1:
            newpaper.download()

#    newpaper = science('science','275' , '637')
#    newpaper.download()

