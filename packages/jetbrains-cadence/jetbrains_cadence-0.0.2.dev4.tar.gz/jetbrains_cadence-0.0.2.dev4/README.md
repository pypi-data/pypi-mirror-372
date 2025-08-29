# Cadence CLI


## Install
Configure poetry
```shell
poetry env use `which python`
poetry install
```

Install 
```shell
poetry run pip install --editable  .
```

This will create a `cadence` script in your current environment.


## Completions
To enable completions, run:
### bash
```bash
echo 'eval "$(_CADENCE_COMPLETE=bash_source cadence)"' >> ~/.bashrc
```
### zsh
```zsh
echo 'eval "$(_CADENCE_COMPLETE=zsh_source cadence)"' >> ~/.zshrc
```

---
## Set Server Endpoint
You can switch endpoint with 
```shell
CADENCE_SERVER_URL='test.jetbrains'
```

## Login

```shell
cadence login
```


or 
## Setup token manually
Go to [api.cadence.jetbrains.com](https://api.cadence.jetbrains.com/profile.html?item=accessTokens) | Profile Icon | Profile | Access Tokens

Create a new access token with 'Permission scope' set to '\<Same as current user>'.


Now login with
```shell
cadence login --browserless
```


Or add this access token to your environment via 
```shell
export CADENCE_TOKEN=<...>
```

## Run
```shell
cadence execution start --preset 'path/to/config' --project-id 'your-project-id'
```

## See status
```shell
cadence execution status --project-id 'your-project-id' --execution-id 'your-execution-id'
```

## Stop
```shell
cadence execution stop --project-id 'your-project-id' --execution-id 'your-execution-id'
```
