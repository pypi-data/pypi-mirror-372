"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Union
import torch
import torch.utils.checkpoint
from torch import nn
from ...modeling_utils import ModelOutput, PreTrainedModel
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_univnet import UnivNetConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "UnivNetConfig"
_CHECKPOINT_FOR_DOC = "dg845/univnet-dev"
@dataclass
class UnivNetModelOutput(ModelOutput):
    """Args:"""
    waveforms: torch.FloatTensor = None
    waveform_lengths: torch.FloatTensor = None
class UnivNetKernelPredictorResidualBlock(nn.Module):
    def __init__(self, config: UnivNetConfig):
        super().__init__()
        self.channels = config.model_in_channels
        self.kernel_size = config.kernel_predictor_conv_size
        self.dropout_prob = config.kernel_predictor_dropout
        self.leaky_relu_slope = config.leaky_relu_slope
        padding = (self.kernel_size - 1) // 2
        self.dropout = nn.Dropout(self.dropout_prob)
        self.conv1 = nn.Conv1d(self.channels, self.channels, self.kernel_size, padding=padding, bias=True)
        self.conv2 = nn.Conv1d(self.channels, self.channels, self.kernel_size, padding=padding, bias=True)
    def forward(self, hidden_states: torch.FloatTensor):
        residual = hidden_states
        hidden_states = self.dropout(hidden_states)
        hidden_states = self.conv1(hidden_states)
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        hidden_states = self.conv2(hidden_states)
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        return hidden_states + residual
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv1)
        weight_norm(self.conv2)
    def remove_weight_norm(self):
        nn.utils.remove_weight_norm(self.conv1)
        nn.utils.remove_weight_norm(self.conv2)
class UnivNetKernelPredictor(nn.Module):
    def __init__(self, config: UnivNetConfig, conv_kernel_size: int = 3, conv_layers: int = 4):
        super().__init__()
        self.conv_in_channels = config.model_hidden_channels
        self.conv_out_channels = 2 * config.model_hidden_channels
        self.conv_kernel_size = conv_kernel_size
        self.conv_layers = conv_layers
        self.kernel_channels = (self.conv_in_channels * self.conv_out_channels * self.conv_kernel_size * self.conv_layers)
        self.bias_channels = self.conv_out_channels * self.conv_layers
        self.resnet_in_channels = config.num_mel_bins
        self.resnet_hidden_channels = config.kernel_predictor_hidden_channels
        self.resnet_kernel_size = config.kernel_predictor_conv_size
        self.num_blocks = config.kernel_predictor_num_blocks
        self.leaky_relu_slope = config.leaky_relu_slope
        padding = (self.resnet_kernel_size - 1) // 2
        self.input_conv = nn.Conv1d(self.resnet_in_channels, self.resnet_hidden_channels, 5, padding=2, bias=True)
        self.resblocks = nn.ModuleList([UnivNetKernelPredictorResidualBlock(config) for _ in range(self.num_blocks)])
        self.kernel_conv = nn.Conv1d(self.resnet_hidden_channels, self.kernel_channels, self.resnet_kernel_size, padding=padding, bias=True)
        self.bias_conv = nn.Conv1d(self.resnet_hidden_channels, self.bias_channels, self.resnet_kernel_size, padding=padding, bias=True)
    def forward(self, spectrogram: torch.FloatTensor):
        batch_size, _, seq_length = spectrogram.shape
        hidden_states = self.input_conv(spectrogram)
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        for resblock in self.resblocks: hidden_states = resblock(hidden_states)
        kernel_hidden_states = self.kernel_conv(hidden_states)
        bias_hidden_states = self.bias_conv(hidden_states)
        kernels = kernel_hidden_states.view(batch_size, self.conv_layers, self.conv_in_channels, self.conv_out_channels, self.conv_kernel_size, seq_length).contiguous()
        biases = bias_hidden_states.view(batch_size, self.conv_layers, self.conv_out_channels, seq_length).contiguous()
        return kernels, biases
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.input_conv)
        for layer in self.resblocks: layer.apply_weight_norm()
        weight_norm(self.kernel_conv)
        weight_norm(self.bias_conv)
    def remove_weight_norm(self):
        nn.utils.remove_weight_norm(self.input_conv)
        for layer in self.resblocks: layer.remove_weight_norm()
        nn.utils.remove_weight_norm(self.kernel_conv)
        nn.utils.remove_weight_norm(self.bias_conv)
