# hic file format 

## Structure

* Header
* Body
    * Matrix
    * Block
* Footer
    * Master index
    * Expected value vectors



## Header

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|Magic|HiC magic string|String|HIC||
|Version|Version number|int|9||
|footerPosition|File position of footer|long|||
|genomeId| Genome identifier (e.g. hg19, mm9, etc)|String|||
|normVectorIndexPosition|  File position for normalization vector index|long|| (ADDED FROM v8)|
|normVectorIndexLength|  Length to read for normalization vector index|long|| (ADDED FROM v8)|

#### Attribute list
*List of key-value pair attributes.  See notes on common attributes below.*

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|nAttributes	|Number of key-value pair attributes|	int|||
||
|*Repeat for each attribute (n = nAttributes)*|||
|key	|Attribute key|	String	|||
|value|Attribute value|		String|||

#### Chromosome list

*List of chromosome name and lengths*

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|nChrs|	Number of chromosomes|int|||		
||
|*Repeat for each chromosome (n = nChrs)*|
|chrName	|Chromosome name	|String|||	
|chrLength|	Chromosome length |	long	|| (CHANGED FROM v8)|

#### Base-pair resolution list

*List of base-pair resolutions*

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|nBpResolutions	|Number of base pair resolutions|	int|||	
||
|*Repeat for each resolution (n = nBpResolutions)*|||
|resBP	|Bin size in base pairs	|int|||	

#### Fragment resolution list

*List of bin sizes for fragment resolution levels*

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|nFragResolutions	|Number of fragment resolutions	|int|||	
||
|*Repeat for each resolution (n = nFragResolutions)*|
|resFrag	|Bin size in fragment units (1, 2, 5, etc)|	int|||

#### Fragment site positions list

*List of fragment site positions per chromosome, in same order as chromosome list above (n = nChrs).  This section absent if nFragResolutions = 0.*

|Field | Description |	Type | Value | V9 change |
|------|------------|------|-------|------|
|nSites|	Number of sites for this chromosome|	int|||	
||
|*Repeat for each site (n = nSites)*|
|sitePosition|	Site position in base pairs|	int|||	





## Body

The **Header** section is followed immediatly by the **Body**, which containe the contact map data for each 
chromosome-chromosome pairing and each  resolution.   





### Matrix metadata

This section contains metadata  for the contact matrices.  It is repeated for all each chromosome-chromosome pair.  
The master index contains an entry for each combination and is used to randomly access a specific
matrix as needed.  The metadata in this section includes an index for data blocks which contain the actual
contact data.  


|Field	|Description|	Type|	Value| v9 Change |
|------|------------|------|-------|--------|
|chr1Idx| Index for chromosome 1.  This is the index into the array of chromosomes defined in the header above.  The first chromosome has index **0**.|	int|||	
|chr2Idx| Index for chromosome 2. |	int	|||
|nResolutions	|Total number of resolutions for this chromosome-chromosome pair, including base pair and fragment resolutions.	|int|||

#### Resolution (zoom level) metadata

*The section below is repeated for each resolution (n = nResolutions)* 

|Field	|Description|	Type|	Value| v9 Change |
|------|------------|------|-------|--------|
|unit|	Distance unit, base-pairs or fragments	|String	|BP or FRAG||
|resIdx	|Index number for this resolution level, an Array index into the bin size list of the header, first element is **0**. |	int|||	
|sumCounts|	Sum of all counts (or scores) across all bins at current resolution.|	float|||	
|occupiedCellCount|	Total count of cells that are occupied.  **Not currently used**|int|0||		
|percent5|	Estimate of 5th percentile of counts among occupied bins. **Not currently used**|float|0||		
|percent95|	Estimate of 95th percentile of counts among occupied bins **Not currently used**|float|0||		
|binSize|	The bin size in base-pairs or fragments	|int|||	
|blockSize			|Dimension of each block in bins.  In v9 interchromosomal blocks are square, so the total number of bins is ```blockSize^2```. But intrachromosomal blocks are rotated and not necessarily square. In this case, blockSize specifies the dimension of the block along the diagonal axis.  See description of grid strcture below|int|||
|blockColumnCount|The number of columns in the grid of blocks. For v9 intrachromosomal block structure, this specifies the number of columns in the grid of blocks along the diagonal. |int|||			
|blockCount|The number of blocks.  Note empty blocks are not stored.|int|||			
||
|*repeat for each block (n = blockCount)|
|blockNumber	|Numeric id for block.  This is the linear position of the block in the grid when counted in row-major order.   ```blockNumber = column * blockColumnCount + row``` where first row and column **0**. **IMPORTANT: block index entries must be ordered by blockNumber**	|int||	
|blockPosition|	File position of the start of the block |	long||	
|blockSizeBytes	|Size of block in bytes| int||	

