from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import numpy as np
import tensorflow as tf
from ...configuration_utils import PretrainedConfig
from ...generation import TFLogitsProcessorList
from ...modeling_tf_utils import (TFCausalLanguageModelingLoss, TFModelInputType, TFPreTrainedModel, keras, shape_list, unpack_inputs)
from ...utils import ModelOutput, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_rag import RagConfig
from .retrieval_rag import RagRetriever
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "RagConfig"
@dataclass
class TFRetrievAugLMMarginOutput(ModelOutput):
    """Args:"""
    loss: tf.Tensor | None = None
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    doc_scores: tf.Tensor | None = None
    retrieved_doc_embeds: tf.Tensor | None = None
    retrieved_doc_ids: tf.Tensor | None = None
    context_input_ids: tf.Tensor | None = None
    context_attention_mask: tf.Tensor | None = None
    question_encoder_last_hidden_state: tf.Tensor | None = None
    question_enc_hidden_states: Tuple[tf.Tensor, ...] | None = None
    question_enc_attentions: Tuple[tf.Tensor, ...] | None = None
    generator_enc_last_hidden_state: tf.Tensor | None = None
    generator_enc_hidden_states: Tuple[tf.Tensor, ...] | None = None
    generator_enc_attentions: Tuple[tf.Tensor, ...] | None = None
    generator_dec_hidden_states: Tuple[tf.Tensor, ...] | None = None
    generator_dec_attentions: Tuple[tf.Tensor, ...] | None = None
@dataclass
class TFRetrievAugLMOutput(ModelOutput):
    """Args:"""
    logits: tf.Tensor = None
    past_key_values: List[tf.Tensor] | None = None
    doc_scores: tf.Tensor | None = None
    retrieved_doc_embeds: tf.Tensor | None = None
    retrieved_doc_ids: tf.Tensor | None = None
    context_input_ids: tf.Tensor | None = None
    context_attention_mask: tf.Tensor | None = None
    question_encoder_last_hidden_state: tf.Tensor | None = None
    question_enc_hidden_states: Tuple[tf.Tensor, ...] | None = None
    question_enc_attentions: Tuple[tf.Tensor, ...] | None = None
    generator_enc_last_hidden_state: tf.Tensor | None = None
    generator_enc_hidden_states: Tuple[tf.Tensor, ...] | None = None
    generator_enc_attentions: Tuple[tf.Tensor, ...] | None = None
    generator_dec_hidden_states: Tuple[tf.Tensor, ...] | None = None
    generator_dec_attentions: Tuple[tf.Tensor, ...] | None = None
