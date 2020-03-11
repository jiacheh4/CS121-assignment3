from Indexer import *
import numpy as np
import pickle
import json
import math
from string import ascii_lowercase
from nltk.stem import PorterStemmer
from operator import itemgetter

TOTAL_UNIQUE_DOC = 55392

class QueryProcessor():
    """ a query processor
        take the npy file and read it
        take the query words and process the query using the file
        each time after processing the query, create a QueryResult object
        and store them in all_result
    """ 

    def __init__(self):
        """ format of dictionaries: 
                self.doc_id: "doc_id": "url"
                self.index: "word": [Posting Objects]  
        """
        self.fp = [open("split_index_%s.txt"%x, 'r') for x in ascii_lowercase]  #Open all the split_index_files simulataneously 
        self.all_results = {}
        self.urlid = []
        self.query_dict = {}
        self.query_score = {}
        self.doc_score = {}
        self.doc_length = {}
    

    def search(self,words):
        """ the search component
            print out the results for this query
        """
        words = words.split()
        if len(words) > 1:
            self.query_tf_idf(words)
            for word in words:
                word = PorterStemmer().stem(word)
                fp_num = ord(word[0]) - 97
                self._process(word, fp_num)
        
            self.cosine_score()
            self.urlid = sorted(self.doc_score.items(), key = lambda kv:kv[1], reverse=True)
            
        elif len(words) == 1:
            fp_num = ord(words[0][0]) - 97
            self.rank_single_word(words[0], fp_num)
            self.urlid = sorted(self.all_results.items(), key = lambda kv:kv[1], reverse=True)
        else:
            return []

        return self.urlid[:20]
    
    def rank_single_word(self, word, fp_num):
        
        while True:
            word_dict = {}
            line = self.fp[fp_num].readline() #read the correct splited_index file
            if word in line:
                word_dict = json.loads(line)
                if (list(word_dict.keys())[0]) != word:
                    continue
                #print(word_dict)
                for i in (sorted(word_dict[word], key=itemgetter(1), reverse=True)[:75]):
                    if i[0] in self.all_results:
                        self.all_results[i[0]] += i[1]
                    else:
                        self.all_results[i[0]] = i[1]  
            if not line:
                break
    
    def cosine_score(self):
        """ 
        Compute the cosine similarity 
        between query and the document
        """
        for i in self.all_results:      
            length = 0
            for j in self.all_results[i]:

                length += self.all_results[i][j] ** 2
            length = math.sqrt(length)
           
            for j in self.all_results[i]:
                self.all_results[i][j] = self.all_results[i][j]/length
        
        for doc in self.all_results:
            score = 0
            for query_word in self.query_score:
                if query_word in self.all_results[doc]:
                    score += self.all_results[doc][query_word] * self.query_score[query_word]
            self.doc_score[doc] = score

    def query_tf_idf(self, words):
        """ 
        Compute the Normalized tf_idf Score 
        words for Query 
        """
        for word in words:
            word = PorterStemmer().stem(word)
            if word in self.query_dict:
                self.query_dict[word] += 1
            else:
                self.query_dict[word] = 1
        
        for token in self.query_dict:
            df = self.query_dict[token]
            idf = math.log(TOTAL_UNIQUE_DOC/df)
            tf = self.query_dict[token]
            tf_idf = (1 + math.log(tf))* idf 
            self.query_score[token] = tf_idf
        
        length = 0
        for word in self.query_score:
            length += self.query_score[word] ** 2
        
        length = math.sqrt(length)
        for word in self.query_score:
            self.query_score[word] = self.query_score[word]/length

    def _process(self,word, fp_num):
        """ get the query words as a list 
            process the query words, add result to all_result list
            return this single result as a result object
        """
        while True:
            word_dict = {}
            line = self.fp[fp_num].readline() #read the correct splited_index file
            if word in line:
                word_dict = json.loads(line)
                if (list(word_dict.keys())[0]) != word:
                    continue
                for i in (sorted(word_dict[word], key=itemgetter(1), reverse=True)[:75]):
                    if i[0] in self.all_results:
                        self.all_results[i[0]].update({word:i[1]})
                    else:
                        self.all_results[i[0]] = {word:i[1]}
                    
            if not line:
                break


    
