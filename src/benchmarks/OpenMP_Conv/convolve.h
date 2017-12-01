// #include <iostream>

#define INPUTIDX(OPIDX, S, idx) (OPIDX*S + idx)
#define INPUTSZ(OPSZ, S, K) (K + (OPSZ-1)*S)
#ifndef DATA_T
#define DATA_T float
#endif


// For accesses to ARRAY[idx3][idx2][idx1][idx0]
#define ARRAY(base, idx3, idx2, idx1, idx0, dim3, dim2, dim1, dim0) \
			(*((base)+\
				(\
					( ( (dim0) * (dim1) * (dim2) ) * (idx3) ) + \
					( ( (dim0) * (dim1) ) * (idx2) ) + \
					( (dim0) * (idx1) ) + \
					(idx0)\
				)\
				)\
			)

// Perform a convolution given the tile data and hyper-parameters
void ompConvolve(float * input, float * output, float * weights, 
	int M, int N, int R, int C, int S, int K)
{
	int R_ifm = INPUTSZ(R, S, K);
	int C_ifm = INPUTSZ(C, S, K);
	for (int in = 0; in < N; in ++)
	{
		#ifdef OMP_COMPILE
		#pragma omp parallel for
		#endif
		for (int im = 0; im < M; im ++)
		{
			for (int ir=0; ir < R; ir++)
			{
				for (int ic = 0; ic < C; ic++)
				{
					float acc = 0;//ARRAY(output, 0, im, ir, ic, 0, M, R, C);
					//#ifdef OMP_COMPILE
					// #pragma omp parallel reduction(+:acc)
					// Don't bother with this one... coordination actually slows it down to 
					// worse than single threaded
					//#endif
					for (int i = 0; i < K; i++)
					{
						for (int j = 0; j < K; j++)
						{
							acc +=
							ARRAY(input, 0, in, INPUTIDX(ir, S, i), INPUTIDX(ic, S, j), 0, N, R_ifm, C_ifm)
							* 
							ARRAY(weights, in, im, i, j, N, M, K, K);
						}
					}
					ARRAY(output, 0, im, ir, ic, 0, M, R, C) += acc;
				}
			}
		}
	}
}