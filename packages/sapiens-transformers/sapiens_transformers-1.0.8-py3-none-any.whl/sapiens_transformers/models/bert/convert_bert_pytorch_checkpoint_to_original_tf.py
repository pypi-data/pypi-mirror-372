"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import os
import numpy as np
import tensorflow as tf
import torch
from sapiens_transformers import BertModel
def convert_pytorch_checkpoint_to_tf(model: BertModel, ckpt_dir: str, model_name: str):
    tensors_to_transpose = ("dense.weight", "attention.self.query", "attention.self.key", "attention.self.value")
    var_map = (("layer.", "layer_"), ("word_embeddings.weight", "word_embeddings"), ("position_embeddings.weight", "position_embeddings"), ("token_type_embeddings.weight", "token_type_embeddings"),
    (".", "/"), ("LayerNorm/weight", "LayerNorm/gamma"), ("LayerNorm/bias", "LayerNorm/beta"), ("weight", "kernel"))
    if not os.path.isdir(ckpt_dir): os.makedirs(ckpt_dir)
    state_dict = model.state_dict()
    def to_tf_var_name(name: str):
        for patt, repl in iter(var_map): name = name.replace(patt, repl)
        return f"bert/{name}"
    def create_tf_var(tensor: np.ndarray, name: str, session: tf.Session):
        tf_dtype = tf.dtypes.as_dtype(tensor.dtype)
        tf_var = tf.get_variable(dtype=tf_dtype, shape=tensor.shape, name=name, initializer=tf.zeros_initializer())
        session.run(tf.variables_initializer([tf_var]))
        session.run(tf_var)
        return tf_var
    tf.reset_default_graph()
    with tf.Session() as session:
        for var_name in state_dict:
            tf_name = to_tf_var_name(var_name)
            torch_tensor = state_dict[var_name].numpy()
            if any(x in var_name for x in tensors_to_transpose): torch_tensor = torch_tensor.T
            tf_var = create_tf_var(tensor=torch_tensor, name=tf_name, session=session)
            tf_var.assign(tf.cast(torch_tensor, tf_var.dtype))
            tf_weight = session.run(tf_var)
            print(f"Successfully created {tf_name}: {np.allclose(tf_weight, torch_tensor)}")
        saver = tf.train.Saver(tf.trainable_variables())
        saver.save(session, os.path.join(ckpt_dir, model_name.replace("-", "_") + ".ckpt"))
def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True, help="model name e.g. google-bert/bert-base-uncased")
    parser.add_argument("--cache_dir", type=str, default=None, required=False, help="Directory containing pytorch model")
    parser.add_argument("--pytorch_model_path", type=str, required=True, help="/path/to/<pytorch-model-name>.bin")
    parser.add_argument("--tf_cache_dir", type=str, required=True, help="Directory in which to save tensorflow model")
    args = parser.parse_args(raw_args)
    model = BertModel.from_pretrained(pretrained_model_name_or_path=args.model_name, state_dict=torch.load(args.pytorch_model_path), cache_dir=args.cache_dir)
    convert_pytorch_checkpoint_to_tf(model=model, ckpt_dir=args.tf_cache_dir, model_name=args.model_name)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
