from datetime import datetime
from pathlib import Path
from hivebox.networking.base_module import BaseModule
from hivebox.storage import SQLite
from hivebox.common.time_utils import human_time_duration
from flask import render_template, Response
import numpy as np

class Module(BaseModule):
    class Meta:
        base_url = '/home'
        module_id = 'index'
        module_name = 'Home Page'
        template_path = Path(__file__).parent / 'templates'
        static_path = Path(__file__).parent / 'static'

    def __init__(self, modules):
        self._modules = modules

    _frame = BaseModule.empty_frame(300, 300)
    _db = SQLite(
        create_sql="""
            CREATE TABLE stats (
                cpu numeric,
                ram numeric,
                disk numeric,
                app_uptime timestamp,
                device_uptime timestamp,
                os_name text,
                os_version text,
                python_version text,
                timestamp timestamp default current_timestamp not null
            );
        """,
        db_name='index.db'
    )

    def enable(self, app):
        @app.route("/")
        def index():
            stats = self._db.get_data('stats', order_by='-timestamp')

            def chart_mapping(field):
                if len(stats) < 6:
                    return []

                def result_mapping(item):
                    return (
                        human_time_duration((datetime.now() - datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S")).total_seconds()),
                        item[field]
                    )
                mapped = list(map(result_mapping, stats))
                factor = len(mapped) // 6
                result = []
                for i in range(6):
                    idx = i * factor
                    idx_next = (i + 1) * factor
                    label = mapped[idx][0]
                    slice = mapped[idx:(idx_next - 1)]
                    if len(slice) == 0:
                        continue
                    value = round(sum(map(lambda x: x[1], slice)) / len(slice), 2)
                    result.append((label, value))
                return result

            data = {
                'app_uptime': human_time_duration(next(map(lambda x: x['app_uptime'], stats), None)),
                'device_uptime': human_time_duration(next(map(lambda x: x['device_uptime'], stats), None)),
                'os_name': next(map(lambda x: x['os_name'], stats), None),
                'os_version': next(map(lambda x: x['os_version'], stats), None),
                'python_version': next(map(lambda x: x['python_version'], stats), None),
                'cpu': chart_mapping('cpu'),
                'ram': chart_mapping('ram'),
                'disk': next(map(lambda x: x['disk'], stats), None),
                'modules': list(filter(
                    lambda module: module.module_id != self.Meta.module_id,
                    map(lambda module: module.Meta, self._modules.values())
                ))
            }

            return render_template('indexmodule.html', **data)

        @app.route('/video_feed')
        def video_feed():
            """Video streaming route. Put this in the src attribute of an img tag."""
            return Response(self.video_stream(lambda: self._frame), mimetype=self.video_stream_mimetype)


    def set_frame(self, frame: np.ndarray):
        self._frame = frame

    def clear(self):
        self._frame = BaseModule.empty_frame(300, 300)

    def set_stats(self, cpu, ram, disk, app_uptime, device_uptime, os_name, os_version, python_version):
        self._db.add_data('stats', [{
            'cpu': cpu,
            'ram': ram,
            'disk': disk,
            'app_uptime': app_uptime,
            'device_uptime': device_uptime,
            'os_name': os_name,
            'os_version': os_version,
            'python_version': python_version,
        }])