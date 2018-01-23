from benchlingapi.base import ModelRegistry

class ModelInterface(object):

    def __init__(self, model_name, http):
        self.model_name = model_name
        self.http = http
        self.model = ModelRegistry.get_model(model_name)

    def find(self, model_id):
        return self.model.find()