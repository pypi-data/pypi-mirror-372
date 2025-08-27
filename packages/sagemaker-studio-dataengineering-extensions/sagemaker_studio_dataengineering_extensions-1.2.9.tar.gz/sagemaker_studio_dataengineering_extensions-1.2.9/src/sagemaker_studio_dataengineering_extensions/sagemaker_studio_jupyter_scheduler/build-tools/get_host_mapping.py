"""
python functionaltest.py
curl 'https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/sagemaker/USD/current/sagemaker-instances-training.json?timestamp=1667695944100' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:106.0) Gecko/20100101 Firefox/106.0' -H 'Accept: */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Origin: https://aws.amazon.com' -H 'Connection: keep-alive' -H 'Referer: https://aws.amazon.com/' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: cross-site' -H 'TE: trailers'
"""
import json
import urllib.request
import re
from bs4 import BeautifulSoup


"""
Function to add instance mapping for AWS Classic partition regions
"""


def get_classic_region_mapping(region_map):
    classic_region_data = json.loads(
        urllib.request.urlopen(
            "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/sagemaker/USD/current/sagemaker-instances-training.json"
        ).read()
    )

    for region_name in classic_region_data["regions"].keys():
        region_map["regions"][region_name] = []
        for instance_title, instance_data in classic_region_data["regions"][
            region_name
        ].items():
            region_map["regions"][region_name].append(
                {"instance_name": instance_data["Instance"].strip()}
            )

    return region_map


"""
Function to add instance mapping for AWS China partition regions

Note: the logic of the function is heavily dependent on the html layout of https://www.amazonaws.cn/en/sagemaker/pricing/.
        If the webpage layout changes, function might break.
"""


def get_china_region_mapping(region_map):
    china_region_url = "https://www.amazonaws.cn/en/sagemaker/pricing/"
    china_region_webpage = BeautifulSoup(
        urllib.request.urlopen(china_region_url).read(),
        "html.parser",
    )

    def get_china_region_instance_list(region_map, region_name):
        region_section = china_region_webpage.find("h3", id=region_name).parent
        region_training_section = region_section.find(
            "h3", id="Model_Training"
        ).parent.parent

        region_map["regions"][region_name] = []

        # find all texts starting with the string 'ml.'
        instance_names = region_training_section(text=re.compile(r"^ml\.*"))
        if not instance_names:
            raise ValueError(
                f"Could not find any instance name. HTML layout of {china_region_url} might be changed."
            )

        for instance_name in instance_names:
            region_map["regions"][region_name].append({"instance_name": instance_name})

        return region_map

    # Add any new China regions below. Please make sure region_name exists as id of relevant h3 tag in
    # webpage (see get_china_region_instance_list() function)
    region_map = get_china_region_instance_list(region_map, region_name="Beijing")
    region_map = get_china_region_instance_list(region_map, region_name="Ningxia")

    return region_map


"""
Function to set region-instance mapping under host_region_mapping.json
"""


def set_region_mapping():
    region_map = {"regions": {}}
    region_map = get_classic_region_mapping(region_map)
    region_map = get_china_region_mapping(region_map)

    with open(
        "amazon_sagemaker_jupyter_scheduler/host_region_mapping.json", "w"
    ) as mapping_file:
        mapping_file.write(json.dumps(region_map, indent=4))
        print("region mapping updated under host_region_mapping.json")


set_region_mapping()
