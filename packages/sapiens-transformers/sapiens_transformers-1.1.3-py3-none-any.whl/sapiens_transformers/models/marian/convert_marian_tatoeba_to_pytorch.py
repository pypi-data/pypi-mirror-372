"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
import argparse
import datetime
import json
import os
import re
from pathlib import Path
from typing import Tuple
import yaml
from tqdm import tqdm
from sapiens_transformers.models.marian.convert_marian_to_pytorch import (FRONT_MATTER_TEMPLATE, convert, convert_opus_name_to_hf_name, download_and_unzip, get_system_metadata)
DEFAULT_REPO = "Tatoeba-Challenge"
DEFAULT_MODEL_DIR = os.path.join(DEFAULT_REPO, "models")
ISO_URL = "https://cdn-datasets.huggingface.co/language_codes/iso-639-3.csv"
ISO_PATH = "lang_code_data/iso-639-3.csv"
LANG_CODE_PATH = "lang_code_data/language-codes-3b2.csv"
TATOEBA_MODELS_URL = "https://object.pouta.csc.fi/Tatoeba-MT-models"
class TatoebaConverter:
    def __init__(self, save_dir="marian_converted"):
        assert Path(DEFAULT_REPO).exists(), "need git clone git@github.com:Helsinki-NLP/Tatoeba-Challenge.git"
        self.download_lang_info()
        self.model_results = json.load(open("Tatoeba-Challenge/models/released-model-results.json"))
        self.alpha3_to_alpha2 = {}
        for line in open(ISO_PATH):
            parts = line.split("\t")
            if len(parts[0]) == 3 and len(parts[3]) == 2: self.alpha3_to_alpha2[parts[0]] = parts[3]
        for line in LANG_CODE_PATH:
            parts = line.split(",")
            if len(parts[0]) == 3 and len(parts[1]) == 2: self.alpha3_to_alpha2[parts[0]] = parts[1]
        self.model_card_dir = Path(save_dir)
        self.tag2name = {}
        for key, value in GROUP_MEMBERS.items(): self.tag2name[key] = value[0]
    def convert_models(self, tatoeba_ids, dry_run=False):
        models_to_convert = [self.parse_metadata(x) for x in tatoeba_ids]
        save_dir = Path("marian_ckpt")
        dest_dir = Path(self.model_card_dir)
        dest_dir.mkdir(exist_ok=True)
        for model in tqdm(models_to_convert):
            if "SentencePiece" not in model["pre-processing"]:
                print(f"Skipping {model['release']} because it doesn't appear to use SentencePiece")
                continue
            if not os.path.exists(save_dir / model["_name"]): download_and_unzip(f"{TATOEBA_MODELS_URL}/{model['release']}", save_dir / model["_name"])
            opus_language_groups_to_hf = convert_opus_name_to_hf_name
            pair_name = opus_language_groups_to_hf(model["_name"])
            convert(save_dir / model["_name"], dest_dir / f"opus-mt-{pair_name}")
            self.write_model_card(model, dry_run=dry_run)
    def expand_group_to_two_letter_codes(self, grp_name): return [self.alpha3_to_alpha2.get(x, x) for x in GROUP_MEMBERS[grp_name][1]]
    def is_group(self, code, name): return "languages" in name or len(GROUP_MEMBERS.get(code, [])) > 1
    def get_tags(self, code, name):
        if len(code) == 2:
            assert "languages" not in name, f"{code}: {name}"
            return [code]
        elif self.is_group(code, name):
            group = self.expand_group_to_two_letter_codes(code)
            group.append(code)
            return group
        else:
            print(f"Three letter monolingual code: {code}")
            return [code]
    def resolve_lang_code(self, src, tgt) -> Tuple[str, str]:
        src_tags = self.get_tags(src, self.tag2name[src])
        tgt_tags = self.get_tags(tgt, self.tag2name[tgt])
        return src_tags, tgt_tags
    @staticmethod
    def model_type_info_from_model_name(name):
        info = {"_has_backtranslated_data": False}
        if "1m" in name: info["_data_per_pair"] = str(1e6)
        if "2m" in name: info["_data_per_pair"] = str(2e6)
        if "4m" in name: info["_data_per_pair"] = str(4e6)
        if "+bt" in name: info["_has_backtranslated_data"] = True
        if "tuned4" in name: info["_tuned"] = re.search(r"tuned4[^-]+", name).group()
        return info
    def write_model_card(self, model_dict, dry_run=False) -> str:
        model_dir_url = f"{TATOEBA_MODELS_URL}/{model_dict['release']}"
        long_pair = model_dict["_name"].split("-")
        assert len(long_pair) == 2, f"got a translation pair {model_dict['_name']} that doesn't appear to be a pair"
        short_src = self.alpha3_to_alpha2.get(long_pair[0], long_pair[0])
        short_tgt = self.alpha3_to_alpha2.get(long_pair[1], long_pair[1])
        model_dict["_hf_model_id"] = f"opus-mt-{short_src}-{short_tgt}"
        a3_src, a3_tgt = model_dict["_name"].split("-")
        resolved_src_tags, resolved_tgt_tags = self.resolve_lang_code(a3_src, a3_tgt)
        a2_src_tags, a2_tgt_tags = [], []
        for tag in resolved_src_tags:
            if tag not in self.alpha3_to_alpha2: a2_src_tags.append(tag)
        for tag in resolved_tgt_tags:
            if tag not in self.alpha3_to_alpha2: a2_tgt_tags.append(tag)
        lang_tags = dedup(a2_src_tags + a2_tgt_tags)
        src_multilingual, tgt_multilingual = (len(a2_src_tags) > 1), (len(a2_tgt_tags) > 1)
        s, t = ",".join(a2_src_tags), ",".join(a2_tgt_tags)
        metadata = {"hf_name": model_dict["_name"], "source_languages": s, "target_languages": t, "opus_readme_url": f"{model_dir_url}/README.md",
        "original_repo": "Tatoeba-Challenge", "tags": ["translation"], "languages": lang_tags}
        lang_tags = l2front_matter(lang_tags)
        metadata["src_constituents"] = list(GROUP_MEMBERS[a3_src][1])
        metadata["tgt_constituents"] = list(GROUP_MEMBERS[a3_tgt][1])
        metadata["src_multilingual"] = src_multilingual
        metadata["tgt_multilingual"] = tgt_multilingual
        backtranslated_data = ""
        if model_dict["_has_backtranslated_data"]: backtranslated_data = " with backtranslations"
        multilingual_data = ""
        if "_data_per_pair" in model_dict: multilingual_data = f"* data per pair in multilingual model: {model_dict['_data_per_pair']}\n"
        tuned = ""
        if "_tuned" in model_dict: tuned = f"* multilingual model tuned for: {model_dict['_tuned']}\n"
        model_base_filename = model_dict["release"].split("/")[-1]
        download = f"* download original weights: [{model_base_filename}]({model_dir_url}/{model_dict['release']})\n"
        langtoken = ""
        if tgt_multilingual: langtoken = ("* a sentence-initial language token is required in the form of >>id<<(id = valid, usually three-letter target language ID)\n")
        metadata.update(get_system_metadata(DEFAULT_REPO))
        scorestable = ""
        for k, v in model_dict.items():
            if "scores" in k:
                this_score_table = f"* {k}\n|Test set|score|\n|---|---|\n"
                pairs = sorted(v.items(), key=lambda x: x[1], reverse=True)
                for pair in pairs: this_score_table += f"|{pair[0]}|{pair[1]}|\n"
                scorestable += this_score_table
        datainfo = ""
        if "training-data" in model_dict:
            datainfo += "* Training data: \n"
            for k, v in model_dict["training-data"].items(): datainfo += f"  * {str(k)}: {str(v)}\n"
        if "validation-data" in model_dict:
            datainfo += "* Validation data: \n"
            for k, v in model_dict["validation-data"].items(): datainfo += f"  * {str(k)}: {str(v)}\n"
        if "test-data" in model_dict:
            datainfo += "* Test data: \n"
            for k, v in model_dict["test-data"].items(): datainfo += f"  * {str(k)}: {str(v)}\n"
        testsetfilename = model_dict["release"].replace(".zip", ".test.txt")
        testscoresfilename = model_dict["release"].replace(".zip", ".eval.txt")
        testset = f"* test set translations file: [test.txt]({model_dir_url}/{testsetfilename})\n"
        testscores = f"* test set scores file: [eval.txt]({model_dir_url}/{testscoresfilename})\n"
        readme_url = f"{TATOEBA_MODELS_URL}/{model_dict['_name']}/README.md"
        extra_markdown = f"""
* source language name: {self.tag2name[a3_src]}
* target language name: {self.tag2name[a3_tgt]}
* OPUS readme: [README.md]({readme_url})
"""
        content = (f"""
* model: {model_dict['modeltype']}
* source language code{src_multilingual*'s'}: {', '.join(a2_src_tags)}
* target language code{tgt_multilingual*'s'}: {', '.join(a2_tgt_tags)}
* dataset: opus {backtranslated_data}
* release date: {model_dict['release-date']}
* pre-processing: {model_dict['pre-processing']}
""" + multilingual_data + tuned + download + langtoken + datainfo + testset + testscores + scorestable)
        content = FRONT_MATTER_TEMPLATE.format(lang_tags) + extra_markdown + content
        items = "\n".join([f"* {k}: {v}" for k, v in metadata.items()])
        sec3 = "\n### System Info: \n" + items
        content += sec3
        if dry_run:
            print("CONTENT:")
            print(content)
            print("METADATA:")
            print(metadata)
            return
        sub_dir = self.model_card_dir / model_dict["_hf_model_id"]
        sub_dir.mkdir(exist_ok=True)
        dest = sub_dir / "README.md"
        dest.open("w").write(content)
        for k, v in metadata.items():
            if isinstance(v, datetime.date): metadata[k] = datetime.datetime.strftime(v, "%Y-%m-%d")
        with open(sub_dir / "metadata.json", "w", encoding="utf-8") as writeobj: json.dump(metadata, writeobj)
    def download_lang_info(self):
        global LANG_CODE_PATH
        Path(LANG_CODE_PATH).parent.mkdir(exist_ok=True)
        import wget
        from huggingface_hub import hf_hub_download
        if not os.path.exists(ISO_PATH): wget.download(ISO_URL, ISO_PATH)
        if not os.path.exists(LANG_CODE_PATH): LANG_CODE_PATH = hf_hub_download(repo_id="huggingface/language_codes_marianMT", filename="language-codes-3b2.csv", repo_type="dataset")
    def parse_metadata(self, model_name, repo_path=DEFAULT_MODEL_DIR, method="best"):
        p = Path(repo_path) / model_name
        def url_to_name(url): return url.split("/")[-1].split(".")[0]
        if model_name not in self.model_results: method = "newest"
        if method == "best":
            results = [url_to_name(model["download"]) for model in self.model_results[model_name]]
            ymls = [f for f in os.listdir(p) if f.endswith(".yml") and f[:-4] in results]
            ymls.sort(key=lambda x: results.index(x[:-4]))
            metadata = yaml.safe_load(open(p / ymls[0]))
            metadata.update(self.model_type_info_from_model_name(ymls[0][:-4]))
        elif method == "newest":
            ymls = [f for f in os.listdir(p) if f.endswith(".yml")]
            ymls.sort(key=lambda x: datetime.datetime.strptime(re.search(r"\d\d\d\d-\d\d?-\d\d?", x).group(), "%Y-%m-%d"))
            metadata = yaml.safe_load(open(p / ymls[-1]))
            metadata.update(self.model_type_info_from_model_name(ymls[-1][:-4]))
        else: raise NotImplementedError(f"Don't know argument method='{method}' to parse_metadata()")
        metadata["_name"] = model_name
        return metadata
