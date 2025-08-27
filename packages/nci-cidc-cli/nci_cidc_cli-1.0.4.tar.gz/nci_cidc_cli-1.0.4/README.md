## NCI-CIDC-CLI

Command line tool for interfacing with the NCI CIDC API.

### Environments

There are four possible environments for the CLI: dev, dev-cloudtwo, staging, and prod. As of v1.00.00, we removed extra options as part of the migration. If you are having trouble with old cached environments remove the .cidc directory in your root.

## Setup

### Installation

```bash
pip3 install nci-cidc-cli
```

### Usage

To display the help message for the CLI, run:

```bash
nci-cidc
```

To authenticate with the CIDC API, run:

```bash
nci-cidc login [token]
```

## Development

For local development, install the development dependencies:

```bash
pip install -r requirements.dev.txt
```

## Admin functions

Under the (hidden) `admin` are several functions meant for CIDC administators / engineers.

### CSMS

```bash
nci-cidc admin test-csms
```

A simple API hit for a test of CSMS connection. Hits API endpoint `/admin/test_csms` which in turn gets CSMS's `/docs`.
This tests that the API is able to successfully make connection with the CSMS, as the `/docs` endpoint requires authorization.
As the API endpoint is protected, only users with role `cidc-admin` can make this request.

### refresh-trial ###

A simple API hit to refresh the trial summary, participants.csv file, and samples.csv file.

```bash
nci-cidc refresh-trial TRIAL_ID
```

### dbedit suite

A set of commands to list / remove data from the database, including shipments, clinical data, and assay/analysis data.
It directly uses Google's cloud SDK to make a direct connection to the postgres cloud sql database, so it requires the user has `cloudsql.instances.connect` IAM permission.

#### Authentication

Authentication uses Application Default Credentials (ADC). Log-in is done via:

```bash
gcloud auth application-default login
```

#### Configuration

Configuration of the environment ie staging versus production is done as above using:

```bash
nci-cidc config get-env
nci-cidc config set-env ENV
```

Configuration of the database username is done via a pair of functions:

```bash
nci-cidc admin get-username
nci-cidc admin set-username USERNAME
```

### IAM Authentication

We are now using IAM for authentication on admin requests.
To make admin requests work, make sure your user has the "iam.serviceAccounts.getAccessToken" permission in the proper enviornment. Contact devops for access.

Before running your admin request, impersonate the service account.

Example for dev `gcloud auth application-default login --impersonate-service-account nih-nci-cimac-cidc-dev2@appspot.gserviceaccount.com`

Be sure to set the correct db admin username.

Example for dev: nci-cidc admin set-username nih-nci-cimac-cidc-dev2@appspot

#### Listing data

Under the `list` subcommand of `nci-cidc admin`, you can get descriptions of the data available in the database.

- `nci-cidc admin list clinical TRIAL_ID`

  - prints a table describing all shipments for the given trial
  - with the following columns:
    - `object_url`, `filename`, `num_participants`, `created`, `comment`

- `nci-cidc admin list misc-data TRIAL_ID`

  - prints a table describing all misc_data files for the given trial
  - with the following columns:
    - `batch_id`, `object_url`, `filename`, `created`, `description`

- `nci-cidc admin list shipments TRIAL_ID`

  - prints a table describing all shipments for the given trial
  - with the following columns:
    - `upload_type`, `manifest_id`, `num_samples`, `created`

- `nci-cidc admin list assay TRIAL_ID ASSAY_OR_ANALYSIS`
  - prints a table listing all samples for the given assay/analysis and trial
  - any of the following values are allowed:
    - `clinical_data`, same as `nci-cidc admin list clinical TRIAL_ID`
    - `misc_data`, same as `nci-cidc admin list misc-data TRIAL_ID`
    - analyses: `atacseq_analysis`, `cytof_analysis`, `rna_level1_analysis`, `tcr_analysis`, `wes_analysis`, `wes_analysis_old`, `wes_tumor_only_analysis`, `wes_tumor_only_analysis_old`
    - assays: `atacseq`, `ctdna`, `cytof`, `hande`, `ihc`, `elisa`, `microbiome`, `mif`, `nanostring`, `olink`, `rna`, `tcr`, `wes`

#### Removing data

Under the `remove` subcommand of `nci-cidc admin`, you can remove a wide variety of data from the JSON blobs.

NOTE: Remove commands only affect the database.
Use the ```refresh-trial``` command to refresh the trial summary, participants.csv, and samples.csv

- `nci-cidc admin remove clinical TRIAL_ID TARGET_ID`

  - removes a given clinical data file from a given trial's metadata as well as the file itself from the portal
  - `TARGET_ID` is the `filename` of the clinical data to remove, as from `nci-cidc admin list clinical TRIAL_ID`
    - special value `'*'` for all files for this trial

- `nci-cidc admin remove shipment TRIAL_ID TARGET_ID`

  - removes a given shipment from a given trial's metadata
  - `TARGET_ID` is the `manifest_id` of the shipment to remove, as from `nci-cidc admin list shipments TRIAL_ID`

- `nci-cidc admin remove assay TRIAL_ID ASSAY_OR_ANALYSIS TARGET_ID`
  - removes a given clinical data file from a given trial's metadata as well as the associated files themselves from the portal
  - for `ASSAY_OR_ANALYSIS=clinical_data`, same as `nci-cidc admin remove clinical TRIAL_ID TARGET_ID`
  - `TARGET_ID` is a tuple of the ids to find the data to remove, as from `nci-cidc admin list assay TRIAL_ID ASSAY_OR_ANALYSIS`.
    - It cannot go past where is divisible in the data, but can end early to remove the whole section.
    - Namely:
      - `elisa`: requires only `assay_run_id`
      - `misc_data`, `olink`: require `batch_id` with an optional `filename`
      - `nanostring`: requires `batch_id` and optional `run_id`
      - `rna_level1_analysis`, `wes_tumor_only_analysis`, `wes_tumor_only_analysis_old`: requires only `cimac_id`
      - `wes_analysis`, `wes_analysis_old`: requires only `run_id`
      - otherwise: requires `batch_id` and optional `cimac_id`
