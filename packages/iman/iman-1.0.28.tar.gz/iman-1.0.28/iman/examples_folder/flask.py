from flask import logging, Flask, render_template, request, flash,send_from_directory,jsonify

app = Flask(__name__)


@app.route('/get', methods=['get'])
def hello_world():
    return jsonify({'message' : 'Hello, World!'})

@app.route('/test', methods=['post'])
def test():
    x= request.get_json()
    filename=x['filename']
    return jsonify({'message' : filename})
 
    
if __name__ == "__main__":
    # app.run(host='192.168.43.37' ,port='8080', debug=True)
    app.run(debug=True)
