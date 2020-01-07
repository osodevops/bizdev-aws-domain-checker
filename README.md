# OSO DevOps BizDev - Part 1
Python util script to parse a list of URLs and checkers each against public IP ranges of all AWS services.

Run as a Docker container:

~~~bash
git clone https://github.com/osodevops/bizdev-aws-domain-checker
cd bizdev-aws-domain-checker
docker build -t osodevops/aws-domain-checker .

# Call it without arguments to display the full help
docker run --rm osodevops/aws-domain-checker

# Call it single domain to display result.
docker run --rm osodevops/aws-domain-checker check --url www.osodevops.io

# Basic usage - pass in the URLs with mounted volume:
docker run --rm -v $(pwd):/tmp osodevops/aws-domain-checker:latest check --website-list ./tmp/big_data_london_exhibitors.json

# To save the report in a specific format (json / csv), mount /tmp as a volume:
docker run --rm -v $(pwd):/tmp osodevops/aws-domain-checker:latest check --website-list ./tmp/big_data_london_exhibitors.json --export-json /tmp/out.json
~~~
