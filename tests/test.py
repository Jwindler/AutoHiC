import json
from collections import defaultdict
from tests.error import ERRORS

info_file = "/home/jzj/Jupyter-Docker/Download/test.json"
classes = ("translocation", "inversion", "debris", "chromosome")
temp_class = ERRORS(classes, info_file)

with open("/home/jzj/Jupyter-Docker/Download/score_filtered_errors.json", "r") as outfile:
    score_filter = json.load(outfile)

overlap_filtered_errors = temp_class.de_diff_overlap(score_filter, iou_score=0.8)
with open("/home/jzj/Downloads/overlap_filtered_errors.json", "w") as outfile:
    json.dump(overlap_filtered_errors, outfile)

translocation_queue, inversion_queue, debris_queue = dict(), dict(), dict()

for tran_error in overlap_filtered_errors["translocation"]:
    translocation_queue[tran_error["id"]] = {  # 存在一个 key 对应多个 value
        "start": tran_error["hic_loci"][0],
        "end": tran_error["hic_loci"][1],
    }
with open("/home/jzj/Downloads/new_tran_error.json", "w") as outfile:
    json.dump(translocation_queue, outfile)

for inv_error in overlap_filtered_errors["inversion"]:
    inversion_queue[inv_error["id"]] = {
        "start": inv_error["hic_loci"][0],
        "end": inv_error["hic_loci"][1],
    }
with open("/home/jzj/Downloads/new_inv_error.json", "w") as outfile:
    json.dump(inversion_queue, outfile)

for deb_error in overlap_filtered_errors["debris"]:
    debris_queue[deb_error["id"]] = {
        "start": deb_error["hic_loci"][0],
        "end": deb_error["hic_loci"][1],
    }
with open("/home/jzj/Downloads/new_deb_error.json", "w") as outfile:
    json.dump(debris_queue, outfile)
