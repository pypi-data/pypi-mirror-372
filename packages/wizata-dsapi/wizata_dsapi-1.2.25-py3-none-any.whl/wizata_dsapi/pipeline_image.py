import json

from .api_dto import ApiDto
from .pipeline import Pipeline
from .script import Script
from .mlmodel import MLModel
from datetime import datetime

import pytz
import io
import tarfile
import gzip
import dill
import pickle


def files_from_gzipped_data(gzipped_data):
    with gzip.GzipFile(fileobj=io.BytesIO(gzipped_data)) as gz:
        with tarfile.open(fileobj=gz, mode='r') as tar:
            files = {}
            for tar_info in tar.getmembers():
                if tar_info.isfile():
                    file_content = tar.extractfile(tar_info).read()
                    files[tar_info.name] = file_content
            return files


class PipelineImage(ApiDto):

    def __init__(self,
                 pipeline_image_id: str = None,
                 pipeline: Pipeline = None):

        # image definition
        self.pipeline_image_id = pipeline_image_id

        # load related packaged entities
        self.pipeline = pipeline
        self.scripts = []
        self.models = {}

    @classmethod
    def route(cls):
        return "pipelineimages"

    def api_id(self) -> str:
        return self.pipeline_image_id

    def endpoint(self) -> str:
        return "PipelineImages"

    def get_script(self, name: str) -> Script:
        """
        get a script stored on the image from its name.
        :param name: name of the script.
        :return: loaded script.
        """
        script = None
        for i_script in self.scripts:
            if i_script.name == name:
                script = i_script
        if script is None:
            raise RuntimeError(f'not able to find {name} in pipeline image')
        return script

    def parse(self):
        if self.pipeline_image_id is None:
            raise ValueError(f'pipeline_image_id cannot be None')

        first_dot = self.pipeline_image_id.index('.')
        second_dot = self.pipeline_image_id.index('.', first_dot + 1)

        datetime_part = self.pipeline_image_id[:first_dot]
        version_part = self.pipeline_image_id[first_dot + 1:second_dot].replace('_', '.')[1:]
        key_part = self.pipeline_image_id[second_dot + 1:]
        return {
            'datetime': int(datetime.strptime(datetime_part, '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC).timestamp() * 1000),
            'version': version_part,
            'key': key_part
        }

    def to_json(self, target: str = None):
        obj = {
            "id": str(self.pipeline_image_id)
        }
        obj.update(self.parse())
        return obj

    @classmethod
    def load(cls,
             pipeline_image_id: str = None,
             g_stream=None) -> 'PipelineImage':
        """
        deserialize from a stream (e.g. file handle).
        :param pipeline_image_id: id of the image.
        :param g_stream: readable stream.
        :return: PipelineImage
        """
        if g_stream is None:
            raise ValueError("No stream provided")
        g_bytes = g_stream.read()
        return cls.loads(pipeline_image_id=pipeline_image_id, g_bytes=g_bytes)

    @classmethod
    def loads(cls,
              pipeline_image_id: str = None,
              g_bytes=None) -> 'PipelineImage':
        """
        deserialize from a bytes array an image.
        :param pipeline_image_id: id of the image.
        :param g_bytes: from loaded content as bytes.
        :return: PipelineImage
        """
        # unpack the content
        image = cls(pipeline_image_id=pipeline_image_id)
        if g_bytes is not None:
            g_files = files_from_gzipped_data(g_bytes)
        else:
            raise ValueError(f'please provide a valid bytes array or dict of files')

        # load the content
        try:

            # load the pipeline
            if 'pipeline.json' not in g_files:
                raise ValueError(f'invalid image')
            image.pipeline = Pipeline.from_dict(json.loads(g_files['pipeline.json']))

            # process the scripts
            script_files = {k: v for k, v in g_files.items() if k.startswith('scripts/')}

            json_files = {k for k in script_files if k.endswith('.json')}
            pkl_files = {k for k in script_files if k.endswith('.pkl')}

            for json_file in json_files:
                base_name = json_file[:-5]
                pkl_file = base_name + '.pkl'

                if pkl_file in script_files:
                    script = Script.from_dict(json.loads(g_files[json_file]))
                    script.function = dill.loads(g_files[pkl_file])
                    image.scripts.append(script)
                else:
                    raise KeyError(f"missing pkl for script json {json_file}")

            for pkl_file in pkl_files:
                base_name = pkl_file[:-4]
                json_file = base_name + '.json'

                if json_file not in json_files:
                    raise KeyError(f"missing json file for script pkl {pkl_file}")

            # process the models
            model_files = {k: v for k, v in g_files.items() if k.startswith('models/')}
            for pkl_file in model_files:
                image.models[pkl_file[7:-4]] = pickle.loads(g_files[pkl_file])

            return image

        except Exception as e:
            raise Exception(f'invalid image - {e}')
