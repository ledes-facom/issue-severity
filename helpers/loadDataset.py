import os
import pandas as pd

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

class LoadDataset():
  severityMap = {'normal': 0, 'major': 1, 'enhancement': 2, 'critical': 3, 'minor': 4, 'blocker': 5}
  severityQtd = {'normal': 110000, 'major': 83000, 'enhancement': 94853, 'critical': 110000, 'minor': 82485, 'blocker': 13661}
  sentences_train_final = []
  sentences_test_final = []
  y_test_final = []
  vectorizer = None
  X_test = None

  def insertItemsOnList(self, dataframe):
    sentences = dataframe['description'].values
    Y = dataframe['severity'].values

    sentences_train, sentences_test, y_train, y_test = train_test_split(sentences, Y, train_size=0.75, test_size=0.25, shuffle=False)
    
    self.sentences_train_final.extend(sentences_train)
    self.sentences_test_final.extend(sentences_test)
    self.y_test_final.extend(y_test)

  def initData(self):
    mysql_user = os.environ.get('MYSQL_USER')
    mysql_password = os.environ.get('MYSQL_PASSWORD')
    mysql_host = os.environ.get('MYSQL_HOST')
    mysql_database = os.environ.get('MYSQL_DATABASE')
    conn_address = "mariadb+pymysql://%s:%s@%s/%s?charset=utf8mb4" % (mysql_user, mysql_password, mysql_host, mysql_database) 
    engine = create_engine(conn_address)

    for severity in self.severityMap:
      sql_join = """SELECT * FROM full_data WHERE severity = "?" ORDER BY id LIMIT !"""
      sql_join = sql_join.replace('?', severity)
      sql_join = sql_join.replace('!', str(self.severityQtd[severity]))
      df_aux = pd.read_sql_query(sql_join, con=engine)
      df_aux.replace({'severity': self.severityMap}, inplace=True)
      self.insertItemsOnList(df_aux)

    self.vectorizer = TfidfVectorizer()
    self.vectorizer.fit(self.sentences_train_final + self.sentences_test_final)
    self.X_test = self.vectorizer.transform(self.sentences_test_final)

    return self.X_test, self.y_test_final, self.vectorizer, self.severityMap
