#include <stdlib.h>
#include <stdio.h>
#include <papi.h>
#include <string.h>

void handle_error (int retval)
{
	printf("PAPI error %d: %s\n", retval, PAPI_strerror(retval) );
	exit(1);
}

int main()
{
	float rtime, ptime, mflips = 1.0;
	long long flpins;
	int retval, i;
	int eventset = PAPI_NULL;
	unsigned int native = 0x0;
	PAPI_event_info_t info;
	PAPI_event_info_t *infostructs;
	char evnt_nm[PAPI_MAX_STR_LEN]  = {'\0'};
	PAPI_hw_info_t *hw_info;

	printf("Found %d PAPI counters!\n", PAPI_num_counters() );
	PAPI_flops(&rtime, &ptime, &flpins, &mflips);
	printf("Flops: %f\n", mflips );
	printf("rtime: %f\n", rtime );
	printf("ptime: %f\n", ptime );

	// Initialize papi:
	retval = PAPI_library_init( PAPI_VER_CURRENT );
	if (retval != PAPI_VER_CURRENT)
	{
		printf("PAPI library init error!\n");
		handle_error(retval);
	}

	// See if preset PAPI_TOT_INS exists
	retval = PAPI_query_event( PAPI_TOT_INS );
	if ( retval != PAPI_OK )
	{
		printf("Booo! No instruction counter!\n");
		handle_error(retval);
	}

	hw_info = PAPI_get_hardware_info();
	if ( hw_info == NULL )
	{
		printf("ERROR: no hw info!\n");
	} else
	{
		printf("Num cores: %d\n", hw_info->cores);
		printf("Model: %s\n", hw_info->model_string);
		printf("Total CPUs: %d\n", hw_info->totalcpus);
	}
	

	// TODO: Rewrite below to start at first event...
	// get preset details:
	retval = PAPI_get_event_info( PAPI_TOT_INS, &info );
	if ( retval != PAPI_OK )
	{
		printf("No event info.\n");
		handle_error(retval);
	}

	if ( info.count > 0 )
	printf("Event is available\n");

	if ( strcmp( info.derived, "NOT_DERIVED") )
		printf("Event is a derived one.");
	
	int evnt_cntr = 0;
	i = PAPI_TOT_INS;
	while ( PAPI_enum_event( &i, PAPI_ENUM_EVENTS) == PAPI_OK )
	{
		evnt_cntr ++;
		retval = PAPI_get_event_info( i, &info );
		if ( retval == PAPI_OK ) 
		{
			PAPI_event_code_to_name( i, evnt_nm );
			if ( info.count > 0 )
			{
				printf("Event %s is available. Count = %d.\n", evnt_nm, info.count);
				printf("Event description:\n");
				printf("%s\n", info.long_descr);
				printf("Component Index: %d\n", info.component_index);
				if ( strcmp( info.derived, "NOT_DERIVED") )
					printf("Event is a derived one.");
				printf("\n");
			} else
			{
			//	printf("Event %s is not available :( \n", evnt_nm);
			}
		}
	}

	printf("There are %d presets after PAPI_TOT_INS.\n", evnt_cntr);
	
/*
	// Create eventset to manage PAPI events
	retval = PAPI_create_eventset( &eventset );
	if ( retval != PAPI_OK ) handle_error(retval);

	// Find first availale event:
	native = PAPI_NATIVE_MASK | 0;
	retval = PAPI_enum_event( &native, PAPI_ENUM_FIRST );
	if ( retval != PAPI_OK ) handle_error(retval);

	// Add the found event to the eventset:
	retval = PAPI_add_event( eventset, native );
	if ( retval != PAPI_OK ) handle_error(retval);

	retval =  PAPI_query_event( PAPI_L1_DCM );
	//if ( retval != PAPI_OK ) handle_error(retval);
	printf("Result: %d\n", retval);
*/

	return 0;
}
