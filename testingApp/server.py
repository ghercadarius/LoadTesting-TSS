import os, subprocess
from datetime import datetime
import sys

from flask import Flask, request, jsonify

app = Flask(__name__)
os.makedirs('test_file_folder', exist_ok=True)
app.config['test_file_folder'] = 'test_file_folder'
app.config['result_file_folder'] = 'result_file_folder'
result_filename = None
test_filename = None

@app.route('/upload_test', methods=['POST'])
def upload_jmx():
    global test_filename
    app.logger.info(f"Current working directory: {os.getcwd()}")
    file = request.files.get('file')
    if not file or file.filename.split('.')[-1] != 'jmx':
        return jsonify({'error': 'Invalid file type. Only .jmx files are allowed.'}), 400
    filepath = os.path.join(app.config['test_file_folder'], file.filename)
    file.save(filepath)
    test_filename = file.filename
    return jsonify({'message': 'File uploaded successfully', 'current_working_dir': os.getcwd()}), 200

@app.route('/run', methods=['POST'])
def run_test():
    global test_filename, result_filename
    app.logger.info(f"Current working directory: {os.getcwd()}")
    if test_filename is None or not os.path.exists(os.path.join(app.config['test_file_folder'], test_filename)):
        return jsonify({'error': 'No test file uploaded'}), 400
    result_filename = 'result-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.csv'
    result_path = os.path.join(app.config['result_file_folder'], result_filename)
    test_path = os.path.join(app.config['test_file_folder'], test_filename)
    
    try:
        subprocess.run([
            '../opt/jmeter/bin/jmeter',
            '-n',
            '-t', test_path,
            '-l', result_path
        ], check=True)
        app.logger.info(f"Test run completed. Result file: {result_path}")
        result_text = ''
        with open(result_path, 'r') as f:
            results = f.readlines()
            for line in results:
                result_text += line + '\n'
        return jsonify({'message': 'Test run successfully', 'result_file': result_filename, 'results': result_text}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Execution failed', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)