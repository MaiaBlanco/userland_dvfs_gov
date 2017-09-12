#include <stdlib.h>
#include <stdio.h>
#include <papi.h>

void handle_error (int retval)
{
	printf("PAPI error %d: %s\n", retval, PAPI_strerror(retval) );
	exit(1);
}

int main()
{
	float rtime, ptime, mflips = 1.0;
	long long flpins;
	printf("Found %d PAPI counters!\n\r", PAPI_num_counters() );
	PAPI_flops(&rtime, &ptime, &flpins, &mflips);
	printf("Flops: %f\n\r", mflips );
	printf("rtime: %f\n\r", rtime );
	printf("ptime: %f\n\r", ptime );

	return 0;
}
