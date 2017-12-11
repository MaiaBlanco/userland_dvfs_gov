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

#include <stdio.h>
#include <unistd.h>
// #include <asm.h>

#define CYCLES 100000000
unsigned int microseconds = 10000000;

int main()
{
	printf("Benchmarking operations...\n\r");
	int a = 0;
	int b = 20;
	int c = 10;
	float fa = 0.0;
	float fb = 20.0;
	float fc = 10.0;
	
	printf("Doing float MAC.\n\r");	
	for (int i = 0; i < CYCLES; i++)
	{
		fa += fb * fc;
	}
		
	usleep(microseconds);

	printf("Doing int MAC\n\r");
	for (int i = 0; i < CYCLES; i++)
	{
		a += b * c;
	}
	// __asm__("MOV ")

	//__asm__("ADD r1,r2,#100");

	//printf("Added! Result is %d\n\r", a);
	printf("Completed float multiply accumulates.\n\r");
	return 0;
}