***End of Matrix metadata section***





### Blocks  

A block represents a square sub-matrix of a contact map.   

***Note: Blocks are indivdually compressed with ZLib***

|Field	|Description|	Type|	Value| v9 Change|
|------|------------|------|-------|---------|
|nRecords	|Number or contact records in this block|	int	||
|binColumnOffset | Column offset for the contact records in this block.  The binColumn value below is relative to this offset.|| int |
|binRowOffset | Row offset for the contact records in this block.  The rowNumber value below is relative to this offset.|| int |
|useFloatContact | Flag indicating the ```value``` field in contact records for this block are recorded with data type ```float```.  If == 1 a ```float``` is used, otherwise type is ```short```| byte ||
|useIntXPos | Flag indicating the ```recordCount``` and ```binColumn``` fields in contact records for this block are recorded with data type ```int```. If == 1 an ```int``` is used, otherwise type is ```short``` | byte || (ADDED FROM v8)|
|useIntYPos | Flag indicating the ```rowCount``` and ```rowNumber``` fields in contact records for this block are recorded with data type ```int```. If == 1 an ```int``` is used, otherwise type is ```short``` | byte || (ADDED FROM v8)|
|matrixRepresentation | Representation of matrix used for the contact records.  If == 1 the representation is a ```list of rows```, if == 2 ```dense```. | byte |
|blockData| The block matrix data.  See descriptions below, also  in the notes section.

##### Block data - list of rows

|Field	|Description|	Type|	Value| v9 Change|
|------|------------|------|-------|--------|
|rowCount | Number or rows. The data type is determined by the ```useIntYPos``` flag above. | int : short || (CHANGED FROM V8)|
||
|*repeat for each row (n = rowCount)*
|rowNumber | Matrix row number, relative to binRowOffset. First row is ```0```. The data type is determined by the ```useIntYPos``` flag above. | int : short || (CHANGED FROM V8)|
|recordCount | Number of records for this row. Row is sparse, zeroes are not recorded. The data type is determined by the ```useIntXPos``` flag above. | int : short || (CHANGED FROM V8)|
||
|*repeat for each contact record (n = recordCount)*|
|binColumn	|Column index relative to binColumnOffset. The data type is determined by the ```useIntXPos``` flag above. |	int : short|| (CHANGED FROM V8)|
|value	|Value (counts or score). The data type is determined by the ```useFloat``` flag above.|	float : short|||	
||
|*End of loop through contact records (n = recordCount)*|
||
|*End of loop through rows (n = rowCount)*|


##### Block data - dense

|Field	|Description|	Type|	Value|
|------|------------|------|-------|
|nRecords | Number of contact records in this block.  | int ||
|w | Width of the dense block.  This can be < the blockSize if the edge columns on either side are zeroes.  See discussion on block representation below | short ||
||
|*repeat for each contact record (n = nRecords)*||
|value	|Value (counts or score). The data type is determined by the ```useFloat``` flag above.  ***Note:  no value is flagged by the value -32768 if data type is short, NaN if data type is float***|	float : short||	

### Footer

| Field |	Description|	Type |	Value | v9 change |
|------|------------|------|-------|-------|
|nBytesV5|	Number of bytes for the “version 5” footer, that is everything up to the normalized expected vectors	|long|| (CHANGED FROM V8)|

#### Master index

