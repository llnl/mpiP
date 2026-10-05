# mpiP 3.6
A light-weight MPI profiler.

## Introduction
mpiP is a light-weight profiling library for MPI applications. Because it only collects statistical information about MPI functions, mpiP generates considerably less overhead and much less data than tracing tools. All the information captured by mpiP is task-local. It only uses communication during report generation, typically at the end of the experiment, to merge results from all of the tasks into one output file.

## Downloading
The current version of mpiP can be accessed at [https://github.com/LLNL/mpiP/releases/latest](https://github.com/LLNL/mpiP/releases/latest).

## New Features & Bug Fixes

Version 3.6 includes the following changes since version 3.5.

### MPI coverage

- Added MPI-4 persistent collective, partitioned communication, and
  `MPI_Isendrecv` wrappers when the selected MPI implementation provides them.
- Collective message histograms now retain call-time information.

### Fortran and build compatibility

- Added Fortran support for `MPI_IN_PLACE`, `MPI_BOTTOM`, `MPI_STATUS_IGNORE`,
  and `MPI_STATUSES_IGNORE`, including status-array translation that respects
  `MPI_STATUS_SIZE`.
- Improved compatibility with older MPICH releases, current GNU Fortran, and
  stricter C99 compiler checks.
- Configure accepts Python, Python 3, or Python 2 and supports reproducible
  wrapper generation without embedded build timestamps or hostnames.

### Source locations and portability

- Updated BFD support for current Binutils releases and improved source lookup
  for executables and shared objects.
- Configure can locate the BFD headers and library associated with the selected
  compiler wrapper.

### Testing

- Added Flux support for the test suite. Slurm `srun` remains the automatic
  choice when available; configure with `--with-launch=flux` to select Flux.
- Corrected RMA and multithreaded tests and added a standalone source-lookup
  check.

### Version 3.5

Version 3.5 introduced multithreaded profiling support, additional MPI-I/O
functions, updated configuration options, and an expanded test suite.

See the ChangeLog for the dated history of these changes.

##  Configuring and Building mpiP
### Dependencies
- MPI installation
- libunwind : for collecting stack traces.  
- binutils : for address to source translation
- glibc backtrace() can also be usef for stack tracing, but source line numbers may be inconsistent.

### Configuration
Several specific configuration flags can be using, as provided by ```./configure -h```.
Standard configure flags, such as CC, can be used for specifying MPI compiler wrapper scripts.
Tests use Slurm's `srun` when it is available. Use `./configure --with-launch=flux`
to run the test suite with Flux instead.

### Build Make Targets
|Target|Effect|
|---|---|
|[default]| Build libmpiP.so|
|all|Build shared library and all tests|
|check|Use dejagnu to run and evaluate tests|

## Using mpiP
Using mpiP is very simple. Because it gathers MPI information through the MPI profiling layer, mpiP is a link time library. That is, you don't have to recompile your application to use mpiP. Note that you might have to recompile to include the '-g' option. This is important if you want mpiP to decode the PC to a source code filename and line number automatically. mpiP will work without -g, but mileage may vary.

### Instrumentation
#### Link Time Instrumentation
Link the mpiP library with an executable. The dependent libraries may need to be specified as well.  If the link command includes the MPI library, order the mpiP library before the MPI library, as in ``` -lmpiP -lmpi```.

#### Run Time Instrumentation
An uninstrumented executable may able to be instrumented at run time by setting the LD_PRELOAD environment variable, as in ```export LD_PRELOAD=[path to mpiP]/libmpiP.so```.  Preloading libmpiP can possibly interfere with the launcher and may need to be specified on the launch command, such as ```srun -n 2 --export=LD_PRELOAD=[path to mpiP]/libmpiP.so [executable]```.

### mpiP Run Time Flags
The behavior of mpiP can be set at run time through the use of the following flags.  Multiple flags can be delimited with spaces or commas.

|Option|	Description|	Default|
|---|---|---|
|-c	| Generate concise version of report, omitting callsite process-specific detail.||
|-d	|Suppress printing of callsite detail sections.||
|-e|Print report data using floating-point format.  |
|-f dir| Record output file in directory \<dir>. |.|
|-g|Enable mpiP debug mode.| disabled|
|-k n |Sets callsite stack traceback depth to <n>.| 1|
|-l|Use less memory to generate the report by using MPI collectives to generate callsite information on a callsite-by-callsite basis.  |
|-n|Do not truncate full pathname of filename in callsites.  |
|-o|Disable profiling at initialization. Application must enable profiling with MPI_Pcontrol().  |
|-p|Point-to-point histogram reporting on message size and communicator used.|
|-r|Generate the report by aggregating data at a single task. |default|
|-s n|Set hash table size to \<n>. |256|
|-t x|Set print threshold for report, where \<x> is the MPI percentage of time for each callsite. |0.0|
|-v|Generates both concise and verbose report output.  |
|-x exe |Specify the full path to the executable.  |
|-y|Collective histogram reporting on message size and communicator used.|
|-z|Suppress printing of the report at MPI_Finalize.  |
	
For example, to set the callsite stack walking depth to 2 and the report print threshold to 10%, you simply need to define the mpiP string in your environment, as in any of the following examples:

```
$ export MPIP="-t 10.0 -k 2" (bash)

$ export MPIP=-t10.0,-k2 (bash)

$ setenv MPIP "-t 10.0 -k 2" (csh)
```

mpiP prints a message at initialization if it successfully finds the MPIP variable.

For more information on mpiP, please see the User Guide in the mpiP distribution.

## License
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
