#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <unistd.h>  //getopt
#include <string.h>
#include <pthread.h>
#include "mt_common.h"

// Intra-proc synchronization
static pthread_barrier_t barrier;

// MPI-level credentials
int mpi_rank = -1;
int mpi_size = -1;
int mpi_peer = -1;

// Test status
static int thread_mode = 0;
static int thread_cnt = 1;
static int iter_cnt = 1000;
static int test_id = -1;
static int want_help = 0;
static int debug = 0;

double glob_start = 0;

char *mpi_api_names[TEST_MPI_COUNT] =
{
  [TEST_MPI_SEND] = "MPI_Send",
  [TEST_MPI_RECV] = "MPI_Recv",
  [TEST_MPI_ISEND] = "MPI_Isend",
  [TEST_MPI_IRECV] = "MPI_Irecv",
  [TEST_MPI_WAITALL] = "MPI_Waitall",
  [TEST_MPI_BARRIER] = "MPI_Barrier",
};


/* Measure application time */
typedef struct {
  double start;
  double duration;
} test_timings_t;

/* Measure MPI statistics */
typedef struct {
  int count;
  double total_time;
} test_mpi_call_stat_t;

/* Thread data */
typedef struct {
  int tid;
  mt_common_thrptr_t fptr;
} test_thr_data_t;

// Per-thread structures */
MPI_Comm *coll_comms = NULL;
pthread_t *thread_objs = NULL;
test_thr_data_t *thread_ids = NULL;
test_timings_t *thread_times;
test_mpi_call_stat_t *stats_thr[TEST_MPI_COUNT] = { 0 };

test_mpi_call_stat_t stats_glob[TEST_MPI_COUNT] = { 0 };

static void usage(char *progname)
{
  fprintf(stderr, "Usage: %s [parameters]\n", progname);
  fprintf(stderr, "\nParameters are:\n");
  fprintf(stderr, "   -m\tMulti-thread mode\n");
  fprintf(stderr, "   -t\tNumber of threads to use\n");
  fprintf(stderr, "   -n\tNumber of iterations\n");
  fprintf(stderr, "   -d\tEnable debug\n");
}

static void parse_args(int argc, char **argv)
{
  int c = 0, index = 0;
  int opterr = 0;
  while ((c = getopt(argc, argv, "mt:n:v:d")) != -1) {
      switch (c) {
        case 't':
          thread_cnt = atoi(optarg);
          break;
        case 'm':
          thread_mode = 1;
          break;
        case 'n':
          iter_cnt = atoi(optarg);
          break;
        case 'd':
          debug = 1;
          break;
        case 'h':
        default:
          want_help = 1;
        }
    }
}

static void check_args(int argc, char **argv)
{
  char error_str[1024];

  if (want_help) {
      if(0 == mpi_rank) {
          usage(argv[0]);
        }
      goto eexit;
    }

  if( (0 == thread_mode) && (1 < thread_cnt) ) {
      sprintf(error_str, "A single-threaded mode requested with %d (multiple) threads\n", thread_cnt);
      goto eprint;
    }

  if( (0 > thread_mode) ) {
      sprintf(error_str, "MPI_THREAD_MULTIPLE was requested, but it is not supported by MPI implementation\n");
      goto eprint;
    }

  /* All is good */
  return;
eprint:
  if (0 == mpi_rank) {
      printf("ERROR: %s", error_str);
    }
eexit:
  MPI_Finalize();
  exit(1);
}

void mt_common_init(int *argc, char ***argv)
{
  int mpi_thr_required = 1, mpi_thr_provided = -1, i;

  glob_start = GET_TS();

  /* Parse cmdline arguments.
   * Need to do this prior to MPI init to discover requested threading mode.
   */
  parse_args(*argc, *argv);

  /* Initialize MPI */
  if (0 == thread_mode) {
      mpi_thr_required = MPI_THREAD_SINGLE;
    } else {
      mpi_thr_required = MPI_THREAD_MULTIPLE;
    }

  MPI_Init_thread(argc, argv, mpi_thr_required, &mpi_thr_provided);
  if( mpi_thr_required != mpi_thr_provided ){
      thread_mode = -1;
    }

  MPI_Comm_size(MPI_COMM_WORLD, &mpi_size);
  MPI_Comm_rank(MPI_COMM_WORLD, &mpi_rank);
  /* Ensure pairwise exchanges for the send/recv tests */
  mpi_peer = mpi_rank/2*2 + !(mpi_rank % 2);

  pthread_barrier_init(&barrier, NULL, thread_cnt);

  /* Check the arguments and print an error if any */
  check_args(*argc, *argv);

  /* Allocate reuired per-thread structures */
  for(i=0; i < TEST_MPI_COUNT; i++) {
      stats_thr[i] = calloc(thread_cnt, sizeof(*stats_thr[i]));
  }
  thread_ids = calloc(thread_cnt, sizeof(*thread_ids));
  thread_objs = calloc(thread_cnt, sizeof(*thread_objs));
  thread_times = calloc(thread_cnt, sizeof(*thread_times));

  /* If the test is using collectives - need to create communicators */
  coll_comms = calloc(thread_cnt, sizeof(*coll_comms));
  for (i=0; i<thread_cnt; i++) {
      MPI_Comm_dup(MPI_COMM_WORLD, &coll_comms[i]);
  }
}

