# dismcli

DIALS InfenceService Manager or simply `dism` is a program to deploy/remove InferenceServices in KServe managed by DIALS.

## Local development

Install the dependencies and the package using `uv`:

```bash
uv sync --all-groups
uv pip install -e .
uv run pre-commit install
```

## Tests

Run tests with `pytest`:

```shell
uv run pytest tests/ --cov=dismcli --cov-report=xml --cov-report=term
```

### Tox

You may also want to run the tests with `tox` to test against multiple python versions:

```shell
uv run tox
```

**[asdf](https://asdf-vm.com/) users**

tox requires multiple versions of Python to be installed. Using `asdf`, you have multiple versions installed, but they aren’t normally exposed to the current shell. You can use the following command to expose multiple versions of Python in the current directory:

```bash
asdf set python 3.12.9 3.11.10 3.10.13
```

This will use `3.12.9` by default (if you just run `python`), but it will also put `python3.11` and `python3.10` symlinks in your PATH so you can run those too (which is exactly what tox is looking for).


## GitLab CI Setup for `dism-cli`

This document describes the steps taken to configure GitLab CI for the `dism-cli` repository so it can access the private repository `dism-core` via SSH during pipeline execution.

### Purpose

The `dism-cli` project depends on the `dism-core` repository using a Git+SSH link specified in `pyproject.toml`:

```toml
[tool.uv.sources]
dism-core = { git = "ssh://git@gitlab.cern.ch:7999/cms-dqmdc/libraries/dism-core.git", rev = "v1.0.0" }
```

To allow GitLab CI in `dism-cli` to clone `dism-core`, we need to set up SSH access.

---

### Steps

#### 1. Generate SSH Key Pair

Generate a new SSH key pair (without a passphrase) for CI access:

```bash
ssh-keygen -t ed25519 -f ci_key -N "" -C "dism-cli-ci-access"
```

- This creates:
  - `ci_key` (private key)
  - `ci_key.pub` (public key)

---

#### 2. Add Deploy Key to `dism-core`

- Go to the `dism-core` project on GitLab.
- Navigate to: **Settings > Repository > Deploy Keys**
- Add a new key:
  - **Title:** `dism-cli-ci-access`
  - **Key:** paste the contents of `ci_key.pub`

---

#### 3. Add CI/CD Variable to `dism-cli`

To securely provide the private key to GitLab CI:

1. Convert the private key to a base64 string:

   ```bash
   base64 -w0 ci_key > ci_key.b64
   ```

2. Copy the content of `ci_key.b64`.

3. Go to the `dism-cli` project on GitLab.

4. Navigate to: **Settings > CI/CD > Variables**

5. Add a new variable:
   - **Key:** `CI_SSH_PRIVATE_KEY_B64`
   - **Value:** paste the content from `ci_key.b64`
   - **Type:** Variable
   - **Masked and Hidden:** ✅

---

With this setup, the GitLab CI runner in `dism-cli` can authenticate with `dism-core` via SSH, allowing it to fetch dependencies during the test stage.
