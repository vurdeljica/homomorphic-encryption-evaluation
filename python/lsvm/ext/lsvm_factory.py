from lsvm.lsvm_pyfhel import LsvmPyfhel
from lsvm.lsvm_plain import LsvmPlain
from lsvm.lsvm_palisade import LsvmPalisade
from lsvm.lsvm_seal import LsvmSeal
from lsvm.lsvm_seal_batch import LsvmSealBatch
from lsvm.ext.lsvm_interface import LsvmInterface
import enum


class LsvmEncType(enum.Enum):
    PYFHEL = 1
    PALISADE = 2
    PLAIN = 3
    PYSEAL = 4
    PYSEAL_BATCH = 5


class LsvmFactory:
    def __init__(self):
        pass

    def get(self, type : LsvmEncType, model_name) -> LsvmInterface:
        if type == LsvmEncType.PLAIN:
            return LsvmPlain(model_name)
        elif type == LsvmEncType.PYFHEL:
            return LsvmPyfhel(model_name)
        elif type == LsvmEncType.PALISADE:
            return LsvmPalisade(model_name)
        elif type == LsvmEncType.PYSEAL:
            return LsvmSeal(model_name)
        elif type == LsvmEncType.PYSEAL_BATCH:
            return LsvmSealBatch(model_name)
