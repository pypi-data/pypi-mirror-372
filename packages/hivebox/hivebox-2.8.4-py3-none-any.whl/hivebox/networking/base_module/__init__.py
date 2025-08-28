import uuid

import numpy as np
import cv2
from flask import request


class BaseModule:
    @staticmethod
    def empty_frame(w, h):
        return np.zeros((h, w, 3), np.uint8)

    video_stream_mimetype = 'multipart/x-mixed-replace; boundary=frame'

    @staticmethod
    def video_stream(get_frame):
        """Video streaming generator function."""
        while True:
            frame = get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + bytes(cv2.imencode('.jpg', frame)[1]) + b'\r\n')


class FormItem:
    def __init__(self, item_id, item_type, data, callback):
        self.id = item_id
        self.type = item_type
        self.data = data
        self.callback = callback

    def __iter__(self):
        yield 'id', self.id
        yield 'type', self.type
        yield 'data', self.data


class BaseFormModule(BaseModule):
    form = {}

    def get_form_data(self):
        if not hasattr(self, 'Meta') or not hasattr(self.Meta, 'base_url'):
            raise RuntimeError("Provide a proper Meta subclass!")

        return {
            "base_url": self.Meta.base_url,
            "form": list(map(dict, self.form.values()))
        }

    def add_slider(self, callback, start=0, end=100, label=None, idx=None):
        if idx is None:
            idx = uuid.uuid4().hex
        if label is None:
            label = f"Slider {idx}"
        item_data = {'start': start, 'end': end, 'label': label}
        self.form[idx] = FormItem(item_id=idx, item_type='slider', data=item_data, callback=callback)


    def add_input(self, callback, placeholder='', label=None, idx=None):
        if idx is None:
            idx = uuid.uuid4().hex
        if label is None:
            label = f"Input {idx}"
        item_data = {'placeholder': placeholder, 'label': label}
        self.form[idx] = FormItem(item_id=idx, item_type='input', data=item_data, callback=callback)

    def add_button(self, callback, label=None, idx=None ):
        if idx is None:
            idx = uuid.uuid4().hex
        if label is None:
            label = f"Button {idx}"
        item_data = {'label': label}
        self.form[idx] = FormItem(item_id=idx, item_type='button', data=item_data, callback=callback)

    def add_submit_list(self, callback, value_dict: dict, label=None, idx=None):
        if idx is None:
            idx = uuid.uuid4().hex
        if label is None:
            label = f"Submit {idx}"
        item_data = {
            'label': label,
            'options': [{'value': val, 'label': name} for val, name in value_dict.items()]
        }
        self.form[idx] = FormItem(item_id=idx, item_type='submit', data=item_data, callback=callback)

    def enable(self, app):
        @app.route("/submit/<field>", methods=['POST'])
        def submit(field):
            if field in self.form:
                self.form[field].callback(request.get_json())
                return '', 204
            else:
                return f'Available: {list(self.form.keys())}', 404