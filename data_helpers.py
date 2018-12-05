import re
import operator


def extend_dataframe(df):
    # add or replace?
    
    for i in range(df['text'].count()):
        
        text = df['text'].get(i)
        for word in text.split():

            if '\\' in word or '/' in word:
                df.at[i, 'text'] += ' system-path'

            if word.endswith('()'):
                df.at[i, 'text'] += ' function-name'

            file = re.search('.*\.([A-Za-z]{3})$', word)
            if file:
                df.at[i, 'text'] += ' {}-file'.format(file.group(1))

            cmd = re.search(r'^-{1,2}[a-zA-Z]+', word)
            if cmd:
                df.at[i, 'text'] += ' cmd-param'

            ip = re.search(r'[0-9]+?\.[0-9]+?\.[0-9]+?.\.[0-9]+', word)
            if ip:
                df.at[i, 'text'] += ' ip-address'
            
        df.at[i, 'text'] = df.at[i, 'text'].lower()

    return df

def clean_dataframe(df):
    columns = ['text-neigh-processed', 'text-rel-processed']
    
    for c in columns:
        for i in range(df[c].count()):
#             text = df[c].get(i)
            text = df.at[i, c]
            for word in text.split():

                if '\\' in word or '/' in word:
                    text = text.replace(word, 'system-path ')

                if word.endswith('()'):
                    text = text.replace(word, 'function-name')

                file = re.search('[^\s]+\.([A-Za-z]{3})', word)
                if file:
                    replacement = ' {}-file'.format(file.group(1))
                    if word in text:
                        text = text.replace(word, replacement)
                    else:
                        text += replacement

                cmd = re.search(r'^-{1,2}[a-zA-Z]+', word)
                if cmd:
                    text = text.replace(word, 'cmd-param')

                ip = re.search(r'[0-9]+?\.[0-9]+?\.[0-9]+?\.[0-9]+', word)
                if ip:
                    text = text.replace(word, 'ip-address')

                var = re.search(r'%[a-zA-Z0-9]+%', word)
                if var:
                    text = text + " some-variable"

                index = re.search(r'^\([0-9]+\)$', word)
                if index:
                    text = text.replace(word, "")

                year = re.search(r'^[0-9]{4}$', word)
                if year:
                    text = text.replace(word, "")
                    
                hash_s = re.search(r'^[0-9a-zA-Z]{31,}$', word)
                if hash_s:
                    text = text.replace(word, 'hash')

            df.at[i, c] = text.lower()
        
    return df

def clean_sentence(text):
    
    for word in text.split():

        if '\\' in word or '/' in word:
            text = text.replace(word, 'system-path ')

        if word.endswith('()'):
            text = text.replace(word, 'function-name')

        file = re.search('[^\s]+\.([A-Za-z]{3})', word)
        if file:
            replacement = ' {}-file'.format(file.group(1))
            if word in text:
                text = text.replace(word, replacement)
            else:
                text += replacement

        cmd = re.search(r'^-{1,2}[a-zA-Z]+', word)
        if cmd:
            text = text.replace(word, 'cmd-param')

        ip = re.search(r'[0-9]+?\.[0-9]+?\.[0-9]+?\.[0-9]+', word)
        if ip:
            text = text.replace(word, 'ip-address')

        var = re.search(r'%[a-zA-Z0-9]+%', word)
        if var:
            text = text + " some-variable"

        index = re.search(r'^\([0-9]+\)$', word)
        if index:
            text = text.replace(word, "")

        year = re.search(r'^[0-9]{4}$', word)
        if year:
            text = text.replace(word, "")

        hash_s = re.search(r'^[0-9a-zA-Z]{31,}$', word)
        if hash_s:
            text = text.replace(word, 'hash')
            
    return text

def get_top_occuring_words(X_train_counts, how_many_words, vectorizer, train):
    id_to_word = {v: k for k, v in vectorizer.vocabulary_.items()} # stwórz mapowanie pozycji wektora bag-of-words na konkretne słowa
    cx = X_train_counts.tocoo()
    category_word_counts = dict()      # słownik, w którym przeprowadzimy zliczanie
    
    for doc_id, word_id, count in zip(cx.row, cx.col, cx.data):
        category = train.iloc[doc_id]['label']  # w category znajduje się idetyfikator kategorii dla aktualnego dokumentu, zapisujemy go
        word = id_to_word[word_id]              # w word - aktualne słowo z dokumentu
                                                # mamy też liczność wystąpienia danego słowa w dokumencie (gdzie? :) )
            
        if category not in category_word_counts.keys(): # stwórzmy słownik z kategoriami jako kluczami
            category_word_counts[category] = dict()     # jeśli widzimy nową kategorię - dodajemy do słownika

        if word not in category_word_counts[category]: # w ramach każdej kategorii będziemy zliaczać słowa
            category_word_counts[category][word] = 0.0 # jeśli aktualne słowo jeszce nie zotało uwzględnione w kategorii - zainicjujmy jego licznik liczbą 0

        category_word_counts[category][word] += count
        
    result = []
    for category_name in category_word_counts.keys(): # wyświetl nazwy kategorii i n najczęściej występujących w nich słów
        sorted_cat = sorted(category_word_counts[category_name].items(), key=operator.itemgetter(1), reverse=True) # posortowany dict() słowo -> liczność, wg liczności, malejąco
        result.append([category_name, sorted_cat[:how_many_words]])
#         print(category_name)
#         print(sorted_cat[:how_many_words])
#         print("{cat}: {top}".format(cat=category_name, top=[word for word, count in sorted_cat[:how_many_words]])) # wyświetl nazwę kategorii i top n słów

    return result