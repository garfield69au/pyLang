import string
import array
import re
import operator
from prettytable import PrettyTable
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, nps_chat
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
from nltk.collocations import *
from gensim import models, corpora
from gensim.models import LsiModel
from gensim.models.coherencemodel import CoherenceModel
import matplotlib.pyplot as plt




class MatchResult(object):
    
    def __init__(self:object, score:float, code:str, tokens:list):
        self.score = score
        self.code = code
        self.tokens = tokens
        
        
    def __repr__(self):
        return self.__str__()
 
    def __str__(self):
        return "{0}:{1}:{2}\n".format(self.code, self.score, self.tokens)


        
class GenericTextAnalysis(object):
    """
    ICD10TextSearch: Provodes a class for searching ICD10 code tables. It requires a dictionary of codes and descriptions and
    a search string written in natural language.
    This class uses the NLTK natural language tool kit.
    """
    
    def __init__(self:object):
        """
        Creates a set of stop words - these will be filtered out of the search string 
        """
        self.stop_words=set(stopwords.words("english"))
        self.stop_words.add("unspecified")
        self.stop_words.add("cardiologist")
        self.stop_words.add("ie")
        self.stop_words.add("i.e.")
        self.stop_words.add("data")
        self.stop_words.add("matrix")
        
        self.ps = PorterStemmer()
        self.wnl = WordNetLemmatizer()


    def plot_graph(self,doc_clean,start=2, stop=12, step=1):
        dictionary,doc_term_matrix=self.prepare_corpus(doc_clean)
        model_list, coherence_values = self.compute_coherence_values(dictionary, doc_term_matrix,doc_clean,
                                                                12, stop, start, step)
        # Show graph
        x = range(start, stop, step)
        plt.plot(x, coherence_values)
        plt.xlabel("Number of Topics")
        plt.ylabel("Coherence score")
        plt.legend(("coherence_values"), loc='best')
        plt.show()

    def prepare_corpus(self, doc_clean):
        """
        Input  : clean document
        Purpose: create term dictionary of our courpus and Converting list of documents (corpus) into Document Term Matrix
        Output : term dictionary and Document Term Matrix
        """
        # Creating the term dictionary of our courpus, where every unique term is assigned an index. dictionary = corpora.Dictionary(doc_clean)
        dictionary = corpora.Dictionary(doc_clean)
        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
        # generate LDA model
        
        return dictionary,doc_term_matrix        
    
    def create_gensim_lsa_model(self, doc_clean,number_of_topics,words):
        """
        Input  : clean document, number of topics and number of words associated with each topic
        Purpose: create LSA model using gensim
        Output : return LSA model
        """
        dictionary,doc_term_matrix=self.prepare_corpus(doc_clean)
        # generate LSA model
        lsamodel = LsiModel(doc_term_matrix, num_topics=number_of_topics, id2word = dictionary)  # train model
        print(lsamodel.print_topics(num_topics=number_of_topics, num_words=words))
        self.plot_graph(doc_clean)

        return lsamodel        

    def compute_coherence_values(self, dictionary, doc_term_matrix, doc_clean, number_of_topics, stop=12, start=2, step=3):
        """
        Input   : dictionary : Gensim dictionary
                  corpus : Gensim corpus
                  texts : List of input texts
                  stop : Max num of topics
        purpose : Compute c_v coherence for various number of topics
        Output  : model_list : List of LSA topic models
                  coherence_values : Coherence values corresponding to the LDA model with respective number of topics
        """
        coherence_values = []
        model_list = []
        for num_topics in range(start, stop, step):
            # generate LSA model
            model = LsiModel(doc_term_matrix, num_topics=number_of_topics, id2word = dictionary)  # train model
            model_list.append(model)
            coherencemodel = CoherenceModel(model=model, texts=doc_clean, dictionary=dictionary, coherence='c_v')
            coherence_values.append(coherencemodel.get_coherence())
        
        return model_list, coherence_values
        
        
            
    def analyse(self:object, searchstr) -> list:   
        #search_tokens = [self.tokenize(searchstr)]
    
        search_tokens = []
        search_tokens.extend(self.tokenize(s) for s in searchstr)
        tagged = []
        tagged.extend(nltk.pos_tag(s) for s in search_tokens)
        
        nouns=[]
        for s in tagged:
            l=[]
            for n in s:
                if (str(n[1]).startswith("N")):
                    l.append(str(n[0]))
            nouns.extend(l)
            
        print(nouns)
        #print(tagged)
        
        #match_list=list()
        #bigram_measures = nltk.collocations.BigramAssocMeasures()
        #trigram_measures = nltk.collocations.TrigramAssocMeasures()

        # change this to read in your data
        #finder = BigramCollocationFinder.from_words(search_tokens)

        # only bigrams that appear 3+ times
        #finder.apply_freq_filter(2) 

        # return the 10 n-grams with the highest PMI
        #match_list = finder.nbest(bigram_measures.pmi, 50)
                
        # Build a Dictionary - association word to numeric id
        
        #model=self.create_gensim_lsa_model(search_tokens,7,10)
        model=self.create_gensim_lsa_model([nouns],7,20)
        
        return {}
        
    
    def tokenize(self:object, text:str):
        tokenized_text = word_tokenize(text.strip().lower())
        cleaned_text = [self.ps.stem(t) for t in tokenized_text if t not in self.stop_words and re.match('[a-zA-Z\-][a-zA-Z\-]{2,}', t)]
        #cleaned_text = [self.wnl.lemmatize(t,'v') for t in tokenized_text if t not in self.stop_words]
        return cleaned_text
