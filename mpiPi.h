/* -*- C -*- 

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   Please see COPYRIGHT AND LICENSE information at the end of this file.

   ----- 

   mpiPi.h -- internal mpiP header

   $Id$

*/

#ifndef _MPIPI_H
#define _MPIPI_H

#include <assert.h>
#include <malloc.h>
#include <math.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "mpiPconfig.h"

#ifdef ENABLE_BFD
#include "bfd.h"
#endif

#if !defined(CEXTRACT) && !defined(ENABLE_API_ONLY)
#include <mpi.h>
#include "mpiPi_def.h"
#endif

#include "mpiP-hash.h"
#include "mpiP-callsites.h"
#include "mpiP-mt-stats.h"

#include "mpip_timers.h"

#define MPIPI_HOSTNAME_LEN_MAX 128

#define MPIP_CALLSITE_STATS_COOKIE 518641
#define MPIP_CALLSITE_STATS_COOKIE_ASSERT(f) {assert(MPIP_CALLSITE_STATS_COOKIE==((f)->cookie));}

#ifdef USE_MPI3_CONSTS
typedef const void mpip_const_void_t;
typedef const int mpip_const_int_t;
typedef const char mpip_const_char_t;
typedef const MPI_Datatype mpip_const_datatype_t;
#else
typedef void mpip_const_void_t;
typedef int mpip_const_int_t;
typedef char mpip_const_char_t;
#endif

typedef char mpiPi_hostname_t[MPIPI_HOSTNAME_LEN_MAX];

typedef struct callsite_src_id_cache_entry_t
{
  int id;			/* unique id for this src code/stack location */
  int op;			/* at the lowest level, this is a MPI op */
  char *filename[MPIP_CALLSITE_STACK_DEPTH_MAX];
  char *functname[MPIP_CALLSITE_STACK_DEPTH_MAX];
  int line[MPIP_CALLSITE_STACK_DEPTH_MAX];
  void *pc[MPIP_CALLSITE_STACK_DEPTH_MAX];
}
callsite_src_id_cache_entry_t;

extern h_t *callsite_src_id_cache;

typedef struct _mpiPi_lookup_t
{
  int op;
  char *name;
}
mpiPi_lookup_t;

typedef struct _histogram_entry_t
{
  int op;
  double time;
  long count;
  int comm_size_bin;
  int data_size_bin;
}
mpiPi_histogram_entry_t;

typedef struct _mpiPi_fortran_t {
  size_t in_place;
  size_t bottom;
  size_t status_ignore;
  size_t statuses_ignore;
  size_t status_size;
} mpiPi_fortran_t;

extern mpiPi_lookup_t mpiPi_lookup[];
extern mpiPi_fortran_t mpiPi_fortran;

enum
{ MPIP_MPI_TIME_FMT, MPIP_MPI_TIME_SUMMARY_FMT,
  MPIP_AGGREGATE_TIME_FMT, MPIP_AGGREGATE_COV_TIME_FMT,
  MPIP_AGGREGATE_MESS_FMT, MPIP_AGGREGATE_IO_FMT,
  MPIP_CALLSITE_TIME_SUMMARY_FMT, MPIP_CALLSITE_TIME_RANK_FMT,
  MPIP_CALLSITE_MESS_SUMMARY_FMT, MPIP_CALLSITE_MESS_RANK_FMT,
  MPIP_CALLSITE_IO_SUMMARY_FMT, MPIP_CALLSITE_IO_RANK_FMT,
  MPIP_CALLSITE_TIME_CONCISE_FMT, MPIP_CALLSITE_MESS_CONCISE_FMT,
  MPIP_HISTOGRAM_FMT
};

typedef enum
{ MPIP_REPORT_SCI_FORMAT, MPIP_REPORT_FLT_FORMAT }
MPIP_REPORT_FORMAT_TYPE;

#ifdef ENABLE_BFD
typedef struct SO_INFO
{
  void *lvma;
  void *uvma;
  size_t offset;
  char *fpath;
  bfd *bfd;
  asymbol **syms;
} so_info_t;
#endif

typedef struct _mpiPi_t
{
  int ac;
  char *av[MPIP_COPIED_ARGS_MAX];
  char *toolname;
  char *appName;
  char *appFullName;
  char oFilename[256];
  int tag;
  int procID;
  int rank;
  int size;
  int collectorRank;
#ifndef ENABLE_API_ONLY
  MPI_Comm comm;
  mpiPi_hostname_t hostname;
#endif
  int hostnamelen;
  char *outputDir;
  char *envStr;
  FILE *stdout_;
  FILE *stderr_;

  double cumulativeTime;	/* necessary for pcontrol */
  time_t start_timeofday;
  time_t stop_timeofday;

  /* pcontrol */
  int enabled;
  int enabledCount;

  mpiPi_TIMER timer;
  mpiPi_hostname_t *global_task_hostnames;
  double *global_task_app_time;
  double *global_task_mpi_time;
  double global_app_time;
  double global_mpi_time;
  double global_mpi_size;
  double global_mpi_io;
  double global_mpi_rma;
  long long global_mpi_msize_threshold_count;
  long long global_mpi_sent_count;
  long long global_time_callsite_count;

  int tableSize;
  h_t *global_callsite_stats;
  h_t *global_callsite_stats_agg;
  h_t *global_MPI_stats_agg;

  mpiPi_mt_stat_t task_stats;

  mpiPi_lookup_t *lookup;

  int reportStackDepth;
  int internalStackDepth;
  int fullStackDepth;
  double reportPrintThreshold;
  int baseNames;
  MPIP_REPORT_FORMAT_TYPE reportFormat;
  int calcCOV;
  int do_lookup;
  int inAPIrtb;
  int messageCountThreshold;
  long text_start;
  int obj_mode;
  int printRankInfo;
  enum mpiPi_report_style
  { mpiPi_style_verbose, mpiPi_style_concise, mpiPi_style_both } report_style;
  int print_callsite_detail;
  int collective_report;
#ifdef SO_LOOKUP
  so_info_t **so_info;
  int so_count;
#endif
  int disable_finalize_report;

  int do_collective_stats_report;
  double coll_time_stats[MPIP_NFUNC][MPIP_COMM_HISTCNT][MPIP_SIZE_HISTCNT];
  int do_pt2pt_stats_report;
  double pt2pt_send_stats[MPIP_NFUNC][MPIP_COMM_HISTCNT][MPIP_SIZE_HISTCNT];
}
mpiPi_t;