class UnivNetLvcResidualBlock(nn.Module):
    def __init__(self, config: UnivNetConfig, kernel_size: int, dilation: int):
        super().__init__()
        self.hidden_channels = config.model_hidden_channels
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.leaky_relu_slope = config.leaky_relu_slope
        padding = self.dilation * (self.kernel_size - 1) // 2
        self.conv = nn.Conv1d(self.hidden_channels, self.hidden_channels, self.kernel_size, padding=padding, dilation=self.dilation)
    def forward(self, hidden_states, kernel, bias, hop_size=256):
        residual = hidden_states
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        hidden_states = self.conv(hidden_states)
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        hidden_states = self.location_variable_convolution(hidden_states, kernel, bias, hop_size=hop_size)
        hidden_states = torch.sigmoid(hidden_states[:, : self.hidden_channels, :]) * torch.tanh(hidden_states[:, self.hidden_channels :, :])
        hidden_states = residual + hidden_states
        return hidden_states
    def location_variable_convolution(self, hidden_states: torch.FloatTensor, kernel: torch.FloatTensor, bias: torch.FloatTensor, dilation: int = 1, hop_size: int = 256):
        batch, _, in_length = hidden_states.shape
        batch, _, out_channels, kernel_size, kernel_length = kernel.shape
        if in_length != (kernel_length * hop_size): raise ValueError(f"Dim 2 of `hidden_states` should be {kernel_length * hop_size}) but got {in_length}. Please check `hidden_states` or `kernel` and `hop_size` to make sure they are correct.")
        padding = dilation * int((kernel_size - 1) / 2)
        hidden_states = nn.functional.pad(hidden_states, (padding, padding), "constant", 0)
        hidden_states = hidden_states.unfold(2, hop_size + 2 * padding, hop_size)
        if hop_size < dilation: hidden_states = nn.functional.pad(hidden_states, (0, dilation), "constant", 0)
        hidden_states = hidden_states.unfold(3, dilation, dilation)
        hidden_states = hidden_states[:, :, :, :, :hop_size]
        hidden_states = hidden_states.transpose(3, 4)
        hidden_states = hidden_states.unfold(4, kernel_size, 1)
        output_hidden_states = torch.einsum("bildsk,biokl->bolsd", hidden_states, kernel)
        output_hidden_states = output_hidden_states.to(memory_format=torch.channels_last_3d)
        bias = bias.unsqueeze(-1).unsqueeze(-1).to(memory_format=torch.channels_last_3d)
        output_hidden_states = output_hidden_states + bias
        output_hidden_states = output_hidden_states.contiguous().view(batch, out_channels, -1)
        return output_hidden_states
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv)
    def remove_weight_norm(self): nn.utils.remove_weight_norm(self.conv)
