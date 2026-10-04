dnl Process this file with autoconf to produce a configure script.
dnl $Id$

dnl These two lines disable the cache.
define([AC_CACHE_LOAD], )
define([AC_CACHE_SAVE], )

AC_INIT([mpiP],[3.5])
AC_PREREQ(2.61)
AC_CONFIG_HEADER(mpiPconfig.h)
AC_CONFIG_AUX_DIR(bin)

AC_CANONICAL_TARGET()

AC_PREFIX_DEFAULT(".")
cross_compiling=yes
ac_tool_warned=yes
echo
echo "  Note: mpiP sets cross_compiling to yes to keep configure from failing in"
echo "        the case where test executables would need to be run as a parallel job."
echo


#
#  With specifications
#

AC_ARG_WITH(cc,
	AS_HELP_STRING(--with-cc,Gives the name of the C compiler to use.),
	CC=$withval
)

AC_ARG_WITH(cxx,
	AS_HELP_STRING(--with-cxx,Gives the name of the C++ compiler to use.),
	CXX=$withval
)

AC_ARG_WITH(f77,
	AS_HELP_STRING(--with-f77,Gives the name of the FORTRAN 77 compiler to use.),
	F77=$withval
)

AC_ARG_WITH(launch,
	AS_HELP_STRING(--with-launch=PROGRAM,Specifies the MPI launcher for tests (for example, flux).),
	LAUNCH=$withval
)

AC_ARG_WITH(include,
	AS_HELP_STRING(--with-include,Specifies include directories (-Idir1 -Idir2).),
	CPPFLAGS=$withval
	echo Using extra include directories: $withval
)

AC_ARG_WITH(ldflags,
	AS_HELP_STRING(--with-ldflags,Specifies ld flags (-L/usr/local/lib).),
	LDFLAGS=$withval
	echo Using ld flags: $withval
)
AC_SUBST(LDFLAGS)

AC_SUBST(CFLAGS)
if test -z "${FFLAGS}" ; then
  FFLAGS=${CFLAGS}
fi
AC_SUBST(FFLAGS)

AC_ARG_WITH(libs,
	AS_HELP_STRING(--with-libs,Specifies libraries (-llib1 -llib2).),
	LIBS=$withval
	echo Using extra libraries: $withval
)

AC_ARG_WITH(binutils-dir,
	AS_HELP_STRING(--with-binutils-dir,Base directory of binutils installation.),
	BINUTILS_DIR=$withval
	CPPFLAGS="${CPPFLAGS} -I${BINUTILS_DIR}/include"
	LIBS="-L${BINUTILS_DIR}/lib ${LIBS}"
	echo Using binutils-dir: $withval
	,
	BINUTILS_DIR=/usr
)
AC_SUBST(BINUTILS_DIR)

AC_ARG_WITH(libunwind,
	AS_HELP_STRING(--with-libunwind,Specify location of libunwind to merge.),
	LIBUNWIND_LOC=$withval
	echo Using libunwind: $withval
	,
	LIBUNWIND_LOC=/usr/lib/libunwind.a
)
AC_SUBST(LIBUNWIND_LOC)

AC_ARG_WITH(bin-type-flag,
	AS_HELP_STRING(--with-bin-type-flag,Binary format for AIX ar operations.),
	BIN_TYPE_FLAG=$withval
	echo Using bin-type-flag: $withval
	,
	BIN_TYPE_FLAG=
)
AC_SUBST(BIN_TYPE_FLAG)

#
# Timer options
#
TIMER_OPTION=no
AC_ARG_WITH(gettimeofday,
	AS_HELP_STRING(--with-gettimeofday,Use gettimeofday for timing.),
	AC_DEFINE([USE_GETTIMEOFDAY],[1],[Use gettimeofday for the timer])
        USE_GETTIMEOFDAY=true
	TIMER_OPTION=yes
	,
)

AC_ARG_WITH(wtime,
	AS_HELP_STRING(--with-wtime,Use MPI_Wtime for timing.),
	AC_DEFINE([USE_WTIME],[1],[Use MPI_Wtime for timer])
	TIMER_OPTION=yes
	,
)

AC_ARG_WITH(clock_gettime,
	AS_HELP_STRING(--with-clock_gettime,Use clock_gettime for timing.),
	AC_DEFINE([USE_CLOCK_GETTIME], [1], [Use clock_gettime for timing])
	USE_CLOCK_GETTIME=yes
	TIMER_OPTION=yes
	,
)

AC_ARG_WITH(rts_get_timebase,
	AS_HELP_STRING(--with-rts_get_timebase,Use rts_get_timebase for timing on BG/L systems (default for BG/L).),
	AC_DEFINE([USE_RTS_GET_TIMEBASE],[1],[Use RTS get timebase])
	USE_RTS_GET_TIMEBASE=yes
	TIMER_OPTION=yes
	,
        USE_RTS_TIMEBASE=no
)

AC_ARG_WITH(read_real_time,
	AS_HELP_STRING(--with-read_real_time,Use read_real_time for timing on AIX systems (default for AIX).),
	AC_DEFINE([USE_READ_REAL_TIME], [1], [Use read real time])
	USE_READ_REAL_TIME=yes
	TIMER_OPTION=yes
	,
        USE_READ_REAL_TIME=no
)

AC_ARG_WITH(rtc,
	AS_HELP_STRING(--with-rtc,Use _rtc for timing on CRAY X1 systems (default for X1).),
	AC_DEFINE([USE_RTC], [1], [Use RTC])
	USE_RTC=yes
	TIMER_OPTION=yes
	,
        USE_RTC=no
)

AC_ARG_WITH(dclock,
	AS_HELP_STRING(--with-dclock,Use Catamount dclock for timing.),
	AC_DEFINE([USE_DCLOCK], [1], [Use dlock])
	USE_DCLOCK=yes
	TIMER_OPTION=yes
	,
        USE_DCLOCK=no
)


#
#  Enable / Disable specifications
#

