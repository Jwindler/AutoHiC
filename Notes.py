# juice-box 
java -jar juicebox.jar 


# Juicebox 右下角信息

# 随鼠标实时变化
	assembly（蓝）: 序列长度与位置信息
	assembly（绿）: 序列长度与位置信息
	observed value (O) 
	expected value (E)
	O/E 


# Contig级别信息（Contig变化，则信息变化）
	Feature
	assembly（蓝）:
	assembly（绿）:

	# Contig序号
	Scaffold # = 
	Scaffold name = utg10238

	# Scaffold name的序号，负号代表反向
	Signed scaffold # = -1523 



# 染色体级别的信息（Chr变化，则信息变化）
	Feature
	assembly（蓝）:
	assembly（绿）:

	# 染色体序号
	Superscaffold # = 1

	# 名称以该染色体框内，第一条Congit为准
	Superscaffold name = utg10238



.assembly文件 ，必须包含完整的序列信息，否则无法在Juicebox 中可视化

.hic 文件和 .assembly文件必须保持一致，否从会出现染色体边框和Contig边框出现偏移的情况