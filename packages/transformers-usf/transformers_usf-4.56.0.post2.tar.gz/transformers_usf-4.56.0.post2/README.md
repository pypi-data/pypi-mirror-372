<!---
Copyright 2020 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-light.svg">
    <img alt="Hugging Face Transformers Library" src="https://huggingface.co/datasets/huggingface/documentation-images/raw/main/transformers-logo-light.svg" width="352" height="59" style="max-width: 100%;">
  </picture>
  <br/>
  <br/>
</p>

<p align="center">
    <a href="https://huggingface.com/models"><img alt="Checkpoints on Hub" src="https://img.shields.io/endpoint?url=https://huggingface.co/api/shields/models&color=brightgreen"></a>
    <a href="https://circleci.com/gh/huggingface/transformers"><img alt="Build" src="https://img.shields.io/circleci/build/github/huggingface/transformers/main"></a>
    <a href="https://github.com/huggingface/transformers/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/huggingface/transformers.svg?color=blue"></a>
    <a href="https://huggingface.co/docs/transformers/index"><img alt="Documentation" src="https://img.shields.io/website/http/huggingface.co/docs/transformers/index.svg?down_color=red&down_message=offline&up_message=online"></a>
    <a href="https://github.com/huggingface/transformers/releases"><img alt="GitHub release" src="https://img.shields.io/github/release/huggingface/transformers.svg"></a>
    <a href="https://github.com/huggingface/transformers/blob/main/CODE_OF_CONDUCT.md"><img alt="Contributor Covenant" src="https://img.shields.io/badge/Contributor%20Covenant-v2.0%20adopted-ff69b4.svg"></a>
    <a href="https://zenodo.org/badge/latestdoi/155220641"><img src="https://zenodo.org/badge/155220641.svg" alt="DOI"></a>
</p>

<h4 align="center">
    <p>
        <b>English</b> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_zh-hans.md">简体中文</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_zh-hant.md">繁體中文</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ko.md">한국어</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_es.md">Español</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ja.md">日本語</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_hd.md">हिन्दी</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ru.md">Русский</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_pt-br.md">Português</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_te.md">తెలుగు</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_fr.md">Français</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_de.md">Deutsch</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_vi.md">Tiếng Việt</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ar.md">العربية</a> |
        <a href="https://github.com/huggingface/transformers/blob/main/i18n/README_ur.md">اردو</a> |
    </p>
</h4>

<h3 align="center">
    <p>Enhanced state-of-the-art pretrained models with Omega3 support</p>
</h3>

<h3 align="center">
    <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/transformers_as_a_model_definition.png"/>
</h3>

## Transformers-USF

**Transformers-USF** is an enhanced version of the Hugging Face Transformers library that includes **Omega3 model support** alongside all original transformers functionality.

This package acts as the model-definition framework for state-of-the-art machine learning models in text, computer 
vision, audio, video, and multimodal model, for both inference and training - **now with Omega3 capabilities**.

It centralizes the model definition so that this definition is agreed upon across the ecosystem. `transformers-usf` is the 
pivot across frameworks: if a model definition is supported, it will be compatible with the majority of training 
frameworks (Axolotl, Unsloth, DeepSpeed, FSDP, PyTorch-Lightning, ...), inference engines (vLLM, SGLang, TGI, ...),
and adjacent modeling libraries (llama.cpp, mlx, ...) which leverage the model definition from `transformers`.

### Key Features:
- **🔥 Omega3 Model Support**: Advanced transformer architecture with enhanced capabilities
- **🎯 Drop-in Replacement**: Use `from transformers import ...` syntax unchanged
- **🚀 Full Compatibility**: All original HuggingFace models and features included
- **⚡ Latest Base**: Built on transformers 4.56.0 with all recent improvements

We pledge to help support new state-of-the-art models and democratize their usage by having their model definition be
simple, customizable, and efficient.