DEFAULT_TARGS='${SHARED_C_TARGET}'
ENABLE_API_ONLY=no
AC_ARG_ENABLE(api-only,
	AS_HELP_STRING(--enable-api-only,Only build the API library.),
	if test x"$enableval" = xyes ; then
		ENABLE_API_ONLY=yes
		echo Configuring for API library only.
		AC_DEFINE([ENABLE_API_ONLY], [1], ["Only build API"])
		DEFAULT_TARGS="API test"
	fi
	,
)


if test "$ENABLE_API_ONLY" = no ; then

ENABLE_MPI_IO=yes
AC_ARG_ENABLE(mpi-io,
	AS_HELP_STRING(--disable-mpi-io,Disable MPI-I/O reporting.),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_IO=no
		echo Profiling of MPI I/O has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_IO)
fi

if test x"$ENABLE_API_ONLY" = xno ; then

ENABLE_MPI_RMA=yes
AC_ARG_ENABLE(mpi-rma,
	AS_HELP_STRING(--disable-mpi-rma,[Disable MPI RMA reporting.]),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_RMA=no
		echo Profiling of MPI RMA has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_RMA)

ENABLE_MPI_NONBLOCKINGCOLLECTIVES=yes
AC_ARG_ENABLE(mpi-nbc,
	AS_HELP_STRING(--disable-mpi-nbc,[Disable MPI NONBLOCKINGCOLLECTIVES reporting.]),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_NONBLOCKINGCOLLECTIVES=no
		echo Profiling of MPI NONBLOCKINGCOLLECTIVES has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_NONBLOCKINGCOLLECTIVES)

ENABLE_MPI_PERSISTENTCOLLECTIVES=yes
AC_ARG_ENABLE(mpi-pcoll,
	AS_HELP_STRING(--disable-mpi-pcoll,[Disable MPI PERSISTENTCOLLECTIVES reporting.]),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_PERSISTENTCOLLECTIVES=no
		echo Profiling of MPI PERSISTENTCOLLECTIVES has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_PERSISTENTCOLLECTIVES)


ENABLE_MPI_ISENDRECV=yes
AC_ARG_ENABLE(mpi-isendrecv,
	AS_HELP_STRING(--disable-mpi-isendrecv,[Disable MPI ISENDRECV reporting.]),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_ISENDRECV=no
		echo Profiling of MPI ISENDRECV has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_ISENDRECV)

ENABLE_MPI_PARTITIONED=yes
AC_ARG_ENABLE(mpi-partitioned,
	AS_HELP_STRING(--disable-mpi-partitioned,[Disable MPI PARTITIONED reporting.]),
	if test x"$enableval" = xno ; then
		ENABLE_MPI_PARTITIONED=no
		echo Profiling of MPI PARTITIONED has been disabled.
	fi
	,
)
AC_SUBST(ENABLE_MPI_PARTITIONED)

dnl end of API conditional
fi

ENABLE_BFD=yes
AC_ARG_ENABLE(bfd,
	AS_HELP_STRING(--disable-bfd,Do not use GNU binutils libbfd for source lookup.),
	if test x"$enableval" = xno ; then
		echo Use of libbfd has been disabled.
		ENABLE_BFD=no SO_LOOKUP=no
	fi
	,
)

DISABLE_LIBUNWIND=no
AC_ARG_ENABLE(libunwind,
	AS_HELP_STRING(--disable-libunwind,Do not use libunwind to generate stack traces.),
	if test x"$enableval" = xno ; then
		DISABLE_LIBUNWIND=yes
		echo Use of libunwind has been disabled.
	fi
	,
)

DISABLE_SO_LOOKUP=no
AC_ARG_ENABLE(so-lookup,
	AS_HELP_STRING(--disable-so-lookup,Disable functionality to attempt to find source info in shared objects.),
	if test x"$enableval" = xno ; then
		DISABLE_SO_LOOKUP=yes
		echo Use of shared object source lookup has been disabled.
	fi
	,
)

USE_SETJMP=no
AC_ARG_ENABLE(setjmp,
	AS_HELP_STRING(--enable-setjmp,Use setjmp instead of glic backtrace() to generate stack traces.),
	if test x"$enableval" = xyes ; then
		USE_SETJMP=yes
    AC_DEFINE([USE_SETJMP], [1], [Use setjmp])
		echo Setjmp will be used to generate stack traces.
	fi
	,
)

AC_ARG_ENABLE(fortranxlate,
	AS_HELP_STRING(--disable-fortranxlate,Disable translation of Fortran opaque objects.),
	if test "$enable_fortranxlate" = "no" ; then
		ENABLE_FORTRAN_XLATE=no
		  echo Translation of FORTRAN opaque objects has been disabled.
	else
		ENABLE_FORTRAN_XLATE=yes
		echo Translation of FORTRAN opaque objects has been enabled.
	fi
	,
	ENABLE_FORTRAN_XLATE=yes
)
AC_SUBST(ENABLE_FORTRAN_XLATE)

ENABLE_FORTRAN_WEAK_SYMS=no
AC_ARG_ENABLE(fortranweak,
        AS_HELP_STRING(--enable-fortranweak,Generate weak symbols for additional Fortran symbol name styles.),
        if test "$enable_fortranweak" = "no" ; then
                ENABLE_FORTRAN_WEAK_SYMS=no
                  echo Generation of additional weak FORTRAN symbol names has been disabled.
        else
                ENABLE_FORTRAN_WEAK_SYMS=yes
                AC_DEFINE([ENABLE_FORTRAN_WEAK_SYMS], [1], [Enable weak symbols for FORTRAN])
                echo Generation of additional weak FORTRAN symbol names has been enabled.
        fi
        ,
        ENABLE_FORTRAN_WEAK_SYMS=no
)
AC_SUBST(ENABLE_FORTRAN_WEAK_SYMS)



