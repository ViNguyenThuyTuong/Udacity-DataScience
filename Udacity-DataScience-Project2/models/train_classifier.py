import sys
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine

import pandas as pd
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import re
import nltk


from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

import pickle
nltk.download(['punkt', 'wordnet'])


def load_data(database_filepath):
    '''
    Loads data from SQLite database.
    
    Parameters:
        database_filepath: string
    
    Returns:
        X: message column
        Y: labels
    '''
    # load data from database 
    engine = create_engine(f'sqlite:///{database_filepath}')
    df = pd.read_sql_table("disaster_messages", con=engine)
    X = df['message']
    Y = df.iloc[:, 4:]
    return X, Y


def tokenize(text):
    '''
    Tokenize the text
    Params:
        text: string 
    Return: list of substrings   
    '''
    text = text.lower()
    return word_tokenize(text)


def build_model():
    '''
    Build model with pipeline and GridSearchCV
    Return:
        cv: model with GridSearchCV
    '''
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(DecisionTreeClassifier()))
    ])
    parameters = {
        'vect__max_df': [10, 20],
        'vect__max_features': (5, 10),
        'clf__estimator__max_depth' : [20, 30, 50]
    }

    cv = GridSearchCV(pipeline, param_grid=parameters)
    return cv


def evaluate_model(model, X_test, Y_test):
    '''
    Evaluate model using classification_report function and calculate Average accuracy
    Params:
        model: model
        X_test: test set
        Y_test: labels for test set X_test
    '''
    Y_pred = model.predict(X_test)
    for index, value in enumerate(Y_test):
        print(value, classification_report(Y_test[value], Y_pred[:, index]))
    print('Average accuracy: ', (Y_pred == Y_test).mean().mean())


def save_model(model, model_filepath):
    '''
    Save model as a pickle file
    '''
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print(database_filepath)
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()