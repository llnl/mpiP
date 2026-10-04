/* -*- C -*-

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   Please see COPYRIGHT AND LICENSE information at the end of this file.

   -----

   mpiP-API.c -- mpiP API functions

   $Id$

 */


#include <stdio.h>
#include <setjmp.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "mpiPi.h"
#include "mpiPi_proto.h"
#include "mpiP-API.h"

static int mpiP_api_init = 0;

void
mpiP_init_api ()
{
  char *mpiP_env;

  mpiP_env = getenv ("MPIP");
  if (mpiP_env != NULL && strstr (mpiP_env, "-g") != NULL)
    mpiPi_debug = 1;
  else
    mpiPi_debug = 0;

  mpiPi.stdout_ = stdout;
  mpiPi.stderr_ = stderr;
  mpiP_api_init = 1;
  mpiPi.toolname = "mpiP-API";
  mpiPi.inAPIrtb = 0;
}


int
mpiP_record_traceback (void *pc_array[], int max_stack)
{
  jmp_buf jb;
  int retval;

  if (mpiP_api_init == 0)
    mpiP_init_api ();

  setjmp (jb);

  mpiPi.inAPIrtb = 1;		/*  Used to correctly identify caller FP  */

  retval = mpiPi_RecordTraceBack (jb, pc_array, max_stack);

  mpiPi.inAPIrtb = 0;

  return retval;
}

extern int
mpiP_find_src_loc (void *i_addr_hex, char **o_file_str, int *o_lineno,
		   char **o_funct_str);

int
mpiP_open_executable (char *filename)
{
  if (mpiP_api_init == 0)
    mpiP_init_api ();

  if (access (filename, R_OK | F_OK) != 0)
    return -1;

#ifdef ENABLE_BFD

  if (open_bfd_executable (filename) == 0)
    return -1;

#elif defined(USE_LIBDWARF)

  if (open_dwarf_executable (filename) == 0)
    return -1;

#endif

  return 0;
}


void
mpiP_close_executable ()
{
#ifdef ENABLE_BFD
  close_bfd_executable ();
#elif defined(USE_LIBDWARF)
  close_dwarf_executable ();
#endif
}

/*  Returns current time in usec  */
mpiP_TIMER
mpiP_gettime ()
{
  mpiPi_TIME currtime;

  mpiPi_GETTIME (&currtime);

  return mpiPi_GETUSECS (&currtime);
}

char *
mpiP_get_executable_name ()
{
  int ac;
  char *av[1];

#ifdef Linux
  return getProcExeLink ();
#else
  mpiPi_copy_args (&ac, av, 1);
  if (av[0] != NULL)
    return av[0];
#endif
  return NULL;
}



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



/* eof */