class TFRagPreTrainedModel(TFPreTrainedModel):
    config_class = RagConfig
    base_model_prefix = "rag"
    _keys_to_ignore_on_load_missing = [r"position_ids"]
    @classmethod
    def from_pretrained_question_encoder_generator(cls, question_encoder_pretrained_model_name_or_path: str = None, generator_pretrained_model_name_or_path: str = None,
    retriever: RagRetriever = None, *model_args, **kwargs) -> TFPreTrainedModel:
        kwargs_question_encoder = {argument[len("question_encoder_") :]: value for argument, value in kwargs.items() if argument.startswith("question_encoder_")}
        kwargs_generator = {argument[len("generator_") :]: value for argument, value in kwargs.items() if argument.startswith("generator_")}
        for key in kwargs_question_encoder.keys(): del kwargs["question_encoder_" + key]
        for key in kwargs_generator.keys(): del kwargs["generator_" + key]
        question_encoder = kwargs_question_encoder.pop("model", None)
        if question_encoder is None:
            assert question_encoder_pretrained_model_name_or_path is not None, ("If `model` is not defined as an argument, a `question_encoder_pretrained_model_name_or_path` has to be defined")
            from ..auto.modeling_tf_auto import TFAutoModel
            if "config" not in kwargs_question_encoder:
                from ..auto.configuration_auto import AutoConfig
                question_encoder_config = AutoConfig.from_pretrained(question_encoder_pretrained_model_name_or_path)
                kwargs_question_encoder["config"] = question_encoder_config
            question_encoder = TFAutoModel.from_pretrained(question_encoder_pretrained_model_name_or_path, name="question_encoder", load_weight_prefix=cls.load_weight_prefix,
            *model_args, **kwargs_question_encoder)
        generator = kwargs_generator.pop("generator", None)
        if generator is None:
            assert generator_pretrained_model_name_or_path is not None, ("If `generator_model` is not defined as an argument, a `generator_pretrained_model_name_or_path` has to be defined")
            from ..auto.modeling_tf_auto import TFAutoModelForSeq2SeqLM
            if "config" not in kwargs_generator:
                from ..auto.configuration_auto import AutoConfig
                generator_config = AutoConfig.from_pretrained(generator_pretrained_model_name_or_path)
                kwargs_generator["config"] = generator_config
            generator = TFAutoModelForSeq2SeqLM.from_pretrained(generator_pretrained_model_name_or_path, name="generator", load_weight_prefix=cls.load_weight_prefix, **kwargs_generator)
        config = kwargs.get("config", None)
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        return cls(question_encoder=question_encoder, generator=generator, config=config, retriever=retriever)
RAG_START_DOCSTRING = r"""
    RAG is a sequence-to-sequence model which encapsulates two core components: a question encoder and a generator.
    During a forward pass, we encode the input with the question encoder and pass it to the retriever to extract
    relevant context documents. The documents are then prepended to the input. Such contextualized inputs is passed to
    the generator.
    The question encoder can be any *autoencoding* model, preferably [`TFDPRQuestionEncoder`], and the generator can be
    any *seq2seq* model, preferably [`TFBartForConditionalGeneration`].
    The model can be initialized with a [`RagRetriever`] for end-to-end generation or used in combination with the
    outputs of a retriever in multiple steps---see examples for more details. The model is compatible any
    *autoencoding* model as the `question_encoder` and any *seq2seq* model with language model head as the `generator`.
    It has been tested with [`TFDPRQuestionEncoder`] as the `question_encoder` and [`TFBartForConditionalGeneration`]
    as the `generator`.
    This model inherits from [`TFPreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a Tensorflow [keras.Model](https://www.tensorflow.org/api_docs/python/tf/keras/Model)
    subclass. Use it as a regular TF 2.0 Keras Model and refer to the TF 2.0 documentation for all matter related to
    general usage and behavior.
    The model is in a developing state as it is now fully supports in eager-mode only, and may not be exported in
    SavedModel format.
    Args:
        config ([`RagConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~TFPreTrainedModel.from_pretrained`] method to load the model weights.
        question_encoder ([`TFPreTrainedModel`]):
            An encoder model compatible with the faiss index encapsulated by the `retriever`.
        generator ([`TFPreTrainedModel`]):
            A seq2seq model used as the generator in the RAG architecture.
        retriever ([`RagRetriever`]):
            A retriever class encapsulating a faiss index queried to obtain context documents for current inputs.
"""
RAG_FORWARD_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`tf.Tensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. [`RagConfig`], used to initialize the model, specifies
            which generator to use, it also specifies a compatible generator tokenizer. Use that tokenizer class to
            obtain the indices.
        attention_mask (`tf.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        encoder_outputs (`tuple(tuple(tf.Tensor)`, *optional*)
            Tuple consists of (`generator_enc_last_hidden_state`, *optional*: `generator_enc_hidden_states`,
            *optional*: `generator_enc_attentions`). `generator_enc_last_hidden_state` of shape `(batch_size, n_docs *
            sequence_length, hidden_size)` is a sequence of hidden-states at the output of the last layer of the
            generator's encoder.
            Used by the ([`TFRagModel`]) model during decoding.
        decoder_input_ids (`tf.Tensor` of shape `(batch_size, target_sequence_length)`, *optional*):
            Provide for generation tasks. `None` by default, construct as per instructions for the generator model
            you're using with your RAG instance.
        decoder_attention_mask (`torch.BoolTensor` of shape `(batch_size,  target_sequence_length)`, *optional*):
            Default behavior: generate a tensor that ignores pad tokens in `decoder_input_ids`. Causal mask will also
            be used by default.
        past_key_values (`tuple(tuple(tf.Tensor))`):
            Tuple consists of two elements: `encoder_outputs` of the RAG model (see `encoder_outputs`) and
            `past_key_values` of the underlying generator. Can be used to speed up decoding. `past_key_values` are used
            in the ([`RagTokenForGeneration`]) model during decoding.
        doc_scores (`tf.Tensor` of shape `(batch_size, config.n_docs)`):
            Score between each retrieved document embeddings (see `retrieved_doc_embeds`) and
            `question_encoder_last_hidden_state`. If the model has is not initialized with a `retriever` `doc_scores`
            has to be provided to the forward pass. `doc_scores` can be computed via
            `question_encoder_last_hidden_state` and `retrieved_doc_embeds`, see examples for more information.
        context_input_ids (`tf.Tensor` of shape `(batch_size * config.n_docs, config.max_combined_length)`, *optional*, returned when *output_retrieved=True*):
            Input IDs post-processed from the retrieved documents and the question encoder `input_ids` by the
            retriever.
            If the model has is not initialized with a `retriever` ``context_input_ids` has to be provided to the
            forward pass. `context_input_ids` are returned by [`~RagRetriever.__call__`]. context_attention_mask
            (`tf.Tensor` of shape `(batch_size * config.n_docs, config.max_combined_length)`, *optional*, returned when
            *output_retrieved=True*): Attention mask post-processed from the retrieved documents and the question
            encoder `input_ids` by the retriever.
            If the model has is not initialized with a `retriever` `context_attention_mask` has to be provided to the
            forward pass. `context_attention_mask` are returned by [`~RagRetriever.__call__`].
        use_cache (`bool`, *optional*, defaults to `True`):
            If set to `True`, `past_key_values` key value states are returned and can be used to speed up decoding (see
            `past_key_values`).
        output_attentions (`bool`, *optional*):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under returned
            tensors for more detail.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        output_retrieved(`bool`, *optional*):
            Whether or not to return the `retrieved_doc_embeds`, `retrieved_doc_ids`, `context_input_ids` and
            `context_attention_mask`. See returned tensors for more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`TFRetrievAugLMOutput`] instead of a plain tuple.
        n_docs (`int`, *optional*, defaults to `config.n_docs``)
            Number of documents to retrieve and/or number of documents for which to generate an answer.
