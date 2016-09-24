# -*- coding: utf-8 -*-

import numpy as np
from pydub import AudioSegment
import speech_recognition as sr
import re
import os

from pydub.utils import (
    db_to_float,
    ratio_to_db
)

import pymorphy2
from pydub.silence import split_on_silence
from pydub.playback import play
import time
import pickle


def normalize(seg, headroom=0.1):
    peak_sample_val = seg.max

    if peak_sample_val == 0:
        return seg

    target_peak = seg.max_possible_amplitude * db_to_float(-headroom)
    needed_boost = ratio_to_db(target_peak / peak_sample_val)
    return seg.apply_gain(needed_boost)

def get_norm_form(word, analyzer, FORBIDDEN_TAGS = set(['PRCL', 'PREP', 'UNKN', 'LATN'])):

    parsed = analyzer.parse(word)[0]
    if filter(lambda s: s in parsed.tag, FORBIDDEN_TAGS) == []:
        return parsed.normal_form

def parse_text(input_file):

    with open(input_file) as story_file:
        story = story_file.read().strip().decode('utf-8')

    story = re.sub('[^\w\s]', '', story, flags=re.U)
    story_words = re.split('\s+', story)

    story_words_noprep = []
    analyzer = pymorphy2.MorphAnalyzer()

    for word in story_words:
        norm_form = get_norm_form(word, analyzer)
        if not norm_form is None:
            story_words_noprep.append((word.lower(), norm_form))

    return story_words, story_words_noprep

def split_into_words(audiodata, min_silence_len=60, silence_thresh=-16, test_mode=False):

    audio_chunks = split_on_silence(audiodata,
                                    min_silence_len=min_silence_len,
                                    silence_thresh=silence_thresh)
    if test_mode:
        for audio in audio_chunks:
            play(audio)
            time.sleep(2)

    return audio_chunks

def match_words_and_audio(words, audio_chunks, eps=300, test_mode = False):

    def estimate_time_of_pronunciation(word, MEAN_CONS_DURATION=30,
                                       MEAN_VOWEL_DURATION=100):

        VOWELS = u'аеуоиыэяюё'
        num_vowels = sum(word.count(vowel) for vowel in VOWELS)
        num_consonants = len(word) - num_vowels
        return MEAN_VOWEL_DURATION * num_vowels + MEAN_CONS_DURATION * num_consonants

    current_words_index = 0
    matched_audio = []
    current_chunk = None

    for audio_chunk in audio_chunks:
        print words[current_words_index]
        if current_chunk is None:
            current_chunk = audio_chunk
        else:
            current_chunk += audio_chunk


        if abs(estimate_time_of_pronunciation(words[current_words_index]) - len(current_chunk)) < len(current_chunk)//3:
            matched_audio.append(current_chunk)
            current_chunk = None
            current_words_index += 1
            if current_words_index == len(words):
                print 'the words ended'
                break

    matched_pairs =  zip(words[:len(matched_audio)], matched_audio)

    if test_mode:
        for word, audio in matched_pairs:
            print "current word: {}".format(word.encode('utf-8'))
            play(audio)
            time.sleep(3)

    return matched_pairs

def split_text_into_segments(words_pairs, audio_file, sec_duration, time_interval=3):

    words_segments = []
    story_normal_words_set = [s[1] for s in words_pairs]
    story_normal_words_set = list(map(lambda s: s.encode('utf-8'), story_normal_words_set))
    story_normal_words_set = set(story_normal_words_set)
    #for s in story_normal_words_set:
    #    print s

    #print 'философский' in story_normal_words_set
    analyzer = pymorphy2.MorphAnalyzer()

    for i in range(0, sec_duration - time_interval, time_interval):
        print "segmentation audio from {} to {} sec".format(i, i + time_interval)

        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source, duration=time_interval, offset=i)
            text = r.recognize_sphinx(audio, language='ru-RU').split()

        #audiodata = AudioSegment.from_file(audio_file, format='wav')
        #play(audiodata[i * 1000: i * 1000 + time_interval * 1000])
        current_segment_words = []
        for word in text:
            norm_form = get_norm_form(word.decode('utf-8'), analyzer)
            if norm_form is not None and norm_form.encode('utf-8') in story_normal_words_set:
                current_segment_words.append(norm_form)
                print norm_form

        words_segments.append(current_segment_words)

    return words_segments


def main():

    input_file = os.path.realpath('data/audio/harry-potter-rus.wav')
    input_text = 'data/texts/potter_all_word.txt'
    output_text = os.path.realpath('audio-text/harry-potter.pickle')

    words, norm_words = parse_text(input_text)

    #for word in norm_words:
    #    print word[1].encode('utf-8')

    segm = split_text_into_segments(norm_words, input_file, 60)
    #audiodata = AudioSegment.from_file(input_file, format='wav')
    #len_in_sec = len(audiodata) // 1000

    #matched_pairs = match_words_and_audio(words, audio_chunks, test_mode=True)

if __name__ == '__main__':
    main()