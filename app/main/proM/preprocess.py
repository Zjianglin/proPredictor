import pandas as pd
import numpy as np
import io
from minepy import MINE
from sklearn.pipeline import make_pipeline
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold, GridSearchCV
from sklearn import decomposition
from sklearn import metrics
import pandas as pd
import numpy as np
import statistics
from stop_words import get_stop_words


def get_correlection(dataset, target, features=set([])):
    if target is None:
        raise ValueError('corr() need target value')
    if not isinstance(dataset, pd.DataFrame):
        dataset = pd.DataFrame(dataset)
    if not features:
        features = set(dataset.columns)
    numerical = {}
    text = {}
    num_types = (np.dtype('float64'), np.dtype('int64'), np.dtype('bool'))
    target = dataset[target]
    mine = MINE()
    for col in features:
        if dataset.dtypes[col] in num_types:
            if dataset.dtypes[col] is np.dtype('bool'):
                dataset[col] = dataset[col].astype(int, copy=False)
            mine.compute_score(dataset[col], target)
            numerical[col] = mine.mic()
        else:
            text[col] = np.nan
    return {
        'numerical': dict(sorted(numerical.items(), key=lambda d: d[1],
                                 reverse=True)),
        'object': dict(sorted(text.items(), key=lambda d: d[1],
                              reverse=True))
    }

def dataset_info(filepath):
    dataset = pd.read_csv(filepath)
    describe = dataset.describe().to_dict()
    corr = get_correlection(dataset, dataset.columns[0])
    return {
        'filepath': filepath,
        'describe': describe,
        'correlection': corr
    }

def _topics_extraction_with_lda(X):
    tf_vectorizer = TfidfVectorizer(min_df=2, ngram_range=(1, 2),
            stop_words=get_stop_words('nl'))
    data = tf_vectorizer.fit_transform(X)
    #print('Before LDA, sample size: {}'.format(data.shape))
    best_params_ = {'n_topics': 4, 'max_iter': 100, 'n_jobs': -1,
                    'learning_method': 'batch'}
    lda = decomposition.LatentDirichletAllocation(**best_params_)
    data = lda.fit_transform(data)
    #print('After LDA, sample size: {}'.format(data.shape))
    return data

def preprocess(data, numerical_f=list([]), text_f=list([])):
    if not numerical_f and not text_f:
        numerical_f = []
        text_f = []
        num_types = (np.dtype('float64'), np.dtype('int64'), np.dtype('bool'))
        for col in data.columns:
            if col in num_types:
                numerical_f.append(col)
            else:
                text_f.append(col)
    imp = preprocessing.Imputer(missing_values='NaN',
                                strategy='most_frequent', axis=0, copy=False)
    try:
        df_lda = pd.DataFrame()
        # LDA some text features
        for tf in text_f:
            #print('case attrib: ', tf)
            samples = data[tf]
            if samples.count() * 2 < samples.size: continue
            samples = samples.fillna(samples.mode().iloc[0])
            samples = _topics_extraction_with_lda(samples)
            columns = ['_'.join(
                [tf, str(i)]) for i in range(samples.shape[1])]
            df_lda = pd.concat([df_lda,
                                pd.DataFrame(samples, columns=columns).T])
        print(df_lda.T.info())
        df_num = data[numerical_f]
        for nf in numerical_f:
            f = df_num[nf]
            if f.count() * 2 < f.size:
                df_num.drop([nf], axis=1, inplace=True)
                numerical_f.remove(nf)
        df_num = imp.fit_transform(df_num)
        # Standardize features
        df_num = preprocessing.normalize(df_num, norm='l2', copy=False)
        df_num = pd.DataFrame(df_num, columns=numerical_f)
        print(df_num.info())
        dataset = pd.concat([df_num.T, df_lda]).T
    except Exception as err:
        raise ValueError('selected features error.')
    return dataset


