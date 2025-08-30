# DISCLAIMER
**This implementation is taken from [HumanCompatibleAI/overcooked_ai](https://github.com/HumanCompatibleAI/overcooked_ai)**. This repo has been forked to remove any algorithm implementation, upgrade dependencies (such as numpy>=2.0) and only keep the core environment. 
It implements the `marlenv` interface in addition to original `gymnasium` one.

# Overcooked-AI 🧑‍🍳🤖
<p align="center">
  <img src="./images/layouts.gif" width="100%"> 
  <i>5 of the available layouts. New layouts are easy to hardcode or generate programmatically.</i>
</p>

## Introduction 🥘

Overcooked-AI is a benchmark environment for fully cooperative human-AI task performance, based on the wildly popular video game [Overcooked](http://www.ghosttowngames.com/overcooked/).

The goal of the game is to deliver soups as fast as possible. Each soup requires placing up to 3 ingredients in a pot, waiting for the soup to cook, and then having an agent pick up the soup and delivering it. The agents should split up tasks on the fly and coordinate effectively in order to achieve high reward.

You can **try out the game [here](https://humancompatibleai.github.io/overcooked-demo/)** (playing with some previously trained DRL agents). To play with your own trained agents using this interface, or to collect more human-AI or human-human data, you can use the code [here](https://github.com/HumanCompatibleAI/overcooked_ai/tree/master/src/overcooked_demo). You can find some human-human and human-AI gameplay data already collected [here](https://github.com/HumanCompatibleAI/overcooked_ai/tree/master/src/human_aware_rl/static/human_data).

**NOTE + LOOKING FOR CONTRIBUTORS:** DRL and BC implementations are now deprecated. We used to include code for training BC and PPO agents in the `human_aware_rl` directory. See [this issue](https://github.com/HumanCompatibleAI/overcooked_ai/issues/162) for more details.

This benchmark was build in the context of a 2019 paper: *[On the Utility of Learning about Humans for Human-AI Coordination](https://arxiv.org/abs/1910.05789)*. Also see our [blog post](https://bair.berkeley.edu/blog/2019/10/21/coordination/).

## Installation ☑️
You can install the pre-compiled wheel file using pip or your favorite package manager.
```bash
pip install overcooked
```
Note that PyPI releases are stable but infrequent. For the most up-to-date development features, build from source. We recommend using [uv](https://docs.astral.sh/uv/getting-started/installation/) to install the package, so that you can use the provided lockfile to ensure no minimal package version issues.


## Research Papers using Overcooked-AI 📑


- Carroll, Micah, Rohin Shah, Mark K. Ho, Thomas L. Griffiths, Sanjit A. Seshia, Pieter Abbeel, and Anca Dragan. ["On the utility of learning about humans for human-ai coordination."](https://arxiv.org/abs/1910.05789) NeurIPS 2019.
- Charakorn, Rujikorn, Poramate Manoonpong, and Nat Dilokthanakul. [“Investigating Partner Diversification Methods in Cooperative Multi-Agent Deep Reinforcement Learning.”](https://www.rujikorn.com/files/papers/diversity_ICONIP2020.pdf) Neural Information Processing. ICONIP 2020.
- Knott, Paul, Micah Carroll, Sam Devlin, Kamil Ciosek, Katja Hofmann, Anca D. Dragan, and Rohin Shah. ["Evaluating the Robustness of Collaborative Agents."](https://arxiv.org/abs/2101.05507) AAMAS 2021.
- Nalepka, Patrick, Jordan P. Gregory-Dunsmore, James Simpson, Gaurav Patil, and Michael J. Richardson. ["Interaction Flexibility in Artificial Agents Teaming with Humans."](https://www.researchgate.net/publication/351533529_Interaction_Flexibility_in_Artificial_Agents_Teaming_with_Humans) Cogsci 2021.
- Fontaine, Matthew C., Ya-Chuan Hsu, Yulun Zhang, Bryon Tjanaka, and Stefanos Nikolaidis. [“On the Importance of Environments in Human-Robot Coordination”](http://arxiv.org/abs/2106.10853) RSS 2021.
- Zhao, Rui, Jinming Song, Hu Haifeng, Yang Gao, Yi Wu, Zhongqian Sun, Yang Wei. ["Maximum Entropy Population Based Training for Zero-Shot Human-AI Coordination"](https://arxiv.org/abs/2112.11701). NeurIPS Cooperative AI Workshop, 2021.
- Sarkar, Bidipta, Aditi Talati, Andy Shih, and Dorsa Sadigh. [“PantheonRL: A MARL Library for Dynamic Training Interactions”](https://iliad.stanford.edu/pdfs/publications/sarkar2022pantheonrl.pdf). AAAI 2022.
- Ribeiro, João G., Cassandro Martinho, Alberto Sardinha, Francisco S. Melo. ["Assisting Unknown Teammates in Unknown Tasks: Ad Hoc Teamwork under Partial Observability"](https://arxiv.org/abs/2201.03538).
- Xihuai Wang, Shao Zhang, Wenhao Zhang, Wentao Dong, Jingxiao Chen, Ying Wen and Weinan Zhang. NeurIPS 2024. [“ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination”](https://arxiv.org/abs/2310.05208v2).


## Further Issues and questions ❓
If you have issues or questions, you can contact [Micah Carroll](https://micahcarroll.github.io) at mdc@berkeley.edu.