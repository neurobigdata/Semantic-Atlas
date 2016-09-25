# -*- coding: utf-8 -*-

import os
import re
from zipfile import ZipFile
import multiprocessing as mp
import pickle
import pymorphy2
import numpy as np

def get_norm_form(word, analyzer, FORBIDDEN_TAGS = set(['PRCL', 'PREP', 'CONJ', 'UNKN', 'LATN'])):

    parsed = analyzer.parse(word)[0]
    #if filter(lambda s: s in parsed.tag, FORBIDDEN_TAGS) == []:
    return parsed.normal_form

def parse_text(content=None, path=None, delimiters = ['\n', ' \n', ' ', ',', '\.','\. ' '!', ':', '\?', '-']):

    if content is None:
        assert path is not None

        with open(path) as f_in:
            content = f_in.read()

    alphas = 'абвгдежзиклмнопрстуфцчшщъьэюя'
    analyzer = pymorphy2.MorphAnalyzer()

    reg =  u'|'.join(delimiters)
    words = re.split(reg, content)
    words = map(lambda s: s.lower(), words)
    words = filter(lambda s: len(s) > 0 and s[0].lower() in alphas, words)
    words_norm = map(lambda s: get_norm_form(s.decode('utf-8'), analyzer), words)
    return words, words_norm


def compute_semantic_matrix(args):

    zpath, basis_words, audio_words, window_size = args

    zfolder = ZipFile(zpath)
    books = zfolder.namelist()
    semantic_matrix = np.zeros((len(basis_words), len(audio_words)))

    for book in books:
        with zfolder.open(book) as b_file:
            content = b_file.read()
            corpus_words, norm_corpus_words = parse_text(content=content)

            for corpus_index, corpus_word in enumerate(corpus_words[: -window_size]):
                for basis_index, basis_word in enumerate(basis_words):
                    if basis_word in norm_corpus_words[corpus_index: corpus_index + window_size]:

                        for audio_index, audio_word in enumerate(audio_words):
                            if audio_word in norm_corpus_words[corpus_index: corpus_index + window_size]\
                                    and audio_word != basis_word:
                                semantic_matrix[basis_index][audio_index] += 1

        print "book {} successfully processed, semantic_matrix sum {}".format(book, semantic_matrix.sum())

    folder_name = os.path.basename(zpath)
    with open(os.path.join('data/semantic_matricies/librusec/', folder_name, '.pickle')) as m_file:
        pickle.dump(semantic_matrix)
    return semantic_matrix



if __name__ == '__main__':

    path_basis = 'data/texts/basis.txt'
    path_potter ='data/texts/potter_rosman.txt'
    corpus_folder = '/home/anya/Downloads/librusec/librusec/'
    matrix_path = 'data/semantic_matricies/test_matrix_parallel.pickle'

    basis, basis_norm = parse_text(path=path_basis)
    potter_words, norm_potter = parse_text(path=path_potter)
    norm_potter = filter(lambda s: s is not None, norm_potter)

    #shared_basis = mp.Array('basis', basis)
    #shared_story_words = mp.Array('norm_potter', norm_potter)
    files_paths = map(lambda s: corpus_folder + s, os.listdir(corpus_folder))

    #with open('data/texts/basis_norm.txt', 'w') as bf:
    #for nbw in norm_potter:
    #    print nbw
    #print '=================='

    #for pw in norm_potter:
    #    print pw

    pool = mp.Pool(processes=2)
    matrices = pool.map(compute_semantic_matrix, [(f_path, basis_norm, norm_potter, 15) for f_path in files_paths])
    pool.close()
    pool.join()

