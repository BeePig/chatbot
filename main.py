#! /usr/bin/python
# -*- coding: utf-8 -*-

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


def train():
    # data preprocessing
    metadata, trainX, trainY, testX, testY, validX, validY = initial_setup(data_corpus)
    src_len = len(trainX)
    tgt_len = len(trainY)

    assert src_len == tgt_len

    # batch_size = 32
    batch_size = 2
    n_step = src_len // batch_size
    src_vocab_size = len(metadata['idx2w'])  # 211 (0 ~ 210)
    print("src_vocab_size", src_vocab_size)
    emb_dim = 1024

    word2idx = metadata['w2idx']  # dict  word 2 index
    idx2word = metadata['idx2w']  # list index 2 word

    unk_id = word2idx['unk']  # 1
    pad_id = word2idx['_']  # 0

    start_id = src_vocab_size  # 211
    end_id = src_vocab_size + 1  # 213

    word2idx.update({'start_id': start_id})
    word2idx.update({'end_id': end_id})
    idx2word = idx2word + ['start_id', 'end_id']

    src_vocab_size = tgt_vocab_size = src_vocab_size + 2

    num_epochs = 50
    vocabulary_size = src_vocab_size

    decoder_seq_length = 20

    model_ = Seq2seq(
        decoder_seq_length=decoder_seq_length,
        cell_enc=tf.keras.layers.GRUCell,
        cell_dec=tf.keras.layers.GRUCell,
        n_layer=3,
        n_units=256,
        embedding_layer=tl.layers.Embedding(vocabulary_size=vocabulary_size, embedding_size=emb_dim),
    )

    optimizer = tf.optimizers.Adam(learning_rate=0.001)
    model_.train()
    for epoch in range(num_epochs):
        model_.train()
        trainX, trainY = shuffle(trainX, trainY, random_state=0)
        total_loss, n_iter = 0, 0
        for X, Y in tqdm(tl.iterate.minibatches(inputs=trainX, targets=trainY, batch_size=batch_size, shuffle=False),
                         total=n_step, desc='Epoch[{}/{}]'.format(epoch + 1, num_epochs), leave=False):
            X = tl.prepro.pad_sequences(X)
            _target_seqs = tl.prepro.sequences_add_end_id(Y, end_id=end_id)
            _target_seqs = tl.prepro.pad_sequences(_target_seqs, maxlen=decoder_seq_length)
            _decode_seqs = tl.prepro.sequences_add_start_id(Y, start_id=start_id, remove_last=False)
            _decode_seqs = tl.prepro.pad_sequences(_decode_seqs, maxlen=decoder_seq_length)
            _target_mask = tl.prepro.sequences_get_mask(_target_seqs)

            with tf.GradientTape() as tape:
                ## compute outputs
                output = model_(inputs=[X, _decode_seqs])

                output = tf.reshape(output, [-1, vocabulary_size])
                ## compute loss and update model
                loss = cross_entropy_seq_with_mask(logits=output, target_seqs=_target_seqs, input_mask=_target_mask)

                grad = tape.gradient(loss, model_.all_weights)
                optimizer.apply_gradients(zip(grad, model_.all_weights))

            total_loss += loss
            n_iter += 1

        # printing average loss after every epoch
        print('Epoch [{}/{}]: loss {:.4f}'.format(epoch + 1, num_epochs, total_loss / n_iter))
        tl.files.save_npz(model_.all_weights, name='model.npz')


def answer():
    # data preprocessing
    metadata, trainX, trainY, testX, testY, validX, validY = initial_setup(data_corpus)
    src_len = len(trainX)
    tgt_len = len(trainY)

    assert src_len == tgt_len

    # batch_size = 32
    batch_size = 2
    n_step = src_len // batch_size
    src_vocab_size = len(metadata['idx2w'])  # 8002 (0~8001)
    print("src_vocab_size", src_vocab_size)
    emb_dim = 1024

    word2idx = metadata['w2idx']  # dict  word 2 index
    idx2word = metadata['idx2w']  # list index 2 word

    unk_id = word2idx['unk']  # 1
    pad_id = word2idx['_']  # 0

    start_id = src_vocab_size  # 8002
    end_id = src_vocab_size + 1  # 8003

    word2idx.update({'start_id': start_id})
    word2idx.update({'end_id': end_id})
    idx2word = idx2word + ['start_id', 'end_id']

    src_vocab_size = src_vocab_size + 2

    vocabulary_size = src_vocab_size

    def inference(seed, top_n):
        model_.eval()
        seed_id = [word2idx.get(w, unk_id) for w in seed.split(" ")]
        # sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        sentence = []
        for w_id in sentence_id[0]:
            w = idx2word[w_id]
            if w == 'end_id':
                break
            sentence = sentence + [w]
        return sentence

    decoder_seq_length = 20
    model_ = Seq2seq(
        decoder_seq_length=decoder_seq_length,
        cell_enc=tf.keras.layers.GRUCell,
        cell_dec=tf.keras.layers.GRUCell,
        n_layer=3,
        n_units=256,
        embedding_layer=tl.layers.Embedding(vocabulary_size=vocabulary_size, embedding_size=emb_dim),
    )

    load_weights = tl.files.load_npz(name='model.npz')
    tl.files.assign_weights(load_weights, model_)

    print("=======================================================================================================")
    print("start talk to bot, enter u want in terminal. To stop, type 'end'")
    close = 'end'
    f = open("sample.txt", "w")
    question = input()

    while question != close:
        f.write("q: " + question + "\n")
        sentence = inference(question, 1)
        w = "a: " + ' '.join(sentence) + "\n"
        f.write(w)
        print(" >", ' '.join(sentence))
        question = input()
    f.close()

