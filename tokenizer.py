from sklearn.metrics import classification_report
from nltk import word_tokenize, pos_tag       
from nltk.stem import WordNetLemmatizer 
from nltk.stem.porter import *
from nltk.corpus import stopwords
from nltk.corpus import wordnet

class TheTokenizer(object):         
    def __init__(self, stem=False, lem=False, stopword=False):
        self.use_stemming = stem
        self.use_lemmatization = lem
        self.use_stopword_removal = stopword
        
        self.wnl = WordNetLemmatizer() 
        self.stemmer = PorterStemmer()  
        self.stopwords = set(stopwords.words('english'))
        
    def __call__(self, doc):
        if not self.use_stemming and not self.use_lemmatization: 
            return [t for t in word_tokenize(doc) if self.allow(t)]
        elif self.use_stemming and not self.use_lemmatization:
            return [self.stem_token(t) for t in word_tokenize(doc) if self.allow(t)]
        elif self.use_lemmatization and not self.use_stemming:
            return [self.lemmatize_token(t, pos) for t, pos in pos_tag(word_tokenize(doc)) if self.allow(t)]
    
    def stem_token(self, t):
        return self.stemmer.stem(t)
    
    def lemmatize_token(self, t, postag):
        return self.wnl.lemmatize(t, self.get_wordnet_pos(postag))
    
    def allow(self, t):
        if not self.use_stopword_removal:
            return True
        
        if t in self.stopwords:
            return False
        else:
            return True
        
    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN
