# -*- coding: utf-8 -*-
import os
import random

def read_all_lyrics():
    lyrics_location="./lyrics_db"
    all_files=os.listdir(lyrics_location)
    ans=""
    for file_loc in all_files:
        f=open(lyrics_location+'/'+file_loc,"r")
        ans+=f.read()
        ans+=" "
    return ans


def create_word_probability_map(all_lyrics):
    #Initiate map with zeros
    all_words=all_lyrics.replace("\n"," ").split()
    l = len(all_words)

    #Initiate map
    ans={}
    for main_word in set(all_words):
        ans[main_word]={}
        for sub_word in all_words:
            ans[main_word][sub_word]=0

    #Initiate table
    for main_word in all_words:
        for index, sub_word in enumerate(all_words):
            if main_word == sub_word and index < (l - 1):
                add_word=all_words[index+1]
                ans[main_word][add_word]+=1
    return ans


def find_next_word(words):
    ans_first_value=-100
    ans_first_key=""

 #first number
    for key in words:
        value=words[key]
        if value>ans_first_value:
            ans_first_value=value
            ans_first_key=key


 #second number
    ans_sec_value=-100
    ans_sec_key=""
    for key in words:
        value=words[key]
        if value>ans_sec_value and value!=ans_first_value:
            ans_sec_value=value
            ans_sec_key=key



    lotto=[]
    if ans_first_value >= 0 :
        lotto.append(ans_first_key)
    if ans_sec_value > 0 :
        lotto.append(ans_sec_key)

    return random.choice(lotto)


def create_lyrics(first_word,plan,num_words_in_line):
    if plan == 0:
        num_byte,num_lines=2,3
    elif plan == 1:
        num_byte,num_lines=3,4
    else:
        num_byte,num_lines=4,5
    num_decrease=2
    all_lyrics=read_all_lyrics()
    probability_map=create_word_probability_map(all_lyrics)
    song=""
    if first_word in all_lyrics.split():
        add_word=first_word
    else:
        add_word=random.choice(all_lyrics.split())

    #print probability_map
    for i in range(0,num_byte):
        for k in range (0,random.randrange(num_lines-2,num_lines+2)):
            for j in range (0,random.randrange(num_words_in_line-3,num_words_in_line+3)):
                next_add_word=find_next_word(probability_map[add_word])
                probability_map[add_word][next_add_word]-=num_decrease
                song+=add_word
                song+=" "
                add_word=next_add_word
            song += "\n"
        song += "\n"
        song += "\n"
##    print song
    return song





if __name__ == "__main__":
    create_lyrics("hi",1,10)