AC_ARG_ENABLE(stackdepth,
	AS_HELP_STRING([--enable-stackdepth], [Specify maximum report stacktrace depth (default is 8).]),
	STACKDEPTH=$enableval; 
    echo "Maximum stacktrace depth is $STACKDEPTH",
	STACKDEPTH=8,
)
AC_DEFINE_UNQUOTED([MPIP_CALLSITE_REPORT_STACK_DEPTH_MAX], [$STACKDEPTH], [Stack depth of callsites in report])
AC_SUBST(MPIP_CALLSITE_REPORT_STACK_DEPTH_MAX)

AC_ARG_ENABLE(internal-stackdepth,
	AS_HELP_STRING([--enable-internal-stackdepth], [Specify number of internal stack frames (default is 3).]),
	MPIP_INTERNAL_STACK_DEPTH=$enableval; 
    echo "Internal stacktrace depth is $MPIP_INTERNAL_STACK_DEPTH",
	MPIP_INTERNAL_STACK_DEPTH=3,
)
AC_DEFINE_UNQUOTED([MPIP_INTERNAL_STACK_DEPTH], [$MPIP_INTERNAL_STACK_DEPTH], [Number of internal stack frames])
AC_SUBST(MPIP_INTERNAL_STACK_DEPTH)

AC_DEFINE([MPIP_CALLSITE_STACK_DEPTH_MAX], [(MPIP_CALLSITE_REPORT_STACK_DEPTH_MAX + MPIP_INTERNAL_STACK_DEPTH)], [Recorded stack depth of callsites])
AC_SUBST(MPIP_CALLSITE_STACK_DEPTH_MAX)

AC_ARG_ENABLE(maxargs,
    AS_HELP_STRING(--enable-maxargs,Maximum number of command line arguments copied (default is 32).),
    MPIP_COPIED_ARGS_MAX=$enableval
    echo Maximum number of command line arguments copied is $MPIP_COPIED_ARGS_MAX
    ,
    MPIP_COPIED_ARGS_MAX=32
)
AC_DEFINE_UNQUOTED(MPIP_COPIED_ARGS_MAX, [$MPIP_COPIED_ARGS_MAX], [Maximum number of command line arguments copied])

PC_LOOKUP_FILE=pc_lookup.c
AC_ARG_ENABLE(dwarf,
	AS_HELP_STRING(--enable-dwarf,Use DWARF library for source lookup.),
	if test x"$enableval" = xyes ; then
		echo "Using DWARF library for symbol lookup; forcing --disable-bfd"
		ENABLE_BFD=no
		PC_LOOKUP_FILE=pc_lookup_dwarf.c
	fi ;
	USE_LIBDWARF=yes
	,
	USE_LIBDWARF=no
)
AC_SUBST(USE_LIBDWARF)
AC_SUBST(PC_LOOKUP_FILE)

USE_GETARG=false
AC_ARG_ENABLE(getarg,
	AS_HELP_STRING(--enable-getarg,Use getarg to get fortran command line args.),
	if test x"$enableval" = xyes ; then
		AC_DEFINE([USE_GETARG], [1], [Use getarg])
		echo Use of getarg has been enabled
		USE_GETARG=true
	fi
	,
)
AC_SUBST(USE_GETARG)

AC_ARG_ENABLE(demangling,
	AS_HELP_STRING(--enable-demangling,[Specify GNU, IBM, or Compaq demangling support.]),
	DO_DEMANGLE=$enableval
	echo $DO_DEMANGLE demangling enabled
	,
	DO_DEMANGLE=false
)
AC_SUBST(DO_DEMANGLE)

AC_ARG_ENABLE(check-time,
	AS_HELP_STRING(--enable-check-time,Enable AIX check for negative time values.),
	if test x"$enableval" = xyes ; then
		AC_DEFINE([MPIP_CHECK_TIME], [1], [MPI check time])
		echo AIX negative time value checking has been enabled
	fi
	,
)

AC_ARG_ENABLE(collective-report-default,
	AS_HELP_STRING(--enable-collective-report-default,Have mpiP default to low-memory-use collective report generation as opposed to collecting all data at a single task (see runtime flags -l and -s).),
	if test "x$enableval" = xyes ; then
                AC_DEFINE([COLLECTIVE_REPORT_DEFAULT],[1], ["Use collective reporting by default"])
		echo "Using collective report as default."
	fi
	,
)

AC_DEFINE([DEFAULT_REPORT_FORMAT], [mpiPi_style_verbose], [Default report style])
AC_ARG_ENABLE(concise-report-default,
	AS_HELP_STRING(--enable-concise-report-default,Have mpiP default to a concise summary report format. (see runtime flags -c and -v).),
	if test "x$enableval" = xyes ; then
                AC_DEFINE([DEFAULT_REPORT_FORMAT], [mpiPi_style_concise],[The default format of the report])
		echo "Using concise report as default."
	fi
	,
)

AC_PROG_INSTALL
AC_PROG_RANLIB
if test "x$AR" = "x"; then
   AR=ar
fi

AC_CHECK_PROGS(HAVE_PYTHON,[python python3 python2],[no])
if test "x$HAVE_PYTHON" == "xno" ; then
  AC_MSG_ERROR([Python is required to build mpiP.])
fi
AC_SUBST(HAVE_PYTHON)

TEST_LIST=

#  Test for available compilers
C_IBM_MPI_WRAPPERS="mpixlc"
C_INTEL_MPI_WRAPPERS="mpiicc"
CXX_IBM_MPI_WRAPPERS="mpixlC"
CXX_INTEL_MPI_WRAPPERS="mpiicpc"
F77_IBM_MPI_WRAPPERS="mpixlf"
F77_INTEL_MPI_WRAPPERS="mpiifort"