"""
@add_start_docstrings_to_model_forward(RAG_START_DOCSTRING)
class TFRagModel(TFRagPreTrainedModel):
    load_weight_prefix = "tf_rag_model_1"
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[TFPreTrainedModel] = None, generator: Optional[TFPreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, load_weight_prefix: Optional[str] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an question_encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        else: assert isinstance(config, self.config_class), f"config: {config} has to be of type {self.config_class}"
        super().__init__(config, **kwargs)
        if question_encoder is None:
            from ..auto.modeling_tf_auto import TFAutoModel
            question_encoder = TFAutoModel.from_config(config.question_encoder, name="question_encoder")
        if generator is None:
            from ..auto.modeling_tf_auto import TFAutoModelForSeq2SeqLM
            load_weight_prefix = load_weight_prefix if load_weight_prefix is not None else self.load_weight_prefix
            generator = TFAutoModelForSeq2SeqLM.from_config(config.generator, name="generator", load_weight_prefix=load_weight_prefix + "/generator")
        self.retriever = retriever
        if self.retriever is not None:
            assert isinstance(retriever, RagRetriever), f"`self.retriever` is of type {type(self.retriever)}, but should be of type `RagRetriever`"
            self.retriever = retriever
        self.question_encoder = question_encoder
        self.generator = generator
    def set_retriever(self, retriever: RagRetriever): self.retriever = retriever
    @unpack_inputs
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, encoder_outputs: np.ndarray | tf.Tensor | None = None,
    decoder_input_ids: np.ndarray | tf.Tensor | None = None, decoder_attention_mask: np.ndarray | tf.Tensor | None = None, past_key_values: Tuple[Tuple[Union[np.ndarray, tf.Tensor]]] | None = None,
    doc_scores: np.ndarray | tf.Tensor | None = None, context_input_ids: np.ndarray | tf.Tensor | None = None, context_attention_mask: np.ndarray | tf.Tensor | None = None,
    use_cache: bool | None = None, output_attentions: bool | None = None, output_hidden_states: bool | None = None, output_retrieved: bool | None = None,
    n_docs: int | None = None, return_dict: bool | None = None, training: bool = False, **kwargs) -> TFRetrievAugLMOutput:
        assert ("decoder_cached_states" not in kwargs), "Please use past_key_values to cache intermediate outputs"
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        has_to_retrieve = (self.retriever is not None and (context_input_ids is None or context_attention_mask is None or doc_scores is None) and encoder_outputs is None)
        if encoder_outputs is None:
            if has_to_retrieve:
                question_enc_outputs = self.question_encoder(input_ids, attention_mask=attention_mask, return_dict=True, training=training)
                question_encoder_last_hidden_state = question_enc_outputs[0]
                retriever_outputs = self.retriever(input_ids, question_encoder_last_hidden_state.numpy(), prefix=self.generator.config.prefix, n_docs=n_docs, return_tensors="tf")
                context_input_ids, context_attention_mask, retrieved_doc_embeds, retrieved_doc_ids = (retriever_outputs["context_input_ids"], retriever_outputs["context_attention_mask"],
                retriever_outputs["retrieved_doc_embeds"], retriever_outputs["doc_ids"])
                context_input_ids = tf.cast(context_input_ids, tf.int32)
                context_attention_mask = tf.cast(context_attention_mask, tf.int32)
                retrieved_doc_embeds = tf.cast(retrieved_doc_embeds, tf.float32)
                retrieved_doc_ids = tf.cast(retrieved_doc_ids, tf.int32)
                doc_scores = tf.squeeze(tf.matmul(tf.expand_dims(question_encoder_last_hidden_state, axis=1), retrieved_doc_embeds, transpose_b=True), axis=1)
            else:
                assert context_input_ids is not None, ("Make sure that `context_input_ids` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert context_attention_mask is not None, ("Make sure that `context_attention_mask` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert doc_scores is not None, ("Make sure that `doc_scores` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
        assert (doc_scores is not None), "Make sure that `doc_scores` are passed when passing `encoder_outputs` to the forward function."
        assert (doc_scores.shape[1] % n_docs) == 0, (f" The first dimension of `context_input_ids` should be a multiple of `n_docs`={n_docs}, but is {context_input_ids.shape[0]}.")
        if decoder_input_ids is not None: decoder_input_ids = tf.repeat(decoder_input_ids, n_docs, axis=0)
        if decoder_attention_mask is not None: decoder_attention_mask = tf.repeat(decoder_attention_mask, n_docs, axis=0)
        gen_outputs = self.generator(context_input_ids, attention_mask=context_attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids,
        decoder_attention_mask=decoder_attention_mask, past_key_values=past_key_values, use_cache=use_cache, return_dict=True, training=training)
        if not has_to_retrieve:
            question_encoder_last_hidden_state = None
            question_enc_hidden_states = None
            question_enc_attentions = None
            retrieved_doc_embeds = None
            retrieved_doc_ids = None
        else:
            question_enc_hidden_states = question_enc_outputs.hidden_states
            question_enc_attentions = question_enc_outputs.attentions
        if not has_to_retrieve or not output_retrieved:
            context_input_ids = (None,)
            context_attention_mask = None
            retrieved_doc_embeds = None
            retrieved_doc_ids = None
        return TFRetrievAugLMOutput(logits=gen_outputs.logits, doc_scores=doc_scores, past_key_values=gen_outputs.past_key_values, context_input_ids=context_input_ids,
        context_attention_mask=context_attention_mask, retrieved_doc_embeds=retrieved_doc_embeds, retrieved_doc_ids=retrieved_doc_ids, question_encoder_last_hidden_state=question_encoder_last_hidden_state,
        question_enc_hidden_states=question_enc_hidden_states, question_enc_attentions=question_enc_attentions, generator_enc_last_hidden_state=gen_outputs.encoder_last_hidden_state,
        generator_enc_hidden_states=gen_outputs.encoder_hidden_states, generator_enc_attentions=gen_outputs.encoder_attentions, generator_dec_hidden_states=gen_outputs.decoder_hidden_states,
        generator_dec_attentions=gen_outputs.decoder_attentions)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        with tf.name_scope(self.generator.name): self.generator.build(None)
        with tf.name_scope(self.question_encoder.name): self.question_encoder.build(None)
@add_start_docstrings_to_model_forward("A TF RAG-token model implementation. It performs RAG-token specific marginalization in the forward pass.", RAG_START_DOCSTRING)
class TFRagTokenForGeneration(TFRagPreTrainedModel, TFCausalLanguageModelingLoss):
    load_weight_prefix = "tf_rag_token_for_generation_1/rag"
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[TFPreTrainedModel] = None, generator: Optional[TFPreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        super().__init__(config)
        self.rag = TFRagModel(config=config, question_encoder=question_encoder, generator=generator, retriever=retriever, load_weight_prefix=self.load_weight_prefix, name="rag")
    def set_retriever(self, retriever: RagRetriever): self.rag.retriever = retriever
    def prepare_inputs_for_generation(self, decoder_input_ids, past_key_values=None, attention_mask=None, use_cache=None, encoder_outputs=None, doc_scores=None, n_docs=None, **kwargs):
        if past_key_values is not None: decoder_input_ids = decoder_input_ids[:, -1:]
        return {"input_ids": None, "encoder_outputs": encoder_outputs, "doc_scores": doc_scores, "context_attention_mask": attention_mask, "decoder_input_ids": decoder_input_ids,
        "past_key_values": past_key_values, "use_cache": use_cache, "do_marginalize": True, "n_docs": n_docs}
    @property
    def retriever(self): return self.rag.retriever
    @property
    def generator(self): return self.rag.generator
    @property
    def question_encoder(self): return self.rag.question_encoder
    @staticmethod
    def _gather_beams(nested, beam_indices, batch_axis=0):
        def gather_fn(tensor):
            is_rag_cache = tensor.shape[0] != beam_indices.shape[0]
            if is_rag_cache:
                n_docs = tensor.shape[0] // beam_indices.shape[0]
                batch_size = beam_indices.shape[0]
                tensor = tf.reshape(tensor, (batch_size, -1, n_docs, *tensor.shape[2:]))
            gathered_tensor = tf.gather(params=tensor, indices=beam_indices, axis=1, batch_dims=1)
            if is_rag_cache: gathered_tensor = tf.reshape(gathered_tensor, (batch_size * n_docs, -1, *gathered_tensor.shape[3:]))
            return gathered_tensor
        return tf.nest.map_structure(gather_fn, nested)
    def marginalize(self, seq_logits, doc_scores, n_docs=None):
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        seq_logprobs = tf.nn.log_softmax(seq_logits, axis=-1)
        seq_logprobs = tf.reshape(seq_logprobs, [seq_logits.shape[0] // n_docs, n_docs, -1, seq_logits.shape[-1]])
        doc_logprobs = tf.nn.log_softmax(doc_scores, axis=1)
        doc_logprobs = tf.expand_dims(doc_logprobs, axis=-1)
        doc_logprobs = tf.expand_dims(doc_logprobs, axis=-1)
        log_prob_sum = seq_logprobs + doc_logprobs
        return tf.reduce_logsumexp(log_prob_sum, axis=1)
    @unpack_inputs
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, decoder_input_ids: np.ndarray | tf.Tensor | None = None,
    decoder_attention_mask: np.ndarray | tf.Tensor | None = None, encoder_outputs: np.ndarray | tf.Tensor | None = None, past_key_values: Tuple[Tuple[Union[np.ndarray, tf.Tensor]]] | None = None,
    doc_scores: np.ndarray | tf.Tensor | None = None, context_input_ids: np.ndarray | tf.Tensor | None = None, context_attention_mask: np.ndarray | tf.Tensor | None = None,
    use_cache: bool | None = None, output_attentions: bool | None = None, output_hidden_states: bool | None = None, output_retrieved: bool | None = None,
    n_docs: int | None = None, do_marginalize: bool | None = None, labels: np.ndarray | tf.Tensor | None = None, reduce_loss: bool | None = None,
    return_dict: bool | None = None, training: bool = False, **kwargs) -> TFRetrievAugLMMarginOutput:
        assert ("decoder_cached_states" not in kwargs), "Please use past_key_values to cache intermediate outputs"
        do_marginalize = do_marginalize if do_marginalize else self.config.do_marginalize
        reduce_loss = reduce_loss if reduce_loss else self.config.reduce_loss
        if labels is not None:
            if decoder_input_ids is None: decoder_input_ids = labels
            use_cache = False
        outputs = self.rag(input_ids, attention_mask=attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
        context_input_ids=context_input_ids, context_attention_mask=context_attention_mask, doc_scores=doc_scores, past_key_values=past_key_values, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_retrieved=output_retrieved, n_docs=n_docs, training=training)
        loss = None
        logits = outputs.logits
        if labels is not None:
            assert decoder_input_ids is not None
            loss = self.get_nll(outputs.logits, outputs.doc_scores, labels, reduce_loss=reduce_loss, epsilon=self.config.label_smoothing, n_docs=n_docs)
        if do_marginalize: logits = self.marginalize(logits, outputs.doc_scores, n_docs)
        return TFRetrievAugLMMarginOutput(loss=loss, logits=logits, past_key_values=outputs.past_key_values, doc_scores=outputs.doc_scores, context_input_ids=outputs.context_input_ids,
        context_attention_mask=outputs.context_attention_mask, retrieved_doc_embeds=outputs.retrieved_doc_embeds, retrieved_doc_ids=outputs.retrieved_doc_ids,
        question_encoder_last_hidden_state=outputs.question_encoder_last_hidden_state, question_enc_hidden_states=outputs.question_enc_hidden_states,
        question_enc_attentions=outputs.question_enc_attentions, generator_enc_last_hidden_state=outputs.generator_enc_last_hidden_state,
        generator_enc_hidden_states=outputs.generator_enc_hidden_states, generator_enc_attentions=outputs.generator_enc_attentions,
        generator_dec_hidden_states=outputs.generator_dec_hidden_states, generator_dec_attentions=outputs.generator_dec_attentions)
    def generate(self, input_ids: TFModelInputType | None = None, attention_mask: tf.Tensor | None = None, context_input_ids=None, context_attention_mask=None,
    doc_scores=None, n_docs=None, generation_config=None, logits_processor=TFLogitsProcessorList(), **kwargs):
        if generation_config is None: generation_config = self.generation_config
        generation_config = copy.deepcopy(generation_config)
        model_kwargs = generation_config.update(**kwargs)
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        if self.retriever is not None and context_input_ids is None:
            question_hidden_states = self.question_encoder(input_ids, attention_mask=attention_mask)[0]
            out = self.retriever(input_ids, question_hidden_states.numpy().astype(np.float32), prefix=self.generator.config.prefix, n_docs=n_docs, return_tensors="tf")
            context_input_ids, context_attention_mask, retrieved_doc_embeds = (out["context_input_ids"], out["context_attention_mask"], out["retrieved_doc_embeds"])
            context_input_ids = tf.cast(context_input_ids, tf.int32)
            context_attention_mask = tf.cast(context_attention_mask, tf.int32)
            retrieved_doc_embeds = tf.cast(retrieved_doc_embeds, tf.float32)
            doc_scores = tf.matmul(tf.expand_dims(question_hidden_states, axis=1), retrieved_doc_embeds, transpose_b=True)
            doc_scores = tf.squeeze(doc_scores, axis=1)
        assert (context_input_ids.shape[0] % n_docs) == 0, (f" The first dimension of `context_input_ids` should be a multiple of `n_docs`={n_docs}, but is {context_input_ids.shape[0]}.")
        batch_size = context_input_ids.shape[0] // n_docs
        encoder = self.rag.generator.get_encoder()
        encoder_outputs = encoder(input_ids=context_input_ids, attention_mask=context_attention_mask, output_attentions=generation_config.output_attentions,
        output_hidden_states=generation_config.output_hidden_states, return_dict=True)
        decoder_input_ids = tf.fill((batch_size * generation_config.num_beams, 1), tf.cast(generation_config.decoder_start_token_id, tf.int32))
        last_hidden_state = encoder_outputs["last_hidden_state"]
        def extend_enc_output(tensor, num_beams=None):
            d_shape_list = tensor.shape[1:]
            new_shape = (batch_size, 1, n_docs) + d_shape_list
            tensor = tf.reshape(tensor, new_shape)
            new_shape = (batch_size, num_beams, n_docs) + d_shape_list
            tensor = tf.broadcast_to(tensor, new_shape)
            new_shape = (batch_size * num_beams * n_docs,) + d_shape_list
            return tf.reshape(tensor, new_shape)
        context_attention_mask = extend_enc_output(context_attention_mask, num_beams=generation_config.num_beams)
        encoder_outputs["last_hidden_state"] = extend_enc_output(last_hidden_state, num_beams=generation_config.num_beams)
        doc_scores = tf.repeat(doc_scores, generation_config.num_beams, axis=0)
        model_kwargs["doc_scores"] = doc_scores
        model_kwargs["encoder_outputs"] = encoder_outputs
        model_kwargs["attention_mask"] = context_attention_mask
        model_kwargs["n_docs"] = n_docs
        pre_processor = self._get_logits_processor(generation_config=generation_config, input_ids_seq_length=tf.shape(decoder_input_ids)[-1], logits_processor=logits_processor)
        if generation_config.num_beams == 1:
            return self.greedy_search(input_ids=decoder_input_ids, max_length=generation_config.max_length, pad_token_id=generation_config.pad_token_id,
            eos_token_id=generation_config.eos_token_id, logits_processor=pre_processor, output_attentions=generation_config.output_attentions,
            output_hidden_states=generation_config.output_hidden_states, output_scores=generation_config.output_scores,
            return_dict_in_generate=generation_config.return_dict_in_generate, **model_kwargs)
        elif generation_config.num_beams > 1:
            if generation_config.num_beams < generation_config.num_return_sequences: raise ValueError(f"Beam search decoding cannot return more sequences than it has beams. Please set num_beams >= num_return_sequences, got {generation_config.num_beams} and {generation_config.num_return_sequences} (respectivelly)")
            def unflatten_beam_dim(tensor):
                shape = shape_list(tensor)
                return tf.reshape(tensor, [-1, generation_config.num_beams] + shape[1:])
            decoder_input_ids = unflatten_beam_dim(decoder_input_ids)
            model_kwargs["attention_mask"] = unflatten_beam_dim(model_kwargs["attention_mask"])
            model_kwargs["encoder_outputs"]["last_hidden_state"] = unflatten_beam_dim(model_kwargs["encoder_outputs"]["last_hidden_state"])
            return self.beam_search(input_ids=decoder_input_ids, max_length=generation_config.max_length, pad_token_id=generation_config.pad_token_id,
            eos_token_id=generation_config.eos_token_id, logits_processor=pre_processor, output_attentions=generation_config.output_attentions,
            output_hidden_states=generation_config.output_hidden_states, output_scores=generation_config.output_scores,
            return_dict_in_generate=generation_config.return_dict_in_generate, **model_kwargs)
        else: raise ValueError(f"`num_beams` has to be an integer strictly superior to 0 (≥ 1), but is {generation_config.num_beams}")
    def get_input_embeddings(self): return self.rag.generator.get_input_embeddings()
    def get_output_embeddings(self): return self.rag.generator.get_output_embeddings()
    def shift_tokens_right(self, input_ids, start_token_id=None):
        if start_token_id is None:
            start_token_id = self.generator.config.decoder_start_token_id
            assert start_token_id is not None, ("self.generator.config.decoder_start_token_id has to be defined. In Rag we commonly use Bart as generator, see Bart docs for more information")
        pad_token_id = self.generator.config.pad_token_id
        assert pad_token_id is not None, "self.model.config.pad_token_id has to be defined."
        start_tokens = tf.fill((shape_list(input_ids)[0], 1), tf.cast(start_token_id, input_ids.dtype))
        shifted_input_ids = tf.concat([start_tokens, input_ids[:, :-1]], -1)
        shifted_input_ids = tf.where(shifted_input_ids == -100, tf.fill(shape_list(shifted_input_ids), tf.cast(pad_token_id, input_ids.dtype)), shifted_input_ids)
        assert_gte0 = tf.debugging.assert_greater_equal(shifted_input_ids, tf.cast(0, shifted_input_ids.dtype))
        with tf.control_dependencies([assert_gte0]): shifted_input_ids = tf.identity(shifted_input_ids)
        return shifted_input_ids
    def get_nll(self, seq_logits, doc_scores, target, reduce_loss=False, epsilon=0.0, n_docs=None):
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        target = tf.concat([target[:, 1:], tf.fill([target.shape[0], 1], tf.cast(self.config.generator.pad_token_id, target.dtype))], axis=1)
        rag_logprobs = self.marginalize(seq_logits, doc_scores, n_docs)
        loss = self.hf_compute_loss(target, rag_logprobs, from_logits=True, reduce_loss=reduce_loss)
        return loss
    def hf_compute_loss(self, labels, y_pred, smooth_epsilon=0.0, from_logits=True, reduce_loss=False):
        loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction=keras.losses.Reduction.SUM)
        if from_logits is False:
            eps = 1e-9
            y_pred = tf.clip_by_value(y_pred, clip_value_min=eps, clip_value_max=1 - eps)
            y_pred = tf.math.log(y_pred)
        logits = y_pred
        melted_labels = tf.reshape(labels, (-1,))
        active_loss = tf.not_equal(melted_labels, self.config.generator.pad_token_id)
        reduced_logits = tf.boolean_mask(tf.reshape(logits, (-1, logits.shape[2])), active_loss)
        labels = tf.boolean_mask(melted_labels, active_loss)
        nll_loss = loss_fn(labels, reduced_logits)
        smooth_loss = -tf.reduce_sum(reduced_logits, axis=-1)
        smooth_loss = tf.reduce_sum(smooth_loss)
        eps_i = smooth_epsilon / reduced_logits.shape[-1]
        loss = (1.0 - smooth_epsilon) * nll_loss + eps_i * smooth_loss
        return loss
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "rag", None) is not None:
            with tf.name_scope(self.rag.name): self.rag.build(None)
@add_start_docstrings_to_model_forward("A TF RAG-sequence model implementation. It performs RAG-sequence specific marginalization in the forward pass.", RAG_START_DOCSTRING)
class TFRagSequenceForGeneration(TFRagPreTrainedModel, TFCausalLanguageModelingLoss):
    load_weight_prefix = "tf_rag_sequence_for_generation_1/rag"
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[TFPreTrainedModel] = None, generator: Optional[TFPreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        super().__init__(config)
        self.rag = TFRagModel(config=config, question_encoder=question_encoder, generator=generator, retriever=retriever, load_weight_prefix=self.load_weight_prefix, name="rag")
    def set_retriever(self, retriever: RagRetriever): self.rag.retriever = retriever
    @property
    def retriever(self): return self.rag.retriever
    @property
    def generator(self): return self.rag.generator
    @property
    def question_encoder(self): return self.rag.question_encoder
    @unpack_inputs
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def call(self, input_ids: TFModelInputType | None = None, attention_mask: np.ndarray | tf.Tensor | None = None, decoder_input_ids: np.ndarray | tf.Tensor | None = None,
    decoder_attention_mask: np.ndarray | tf.Tensor | None = None, encoder_outputs: np.ndarray | tf.Tensor | None = None, past_key_values: Optional[Tuple[Tuple[Union[np.ndarray, tf.Tensor]]]] = None,
    doc_scores: np.ndarray | tf.Tensor | None = None, context_input_ids: np.ndarray | tf.Tensor | None = None, context_attention_mask: np.ndarray | tf.Tensor | None = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_retrieved: Optional[bool] = None,
    n_docs: Optional[int] = None, exclude_bos_score: Optional[bool] = None, labels: np.ndarray | tf.Tensor | None = None, reduce_loss: Optional[bool] = None,
    return_dict: Optional[bool] = None, training: bool = False,
    **kwargs) -> Union[Tuple[tf.Tensor], TFRetrievAugLMMarginOutput]:
        assert ("decoder_cached_states" not in kwargs), "Please use past_key_values to cache intermediate outputs"
        exclude_bos_score = exclude_bos_score if exclude_bos_score else self.config.exclude_bos_score
        reduce_loss = reduce_loss if reduce_loss else self.config.reduce_loss
        if labels is not None:
            if decoder_input_ids is None: decoder_input_ids = labels
            use_cache = False
        outputs = self.rag(input_ids, attention_mask=attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
        context_input_ids=context_input_ids, context_attention_mask=context_attention_mask, doc_scores=doc_scores, past_key_values=past_key_values, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_retrieved=output_retrieved, n_docs=n_docs, training=training)
        loss = None
        if labels is not None: loss = self.get_nll(outputs.logits, outputs.doc_scores, labels, reduce_loss=reduce_loss, epsilon=self.config.label_smoothing, n_docs=n_docs)
        return TFRetrievAugLMMarginOutput(loss=loss, logits=outputs.logits, doc_scores=outputs.doc_scores, past_key_values=outputs.past_key_values,
        context_input_ids=outputs.context_input_ids, context_attention_mask=outputs.context_attention_mask, retrieved_doc_embeds=outputs.retrieved_doc_embeds,
        retrieved_doc_ids=outputs.retrieved_doc_ids, question_encoder_last_hidden_state=outputs.question_encoder_last_hidden_state,
        question_enc_hidden_states=outputs.question_enc_hidden_states, question_enc_attentions=outputs.question_enc_attentions,
        generator_enc_last_hidden_state=outputs.generator_enc_last_hidden_state, generator_enc_hidden_states=outputs.generator_enc_hidden_states,
        generator_enc_attentions=outputs.generator_enc_attentions, generator_dec_hidden_states=outputs.generator_dec_hidden_states,
        generator_dec_attentions=outputs.generator_dec_attentions)
    def get_nll(self, seq_logits, doc_scores, target, reduce_loss=False, epsilon=0.0, exclude_bos_score=False, n_docs=None):
        target = tf.concat([target[:, 1:], tf.fill([target.shape[0], 1], tf.cast(self.config.generator.pad_token_id, target.dtype))], axis=1)
        bos_token_id = self.config.bos_token_id or self.config.generator.bos_token_id
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        equal_bos_token_id_all = tf.reduce_all(tf.equal(target[:, 0], bos_token_id))
        use_bos = bos_token_id is not None and equal_bos_token_id_all
        def _mask_pads(ll, smooth_obj):
            pad_mask = tf.equal(target, tf.cast(self.config.generator.pad_token_id, target.dtype))
            if tf.reduce_any(pad_mask):
                ll = tf.where(pad_mask, 0.0, ll)
                smooth_obj = tf.where(pad_mask, 0.0, smooth_obj)
            return tf.squeeze(ll, axis=-1), tf.squeeze(smooth_obj, axis=-1)
        seq_logprobs = tf.nn.log_softmax(seq_logits, axis=-1)
        seq_logprobs = tf.reshape(seq_logprobs, (seq_logits.shape[0] // n_docs, n_docs, -1, seq_logits.shape[-1]))
        doc_logprobs = tf.nn.log_softmax(doc_scores, axis=1)
        doc_logprobs = tf.expand_dims(doc_logprobs, axis=-1)
        doc_logprobs = tf.expand_dims(doc_logprobs, axis=-1)
        first_token_scores = seq_logprobs[:, :, :1, :]
        second_token_scores = seq_logprobs[:, :, 1:2, :]
        remainder = seq_logprobs[:, :, 2:, :]
        rag_logprobs = tf.concat([first_token_scores, second_token_scores + doc_logprobs, remainder], axis=2)
        target = tf.expand_dims(target, axis=1)
        target = tf.expand_dims(target, axis=-1)
        target = tf.repeat(target, n_docs, axis=1)
        assert len(target.shape) == len(rag_logprobs.shape)
        def torch_gather(param, id_tensor):
            def gather2d(target, id_tensor):
                idx = tf.stack([tf.range(tf.shape(id_tensor)[0], dtype=id_tensor.dtype), id_tensor[:, 0]], axis=-1)
                result = tf.gather_nd(target, idx)
                return tf.expand_dims(result, axis=-1)
            target = tf.reshape(param, (-1, param.shape[-1]))
            target_shape = id_tensor.shape
            id_tensor = tf.reshape(id_tensor, (-1, 1))
            result = gather2d(target, id_tensor)
            return tf.reshape(result, target_shape)
        ll = torch_gather(rag_logprobs, id_tensor=target)
        smooth_obj = tf.reduce_sum(rag_logprobs, axis=-1, keepdims=True)
        ll, smooth_obj = _mask_pads(ll, smooth_obj)
        if exclude_bos_score and use_bos: ll = tf.reduce_sum(ll[:, :, 1:], axis=2)
        else: ll = tf.reduce_sum(ll, axis=2)
        smooth_obj = tf.reduce_sum(smooth_obj, axis=2)
        ll = tf.math.reduce_logsumexp(ll, axis=1)
        smooth_obj = tf.math.reduce_logsumexp(smooth_obj, axis=1)
        nll_loss = -ll
        smooth_loss = -smooth_obj
        if reduce_loss:
            nll_loss = tf.reduce_sum(nll_loss)
            smooth_loss = tf.reduce_sum(smooth_loss)
        eps_i = epsilon / rag_logprobs.shape[-1]
        loss = (1.0 - epsilon) * nll_loss + eps_i * smooth_loss
        return loss
    def generate(self, input_ids: TFModelInputType | None = None, attention_mask: tf.Tensor | None = None, context_input_ids=None, context_attention_mask=None,
    doc_scores=None, do_deduplication=None, num_return_sequences=None, num_beams=None, n_docs=None, **model_kwargs):
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        do_deduplication = do_deduplication if do_deduplication is not None else self.config.do_deduplication
        num_doc_return_sequences = (num_return_sequences if num_return_sequences is not None else self.config.num_return_sequences)
        num_beams = num_beams if num_beams is not None else self.config.num_beams
        assert (input_ids is not None or context_input_ids is not None), " At least one of input_ids or context_input_ids must be given"
        if self.retriever is not None and context_input_ids is None:
            question_hidden_states = self.question_encoder(input_ids, attention_mask=attention_mask)[0]
            context_input_ids = self.retriever(input_ids, question_hidden_states.numpy(), prefix=self.generator.config.prefix, n_docs=n_docs, return_tensors="tf")["context_input_ids"]
        hypos = []
        model_kwargs["num_beams"] = num_beams
        model_kwargs["num_return_sequences"] = num_beams
        model_kwargs["attention_mask"] = None
        batch_size = input_ids.shape[0] if input_ids is not None else context_input_ids.shape[0] // n_docs
        for index in range(batch_size):
            generator_input_ids = context_input_ids[index * n_docs : (index + 1) * n_docs]
            output_sequences = self.generator.generate(generator_input_ids, **model_kwargs)
            if do_deduplication: output_sequences = tf.stack(list({str(k.numpy().tolist()): k for k in output_sequences}.values()))
            num_candidates = output_sequences.shape[0]
            if input_ids is not None:
                new_input_ids = tf.tile(input_ids[index : index + 1], (num_candidates, 1))
                outputs = self(new_input_ids, labels=output_sequences, exclude_bos_score=True)
            else:
                assert context_attention_mask is not None, ("Make sure that `context_attention_mask` are passed, if no `input_ids` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert doc_scores is not None, ("Make sure that `doc_scores` are passed, if no `input_ids` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                individual_input_ids = tf.tile(generator_input_ids, (num_candidates, 1))
                individual_attention_mask = context_attention_mask[index * n_docs : (index + 1) * n_docs]
                individual_attention_mask = tf.tile(individual_attention_mask, (num_candidates, 1))
                individual_doc_scores = doc_scores[index : (index + 1), :]
                individual_doc_scores = tf.tile(individual_doc_scores, (num_candidates, 1))
                outputs = self(input_ids=None, context_input_ids=individual_input_ids, context_attention_mask=individual_attention_mask, doc_scores=individual_doc_scores,
                labels=output_sequences, exclude_bos_score=True)
            top_cand_inds = tf.math.top_k((-outputs["loss"]), k=num_doc_return_sequences)[1]
            hypos.append(tf.gather(output_sequences, top_cand_inds))
        return self._cat_and_pad(hypos, pad_token_id=self.config.generator.pad_token_id)
    @staticmethod
    def _cat_and_pad(tensors, pad_token_id):
        new_shape = sum([t.shape[0] for t in tensors]), max([t.shape[1] for t in tensors])
        output = tf.fill(new_shape, pad_token_id)
        output = tf.Variable(output)
        ind = 0
        for t in tensors:
            output[ind : ind + t.shape[0], : t.shape[1]].assign(t)
            ind += t.shape[0]
        output = tf.convert_to_tensor(output)
        return tf.cast(output, tensors[0][0][0].dtype)
    def build(self, input_shape=None):
        if self.built: return
        self.built = True
        if getattr(self, "rag", None) is not None:
            with tf.name_scope(self.rag.name): self.rag.build(None)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
