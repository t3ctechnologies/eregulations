## Findings

# Missing / incomplete information
- Set up github actions including OICD provider , environments and secrets are incomplete
- Role policies for the OIDC ROLE that github actions need is not described
- SSM variable setup for VPC id and subnets is not documented.
- s3 bucket name cannot be as in git - will get a 'S3 bucket exists'


# Running on local
- Dockerfile has error and does not compile as is need to be modified
- Steps for setting up are not in order. The formatting does not show up automatically


# Miscellaneous
There are publicly accessible API gateway URLs in the repo - a security no no



# Setup eregulations

This article explains the steps needed to set-up a new environment for the eregulations application on the AWS environment
### Prerequisites
The typical components in an image tag are shown in example below

-   `Access to AWS`
-   `git `
-   ``

## Steps to install



### Create the necessary AWS stored parameters


| SSM Variable | SSM Key | Required | Comments |
|----------|----------|----------|----------|
| DB_PASSWORD | /eregulations/db/password | **YES** | Required for application backend connectivity |
| DB_HOST | /eregulations/db/host | **YES** | Required for application backend connectivity |
| DB_PORT | /eregulations/db/port | **YES** | Required for application backend connectivity |
| GA_ID | /eregulations/http/google_analytics | NO | Required only if Google analytics is needed |
| HTTP_AUTH_USER | /eregulations/http/user | **YES** | User ID for application
| HTTP_AUTH_PASSWORD | /eregulations/http/password | **YES** | Password for application
| DJANGO_USERNAME | /eregulations/http/reader_user | **YES** | Django User|
| DJANGO_PASSWORD | /eregulations/http/reader_password | **YES** | Django Password
| DJANGO_ADMIN_USERNAME |/eregulations/http/user | **YES** | Django User Name 
| DJANGO_ADMIN_PASSWORD | /eregulations/http/password | **YES** | Django Admin password
| DJANGO_SETTINGS_MODULE |/eregulations/django_settings_module}
| BASE_URL|/eregulations/base_url
| CUSTOM_URL|/eregulations/custom_url}
| SURVEY_URL|/eregulations/survey_url}
| SIGNUP_URL|/eregulations/signup_url}
| SEARCHGOV_KEY|/eregulations/searchgov/key}
|SEARCHGOV_SITE_NAME|/eregulations/searchgov/site_name}
|OIDC_RP_CLIENT_ID|/eregulations/oidc/client_id}
|OIDC_RP_CLIENT_SECRET|/eregulations/oidc/client_secret}
|OIDC_OP_AUTHORIZATION_ENDPOINT|/eregulations/oidc/authorization_endpoint}
|OIDC_OP_TOKEN_ENDPOINT|/eregulations/oidc/token_endpoint}
|OIDC_OP_JWKS_ENDPOINT|/eregulations/oidc/jwks_endpoint}
|OIDC_OP_USER_ENDPOINT|/eregulations/oidc/user_endpoint}
|OIDC_END_EUA_SESSION|/eregulations/oidc/end_eua_session}
|BASIC_SEARCH_FILTER|/eregulations/basic_search_filter}
|QUOTED_SEARCH_FILTER|/eregulations/quoted_search_filter}
|EUA_FEATUREFLAG|/eregulations/eua/featureflag}
|subnet-01de8e5c081a2af6e
|subnet-0c2e0a7a4fc60e6de

