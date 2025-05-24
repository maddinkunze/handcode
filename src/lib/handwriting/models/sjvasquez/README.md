### Attribution

This model runner is a (in parts) heavily modified version of Sean Vasquez's [handwriting-synthesis](https://github.com/sjvasquez/handwriting-synthesis)

### Setup

This library contains multiple versions of the same model. Depending on which version you want to use, you will need to install different dependencies.

There is a `tensorflow` and a `tflite` runner (both will load the `model.tflite`). You can install the dependencies for the `tensorflow` runner with `uv sync --extra tf`.

If you want to use the `tflite` runner, you will have to install `tflite` (at the time of writing in the process of rebranding to `litert`). The version of `tflite` for using this runner must be compiled with flex delegates enabled, which it is not by default. I do not know how to do that and i cannot give any support/information on that.
If you want to try though, please take a look at these resources:
 - https://ai.google.dev/edge/litert/performance/delegates
 - https://ai.google.dev/edge/litert/models/ops_select
Note, that the `tflite` and `tensorflow` runner are functionally the same, so except for special use-cases, using the `tensorflow` runner and dependencies is highly recommended.

Finally, there is the original checkpoint version, which can theoretically be used to train on your own handwriting. Support for the checkpoint version was dropped in favor of the aforementioned `tflite` model, however you can still try to use the checkpoint model for training your own handwriting. I do not know how to do that and I cannot give any support/information on that.
If you want to try though, you will need to install an old version of python, that supports `tensorflow==2.11` (or `1.15.2`, i dont remember, you will have to try). Please see [this issue](https://github.com/maddinkunze/handcode/issues/1) for (some) more information. Note, that much of the surrounding code will probably not work with such an old python version.

### License

The code itself does not contain any license. The wording in the README suggest, that usage like this seems reasonable.

As far as could be determined, the pretrained models/checkpoints of this model runner are trained on the [IAM On-Line Handwriting Database](https://fki.tic.heia-fr.ch/databases/iam-on-line-handwriting-database), which strictly prohibits commercial use.