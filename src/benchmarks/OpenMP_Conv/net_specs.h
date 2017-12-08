/*
Definition of neural network specifications
*/

// Alexnet has 5 convolution layers
// NOTE: there are max pooling and RELU steps here and there between these,
// but for the purpose of this benchmark they are ignored.
const extern int num_layers=5;
/* Alexnet-derived specs:
Ifm	Ofm	R_O	C_O	R_I	C_I	K	S
3	48	55	55	227	227	11	4
48	128	27	27	31	31	5	1
128	192	13	13	15	15	3	1
192	192	13	13	15	15	3	1
192	128	13	13	15	15	3	1
*/

// Values are ordered as Ifm, Ofm, R_O, C_O, K, S
// R_I and C_I can be derived as needed (and match previous rows anyways)

// Half alexnet size as used in Zhang et al, Shen et al:
const extern int hyperparameters[5][6] = {
	{3, 48, 55, 55, 11, 4},
	{48, 128, 27, 27, 5, 1},
	{128, 192, 13, 13, 3, 1},
	{192, 192, 13, 13, 3, 1},
	{192, 128, 13, 13, 3, 1}
};

// Full alexnet size:
/*const extern int hyperparameters[5][6] = {
	{3, 96, 55, 55, 11, 4},
	{96, 256, 27, 27, 5, 1},
	{256, 384, 13, 13, 3, 1},
	{384, 384, 13, 13, 3, 1},
	{384, 256, 13, 13, 3, 1}
};*/
