## battleship_backend

### Startup

```
1. source battlship_backend_env/bin/activate
2. pip install -r requirements.txt
3. python main.py (tested with python3.10)
```

Sample vscode launch.json (Please select correct virtual enviroment for vscode)
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            // "args": [
            //     "run",
            //     "--host",
            //     "0.0.0.0",
            //     "--port",
            //     "8000",
            //     "--reload"
            // ],
            // "jinja": true,
            // "env": {
            //     "PYTHONPATH": "/home/kartikjha/Documents/code/battleship_backend/battlship_backend_env/bin/python"
            // }
        },
        {
            "name": "Python: Attach to Process",
            "type": "debugpy",
            "request": "attach",
            "processId": "2719645",
            "justMyCode": true
        }
    ]
}
```