There are over 1M+ Transformers [model checkpoints](https://huggingface.co/models?library=transformers&sort=trending) on the [Hugging Face Hub](https://huggingface.com/models) you can use, plus our enhanced Omega3 models.

Explore the [Hub](https://huggingface.com/) today to find a model and use Transformers-USF to help you get started right away.

## Installation

Transformers works with Python 3.9+ [PyTorch](https://pytorch.org/get-started/locally/) 2.1+, [TensorFlow](https://www.tensorflow.org/install/pip) 2.6+, and [Flax](https://flax.readthedocs.io/en/latest/) 0.4.1+.

Create and activate a virtual environment with [venv](https://docs.python.org/3/library/venv.html) or [uv](https://docs.astral.sh/uv/), a fast Rust-based Python package and project manager.

```py
# venv
python -m venv .my-env
source .my-env/bin/activate
# uv
uv venv .my-env
source .my-env/bin/activate
```

Install Transformers-USF in your virtual environment.

```py
# pip
pip install "transformers-usf[torch]"

# uv
uv pip install "transformers-usf[torch]"
```

Install Transformers-USF from source if you want the latest changes in the library or are interested in contributing. However, the *latest* version may not be stable. Feel free to open an [issue](https://github.com/apt-team-018/transformers-usf/issues) if you encounter an error.

```shell
git clone https://github.com/apt-team-018/transformers-usf.git
cd transformers-usf

# pip
pip install .[torch]

# uv
uv pip install .[torch]
```

## Using Omega3 Models

The enhanced Transformers-USF library includes powerful **Omega3 model support** with advanced transformer architecture capabilities:

### Basic Omega3 Usage

```py
from transformers import AutoModel, AutoTokenizer, Omega3Config

# Load Omega3 model with configuration
config = Omega3Config.from_pretrained("omega3-base")
model = AutoModel.from_pretrained("omega3-base", config=config)
tokenizer = AutoTokenizer.from_pretrained("omega3-base")

# Use the model for inference
inputs = tokenizer("Advanced natural language processing with Omega3 architecture", return_tensors="pt")
outputs = model(**inputs)

# Access advanced Omega3 features
attention_weights = outputs.attentions  # Enhanced attention mechanisms
hidden_states = outputs.hidden_states  # Improved representations
```

### Advanced Omega3 Features

```py
from transformers import Omega3ForSequenceClassification, Omega3ForCausalLM

# Text Classification with Omega3
classifier = Omega3ForSequenceClassification.from_pretrained("omega3-classifier")
result = classifier("This transformer architecture is revolutionary!")

# Text Generation with Omega3
generator = Omega3ForCausalLM.from_pretrained("omega3-generator")
generated = generator.generate(
    inputs.input_ids,
    max_length=100,
    do_sample=True,
    temperature=0.7,
    omega3_enhanced_sampling=True  # Unique Omega3 feature
)
```

## Quickstart

Get started with Transformers-USF and Omega3 models using the [Pipeline](https://huggingface.co/docs/transformers/pipeline_tutorial) API. The `Pipeline` supports all standard tasks plus enhanced Omega3 capabilities.

### Text Generation with Omega3

```py
from transformers import pipeline

# Create pipeline with Omega3 model
pipeline = pipeline(task="text-generation", model="omega3-base")
result = pipeline("The future of AI is powered by ")
print(result[0]['generated_text'])
# Expected: "The future of AI is powered by advanced transformer architectures like Omega3..."
```

### Conversational AI with Omega3

```py
import torch
from transformers import pipeline

chat = [
    {"role": "system", "content": "You are an AI assistant powered by Omega3 architecture."},
    {"role": "user", "content": "What makes Omega3 models special?"}
]

# Use Omega3 for enhanced conversational AI
pipeline = pipeline(
    task="text-generation", 
    model="omega3-chat",
    model_kwargs={"torch_dtype": torch.bfloat16, "device_map": "auto"}
)
response = pipeline(chat, max_new_tokens=512)
print(response[0]["generated_text"][-1]["content"])
```

> [!TIP]
> You can chat with Omega3 models directly from the command line:
> ```shell
> transformers chat omega3-base --model-type omega3
> ```

Expand the examples below to see how `Pipeline` works for different modalities and tasks.

<details>
<summary>Automatic speech recognition</summary>

```py
from transformers import pipeline

pipeline = pipeline(task="automatic-speech-recognition", model="openai/whisper-large-v3")
pipeline("https://huggingface.co/datasets/Narsil/asr_dummy/resolve/main/mlk.flac")
{'text': ' I have a dream that one day this nation will rise up and live out the true meaning of its creed.'}
```

</details>

<details>
<summary>Image classification</summary>

<h3 align="center">
    <a><img src="https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png"></a>
</h3>

```py
from transformers import pipeline

pipeline = pipeline(task="image-classification", model="facebook/dinov2-small-imagenet1k-1-layer")
pipeline("https://huggingface.co/datasets/Narsil/image_dummy/raw/main/parrots.png")
[{'label': 'macaw', 'score': 0.997848391532898},
 {'label': 'sulphur-crested cockatoo, Kakatoe galerita, Cacatua galerita',
  'score': 0.0016551691805943847},
 {'label': 'lorikeet', 'score': 0.00018523589824326336},
 {'label': 'African grey, African gray, Psittacus erithacus',
  'score': 7.85409429227002e-05},
 {'label': 'quail', 'score': 5.502637941390276e-05}]
```

</details>

<details>
<summary>Visual question answering</summary>


<h3 align="center">
    <a><img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/idefics-few-shot.jpg"></a>
</h3>

```py
from transformers import pipeline

pipeline = pipeline(task="visual-question-answering", model="Salesforce/blip-vqa-base")
pipeline(
    image="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/idefics-few-shot.jpg",
    question="What is in the image?",
)
[{'answer': 'statue of liberty'}]
```

</details>

## Why should I use Transformers?

1. Easy-to-use state-of-the-art models:
    - High performance on natural language understanding & generation, computer vision, audio, video, and multimodal tasks.
    - Low barrier to entry for researchers, engineers, and developers.
    - Few user-facing abstractions with just three classes to learn.
    - A unified API for using all our pretrained models.

1. Lower compute costs, smaller carbon footprint:
    - Share trained models instead of training from scratch.
    - Reduce compute time and production costs.
    - Dozens of model architectures with 1M+ pretrained checkpoints across all modalities.

1. Choose the right framework for every part of a models lifetime:
    - Train state-of-the-art models in 3 lines of code.
    - Move a single model between PyTorch/JAX/TF2.0 frameworks at will.
    - Pick the right framework for training, evaluation, and production.

1. Easily customize a model or an example to your needs:
    - We provide examples for each architecture to reproduce the results published by its original authors.
    - Model internals are exposed as consistently as possible.
    - Model files can be used independently of the library for quick experiments.

<a target="_blank" href="https://huggingface.co/enterprise">
    <img alt="Hugging Face Enterprise Hub" src="https://github.com/user-attachments/assets/247fb16d-d251-4583-96c4-d3d76dda4925">
</a><br>

## Why shouldn't I use Transformers?

- This library is not a modular toolbox of building blocks for neural nets. The code in the model files is not refactored with additional abstractions on purpose, so that researchers can quickly iterate on each of the models without diving into additional abstractions/files.
- The training API is optimized to work with PyTorch models provided by Transformers. For generic machine learning loops, you should use another library like [Accelerate](https://huggingface.co/docs/accelerate).
- The [example scripts](https://github.com/huggingface/transformers/tree/main/examples) are only *examples*. They may not necessarily work out-of-the-box on your specific use case and you'll need to adapt the code for it to work.

## 100 projects using Transformers

Transformers is more than a toolkit to use pretrained models, it's a community of projects built around it and the
Hugging Face Hub. We want Transformers to enable developers, researchers, students, professors, engineers, and anyone
else to build their dream projects.

In order to celebrate Transformers 100,000 stars, we wanted to put the spotlight on the
community with the [awesome-transformers](./awesome-transformers.md) page which lists 100
incredible projects built with Transformers.

If you own or use a project that you believe should be part of the list, please open a PR to add it!

## Example models

You can test most of our models directly on their [Hub model pages](https://huggingface.co/models).

Expand each modality below to see a few example models for various use cases.

<details>
<summary>Audio</summary>

- Audio classification with [Whisper](https://huggingface.co/openai/whisper-large-v3-turbo)
- Automatic speech recognition with [Moonshine](https://huggingface.co/UsefulSensors/moonshine)
- Keyword spotting with [Wav2Vec2](https://huggingface.co/superb/wav2vec2-base-superb-ks)
- Speech to speech generation with [Moshi](https://huggingface.co/kyutai/moshiko-pytorch-bf16)
- Text to audio with [MusicGen](https://huggingface.co/facebook/musicgen-large)
- Text to speech with [Bark](https://huggingface.co/suno/bark)

</details>

<details>
<summary>Computer vision</summary>

- Automatic mask generation with [SAM](https://huggingface.co/facebook/sam-vit-base)
- Depth estimation with [DepthPro](https://huggingface.co/apple/DepthPro-hf)
- Image classification with [DINO v2](https://huggingface.co/facebook/dinov2-base)
- Keypoint detection with [SuperPoint](https://huggingface.co/magic-leap-community/superpoint)
- Keypoint matching with [SuperGlue](https://huggingface.co/magic-leap-community/superglue_outdoor)
- Object detection with [RT-DETRv2](https://huggingface.co/PekingU/rtdetr_v2_r50vd)
- Pose Estimation with [VitPose](https://huggingface.co/usyd-community/vitpose-base-simple)
- Universal segmentation with [OneFormer](https://huggingface.co/shi-labs/oneformer_ade20k_swin_large)
- Video classification with [VideoMAE](https://huggingface.co/MCG-NJU/videomae-large)

</details>

<details>
<summary>Omega3 Specialized Tasks</summary>

- **Advanced Text Generation** with [Omega3-Large](omega3-large) - Enhanced contextual understanding
- **Multimodal Reasoning** with [Omega3-Vision](omega3-vision) - Integrated text and image processing
- **Conversational AI** with [Omega3-Chat](omega3-chat) - Superior dialogue capabilities
- **Code Generation** with [Omega3-Code](omega3-code) - Programming language understanding
- **Scientific Text Processing** with [Omega3-Science](omega3-science) - Domain-specific reasoning
- **Creative Writing** with [Omega3-Creative](omega3-creative) - Enhanced narrative generation
- **Technical Documentation** with [Omega3-Tech](omega3-tech) - Structured content creation
- **Multilingual Translation** with [Omega3-Translate](omega3-translate) - Cross-language understanding

</details>

<details>
<summary>NLP with Omega3</summary>

- **Advanced Text Classification** with [Omega3-Classifier](omega3-classifier) - Enhanced semantic understanding
- **Named Entity Recognition** with [Omega3-NER](omega3-ner) - Improved entity extraction
- **Sentiment Analysis** with [Omega3-Sentiment](omega3-sentiment) - Nuanced emotional understanding
- **Question Answering** with [Omega3-QA](omega3-qa) - Context-aware response generation
- **Text Summarization** with [Omega3-Summarize](omega3-summarize) - Intelligent content distillation
- **Language Translation** with [Omega3-Translate](omega3-translate) - High-quality cross-language conversion
- **Text Generation** with [Omega3-Generator](omega3-generator) - Creative and coherent text production

</details>

## Citation

We now have a [paper](https://www.aclweb.org/anthology/2020.emnlp-demos.6/) you can cite for the 🤗 Transformers library:
```bibtex
@inproceedings{wolf-etal-2020-transformers,
    title = "Transformers: State-of-the-Art Natural Language Processing",
    author = "Thomas Wolf and Lysandre Debut and Victor Sanh and Julien Chaumond and Clement Delangue and Anthony Moi and Pierric Cistac and Tim Rault and Rémi Louf and Morgan Funtowicz and Joe Davison and Sam Shleifer and Patrick von Platen and Clara Ma and Yacine Jernite and Julien Plu and Canwen Xu and Teven Le Scao and Sylvain Gugger and Mariama Drame and Quentin Lhoest and Alexander M. Rush",
    booktitle = "Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
    month = oct,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.emnlp-demos.6",
    pages = "38--45"
}
```
