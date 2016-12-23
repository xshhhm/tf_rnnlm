"""

  December 2016 - pltrdy
  Handling datasets

  Notes: we assume that <eos>'s id is 1.

"""
import numpy as np

import reader
IEOS = reader.IEOS
IBOS = reader.IBOS
IPAD = reader.IPAD

# Cut sentences after MAX_LEN words
MAX_LEN = 80

class SentenceSet:
  """
    A class defining sub-dataset 
    i.e. train, valid & text sets
  """
  def __init__(self, sentences, max_len, batch_size):
    self.sentences = sentences
    self.max_len = max_len
    self.batch_size = batch_size
    
  def batch_iterator(self):
    batch_size = self.batch_size
    # max length (# words) of sentences aka. num_steps
    sentence_len = self.max_len

    # nb batch we want aka. batch_size
    n_batch = self.batch_size

    # nb sentence in data
    n_sentences = len(self.data)

    # nb sentences per batch
    n_sentences_batch = n_sentences // n_batch

    # nb words per batch
    batch_len = n_sentences_batch * sentence_len

    # n_iter aka. 'epoch_size'
    n_iter = n_sentences_batch


    if n_iter == 0:
      raise ValueError("epoch_size == 0, decrease batch_size or num_steps")
    
    # Batching data
    for i in range(n_iter):
      batch_sentences = self.sentences[batch_size*i:batch_size*(i+1)]
      max_len = min(max([len(s) for s in batch_sentences]), MAX_LEN)
      x = np.zeros([batch_size, max_len])+IPAD
      y = np.zeros([batch_size, max_len])+IPAD
    
      for j in range(batch_size):
        s = batch_sentences[j] 
        l = min(80, len(s))
        x[j][:l] = [IBOS]+s[:l-1]
        y[j][:l] = s[:l]

      yield (x, y)
  
  
  @property
  def data(self):
    return self.sentences



class Datasets:
  """
    Managing datasets
    It may actually contains 3 datasets, namely 
    train, valid and test.
  """
  def __init__(self, path, batch_size=1, training=True, word_to_id=None):
    if not training and word_to_id is None:
      raise ValueError("Must set 'word_to_id' when action is not 'train'")

    # Setting parameters
    self.path = path
    self.training = training
    self.word_to_id = word_to_id
    self.batch_size = batch_size
    
    # Loading from files
    raw_dataset, self.word_to_id = self._read_from_path()
    self.raw_dataset = raw_dataset 
    
    # Splitting into sentences
    sentences_dataset, sentence_len = self._raw_to_sentences(raw_dataset)

    # Creating sub-sets
    self.train, self.valid, self.test = [ 
                SentenceSet(_set, sentence_len, self.batch_size)
                  if _set is not None else None
                  for _set in sentences_dataset]
    

    self.sentence_len = sentence_len

  def _read_from_path(self):
    """Read file(s) in directory 'self.path' converting word to integer
    """
    return reader.raw_data(data_path=self.path, training=self.training, word_to_id=self.word_to_id) 
 
  def _raw_to_sentences(self,raw_dataset):
    sentences = []
    max_size = 0
    for _set in raw_dataset:
      _sen_set, _max_size = self._to_sentences(_set)
      sentences.append(_sen_set)
      max_size = max(max_size, _max_size)
      del _set

    return sentences, max_size

  def _to_sentences(self, raw_data):
    """ 
      Inputs:
        * raw_data: list of word indentifier.  [ int ]. 
        * eos: end of string identifier, int
      Output: 
        * List of (sentences, max_size)
    """
    ieos = IEOS
    sentences = []

    sentence = []
    count = 0
    max_size = 0
    for d in raw_data:
      sentence.append(d)
      count += 1
      if d == ieos:
        sentences.append(sentence)
        sentence = []
        max_size = max(max_size, count)
        count = 0

    return sentences, max_size

  @property
  def train_data(self):
    return self.train.data

  @property
  def valid_data(self):
    return self.valid.data 

  @property
  def test_data(self):
    return self.test.data
