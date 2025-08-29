"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
ADDITIONAL_DIACRITICS = {'œ': 'oe', 'Œ': 'OE', 'ø': 'o', 'Ø': 'O', 'æ': 'ae', 'Æ': 'AE', 'ß': 'ss', 'ẞ': 'SS', 'đ': 'd', 'Đ': 'D', 'ð': 'd', 'Ð': 'D', 'þ': 'th', 'Þ': 'th', 'ł': 'l', 'Ł': 'L'}
ATTRIBUTE_MAP = {'num_key_value_heads': 'encoder_attention_heads', 'num_attention_heads': 'encoder_attention_heads', 'hidden_size': 'd_model'}
FLAX_SAPI_AUDIO_AUDIO_CLASSIFICATION_DOCSTRING = r"""
    Returns:
    Transcription example:
    ```python
    >>> import jax.numpy as jnp
    >>> from sapiens_transformers import AutoFeatureExtractor, FlaxSAPIAudioForAudioClassification
    >>> from datasets import load_dataset
    >>> feature_extractor = AutoFeatureExtractor.from_pretrained("sanchit-gandhi/sapi_audio-medium-fleurs-lang-id")
    >>> model = FlaxSAPIAudioForAudioClassification.from_pretrained(
    ...     "sanchit-gandhi/sapi_audio-medium-fleurs-lang-id", from_pt=True
    ... )
    >>> ds = load_dataset("google/fleurs", "all", split="validation", streaming=True, trust_remote_code=True)
    >>> sample = next(iter(ds))
    >>> inputs = feature_extractor(
    ...     sample["audio"]["array"], sampling_rate=sample["audio"]["sampling_rate"], return_tensors="np"
    ... )
    >>> input_features = inputs.input_features
    >>> logits = model(input_features).logits
    >>> predicted_class_ids = jnp.argmax(logits).item()
    >>> predicted_label = model.config.id2label[predicted_class_ids]
    >>> predicted_label
    'af_za'
    ```
"""
FLAX_SAPI_AUDIO_CONDITIONAL_GENERATION_DOCSTRING = r"""
    Returns:
    Transcription example:
    ```python
    >>> from sapiens_transformers import SAPIAudioProcessor, FlaxSAPIAudioForConditionalGeneration
    >>> from datasets import load_dataset
    >>> processor = SAPIAudioProcessor.from_pretrained("sapiens/sapi_audio.en")
    >>> model = FlaxSAPIAudioForConditionalGeneration.from_pretrained("sapiens/sapi_audio.en", from_pt=True)
    >>> ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
    >>> inputs = processor(ds[0]["audio"]["array"], return_tensors="np")
    >>> input_features = inputs.input_features
    >>> generated_ids = model.generate(input_ids=input_features)
    >>> transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    >>> transcription
    ' Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.'
    ```
"""
LANGUAGES = {'en': 'english', 'zh': 'chinese', 'de': 'german', 'es': 'spanish', 'ru': 'russian', 'ko': 'korean', 'fr': 'french', 'ja': 'japanese', 'pt': 'portuguese',
'tr': 'turkish', 'pl': 'polish', 'ca': 'catalan', 'nl': 'dutch', 'ar': 'arabic', 'sv': 'swedish', 'it': 'italian', 'id': 'indonesian', 'hi': 'hindi', 'fi': 'finnish',
'vi': 'vietnamese', 'he': 'hebrew', 'uk': 'ukrainian', 'el': 'greek', 'ms': 'malay', 'cs': 'czech', 'ro': 'romanian', 'da': 'danish', 'hu': 'hungarian', 'ta': 'tamil',
'no': 'norwegian', 'th': 'thai', 'ur': 'urdu', 'hr': 'croatian', 'bg': 'bulgarian', 'lt': 'lithuanian', 'la': 'latin', 'mi': 'maori', 'ml': 'malayalam', 'cy': 'welsh',
'sk': 'slovak', 'te': 'telugu', 'fa': 'persian', 'lv': 'latvian', 'bn': 'bengali', 'sr': 'serbian', 'az': 'azerbaijani', 'sl': 'slovenian', 'kn': 'kannada', 'et': 'estonian',
'mk': 'macedonian', 'br': 'breton', 'eu': 'basque', 'is': 'icelandic', 'hy': 'armenian', 'ne': 'nepali', 'mn': 'mongolian', 'bs': 'bosnian', 'kk': 'kazakh', 'sq': 'albanian',
'sw': 'swahili', 'gl': 'galician', 'mr': 'marathi', 'pa': 'punjabi', 'si': 'sinhala', 'km': 'khmer', 'sn': 'shona', 'yo': 'yoruba', 'so': 'somali', 'af': 'afrikaans',
'oc': 'occitan', 'ka': 'georgian', 'be': 'belarusian', 'tg': 'tajik', 'sd': 'sindhi', 'gu': 'gujarati', 'am': 'amharic', 'yi': 'yiddish', 'lo': 'lao', 'uz': 'uzbek',
'fo': 'faroese', 'ht': 'haitian creole', 'ps': 'pashto', 'tk': 'turkmen', 'nn': 'nynorsk', 'mt': 'maltese', 'sa': 'sanskrit', 'lb': 'luxembourgish', 'my': 'myanmar',
'bo': 'tibetan', 'tl': 'tagalog', 'mg': 'malagasy', 'as': 'assamese', 'tt': 'tatar', 'haw': 'hawaiian', 'ln': 'lingala', 'ha': 'hausa', 'ba': 'bashkir',
'jw': 'javanese', 'su': 'sundanese', 'yue': 'cantonese'}
MULTIPLIERS = {'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000, 'trillion': 1000000000000, 'quadrillion': 1000000000000000, 'quintillion': 1000000000000000000,
'sextillion': 1000000000000000000000, 'septillion': 1000000000000000000000000, 'octillion': 1000000000000000000000000000,
'nonillion': 1000000000000000000000000000000, 'decillion': 1000000000000000000000000000000000}
NON_SPEECH_TOKENS = [1, 2, 7, 8, 9, 10, 14, 25, 26, 27, 28, 29, 31, 58, 59, 60, 61, 62, 63, 90, 91, 92, 93, 357, 366, 438, 532, 685, 705, 796, 930, 1058, 1220, 1267, 1279, 1303, 1343, 1377,
1391, 1635, 1782, 1875, 2162, 2361, 2488, 3467, 4008, 4211, 4600, 4808, 5299, 5855, 6329, 7203, 9609, 9959, 10563, 10786, 11420, 11709, 11907, 13163, 13697, 13700, 14808, 15306, 16410, 16791,
17992, 19203, 19510, 20724, 22305, 22935, 27007, 30109, 30420, 33409, 34949, 40283, 40493, 40549, 47282, 49146, 50257, 50359, 50360, 50361]
NON_SPEECH_TOKENS_MULTI = [1, 2, 7, 8, 9, 10, 14, 25, 26, 27, 28, 29, 31, 58, 59, 60, 61, 62, 63, 90, 91, 92, 93, 359, 503, 522, 542, 873, 893, 902, 918, 922, 931, 1350, 1853, 1982, 2460, 2627,
3246, 3253, 3268, 3536, 3846, 3961, 4183, 4667, 6585, 6647, 7273, 9061, 9383, 10428, 10929, 11938, 12033, 12331, 12562, 13793, 14157, 14635, 15265, 15618, 16553, 16604, 18362, 18956, 20075, 21675,
22520, 26130, 26161, 26435, 28279, 29464, 31650, 32302, 32470, 36865, 42863, 47425, 49870, 50254, 50258, 50360, 50361, 50362]
TO_LANGUAGE_CODE = {**{language: code for code, language in LANGUAGES.items()}, "burmese": "my", "valencian": "ca", "flemish": "nl", "haitian": "ht", "letzeburgesch": "lb",
"pushto": "ps", "panjabi": "pa", "moldavian": "ro", "moldovan": "ro", "sinhalese": "si", "castilian": "es", "mandarin": "zh"}
REPLACERS = {"\\bwon't\\b": 'will not', "\\bcan't\\b": 'can not', "\\blet's\\b": 'let us', "\\bain't\\b": 'aint', "\\by'all\\b": 'you all', '\\bwanna\\b': 'want to',
'\\bgotta\\b': 'got to', '\\bgonna\\b': 'going to', "\\bi'ma\\b": 'i am going to', '\\bimma\\b': 'i am going to', '\\bwoulda\\b': 'would have', '\\bcoulda\\b': 'could have',
'\\bshoulda\\b': 'should have', "\\bma'am\\b": 'madam', '\\bmr\\b': 'mister ', '\\bmrs\\b': 'missus ', '\\bst\\b': 'saint ', '\\bdr\\b': 'doctor ', '\\bprof\\b': 'professor ',
'\\bcapt\\b': 'captain ', '\\bgov\\b': 'governor ', '\\bald\\b': 'alderman ', '\\bgen\\b': 'general ', '\\bsen\\b': 'senator ', '\\brep\\b': 'representative ',
'\\bpres\\b': 'president ', '\\brev\\b': 'reverend ', '\\bhon\\b': 'honorable ', '\\basst\\b': 'assistant ', '\\bassoc\\b': 'associate ', '\\blt\\b': 'lieutenant ',
'\\bcol\\b': 'colonel ', '\\bjr\\b': 'junior ', '\\bsr\\b': 'senior ', '\\besq\\b': 'esquire ', "'d been\\b": ' had been', "'s been\\b": ' has been', "'d gone\\b": ' had gone',
"'s gone\\b": ' has gone', "'d done\\b": ' had done', "'s got\\b": ' has got', "n't\\b": ' not', "'re\\b": ' are', "'s\\b": ' is', "'d\\b": ' would',
"'ll\\b": ' will', "'t\\b": ' not', "'ve\\b": ' have', "'m\\b": ' am'}
VOCAB_FILES_NAMES = {'vocab_file': 'vocab.json', 'tokenizer_file': 'tokenizer.json', 'merges_file': 'merges.txt', 'normalizer_file': 'normalizer.json'}
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
