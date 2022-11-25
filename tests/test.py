import json
import os

out_path = "/home/jzj/Jupyter-Docker/Download/result/Aa"
with open("/home/jzj/Jupyter-Docker/Download/result/Aa/overlap_filtered_errors.json", "r") as outfile:
    all_filtered_error = json.loads(outfile.read())

classes = ("translocation", "inversion", "debris", "chromosome")
for _class in classes:
    if _class in all_filtered_error.keys():
        divided_error = dict()
        for tran_error in all_filtered_error[_class]:
            divided_error[tran_error["id"]] = {  # 存在一个 key 对应多个 value
                "start": tran_error["hic_loci"][0],
                "end": tran_error["hic_loci"][1],
            }
        with open(os.path.join(out_path, _class + "_error.json"), "w") as outfile:
            json.dump(divided_error, outfile)
    else:
        continue
print("Divide all error category Done")