if test "$ENABLE_API_ONLY" = no ; then
  AC_CHECK_PROGS(CC,  $C_IBM_MPI_WRAPPERS $C_INTEL_MPI_WRAPPERS cmpicc mpcc mpicc gcc cc icc, mpicc)
  AC_CHECK_PROGS(CXX, $CXX_IBM_MPI_WRAPPERS $CXX_INTEL_MPI_WRAPPERS mpiCC mpicxx cmpic++ c++ g++ CC cxx icc, mpicxx)
  AC_CHECK_PROGS(F77, $F77_IBM_MPI_WRAPPERS $F77_INTEL_MPI_WRAPPERS mpifort mpif77 cmpifc xlf f77 g77 pgf77 fort ifc, mpifort)
  AC_CHECK_PROGS(LAUNCH, srun poe jsrun prun flux mpirun mpiexec, mpirun)
else
  AC_CHECK_PROGS(CC, xlc gcc cc icc, mpicc)
  AC_CHECK_PROGS(CXX, xlC c++ g++ CC cxx icc, mpiCC)
  AC_CHECK_PROGS(F77, xlf f77 g77 pgf77 fort ifc, mpif77)
  LAUNCH="\\\"\\\""
  TEST_LIST="api-test.exp"
fi

AC_CHECK_LIB(m,sqrt)

AC_CHECK_SIZEOF(void*)

AC_MSG_CHECKING(PIC flags)
if `$CC -fpic 2>&1 | grep 'warning' >/dev/null 2>&1` ; then
  PIC_FLAGS="-DPIC"
else
  PIC_FLAGS="-fpic -DPIC"
fi
AC_MSG_RESULT($PIC_FLAGS)

