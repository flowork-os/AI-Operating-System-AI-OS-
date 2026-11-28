/* libc behavior an application depends on, one function per libc call. */
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

long parse_long(const char *text, int base) { return strtol(text, NULL, base); }
int parse_int(const char *text) { return atoi(text); }
double parse_double(const char *text) { return strtod(text, NULL); }
size_t span(const char *text, const char *accept) { return strspn(text, accept); }
int compare(const char *a, const char *b) {
    int c = strcmp(a, b);
    return (c > 0) - (c < 0);
}
int is_alpha(int c) { return isalpha(c) != 0; }
int is_space(int c) { return isspace(c) != 0; }
int is_punct(int c) { return ispunct(c) != 0; }
int to_upper(int c) { return toupper(c); }