extern mpiPi_t mpiPi;

extern int mpiPi_vmajor;
extern int mpiPi_vminor;
extern int mpiPi_vpatch;
extern char *mpiPi_vdate;
extern char *mpiPi_vtime;

extern int mpiPi_debug;
extern int mpiPi_do_demangle;

#ifdef HAVE_MPIR_TOPOINTER
extern void *MPIR_ToPointer (int idx);
#endif

#if !defined(UNICOS_mp)

/*  AIX  */
#if defined(AIX)

#if defined(__64BIT__)		/*  64-bit AIX  */
#define ParentFP(jb) ((void *) *(long *) jb[5])
#else /*  32-bit AIX  */
#define ParentFP(jb) ((void *) *(long *) jb[3])
#endif

/*  For both 32-bit and 64-bit AIX  */
#define FramePC(fp) ((void *) *(long *) (((long) fp) + (2 * sizeof (void *))))
#define NextFP(fp) ((void *) *(long *) fp)

/*  IA32 Linux  */
#elif defined(Linux) && defined(IA32)
#define ParentFP(jb) ((void*) jb[0].__jmpbuf[3])
#define FramePC(fp) ((void*)(((void**)fp)[1]))
#define NextFP(fp) ((void*)((void**)fp)[0])

/*  X86_64 Linux  */
#elif defined(Linux) && defined(X86_64)
#define ParentFP(jb) ((void*) jb[0].__jmpbuf[1])
#define FramePC(fp) ((void*)(((void**)fp)[1]))
#define NextFP(fp) ((void*)((void**)fp)[0])

/*  BG/L  */
#elif defined(ppc64)
#define ParentFP(jb) NextFP(((void*)jb[0].__jmpbuf[0]))
#define FramePC(fp) ((void*)(((char**)fp)[1]))
#define NextFP(fp) ((void*)((char**)fp)[0])

/* Catamount */
#elif defined(Catamount) && defined(X86_64)
#define ParentFP(jb) ((void*) jb[0].__jmpbuf[1])
#define FramePC(fp) ((void*)(((void**)fp)[1]))
#define NextFP(fp) ((void*)((void**)fp)[0])

/* MIPS+GCC */
/* We don't use the macros on the mips and instead
 * use gcc's __builtin_return_address(0) intrinsic
 * to get a single level of stack backtrace. The
 * value is saved in saved_ret_addr variable each time
 * setjmp is called.
 */
#elif defined(mips) && defined(__GNUC__)
#define ParentFP(jb) (0)
#define FramePC(fp) (0)
#define NextFP(fp) (0)
extern void *saved_ret_addr;


/*  undefined  */
#else
#if ! (defined(HAVE_LIBUNWIND) || defined(USE_BACKTRACE))

#warning "No stack trace mechanism defined for this platform."
#endif
#define ParentFP(jb) (0)
#define FramePC(fp) (0)
#define NextFP(fp) (0)
#endif

#else /* defined(UNICOS_mp) */

#include <intrinsics.h>
#include <stdint.h>

/*
 * Cray X1
 * Stacks grow downward in the address space.
 */


/*
 * Unlike some of the other platforms, we do not use setjmp to obtain
 * the frame pointer of the current function.  Instead, we use the
 * Cray intrinsic function _read_fp() to get the frame pointer of the 
 * current function.
 */
#define GetFP()    ((void*)(_read_fp()))


/* 
 * Given a frame pointer for a callee, the caller's frame pointer is at the 
 * callee's frame pointer address.
 */
#define NextFP(fp)      ((void*)((void**)fp)[0])


/*
 * Given a frame pointer for a callee, the return address to the caller
 * is two elements in the callee's frame.

 * TODO try masking off the high 32-bits
 */
#define FramePC(fp)     ((void*)(((uint64_t)(((void**)fp)[-2])) & 0xFFFFFFFF))


#endif /* defined(UNICOS_mp) */


#define min(x,y) ((x<y)?(x):(y))
#define max(x,y) ((x>y)?(x):(y))

#include "mpiPi_proto.h"

#endif

/*
  
  <license>
  
  Copyright (c) 2006, The Regents of the University of California. 
  Produced at the Lawrence Livermore National Laboratory 
  Written by Jeffery Vetter and Christopher Chambreau. 
  UCRL-CODE-223450. 
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

/* EOF */