| Field |	Description|	Type |	Value |
|------|------------|------|-------|
|nEntries|	Number of index entries|	int||
||	
||*List of index entries (n = nEntries)*||
|key|	A key constructed from the indeces of the two chromosomes for this matrix.  The indeces are defined by the list of chromosomes in the header section with the first chromosome occupying index **0**|String||	
|position	|Position of the start of the chromosome-chromosome matrix record in bytes	|long||	
|size	|Size of the chromosome-chromsome matrix record in bytes.  This does not include the **Block** data.| int||	



#### Expected value vectors

| Field |	Description|	Type |	Value | v9 Change|
|------|------------|------|-------|--------|
|nExpectedValueVectors|	Number of expected value vectors to follow.  These are expected values from the non-normalized observed matrix.| int||	
||
|*List of expected value vectors (n = nExpectedValueVectors)*||
|unit|	Bin units either FRAG or BP.	|String	|FRAG : BP||
|binSize	|Bin (grid) size for this calculation	|int|||	
|nValues	|Size of the vector|	long||	(CHANGED FROM V8)|
||
||*List of expected values (n = nValues)*|
|value	|Expected value|	float||	(CHANGED FROM V8)|
|nChrScaleFactors| Number of chromosome normalization factors| int|||
||
||*List of normalization factors (n = nChrScaleFactors)*|||
|chrIndex|	Chromosome index|	int|||	
|chrScaleFactor|	Chromosome scale factor	|float||CHANGED FROM v8|	



#### Normalized expected value vectors
| Field |	Description|	Type |	Value | v9 Change|
|------|------------|------|-------|---------|
|nNormExpectedValueVectors|	Number of normalized expected value vectors to follow	|int|||	
||
|*List of normalized vectors (n = nNormExpectedValueVectors)*||
|type|	Indicates type of normalization	|String|	VC:KR:INTER_KR:INTER_VC:GW_KR:GW_VC||
|unit	|Bin units either FRAG or BP.	|String|	FRAG : BP||
|binSize|	Bin (grid) size for this calculation	|int|||	
|nValues|	Size of the vector	|long	|| (CHANGED FROM V8)|
||
|*List of expected values (n = nValues)*|
|value	|Expected value	|float||	(CHANGED FROM V8)|
|nChrScaleFactors|Number of normalizatoin factos for this vector||||
||
|*List of normalization factors (n = nChrScaleFactors)*|
|chrIndex|	Chromosome index	|int	|||
|chrScaleFactor|	Chromosome scale factor	|float|| (CHANGED FROM V8)|	




#### Normalization vector index
| Field |	Description|	Type |	Value | v9 change | 
|------|------------|------|-------|---------|
|nNormVectors|	Number of normalization vectors |	int|||
||
|*Repeat for each norm vector (n=  nNormalizationVectors)*|
|type	|Indicates type of normalization	|String|	VC:KR:INTER_KR:INTER_VC:GW_KR:GW_VC||
|chrIdx|	Chromosome index	|int|	||
|unit|	Bin units either FRAG or BP.|	String|	FRAG : BP||
|binSize	|Resolution 	|int|||	
|position|	File position of value array, described below|	long	|||
|nBytes|	Size in bytes of value array	| long	|| (CHANGED FROM V8)|

#### Normalization vector arrays, 1 per normalization vector.

| Field |	Description|	Type |	Value | v9 change | 
|------|------------|------|-------|---------|
|nValues|	Number of values in array|	long||	(CHANGED FROM V8)|
||
|*Normalization vector values (n=  nValues)*|
| value | Norm value | float || (CHANGED FROM V8)|



#### Notes

##### Data types

* Strings are null (0) terminated.  So for example the string "HIC" is represented by 4 bytes [48 49 43 0]
* Other data types are Java
    * short - 16 bit integer
    * int - 32 bit integer
    * long  -  64 bit integer
    * float - 32 bit floating point
    * double - 64 bit floating point
    
##### Attributes

The attributes table in the header can contain an arbitrary number of key-value string pairs.  The **Juicer** tool
inserts one or more of the following attributes.
* "statistics":
* "graphs":
* "software":
* "nviIndex":  reserved for future use
* "nviLength":  reserved for future use

#### Grid structure

