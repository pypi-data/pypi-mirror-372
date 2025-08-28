import threading
from pathlib import Path, PurePosixPath
from hivebox.networking.utils import get_ip
from flask import Flask, Blueprint, redirect
from werkzeug.serving import make_server
from hivebox.networking.index_module import Module as IndexModule
from urllib.parse import unquote, urlparse



class WebServer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = threading.Event()
        self.modules = {}
        self.blueprints = {}
        self.index_module = IndexModule(modules=self.modules)
        self.register_module(self.index_module)
        self.app = Flask(__name__)

        @self.app.route("/")
        def home():
            return redirect(self.index_module.Meta.base_url)

        self.server = make_server('0.0.0.0', 5001, self.app, threaded=True)
        self.ctx = self.app.app_context()
        self.ctx.push()

    # NOTE: Use start() to start the thread, this method is a new thread starting point
    def run(self):
        for module_id, blueprint in self.blueprints.items():
            module = self.modules[module_id]
            print(f"Enabling \"{module.Meta.module_name}\" module...")
            self.app.register_blueprint(blueprint, url_prefix=module.Meta.base_url)
        print('WebServer starting...')
        self.running.set()
        print("WebServer started at http://{}:{}".format(get_ip(self.server.host), self.server.port))

        self.server.serve_forever()

    def stop(self):
        print('WebServer stopping...')
        self.running.clear()
        self.server.shutdown()

    def register_module(self, module):
        if not hasattr(module, 'Meta'):
            raise RuntimeError('Module "{}" has no Meta class!'.format(module))

        if not hasattr(module.Meta, 'module_id'):
            raise RuntimeError('Module "{}" Meta class has no module_id!'.format(module))

        if module.Meta.module_id in self.modules:
            raise RuntimeError(f'Module with ID "{module.Meta.module_id}" already registered')

        if not hasattr(module.Meta, 'base_url'):
            raise RuntimeError('Module "{}" Meta class has no module_id!'.format(module))

        if module.Meta.base_url in ('', None, '/'):
            raise RuntimeError('Module "{}" Meta class has incorrect base_url!'.format(module))

        if len(PurePosixPath(unquote(urlparse(module.Meta.base_url).path)).parts) < 2 and module.Meta.module_id != IndexModule.Meta.module_id:
            raise RuntimeError(f'Module with ID "{module.Meta.module_id}" has invalid base_url value')

        self.blueprints[module.Meta.module_id] = Blueprint(
            name=module.Meta.module_id,
            import_name=__name__,
            static_folder=str(Path(module.Meta.static_path).absolute()) if getattr(module.Meta, 'static_path', None) else None,
            template_folder=str(Path(module.Meta.template_path).absolute()) if getattr(module.Meta, 'template_path', None) else None,
        )
        module.enable(self.blueprints[module.Meta.module_id])
        self.modules[module.Meta.module_id] = module


if __name__ == "__main__":
    server = WebServer()
    server.start()
    try:
        while True:
            pass
    finally:
        server.stop()
