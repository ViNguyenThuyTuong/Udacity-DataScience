import sys
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    '''
    Loads and merges 2 datasets.
    
    Parameters:
        messages_filepath: string
        categories_filepath: string
    
    Returns:
        df: dataframe containing messages_filepath and categories_filepath merged
    
    '''
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    # merge datasets on common id and assign to df
    df = pd.merge(messages, categories, on='id')
    return df


def clean_data(df):
    '''
    Clean the dataframe.
    
    Parameters:
        df: DataFrame
    
    Returns:
        df: Cleaned DataFrame
    
    '''
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True)
    # select first row of the categories dataframe
    row = categories.iloc[0]
    # apply a lambda function that takes everything 
    # up to the second to last character of each string with slicing
    category_colnames = row.apply(lambda x : x[:-2])
    # rename the columns of `categories`
    categories.columns = category_colnames
    
    # iterate through the category columns in df to keep only the
    # last character of the string 
    
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].apply(lambda x : x[-1])
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)
        # replace 2 with 1 in related column
        categories['related'] = categories['related'].replace(to_replace=2, value=1)
        
    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    # drop duplicates
    df.drop_duplicates(inplace=True)
    return df


def save_data(df, database_filepath):
    '''
    Stores df in a SQLite database
    Parameters:
        df: dataframe
        database_filepath: string
    '''
    # create engine
    engine = create_engine(f'sqlite:///{database_filepath}')
    # write records stored in a dataframe to a SQL database
    df.to_sql('disaster_messages', engine, index=False, if_exists='replace')  

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]
        print('VVV', database_filepath)

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()