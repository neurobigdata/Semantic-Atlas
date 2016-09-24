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

def parse_text(path, delimiters = ['\n', ' \n', ' ', ',', '\.','\. ' '!', ':', '\?', '-']):

    alphas = 'абвгдежзиклмнопрстуфцчшщъьэюя'
    analyzer = pymorphy2.MorphAnalyzer()

    with open(path) as f:
        content = f.read()

    reg =  u'|'.join(delimiters)
    words = re.split(reg, content)
    words = map(lambda s: s.lower(), words)
    words = filter(lambda s: len(s) > 0 and s[0].lower() in alphas, words)
    words_norm = map(lambda s: get_norm_form(s.decode('utf-8'), analyzer), words)
    return words, words_norm


def update_semantic_matrix(file_path, basis_words, story_words, semantic_matrix, window_size=15):

    corpus_words, norm_corpus_words = parse_text(file_path)

    for corpus_index, corpus_word in enumerate(corpus_words[: -window_size]):
        for basis_index, basis_word in enumerate(basis_words):
            if basis_word in norm_corpus_words[corpus_index: corpus_index + window_size]:

                for story_index, story_word in enumerate(story_words):
                    if story_word in norm_corpus_words[corpus_index: corpus_index + window_size]\
                            and story_word != basis_word:
                        semantic_matrix[basis_index][story_index] += 1

    return semantic_matrix



if __name__ == '__main__':

    path_basis = 'data/texts/basis.txt'
    path_potter ='data/texts/potter_rosman.txt'
    corpus_folder = 'data/texts/test_corpus/'
    matrix_path = 'data/semantic_matricies/test_matrix.pickle'

    basis, basis_norm = parse_text(path_basis)
    potter_words, norm_potter = parse_text(path_potter)

    norm_potter = filter(lambda s: s is not None, norm_potter)

    #for w, nw in zip(basis, basis_norm):
    #    print w, nw

    files = os.listdir(corpus_folder)
    files_paths = map(lambda s: corpus_folder + s, files)
    semantic_matrix = np.zeros((len(basis), len(norm_potter)))

    for path in files_paths:
        print path, semantic_matrix.sum()
        semantic_matrix = update_semantic_matrix(path, basis_norm, norm_potter, semantic_matrix)


    with open(matrix_path, 'wb') as f_out:
        pickle.dump(semantic_matrix, f_out)

    #for zip_folder in zip_folders:
    #    fpath = os.path.join(path, zip_folder)
    #    with ZipFile(fpath) as zfolder:
    #        books = zfolder.namelist()
    #        for book in books:
    #            book_path = os.path.join(fpath, book)

    #            with zfolder.open(book) as b_file:
    #                for line in b_file.readlines():
    #                    print line
    #print files
