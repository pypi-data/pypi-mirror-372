"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import collections
import types
import numpy as np
from ..utils import (add_end_docstrings, is_tf_available, is_torch_available, requires_backends)
from .base import ArgumentHandler, Dataset, Pipeline, PipelineException, build_pipeline_init_args
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import (MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES, MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING_NAMES)
if is_tf_available():
    import tensorflow as tf
    from ..models.auto.modeling_tf_auto import (TF_MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES, TF_MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING_NAMES)
class TableQuestionAnsweringArgumentHandler(ArgumentHandler):
    def __call__(self, table=None, query=None, **kwargs):
        requires_backends(self, "pandas")
        import pandas as pd
        if table is None: raise ValueError("Keyword argument `table` cannot be None.")
        elif query is None:
            if isinstance(table, dict) and table.get("query") is not None and table.get("table") is not None: tqa_pipeline_inputs = [table]
            elif isinstance(table, list) and len(table) > 0:
                if not all(isinstance(d, dict) for d in table): raise ValueError(f"Keyword argument `table` should be a list of dict, but is {(type(d) for d in table)}")
                if table[0].get("query") is not None and table[0].get("table") is not None: tqa_pipeline_inputs = table
                else: raise ValueError(f"If keyword argument `table` is a list of dictionaries, each dictionary should have a `table` and `query` key, but only dictionary has keys {table[0].keys()} `table` and `query` keys.")
            elif Dataset is not None and isinstance(table, Dataset) or isinstance(table, types.GeneratorType): return table
            else: raise ValueError(f"Invalid input. Keyword argument `table` should be either of type `dict` or `list`, but is {type(table)})")
        else: tqa_pipeline_inputs = [{"table": table, "query": query}]
        for tqa_pipeline_input in tqa_pipeline_inputs:
            if not isinstance(tqa_pipeline_input["table"], pd.DataFrame):
                if tqa_pipeline_input["table"] is None: raise ValueError("Table cannot be None.")
                tqa_pipeline_input["table"] = pd.DataFrame(tqa_pipeline_input["table"])
        return tqa_pipeline_inputs
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True))
class TableQuestionAnsweringPipeline(Pipeline):
    default_input_names = "table,query"
    def __init__(self, args_parser=TableQuestionAnsweringArgumentHandler(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args_parser = args_parser
        if self.framework == "tf":
            mapping = TF_MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING_NAMES.copy()
            mapping.update(TF_MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES)
        else:
            mapping = MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING_NAMES.copy()
            mapping.update(MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES)
        self.check_model_type(mapping)
        self.aggregate = bool(getattr(self.model.config, "aggregation_labels", None)) and bool(getattr(self.model.config, "num_aggregation_labels", None))
        self.type = "tapas" if hasattr(self.model.config, "aggregation_labels") else None
    def batch_inference(self, **inputs): return self.model(**inputs)
    def sequential_inference(self, **inputs):
        if self.framework == "pt":
            all_logits = []
            all_aggregations = []
            prev_answers = None
            batch_size = inputs["input_ids"].shape[0]
            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)
            token_type_ids = inputs["token_type_ids"].to(self.device)
            token_type_ids_example = None
            for index in range(batch_size):
                if prev_answers is not None:
                    prev_labels_example = token_type_ids_example[:, 3]
                    model_labels = np.zeros_like(prev_labels_example.cpu().numpy())
                    token_type_ids_example = token_type_ids[index]
                    for i in range(model_labels.shape[0]):
                        segment_id = token_type_ids_example[:, 0].tolist()[i]
                        col_id = token_type_ids_example[:, 1].tolist()[i] - 1
                        row_id = token_type_ids_example[:, 2].tolist()[i] - 1
                        if row_id >= 0 and col_id >= 0 and segment_id == 1: model_labels[i] = int(prev_answers[(col_id, row_id)])
                    token_type_ids_example[:, 3] = torch.from_numpy(model_labels).type(torch.long).to(self.device)
                input_ids_example = input_ids[index]
                attention_mask_example = attention_mask[index]
                token_type_ids_example = token_type_ids[index]
                outputs = self.model(input_ids=input_ids_example.unsqueeze(0), attention_mask=attention_mask_example.unsqueeze(0), token_type_ids=token_type_ids_example.unsqueeze(0))
                logits = outputs.logits
                if self.aggregate: all_aggregations.append(outputs.logits_aggregation)
                all_logits.append(logits)
                dist_per_token = torch.distributions.Bernoulli(logits=logits)
                probabilities = dist_per_token.probs * attention_mask_example.type(torch.float32).to(dist_per_token.probs.device)
                coords_to_probs = collections.defaultdict(list)
                for i, p in enumerate(probabilities.squeeze().tolist()):
                    segment_id = token_type_ids_example[:, 0].tolist()[i]
                    col = token_type_ids_example[:, 1].tolist()[i] - 1
                    row = token_type_ids_example[:, 2].tolist()[i] - 1
                    if col >= 0 and row >= 0 and segment_id == 1: coords_to_probs[(col, row)].append(p)
                prev_answers = {key: np.array(coords_to_probs[key]).mean() > 0.5 for key in coords_to_probs}
            logits_batch = torch.cat(tuple(all_logits), 0)
            return (logits_batch,) if not self.aggregate else (logits_batch, torch.cat(tuple(all_aggregations), 0))
        else:
            all_logits = []
            all_aggregations = []
            prev_answers = None
            batch_size = inputs["input_ids"].shape[0]
            input_ids = inputs["input_ids"]
            attention_mask = inputs["attention_mask"]
            token_type_ids = inputs["token_type_ids"].numpy()
            token_type_ids_example = None
            for index in range(batch_size):
                if prev_answers is not None:
                    prev_labels_example = token_type_ids_example[:, 3]
                    model_labels = np.zeros_like(prev_labels_example, dtype=np.int32)
                    token_type_ids_example = token_type_ids[index]
                    for i in range(model_labels.shape[0]):
                        segment_id = token_type_ids_example[:, 0].tolist()[i]
                        col_id = token_type_ids_example[:, 1].tolist()[i] - 1
                        row_id = token_type_ids_example[:, 2].tolist()[i] - 1
                        if row_id >= 0 and col_id >= 0 and segment_id == 1: model_labels[i] = int(prev_answers[(col_id, row_id)])
                    token_type_ids_example[:, 3] = model_labels
                input_ids_example = input_ids[index]
                attention_mask_example = attention_mask[index]
                token_type_ids_example = token_type_ids[index]
                outputs = self.model(input_ids=np.expand_dims(input_ids_example, axis=0), attention_mask=np.expand_dims(attention_mask_example, axis=0), token_type_ids=np.expand_dims(token_type_ids_example, axis=0))
                logits = outputs.logits
                if self.aggregate: all_aggregations.append(outputs.logits_aggregation)
                all_logits.append(logits)
                probabilities = tf.math.sigmoid(tf.cast(logits, tf.float32)) * tf.cast(attention_mask_example, tf.float32)
                coords_to_probs = collections.defaultdict(list)
                token_type_ids_example = token_type_ids_example
                for i, p in enumerate(tf.squeeze(probabilities).numpy().tolist()):
                    segment_id = token_type_ids_example[:, 0].tolist()[i]
                    col = token_type_ids_example[:, 1].tolist()[i] - 1
                    row = token_type_ids_example[:, 2].tolist()[i] - 1
                    if col >= 0 and row >= 0 and segment_id == 1: coords_to_probs[(col, row)].append(p)
                prev_answers = {key: np.array(coords_to_probs[key]).mean() > 0.5 for key in coords_to_probs}
            logits_batch = tf.concat(tuple(all_logits), 0)
            return (logits_batch,) if not self.aggregate else (logits_batch, tf.concat(tuple(all_aggregations), 0))
    def __call__(self, *args, **kwargs):
        pipeline_inputs = self._args_parser(*args, **kwargs)
        results = super().__call__(pipeline_inputs, **kwargs)
        if len(results) == 1: return results[0]
        return results
    def _sanitize_parameters(self, sequential=None, padding=None, truncation=None, **kwargs):
        preprocess_params = {}
        if padding is not None: preprocess_params["padding"] = padding
        if truncation is not None: preprocess_params["truncation"] = truncation
        forward_params = {}
        if sequential is not None: forward_params["sequential"] = sequential
        return preprocess_params, forward_params, {}
    def preprocess(self, pipeline_input, sequential=None, padding=True, truncation=None):
        if truncation is None:
            if self.type == "tapas": truncation = "drop_rows_to_fit"
            else: truncation = "do_not_truncate"
        table, query = pipeline_input["table"], pipeline_input["query"]
        if table.empty: raise ValueError("table is empty")
        if query is None or query == "": raise ValueError("query is empty")
        inputs = self.tokenizer(table, query, return_tensors=self.framework, truncation=truncation, padding=padding)
        inputs["table"] = table
        return inputs
    def _forward(self, model_inputs, sequential=False, **generate_kwargs):
        table = model_inputs.pop("table")
        if self.type == "tapas":
            if sequential: outputs = self.sequential_inference(**model_inputs)
            else: outputs = self.batch_inference(**model_inputs)
        else:
            if "generation_config" not in generate_kwargs: generate_kwargs["generation_config"] = self.generation_config
            outputs = self.model.generate(**model_inputs, **generate_kwargs)
        model_outputs = {"model_inputs": model_inputs, "table": table, "outputs": outputs}
        return model_outputs
    def postprocess(self, model_outputs):
        inputs = model_outputs["model_inputs"]
        table = model_outputs["table"]
        outputs = model_outputs["outputs"]
        if self.type == "tapas":
            if self.aggregate:
                logits, logits_agg = outputs[:2]
                predictions = self.tokenizer.convert_logits_to_predictions(inputs, logits, logits_agg)
                answer_coordinates_batch, agg_predictions = predictions
                aggregators = {i: self.model.config.aggregation_labels[pred] for i, pred in enumerate(agg_predictions)}
                no_agg_label_index = self.model.config.no_aggregation_label_index
                aggregators_prefix = {i: aggregators[i] + " > " for i, pred in enumerate(agg_predictions) if pred != no_agg_label_index}
            else:
                logits = outputs[0]
                predictions = self.tokenizer.convert_logits_to_predictions(inputs, logits)
                answer_coordinates_batch = predictions[0]
                aggregators = {}
                aggregators_prefix = {}
            answers = []
            for index, coordinates in enumerate(answer_coordinates_batch):
                cells = [table.iat[coordinate] for coordinate in coordinates]
                aggregator = aggregators.get(index, "")
                aggregator_prefix = aggregators_prefix.get(index, "")
                answer = {"answer": aggregator_prefix + ", ".join(cells), "coordinates": coordinates, "cells": [table.iat[coordinate] for coordinate in coordinates]}
                if aggregator: answer["aggregator"] = aggregator
                answers.append(answer)
            if len(answer) == 0: raise PipelineException("Empty answer")
        else: answers = [{"answer": answer} for answer in self.tokenizer.batch_decode(outputs, skip_special_tokens=True)]
        return answers if len(answers) > 1 else answers[0]
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
