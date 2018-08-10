const spawn = require('child_process').spawn;
const path = require('path');

const zerorpc = require('zerorpc');
const Utils = require('./Utils.js');

class PythonConnector {
    static server() {
        if (!PythonConnector.connected) {
            console.log('PythonConnector – making a new connection to the python layer');
            PythonConnector.zeropcProcess = spawn('python3', ['-u', path.join(__dirname, 'PythonServer.py')]);
            PythonConnector.zeropcProcess.stdout.on('data', function(data) {
                console.info('python:', data.toString());
            });
            PythonConnector.zeropcProcess.stderr.on('data', function(data) {
                console.error('python:', data.toString());
            });

            PythonConnector.zeropc = new zerorpc.Client({'timeout': 50000, 'heartbeatInterval': 50000000});
            PythonConnector.zeropc.connect('tcp://127.0.0.1:4242');
            PythonConnector.connected = true;
        }

        return PythonConnector.zeropc;
    }

    static async invoke(method, ...args) {
        var zeropc = PythonConnector.server();
        return await Utils.promisify(zeropc.invoke, zeropc, method, ...args);
    }
}

module.exports = PythonConnector;
