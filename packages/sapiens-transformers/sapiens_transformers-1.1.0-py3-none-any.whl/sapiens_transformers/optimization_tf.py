"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
try: from tf_keras.optimizers.legacy import Adam
except (ImportError, ModuleNotFoundError): from tensorflow.keras.optimizers.legacy import Adam
from typing import Callable, List, Optional, Union
from .modeling_tf_utils import keras
import tensorflow as tf
import re
if hasattr(keras.optimizers.schedules, "learning_rate_schedule"): schedules = keras.optimizers.schedules.learning_rate_schedule
else: schedules = keras.optimizers.schedules
class WarmUp(schedules.LearningRateSchedule):
    def __init__(self, initial_learning_rate: float, decay_schedule_fn: Callable, warmup_steps: int, power: float = 1.0, name: str = None):
        super().__init__()
        self.initial_learning_rate = initial_learning_rate
        self.warmup_steps = warmup_steps
        self.power = power
        self.decay_schedule_fn = decay_schedule_fn
        self.name = name
    def __call__(self, step):
        with tf.name_scope(self.name or "WarmUp") as name:
            global_step_float = tf.cast(step, tf.float32)
            warmup_steps_float = tf.cast(self.warmup_steps, tf.float32)
            warmup_percent_done = global_step_float / warmup_steps_float
            warmup_learning_rate = self.initial_learning_rate * tf.math.pow(warmup_percent_done, self.power)
            return tf.cond(global_step_float < warmup_steps_float, lambda: warmup_learning_rate, lambda: self.decay_schedule_fn(step - self.warmup_steps), name=name)
    def get_config(self): return {"initial_learning_rate": self.initial_learning_rate, "decay_schedule_fn": self.decay_schedule_fn, "warmup_steps": self.warmup_steps, "power": self.power, "name": self.name}
def create_optimizer(init_lr: float, num_train_steps: int, num_warmup_steps: int, min_lr_ratio: float = 0.0, adam_beta1: float = 0.9, adam_beta2: float = 0.999, adam_epsilon: float = 1e-8,
adam_clipnorm: Optional[float] = None, adam_global_clipnorm: Optional[float] = None, weight_decay_rate: float = 0.0, power: float = 1.0, include_in_weight_decay: Optional[List[str]] = None):
    lr_schedule = schedules.PolynomialDecay(initial_learning_rate=init_lr, decay_steps=num_train_steps - num_warmup_steps, end_learning_rate=init_lr * min_lr_ratio, power=power)
    if num_warmup_steps: lr_schedule = WarmUp(initial_learning_rate=init_lr, decay_schedule_fn=lr_schedule, warmup_steps=num_warmup_steps)
    if weight_decay_rate > 0.0: optimizer = AdamWeightDecay(learning_rate=lr_schedule, weight_decay_rate=weight_decay_rate, beta_1=adam_beta1, beta_2=adam_beta2, epsilon=adam_epsilon, clipnorm=adam_clipnorm,
    global_clipnorm=adam_global_clipnorm, exclude_from_weight_decay=["LayerNorm", "layer_norm", "bias"], include_in_weight_decay=include_in_weight_decay)
    else: optimizer = keras.optimizers.Adam(learning_rate=lr_schedule, beta_1=adam_beta1, beta_2=adam_beta2, epsilon=adam_epsilon, clipnorm=adam_clipnorm, global_clipnorm=adam_global_clipnorm)
    return optimizer, lr_schedule
