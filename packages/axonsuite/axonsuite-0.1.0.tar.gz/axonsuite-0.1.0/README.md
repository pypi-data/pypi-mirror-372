# AxonSuite 🧠⚡


**AxonSuite** is a curated set of pip *extras* that lets you install complete ML/DL stacks with one command. Ideal for **freshers, hackathons, interviews, college labs**, and anyone who wants to skip setup stress.

# Show groups
axonsuite list


# See what's inside a group
axonsuite show ml-basic


## Install


Pick exactly what you need:


```bash
# Tabular ML essentials (numpy/pandas/sklearn/plots)
pip install axonsuite[ml-basic]


# Advanced ML (boosting + encoders + imbalance)
pip install axonsuite[ml-advanced]


# Deep learning cores (TensorFlow + PyTorch CPU wheels)
pip install axonsuite[dl-basic]


# Vision/Audio/NLP DL add‑ons (torchvision/torchaudio/TFP/transformers)
pip install axonsuite[dl-advanced]


# Viz add‑ons (plotly, pydot, graphviz)
pip install axonsuite[viz]


# NLP stack (nltk, gensim, spaCy, datasets, transformers)
pip install axonsuite[nlp]


# Utilities (dotenv, requests)
pip install axonsuite[utils]


# Everything (heavy)
pip install axonsuite[all]