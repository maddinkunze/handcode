import os
import json
import time
import threading
from collections import deque
from common import version_handcode, path_settings, path_data
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

class WebRequestHandler(BaseHTTPRequestHandler):
    info = {"version": version_handcode, "status": "init"}

    tasks = {}
    tasks_queue = deque()
    task_id = 0

    def do_GET(self):
        if self.path == "/tasks":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(list(self.tasks.keys())).encode())
            return

        if self.path.startswith("/task/"):
            delete_task = False
            try:
                task_id = self.path[6:]

                if task_id.endswith("?delete"):
                    delete_task = True
                    task_id = task_id[:-7]

                task_id = int(task_id)
            except:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"invalid_taskid"}')
                return
            
            task = self.tasks.get(task_id, None)
            if not task:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"unknown_taskid"}')
                return
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(task)

            if delete_task:
                try:
                    self.tasks.pop(task_id)
                except: 
                    pass

            return

        if self.path == "/info":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.info).encode())
            return
        
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"unknown_endpoint"}')

    def do_POST(self):
        if self.path == "/task":
            try:
                this_task_id = self.create_task()
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "unknown_task_creation_error", "message": str(e)}).encode())
                return

            self.send_response(202)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"taskid": this_task_id}).encode())
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"error":"unknown_endpoint"}')

    def create_task(self):
        this_task_id = self.task_id
        self.task_id += 1

        self.rfile.read().decode()
        threading.Thread(target=self._handwriting_target, ).start()

        return this_task_id
    
    @classmethod
    def _handwriting_target(cls):
        try:
            cls.info["status"] = "starting"
            import handwriting
            gcode = handwriting.gcode.HandGCode()
        except Exception as e:
            cls.info["status"] = "error"
            cls.info["error"] = str(e.__class__.__name__)
            cls.info["message"] = str(e)
            return

        default_settings = {}
        try:
            file_settings = open(path_settings)
            default_settings = json.load(file_settings)
            file_settings.close()
        except:
            pass

        while True:
            cls.info["status"] = "idle"

            try:
                task_id, settings = cls.tasks_queue.popleft()
            except:
                time.sleep(0.5)
                continue

            try:
                cls.info["status"] = "working"
                cls.tasks[task_id] = b'{"status":"working"}'

                file_out = os.path.join(path_data, f"{task_id}.gcode")
                settings = {**default_settings, **settings, **{"output": {"file": os.path.join(path_data, f"{task_id}.gcode")}}}
                gcode.generate(settings)

                file = open(file_out)
                content = file.read()
                file.close()

                cls.tasks[task_id] = json.dumps({"status": "done", "gcode": content})

            except Exception as e:
                cls.tasks[task_id] = json.dumps({"status": "error", "error": str(e.__class__.__name__), "message": str(e)}).encode()

if __name__ == "__main__":
    threading.Thread(target=WebRequestHandler._handwriting_target, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8000), WebRequestHandler).serve_forever()