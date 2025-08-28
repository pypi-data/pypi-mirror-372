import os

VINZ_URL = os.getenv('VINZ_URL') or 'https://vinz.atlasai.co'
DS_TOOLKIT_URL = os.getenv('DS_TOOLKIT_URL') or 'https://dstoolkit.atlasai.co'

# force mlhub library to go to ds toolkit
os.environ['MLHUB_URL'] = f'{DS_TOOLKIT_URL}/api'

DEFAULT_PAGE_SIZE = 20
DISABLE_SSL_VERIFICATION = 'DISABLE_SSL_VERIFICATION'

TOKEN_ENV_VAR = 'VINZ_ENCRYPTED_TOKEN'
TOKEN_TIMESTAMP_ENV_VAR = 'VINZ_ENCRYPTED_TOKEN_TIMESTAMP'

LEAFMAP_COLORMAP = [
    "viridis", "plasma", "inferno", "magma", "cividis",
    "Greys", "Purples", "Blues", "Greens", "Oranges", "Reds",
    "YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu", "GnBu", "PuBu",
    "YlGnBu", "PuBuGn", "BuGn", "YlGn"
]
