import numpy
import re
from konlpy import utils
from konlpy.tag import Komoran
import pandas as pd

# removes emjois and corrects some spacing
def clean(original_text):
    # remove extra spaces by spliting and joining by ' '
    clean_text = ' '.join(original_text.split())
    # replace extra punctuation such as ..., ??
    clean_text = re.sub('[.]+', '. ', clean_text)
    clean_text = re.sub('[!]+', '! ', clean_text)
    clean_text = re.sub('[?]+', '? ', clean_text)
    return clean_text

# tag
def tag_text(clean_text):
    # using Komoran tagger to tag POS
    komoran = Komoran(userdic='userdic.txt')
    text_tagged = komoran.pos(clean_text)
    return text_tagged

def format_text(text_tagged):
    # format the output
    text_formatted = ''
    for i in range(len(text_tagged)):
        text_formatted += ((text_tagged[i][0] + '/' + text_tagged[i][1] + ' '))
        i += 1
    text_lines = re.sub('(?<=[.!?])/\\w+', '/SF \\n', text_formatted)
    return text_lines

# data
def data_list(text_clean):
    df = pd.DataFrame(tag_text(text_clean), columns=['Word', 'Tag'])
    df = df.rename_axis('Index').reset_index()
    pd.options.mode.chained_assignment = None  # default='warn'
    return df
  
def data_df(text_clean):
    df = pd.DataFrame(tag_text(text_clean), columns=['Word', 'Tag'])
    df = df.rename_axis('Index').reset_index()
    pd.options.mode.chained_assignment = None  # default='warn'

    df_1 = df[df['Tag'].isin(['NNG', 'NNP', 'NNB', 'MAG', 'MAJ'])]
    df_2 = df[df['Tag'].isin(['VV', 'VA', 'VX', 'VCP', 'VCN', 'XSA', 'XSV'])]
    df_3 = df[df['Tag'] == 'XR']

    df_2['Word'] = df_2['Word'] + '다'
    #df_3['Word'] = df_3['Word'] + '하다'
    dfs = [df_1, df_2, df_3]
    
    df_all = pd.concat(dfs)
    df_all = df_all.sort_values(by=['Index'])
    # columns = Index, Word, Tag
    return df_all

def sttr(data_df):
    # initialization
    total_length = len(data_df.index)
    remainder = total_length % 100
    # comput TTR if number of content words is less than 100
    if total_length <= 100:
      return variety(data_df)
    
    # loop initialization: computer TTR for every 100 words
    ttr = 0
    i = 0
    counter = 0
    df = data_df.iloc[:, 1] # select 'Word' column
    
    while (total_length > 100):
      subset = df.iloc[i:i+99]
      ttr += len(pd.unique(subset))/100 # add up the number of unique words/ total words per seg
      
      i += 100
      total_length -= 100
      counter += 1
    
    if (remainder == 0):
      sttr = round(ttr/counter, 2)
    else:
      last_range = len(data_df.index)-100
      last = len(pd.unique(df.iloc[last_range:len(data_df.index)]))/100
      sttr = round((ttr + last)/(counter+1), 2)
    
    return sttr

def total_words(data_df):
    no_total_words = len(data_df.index)
    return no_total_words

def unique_words(data_df):
    no_unique_words = len(pd.unique(data_df['Word']))
    return no_unique_words

def variety(data_df):
    no_unique_words = len(pd.unique(data_df.iloc[:, 1]))
    no_total_words = len(data_df.index)
    lex_var = round(no_unique_words/no_total_words, 2)
    return lex_var

def complexity(text_lines):
    no_ec = len(re.compile('/EC').findall(text_lines))
    #no_etm = len(re.compile('/ETM').findall(text_lines))
    no_sentences = len(re.compile('\\n').findall(text_lines))
    sent_comp = round(no_ec/no_sentences, 1)
    return sent_comp
    
def ec(text_lines):
    no_ec = len(re.compile('/EC').findall(text_lines))
    return no_ec
  
def etm(text_lines):
    no_etm = len(re.compile('/ETM').findall(text_lines))
    return no_etm

def sentences(text_lines):
    no_sentences = len(re.compile('\\n').findall(text_lines))
    return no_sentences
  
def modifiers(text_lines):
    no_etm = len(re.compile('/ETM').findall(text_lines))
    no_sentences = len(re.compile('\\n').findall(text_lines))
    no_modif = round(no_etm/no_sentences, 1)
    return no_modif
  
    
# creates wordcloud data
def text_wc(df_all):
    df_freq = df_all.groupby(['Word']).size().reset_index(name='n') 
    #reset_index makes it a dataframe, not a series
    return df_freq
  
  
def search_vocab_list(formatted_text, vocab_df):
    vocab_list = {}
    for i in range(len(vocab_df['Pattern'])):
        pattern = re.compile(vocab_df['Pattern'].iloc[i])
        matches = pattern.findall(formatted_text)
        if len(matches) >= 1:
            vocab_list.update({vocab_df['Level'].iloc[i] + ',' +vocab_df['Word'].iloc[i] + ',' + vocab_df['Lesson'].iloc[i]: int(len(matches))})
        else:
            pass
    df_list = pd.DataFrame(vocab_list.items())
    #df_list.columns = ['Word', 'Count']
    if len(df_list) > 0: 
      return df_list
    else:
      return str("No results.")
