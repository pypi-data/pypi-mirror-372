"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from ...configuration_utils import PretrainedConfig
class TapasConfig(PretrainedConfig):
    model_type = "tapas"
    def __init__(self, vocab_size=30522, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, intermediate_size=3072, hidden_act="gelu", hidden_dropout_prob=0.1,
    attention_probs_dropout_prob=0.1, max_position_embeddings=1024, type_vocab_sizes=[3, 256, 256, 2, 256, 256, 10], initializer_range=0.02, layer_norm_eps=1e-12, pad_token_id=0,
    positive_label_weight=10.0, num_aggregation_labels=0, aggregation_loss_weight=1.0, use_answer_as_supervision=None, answer_loss_importance=1.0, use_normalized_answer_loss=False,
    huber_loss_delta=None, temperature=1.0, aggregation_temperature=1.0, use_gumbel_for_cells=False, use_gumbel_for_aggregation=False, average_approximation_function="ratio",
    cell_selection_preference=None, answer_loss_cutoff=None, max_num_rows=64, max_num_columns=32, average_logits_per_cell=False, select_one_column=True, allow_empty_column_selection=False,
    init_cell_selection_weights_to_zero=False, reset_position_index_per_cell=True, disable_per_token_loss=False, aggregation_labels=None, no_aggregation_label_index=None, **kwargs):
        super().__init__(pad_token_id=pad_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_sizes = type_vocab_sizes
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.positive_label_weight = positive_label_weight
        self.num_aggregation_labels = num_aggregation_labels
        self.aggregation_loss_weight = aggregation_loss_weight
        self.use_answer_as_supervision = use_answer_as_supervision
        self.answer_loss_importance = answer_loss_importance
        self.use_normalized_answer_loss = use_normalized_answer_loss
        self.huber_loss_delta = huber_loss_delta
        self.temperature = temperature
        self.aggregation_temperature = aggregation_temperature
        self.use_gumbel_for_cells = use_gumbel_for_cells
        self.use_gumbel_for_aggregation = use_gumbel_for_aggregation
        self.average_approximation_function = average_approximation_function
        self.cell_selection_preference = cell_selection_preference
        self.answer_loss_cutoff = answer_loss_cutoff
        self.max_num_rows = max_num_rows
        self.max_num_columns = max_num_columns
        self.average_logits_per_cell = average_logits_per_cell
        self.select_one_column = select_one_column
        self.allow_empty_column_selection = allow_empty_column_selection
        self.init_cell_selection_weights_to_zero = init_cell_selection_weights_to_zero
        self.reset_position_index_per_cell = reset_position_index_per_cell
        self.disable_per_token_loss = disable_per_token_loss
        self.aggregation_labels = aggregation_labels
        self.no_aggregation_label_index = no_aggregation_label_index
        if isinstance(self.aggregation_labels, dict): self.aggregation_labels = {int(k): v for k, v in aggregation_labels.items()}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
