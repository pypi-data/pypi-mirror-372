# %% import
from plus_sync.config import Config
from plus_sync.hashing import SubjectIDHasher

# %% load config
config = Config.from_toml('plus_sync.toml')

hasher = SubjectIDHasher(config)
