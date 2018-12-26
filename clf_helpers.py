from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import Pipeline

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from sklearn.metrics import classification_report, confusion_matrix

def get_most_important_features(vectorizer, model, n=5):
    index_to_word = {v:k for k,v in vectorizer.vocabulary_.items()}
    classes = {}
    for class_index in range(model.coef_.shape[0]):
        word_importances = [(el, index_to_word[i]) for i,el in enumerate(model.coef_[class_index])]
        sorted_coeff = sorted(word_importances, key = lambda x : x[0], reverse=True)
        tops = sorted(sorted_coeff[:n], key = lambda x : x[0])
        bottom = sorted_coeff[-n:]
        if model.coef_.shape[0] == 1:
            class_index = 'Positive class'
        classes[class_index] = {
            'tops': tops,
            'bottom': bottom
        }
    return classes

def get_metrics(y_test, y_predicted, cat):  
    # true positives / (true positives+false positives)
    precision = precision_score(y_test, y_predicted, pos_label=1,
                                    average='binary')             
    # true positives / (true positives + false negatives)
    recall = recall_score(y_test, y_predicted, pos_label=1,
                              average='binary')
    
    # harmonic mean of precision and recall
    f1 = f1_score(y_test, y_predicted, pos_label=1, average='binary')
    
    # true positives + true negatives/ total
    accuracy = accuracy_score(y_test, y_predicted)
    return accuracy, precision, recall, f1

def map_labels(cat, vector_of_indices):
    return [cat if ind == 1 else 'No'+cat for ind in vector_of_indices] 

def do_the_pipeline(pipeline, cats, dataframes, accuracy=True, report=True, top_features=True, rel=True, neigh=True):

    for cat in cats:

        dfs = dataframes[cat]
        print("\n>>> {}:".format(cat))
        train = dfs['Train']
        test = dfs['Test']
        
        for c in ['text-rel-tokens', 'text-neigh-tokens']:

                if 'rel' in c:
                        if not rel:
                                continue
                        else:
                                print("\n# RELATIONS")

                if 'neigh' in c:
                        if not neigh:
                                continue
                        else:
                                print("\n# NEIGHBOURS")
                
                pipeline.fit(train[c], train['label_num'])
                print("Vectorizer: W słowniku znajduje się {n} różnych słów".format(
                    n=len(pipeline.named_steps['vectorizer'].vocabulary_.keys())
                ))

                train_prediction = pipeline.predict(train[c])
                accuracy = pipeline.score(train[c], train['label_num'])

                print("- Zbiór treningowy:")
                if accuracy:
                    print("\tACCURACY: {n:2g}%".format(n=100.*accuracy))
                if report:
                    print(classification_report(
                        map_labels(cat, train['label_num']), 
                        map_labels(cat, train_prediction)
                    ))

                if top_features:
                    print("\tTop Features:\n", get_most_important_features(pipeline.named_steps['vectorizer'], pipeline.named_steps['clf']))
                
                test_prediction = pipeline.predict(test[c])
                accuracy = pipeline.score(test[c], test['label_num'])

                print("- Zbiór testowy:")
                if accuracy:
                    print("\tACCURACY: {n:2g}%".format(n=100.*accuracy))
                if report:
                    print(classification_report(
                        map_labels(cat, test['label_num']), 
                        map_labels(cat, test_prediction)
                    ))

def train_and_test(pipeline, train, test, data_column, label_num_column, accuracy = False, top_features = False, report = False):
    pipeline.fit(train[data_column], train[label_num_column])

    train_prediction = pipeline.predict(train[data_column])
    accuracy = pipeline.score(train[data_column], train[label_num_column])

    print("- Zbiór treningowy:")
    if accuracy:
        print("\tACCURACY: {n:2g}%".format(n=100.*accuracy))
    if report:
        print(classification_report(
           train[label_num_column], 
           train_prediction
        ))

    if top_features:
        print("\tTop Features:\n", get_most_important_features(pipeline.named_steps['vectorizer'], pipeline.named_steps['clf']))

    test_prediction = pipeline.predict(test[data_column])
    accuracy = pipeline.score(test[data_column], test[label_num_column])

    print("- Zbiór testowy:")
    if accuracy:
        print("\tACCURACY: {n:2g}%".format(n=100.*accuracy))
    if report:
        print(classification_report(
            test[label_num_column], 
            test_prediction
        ))