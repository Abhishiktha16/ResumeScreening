from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "<h1>Hello World!</h1><p>Test server is working!</p>"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
