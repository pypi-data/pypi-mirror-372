# spider_env

`spider_env` is a lightweight environment wrapper for the [Spider dataset](https://yale-lily.github.io/spider).

## Installation

```bash
pip install spider_env
```

## Usage
```bash
from spider_env import SpiderEnv

spider = SpiderEnv(cache_dir="spider")
observation, info = spider.reset()
print("Question:", observation["instruction"])
print("SQL:", info["gold_query"])
print("Result:", info["gold_result"])
```

## Requirements
- Python 3.8+
- NumPy 1.26.4

## Author
Kha Nguyen Van - vankha.contact@gmail.com