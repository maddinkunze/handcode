import tensorflow as tf

tconv = tf.lite.TFLiteConverter.from_saved_model("pbexport")
tconv.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
#    tf.lite.OpsSet.SELECT_TF_OPS
]
model = tconv.convert()

f = open("model.tflite", "wb")
f.write(model)
f.close()