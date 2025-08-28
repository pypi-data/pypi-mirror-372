"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import copy
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple, Union
import torch
from torch import nn
from ...configuration_utils import PretrainedConfig
from ...generation import BeamSearchScorer, GenerationConfig, LogitsProcessorList, StoppingCriteriaList
from ...modeling_outputs import ModelOutput
from ...modeling_utils import PreTrainedModel
from ...utils import add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_rag import RagConfig
from .retrieval_rag import RagRetriever
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "RagConfig"
@dataclass
class RetrievAugLMMarginOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    doc_scores: torch.FloatTensor = None
    past_key_values: Optional[List[torch.FloatTensor]] = None
    retrieved_doc_embeds: Optional[torch.FloatTensor] = None
    retrieved_doc_ids: Optional[torch.LongTensor] = None
    context_input_ids: Optional[torch.LongTensor] = None
    context_attention_mask: Optional[torch.LongTensor] = None
    question_encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    question_enc_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    question_enc_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_enc_last_hidden_state: Optional[torch.FloatTensor] = None
    generator_enc_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_enc_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_dec_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_dec_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_cross_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
@dataclass
class RetrievAugLMOutput(ModelOutput):
    """Args:"""
    logits: torch.FloatTensor = None
    doc_scores: torch.FloatTensor = None
    past_key_values: Optional[List[torch.FloatTensor]] = None
    retrieved_doc_embeds: Optional[torch.FloatTensor] = None
    retrieved_doc_ids: Optional[torch.LongTensor] = None
    context_input_ids: Optional[torch.LongTensor] = None
    context_attention_mask: Optional[torch.LongTensor] = None
    question_encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    question_enc_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    question_enc_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_enc_last_hidden_state: Optional[torch.FloatTensor] = None
    generator_enc_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_enc_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_dec_hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_dec_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
    generator_cross_attentions: Optional[Tuple[torch.FloatTensor, ...]] = None
