from python.utility import confusion, util
from python.lsvm.ext.lsvm_factory import *
import sys


def print_statistics(y_pred, y):
    TP, TN, FN, FP = confusion.calculate(y_pred, y)
    num_test = len(y)
    print("Ground truth Confusion Table")
    print("TN = {0:0.1f}".format(float(TN) / float(num_test) * 100.0))
    print("FP = {0:0.1f}".format(float(FP) / float(num_test) * 100.0))
    print("FN = {0:0.1f}".format(float(FN) / float(num_test) * 100.0))
    print("TP = {0:0.1f}".format(float(TP) / float(num_test) * 100.0))


dataset_name = sys.argv[1]
lsvm_type = LsvmEncType(int(sys.argv[2]))

forbidden_configurations = {(LsvmEncType.PYSEAL, "ovarian"): "Memory limit will be exceeded!"}
lsvm_factory = LsvmFactory()

conf = (lsvm_type, dataset_name)
if conf in forbidden_configurations:
    print("Skipping configuration lsvm_type:", lsvm_type,
          "dataset_name:", dataset_name, "\nReason:", forbidden_configurations[conf], '\n')
    #exit(0)

encryption_start_time = util.tic()
lsvm = lsvm_factory.get(lsvm_type, dataset_name)
encryption_end_time = util.tic()
print("Dataset: " + dataset_name + ", lsvm_type: " + type(lsvm).__name__)

lsvm_calculation_start_time = util.tic()
res = lsvm.calc()
lsvm_calculation_end_time = util.tic()

lsvm_decryption_start_time = util.tic()
res = lsvm.decrypt(res)
lsvm_decryption_end_time = util.tic()

confusion.display(res, lsvm.get_labels(), "Result " + type(lsvm).__name__, lsvm_type, dataset_name)
print_statistics(res, lsvm.get_labels())
util.print_toc(encryption_start_time, "Encryption duration:", encryption_end_time)
util.print_toc(lsvm_calculation_start_time, "LSVM calculation duration:", lsvm_calculation_end_time)
util.print_toc(lsvm_decryption_start_time, "Decryption duration:", lsvm_decryption_end_time)

