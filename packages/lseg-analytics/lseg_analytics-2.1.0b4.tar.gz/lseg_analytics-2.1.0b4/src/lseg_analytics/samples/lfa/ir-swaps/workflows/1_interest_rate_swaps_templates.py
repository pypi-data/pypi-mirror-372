import pandas as pd
import json
from lseg_analytics.templates.instrument_templates import search, load 
from lseg_analytics.common import SortingOrderEnum
from IPython.display import display

def extract_tag_key(tag):
    return tag.split(":")[0] if ":" in tag else tag

def list_unique_tags(all_swaps):
    unique_tags = set()
    for item in all_swaps:
        tags = item.get("description", {}).get("tags", [])
        for tag in tags:
            key = extract_tag_key(tag)
            unique_tags.add(key)
    return unique_tags

def display_templates(templates):
    unique_tag_keys = list(list_unique_tags(templates))

    rows = []
    for item in templates:
        row = {
            "Space": item.get("location", {}).get("space", ""),
            "Id": item.get("id", ""),
            "Name": item.get("location", {}).get("name", ""),
            "Summary": item.get("description", {}).get("summary", ""),
        }
        tags = item.get("description", {}).get("tags", [])
        tag_dict = {extract_tag_key(tag): tag for tag in tags}
        for key in unique_tag_keys:
            tag_val = tag_dict.get(key, None)
            if tag_val is not None and ":" in tag_val:
                row[key] = tag_val.split(":", 1)[1]
            else:
                row[key] = tag_val
        rows.append(row)

    display(pd.DataFrame(rows))

swap_templates = search(item_per_page= 3, spaces=["LSEG"], space_name_sort_order = SortingOrderEnum.DESC)

display_templates(swap_templates)

swap_templates = search(tags=["instrumentType:VanillaSwap", "currency:USD"], spaces=["LSEG"])

display_templates(swap_templates)

swap_templates = search(tags=["instrumentType:VanillaSwap", "currency:USD", "index:USD_SOFR_ON"],
                        spaces=["LSEG"],
                        item_per_page= 1)

display_templates(swap_templates)

sofr_swap = load(resource_id="LSEG/OIS_SOFR")

print(json.dumps(sofr_swap.definition.as_dict(), indent=4))

sofr_id = swap_templates[0].get("id", None)
print(sofr_id)

sofr_swap = load(resource_id=sofr_id)

print(json.dumps(sofr_swap.definition.as_dict(), indent=4))