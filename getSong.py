# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import webbrowser
import time
import sys
import random
from PyQt4 import QtCore, QtGui
from interface import Ui_Form
import createSong

def open_url(link):
    print "Opening Link: {}".format(link)
    resultsReq = urllib2.Request(link)
    if "mako" in link:
        webbrowser.open(link,autoraise=False)
        time.sleep(7)
    resultsReq=urllib2.urlopen(resultsReq)
    return resultsReq.read()


def get_lyrics(song_name):
    base_link="http://m.shironet.mako.co.il/"
    searchLink='{}search?q={}'.format(base_link,urllib.quote_plus(song_name))
    reg_exp_for_link=r"(.*)(/artist\?type=lyrics[^\"]*)(.*)"
    reg_exp_for_lyrics=r"""(.*)(artist_lyrics_text\">)(.+?)(</span>)+(.*)"""
    link_group=2
    lyrics_group=3

    #Open search windows, and get the list of all results
    result_html=open_url(searchLink).split()
    links_list=map(lambda x: re.search(reg_exp_for_link, x), result_html)
    links_list=filter(lambda x: x, links_list)
    links_list=map(lambda x: x.group(link_group), links_list)
    if not links_list:
        print "Couldn't find song! Choose another Song!"
        exit()

    #Get the lyrics of the first result
    lyrics_link='{}{}'.format(base_link,links_list[0])
    result_html=open_url(lyrics_link)
    lyrics=re.search(reg_exp_for_lyrics,result_html,re.DOTALL).group(lyrics_group).replace("<br>","")
    return lyrics


def searchAlternative(name):
    filter_past_male_url='http://milog.co.il/{}'.format(urllib.quote_plus(name))
    filter_result_html=open_url(filter_past_male_url)
    if filter_result_html.find("רבים") != -1 or filter_result_html.find("גוף שלישי") != -1 or filter_result_html.find("גוף שני") != -1 or name=="-":
        return name
    base_link='http://milog.co.il/{}/s/{}'.format(urllib.quote_plus(name),urllib.quote_plus('נרדפות'))
    reg_exp_for_alternative=r"(.+?)('sr_e_txt'>)(.+?)(</div>)(.*)"
    check_group=2
    check_str="לא התקבלו"
    result_group=3
    result_html=open_url(base_link)
    find_text=re.search(reg_exp_for_alternative,result_html,re.DOTALL)
    words=name
    if result_html.find(check_str) == -1:
        words=find_text.group(result_group).split(",")
        words=words[0].replace('<a href=\'/',"").replace(' class=\'sr_e_url\' onmousedown=\'_gaq.push(["_trackEvent"',"")
    return words

def searchVerse(name):
    base_link='http://milog.co.il/{}/s/{}'.format(urllib.quote_plus(name),urllib.quote_plus('חרוזים'))
    reg_exp_for_alternative=r"(.+?)('sr_e_txt'>)(.+?)(</div>)(.*)"
    check_group=2
    check_str="לא התקבלו"
    result_group=3
    result_html=open_url(base_link)
    find_text=re.search(reg_exp_for_alternative,result_html,re.DOTALL)
    words=name
    if result_html.find(check_str) == -1:
        words=find_text.group(result_group).split(",")
        words=words[0].replace('<a href=\'/',"").replace(' class=\'sr_e_url\' onmousedown=\'_gaq.push(["_trackEvent"',"")
    return words

def doVerse(original_lyrics):
    newSong=[]
    replace_bool=0;
    replace_word=""
    for line in original_lyrics.split('\n'):
        if not line or line == "\r":
           newSong.append("")
           continue
        line_array=line.split()
        if replace_bool == 0:
            replace_word=searchVerse(line_array[-1])
            replace_bool=1
        else:
            line_array[-1]=replace_word
            replace_word=""
            replace_bool=0
        newSong.append(" ".join(line_array).decode('utf-8'))
    return "\n".join(newSong)


class MyForm(QtGui.QMainWindow):
    original_lyrics = ""
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.OK.clicked.connect(self.OK1_func)
        self.ui.OK_2.clicked.connect(self.OK2_func)
        self.ui.OK_3.clicked.connect(self.OK3_func)
        self.ui.OK_4.clicked.connect(self.OK4_func)
        self.ui.word_changer.clicked.connect(self.word_changer_func)