class UnivNetLvcBlock(nn.Module):
    def __init__(self, config: UnivNetConfig, layer_id: int, lvc_hop_size: int = 256):
        super().__init__()
        self.hidden_channels = config.model_hidden_channels
        self.kernel_size = config.resblock_kernel_sizes[layer_id]
        self.stride = config.resblock_stride_sizes[layer_id]
        self.dilations = config.resblock_dilation_sizes[layer_id]
        self.cond_hop_length = lvc_hop_size
        self.leaky_relu_slope = config.leaky_relu_slope
        self.num_blocks = len(self.dilations)
        self.convt_pre = nn.ConvTranspose1d(self.hidden_channels, self.hidden_channels, 2 * self.stride, stride=self.stride, padding=self.stride // 2 + self.stride % 2, output_padding=self.stride % 2)
        self.kernel_predictor = UnivNetKernelPredictor(config, self.kernel_size, self.num_blocks)
        self.resblocks = nn.ModuleList([UnivNetLvcResidualBlock(config, self.kernel_size, self.dilations[i]) for i in range(self.num_blocks)])
    def forward(self, hidden_states: torch.FloatTensor, spectrogram: torch.FloatTensor):
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        hidden_states = self.convt_pre(hidden_states)
        kernels, biases = self.kernel_predictor(spectrogram)
        for i, resblock in enumerate(self.resblocks):
            kernel = kernels[:, i, :, :, :, :]
            bias = biases[:, i, :, :]
            hidden_states = resblock(hidden_states, kernel, bias, hop_size=self.cond_hop_length)
        return hidden_states
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.convt_pre)
        self.kernel_predictor.apply_weight_norm()
        for layer in self.resblocks: layer.apply_weight_norm()
    def remove_weight_norm(self):
        nn.utils.remove_weight_norm(self.convt_pre)
        self.kernel_predictor.remove_weight_norm()
        for layer in self.resblocks: layer.remove_weight_norm()
