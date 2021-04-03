class LsvmInterface:
    def __init__(self, model_name):
        pass

    def calc(self) -> list:
        raise NotImplementedError

    def decrypt(self, encrypted_labels) -> list:
        raise NotImplementedError

    def get_labels(self) -> list:
        raise NotImplementedError