#  Check for MPI, but also define AC_CHECK_DECL macro, since the next use
#  would be within the bfd tests, making AC_CHECK_DECL undefined if not
#  checking for bfd.
AC_CHECK_DECL(MPI_Init,,AC_MSG_ERROR(["Failed to find declaration for MPI_Init!"]),[#include "mpi.h"])

SOURCE_LOOKUP=none


if test "x$ENABLE_BFD" = "xyes" ; then
  BFD_AUX_LIBS=
  BFD_CPPFLAGS=
  BFD_LDFLAGS=
  BFD_LIB_FILE=
  BFD_INCLUDE_DIR=
  AC_SEARCH_LIBS([dlopen], [dl dld]) # newer versions of binutils have a libdl dependency
  AC_CHECK_LIB(z,inflate, BFD_AUX_LIBS="$BFD_AUX_LIBS -lz")  # newer versions of binutils have a zlib dependency
  AC_CHECK_LIB(intl,dcgettext__, BFD_AUX_LIBS="$BFD_AUX_LIBS -lintl")  #libintl required only on some platforms, eg AIX
  AC_CHECK_LIB(iberty,objalloc_create, BFD_AUX_LIBS="$BFD_AUX_LIBS -liberty")

  AC_MSG_CHECKING([for libbfd path])
  BFD_LIB_FILE=`$CC -print-file-name=libbfd.a 2>/dev/null`
  if test "x$BFD_LIB_FILE" = "xlibbfd.a" || test ! -f "$BFD_LIB_FILE" ; then
    BFD_LIB_FILE=`$CC -print-file-name=libbfd.so 2>/dev/null`
  fi
  if test "x$BFD_LIB_FILE" = "xlibbfd.so" || test ! -f "$BFD_LIB_FILE" ; then
    BFD_LIB_FILE=
    AC_MSG_RESULT([not found via compiler wrapper])
  else
    AC_MSG_RESULT([$BFD_LIB_FILE])
    BFD_LIB_DIR=`dirname "$BFD_LIB_FILE"`
    BFD_INCLUDE_DIR=`dirname "$BFD_LIB_DIR"`/include
    if test -f "$BFD_INCLUDE_DIR/bfd.h" ; then
      BFD_CPPFLAGS="-I$BFD_INCLUDE_DIR"
      BFD_LDFLAGS="-L$BFD_LIB_DIR"
      AC_MSG_NOTICE([using bfd.h from $BFD_INCLUDE_DIR])
    else
      BFD_INCLUDE_DIR=
    fi
  fi

  mpip_save_CPPFLAGS="$CPPFLAGS"
  mpip_save_LDFLAGS="$LDFLAGS"
  CPPFLAGS="$BFD_CPPFLAGS $CPPFLAGS"
  LDFLAGS="$BFD_LDFLAGS $LDFLAGS"

  AC_CHECK_HEADER(bfd.h,
    AC_CHECK_LIB(bfd,bfd_openr, LIBS="$LIBS -lbfd", ENABLE_BFD=no, $BFD_AUX_LIBS)
    AC_CHECK_DECL(bfd_get_section_size, AC_DEFINE([HAVE_BFD_GET_SECTION_SIZE], [1], [BFD get section size]), ,[#include "bfd.h"])
    AC_CHECK_DECL(bfd_get_section_vma, AC_DEFINE(HAVE_BFD_GET_SECTION_MACROS, [1], [BFD get section macros]), ,[#include "bfd.h"])
    , ENABLE_BFD=no SO_LOOKUP=no
  )
  AC_CHECK_TYPE(bfd_boolean, ,AC_DEFINE([HAVE_BFD_BOOLEAN], [1], [BFD booleans]), [#include "bfd.h"])
  CPPFLAGS="$mpip_save_CPPFLAGS"
  LDFLAGS="$mpip_save_LDFLAGS"
  if test "x$ENABLE_BFD" = "xyes" ; then
    CPPFLAGS="$BFD_CPPFLAGS $CPPFLAGS"
    LDFLAGS="$BFD_LDFLAGS $LDFLAGS"
    AC_CHECK_HEADER(demangle.h, [AC_DEFINE([HAVE_DEMANGLE_H], [1], [Have demangling]) if test "x$DO_DEMANGLE" = xfalse ; then DO_DEMANGLE=GNU ; fi])
    LIBS="$LIBS $BFD_AUX_LIBS"
    AC_DEFINE([ENABLE_BFD], [1], [Enable BFD library for the PC to source lookups])
    SOURCE_LOOKUP=bfd
  fi

else
  if test x$USE_LIBDWARF = xyes ; then
    AC_CHECK_LIB(elf, elf_begin, 
      LIBELF_FOUND=yes, 
      ELFDWARF_ERR="failed to find libelf." ; LIBELF_FOUND=no
      )
    AC_CHECK_LIB(dwarf, dwarf_init, 
      LIBDWARF_FOUND=yes, 
      ELFDWARF_ERR="failed to find libdwarf." ; LIBDWARF_FOUND=no, [-lelf]
      )
    echo $ECHO_N "checking for libelf/libdwarf..." $ECHO_C
    if test x$LIBELF_FOUND = xyes -a x$LIBDWARF_FOUND = xyes ; then
      LIBS="${LIBS} -ldwarf -lelf"
      AC_DEFINE([USE_LIBDWARF], [1], [Use libdwarf])
      echo " found libelf/libdwarf"
      SOURCE_LOOKUP=libelf/libdwarf
      SO_LOOKUP=no
    else
      echo " $ELFDWARF_ERR Not using libelf/libdwarf"
    fi
  fi
fi

if test "$ENABLE_API_ONLY" = no ; then
  AC_CHECK_LIB(mpi,MPIR_ToPointer,AC_DEFINE([HAVE_MPIR_TOPOINTER], [1], [Have MPIR to pointer]),)
  AC_CHECK_LIB(mpich,MPIR_ToPointer,AC_DEFINE([HAVE_MPIR_TOPOINTER],[1], [Have MPIR to pointer]),)
fi

#  Check for MPI3
AC_COMPILE_IFELSE(
    [AC_LANG_PROGRAM([@%:@include <mpi.h>],
        [ #if MPI_VERSION < 3
          # error not using MPI3
          #endif
        ])
    ],
    AC_DEFINE([USE_MPI3_CONSTS],[1],[Use MPI v3 constructions]))

AC_PATH_PROG([MPICHVERSION], [mpichversion])
if test -n "$MPICHVERSION" ; then
  AC_MSG_CHECKING([whether MPICH requires -lmpifort])
  mpich_major_version=`$MPICHVERSION 2>/dev/null | grep -i 'version:' | head -n 1 | cut -d: -f2 | cut -d. -f1 | sed 's/^ *//'`
  if test -n "$mpich_major_version" && test "$mpich_major_version" -lt 3 ; then
    case " $LIBS " in
      *" -lmpifort "*) AC_MSG_RESULT([no, already present]) ;;
      *) LIBS="$LIBS -lmpifort"
         AC_MSG_RESULT([yes]) ;;
    esac
  else
    AC_MSG_RESULT([no])
  fi
fi


#
#  Find an appropriate timer function
#

TIMER_FOUND=no
TIMER_NAME=none

# use rts_get_timebase (BG/L) by default if it exists
if test x$TIMER_FOUND = xno && \
  (test x$TIMER_OPTION = xno || test x$USE_RTS_GET_TIMEBASE = xyes); then
AC_CHECK_FUNC(rts_get_timebase, AC_DEFINE([USE_RTS_GET_TIMEBASE], [1], [Use RTS get timebase])
        USE_RTS_GET_TIMEBASE=yes ; TIMER_FOUND=yes ; TIMER_NAME="rts_get_timebase (assuming 700MHz)" ; AC_SUBST(USE_RTS_GET_TIMEBASE)
        )
fi

# use _rtc (Cray X1) by default if it exists
if test x$TIMER_FOUND = xno && \
  (test x$TIMER_OPTION = xno || test x$USE_RTC = xyes); then
AC_CHECK_DECL(_rtc, AC_DEFINE([USE_RTC], [1], [Use RTC])
        USE_RTC=yes ; TIMER_FOUND=yes ; TIMER_NAME=_rtc ; AC_SUBST(USE_RTC)
        , , [#include <intrinsics.h>])
fi

READ_REAL_TIME=read_real_time
## On AIX, prefer monotonic mread_real_time, if available
if test x$TIMER_FOUND = xno && test x$TIMER_OPTION = xno ; then
  AC_CHECK_FUNC(mread_real_time, READ_REAL_TIME=mread_real_time TIMER_FOUND=yes)
  if test x$TIMER_FOUND = xyes; then
    #  In AIX 5.3, finding mread_real_time in libc, but not in header files.
    AC_CHECK_DECL(mread_real_time, ,AC_DEFINE([NEED_MREAD_REAL_TIME_DECL], [1], [Need Real-time declaration]),[#include <sys/systemcfg.h>] [#include <sys/time.h>])
  else
    AC_CHECK_FUNC(read_real_time, READ_REAL_TIME=read_real_time TIMER_FOUND=yes)
  fi
  if test x$TIMER_FOUND = xyes ; then
    TIMER_NAME=$READ_REAL_TIME
  fi
fi

# If specified, try to use clock_gettime
if test x$TIMER_FOUND = xno && test "x$USE_CLOCK_GETTIME" = "xyes" ; then
  AC_CHECK_LIB(rt,clock_gettime, AC_DEFINE([USE_CLOCK_GETTIME],[1] [Use clock_gettime for timing]) USE_CLOCK_GETTIME=true TIMER_FOUND=yes TIMER_NAME=clock_gettime LIBS="$LIBS -lrt"
  )
fi

# If specified, use dclock
if test x$TIMER_FOUND = xno && test "x$USE_DCLOCK" = "xyes" ; then
  AC_DEFINE([USE_DCLOCK], [1], [Use dlock]) TIMER_FOUND=yes TIMER_NAME=dclock
fi

# If no appropriate timers were found, default to MPI_Wtime
if test x$TIMER_FOUND = xno ; then
        AC_CHECK_FUNC(MPI_Wtime, AC_DEFINE([USE_WTIME], [1], [Use MPI_Wtime]) TIMER_NAME=MPI_Wtime
          , echo Failed to find MPI_Wtime.  Trying to use gettimeofday.; AC_DEFINE([USE_GETTIMEOFDAY],[1],[Use gettimofday]) USE_GETTIMEOFDAY=true)
fi


UNWIND_WITH=internal

#  Not using AC_CHECK_LIB for libunwind as libunwnd API uses macros in libunwind.h to
#  access platform-specific functions.
HAVE_LIBUNWIND=no
if test "x$DISABLE_LIBUNWIND" = "xno" ; then
	AC_CHECK_HEADER(libunwind.h, AC_DEFINE([HAVE_LIBUNWIND],[1], [Have libunwind]) LIBS="$LIBS -lunwind" HAVE_LIBUNWIND=yes UNWIND_WITH=libunwind, 
	[ if test x$build_cpu = xx86_64 ; then
	  echo
	  echo "  mpiP on x86_64 platforms requires libunwind."
	  echo "  Please install libunwind and, if necessary, configure mpiP with "
    echo "  appropriate CFLAGS and LDFLAGS settings."
	  echo
	  exit 1
	fi ]
	)
fi

if test x"$HAVE_LIBUNWIND" = xno && test x"$USE_SETJMP" = xno ; then 
  AC_CHECK_FUNC(backtrace, AC_DEFINE([USE_BACKTRACE], [1], [Use backtrace]) UNWIND_WITH=glibc-backtrace, USE_SETJMP=yes)
fi

if test "$ENABLE_API_ONLY" = no && test "$ENABLE_MPI_IO" = yes ; then
AC_CHECK_FUNC(MPI_File_open,
              AC_DEFINE([HAVE_MPI_IO], [1], [Have MPI-IO]) HAVE_MPI_IO=mpi.io.protos.txt,
	      AC_CHECK_LIB(mpio,MPI_File_open, 
                AC_DEFINE([HAVE_MPI_IO],[1],[Have MPI-IO]) HAVE_MPI_IO=mpi.io.protos.txt LIBS="${LIBS} -lmpio",
                AC_MSG_RESULT(MPI I/O symbols not found.  MPI I/O reporting deactivated.)
                HAVE_MPI_IO=/dev/null
                ENABLE_MPI_IO=no )
)
else
  HAVE_MPI_IO=/dev/null
fi

if test "x$ENABLE_API_ONLY" = xno && test "x$ENABLE_MPI_RMA" = xyes ; then
AC_CHECK_FUNC(MPI_Win_allocate,
              AC_DEFINE([HAVE_MPI_RMA], [1], [Have MPI RMA]) HAVE_MPI_RMA=mpi.rma.protos.txt,
                AC_MSG_RESULT([MPI RMA symbols not found.  MPI RMA reporting deactivated.])
                HAVE_MPI_RMA=/dev/null
                ENABLE_MPI_RMA=no
)
else
  HAVE_MPI_RMA=/dev/null
fi

if test "x$ENABLE_API_ONLY" = xno && test "x$ENABLE_MPI_NONBLOCKINGCOLLECTIVES" = xyes ; then
AC_CHECK_FUNC(MPI_Ibarrier,
              AC_DEFINE([HAVE_MPI_NONBLOCKINGCOLLECTIVES],[1],[Have MPI non-blocking collectives]) HAVE_MPI_NONBLOCKINGCOLLECTIVES=mpi.nbc.protos.txt,
                AC_MSG_RESULT([MPI NONBLOCKINGCOLLECTIVES symbols not found.  MPI NONBLOCKINGCOLLECTIVES reporting deactivated.])
                HAVE_MPI_NONBLOCKINGCOLLECTIVES=/dev/null
                ENABLE_MPI_NONBLOCKINGCOLLECTIVES=no
)
else
  HAVE_MPI_NONBLOCKINGCOLLECTIVES=/dev/null
fi

if test "x$ENABLE_API_ONLY" = xno && test "x$ENABLE_MPI_PERSISTENTCOLLECTIVES" = xyes ; then
AC_CHECK_FUNC(MPI_Barrier_init,
              AC_DEFINE([HAVE_MPI_PERSISTENTCOLLECTIVES],[1],[Have MPI persistent collectives]) HAVE_MPI_PERSISTENTCOLLECTIVES=mpi.pcoll.protos.txt,
                AC_MSG_RESULT([MPI PERSISTENTCOLLECTIVES symbols not found.  MPI PERSISTENTCOLLECTIVES reporting deactivated.])
                HAVE_MPI_PERSISTENTCOLLECTIVES=/dev/null
                ENABLE_MPI_PERSISTENTCOLLECTIVES=no
)
else
  HAVE_MPI_PERSISTENTCOLLECTIVES=/dev/null
fi

if test "x$ENABLE_API_ONLY" = xno && test "x$ENABLE_MPI_ISENDRECV" = xyes ; then
AC_CHECK_FUNC(MPI_Isendrecv,
              AC_DEFINE([HAVE_MPI_ISENDRECV],[1],[Have MPI Isendrecv]) HAVE_MPI_ISENDRECV=mpi.isendrecv.protos.txt,
                AC_MSG_RESULT([MPI ISENDRECV symbols not found.  MPI ISENDRECV reporting deactivated.])
                HAVE_MPI_ISENDRECV=/dev/null
                ENABLE_MPI_ISENDRECV=no
)
else
  HAVE_MPI_ISENDRECV=/dev/null
fi

if test "x$ENABLE_API_ONLY" = xno && test "x$ENABLE_MPI_PARTITIONED" = xyes ; then
AC_CHECK_FUNC(MPI_Psend_init,
              AC_DEFINE([HAVE_MPI_PARTITIONED],[1],[Have MPI Psend_init]) HAVE_MPI_PARTITIONED=mpi.partitioned.protos.txt,
                AC_MSG_RESULT([MPI PARTITIONED symbols not found.  MPI PARTITIONED reporting deactivated.])
                HAVE_MPI_PARTITIONED=/dev/null
                ENABLE_MPI_PARTITIONED=no
)
else
  HAVE_MPI_PARTITIONED=/dev/null
fi

if test "x$DISABLE_SO_LOOKUP" = "xno" && test "x$ENABLE_BFD" = xyes; then
  SO_LOOKUP=no
  #  Check for /proc/self/maps, can't use AC_CHECK_FILES since cross compiling
  AC_MSG_CHECKING(/proc/self/maps)
  if test -r /proc/self/maps ; then
    AC_MSG_RESULT([yes])
    SO_LOOKUP=yes
  else
    AC_MSG_RESULT([no])
  fi
  
  #  SO lookup code uses getline, assumes ought to be available if we are using libbfd
  if test "x$SO_LOOKUP" = xyes ; then
    AC_CHECK_FUNC(getline, AC_DEFINE([SO_LOOKUP],[1],[SO lookup]), AC_MSG_RESULT([getline not found so SO lookup is disabled.]))
  fi
fi

if test "$ENABLE_API_ONLY" = no ; then

if test "$ENABLE_FORTRAN_XLATE" = yes ; then
     AC_MSG_CHECKING(fortran to C conversion)
     AC_LINK_IFELSE(
       [ AC_LANG_PROGRAM([[#include "mpi.h"]], 
              [[ MPI_Fint mi; MPI_Request ri; ri = MPI_Request_f2c(mi);]] ) ],
	      [AC_MSG_RESULT([yes])],
              (AC_MSG_RESULT(  functions not found  translation deactivated)
                ENABLE_FORTRAN_XLATE=no) )
fi

#  Check for ARM LSE
     AC_MSG_CHECKING(ARM LSE)
     AC_LINK_IFELSE(
       [ AC_LANG_PROGRAM([[#include <stdint.h>]], 
                         [[ #if __aarch64__   
                          int64_t *addr, newval; int64_t ret;

__asm__ __volatile__ ("swpl %2, %0, [%1]\n"
                      : "=&r" (ret)
                      : "r" (addr), "r" (newval)
                      : );
#else
fail
#endif
]] ) ],
	      [AC_MSG_RESULT([yes])] AC_DEFINE(HAVE_ARM_LSE, [1], [Using a processor with LSE]),
              (AC_MSG_RESULT( no)) )
#AC_SUBST(HAVE_ARM_LSE)
fi

#  If using Fortran routines to access command line,
#  test whether get_command_argument is available, otherwise
#  use getarg.
FORTRAN_GETARG=""
FORTRAN_GETARG_SRC_FILE=mpiP_getarg.f.part
if test "$USE_GETARG" = true ; then
     AC_LANG_PUSH(Fortran 77)
     # Force Fortran compiler tests
     AC_LINK_IFELSE(AC_LANG_PROGRAM(,,), , )
     AC_MSG_CHECKING(fortran command-line argument functions)
     AC_LINK_IFELSE(
       [ AC_LANG_PROGRAM(, 
              [[
       integer len
       character*10 val
       call get_command_argument(0, val, len)]] ) ],
	      AC_MSG_RESULT([using get_command_argument]) 
                echo "       call get_command_argument(idx, buf, len)" > $FORTRAN_GETARG_SRC_FILE
                FORTRAN_GETARG=$FORTRAN_GETARG_SRC_FILE,
              AC_MSG_RESULT(using getarg) 
	      echo "       call getarg(idx, buf)" > $FORTRAN_GETARG_SRC_FILE
	      echo "       len = mpipi_get_strlen(buf)" >> $FORTRAN_GETARG_SRC_FILE
	      FORTRAN_GETARG=$FORTRAN_GETARG_SRC_FILE
              AC_SUBST_FILE(FORTRAN_GETARG)
                )
     AC_LANG_POP(Fortran 77)
fi


if test "$ENABLE_API_ONLY" = no ; then
dnl ========== Find out how FORTRAN symbol names appear in C ==========

AC_MSG_CHECKING(fortran symbols)

if test -n "$F77" -a "$F77" != no ; then
  /bin/rm -f ffunc.f flink.c
  echo "      subroutine f_fun()" > ffunc.f
  echo "      return" >> ffunc.f
  echo "      end" >> ffunc.f
  if ! $F77 $FFLAGS -c ffunc.f 1>/dev/null 2>/dev/null ; then
    AC_MSG_RESULT(Failed to compile fortran test object. Example error follows:)
    F77_OBJ_OUT=`$F77 $FFLAGS -c ffunc.f 2>&1`
    AC_MSG_NOTICE($F77_OBJ_OUT)
    AC_MSG_ERROR([giving up])
  fi
  echo "extern void f_fun_(void);" > flink.c
  echo "int main(void){ FF(); return 0; }" >> flink.c
  if $CC -o flink -DFF=f_fun flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(same as C)
    F77_SYMBOLS=symbol
  elif $CC -o flink -DFF=f_fun_ flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(lowercase with underscore)
    F77_SYMBOLS=symbol_
  elif $CC -o flink -DFF=f_fun__ flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(lowercase with 2 underscores)
    F77_SYMBOLS=symbol__
  elif $CC -o flink -DFF=F_FUN flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(uppercase)
    F77_SYMBOLS=SYMBOL
  elif $CC -o flink -DFF=F_FUN_ flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(uppercase with underscore)
    F77_SYMBOLS=SYMBOL_
  elif $CC -o flink -DFF=F_FUN_ flink.c ffunc.o $LDFLAGS $LIBS 1>/dev/null 2>/dev/null; then
    AC_MSG_RESULT(uppercase with 2 underscores)
    F77_SYMBOLS=SYMBOL__
  else
    AC_MSG_RESULT(could not determine F77 symbol names. Example error follows:)
    CC_F77_SYM_OUT=`$CC -o flink -DFF=f_fun flink.c ffunc.o $LDFLAGS $LIBS 2>&1`
    AC_MSG_NOTICE($CC_F77_SYM_OUT)
    AC_MSG_ERROR([giving up])
  fi
  /bin/rm -f ffunc.f ffunc.o flink flink.c flink.o ffunc
else
  F77_SYMBOLS=symbol_
  AC_MSG_RESULT(guessing lowercase with underscore)
fi
AC_SUBST(F77_SYMBOLS)
AC_DEFINE_UNQUOTED([F77_SYMBOLS],[$F77_SYMBOLS], [F77 symbols])


dnl ========== Identify F77 ==========
FORTRAN_GETARG_OBJ_FILE=get_fortran_arg.o

AC_MSG_CHECKING(fortran compiler)
if $F77 -V 2>&1 | grep -e 'Portland Group' 1> /dev/null 2> /dev/null ; then
  F77_VENDOR=PGI
  MPIPFLIB=mpiPpgf
  FORTRAN_FLAG=-DPGI
  FORTRAN_TARGET=libmpiPpgf.a
elif echo $F77 2>&1 | grep 'xlf' 1> /dev/null 2> /dev/null ; then
  F77_VENDOR=IBM
  if test "x$USE_GETARG" = xtrue ; then
    MPIPFLIB=mpiPxlf
    FORTRAN_TARGET=libmpiPxlf.a
  else
    MPIPFLIB=mpiP
  fi
elif test "x$G77" = xyes ; then
  F77_VENDOR=GNU
  FORTRAN_FLAG=-DGNU_Fortran
  FORTRAN_TARGET=libmpiPg77.a
  MPIPFLIB=mpiPg77
elif $F77 --version 2>&1 | grep -e 'GNU Fortran' -e gfortran 1> /dev/null 2> /dev/null ; then
  F77_VENDOR=GNU
  FORTRAN_FLAG=-DGNU_Fortran
  FORTRAN_TARGET=libmpiPg77.a
  MPIPFLIB=mpiPg77
elif $F77 -V 2>&1 | grep -e Intel 1> /dev/null 2> /dev/null ; then
  F77_VENDOR=Intel
  FORTRAN_FLAG=
  FORTRAN_TARGET=
  MPIPFLIB=
elif $F77 -V 2>&1 | grep -e Cray 1>/dev/null 2>/dev/null ; then
  F77_VENDOR=Cray
  FORTRAN_FLAG=-DCray_Fortran
  FORTRAN_TARGET=libmpiPftn.a
  MPIPFLIB=mpiPftn 
  if test "x$USE_GETARG" = xtrue ; then
    FORTRAN_GETARG_OBJ_FILE=get_fortran_arg_pxf.o
  fi
elif $F77 -version 2>&1 | grep -e Compaq 1> /dev/null 2> /dev/null ; then
  F77_VENDOR=Compaq
  MPIPFLIB=mpiP
  FORTRAN_FLAG=
  FORTRAN_TARGET=
else
  F77_VENDOR=Unknown
  MPIPFLIB=mpiP
  FORTRAN_FLAG=
  FORTRAN_TARGET=
fi

if test x"$F77_VENDOR" = x"IBM" ; then
  FORTRAN_STR_DECL="character (buf_len) buf"
else
  FORTRAN_STR_DECL="character buf*(*)"
fi

fi #if test "$ENABLE_API_ONLY" = no ; then

AC_MSG_RESULT($F77_VENDOR)
AC_SUBST(F77_VENDOR,$F77_VENDOR)
AC_SUBST(MPIPFLIB,$MPIPFLIB)
AC_SUBST(FORTRAN_FLAG,$FORTRAN_FLAG)
AC_SUBST(FORTRAN_TARGET,$FORTRAN_TARGET)
AC_SUBST(FORTRAN_STR_DECL, $FORTRAN_STR_DECL)
AC_SUBST(ENABLE_BFD, $ENABLE_BFD)
AC_SUBST(ENABLE_API_ONLY)
AC_SUBST(READ_REAL_TIME)
AC_SUBST(DEFAULT_TARGS)
AC_SUBST(FORTRAN_GETARG_OBJ_FILE)
AC_SUBST(TEST_LIST)
AC_SUBST(USE_BACKTRACE)
AC_SUBST(USE_SETJMP)
AC_SUBST(ADD_OBJS)
AC_SUBST(PIC_FLAGS)
AC_SUBST(MPIP_COPIED_ARGS_MAX)
AC_SUBST_FILE(HAVE_MPI_IO)
AC_SUBST_FILE(HAVE_MPI_RMA)
AC_SUBST_FILE(HAVE_MPI_NONBLOCKINGCOLLECTIVES)
AC_SUBST_FILE(HAVE_MPI_PERSISTENTCOLLECTIVES)
AC_SUBST_FILE(HAVE_MPI_ISENDRECV)
AC_SUBST_FILE(HAVE_MPI_PARTITIONED)
AC_SUBST_FILE(FORTRAN_GETARG)

if test "x${slibdir}" = x ; then
  slibdir=$libdir
fi
AC_SUBST(slibdir)

AC_CONFIG_FILES([Defs.mak Makefile testing/Makefile Check.mak mpi.protos.txt get_fortran_arg.f mpip_timers/aix_local.h])
AC_OUTPUT

#  
#  Print out Summary of configuration
#

echo
echo "********************************************************************************"
echo "  mpiP Configuration Summary"
echo
echo "  C compiler               : ${CC}"
echo "  C++ compiler             : ${CXX}"
echo "  Fortran compiler         : ${F77}"
echo "  Python                   : ${HAVE_PYTHON}"
echo "  Test launcher            : ${LAUNCH}"
echo
echo "  Timer                    : ${TIMER_NAME}"
echo "  Stack Unwinding          : ${UNWIND_WITH}"
echo "  Address to Source Lookup : ${SOURCE_LOOKUP}"
echo
echo "  MPI-I/O support          : ${ENABLE_MPI_IO}"
echo "  MPI-RMA support          : ${ENABLE_MPI_RMA}"
echo "  MPI-NBC support          : ${ENABLE_MPI_NONBLOCKINGCOLLECTIVES}"
echo "  MPI-PC  support          : ${ENABLE_MPI_PERSISTENTCOLLECTIVES}"
echo "  MPI-Isendrecv support    : ${ENABLE_MPI_ISENDRECV}"
echo "  MPI-Partitioned support  : ${ENABLE_MPI_PARTITIONED}"
echo "********************************************************************************"
