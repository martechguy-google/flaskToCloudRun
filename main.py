from flask import Flask
import subprocess

app = Flask(__name__)


@app.route('/')
def flaskApp():
    subprocess.run(['/bin/bash','runner.sh'])
    return 'Script from Main'

@app.route('/run-script')
def run_script():
    subprocess.run(['/bin/bash', 'runner.sh'])
    return 'Script executed'

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)