void mt_common_fini()
{
  int i;
  double duration = 0, dur_max, dur_min, dur_avg, dur_cum;
  double mpi_duration = 0, mpi_dur_max, mpi_dur_min, mpi_dur_avg, mpi_dur_cum;

  memset(stats_glob, 0, sizeof(stats_glob));
  for(i=0; i<TEST_MPI_COUNT; i++){
      test_mpi_call_stat_t buf[mpi_size];
      int j;
      for(j=0; j<thread_cnt; j++) {
          stats_glob[i].count += stats_thr[i][j].count;
          stats_glob[i].total_time += stats_thr[i][j].total_time;
      }
      mpi_duration += stats_glob[i].total_time;
      MPI_Gather(&stats_glob[i], sizeof(stats_glob[i]), MPI_CHAR,
                 buf, sizeof(stats_glob[i]), MPI_CHAR,
                 0, MPI_COMM_WORLD);

      for(j=1; j < mpi_size; j++) {
          stats_glob[i].count += buf[j].count;
          stats_glob[i].total_time += buf[j].total_time;
      }
  }

  MPI_Reduce(&mpi_duration, &mpi_dur_max, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&mpi_duration, &mpi_dur_min, 1, MPI_DOUBLE, MPI_MIN, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&mpi_duration, &mpi_dur_cum, 1, MPI_DOUBLE, MPI_SUM, 0,
             MPI_COMM_WORLD);

  /* Calculate application execution time */
  for(i=0; i<thread_cnt; i++)
    {
      duration += thread_times[i].duration;
    }
  duration += GET_TS() - glob_start;

  MPI_Reduce(&duration, &dur_max, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
  MPI_Reduce(&duration, &dur_min, 1, MPI_DOUBLE, MPI_MIN, 0, MPI_COMM_WORLD);
  MPI_Reduce(&duration, &dur_cum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

  if (0 == mpi_rank) {
      dur_avg = dur_cum / mpi_size;
      mpi_dur_avg = mpi_dur_cum / mpi_size;
      printf("Application runtime statistics:\n");
      printf("Max\t%lf\t%lf\n", dur_max, mpi_dur_max);
      printf("Avg\t%lf\t%lf\n", dur_avg, mpi_dur_avg);
      printf("Min\t%lf\t%lf\n", dur_min, mpi_dur_min);
      printf("Aggr\t%lf\t%lf\n", dur_cum, mpi_dur_cum);

      printf("MPI statistics for mpiP profile verification:\n");
      for(i=0; i<TEST_MPI_COUNT; i++){
          if (!stats_glob[i].count) {
              continue;
          }
          printf("%s: count=%d, total_time=%lf\n",
                 mpi_api_names[i], stats_glob[i].count,
                 stats_glob[i].total_time);
      }
      printf("%s: count=%d, <service calls>\n",
             "MPI_Gather (Rank 0)", TEST_MPI_COUNT);
  }

  free(thread_ids);
  free(thread_objs);
  if (NULL != coll_comms) {
      for (i=0; i<thread_cnt; i++) {
          MPI_Comm_free(&coll_comms[i]);
      }
      free(coll_comms);
  }
  for(i=0; i < TEST_MPI_COUNT; i++) {
      free(stats_thr[i]);
  }

  MPI_Finalize();
}

void mt_common_sync()
{
  pthread_barrier_wait(&barrier);
}

int mt_common_dbg()
{
  return debug;
}

int mt_common_iter()
{
  return iter_cnt;
}
int mt_common_nthreads()
{
  return thread_cnt;
}

int mt_common_rank()
{
  return mpi_rank;
}
int mt_common_size()
{
  return mpi_size;
}
int mt_common_nbr()
{
  return mpi_peer;
}

void mt_common_stat_append(int tid, test_mpi_call_ids_t id,
                           int count, double duration)
{
  stats_thr[id][tid].count += count;
  stats_thr[TEST_MPI_SEND][tid].total_time += duration;
}

void mt_common_thr_enter(int tid)
{
  thread_times[tid].start = GET_TS();
}
void mt_common_thr_exit(int tid)
{
  thread_times[tid].duration = GET_TS() - thread_times[tid].start;
  thread_times[tid].start = 0;
}

void* _mt_common_proxy_thread(void *id_ptr)
{
  test_thr_data_t *tdata = (test_thr_data_t*)id_ptr;
  tdata->fptr(tdata->tid);
  return NULL;
}

void mt_common_exec(mt_common_thrptr_t *workers)
{
  int i;
  /* Create threads with user-specified handlers */
  for(i=0; i < thread_cnt; i++){
      thread_ids[i].tid = i;
      thread_ids[i].fptr = workers[i];
      pthread_create(&thread_objs[i], NULL, _mt_common_proxy_thread,
                     &thread_ids[i]);
  }

  /* Wait for the threads to finish */
  for(i=0; i < thread_cnt; i++){
      pthread_join(thread_objs[i], NULL);
  }
}

MPI_Comm mt_common_comm(int tid)
{
  return coll_comms[tid];
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
