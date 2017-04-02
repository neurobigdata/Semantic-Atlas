import argparse
import base64
import cStringIO
import json
import pickle
import os
import sys

from scipy.spatial.distance import cosine, euclidean
from sklearn.metrics.pairwise import cosine_similarity
import gensim
import numpy as np
import pandas as pd
import io
from PIL import Image

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template, jsonify, request


__dir__ = os.path.dirname(__file__)

app = Flask(__name__)


def _load_stimulus(stimulus_path):
    print >>sys.stderr, 'Loading stimulus data from {}'.format(
        stimulus_path)
    with open(stimulus_path) as f:
        words = f.readlines()
    words = map(lambda x: x.rstrip(), words)
    return words


def _load_word_vectors(word_vectors_path):
    print >>sys.stderr, 'Loading word vectors data from {}'.format(
        word_vectors_path)
    with open(word_vectors_path, 'rb') as f:
        wvectors = pickle.load(f)
    return wvectors


def _get_nearest_neighbours(weights, vectors, words, topn=10, metric='cosin'):
    weights = weights.reshape(1,-1)
    if metric == 'cosin':
        dist = map(lambda x: cosine_similarity(weights, x.reshape(1, -1))[0,0], wvectors)
        data = zip(words, dist)
        data = list(set(data))
        data.sort(key=lambda x:-x[1])
        return data[:topn]


PROCESSED_SUBJECTS = [9, 3, 15, 12]

def _load_weights_and_correlations(models_dir, sub):
    try:
        sub_dir = os.path.join(models_dir, 'sub{}'.format(sub))
        weights = np.load(
            os.path.join(sub_dir, 'weights_reshaped.npy')
        )
        for filename in os.listdir(sub_dir):
            if filename.startswith('sub{}_alph'.format(sub)):
                model_filename = os.path.join(sub_dir, filename)
                print >>sys.stderr, 'Loading model {} from {}'.format(
                    sub, model_filename)
                mask = np.load(model_filename)
                mask = np.nan_to_num(mask)
                return weights, mask
        print >>sys.stderr, "sorry, there is no suitable data"
    except Exception as e:
        print >>sys.stderr, e
        print >>sys.stderr, "sorry, there is no suitable data"


def _get_voxel_result(x, y, z, weights, mask, topn=10):
    global words
    global wvectors

    print >>sys.stderr, 'Retrieving result for voxel ({},{},{})'.format(x, y, z)

    results = {}
    results['correlation_score'] = mask[x,y,z]

    data = _get_nearest_neighbours(weights[x,y,z], wvectors, words, topn=topn)
    results['most_similar'] = []
    for word, similarity in data:
        results['most_similar'].append({
            'word': word,
            'similarity': round(similarity, 3),
        })

    plt.figure()
    plt.imshow(mask[:,:, z], cmap='hot')
    plt.scatter([y], [x])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    #image.show()
    #buf.close()

    b64buffer = cStringIO.StringIO()
    image.save(b64buffer, format='png')
    img_str = base64.b64encode(b64buffer.getvalue())
    results['image_xy'] = img_str

    return results


@app.route('/get_voxel_result', methods=['GET'])
def get_voxel_result():
    global models
    global words
    global wvectors
    try:
        x = int(request.args.get('x'))
        y = int(request.args.get('y'))
        z = int(request.args.get('z'))
        sub = int(request.args.get('sub'))
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)})
    if sub in models:
        weights, mask = models[sub]
    else:
        message = 'Cannot find a models for subject "{}"'.format(sub)
        print >>sys.stderr, message
        return jsonify({'status': 'error', 'message': message})
    try:
        result = _get_voxel_result(x, y, z, weights, mask)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    else:
        result['status'] = 'ok'
        return jsonify(result)


def main(options):
    global models
    global words
    global wvectors
    models = {}
    for sub in PROCESSED_SUBJECTS:
        models[sub] = _load_weights_and_correlations(options.models_dir, sub)
    words = _load_stimulus(options.stimulus_path)
    wvectors = _load_word_vectors(options.word_vectors_path)
    app.run(host='::', port=options.port, debug=True)


def parse_options():
    parser = argparse.ArgumentParser(description='Run the Semantic Atlas server.')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('-s', '--stimulus-path', dest='stimulus_path', required=True,
        help='path to the set of words for the stimulus.')
    parser.add_argument('-w', '--word-vectors-path', dest='word_vectors_path', required=True,
        help='path to file containing the word vectors.')
    parser.add_argument('-m', '--models-dir', dest='models_dir', required=True,
        help='path to directories containing the learned models.')
    return parser.parse_args()


if __name__ == '__main__':
    options = parse_options()
    main(options)

