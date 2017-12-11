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
// #include <asm.h>

int main()
{
	printf("Benchmarking operations...\n\r");
	int a = 0;
	int b = 20;
	int c = 10;
	float fa = 0.0;
	float fb = 20.0;
	float fc = 10.0;

	// __asm__("MOV ")

	__asm__("ADD $a,$b,$c");

	printf("Added! Result is %d\n\r", a);

	return 0;
}