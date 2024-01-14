#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAX_NUM 10

typedef enum
{
   ADD,
   MULT,
   SUBTRACT,
   DIV,
   NUMBER,
   UNSUPPORTED
} MathOperation;

struct queue {
	double parsed[MAX_NUM];
	int back, population;
};

typedef struct queue Queue;

void IssueBadNumberError()
{
    printf("The string does not represent a floating point number.\n");
    exit(EXIT_FAILURE);
}
void IssueBadOperationError()
{
    printf("The string does not represent a valid operation.\n");
    exit(EXIT_FAILURE);
}

double CalculateFraction(int arg1, int arg2)
{
	return (double)arg1/(double)arg2;
}

double operation(MathOperation op, double v, double v2) {
double result;    
switch (op)
    {
        case ADD:
         result = v+v2;
         break;
	case SUBTRACT:
	 result = v-v2;
	 break;
	case MULT:
	 result = v*v2;
	 break;
	case UNSUPPORTED:
	 IssueBadOperationError();
	 result = 1;
	 break;
    }
}

int LoopTen(int num)
{
	int i=0;
	int ten = 1;
	for (i; i<num; i++) {
		ten = ten * 10;
	}
	return ten;
}	

double StringToDouble(char *str)
{
	double num = 0;
	int truth;
	if (str[0] == '-') {
		truth = 0; }
	else {
		truth = 1; }
	int length = 0;
	int dindex = 0;
	int dcount = 0;
	while (str[length] != '\0') {
		if (str[length] == '-') {
			if (length != 0) {
				return INFINITY;
				 } 
			}
		if (str[length] == '.') {
                        dcount += 1; 
			dindex = length;    
                        }
		if (str[length]>'9') {
			return INFINITY;
		}
		length += 1;
		}
	if (dcount > 1){
		return INFINITY;
	 }
	int i = 0;
	for (i; i < length; i++) {
		if (str[i] == '-') {
			continue;
		}
		if (dcount == 0) {
			num += (str[i] - '0') * LoopTen(length-i-1);
		}
		else {
			if (i > dindex) {
				num += CalculateFraction((str[i] - '0'), LoopTen(i-dindex));
			}
			if (i < dindex) {
				num += (str[i] - '0') * LoopTen(dindex-i-1);
			}
		}
	}
	if (truth == 0) {
		num = num * -1;
	}
	return num;
}

MathOperation GetOperation(char *op)
{
	int i=0;
	int j=0;
	int num_truth = 0;
	while (op[i] != '\0') {
		i += 1;
	}
	for (j; j<i; j++) {
		if (op[j] >= 48 && op[j] <= 57 || op[j] == '.') {
			num_truth = 1;
		}
		else {
			num_truth = 0;
		}
	}
	if (num_truth) {
		return NUMBER;
	}
	if (i > 1) {
		return UNSUPPORTED;
	}
	if (*op == '+') {
		return ADD;
	}
	else if (*op == '-') {
		return SUBTRACT;
	}
	else if (*op == 'x') {
		return MULT;
	}
}

void intialize(Queue *q) {
	q->back = -1;
	q->population = 0;
}

void enqueue(double num, Queue *q) {
	if (q->population>=MAX_NUM) {
		printf("Too many numbers to handle.\n");
		exit(EXIT_FAILURE);
	}
	if (q->back==MAX_NUM-1) {
		q->back=0;
	}
	else {
		q->back++;
	}
	q->parsed[q->back] = num;
	q->population++;
}

double dequeue(Queue *q) {
	if (q->population == 0) {
		printf("No numbers in queue\n");
		exit(EXIT_FAILURE);
	}
	double rv = q->parsed[q->back];
	q->back--;
	q->population--;
	return rv;
}

int main(int argc, char *argv[])
{
    
    double result = 0;
    struct queue *q = malloc(sizeof(Queue));
    intialize(q);
    int op_count = 0;
    int num_count = 0;
    for (int j = 1; j<argc; j++) {
	    if (GetOperation(argv[j]) == NUMBER) {
		    if (StringToDouble(argv[j])==INFINITY) {
			    IssueBadNumberError();
		    }
		    num_count++;
	    }
	    else if (GetOperation(argv[j]) == UNSUPPORTED) {
			    IssueBadOperationError();
	    }
	    else {
		    op_count++;
	    }
    }
    if (num_count != (op_count + 1)) {
	    IssueBadOperationError();
    }
    for (int i = 1; i<(argc); i++) {
	    if (GetOperation(argv[i]) == NUMBER)  {
		    enqueue(StringToDouble(argv[i]), q);
	    }		
	    else {
		    double num2 = dequeue(q);
		    double num1 = dequeue(q);
		    double new = operation(GetOperation(argv[i]), num1, num2);
		    enqueue(new, q);
		}
	}
    result = q->parsed[0];
    printf("The total is %d\n", (int) result);
 
    return 0;
 }
