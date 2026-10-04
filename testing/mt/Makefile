
include ../../Defs.mak

HEADERS = mt_common.h

EXE_SRCS =  01_mt_send-recv_b.c     \
        02_mt_send-recv_nb.c    \
        03_mt_barrier.c         \
#        04_mt_dynamic_threads.c 

EXES = ${EXE_SRCS:.c=.exe}

LIBS += -lpthread -L../.. -lmpiP
LDFLAGS += -Wl,-rpath,'$$ORIGIN/../..'

.PHONY: all
all: ${EXES}

mt_common.o : mt_common.c $(HEADERS)
	${CC} ${CFLAGS} ${CPPFLAGS} -c $< -o $@

%.exe : %.c mt_common.o $(HEADERS) 
	${CC} ${CFLAGS} ${CPPFLAGS} $< ${ADD_OBJS} mt_common.o ${ADD_OBJS} -o $@ ${LDFLAGS} ${LIBS}

clean::
	rm -f ${EXES} *.o *.mpiP