Each chr-chr matrix at a given resolution is subdivided into a grid structure of square **blocks**. 
Each block consists of NxN bins, where N is referred to as **blockSize**.  In older versions of the spec,
and in code, this parameter is referred to as **blockBinCount**.

For intra chromosome matrices (chr1 == chr2) only the lower diagonal is stored (row >= column).  The upper diagonal
can be inferred upon reading by tansposition.  


#### Intrachromosomal Block matrix representation

For intrachromosomal matrices, blocks are stored in a rotated manner, with the axes defined along the diagonal and perpendicular to the diagonal. A visual example of this is included at [https://bcm.box.com/v/hic-file-version-9](https://bcm.box.com/v/hic-file-version-9)

Furthermore, the block size increases by a factor of 2 along the anti-diagonal axis, as the number of contacts also decrease further from the diagonal. This allows for a natural and dynamic block size to decrease overall file size.

The spatial unit for a block is a still a ```bin```, which can be still computed from a genomic position with the formula

```bin = floor(position / binSize)```.

The origin of a block is then

```binX = floor(x / binsSize), binY = floor(y / binSize)```

where x and y are genomic positions in either base pairs or fragment number.

To identify the block number data is stored in, we calculate

```
position_along_diagonal = (binX + binY) / 2 / blockBinCount;
position_along_anti_diagonal = log2(1 + Math.abs(binX - binY) / Math.sqrt(2) / blockBinCount);
block_number = position_along_anti_diagonal * blockColumnCount + positionAlongDiagonal
```

Because the 2D heatmap viewers are often at a 45 degree rotation from the representation of the block, it is necessary to identify all the blocks that overlap this region. For a rectangular region spanning binX1 to binX2 and binY1 to binY2, to rotation along the diagonal and antidiagonal correspond to:

```
// pad = position along diagonal
padMin = (binX1 + binY1) / 2 / blockBinCount;
padMax = (binX2 + binY2) / 2 / blockBinCount + 1;

// anti = position along anti diagonal
// UR = upper right corner, LL = lower left corner
antiUR = log2(1 + Math.abs(binX1 - binY2) / Math.sqrt(2) / blockBinCount);
antiLL = log2(1 + Math.abs(binX2 - binY1) / Math.sqrt(2) / blockBinCount);
```
We determine the appropriate boundaries for the anti-diagonal axis.
```
antiMin = Math.min(antiLL, antiUR);
antiMax = Math.max(antiLL, antiUR) + 1;
```
If the diagonal is contained in the viewer, we explicitly set the lower bound along the anti-diagonal axis.
```
if ((binX1 > binY2 && binX2 < binY1) || (binX2 > binY1 && binX1 < binY2)) {
   antiMin = 0;
}
```
This calculates a permissive region for the viewer to ensure all data is captured for the region,
resulting in block numbers defined by the (inclusive) boundaries:
```
for each p in [padMin, padMax]
   for each a in [antiMin, antiMax]
      block_number = a * blockColumnCount + p
```

#### Block matrix representation

The spatial unit for a block is a ```bin```, which can be computed from a genomic position with the formula

```bin = floor(position / binSize)```.

The origin of a block is then 

```floor(x / binsSize), floor(y / binSize)```

where x and y are genomic positions in either base pairs or fragment number, depending on the

* List of rows

The list of rows is a sparse matrix format.  Each row is represented as follows

```rowNumber rowSize [binX1 value1, binX2 value2, ...]``` 

The first row in the matrix has ```rowNumber = 0```.  The highest row number possible is ```blockSize - 1```

* Dense

In dense matrix format all values including zero are output in row major order.  Allowance is made however for the 
possibility that only a sub-matrix of the block is populated, specifically that leading or trailing columns of 
the block might have no contacts (value = 0).   To account for this possibility the maximum column number within the block
which has at least 1 non-zero value is determined, which we will call ```binXMax```.   The width of the block can
then be determined and used to obtain the x and y coordinates in bin units for each value as follows.  

         w = (binXMax - binXOffset + 1);
         row = floor(i / w);
         col = i - row * w;
         binX = binXOffset + col;
         binY = binYOffset + row;


