from src.common.search_right_site_v8 import search_right_site_v8

hic_file = "/home/jzj/buffer/autohic_tr_bug_fix/rp.2.hic"
assembly_file = "/home/jzj/buffer/autohic_tr_bug_fix/rp.2.assembly"
ratio = 1
error_site = (45100000, 47600000)
modified_assembly_file = "/home/jzj/buffer/test.assembly"

search_right_site_v8(hic_file, assembly_file, ratio, error_site, modified_assembly_file)

print("Done")
