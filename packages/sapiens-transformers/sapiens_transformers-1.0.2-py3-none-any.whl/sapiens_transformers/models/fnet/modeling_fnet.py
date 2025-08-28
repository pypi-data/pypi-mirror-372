"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import warnings
from dataclasses import dataclass
from functools import partial
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss, MSELoss
from ...utils import is_scipy_available
if is_scipy_available(): from scipy import linalg
from ...activations import ACT2FN
from ...modeling_outputs import (BaseModelOutput, BaseModelOutputWithPooling, MaskedLMOutput, ModelOutput, MultipleChoiceModelOutput, NextSentencePredictorOutput,
QuestionAnsweringModelOutput, SequenceClassifierOutput, TokenClassifierOutput)
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import apply_chunking_to_forward
from ...utils import (add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings)
from .configuration_fnet import FNetConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "google/fnet-base"
_CONFIG_FOR_DOC = "FNetConfig"
def _two_dim_matmul(x, matrix_dim_one, matrix_dim_two):
    seq_length = x.shape[1]
    matrix_dim_one = matrix_dim_one[:seq_length, :seq_length]
    x = x.type(torch.complex64)
    return torch.einsum("bij,jk,ni->bnk", x, matrix_dim_two, matrix_dim_one)
def two_dim_matmul(x, matrix_dim_one, matrix_dim_two): return _two_dim_matmul(x, matrix_dim_one, matrix_dim_two)
def fftn(x):
    out = x
    for axis in reversed(range(x.ndim)[1:]): out = torch.fft.fft(out, axis=axis)
    return out
class FNetEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.word_embeddings = nn.Embedding(config.vocab_size, config.hidden_size, padding_idx=config.pad_token_id)
        self.position_embeddings = nn.Embedding(config.max_position_embeddings, config.hidden_size)
        self.token_type_embeddings = nn.Embedding(config.type_vocab_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.projection = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.register_buffer("position_ids", torch.arange(config.max_position_embeddings).expand((1, -1)), persistent=False)
        self.register_buffer("token_type_ids", torch.zeros(self.position_ids.size(), dtype=torch.long), persistent=False)
    def forward(self, input_ids=None, token_type_ids=None, position_ids=None, inputs_embeds=None):
        if input_ids is not None: input_shape = input_ids.size()
        else: input_shape = inputs_embeds.size()[:-1]
        seq_length = input_shape[1]
        if position_ids is None: position_ids = self.position_ids[:, :seq_length]
        if token_type_ids is None:
            if hasattr(self, "token_type_ids"):
                buffered_token_type_ids = self.token_type_ids[:, :seq_length]
                buffered_token_type_ids_expanded = buffered_token_type_ids.expand(input_shape[0], seq_length)
                token_type_ids = buffered_token_type_ids_expanded
            else: token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=self.position_ids.device)
        if inputs_embeds is None: inputs_embeds = self.word_embeddings(input_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        embeddings = inputs_embeds + token_type_embeddings
        position_embeddings = self.position_embeddings(position_ids)
        embeddings += position_embeddings
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.projection(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
class FNetBasicFourierTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self._init_fourier_transform(config)
    def _init_fourier_transform(self, config):
        if not config.use_tpu_fourier_optimizations: self.fourier_transform = partial(torch.fft.fftn, dim=(1, 2))
        elif config.max_position_embeddings <= 4096:
            if is_scipy_available():
                self.register_buffer("dft_mat_hidden", torch.tensor(linalg.dft(config.hidden_size), dtype=torch.complex64))
                self.register_buffer("dft_mat_seq", torch.tensor(linalg.dft(config.tpu_short_seq_length), dtype=torch.complex64))
                self.fourier_transform = partial(two_dim_matmul, matrix_dim_one=self.dft_mat_seq, matrix_dim_two=self.dft_mat_hidden)
            else:
                logging.warning("SciPy is needed for DFT matrix calculation and is not found. Using TPU optimized fast fourier transform instead.")
                self.fourier_transform = fftn
        else: self.fourier_transform = fftn
    def forward(self, hidden_states):
        outputs = self.fourier_transform(hidden_states).real
        return (outputs,)
class FNetBasicOutput(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states, input_tensor):
        hidden_states = self.LayerNorm(input_tensor + hidden_states)
        return hidden_states
class FNetFourierTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.self = FNetBasicFourierTransform(config)
        self.output = FNetBasicOutput(config)
    def forward(self, hidden_states):
        self_outputs = self.self(hidden_states)
        fourier_output = self.output(self_outputs[0], hidden_states)
        outputs = (fourier_output,)
        return outputs
class FNetIntermediate(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str): self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else: self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class FNetOutput(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.LayerNorm(hidden_states + input_tensor)
        return hidden_states
class FNetLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.fourier = FNetFourierTransform(config)
        self.intermediate = FNetIntermediate(config)
        self.output = FNetOutput(config)
    def forward(self, hidden_states):
        self_fourier_outputs = self.fourier(hidden_states)
        fourier_output = self_fourier_outputs[0]
        layer_output = apply_chunking_to_forward(self.feed_forward_chunk, self.chunk_size_feed_forward, self.seq_len_dim, fourier_output)
        outputs = (layer_output,)
        return outputs
    def feed_forward_chunk(self, fourier_output):
        intermediate_output = self.intermediate(fourier_output)
        layer_output = self.output(intermediate_output, fourier_output)
        return layer_output
class FNetEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([FNetLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(self, hidden_states, output_hidden_states=False, return_dict=True):
        all_hidden_states = () if output_hidden_states else None
        for i, layer_module in enumerate(self.layer):
            if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
            if self.gradient_checkpointing and self.training: layer_outputs = self._gradient_checkpointing_func(layer_module.__call__, hidden_states)
            else: layer_outputs = layer_module(hidden_states)
            hidden_states = layer_outputs[0]
        if output_hidden_states: all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict: return tuple(v for v in [hidden_states, all_hidden_states] if v is not None)
        return BaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states)
class FNetPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.activation = nn.Tanh()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output
class FNetPredictionHeadTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        if isinstance(config.hidden_act, str): self.transform_act_fn = ACT2FN[config.hidden_act]
        else: self.transform_act_fn = config.hidden_act
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        return hidden_states
class FNetLMPredictionHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.transform = FNetPredictionHeadTransform(config)
        self.decoder = nn.Linear(config.hidden_size, config.vocab_size)
        self.bias = nn.Parameter(torch.zeros(config.vocab_size))
        self.decoder.bias = self.bias
    def forward(self, hidden_states):
        hidden_states = self.transform(hidden_states)
        hidden_states = self.decoder(hidden_states)
        return hidden_states
    def _tie_weights(self) -> None:
        if self.decoder.bias.device.type == "meta": self.decoder.bias = self.bias
        else: self.bias = self.decoder.bias
class FNetOnlyMLMHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.predictions = FNetLMPredictionHead(config)
    def forward(self, sequence_output):
        prediction_scores = self.predictions(sequence_output)
        return prediction_scores
class FNetOnlyNSPHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.seq_relationship = nn.Linear(config.hidden_size, 2)
    def forward(self, pooled_output):
        seq_relationship_score = self.seq_relationship(pooled_output)
        return seq_relationship_score
class FNetPreTrainingHeads(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.predictions = FNetLMPredictionHead(config)
        self.seq_relationship = nn.Linear(config.hidden_size, 2)
    def forward(self, sequence_output, pooled_output):
        prediction_scores = self.predictions(sequence_output)
        seq_relationship_score = self.seq_relationship(pooled_output)
        return prediction_scores, seq_relationship_score
class FNetPreTrainedModel(PreTrainedModel):
    config_class = FNetConfig
    base_model_prefix = "fnet"
    supports_gradient_checkpointing = True
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None: module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
@dataclass
class FNetForPreTrainingOutput(ModelOutput):
    """Args:"""
    loss: Optional[torch.FloatTensor] = None
    prediction_logits: torch.FloatTensor = None
    seq_relationship_logits: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
FNET_START_DOCSTRING = r"""
    This model is a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) sub-class. Use
    it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage and
    behavior.
    Parameters:
        config ([`FNetConfig`]): Model configuration class with all the parameters of the model.
            Initializing with a config file does not load the weights associated with the model, only the
            configuration. Check out the [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
FNET_INPUTS_DOCSTRING = r"""
    Args:
        input_ids (`torch.LongTensor` of shape `(0)`):
            Indices of input sequence tokens in the vocabulary.
            Indices can be obtained using [`AutoTokenizer`]. See [`PreTrainedTokenizer.encode`] and
            [`PreTrainedTokenizer.__call__`] for details.
            [What are input IDs?](../glossary#input-ids)
        token_type_ids (`torch.LongTensor` of shape `(0)`, *optional*):
            Segment token indices to indicate first and second portions of the inputs. Indices are selected in `[0,
            1]`:
            - 0 corresponds to a *sentence A* token,
            - 1 corresponds to a *sentence B* token.
            [What are token type IDs?](../glossary#token-type-ids)
        position_ids (`torch.LongTensor` of shape `(0)`, *optional*):
            Indices of positions of each input sequence tokens in the position embeddings. Selected in the range `[0,
            config.max_position_embeddings - 1]`.
            [What are position IDs?](../glossary#position-ids)
        inputs_embeds (`torch.FloatTensor` of shape `(0, hidden_size)`, *optional*):
            Optionally, instead of passing `input_ids` you can choose to directly pass an embedded representation. This
            is useful if you want more control over how to convert *input_ids* indices into associated vectors than the
            model's internal embedding lookup matrix.
        output_hidden_states (`bool`, *optional*):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors for
            more detail.
        return_dict (`bool`, *optional*):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.
"""
@add_start_docstrings("The bare FNet Model transformer outputting raw hidden-states without any specific head on top.", FNET_START_DOCSTRING)
class FNetModel(FNetPreTrainedModel):
    def __init__(self, config, add_pooling_layer=True):
        super().__init__(config)
        self.config = config
        self.embeddings = FNetEmbeddings(config)
        self.encoder = FNetEncoder(config)
        self.pooler = FNetPooler(config) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self): return self.embeddings.word_embeddings
    def set_input_embeddings(self, value): self.embeddings.word_embeddings = value
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.LongTensor] = None, token_type_ids: Optional[torch.LongTensor] = None, position_ids: Optional[torch.LongTensor] = None,
    inputs_embeds: Optional[torch.FloatTensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[tuple, BaseModelOutput]:
        output_hidden_states = (output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states)
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None: raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
            batch_size, seq_length = input_shape
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
            batch_size, seq_length = input_shape
        else: raise ValueError("You have to specify either input_ids or inputs_embeds")
        if (self.config.use_tpu_fourier_optimizations and seq_length <= 4096 and self.config.tpu_short_seq_length != seq_length): raise ValueError("The `tpu_short_seq_length` in FNetConfig should be set equal to the sequence length being passed to the model when using TPU optimizations.")
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        if token_type_ids is None:
            if hasattr(self.embeddings, "token_type_ids"):
                buffered_token_type_ids = self.embeddings.token_type_ids[:, :seq_length]
                buffered_token_type_ids_expanded = buffered_token_type_ids.expand(batch_size, seq_length)
                token_type_ids = buffered_token_type_ids_expanded
            else: token_type_ids = torch.zeros(input_shape, dtype=torch.long, device=device)
        embedding_output = self.embeddings(input_ids=input_ids, position_ids=position_ids, token_type_ids=token_type_ids, inputs_embeds=inputs_embeds)
        encoder_outputs = self.encoder(embedding_output, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = encoder_outputs[0]
        pooler_output = self.pooler(sequence_output) if self.pooler is not None else None
        if not return_dict: return (sequence_output, pooler_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(last_hidden_state=sequence_output, pooler_output=pooler_output, hidden_states=encoder_outputs.hidden_states)
@add_start_docstrings("FNet Model with two heads on top as done during the pretraining: a `masked language modeling` head and a `next sentence prediction (classification)` head.", FNET_START_DOCSTRING)
class FNetForPreTraining(FNetPreTrainedModel):
    _tied_weights_keys = ["cls.predictions.decoder.bias", "cls.predictions.decoder.weight"]
    def __init__(self, config):
        super().__init__(config)
        self.fnet = FNetModel(config)
        self.cls = FNetPreTrainingHeads(config)
        self.post_init()
    def get_output_embeddings(self): return self.cls.predictions.decoder
    def set_output_embeddings(self, new_embeddings):
        self.cls.predictions.decoder = new_embeddings
        self.cls.predictions.bias = new_embeddings.bias
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, next_sentence_label: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, FNetForPreTrainingOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output, pooled_output = outputs[:2]
        prediction_scores, seq_relationship_score = self.cls(sequence_output, pooled_output)
        total_loss = None
        if labels is not None and next_sentence_label is not None:
            loss_fct = CrossEntropyLoss()
            masked_lm_loss = loss_fct(prediction_scores.view(-1, self.config.vocab_size), labels.view(-1))
            next_sentence_loss = loss_fct(seq_relationship_score.view(-1, 2), next_sentence_label.view(-1))
            total_loss = masked_lm_loss + next_sentence_loss
        if not return_dict:
            output = (prediction_scores, seq_relationship_score) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output
        return FNetForPreTrainingOutput(loss=total_loss, prediction_logits=prediction_scores, seq_relationship_logits=seq_relationship_score, hidden_states=outputs.hidden_states)
@add_start_docstrings("FNet Model with a `language modeling` head on top.", FNET_START_DOCSTRING)
class FNetForMaskedLM(FNetPreTrainedModel):
    _tied_weights_keys = ["cls.predictions.decoder.bias", "cls.predictions.decoder.weight"]
    def __init__(self, config):
        super().__init__(config)
        self.fnet = FNetModel(config)
        self.cls = FNetOnlyMLMHead(config)
        self.post_init()
    def get_output_embeddings(self): return self.cls.predictions.decoder
    def set_output_embeddings(self, new_embeddings):
        self.cls.predictions.decoder = new_embeddings
        self.cls.predictions.bias = new_embeddings.bias
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, MaskedLMOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        prediction_scores = self.cls(sequence_output)
        masked_lm_loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            masked_lm_loss = loss_fct(prediction_scores.view(-1, self.config.vocab_size), labels.view(-1))
        if not return_dict:
            output = (prediction_scores,) + outputs[2:]
            return ((masked_lm_loss,) + output) if masked_lm_loss is not None else output
        return MaskedLMOutput(loss=masked_lm_loss, logits=prediction_scores, hidden_states=outputs.hidden_states)
@add_start_docstrings("FNet Model with a `next sentence prediction (classification)` head on top.", FNET_START_DOCSTRING)
class FNetForNextSentencePrediction(FNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.fnet = FNetModel(config)
        self.cls = FNetOnlyNSPHead(config)
        self.post_init()
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None, **kwargs) -> Union[Tuple, NextSentencePredictorOutput]:
        if "next_sentence_label" in kwargs:
            warnings.warn("The `next_sentence_label` argument is deprecated and will be removed in a future version, use `labels` instead.", FutureWarning)
            labels = kwargs.pop("next_sentence_label")
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs[1]
        seq_relationship_scores = self.cls(pooled_output)
        next_sentence_loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            next_sentence_loss = loss_fct(seq_relationship_scores.view(-1, 2), labels.view(-1))
        if not return_dict:
            output = (seq_relationship_scores,) + outputs[2:]
            return ((next_sentence_loss,) + output) if next_sentence_loss is not None else output
        return NextSentencePredictorOutput(loss=next_sentence_loss, logits=seq_relationship_scores, hidden_states=outputs.hidden_states)
@add_start_docstrings("FNet Model transformer with a sequence classification/regression head on top (a linear layer on top of the pooled output) e.g. for GLUE tasks.", FNET_START_DOCSTRING)
class FNetForSequenceClassification(FNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.fnet = FNetModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, SequenceClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            if self.config.problem_type is None:
                if self.num_labels == 1: self.config.problem_type = "regression"
                elif self.num_labels > 1 and (labels.dtype == torch.long or labels.dtype == torch.int): self.config.problem_type = "single_label_classification"
                else: self.config.problem_type = "multi_label_classification"
            if self.config.problem_type == "regression":
                loss_fct = MSELoss()
                if self.num_labels == 1: loss = loss_fct(logits.squeeze(), labels.squeeze())
                else: loss = loss_fct(logits, labels)
            elif self.config.problem_type == "single_label_classification":
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            elif self.config.problem_type == "multi_label_classification":
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits, labels)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states)
@add_start_docstrings("FNet Model with a multiple choice classification head on top (a linear layer on top of the pooled output and a softmax) e.g. for RocStories/SWAG tasks.", FNET_START_DOCSTRING)
class FNetForMultipleChoice(FNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.fnet = FNetModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, 1)
        self.post_init()
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, num_choices, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, MultipleChoiceModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        num_choices = input_ids.shape[1] if input_ids is not None else inputs_embeds.shape[1]
        input_ids = input_ids.view(-1, input_ids.size(-1)) if input_ids is not None else None
        token_type_ids = token_type_ids.view(-1, token_type_ids.size(-1)) if token_type_ids is not None else None
        position_ids = position_ids.view(-1, position_ids.size(-1)) if position_ids is not None else None
        inputs_embeds = (inputs_embeds.view(-1, inputs_embeds.size(-2), inputs_embeds.size(-1)) if inputs_embeds is not None else None)
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        reshaped_logits = logits.view(-1, num_choices)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(reshaped_logits, labels)
        if not return_dict:
            output = (reshaped_logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return MultipleChoiceModelOutput(loss=loss, logits=reshaped_logits, hidden_states=outputs.hidden_states)
@add_start_docstrings("FNet Model with a token classification head on top (a linear layer on top of the hidden-states output) e.g. for Named-Entity-Recognition (NER) tasks.", FNET_START_DOCSTRING)
class FNetForTokenClassification(FNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.fnet = FNetModel(config)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    labels: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, TokenClassifierOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        sequence_output = self.dropout(sequence_output)
        logits = self.classifier(sequence_output)
        loss = None
        if labels is not None:
            loss_fct = CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TokenClassifierOutput(loss=loss, logits=logits, hidden_states=outputs.hidden_states)
@add_start_docstrings("""
    FNet Model with a span classification head on top for extractive question-answering tasks like SQuAD (a linear
    layers on top of the hidden-states output to compute `span start logits` and `span end logits`).
    """, FNET_START_DOCSTRING)
class FNetForQuestionAnswering(FNetPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.fnet = FNetModel(config)
        self.qa_outputs = nn.Linear(config.hidden_size, config.num_labels)
        self.post_init()
    @add_start_docstrings_to_model_forward(FNET_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    def forward(self, input_ids: Optional[torch.Tensor] = None, token_type_ids: Optional[torch.Tensor] = None, position_ids: Optional[torch.Tensor] = None, inputs_embeds: Optional[torch.Tensor] = None,
    start_positions: Optional[torch.Tensor] = None, end_positions: Optional[torch.Tensor] = None, output_hidden_states: Optional[bool] = None, return_dict: Optional[bool] = None) -> Union[Tuple, QuestionAnsweringModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.fnet(input_ids, token_type_ids=token_type_ids, position_ids=position_ids, inputs_embeds=inputs_embeds, output_hidden_states=output_hidden_states, return_dict=return_dict)
        sequence_output = outputs[0]
        logits = self.qa_outputs(sequence_output)
        start_logits, end_logits = logits.split(1, dim=-1)
        start_logits = start_logits.squeeze(-1).contiguous()
        end_logits = end_logits.squeeze(-1).contiguous()
        total_loss = None
        if start_positions is not None and end_positions is not None:
            if len(start_positions.size()) > 1: start_positions = start_positions.squeeze(-1)
            if len(end_positions.size()) > 1: end_positions = end_positions.squeeze(-1)
            ignored_index = start_logits.size(1)
            start_positions = start_positions.clamp(0, ignored_index)
            end_positions = end_positions.clamp(0, ignored_index)
            loss_fct = CrossEntropyLoss(ignore_index=ignored_index)
            start_loss = loss_fct(start_logits, start_positions)
            end_loss = loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2
        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output
        return QuestionAnsweringModelOutput(loss=total_loss, start_logits=start_logits, end_logits=end_logits, hidden_states=outputs.hidden_states)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
