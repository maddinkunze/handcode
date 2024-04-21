import os
import sys
import tensorflow.compat.v1 as tf

tf.disable_eager_execution()
tf.enable_resource_variables()

pathScript = os.path.dirname(os.path.realpath(__file__))
pathLib = os.path.join(pathScript, os.path.pardir, "src", "lib")
sys.path.append(pathLib)
import handwriting

nn = handwriting.gcode.HandGCode()._nn

# thanks to https://stackoverflow.com/questions/48646459/tensorflow-savedmodelbuilder for parts of this code

#  For exporting the model in SavedModel format
pathImport = os.path.join(pathLib, "handwriting", "checkpoints", "model-17900")
pathImportMeta = f"{pathImport}.meta"
pathExport = "./pbexport"
builder = tf.compat.v1.saved_model.builder.SavedModelBuilder(pathExport)

#  Create classification signature - describes what model is being exported
tensorInfoPrime = tf.compat.v1.saved_model.utils.build_tensor_info(nn.prime)
tensorInfoXPrime = tf.compat.v1.saved_model.utils.build_tensor_info(nn.x_prime)
tensorInfoXPrimeLen = tf.compat.v1.saved_model.utils.build_tensor_info(nn.x_prime_len)
tensorInfoNumSamples = tf.compat.v1.saved_model.utils.build_tensor_info(nn.num_samples)
tensorInfoSampleTSteps = tf.compat.v1.saved_model.utils.build_tensor_info(nn.sample_tsteps)
tensorInfoChars = tf.compat.v1.saved_model.utils.build_tensor_info(nn.c)
tensorInfoCharsLen = tf.compat.v1.saved_model.utils.build_tensor_info(nn.c_len)
tensorInfoBias = tf.compat.v1.saved_model.utils.build_tensor_info(nn.bias)
tensorInfoStrokes = tf.compat.v1.saved_model.utils.build_tensor_info(nn.sampled_sequence)

classification_signature = (
  tf.compat.v1.saved_model.signature_def_utils.build_signature_def(
    inputs={
        "prime": tensorInfoPrime,
        "x_prime": tensorInfoXPrime,
        "x_prime_len": tensorInfoXPrimeLen,
        "num_samples": tensorInfoNumSamples,
        "sample_tsteps": tensorInfoSampleTSteps,
        "chars": tensorInfoChars,
        "chars_len": tensorInfoCharsLen,
        "bias": tensorInfoBias
    },
    outputs={"strokes": tensorInfoStrokes},
    method_name=tf.saved_model.CLASSIFY_METHOD_NAME)
)

tf.reset_default_graph()
saver = tf.train.import_meta_graph(pathImportMeta)
builder = tf.saved_model.builder.SavedModelBuilder(pathExport)
with tf.Session() as sess:
    # Restore variables from disk.
    saver.restore(sess, pathImport)
    print("Model restored.")
    builder.add_meta_graph_and_variables(
        sess,
        [tf.saved_model.SERVING],
        signature_def_map={'classify': classification_signature},
        strip_default_attrs=False
    )
    builder.save()
    