class AdamWeightDecay(Adam):
    def __init__(self, learning_rate: Union[float, schedules.LearningRateSchedule] = 0.001, beta_1: float = 0.9, beta_2: float = 0.999, epsilon: float = 1e-7, amsgrad: bool = False, weight_decay_rate: float = 0.0,
    include_in_weight_decay: Optional[List[str]] = None, exclude_from_weight_decay: Optional[List[str]] = None, name: str = "AdamWeightDecay", **kwargs):
        super().__init__(learning_rate, beta_1, beta_2, epsilon, amsgrad, name, **kwargs)
        self.weight_decay_rate = weight_decay_rate
        self._include_in_weight_decay = include_in_weight_decay
        self._exclude_from_weight_decay = exclude_from_weight_decay
    @classmethod
    def from_config(cls, config):
        custom_objects = {"WarmUp": WarmUp}
        return super(AdamWeightDecay, cls).from_config(config, custom_objects=custom_objects)
    def _prepare_local(self, var_device, var_dtype, apply_state):
        super(AdamWeightDecay, self)._prepare_local(var_device, var_dtype, apply_state)
        apply_state[(var_device, var_dtype)]["weight_decay_rate"] = tf.constant(self.weight_decay_rate, name="adam_weight_decay_rate")
    def _decay_weights_op(self, var, learning_rate, apply_state):
        do_decay = self._do_use_weight_decay(var.name)
        if do_decay: return var.assign_sub(learning_rate * var * apply_state[(var.device, var.dtype.base_dtype)]["weight_decay_rate"], use_locking=self._use_locking)
        return tf.no_op()
    def apply_gradients(self, grads_and_vars, name=None, **kwargs):
        grads, tvars = list(zip(*grads_and_vars))
        return super(AdamWeightDecay, self).apply_gradients(zip(grads, tvars), name=name, **kwargs)
    def _get_lr(self, var_device, var_dtype, apply_state):
        if apply_state is None: return self._decayed_lr_t[var_dtype], {}
        apply_state = apply_state or {}
        coefficients = apply_state.get((var_device, var_dtype))
        if coefficients is None:
            coefficients = self._fallback_apply_state(var_device, var_dtype)
            apply_state[(var_device, var_dtype)] = coefficients
        return coefficients["lr_t"], {"apply_state": apply_state}
    def _resource_apply_dense(self, grad, var, apply_state=None):
        lr_t, kwargs = self._get_lr(var.device, var.dtype.base_dtype, apply_state)
        decay = self._decay_weights_op(var, lr_t, apply_state)
        with tf.control_dependencies([decay]): return super(AdamWeightDecay, self)._resource_apply_dense(grad, var, **kwargs)
    def _resource_apply_sparse(self, grad, var, indices, apply_state=None):
        lr_t, kwargs = self._get_lr(var.device, var.dtype.base_dtype, apply_state)
        decay = self._decay_weights_op(var, lr_t, apply_state)
        with tf.control_dependencies([decay]): return super(AdamWeightDecay, self)._resource_apply_sparse(grad, var, indices, **kwargs)
    def get_config(self):
        config = super().get_config()
        config.update({"weight_decay_rate": self.weight_decay_rate})
        return config
    def _do_use_weight_decay(self, param_name):
        if self.weight_decay_rate == 0: return False
        if self._include_in_weight_decay:
            for r in self._include_in_weight_decay:
                if re.search(r, param_name) is not None: return True
        if self._exclude_from_weight_decay:
            for r in self._exclude_from_weight_decay:
                if re.search(r, param_name) is not None: return False
        return True
class GradientAccumulator:
    def __init__(self):
        self._gradients = []
        self._accum_steps = None
    @property
    def step(self):
        if self._accum_steps is None: self._accum_steps = tf.Variable(tf.constant(0, dtype=tf.int64), trainable=False, synchronization=tf.VariableSynchronization.ON_READ, aggregation=tf.VariableAggregation.ONLY_FIRST_REPLICA)
        return self._accum_steps.value()
    @property
    def gradients(self):
        if not self._gradients: raise ValueError("The accumulator should be called first to initialize the gradients")
        return [gradient.value() if gradient is not None else gradient for gradient in self._gradients]
    def __call__(self, gradients):
        if not self._gradients:
            _ = self.step
            self._gradients.extend([tf.Variable(tf.zeros_like(gradient), trainable=False, synchronization=tf.VariableSynchronization.ON_READ, aggregation=tf.VariableAggregation.ONLY_FIRST_REPLICA) if gradient is not None else gradient for gradient in gradients])
        if len(gradients) != len(self._gradients): raise ValueError(f"Expected {len(self._gradients)} gradients, but got {len(gradients)}")
        for accum_gradient, gradient in zip(self._gradients, gradients):
            if accum_gradient is not None and gradient is not None: accum_gradient.assign_add(gradient)
        self._accum_steps.assign_add(1)
    def reset(self):
        if not self._gradients: return
        self._accum_steps.assign(0)
        for gradient in self._gradients:
            if gradient is not None: gradient.assign(tf.zeros_like(gradient))
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
