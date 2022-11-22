
import json
from collections import defaultdict
from tests.error import ERRORS


with open("/home/swindler/buffer/new_diff_filtered_errors.json", "r") as outfile:
    new_diff = json.load(outfile)
translocation_queue = defaultdict(list)
for tran_error in new_diff["debris"]:
    translocation_queue[tran_error["id"]].append({  # 存在一个 key 对应多个 value
        "start": tran_error["hic_loci"][0],
        "end": tran_error["hic_loci"][1],
    })
with open("/home/swindler/buffer/new_deb_error.json", "w") as outfile:
    json.dump(translocation_queue, outfile)