##        self.ui.tabWidget.setCurrentIndex(0)

    def OK1_func(self):
        global original_lyrics
        song_name=self.ui.SongName.toPlainText()
        song_name=unicode(song_name.toUtf8(), encoding="UTF-8").encode('utf8')
        original_lyrics=get_lyrics(song_name)
        self.ui.Before.setPlainText(QtCore.QString.fromUtf8(original_lyrics))
        if self.ui.checkBox_3.isChecked():
            replace_alternative=1
        else:
             replace_alternative=0

        if self.ui.checkBox.isChecked():
            do_verse=1
        else:
            do_verse=0
        new_lyrics=manipulate_lyrics(original_lyrics,replace_alternative,do_verse)
        self.ui.After.setPlainText(QtCore.QString.fromUtf8(new_lyrics))

    def OK2_func(self):
        # Song 1 lyrics
        song_name1=self.ui.SongName_2_1.toPlainText()
        song_name1=unicode(song_name1.toUtf8(), encoding="UTF-8").encode('utf8')
        original_lyrics1=get_lyrics(song_name1)
        self.ui.Before_2_1.setPlainText(QtCore.QString.fromUtf8(original_lyrics1))
        # Song 2 lyrics
        song_name2=self.ui.SongName_2_2.toPlainText()
        song_name2=unicode(song_name2.toUtf8(), encoding="UTF-8").encode('utf8')
        original_lyrics2=get_lyrics(song_name2)
        self.ui.Before_2_2.setPlainText(QtCore.QString.fromUtf8(original_lyrics2))

        # Figure out length of new song, and  how many verses to take from each song
        verses1 = original_lyrics1.split('\r\n\r\n')
        verses2 = original_lyrics2.split('\r\n\r\n')
        num_of_verses1 = len(verses1)
        num_of_verses2 = len(verses2)
        song_length = (num_of_verses1 + num_of_verses2 + 1) / 2
        desired_num_of_verses1 = (song_length+1)/2
        desired_num_of_verses2 = song_length/2
        while (desired_num_of_verses1 > num_of_verses1):
            desired_num_of_verses1-= 1
            desired_num_of_verses2+= 1
        while (desired_num_of_verses2 > num_of_verses2):
            desired_num_of_verses2-= 1
            desired_num_of_verses1+= 1

        verses_to_take1 = random.sample(range(0, num_of_verses1), desired_num_of_verses1)
        verses_to_take1 = sorted(verses_to_take1, key=int)
        verses_to_take2 = random.sample(range(0, num_of_verses2), desired_num_of_verses2)
        verses_to_take2 = sorted(verses_to_take2, key=int)

        # Combining
        new_song = ""
        count = 0
        index1 = 0
        index2 = 0
        if (desired_num_of_verses1 >= desired_num_of_verses2):
            priority = 1
        else:
            priority = 2
        while (count < song_length):
            if (index1 >=  desired_num_of_verses1):
                take = 2
            elif (index2 >=  desired_num_of_verses2):
                take = 1
            elif (priority == 1):
                take = 1
            elif (priority == 2):
                take = 2

            if (take == 1):
                new_song += verses1[verses_to_take1[index1]] + "\r\n\r\n"
                index1+= 1
                count+= 1
                current = 2
                priority = 2
            if (take == 2):
                new_song += verses2[verses_to_take2[index2]] + "\r\n\r\n"
                index2+= 1
                count+= 1
                current = 1
                priority = 1

        self.ui.After_2.setPlainText(QtCore.QString.fromUtf8(new_song))


    def OK3_func(self):
        global original_lyrics
        # Get song lyrics
        song_name=self.ui.SongName_3.toPlainText()
        song_name=unicode(song_name.toUtf8(), encoding="UTF-8").encode('utf8')
        original_lyrics=get_lyrics(song_name)
        self.ui.Before_3.setPlainText(QtCore.QString.fromUtf8(original_lyrics))

    def OK4_func(self):
        first_word = self.ui.firstword.toPlainText()
        first_word = unicode(first_word.toUtf8(), encoding="UTF-8").encode('utf8')
        avg_sentence_length = self.ui.spinBox.value()
        song_length = self.ui.comboBox.currentIndex()

        song = createSong.create_lyrics(first_word, song_length, avg_sentence_length)
        self.ui.After_4.setPlainText(QtCore.QString.fromUtf8(song))


    def word_changer_func(self):
        global original_lyrics
        # Create list of words
        wordlist = []
        word_to_replace = self.ui.replace1.toPlainText()
        replacement_word = self.ui.replacewith1.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        word_to_replace = self.ui.replace2.toPlainText()
        replacement_word = self.ui.replacewith2.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        word_to_replace = self.ui.replace3.toPlainText()
        replacement_word = self.ui.replacewith3.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        word_to_replace = self.ui.replace4.toPlainText()
        replacement_word = self.ui.replacewith4.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        word_to_replace = self.ui.replace5.toPlainText()
        replacement_word = self.ui.replacewith5.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        word_to_replace = self.ui.replace6.toPlainText()
        replacement_word = self.ui.replacewith6.toPlainText()
        if ( word_to_replace != "" and replacement_word != "" ):
           wordlist += [word_to_replace, replacement_word]
        print(len(wordlist))

        # Replace the words in the lyrics
        result_lyrics = str(original_lyrics)


        # Using a temporary replacement to allow word switches
        for i in range( 0, len(wordlist), 2):
            word_to_replace = wordlist[i].toUtf8()
            replacement_word = "QQQ" + str(i)
            result_lyrics = result_lyrics.replace(word_to_replace,replacement_word)

        for i in range( 0, len(wordlist), 2):
            word_to_replace = "QQQ" + str(i)
            replacement_word = wordlist[i+1].toUtf8()
            result_lyrics = result_lyrics.replace(word_to_replace,replacement_word)

        self.ui.After_3.setPlainText(QtCore.QString.fromUtf8(result_lyrics))


## def manipulate_lyrics(original_lyrics, replace_bool,verse_bool):
##    print original_lyrics
##    result_str=""
##    for line in original_lyrics.split('\n'):
##        if not line:continue
##        for word in line.split():
##            rand_int = random.randint(1,100)
##            if (rand_int > synonym_precent): continue
##
##            result=searchAlternative(word)
##            if not result:
##                result=searchVerse(word)
##                print "Choose verse: Original: {}, New: {}".format(word,result)
##            if not result:
##                print "Kept Original: {}".format(word)
##                result=word
##
##            result_str+=" "
##            result_str+=result
##        result_str += "\n"
##    print result_str
##    return result_str
##   return original_lyrics

def manipulate_lyrics(original_lyrics, replace_bool,verse_bool):
    result_str=original_lyrics

    if replace_bool == 1:
        result_str=""
        for line in original_lyrics.split('\n'):
            if not line or line == "\r" or line =="\r\n":
                if verse_bool:
                    result_str+="\n\n"
                else:
                    result_str+="\n"
                continue
            for word in line.split():
                result=searchAlternative(word)
                result_str += " "
                result_str += result
            result_str += "\n"
    if verse_bool == 1:
        result_str = doVerse(result_str)
    return result_str


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())