GROUP_MEMBERS = {"aav": ("Austro-Asiatic languages", {"hoc", "hoc_Latn", "kha", "khm", "khm_Latn", "mnw", "vie", "vie_Hani"}),
"afa": ("Afro-Asiatic languages", {'rif_Latn', 'tir', 'ary', 'arz', 'shy_Latn', 'apc', 'kab', 'amh', 'som', 'mlt', 'hau_Latn', 'arq', 'thv', 'afb', 'ara', 'heb', 'acm'}),
"afr": ("Afrikaans", {"afr"}), "alv": ("Atlantic-Congo languages", {'fuc', 'fuv', 'umb', 'zul', 'lug', 'ibo', 'sag', 'yor', 'toi_Latn', 'kin', 'ewe', 'nya', 'tso', 'sna', 'wol', 'xho', 'lin', 'swh', 'run'}), "ara": ("Arabic", {"afb", "apc", "apc_Latn", "ara", "ara_Latn", "arq", "arq_Latn", "arz"}),
"art": ("Artificial languages", {'vol_Latn', 'jbo', 'afh_Latn', 'ido_Latn', 'sjn_Latn', 'dws_Latn', 'epo', 'jbo_Latn', 'qya', 'ido', 'jbo_Cyrl', 'tzl', 'lfn_Latn', 'qya_Latn', 'ile_Latn', 'ina_Latn', 'ldn_Latn', 'tlh_Latn', 'avk_Latn', 'nov_Latn', 'lfn_Cyrl', 'tzl_Latn'}),
"aze": ("Azerbaijani", {"aze_Latn"}), "bat": ("Baltic languages", {"lit", "lav", "prg_Latn", "ltg", "sgs"}), "bel": ("Belarusian", {"bel", "bel_Latn"}),
"ben": ("Bengali", {"ben"}), "bnt": ("Bantu languages", {"kin", "lin", "lug", "nya", "run", "sna", "swh", "toi_Latn", "tso", "umb", "xho", "zul"}),
"bul": ("Bulgarian", {"bul", "bul_Latn"}), "cat": ("Catalan", {"cat"}), "cau": ("Caucasian languages", {"abk", "kat", "che", "ady"}),
"ccs": ("South Caucasian languages", {"kat"}), "ceb": ("Cebuano", {"ceb"}), "cel": ("Celtic languages", {"gla", "gle", "bre", "cor", "glv", "cym"}),
"ces": ("Czech", {"ces"}), "cpf": ("Creoles and pidgins, French‑based", {"gcf_Latn", "hat", "mfe"}), "cpp": ("Creoles and pidgins, Portuguese-based", {"zsm_Latn", "ind", "pap", "min", "tmw_Latn", "max_Latn", "zlm_Latn"}),
"cus": ("Cushitic languages", {"som"}), "dan": ("Danish", {"dan"}), "deu": ("German", {"deu"}), "dra": ("Dravidian languages", {"tam", "kan", "mal", "tel"}),
"ell": ("Modern Greek (1453-)", {"ell"}), "eng": ("English", {"eng"}), "epo": ("Esperanto", {"epo"}), "est": ("Estonian", {"est"}), "euq": ("Basque (family)", {"eus"}), "eus": ("Basque", {"eus"}), "fin": ("Finnish", {"fin"}),
"fiu": ("Finno-Ugrian languages", {'fin', 'mdf', 'vep', 'krl', 'udm', 'fkv_Latn', 'sme', 'est', 'hun', 'kpv', 'mhr', 'myv', 'vro', 'izh', 'sma', 'liv_Latn'}),
"fra": ("French", {"fra"}), "gem": ("Germanic languages", {'yid', 'isl', 'fry', 'nds', 'afr', 'non_Latn', 'swg', 'nno', 'ang_Latn', 'swe', 'fao', 'ksh', 'enm_Latn', 'stq', 'sco', 'gsw', 'nob', 'eng', 'pdc', 'nob_Hebr', 'gos', 'frr', 'deu', 'nld', 'dan', 'ltz', 'got_Goth'}),
"gle": ("Irish", {"gle"}), "glg": ("Galician", {"glg"}), "gmq": ("North Germanic languages", {"dan", "nob", "nob_Hebr", "swe", "isl", "nno", "non_Latn", "fao"}),
"gmw": ("West Germanic languages", {'gsw', 'yid', 'ang_Latn', 'fry', 'nds', 'nld', 'eng', 'afr', 'frr', 'pdc', 'ltz', 'stq', 'ksh', 'swg', 'enm_Latn', 'gos', 'sco', 'deu'}),
"grk": ("Greek languages", {"grc_Grek", "ell"}), "hbs": ("Serbo-Croatian", {"hrv", "srp_Cyrl", "bos_Latn", "srp_Latn"}), "heb": ("Hebrew", {"heb"}),
"hin": ("Hindi", {"hin"}), "hun": ("Hungarian", {"hun"}), "hye": ("Armenian", {"hye", "hye_Latn"}), "iir": ("Indo-Iranian languages", {'npi', 'guj', 'hif_Latn', 'hin', 'kur_Arab', 'tly_Latn', 'pes_Thaa', 'rom', 'sin', 'mai', 'snd_Arab', 'jdt_Cyrl', 'awa', 'mar', 'pes', 'bho', 'pes_Latn', 'zza', 'pnb', 'oss', 'ori', 'asm', 'pus', 'urd', 'pan_Guru', 'kur_Latn', 'gom', 'ben', 'san_Deva', 'tgk_Cyrl'}),
"ilo": ("Iloko", {"ilo"}), "inc": ("Indic languages", {'npi', 'guj', 'hif_Latn', 'hin', 'rom', 'sin', 'mai', 'snd_Arab', 'awa', 'mar', 'bho', 'pnb', 'ori', 'asm', 'urd', 'pan_Guru', 'gom', 'ben', 'san_Deva'}),
"ine": ("Indo-European languages", {'spa', 'srp_Cyrl', 'pcd', 'pms', 'prg_Latn', 'rom', 'swe', 'egl', 'gla', 'fao', 'snd_Arab', 'max_Latn', 'awa', 'hye_Latn', 'cat', 'hye', 'cym', 'srp_Latn', 'cor', 'bho', 'lad_Latn', 'pdc', 'ori', 'pus', 'lmo', 'urd', 'ltg', 'dan', 'dsb', 'kur_Latn', 'ltz', 'rue',
'pap', 'ita', 'yid', 'hat', 'isl', 'guj', 'pol', 'glv', 'zsm_Latn', 'hin', 'glg', 'arg', 'swg', 'ang_Latn', 'rus', 'bjn', 'ksh', 'hsb', 'mar', 'cos', 'hrv', 'sgs', 'ron', 'nob', 'zza', 'pes_Latn', 'eng', 'lld_Latn', 'gos', 'bul', 'tmw_Latn', 'frr', 'bos_Latn', 'bre', 'zlm_Latn', 'bul_Latn', 'tgk_Cyrl', 'sqi',
'ind', 'ces', 'got_Goth', 'hif_Latn', 'rus_Latn', 'bel', 'wln', 'kur_Arab', 'tly_Latn', 'pes_Thaa', 'non_Latn', 'frm_Latn', 'gle', 'gcf_Latn', 'mai', 'oci', 'stq', 'fra', 'vec', 'pes', 'pnb', 'nob_Hebr', 'oss', 'mfe', 'asm', 'deu', 'por', 'lat_Latn', 'min', 'csb_Latn', 'san_Deva', 'ext', 'lat_Grek', 'bel_Latn',
'grc_Grek', 'roh', 'npi', 'fry', 'nds', 'afr', 'scn', 'ast', 'nno', 'sin', 'mkd', 'jdt_Cyrl', 'enm_Latn', 'sco', 'aln', 'gsw', 'afr_Arab', 'lav', 'srd', 'slv', 'lij', 'ell', 'nld', 'pan_Guru', 'gom', 'ben', 'lad', 'lit', 'orv_Cyrl', 'ukr', 'mwl'}),
"isl": ("Icelandic", {"isl"}), "ita": ("Italian", {"ita"}), "itc": ("Italic languages", {'hat', 'spa', 'wln', 'zsm_Latn', 'pcd', 'pms', 'glg', 'arg', 'scn', 'frm_Latn', 'ast', 'gcf_Latn', 'egl', 'max_Latn', 'bjn', 'cat', 'ind', 'oci', 'cos', 'fra', 'ron', 'vec', 'lad_Latn', 'lld_Latn', 'tmw_Latn', 'srd', 'mfe', 'lij', 'lmo', 'por', 'lat_Latn', 'min', 'lad', 'zlm_Latn', 'ext', 'lat_Grek', 'pap', 'mwl', 'ita', 'roh'}),
"jpn": ("Japanese", {"jpn", "jpn_Bopo", "jpn_Hang", "jpn_Hani", "jpn_Hira", "jpn_Kana", "jpn_Latn", "jpn_Yiii"}), "jpx": ("Japanese (family)", {"jpn"}), "kat": ("Georgian", {"kat"}),
"kor": ("Korean", {"kor_Hani", "kor_Hang", "kor_Latn", "kor"}), "lav": ("Latvian", {"lav"}), "lit": ("Lithuanian", {"lit"}), "mkd": ("Macedonian", {"mkd"}),
"mkh": ("Mon-Khmer languages", {"vie_Hani", "mnw", "vie", "kha", "khm_Latn", "khm"}), "msa": ("Malay (macrolanguage)", {"zsm_Latn", "ind", "max_Latn", "zlm_Latn", "min"}),
"mul": ("Multiple languages", {'mon', 'tuk_Latn', 'prg_Latn', 'mal', 'egl', 'gla', 'max_Latn', 'cor', 'lad_Latn', 'qya_Latn', 'liv_Latn', 'uzb_Latn', 'yue_Hans', 'lmo', 'dan', 'dsb', 'kur_Latn', 'lin', 'tzl_Latn', 'myv', 'fin', 'khm', 'jbo', 'hin', 'arg', 'vro', 'mww', 'ron', 'nob', 'lld_Latn', 'gos', 'shs_Latn', 'zlm_Latn', 'bul_Latn', 'ind', 'frm_Latn',
'hau_Latn', 'mai', 'gil', 'sah', 'acm', 'pes', 'pnb', 'nya', 'zho_Hant', 'san_Deva', 'hun', 'kat', 'cjy_Hant', 'nog', 'rif_Latn', 'fry', 'moh', 'afr', 'ast', 'lzh_Hans', 'amh', 'mlt', 'kal', 'enm_Latn', 'ceb', 'gsw', 'tzl', 'fij', 'mwl', 'pms', 'ota_Latn', 'rom', 'fao', 'ton', 'awa', 'epo', 'qya', 'cat', 'kek_Latn', 'ewe', 'kan', 'zho_Hans', 'ina_Latn',
'sme', 'bod', 'tlh_Latn', 'ori', 'tso', 'pus', 'yid', 'guj', 'lzh', 'glv', 'glg', 'tpw_Latn', 'ady', 'ang_Latn', 'akl_Latn', 'ibo', 'rap', 'udm', 'xal', 'toi_Latn', 'hil', 'hsb', 'kha', 'niu', 'jpn', 'crh', 'quc', 'bak', 'mic', 'mhr', 'tmw_Latn', 'wuu', 'frr', 'sna', 'tgk_Cyrl', 'sqi', 'lkt', 'est', 'non_Latn', 'cha', 'sma', 'che', 'dws_Latn', 'uig_Cyrl',
'tet', 'cjy_Hans', 'mfe', 'chv', 'csb_Latn', 'mri', 'roh', 'npi', 'lug', 'nds', 'cmn_Hant', 'nav', 'mkd', 'nan', 'sco', 'aln', 'jbo_Cyrl', 'kjh', 'tvl', 'tha', 'slv', 'pan_Guru', 'gom', 'hoc_Latn', 'lfn_Cyrl', 'tuk', 'orv_Cyrl', 'uig_Arab', 'pol', 'kum', 'fkv_Latn', 'kaz_Latn', 'haw', 'apc', 'grn', 'mad', 'ppl_Latn', 'kir_Cyrl', 'tat_Latn', 'ido', 'sag',
'srp_Latn', 'yue', 'kaz_Cyrl', 'bho', 'ota_Arab', 'abk', 'tir', 'ltg', 'avk_Latn', 'rue', 'pap', 'ita', 'hat', 'jav', 'yue_Hant', 'pag', 'hrv', 'tah', 'brx', 'iba', 'zza', 'pes_Latn', 'kpv', 'bos_Latn', 'bam_Latn', 'swh', 'mnw', 'ary', 'got_Goth', 'run', 'hif_Latn', 'wln', 'kur_Arab', 'pes_Thaa', 'gle', 'khm_Latn', 'smo', 'vie', 'sjn_Latn', 'tyv', 'oci',
'oss', 'mya', 'por', 'lat_Latn', 'ext', 'nno', 'ido_Latn', 'tam', 'jdt_Cyrl', 'uzb_Cyrl', 'yor', 'ilo', 'arq', 'shy_Latn', 'lad', 'ukr', 'afb', 'spa', 'srp_Cyrl', 'swe', 'snd_Arab', 'aze_Latn', 'hye', 'cym', 'arz', 'mdf', 'pdc', 'urd', 'mah', 'ltz', 'vie_Hani', 'vol_Latn', 'fuc', 'fuv', 'isl', 'zsm_Latn', 'zul', 'swg', 'afh_Latn', 'eus', 'rus', 'ksh',
'crh_Latn', 'mar', 'kab', 'cos', 'mlg', 'sgs', 'gan', 'ile_Latn', 'lao', 'ldn_Latn', 'hnj_Latn', 'bul', 'bre', 'ces', 'tel', 'umb', 'bel', 'jav_Java', 'tly_Latn', 'gcf_Latn', 'jbo_Latn', 'zho', 'pau', 'stq', 'fra', 'cmn_Hans', 'sun', 'vec', 'nau', 'tur', 'nob_Hebr', 'asm', 'deu', 'dtp', 'war', 'wol', 'min', 'som', 'bel_Latn', 'ike_Latn', 'grc_Grek',
'brx_Latn', 'scn', 'heb', 'sin', 'krl', 'hoc', 'izh', 'tat_Arab', 'kin', 'lfn_Latn', 'lav', 'chr', 'cmn', 'ara', 'lij', 'tat', 'ell', 'nld', 'xho', 'ben', 'nov_Latn', 'lit'}),
"nic": ("Niger-Kordofanian languages", {'fuc', 'fuv', 'umb', 'zul', 'lug', 'ibo', 'sag', 'yor', 'toi_Latn', 'ewe', 'kin', 'nya', 'tso', 'sna', 'wol', 'xho', 'bam_Latn', 'lin', 'swh', 'run'}),
"nld": ("Dutch", {"nld"}), "nor": ("Norwegian", {"nob", "nno"}), "phi": ("Philippine languages", {"ilo", "akl_Latn", "war", "hil", "pag", "ceb"}), "pol": ("Polish", {"pol"}),
"por": ("Portuguese", {"por"}), "pqe": ("Eastern Malayo-Polynesian languages", {"fij", "gil", "haw", "mah", "mri", "nau", "niu", "rap", "smo", "tah", "ton", "tvl"}),
"roa": ("Romance languages", {'hat', 'spa', 'wln', 'zsm_Latn', 'pms', 'glg', 'arg', 'scn', 'frm_Latn', 'ast', 'gcf_Latn', 'egl', 'max_Latn', 'cat', 'ind', 'oci', 'cos', 'fra', 'ron', 'vec', 'lad_Latn', 'lld_Latn', 'tmw_Latn', 'mfe', 'lij', 'lmo', 'por', 'min', 'lad', 'zlm_Latn', 'ext', 'pap', 'mwl', 'ita', 'roh'}),
"ron": ("Romanian", {"ron"}), "run": ("Rundi", {"run"}), "rus": ("Russian", {"rus"}), "sal": ("Salishan languages", {"shs_Latn"}), "sem": ("Semitic languages", {"acm", "afb", "amh", "apc", "ara", "arq", "ary", "arz", "heb", "mlt", "tir"}),
"sla": ("Slavic languages", {'bel', 'srp_Cyrl', 'rus', 'mkd', 'hsb', 'hrv', 'srp_Latn', 'bul', 'slv', 'bos_Latn', 'csb_Latn', 'dsb', 'bul_Latn', 'rue', 'orv_Cyrl', 'bel_Latn', 'ukr', 'pol', 'ces'}),
"slv": ("Slovenian", {"slv"}), "spa": ("Spanish", {"spa"}), "swe": ("Swedish", {"swe"}), "taw": ("Tai", {"lao", "tha"}), "tgl": ("Tagalog", {"tgl_Latn"}), "tha": ("Thai", {"tha"}),
"trk": ("Turkic languages", {'kum', 'tuk_Latn', 'ota_Latn', 'kaz_Latn', 'tyv', 'uig_Cyrl', 'aze_Latn', 'kir_Cyrl', 'sah', 'tat_Latn', 'uzb_Cyrl', 'tat_Arab', 'crh_Latn', 'kjh', 'crh', 'kaz_Cyrl', 'tur', 'bak', 'ota_Arab', 'chv', 'uzb_Latn', 'tat', 'tuk', 'uig_Arab'}),
"tur": ("Turkish", {"tur"}), "ukr": ("Ukrainian", {"ukr"}), "urd": ("Urdu", {"urd"}), "urj": ("Uralic languages", {'fin', 'mdf', 'vep', 'krl', 'udm', 'fkv_Latn', 'sme', 'est', 'hun', 'kpv', 'mhr', 'myv', 'vro', 'izh', 'sma', 'liv_Latn'}),
"vie": ("Vietnamese", {"vie", "vie_Hani"}), "war": ("Waray (Philippines)", {"war"}), "zho": ("Chinese", {'cmn_Hang', 'cmn_Bopo', 'lzh', 'cmn_Yiii', 'wuu_Latn', 'lzh_Kana', 'cmn_Hant', 'yue_Hang', 'lzh_Hans', 'yue_Hant', 'lzh_Yiii', 'hak_Hani', 'yue_Kana', 'zho', 'nan', 'cjy_Hans', 'nan_Hani', 'cmn_Hans', 'wuu_Bopo', 'gan', 'yue', 'zho_Hans', 'cmn_Hira', 'wuu_Hani', 'yue_Hira', 'lzh_Bopo', 'lzh_Hira', 'cmn', 'wuu', 'cmn_Latn',
'lzh_Hang', 'yue_Hani', 'yue_Hans', 'zho_Hant', 'cmn_Hani', 'lzh_Hani', 'cmn_Kana', 'yue_Bopo', 'cjy_Hant'}), "zle": ("East Slavic languages", {"bel", "orv_Cyrl", "bel_Latn", "rus", "ukr", "rue"}), "zls": ("South Slavic languages", {"bos_Latn", "bul", "bul_Latn", "hrv", "mkd", "slv", "srp_Cyrl", "srp_Latn"}), "zlw": ("West Slavic languages", {"csb_Latn", "dsb", "hsb", "pol", "ces"})}
def l2front_matter(langs): return "".join(f"- {l}\n" for l in langs)
def dedup(lst):
    new_lst = []
    for item in lst:
        if not item or item in new_lst: continue
        else: new_lst.append(item)
    return new_lst
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--models", action="append", help="<Required> Set flag", required=True, nargs="+", dest="models")
    parser.add_argument("-save_dir", "--save_dir", default="marian_converted", help="where to save converted models")
    args = parser.parse_args()
    resolver = TatoebaConverter(save_dir=args.save_dir)
    resolver.convert_models(args.models[0])
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
