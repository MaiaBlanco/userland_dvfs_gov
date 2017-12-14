/* 
	Author: Mark Blanco
	Copyright: Carnegie Mellon University
	Date: 12 December 2017
*/

/* benchmark to test the time taken for the following:
integer add (ADD)
integer mult (MUL)
float add (VADD{cond}.F32 {Sd,} Sn, Sm)
float mult (VMUL{cond}.F32 {Sd,} Sn, Sm)
float multiply accumulate (VLMA{cond}.F32 Sd, Sn, Sm)
fused multiply accumulate (VFMA{cond}.F32 {Sd,} Sn, Sm)

http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0068b/CIHEDHIF.html
http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0553a/CHDHHAJF.html
*/
/* C++ incudes... */
#include <chrono>
#include <iostream>
/* c includes... */
#include <stdio.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>
/* Other includes, e.g. PAPI...*/
#include <papi.h>
// #include <asm.h>

// Target number of cycles for each instruction
#define CYCLES 10000
#define ARRAY_SIZE 100000
#define MICROSECONDS 10000000

// Namespaces:
using namespace std::chrono;

// Prototypes:
void HandlePAPIError(int retval);

int main()
{
	duration<double> elapsed;
	high_resolution_clock::time_point start, end;
	int papi_retval, event_set=PAPI_NULL;
	// NOTE: size of papi_event_values must be increased when
	// more events are added.
	long long papi_event_values[2];
	
	// initialize the performance API (PAPI):
	papi_retval = PAPI_library_init(PAPI_VER_CURRENT);
	if ( papi_retval < 0)
	{
		std::cerr << "ERROR: could not initialized PAPI.\n";
		exit(1);
	}
	
	// Print out PAPI information
	std::cout << "PAPI Version Number:\n";
	std::cout << PAPI_VERSION_MAJOR(papi_retval) << "." 
		<< PAPI_VERSION_MINOR(papi_retval) << "." 
		<< PAPI_VERSION_REVISION(papi_retval) << "\n";
	
	// Initialize event set for PAPI cycles tracking:
	if (PAPI_create_eventset(&event_set) != PAPI_OK)
		HandlePAPIError(1);
	
	// Add total instructions executed to event set:
	if (PAPI_add_event(event_set, PAPI_TOT_INS) != PAPI_OK)
		HandlePAPIError(1);
	
	// Add total cycles to the event set:
	if (PAPI_add_event(event_set, PAPI_TOT_CYC) != PAPI_OK)
		HandlePAPIError(1);

	// Onto business -- benchmarking.
	printf("Benchmarking operations...\n\r");
	int a[ARRAY_SIZE] = {0};
	int b[ARRAY_SIZE] = {20};
	float fa[ARRAY_SIZE] = {0.0};
	float fb[ARRAY_SIZE] = {20.0};
	
	printf("Doing float MAC.\n\r");	
	
	start = high_resolution_clock::now();
	
	// Start papi counters:
	if (PAPI_start(event_set) != PAPI_OK)
		HandlePAPIError(1);
	for (unsigned long j = 0; j < CYCLES; j++)
	{
		for (unsigned long i = 0; i < ARRAY_SIZE; i++)
		{
			fa[i] += fb[i] * fb[i];
		}
	}

	if (PAPI_stop(event_set, papi_event_values) != PAPI_OK)
		HandlePAPIError(1);
		
	end = high_resolution_clock::now();
	elapsed = duration_cast<duration<double>>(end-start);
	std::cout << "Performed " << ARRAY_SIZE * CYCLES << " " << sizeof(float)*8 << "-bit" << 
			" fMAC operations in " << elapsed.count() << " seconds." << std::endl;
	std::cout << "PAPI instructions: " << papi_event_values[0] << std::endl; 
	std::cout << "PAPI cycles: " << papi_event_values[1] << std::endl;
	std::cout << "IPC: " << float(papi_event_values[0])/float(papi_event_values[1]) << std::endl;
	std::cout << "Overall throughput: " << 2*float(ARRAY_SIZE * CYCLES)/elapsed.count() << " FLOP/s" << std::endl;


	if (PAPI_reset(event_set) != PAPI_OK)
		HandlePAPIError(1);
	std::cout << "Resting for " << float(MICROSECONDS)/1000000 << " seconds.\n";
	usleep(MICROSECONDS);

	printf("Doing int MAC\n\r");
	
	start = high_resolution_clock::now();
	
	if (PAPI_start(event_set) != PAPI_OK)
		HandlePAPIError(1);
	
	for (unsigned long j = 0; j < CYCLES; j++)
	{
		for (unsigned long i = 0; i < ARRAY_SIZE; i++)
		{
			a[i] += b[i] * b[i];
		}
	}

	if (PAPI_stop(event_set, papi_event_values) != PAPI_OK)
		HandlePAPIError(1);

	end = high_resolution_clock::now();
	elapsed = duration_cast<duration<double>>(end-start);
	std::cout << "Performed " << ARRAY_SIZE * CYCLES << " " << sizeof(int)*8 << "-bit" << 
			" iMAC operations in " << elapsed.count() << " seconds." << std::endl;
	std::cout << "PAPI instructions: " << papi_event_values[0] << std::endl; 
	std::cout << "PAPI cycles: " << papi_event_values[1] << std::endl;
	std::cout << "IPC: " << float(papi_event_values[0])/float(papi_event_values[1]) << std::endl;
	std::cout << "Overall throughput: " << 2*float(ARRAY_SIZE * CYCLES)/elapsed.count() << " FLIP/s" << std::endl;

	std::cout << "Completed multiply accumulate tests." << std::endl;

	std::cout << "Resting for " << float(MICROSECONDS)/1000000 << " seconds.\n";
	usleep(MICROSECONDS);

	printf("Doing float ADD\n\r");
	
	start = high_resolution_clock::now();
	
	if (PAPI_start(event_set) != PAPI_OK)
		HandlePAPIError(1);
	
	for (unsigned long j = 0; j < CYCLES; j++)
	{
		for (unsigned long i = 0; i < ARRAY_SIZE; i++)
		{
			fa[i] = fb[i] + fb[i];
		}
	}

	if (PAPI_stop(event_set, papi_event_values) != PAPI_OK)
		HandlePAPIError(1);

	end = high_resolution_clock::now();
	elapsed = duration_cast<duration<double>>(end-start);
	std::cout << "Performed " << ARRAY_SIZE * CYCLES << " " << sizeof(float)*8 << "-bit" << 
			" fADD operations in " << elapsed.count() << " seconds." << std::endl;
	std::cout << "PAPI instructions: " << papi_event_values[0] << std::endl; 
	std::cout << "PAPI cycles: " << papi_event_values[1] << std::endl;
	std::cout << "IPC: " << float(papi_event_values[0])/float(papi_event_values[1]) << std::endl;
	std::cout << "Overall throughput: " << float(ARRAY_SIZE * CYCLES)/elapsed.count() << " FLOP/s" << std::endl;
	
	std::cout << "Resting for " << float(MICROSECONDS)/1000000 << " seconds.\n";
	usleep(MICROSECONDS);

	printf("Doing int ADD\n\r");
	
	start = high_resolution_clock::now();
	
	if (PAPI_start(event_set) != PAPI_OK)
		HandlePAPIError(1);
	
	for (unsigned long j = 0; j < CYCLES; j++)
	{
		for (unsigned long i = 0; i < ARRAY_SIZE; i++)
		{
			a[i] = b[i] + b[i];
		}
	}

	if (PAPI_stop(event_set, papi_event_values) != PAPI_OK)
		HandlePAPIError(1);

	end = high_resolution_clock::now();
	elapsed = duration_cast<duration<double>>(end-start);
	std::cout << "Performed " << ARRAY_SIZE * CYCLES << " " << sizeof(int)*8 << "-bit" << 
			" iADD operations in " << elapsed.count() << " seconds." << std::endl;
	std::cout << "PAPI instructions: " << papi_event_values[0] << std::endl; 
	std::cout << "PAPI cycles: " << papi_event_values[1] << std::endl;
	std::cout << "IPC: " << float(papi_event_values[0])/float(papi_event_values[1]) << std::endl;
	std::cout << "Overall throughput: " << float(ARRAY_SIZE * CYCLES)/elapsed.count() << " FLIP/s" << std::endl;
	return 0;
}


// Helper function definitions ****************



// Papi error handling function (exits program when called)
void HandlePAPIError(int retval)
{
	printf("PAPI ERROR %d: %s\n", retval, PAPI_strerror(retval));
	exit(1);
}
