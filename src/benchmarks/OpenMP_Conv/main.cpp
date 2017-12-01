#include <stdio.h>
#include <omp.h>
#include <stdlib.h>
#include <sys/time.h>

#include "convolve.h"
#include "net_specs.h"

#define INPUTSZ(OPSZ, S, K) (K + (OPSZ-1)*S)
#define RANGE (100)
// Use values from net_spec.h
#define PARAMS ::hyperparameters
#define NUM_LAYERS ::num_layers
#define DATA_T float

int main()
{	
	printf("Running!\n\r");
	// Allocate space for each layer
	DATA_T * layer_inputs= NULL;
	DATA_T * final_output = NULL;
	DATA_T * layer_weights = NULL;
	int input_size = 0;
	int weights_size = 0;
	for (int i = 0; i < NUM_LAYERS; i ++)
	{
		// Find input map row and col size from output row and column
		// INPUTSZ takes arguments Output Row/Col, Stride, and Kernel size (in that order)
		int IR = INPUTSZ(PARAMS[i][2], PARAMS[i][5], PARAMS[i][4]);
		int IC = INPUTSZ(PARAMS[i][3], PARAMS[i][5], PARAMS[i][4]);
		// Size of input for layer is number of input maps times input row and col size
		input_size += PARAMS[i][0]*IR*IC;
		// Number of input time number of output maps times size of kernel on each side
		weights_size += PARAMS[i][0] * PARAMS[i][1] * PARAMS[i][4] * PARAMS[i][4];
	}
	// Just need one buffer for output since all the intermediate layers can just write in to 
	// the next input buffer space.
	// Final output size is number of output maps times output row and col sizes
	int final_output_size = PARAMS[NUM_LAYERS-1][1] * 
							PARAMS[NUM_LAYERS-1][2] * 
							PARAMS[NUM_LAYERS-1][3];
	// Allocate some big 'ol arrays (filled with zeroes for the input and output maps)
	printf("Allocating flat arrays for inputs, weights, and outputs.\n");
	printf("Size of inputs array is %dx%d bytes.\n", input_size, (int)sizeof(DATA_T));
	layer_inputs = (DATA_T*) calloc(input_size, sizeof(DATA_T));
	if (layer_inputs == NULL)
	{
		fprintf(stderr, "ERROR: could not allocate inputs array.\n");
		return EXIT_FAILURE;
	}
	printf("Size of output array for last layer is %dx%d bytes.\n", final_output_size, (int)sizeof(DATA_T));
	final_output = (DATA_T*) calloc(final_output_size, sizeof(DATA_T));
	if (final_output == NULL)
	{
		fprintf(stderr, "ERROR: could not allocate output array.\n");
		return EXIT_FAILURE;
	}
	printf("Size of weights array is %dx%d bytes.\n", weights_size, (int)sizeof(DATA_T));
	layer_weights = (DATA_T*) malloc(weights_size * sizeof(DATA_T));
	if (layer_weights == NULL)
	{
		fprintf(stderr, "ERROR: could not allocate weights array.\n");
	}
	printf("\n");

	// Generate random weights:
	for (int i = 0; i < weights_size; i++)
	{
		layer_weights[i] = (((DATA_T)(rand()%RANGE))/RANGE);
	}

	// (Re) calculate the input size for the first layer
	// INPUTSZ takes arguments Output Row/Col, Stride, and Kernel size (in that order)
	int IR_1 = INPUTSZ(PARAMS[0][2], PARAMS[0][5], PARAMS[0][4]);
	int IC_1 = INPUTSZ(PARAMS[0][3], PARAMS[0][5], PARAMS[0][4]);
	// Number of input maps times row and column of input map
	int first_layer_size = PARAMS[0][0]*IR_1*IC_1;
	// Generate some random inputs for the first layer:
	for (int i = 0; i < first_layer_size; i++)
	{
		layer_inputs[i] = (((DATA_T)(rand()%RANGE))/RANGE);
	}

	int input_offset = 0;
	int output_offset = 0;
	int weight_offset = 0;
	// Execute each layer in sequence
	for (int il = 0; il < NUM_LAYERS; il++)
	{
		printf("Starting layer %d.\n\r", il);
		// Num output maps
		int M = PARAMS[il][1];
		// Num input maps
		int N = PARAMS[il][0];
		// Size of output row
		int R = PARAMS[il][2];
		// Size of output col
		int C = PARAMS[il][3];
		// Stride size
		int S = PARAMS[il][5];
		// Weights size
		int K = PARAMS[il][4];
		printf("Layer has hyperparameters:\n");
		printf("Input Feature Maps (N): %d\n", N);
		printf("Output Feature Maps (M): %d\n", M);
		printf("Output Row (R): %d\n", R);
		printf("Output Col (C): %d\n", C);
		printf("Kernel Filter Dimensions (K): %d\n", K);
		printf("Stride (S): %d\n", S);
		// Row and column of current input layer
		int IR = INPUTSZ(PARAMS[il][2], PARAMS[il][5], PARAMS[il][4]);
		int IC = INPUTSZ(PARAMS[il][3], PARAMS[il][5], PARAMS[il][4]);
		printf("Input Row (IR): %d\n", IR);
		printf("Input Col (IC): %d\n", IC);
		printf("\n");

		// Use the output array for the last layer
		// else use the input array space
		if (il == NUM_LAYERS-1)
		{
			printf("Input Offset: %d\n", input_offset);
			printf("Output Offset: %d\n", 0);
			printf("Weights Offset: %d\n", weight_offset);
			ompConvolve(
				layer_inputs+input_offset, 
				final_output, 
				layer_weights+weight_offset, M, N, R, C, S, K);
		}
		else
		{
			// Output offset is just the size of the current input layer:
			// (since the size of the current input is the size of the previous output)
			output_offset = PARAMS[il][0]*IR*IC;
			printf("Input Offset: %d\n", input_offset);
			printf("Output Offset: %d\n", input_offset+output_offset);
			printf("Weights Offset: %d\n", weight_offset);
			ompConvolve(
				layer_inputs+input_offset, 
				layer_inputs+input_offset+output_offset, 
				layer_weights+weight_offset, M, N, R, C, S, K);
		}
		// Size of input for layer is number of input maps times input row and col size
		input_offset += output_offset;
		// Weight offset for the next layer is the number of weights for this layer
		// (number of input time number of output maps times the squared kernel size)
		weight_offset += PARAMS[il][0] * PARAMS[il][1] * PARAMS[il][4] * PARAMS[il][4];
		printf("Finished layer %d.\n\r", il);
		printf("\n");
	}
	return 0;
}