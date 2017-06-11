
How to launch the server:

1. Launch the Flask App:
```
python server.py \
    --port 9990 \
    -s <path/to/stimulus> \
    -w <path/to/w_vectors.pcl> \
    -m <path/to/results>
```

2. Copy index.html, css/ and js/ folders to www/ folder of web server.

3. Open the browser at the location pointing to the index.html
(e.g. http://localhost:8080/atlas)