UNIVNET_START_DOCSTRING = r"""
    This model inherits from [`PreTrainedModel`]. Check the superclass documentation for the generic methods the
    library implements for all its model (such as downloading or saving, resizing the input embeddings, pruning heads
    etc.)
    This model is also a PyTorch [torch.nn.Module](https://pytorch.org/docs/stable/nn.html#torch.nn.Module) subclass.
    Use it as a regular PyTorch Module and refer to the PyTorch documentation for all matter related to general usage
    and behavior.
    Parameters:
        config ([`UnivNetConfig`]):
            Model configuration class with all the parameters of the model. Initializing with a config file does not
            load the weights associated with the model, only the configuration. Check out the
            [`~PreTrainedModel.from_pretrained`] method to load the model weights.
"""
UNIVNET_INPUTS_DOCSTRING = r"""
    Converts a noise waveform and a conditioning spectrogram to a speech waveform. Passing a batch of log-mel
    spectrograms returns a batch of speech waveforms. Passing a single, un-batched log-mel spectrogram returns a
    single, un-batched speech waveform.
    Args:
        input_features (`torch.FloatTensor`):
            Tensor containing the log-mel spectrograms. Can be batched and of shape `(batch_size, sequence_length,
            config.num_mel_channels)`, or un-batched and of shape `(sequence_length, config.num_mel_channels)`.
        noise_sequence (`torch.FloatTensor`, *optional*):
            Tensor containing a noise sequence of standard Gaussian noise. Can be batched and of shape `(batch_size,
            sequence_length, config.model_in_channels)`, or un-batched and of shape (sequence_length,
            config.model_in_channels)`. If not supplied, will be randomly generated.
        padding_mask (`torch.BoolTensor`, *optional*):
            Mask indicating which parts of each sequence are padded. Mask values are selected in `[0, 1]`:
            - 1 for tokens that are *not masked*
            - 0 for tokens that are *masked*
            The mask can be batched and of shape `(batch_size, sequence_length)` or un-batched and of shape
            `(sequence_length,)`.
        generator (`torch.Generator`, *optional*):
            A [torch generator](https://pytorch.org/docs/stable/generated/torch.Generator.html) to make generation
            deterministic.
        return_dict:
            Whether to return a [`~utils.ModelOutput`] subclass instead of a plain tuple.
"""
@add_start_docstrings("UnivNet GAN vocoder.", UNIVNET_START_DOCSTRING)
class UnivNetModel(PreTrainedModel):
    config_class = UnivNetConfig
    main_input_name = "input_features"
    def __init__(self, config: UnivNetConfig):
        super().__init__(config)
        self.num_kernels = len(config.resblock_kernel_sizes)
        self.leaky_relu_slope = config.leaky_relu_slope
        self.conv_pre = nn.Conv1d(config.model_in_channels, config.model_hidden_channels, kernel_size=7, stride=1, padding=3, padding_mode="reflect")
        num_layers = len(config.resblock_stride_sizes)
        hop_length = 1
        hop_lengths = []
        for stride in config.resblock_stride_sizes:
            hop_length = hop_length * stride
            hop_lengths.append(hop_length)
        self.resblocks = nn.ModuleList([UnivNetLvcBlock(config, layer_id=i, lvc_hop_size=hop_lengths[i]) for i in range(num_layers)])
        self.conv_post = nn.Conv1d(config.model_hidden_channels, 1, 7, padding=3, padding_mode="reflect")
        self.post_init()
    @add_start_docstrings_to_model_forward(UNIVNET_INPUTS_DOCSTRING)
    def forward(self, input_features: torch.FloatTensor, noise_sequence: Optional[torch.FloatTensor] = None, padding_mask: Optional[torch.FloatTensor] = None,
    generator: Optional[torch.Generator] = None, return_dict: Optional[bool] = None) -> Union[Tuple[torch.FloatTensor], UnivNetModelOutput]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        spectrogram_batched = input_features.dim() == 3
        if not spectrogram_batched: input_features = input_features.unsqueeze(0)
        spectrogram_batch_size, spectrogram_length, _ = input_features.shape
        if noise_sequence is not None:
            noise_sequence_batched = noise_sequence.dim() == 3
            if not noise_sequence_batched: noise_sequence = noise_sequence.unsqueeze(0)
        else:
            noise_sequence_shape = (spectrogram_batch_size, spectrogram_length, self.config.model_in_channels)
            noise_sequence = torch.randn(noise_sequence_shape, generator=generator, dtype=input_features.dtype, device=input_features.device)
        noise_sequence_batch_size = noise_sequence.shape[0]
        if spectrogram_batch_size > 1 and noise_sequence_batch_size == 1: noise_sequence = noise_sequence.repeat(spectrogram_batch_size, 1, 1)
        elif noise_sequence_batch_size > 1 and spectrogram_batch_size == 1: input_features = input_features.repeat(noise_sequence_batch_size, 1, 1)
        if noise_sequence_batch_size != spectrogram_batch_size: raise ValueError(f"The batch size of `noise_sequence` is {noise_sequence_batch_size} and the batch size of `input_features` is {spectrogram_batch_size}, but the two are expected to be equal.")
        if padding_mask is not None:
            if padding_mask.dim() == 1: padding_mask = padding_mask.unsqueeze(0)
            padding_mask_batch_size = padding_mask.shape[0]
            if padding_mask_batch_size != spectrogram_batch_size: raise ValueError(f"The batch size of `padding_mask` is {padding_mask_batch_size} and the batch size of `input_features` is {spectrogram_batch_size}, but the two are expected to be equal.")
        hidden_states = noise_sequence.transpose(2, 1)
        input_features = input_features.transpose(2, 1)
        hidden_states = self.conv_pre(hidden_states)
        for resblock in self.resblocks: hidden_states = resblock(hidden_states, input_features)
        hidden_states = nn.functional.leaky_relu(hidden_states, self.leaky_relu_slope)
        hidden_states = self.conv_post(hidden_states)
        hidden_states = torch.tanh(hidden_states)
        waveform = hidden_states.squeeze(1)
        waveform_lengths = None
        if padding_mask is not None: waveform_lengths = torch.sum(padding_mask, dim=1)
        if not return_dict:
            outputs = (waveform, waveform_lengths)
            return outputs
        return UnivNetModelOutput(waveforms=waveform, waveform_lengths=waveform_lengths)
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv1d, nn.ConvTranspose1d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None: module.bias.data.zero_()
    def apply_weight_norm(self):
        weight_norm = nn.utils.weight_norm
        if hasattr(nn.utils.parametrizations, "weight_norm"): weight_norm = nn.utils.parametrizations.weight_norm
        weight_norm(self.conv_pre)
        for layer in self.resblocks: layer.apply_weight_norm()
        weight_norm(self.conv_post)
    def remove_weight_norm(self):
        nn.utils.remove_weight_norm(self.conv_pre)
        for layer in self.resblocks: layer.remove_weight_norm()
        nn.utils.remove_weight_norm(self.conv_post)
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
