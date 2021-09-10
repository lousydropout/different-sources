# Different Sources

For IaC (Infrastructure as code), this repo uses AWS CDK (cloud development kit).
Much is already set up.

## Steps

### 1. Install node and python 3.8

### 2. Create a python virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4. Install the needed 3rd party modules

```bash
pip install -r requirements.txt
```

### 5. Deploy

```bash
npx cdk deploy
```

## To upload the parsers

After deploying your stack, go into `/scripts` and update `upload.py` `line 5` to reflect the endpoint of the API Gateway you deployed.

Then, run the following

```bash
python upload.py parsers/parser_basic.py
python upload.py parsers/parser_extended.py
python upload.py parsers/parser_augmented.py

```

## To test in AWS

Go to the `example` lambda in your AWS console and create 3 tests using the content of `/scripts/data/example1.json`, `/scripts/data/example2.json`, and `/scripts/data/example3.json`, respectively.

Then, choose your desired test case and hit `Test`.
