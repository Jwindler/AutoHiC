split_file = "/home/jzj/buffer/split.txt"

splid_field = []
with open(split_file, "r") as outfile:
    for line in outfile.readlines():
        if line == "\n":
            continue
        else:
            full_name = line.strip()
            temp_line = line.strip().split("_")[-1]
            name = full_name.replace("_" + temp_line, "")
            start = line.strip().split("_")[-1].split("-")[0]
            end = line.strip().split("-")[-1]
            splid_field.append([name, start, end])

output_file = "/home/jzj/buffer/result.txt"
with open(output_file, "w") as outfile:
    for i in splid_field:
        outfile.write(f"{i[0]}\t{i[1]}\t{i[2]}\n")
