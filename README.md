# OSO DevOps BizDev - Part 1
Python util script to parse a list of URLs and checkers each against public IP ranges of all AWS services.

Run as a Docker container:

~~~bash
git clone https://github.com/osodevops/bizdev-waf-checker
cd bizdev-waf-checker
docker build -t osodevops/aws-domain-checker .

# Call it without arguments to display the full help
docker run --rm osodevops/aws-domain-checker:latest

# Basic usage
docker run --rm osodevops/aws-domain-checker:latest --website-file big_data_london_exhibitors.json

# To save the report in a specific format (json / csv), mount /tmp as a volume:
docker run --rm -v $(pwd):/tmp osodevops/aws-domain-checker:latest \
    --website-file big_data_london_exhibitors.json \ 
    --export-csv ./out.csv
~~~