def test():
    metadata, trainX, trainY, testX, testY, validX, validY = initial_setup(data_corpus)
    print("testX:", trainX)
    src_len = len(trainX)
    tgt_len = len(trainY)
    print("number of q:", src_len)
    assert src_len == tgt_len

    # batch_size = 32
    batch_size = 2
    n_step = src_len // batch_size
    src_vocab_size = len(metadata['idx2w'])  # 8002 (0~8001)
    print("src_vocab_size", src_vocab_size)
    emb_dim = 1024

    word2idx = metadata['w2idx']  # dict  word 2 index
    idx2word = metadata['idx2w']  # list index 2 word

    unk_id = word2idx['unk']  # 1
    pad_id = word2idx['_']  # 0

    start_id = src_vocab_size  # 8002
    end_id = src_vocab_size + 1  # 8003

    word2idx.update({'start_id': start_id})
    word2idx.update({'end_id': end_id})
    idx2word = idx2word + ['start_id', 'end_id']

    src_vocab_size = src_vocab_size + 2

    vocabulary_size = src_vocab_size

    def inference(seed, top_n):
        model_.eval()
        seed_id = [word2idx.get(w, unk_id) for w in seed.split(" ")]
        # sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        sentence_id = model_(inputs=[[seed_id]], seq_length=20, start_token=start_id, top_n=top_n)
        target_seqs = tl.prepro.sequences_add_end_id(sentence_id[0], end_id=end_id)
        target_seqs = tl.prepro.pad_sequences(target_seqs, maxlen=decoder_seq_length)
        sentence = []
        for w_id in sentence_id[0]:
            w = idx2word[w_id]
            if w == 'end_id':
                break
            sentence = sentence + [w]
        return sentence

    decoder_seq_length = 20
    model_ = Seq2seq(
        decoder_seq_length=decoder_seq_length,
        cell_enc=tf.keras.layers.GRUCell,
        cell_dec=tf.keras.layers.GRUCell,
        n_layer=3,
        n_units=256,
        embedding_layer=tl.layers.Embedding(vocabulary_size=vocabulary_size, embedding_size=emb_dim),
    )

    load_weights = tl.files.load_npz(name='model.npz')
    tl.files.assign_weights(load_weights, model_)

    print("===========================================test===========================================================")
    testY = tl.prepro.sequences_add_end_id(testY, end_id=end_id)
    testY = tl.prepro.pad_sequences(testY, maxlen=decoder_seq_length)
    target_mask = tl.prepro.sequences_get_mask(testY)
    # _target_mask = tl.prepro.sequences_get_mask(testY)
    for x, y in zip(testX, testY):
        model_.eval()
        decodeX = [idx2word[w] for w in x]
        question = " ".join(decodeX)
        print("q: " + question)
        output = model_(inputs=[[x]], seq_length=20, start_token=start_id, top_n=1)
        ans = inference(question, 1)
        print(">> " + " ".join(ans))
        output = tf.reshape(output, [20, -1])
        print("out shape", tf.shape(output))

        loss = cross_entropy_seq_with_mask(logits=output, target_seqs=y, input_mask=target_mask)
        print(">>>>>>>>>loss: ", round(loss,2))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="""Project NLP \n
        Example:
        - To train model:   ./main -t
        - To run demo:      ./main
        Author1: Phan Thi Thuy Dung
        Email:  dungptt025@gmail.com
        Author2: Nguyen Quoc Khanh
        Email:  nqkpro96@gmail.com
        Hanoi University of Science and Technology, Hanoi, 2020
        """)
    parser.add_argument('--train', '-t', action="store_true", help='train model')
    parser.add_argument('--test', '-te', action="store_true",help='test model')
    args = parser.parse_args()
    #
    data_corpus = "sales"

    if args.train:
        train()
    elif args.test:
        test()
    else:
        answer()
