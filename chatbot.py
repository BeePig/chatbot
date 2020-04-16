#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import tensorlayer as tl
import numpy as np
from tensorlayer.cost import cross_entropy_seq, cross_entropy_seq_with_mask
from tqdm import tqdm
from sklearn.utils import shuffle
from data.sales import data
from tensorlayer.models.seq2seq import Seq2seq
from tensorlayer.models.seq2seq_with_attention import Seq2seqLuongAttention
import argparse
from handle_chat import *
# import logging
# logging.getLogger('tensorflow').setLevel(logging.DEBUG)
def initial_setup(data_corpus):
    metadata, idx_q, idx_a = data.load_data(PATH='data/{}/'.format(data_corpus))
    (trainX, trainY), (testX, testY), (validX, validY) = data.split_dataset(idx_q, idx_a)
    trainX = tl.prepro.remove_pad_sequences(trainX.tolist())
    trainY = tl.prepro.remove_pad_sequences(trainY.tolist())
    testX = tl.prepro.remove_pad_sequences(testX.tolist())
    testY = tl.prepro.remove_pad_sequences(testY.tolist())
    validX = tl.prepro.remove_pad_sequences(validX.tolist())
    validY = tl.prepro.remove_pad_sequences(validY.tolist())
    return metadata, trainX, trainY, testX, testY, validX, validY

class AnswerSeq2seq():
    def __init__(self, data_corpus):
        self.metadata, self.trainX, self.trainY, self.testX, self.testY, self.validX, self.validY = initial_setup(data_corpus)
        self.src_len = len(self.trainX)
        self.tgt_len = len(self.trainY)

        assert self.src_len == self.tgt_len

        # batch_size = 32
        self.batch_size = 2
        self.n_step = self.src_len // self.batch_size
        self.src_vocab_size = len(self.metadata['idx2w'])  # 8002 (0~8001)
        # print("src_vocab_size", self.src_vocab_size)
        self.emb_dim = 1024

        self.word2idx = self.metadata['w2idx']  # dict  word 2 index
        self.idx2word = self.metadata['idx2w']  # list index 2 word

        self.unk_id = self.word2idx['unk']  # 1
        self.pad_id = self.word2idx['_']  # 0

        self.start_id = self.src_vocab_size  # 8002
        self.end_id = self.src_vocab_size + 1  # 8003

        self.word2idx.update({'start_id': self.start_id})
        self.word2idx.update({'end_id': self.end_id})
        self.idx2word = self.idx2word + ['start_id', 'end_id']

        self.src_vocab_size = self.src_vocab_size + 2

        self.vocabulary_size = self.src_vocab_size
        self.decoder_seq_length = 20
        self.model_ = Seq2seq(
            decoder_seq_length=self.decoder_seq_length,
            cell_enc=tf.keras.layers.GRUCell,
            cell_dec=tf.keras.layers.GRUCell,
            n_layer=3,
            n_units=256,
            embedding_layer=tl.layers.Embedding(vocabulary_size=self.vocabulary_size, embedding_size=self.emb_dim),
        )

        self.load_weights = tl.files.load_npz(name='model.npz')
        tl.files.assign_weights(self.load_weights, self.model_)
        self.temp_listbook = []
        self.temp_author = ""
        self.temp_category = ""
    def inference(self, seed, top_n):
        self.model_.eval()
        seed_id = [self.word2idx.get(w, self.unk_id) for w in seed.split(" ")]
        # sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        sentence_id = self.model_(inputs=[[seed_id]], seq_length=20, start_token=self.start_id, top_n=top_n)
        sentence = []
        for w_id in sentence_id[0]:
            w = self.idx2word[w_id]
            if w == 'end_id':
                break
            sentence = sentence + [w]
        return sentence
    def process_handle(self, sentence):
        seq_answer = " ".join(self.inference(sentence, 1))
        # print(seq_answer)
        return handle(sentence, seq_answer)
    def chat(self):
        print("#"*32)
        usr_input = input("User: ")
        while usr_input != "end":
            # if usr_input != "":
            list_book, answer = self.process_handle(usr_input)
            # print(list_book)
            if len(list_book) > 0:
                self.temp_listbook = list_book
            else:
                list_book = self.temp_listbook
                if self.temp_listbook != []:
                    answer += "\nCó phải bạn muốn tìm:"

            # else:
            #     list_book = self.process_handle("bao nhiêu tiền cuốn sách God Gave?")
            print("Bee: ", answer)
            outputProcess(list_book)
            print("#"*32)
            usr_input = input("User: ")


answer1 = AnswerSeq2seq("sales")
answer1.chat()