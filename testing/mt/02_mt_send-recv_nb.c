#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <unistd.h>  //getopt
#include <string.h>
#include <pthread.h>
#include "mt_common.h"

#define TEST_WIN 50

void send_nb(int tid)
{
  int i, j, count = mt_common_iter();
  double start;
  MPI_Request req[TEST_WIN];
  MPI_Status statuses[TEST_WIN];

  mt_common_sync();

  mt_common_thr_enter(tid);

  MT_COMMON_DBG(tid,"Start");
  for(i=0; i < count; ) {
      int buf;
      start = GET_TS();
      for(j = 0; j < TEST_WIN && i < count; j++, i++) {
          MPI_Isend(&buf, 1, MPI_INT, mt_common_nbr(), tid,
                    MPI_COMM_WORLD, &req[j]);
        }
      mt_common_stat_append(tid, TEST_MPI_ISEND, j, GET_TS() - start);

      start = GET_TS();
      MPI_Waitall(j, req, statuses);
      mt_common_stat_append(tid, TEST_MPI_WAITALL, 1, GET_TS() - start);
    }

  MT_COMMON_DBG(tid,"End");
  mt_common_thr_exit(tid);
}


void recv_nb(int tid)
{
  int i, j, count = mt_common_iter();
  double start;
  MPI_Request req[TEST_WIN];
  MPI_Status statuses[TEST_WIN];

  mt_common_sync();

  mt_common_thr_enter(tid);

  MT_COMMON_DBG(tid,"Start");
  for(i=0; i < count; ) {
      int buf;
      start = GET_TS();
      for(j = 0; j < TEST_WIN && i < count; j++, i++) {
          MPI_Irecv(&buf, 1, MPI_INT, mt_common_nbr(), tid,
                    MPI_COMM_WORLD, &req[j]);
        }
      mt_common_stat_append(tid, TEST_MPI_IRECV, j, GET_TS() - start);

      start = GET_TS();
      MPI_Waitall(j, req, statuses);
      mt_common_stat_append(tid, TEST_MPI_WAITALL, 1, GET_TS() - start);
    }

  MT_COMMON_DBG(tid,"End");
  mt_common_thr_exit(tid);
}

int main(int argc, char **argv)
{
  mt_common_thrptr_t *workers, func_ptr = NULL;
  int i;

  mt_common_init(&argc, &argv);

  workers = calloc(mt_common_nthreads(), sizeof(*workers));
  if( mt_common_rank() % 2 == 0 ) {
      func_ptr = send_nb;
    } else {
      func_ptr = recv_nb;
    }
  for(i=0; i < mt_common_nthreads(); i++) {
      workers[i] = func_ptr;
    }

  mt_common_exec(workers);

  mt_common_fini();

  free(workers);
}

/*

<license>

Copyright (c) 2019      Mellanox Technologies Ltd.
Written by Artem Polyakov
All rights reserved.

This file is part of mpiP.  For details, see http://llnl.github.io/mpiP.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
notice, this list of conditions and the disclaimer below.

* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the disclaimer (as noted below) in
the documentation and/or other materials provided with the
distribution.

* Neither the name of the UC/LLNL nor the names of its contributors
may be used to endorse or promote products derived from this software
without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OF
THE UNIVERSITY OF CALIFORNIA, THE U.S. DEPARTMENT OF ENERGY OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Additional BSD Notice

1. This notice is required to be provided under our contract with the
U.S. Department of Energy (DOE).  This work was produced at the
University of California, Lawrence Livermore National Laboratory under
Contract No. W-7405-ENG-48 with the DOE.

2. Neither the United States Government nor the University of
California nor any of their employees, makes any warranty, express or
implied, or assumes any liability or responsibility for the accuracy,
completeness, or usefulness of any information, apparatus, product, or
process disclosed, or represents that its use would not infringe
privately-owned rights.

3.  Also, reference herein to any specific commercial products,
process, or services by trade name, trademark, manufacturer or
otherwise does not necessarily constitute or imply its endorsement,
recommendation, or favoring by the United States Government or the
University of California.  The views and opinions of authors expressed
herein do not necessarily state or reflect those of the United States
Government or the University of California, and shall not be used for
advertising or product endorsement purposes.

</license>

*/
