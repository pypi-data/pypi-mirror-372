"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from packaging.version import parse
import tensorflow as tf
import math
try: import tf_keras as keras
except (ModuleNotFoundError, ImportError):
    import keras
    if parse(keras.__version__).major > 2: raise ValueError("Your currently installed version of Keras is Keras 3, but this is not yet supported in Sapiens Transformers. Please install the backwards-compatible tf-keras package with `pip install tf-keras`.")
def _gelu(x):
    x = tf.convert_to_tensor(x)
    cdf = 0.5 * (1.0 + tf.math.erf(x / tf.cast(tf.sqrt(2.0), x.dtype)))
    return x * cdf
def _gelu_new(x):
    x = tf.convert_to_tensor(x)
    pi = tf.cast(math.pi, x.dtype)
    coeff = tf.cast(0.044715, x.dtype)
    cdf = 0.5 * (1.0 + tf.tanh(tf.sqrt(2.0 / pi) * (x + coeff * tf.pow(x, 3))))
    return x * cdf
def mish(x):
    x = tf.convert_to_tensor(x)
    return x * tf.tanh(tf.math.softplus(x))
def gelu_fast(x):
    x = tf.convert_to_tensor(x)
    coeff1 = tf.cast(0.044715, x.dtype)
    coeff2 = tf.cast(0.7978845608, x.dtype)
    return 0.5 * x * (1.0 + tf.tanh(x * coeff2 * (1.0 + coeff1 * x * x)))
def quick_gelu(x):
    x = tf.convert_to_tensor(x)
    coeff = tf.cast(1.702, x.dtype)
    return x * tf.math.sigmoid(coeff * x)
def gelu_10(x): return tf.clip_by_value(_gelu(x), -10, 10)
def glu(x, axis=-1):
    a, b = tf.split(x, 2, axis=axis)
    return a * tf.math.sigmoid(b)
if parse(tf.version.VERSION) >= parse("2.4"):
    def approximate_gelu_wrap(x): return keras.activations.gelu(x, approximate=True)
    gelu = keras.activations.gelu
    gelu_new = approximate_gelu_wrap
else:
    gelu = _gelu
    gelu_new = _gelu_new
ACT2FN = {"gelu": gelu, "gelu_10": gelu_10, "gelu_fast": gelu_fast, "gelu_new": gelu_new, "glu": glu, "mish": mish, "quick_gelu": quick_gelu, "relu": keras.activations.relu,
"sigmoid": keras.activations.sigmoid, "silu": keras.activations.swish, "swish": keras.activations.swish, "tanh": keras.activations.tanh}
def get_tf_activation(activation_string):
    if activation_string in ACT2FN: return ACT2FN[activation_string]
    else: raise KeyError(f"function {activation_string} not found in ACT2FN mapping {list(ACT2FN.keys())}")
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
