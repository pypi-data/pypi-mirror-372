# Heaptree SDK

## Prerequisites

### Use a Heaptree Conda environment

1. Install Miniconda: https://www.anaconda.com/download/success
2. After installing, close and reopen your terminal, or run `source ~/.zshrc`
   - Confirm that Conda was successfully installed with `conda --version`
3. Create new conda environment with `conda create --name heaptree`
4. Activate the environment with `conda activate heaptree`

### Set API keys

1. Login to the Heaptree Bitwarden.
2. Set the Anthropic and Heaptree API keys:

```bash
# Set the Anthropic API key
> conda env config vars set ANTHROPIC_API_KEY=...

# Set the Heaptree API key
> conda env config vars set HEAPTREE_API_KEY=...
```

3. List the API keys to confirm they were successfully set: `conda env config vars list`
4. You're all set!

## Setup

`pip3 install requirements.txt`

## Testing

`python -m test.test_client`

## Demo

`python -m playground.chart`
