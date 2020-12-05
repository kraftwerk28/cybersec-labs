#include <stdio.h>
#include <stdlib.h>

int main() {
  srand(0);
  for (size_t i = 0; i < 10; i++) {
    printf("%d\n", rand() % 1000);
  }
}