class RagPreTrainedModel(PreTrainedModel):
    config_class = RagConfig
    base_model_prefix = "rag"
    @classmethod
    def from_pretrained(cls, *args, **kwargs):
        kwargs["_fast_init"] = False
        return super().from_pretrained(*args, **kwargs)
    @classmethod
    def from_pretrained_question_encoder_generator(cls, question_encoder_pretrained_model_name_or_path: str = None, generator_pretrained_model_name_or_path: str = None,
    retriever: RagRetriever = None, **kwargs) -> PreTrainedModel:
        kwargs_question_encoder = {argument[len("question_encoder_") :]: value for argument, value in kwargs.items() if argument.startswith("question_encoder_")}
        kwargs_generator = {argument[len("generator_") :]: value for argument, value in kwargs.items() if argument.startswith("generator_")}
        for key in kwargs_question_encoder.keys(): del kwargs["question_encoder_" + key]
        for key in kwargs_generator.keys(): del kwargs["generator_" + key]
        question_encoder = kwargs_question_encoder.pop("model", None)
        if question_encoder is None:
            assert question_encoder_pretrained_model_name_or_path is not None, ("If `model` is not defined as an argument, a `question_encoder_pretrained_model_name_or_path` has to be defined")
            from ..auto.modeling_auto import AutoModel
            if "config" not in kwargs_question_encoder:
                from ..auto.configuration_auto import AutoConfig
                question_encoder_config, kwargs_question_encoder = AutoConfig.from_pretrained(question_encoder_pretrained_model_name_or_path, **kwargs_question_encoder, return_unused_kwargs=True)
                kwargs_question_encoder["config"] = question_encoder_config
            question_encoder = AutoModel.from_pretrained(question_encoder_pretrained_model_name_or_path, **kwargs_question_encoder)
        generator = kwargs_generator.pop("model", None)
        if generator is None:
            assert generator_pretrained_model_name_or_path is not None, ("If `generator_model` is not defined as an argument, a `generator_pretrained_model_name_or_path` has to be defined")
            from ..auto.modeling_auto import AutoModelForSeq2SeqLM
            if "config" not in kwargs_generator:
                from ..auto.configuration_auto import AutoConfig
                generator_config, kwargs_generator = AutoConfig.from_pretrained(generator_pretrained_model_name_or_path, **kwargs_generator, return_unused_kwargs=True)
                kwargs_generator["config"] = generator_config
            generator = AutoModelForSeq2SeqLM.from_pretrained(generator_pretrained_model_name_or_path, **kwargs_generator)
        config = kwargs.get("config", None)
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        return cls(question_encoder=question_encoder, generator=generator, config=config, retriever=retriever)
RAG_START_DOCSTRING = r"""
    RAG is a seq2seq model which encapsulates two core components: a question encoder and a generator. During a forward
    pass, we encode the input with the question encoder and pass it to the retriever to extract relevant context
    documents. The documents are then prepended to the input. Such contextualized inputs is passed to the generator.
    The question encoder can be any *autoencoding* model, preferably [`DPRQuestionEncoder`], and the generator can be
    any *seq2seq* model, preferably [`BartForConditionalGeneration`].
    The model can be initialized with a [`RagRetriever`] for end-to-end generation or used in combination with the
    outputs of a retriever in multiple steps---see examples for more details. The model is compatible any
    *autoencoding* model as the `question_encoder` and any *seq2seq* model with language model head as the `generator`.
    It has been tested with [`DPRQuestionEncoder`] as the `question_encoder` and [`BartForConditionalGeneration`] or
    [`T5ForConditionalGeneration`] as the `generator`.
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Args:
        config ([`RagConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
        question_encoder ([`PreTrainedModel`]):
            An encoder model compatible with the faiss index encapsulated by the `retriever`.
        generator ([`PreTrainedModel`]):
            A seq2seq model used as the generator in the RAG architecture.
        retriever ([`RagRetriever`]):
            A retriever class encapsulating a faiss index queried to obtain context documents for current inputs.
"""
RAG_FORWARD_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
            Indices of input sequence tokens in the vocabulary. [`RagConfig`], used to initialize the model, specifies
            which generator to use, it also specifies a compatible generator tokenizer. Use that tokenizer class to
            obtain the indices.
            [What are input IDs?](../glossary#input-ids)
        attention_mask (`torch.Tensor` of shape `(batch_size, sequence_length)`, *optional*):
            Mask to avoid performing attention on padding token indices. Mask values selected in `[0, 1]`:
            - 1 for tokens that are *not masked*,
            - 0 for tokens that are *masked*.
            [What are attention masks?](../glossary#attention-mask)
        encoder_outputs (`tuple(tuple(torch.FloatTensor)`, *optional*)
            Tuple consists of (`generator_enc_last_hidden_state`, *optional*: `generator_enc_hidden_states`,
            *optional*: `generator_enc_attentions`). `generator_enc_last_hidden_state` of shape `(batch_size, n_docs *
            sequence_length, hidden_size)` is a sequence of hidden-states at the output of the last layer of the
            generator's encoder.
            Used by the ([`RagModel`]) model during decoding.
        decoder_input_ids (`torch.LongTensor` of shape `(batch_size, target_sequence_length)`, *optional*):
            Provide for generation tasks. `None` by default, construct as per instructions for the generator model
            you're using with your RAG instance.
        decoder_attention_mask (`torch.BoolTensor` of shape `(batch_size,  target_sequence_length)`, *optional*):
            Default behavior: generate a tensor that ignores pad tokens in `decoder_input_ids`. Causal mask will also
            be used by default.
        past_key_values (`tuple(tuple(torch.FloatTensor))`):
            Tuple consists of two elements: `encoder_outputs` of the RAG model (see `encoder_outputs`) and
            `past_key_values` of the underlying generator. Can be used to speed up decoding. `past_key_values` are used
            in the ([`RagTokenForGeneration`]) model during decoding.
        doc_scores (`torch.FloatTensor` of shape `(batch_size, config.n_docs)`):
            Score between each retrieved document embeddings (see `retrieved_doc_embeds`) and
            `question_encoder_last_hidden_state`. If the model has is not initialized with a `retriever` `doc_scores`
            has to be provided to the forward pass. `doc_scores` can be computed via
            `question_encoder_last_hidden_state` and `retrieved_doc_embeds`, see examples for more information.
        context_input_ids (`torch.LongTensor` of shape `(batch_size * config.n_docs, config.max_combined_length)`, *optional*, returned when *output_retrieved=True*):
            Input IDs post-processed from the retrieved documents and the question encoder `input_ids` by the
            retriever. If the model was not initialized with a `retriever` ``context_input_ids` has to be provided to
            the forward pass. `context_input_ids` are returned by [`~RagRetriever.__call__`].
        context_attention_mask (`torch.LongTensor` of shape `(batch_size * config.n_docs, config.max_combined_length)`,*optional*, returned when *output_retrieved=True*):
            Attention mask post-processed from the retrieved documents and the question encoder `input_ids` by the
            retriever. If the model has is not initialized with a `retriever` `context_attention_mask` has to be
            provided to the forward pass. `context_attention_mask` are returned by [`~RagRetriever.__call__`].
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
        n_docs (`int`, *optional*, defaults to `config.n_docs``)
            Number of documents to retrieve and/or number of documents for which to generate an answer.
"""
@add_start_docstrings_to_model_forward(RAG_START_DOCSTRING)
class RagModel(RagPreTrainedModel):
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[PreTrainedModel] = None, generator: Optional[PreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an question_encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        else: assert isinstance(config, self.config_class), f"config: {config} has to be of type {self.config_class}"
        super().__init__(config)
        if question_encoder is None:
            from ..auto.modeling_auto import AutoModel
            question_encoder = AutoModel.from_config(config.question_encoder, attn_implementation=config._attn_implementation)
        if generator is None:
            from ..auto.modeling_auto import AutoModelForSeq2SeqLM
            generator = AutoModelForSeq2SeqLM.from_config(config.generator, attn_implementation=config._attn_implementation)
        self.retriever = retriever
        if self.retriever is not None:
            assert isinstance(retriever, RagRetriever), f"`self.retriever` is of type {type(self.retriever)}, but should be of type `RagRetriever`"
            self.retriever = retriever
        self.question_encoder = question_encoder
        self.generator = generator
        self.ctx_encoder = None
        self.context_encoder_training = False
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    decoder_input_ids: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.BoolTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None,
    doc_scores: Optional[torch.FloatTensor] = None, context_input_ids: Optional[torch.LongTensor] = None, context_attention_mask: Optional[torch.LongTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_retrieved: Optional[bool] = None,
    n_docs: Optional[int] = None) -> Union[Tuple[torch.Tensor], RetrievAugLMOutput]:
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        use_cache = use_cache if use_cache is not None else self.config.use_cache
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        output_retrieved = output_retrieved if output_retrieved is not None else self.config.output_retrieved
        has_to_retrieve = (self.retriever is not None and (context_input_ids is None or context_attention_mask is None or doc_scores is None) and encoder_outputs is None)
        if encoder_outputs is None:
            if has_to_retrieve:
                question_enc_outputs = self.question_encoder(input_ids, attention_mask=attention_mask, return_dict=True)
                question_encoder_last_hidden_state = question_enc_outputs[0]
                retriever_outputs = self.retriever(input_ids, question_encoder_last_hidden_state.cpu().detach().to(torch.float32).numpy(), prefix=self.generator.config.prefix,
                n_docs=n_docs, return_tensors="pt")
                if self.context_encoder_training:
                    (context_input_ids, context_attention_mask, retrieved_doc_embeds, retrived_doc_input_ids, retrived_doc_attention_mask, retrieved_doc_ids,) = (retriever_outputs["context_input_ids"],
                    retriever_outputs["context_attention_mask"], retriever_outputs["retrieved_doc_embeds"], retriever_outputs["tokenized_doc_ids"], retriever_outputs["tokenized_doc_attention_mask"],
                    retriever_outputs["doc_ids"])
                    context_input_ids = context_input_ids.to(input_ids)
                    context_attention_mask = context_attention_mask.to(input_ids)
                    retrived_doc_input_ids = retrived_doc_input_ids.to(input_ids)
                    retrived_doc_attention_mask = retrived_doc_attention_mask.to(input_ids)
                    retrieved_doc_embeds = self.ctx_encoder(retrived_doc_input_ids, attention_mask=retrived_doc_attention_mask, return_dict=True).pooler_output
                    retrieved_doc_embeds = retrieved_doc_embeds.view(-1, n_docs, question_encoder_last_hidden_state.shape[1])
                    doc_scores = torch.bmm(question_encoder_last_hidden_state.unsqueeze(1), retrieved_doc_embeds.transpose(1, 2)).squeeze(1)
                else:
                    context_input_ids, context_attention_mask, retrieved_doc_embeds, retrieved_doc_ids = (retriever_outputs["context_input_ids"], retriever_outputs["context_attention_mask"],
                    retriever_outputs["retrieved_doc_embeds"], retriever_outputs["doc_ids"])
                    retrieved_doc_embeds = retrieved_doc_embeds.to(question_encoder_last_hidden_state)
                    context_input_ids = context_input_ids.to(input_ids)
                    context_attention_mask = context_attention_mask.to(input_ids)
                    doc_scores = torch.bmm(question_encoder_last_hidden_state.unsqueeze(1), retrieved_doc_embeds.transpose(1, 2)).squeeze(1)
            else:
                assert context_input_ids is not None, ("Make sure that `context_input_ids` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert context_attention_mask is not None, ("Make sure that `context_attention_mask` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert doc_scores is not None, ("Make sure that `doc_scores` are passed, if no `retriever` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
        assert (doc_scores is not None), "Make sure that `doc_scores` are passed when passing `encoder_outputs` to the forward function."
        assert (doc_scores.shape[1] % n_docs) == 0, (f" The first dimension of `context_input_ids` should be a multiple of `n_docs`={n_docs}, but is {context_input_ids.shape[0]}.")
        if decoder_input_ids is not None: decoder_input_ids = decoder_input_ids.repeat_interleave(n_docs, dim=0)
        if decoder_attention_mask is not None: decoder_attention_mask = decoder_attention_mask.repeat_interleave(n_docs, dim=0)
        gen_outputs = self.generator(input_ids=context_input_ids, attention_mask=context_attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids,
        decoder_attention_mask=decoder_attention_mask, past_key_values=past_key_values, use_cache=use_cache, output_attentions=output_attentions, return_dict=True)
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
        return RetrievAugLMOutput(logits=gen_outputs.logits, doc_scores=doc_scores, past_key_values=gen_outputs.past_key_values, context_input_ids=context_input_ids,
        context_attention_mask=context_attention_mask, retrieved_doc_embeds=retrieved_doc_embeds, retrieved_doc_ids=retrieved_doc_ids, question_encoder_last_hidden_state=question_encoder_last_hidden_state,
        question_enc_hidden_states=question_enc_hidden_states, question_enc_attentions=question_enc_attentions, generator_enc_last_hidden_state=gen_outputs.encoder_last_hidden_state,
        generator_enc_hidden_states=gen_outputs.encoder_hidden_states, generator_enc_attentions=gen_outputs.encoder_attentions, generator_dec_hidden_states=gen_outputs.decoder_hidden_states,
        generator_dec_attentions=gen_outputs.decoder_attentions, generator_cross_attentions=gen_outputs.cross_attentions)
@add_start_docstrings_to_model_forward("A RAG-sequence model implementation. It performs RAG-sequence specific marginalization in the forward pass.", RAG_START_DOCSTRING)
class RagSequenceForGeneration(RagPreTrainedModel):
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[PreTrainedModel] = None, generator: Optional[PreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        super().__init__(config)
        self.rag = RagModel(config=config, question_encoder=question_encoder, generator=generator, retriever=retriever)
    def set_retriever(self, retriever: RagRetriever): self.rag.retriever = retriever
    def set_context_encoder_for_training(self, ctx_encoder: PreTrainedModel):
        self.rag.context_encoder_training = True
        self.rag.ctx_encoder = ctx_encoder
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.Tensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.Tensor]]] = None,
    decoder_input_ids: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.BoolTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
    context_input_ids: Optional[torch.LongTensor] = None, context_attention_mask: Optional[torch.LongTensor] = None, doc_scores: Optional[torch.FloatTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_retrieved: Optional[bool] = None,
    exclude_bos_score: Optional[bool] = None, reduce_loss: Optional[bool] = None, labels: Optional[torch.LongTensor] = None,
    n_docs: Optional[int] = None, **kwargs) -> RetrievAugLMMarginOutput:
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        exclude_bos_score = exclude_bos_score if exclude_bos_score is not None else self.config.exclude_bos_score
        reduce_loss = reduce_loss if reduce_loss is not None else self.config.reduce_loss
        if labels is not None:
            if decoder_input_ids is None: decoder_input_ids = labels
            use_cache = False
        outputs = self.rag(input_ids=input_ids, attention_mask=attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
        context_input_ids=context_input_ids, context_attention_mask=context_attention_mask, doc_scores=doc_scores, past_key_values=past_key_values, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_retrieved=output_retrieved, n_docs=n_docs)
        loss = None
        if labels is not None: loss = self.get_nll(outputs.logits, outputs.doc_scores, decoder_input_ids, reduce_loss=reduce_loss, epsilon=self.config.label_smoothing, exclude_bos_score=exclude_bos_score, n_docs=n_docs)
        return RetrievAugLMMarginOutput(loss=loss, logits=outputs.logits, doc_scores=outputs.doc_scores, past_key_values=outputs.past_key_values, context_input_ids=outputs.context_input_ids,
        context_attention_mask=outputs.context_attention_mask, retrieved_doc_embeds=outputs.retrieved_doc_embeds, retrieved_doc_ids=outputs.retrieved_doc_ids,
        question_encoder_last_hidden_state=outputs.question_encoder_last_hidden_state, question_enc_hidden_states=outputs.question_enc_hidden_states,
        question_enc_attentions=outputs.question_enc_attentions, generator_enc_last_hidden_state=outputs.generator_enc_last_hidden_state,
        generator_enc_hidden_states=outputs.generator_enc_hidden_states, generator_enc_attentions=outputs.generator_enc_attentions,
        generator_dec_hidden_states=outputs.generator_dec_hidden_states, generator_dec_attentions=outputs.generator_dec_attentions,
        generator_cross_attentions=outputs.generator_cross_attentions)
    @property
    def retriever(self): return self.rag.retriever
    @property
    def generator(self): return self.rag.generator
    @property
    def question_encoder(self): return self.rag.question_encoder
    @torch.no_grad()
    def generate(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.LongTensor] = None, context_input_ids: Optional[torch.LongTensor] = None,
    context_attention_mask: Optional[torch.LongTensor] = None, doc_scores: Optional[torch.FloatTensor] = None, do_deduplication: Optional[bool] = None,
    num_return_sequences: Optional[int] = None, num_beams: Optional[int] = None, n_docs: Optional[int] = None, **model_kwargs) -> torch.LongTensor:
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        do_deduplication = do_deduplication if do_deduplication is not None else self.config.do_deduplication
        num_doc_return_sequences = (num_return_sequences if num_return_sequences is not None else self.config.num_return_sequences)
        num_beams = num_beams if num_beams is not None else self.config.num_beams
        assert (input_ids is not None or context_input_ids is not None), " At least one of input_ids or context_input_ids must be given"
        if self.retriever is not None and context_input_ids is None:
            question_hidden_states = self.question_encoder(input_ids, attention_mask=attention_mask)[0]
            context_input_ids = self.retriever(input_ids, question_hidden_states.cpu().detach().to(torch.float32).numpy(), prefix=self.generator.config.prefix,
            n_docs=n_docs, return_tensors="pt")["context_input_ids"]
            context_input_ids = context_input_ids.to(input_ids)
        hypos = []
        model_kwargs["num_beams"] = num_beams
        model_kwargs["num_return_sequences"] = num_beams
        model_kwargs["attention_mask"] = None
        batch_size = input_ids.shape[0] if input_ids is not None else context_input_ids.shape[0] // n_docs
        for index in range(batch_size):
            generator_input_ids = context_input_ids[index * n_docs : (index + 1) * n_docs]
            output_sequences = self.generator.generate(generator_input_ids, **model_kwargs)
            if do_deduplication: output_sequences = torch.stack(list({str(k.tolist()): k for k in output_sequences}.values()))
            num_candidates = output_sequences.shape[0]
            if input_ids is not None:
                new_input_ids = input_ids[index : index + 1].repeat(num_candidates, 1)
                outputs = self(new_input_ids, labels=output_sequences, exclude_bos_score=True)
            else:
                assert context_attention_mask is not None, ("Make sure that `context_attention_mask` are passed, if no `input_ids` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                assert doc_scores is not None, ("Make sure that `doc_scores` are passed, if no `input_ids` is set. Alternatively, you can set a retriever using the `set_retriever(...)` function.")
                individual_input_ids = generator_input_ids.repeat(num_candidates, 1)
                individual_attention_mask = context_attention_mask[index * n_docs : (index + 1) * n_docs]
                individual_attention_mask = individual_attention_mask.repeat(num_candidates, 1)
                individual_doc_scores = doc_scores[index : (index + 1), :]
                individual_doc_scores = individual_doc_scores.repeat(num_candidates, 1)
                outputs = self(context_input_ids=individual_input_ids, context_attention_mask=individual_attention_mask, doc_scores=individual_doc_scores,
                labels=output_sequences, exclude_bos_score=True)
            top_cand_inds = (-outputs["loss"]).topk(num_doc_return_sequences)[1]
            hypos.append(output_sequences[top_cand_inds])
        return self._cat_and_pad(hypos, pad_token_id=self.config.generator.pad_token_id)
    def get_nll(self, seq_logits, doc_scores, target, reduce_loss=False, epsilon=0.0, exclude_bos_score=False, n_docs=None):
        target = torch.cat([target[:, 1:], target.new(target.shape[0], 1).fill_(self.config.generator.pad_token_id)], 1)
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        bos_token_id = self.config.bos_token_id or self.config.generator.bos_token_id
        use_bos = bos_token_id is not None and target[:, 0].eq(bos_token_id).all()
        def _mask_pads(ll, smooth_obj):
            pad_mask = target.eq(self.config.generator.pad_token_id)
            if pad_mask.any():
                ll.masked_fill_(pad_mask, 0.0)
                smooth_obj.masked_fill_(pad_mask, 0.0)
            return ll.squeeze(-1), smooth_obj.squeeze(-1)
        seq_logprobs = nn.functional.log_softmax(seq_logits, dim=-1).view(seq_logits.shape[0] // n_docs, n_docs, -1, seq_logits.size(-1))
        doc_logprobs = nn.functional.log_softmax(doc_scores, dim=1).unsqueeze(-1).unsqueeze(-1)
        first_token_scores = seq_logprobs[:, :, :1, :]
        second_token_scores = seq_logprobs[:, :, 1:2, :]
        remainder = seq_logprobs[:, :, 2:, :]
        rag_logprobs = torch.cat([first_token_scores, second_token_scores + doc_logprobs, remainder], dim=2)
        target = target.unsqueeze(1).unsqueeze(-1).repeat(1, n_docs, 1, 1)
        assert target.dim() == rag_logprobs.dim()
        ll = rag_logprobs.gather(dim=-1, index=target)
        smooth_obj = rag_logprobs.sum(dim=-1, keepdim=True)
        ll, smooth_obj = _mask_pads(ll, smooth_obj)
        ll = ll[:, :, 1:].sum(2) if exclude_bos_score and use_bos else ll.sum(2)
        smooth_obj = smooth_obj.sum(2)
        ll = ll.logsumexp(1)
        smooth_obj = smooth_obj.logsumexp(1)
        nll_loss = -ll
        smooth_loss = -smooth_obj
        if reduce_loss:
            nll_loss = nll_loss.sum()
            smooth_loss = smooth_loss.sum()
        eps_i = epsilon / rag_logprobs.size(-1)
        loss = (1.0 - epsilon) * nll_loss + eps_i * smooth_loss
        return loss
    @staticmethod
    def _cat_and_pad(tensors, pad_token_id):
        output = (tensors[0].new(sum([t.shape[0] for t in tensors]), max([t.shape[1] for t in tensors])).fill_(pad_token_id))
        ind = 0
        for t in tensors:
            output[ind : ind + t.shape[0], : t.shape[1]] = t
            ind += t.shape[0]
        return output
@add_start_docstrings_to_model_forward("A RAG-token model implementation. It performs RAG-token specific marginalization in the forward pass.", RAG_START_DOCSTRING)
class RagTokenForGeneration(RagPreTrainedModel):
    def __init__(self, config: Optional[PretrainedConfig] = None, question_encoder: Optional[PreTrainedModel] = None, generator: Optional[PreTrainedModel] = None,
    retriever: Optional[RagRetriever] = None, **kwargs):
        assert config is not None or (question_encoder is not None and generator is not None), "Either a configuration or an encoder and a generator has to be provided."
        if config is None: config = RagConfig.from_question_encoder_generator_configs(question_encoder.config, generator.config, **kwargs)
        super().__init__(config)
        self.rag = RagModel(config=config, question_encoder=question_encoder, generator=generator, retriever=retriever)
    def set_retriever(self, retriever: RagRetriever): self.rag.retriever = retriever
    def set_context_encoder_for_training(self, ctx_encoder: PreTrainedModel):
        self.rag.context_encoder_training = True
        self.rag.ctx_encoder = ctx_encoder
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
    def _reorder_cache(past_key_values, beam_idx):
        def _reorder_stacked(hidden_states, new_order):
            n_docs = hidden_states.shape[0] // new_order.shape[0]
            hidden_states = hidden_states.view(-1, n_docs, *hidden_states.shape[1:])
            hidden_states = hidden_states.index_select(0, new_order)
            result = hidden_states.view(-1, *hidden_states.shape[2:])
            return result
        reordered_past = ()
        for layer_past in past_key_values: reordered_past += (tuple(_reorder_stacked(past_state, beam_idx.to(past_state.device)) for past_state in layer_past),)
        return reordered_past
    def marginalize(self, seq_logits, doc_scores, n_docs=None):
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        seq_logprobs = nn.functional.log_softmax(seq_logits, dim=-1).view(seq_logits.shape[0] // n_docs, n_docs, -1, seq_logits.size(-1))
        doc_logprobs = torch.log_softmax(doc_scores, dim=1)
        log_prob_sum = seq_logprobs + doc_logprobs.unsqueeze(-1).unsqueeze(-1)
        return torch.logsumexp(log_prob_sum, dim=1)
    @add_start_docstrings_to_model_forward(RAG_FORWARD_INPUTS_DOCSTRING)
    def forward(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.FloatTensor] = None, encoder_outputs: Optional[Tuple[Tuple[torch.Tensor]]] = None,
    decoder_input_ids: Optional[torch.LongTensor] = None, decoder_attention_mask: Optional[torch.BoolTensor] = None, past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
    context_input_ids: Optional[torch.LongTensor] = None, context_attention_mask: Optional[torch.LongTensor] = None, doc_scores: Optional[torch.FloatTensor] = None,
    use_cache: Optional[bool] = None, output_attentions: Optional[bool] = None, output_hidden_states: Optional[bool] = None, output_retrieved: Optional[bool] = None,
    do_marginalize: Optional[bool] = None, reduce_loss: Optional[bool] = None, labels: Optional[torch.LongTensor] = None, n_docs: Optional[int] = None,
    **kwargs) -> RetrievAugLMMarginOutput:
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        do_marginalize = do_marginalize if do_marginalize is not None else self.config.do_marginalize
        reduce_loss = reduce_loss if reduce_loss is not None else self.config.reduce_loss
        if labels is not None:
            if decoder_input_ids is None: decoder_input_ids = labels
            use_cache = False
        outputs = self.rag(input_ids=input_ids, attention_mask=attention_mask, encoder_outputs=encoder_outputs, decoder_input_ids=decoder_input_ids, decoder_attention_mask=decoder_attention_mask,
        context_input_ids=context_input_ids, context_attention_mask=context_attention_mask, doc_scores=doc_scores, past_key_values=past_key_values, use_cache=use_cache,
        output_attentions=output_attentions, output_hidden_states=output_hidden_states, output_retrieved=output_retrieved, n_docs=n_docs)
        loss = None
        logits = outputs.logits
        if labels is not None:
            assert decoder_input_ids is not None
            loss = self.get_nll(outputs.logits, outputs.doc_scores, labels, reduce_loss=reduce_loss, epsilon=self.config.label_smoothing, n_docs=n_docs)
        if do_marginalize: logits = self.marginalize(logits, outputs.doc_scores, n_docs)
        return RetrievAugLMMarginOutput(loss=loss, logits=logits, doc_scores=outputs.doc_scores, past_key_values=outputs.past_key_values, context_input_ids=outputs.context_input_ids,
        context_attention_mask=outputs.context_attention_mask, retrieved_doc_embeds=outputs.retrieved_doc_embeds, retrieved_doc_ids=outputs.retrieved_doc_ids,
        question_encoder_last_hidden_state=outputs.question_encoder_last_hidden_state, question_enc_hidden_states=outputs.question_enc_hidden_states,
        question_enc_attentions=outputs.question_enc_attentions, generator_enc_last_hidden_state=outputs.generator_enc_last_hidden_state,
        generator_enc_hidden_states=outputs.generator_enc_hidden_states, generator_enc_attentions=outputs.generator_enc_attentions,
        generator_dec_hidden_states=outputs.generator_dec_hidden_states, generator_dec_attentions=outputs.generator_dec_attentions,
        generator_cross_attentions=outputs.generator_cross_attentions)
    @torch.no_grad()
    def generate(self, input_ids: Optional[torch.LongTensor] = None, attention_mask: Optional[torch.LongTensor] = None, context_input_ids: Optional[torch.LongTensor] = None,
    context_attention_mask: Optional[torch.LongTensor] = None, doc_scores: Optional[torch.FloatTensor] = None, n_docs: Optional[int] = None,
    generation_config: Optional[GenerationConfig] = None, prefix_allowed_tokens_fn: Callable[[int, torch.Tensor], List[int]] = None,
    logits_processor: Optional[LogitsProcessorList] = LogitsProcessorList(), stopping_criteria: Optional[StoppingCriteriaList] = StoppingCriteriaList(),
    **kwargs) -> torch.LongTensor:
        if generation_config is None: generation_config = self.generation_config
        generation_config = copy.deepcopy(generation_config)
        model_kwargs = generation_config.update(**kwargs)
        kwargs_has_attention_mask = model_kwargs.get("attention_mask", None) is not None
        self._prepare_special_tokens(generation_config, kwargs_has_attention_mask)
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        if self.retriever is not None and context_input_ids is None:
            question_hidden_states = self.question_encoder(input_ids, attention_mask=attention_mask)[0]
            out = self.retriever(input_ids, question_hidden_states.cpu().detach().to(torch.float32).numpy(), prefix=self.generator.config.prefix, n_docs=n_docs, return_tensors="pt")
            context_input_ids, context_attention_mask, retrieved_doc_embeds = (out["context_input_ids"], out["context_attention_mask"], out["retrieved_doc_embeds"])
            retrieved_doc_embeds = retrieved_doc_embeds.to(question_hidden_states)
            context_input_ids = context_input_ids.to(input_ids)
            context_attention_mask = context_attention_mask.to(input_ids)
            doc_scores = torch.bmm(question_hidden_states.unsqueeze(1), retrieved_doc_embeds.transpose(1, 2)).squeeze(1)
        assert (context_input_ids.shape[0] % n_docs) == 0, (f" The first dimension of `context_input_ids` should be a multiple of `n_docs`={n_docs}, but is {context_input_ids.shape[0]}.")
        batch_size = context_input_ids.shape[0] // n_docs
        encoder = self.rag.generator.get_encoder()
        encoder_outputs = encoder(input_ids=context_input_ids, attention_mask=context_attention_mask, return_dict=True)
        input_ids = torch.full((batch_size * generation_config.num_beams, 1), generation_config.decoder_start_token_id, dtype=torch.long, device=next(self.parameters()).device)
        input_ids_seq_length = input_ids.shape[-1]
        last_hidden_state = encoder_outputs["last_hidden_state"]
        def extend_enc_output(tensor, num_beams=None):
            tensor = tensor[None, None, :].reshape((batch_size, 1, n_docs) + tensor.shape[1:])
            tensor = tensor.expand((batch_size, num_beams, n_docs) + tensor.shape[3:])
            return tensor.reshape((batch_size * num_beams * n_docs,) + tensor.shape[3:])
        context_attention_mask = extend_enc_output(context_attention_mask, num_beams=generation_config.num_beams)
        encoder_outputs["last_hidden_state"] = extend_enc_output(last_hidden_state, num_beams=generation_config.num_beams)
        doc_scores = doc_scores.repeat_interleave(generation_config.num_beams, dim=0)
        model_kwargs["doc_scores"] = doc_scores
        model_kwargs["encoder_outputs"] = encoder_outputs
        model_kwargs["attention_mask"] = context_attention_mask
        model_kwargs["n_docs"] = n_docs
        pre_processor = self._get_logits_processor(generation_config=generation_config, input_ids_seq_length=input_ids_seq_length, encoder_input_ids=context_input_ids,
        prefix_allowed_tokens_fn=prefix_allowed_tokens_fn, logits_processor=logits_processor, device=input_ids.device)
        prepared_stopping_criteria = self._get_stopping_criteria(generation_config=generation_config, stopping_criteria=stopping_criteria)
        if generation_config.num_beams == 1:
            if generation_config.num_return_sequences > 1: raise ValueError(f"num_return_sequences has to be 1, but is {generation_config.num_return_sequences} when doing greedy search.")
            return self._sample(input_ids, logits_processor=pre_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config,
            synced_gpus=False, streamer=None, **model_kwargs)
        elif generation_config.num_beams > 1:
            if generation_config.num_return_sequences > generation_config.num_beams: raise ValueError("`num_return_sequences` has to be smaller or equal to `num_beams`.")
            beam_scorer = BeamSearchScorer(batch_size=batch_size, num_beams=generation_config.num_beams, device=self.device, length_penalty=generation_config.length_penalty,
            do_early_stopping=generation_config.early_stopping, num_beam_hyps_to_keep=generation_config.num_return_sequences, max_length=generation_config.max_length)
            return self._beam_search(input_ids, beam_scorer, logits_processor=pre_processor, stopping_criteria=prepared_stopping_criteria, generation_config=generation_config,
            synced_gpus=False, **model_kwargs)
        else: raise ValueError(f"`num_beams` has to be an integer strictly superior to 0 (≥ 1), but is {generation_config.num_beams}")
    def get_input_embeddings(self): return self.rag.generator.get_input_embeddings()
    def get_output_embeddings(self): return self.rag.generator.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings): return self.rag.generator.set_output_embeddings(new_embeddings)
    def shift_tokens_right(self, input_ids, start_token_id=None):
        if start_token_id is None: start_token_id = self.config.decoder_start_token_id
        shifted_input_ids = input_ids.new_zeros(input_ids.shape)
        shifted_input_ids[:, 1:] = input_ids[:, :-1].clone()
        shifted_input_ids[:, 0] = start_token_id
        return shifted_input_ids
    def get_nll(self, seq_logits, doc_scores, target, reduce_loss=False, epsilon=0.0, n_docs=None):
        n_docs = n_docs if n_docs is not None else self.config.n_docs
        target = torch.cat([target[:, 1:], target.new(target.shape[0], 1).fill_(self.config.generator.pad_token_id)], 1)
        def _mask_pads(ll, smooth_obj):
            pad_mask = target.eq(self.config.generator.pad_token_id)
            if pad_mask.any():
                ll.masked_fill_(pad_mask, 0.0)
                smooth_obj.masked_fill_(pad_mask, 0.0)
            return ll.squeeze(-1), smooth_obj.squeeze(-1)
        rag_logprobs = self.marginalize(seq_logits, doc_scores, n_docs)
        target = target.unsqueeze(-1)
        assert target.dim() == rag_logprobs.dim()
        ll = rag_logprobs.gather(dim=-1, index=target)
        smooth_obj = rag_logprobs.sum(dim=-1, keepdim=True)
        ll, smooth_obj = _mask_pads(ll, smooth_obj)
        ll = ll.sum(1)
        smooth_obj = smooth_obj.sum(1)
        nll_loss = -ll
        smooth_loss = -smooth_obj
        if reduce_loss:
            nll_loss = nll_loss.sum()
            smooth_loss = smooth_loss.sum()
        eps_i = epsilon / rag_logprobs.size(-1)
        loss = (1.0 - epsilon) * nll_loss + eps_i * smooth_loss
        return loss
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
