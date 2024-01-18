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

