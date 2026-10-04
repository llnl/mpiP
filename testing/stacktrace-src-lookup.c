#define _GNU_SOURCE

/*

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   stacktrace-src-lookup.c -- standalone source lookup test for a local
   multi-frame stack without launching MPI ranks.

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <dlfcn.h>
#include <errno.h>

#include "../mpiP-API.h"

#define MAX_STACK 16
#define THIS_SOURCE "stacktrace-src-lookup.c"

#if defined(__GNUC__) || defined(__clang__)
#define MPIP_NOINLINE __attribute__((noinline))
#else
#define MPIP_NOINLINE
#endif

static int captured_frame_count = 0;
static void *captured_pcs[MAX_STACK];
static int requested_max_back = MAX_STACK;

static MPIP_NOINLINE void
capture_traceback (void)
{
  memset (captured_pcs, 0, sizeof (captured_pcs));
  captured_frame_count = mpiP_record_traceback (captured_pcs, requested_max_back);
}

static MPIP_NOINLINE void
stack_level_3 (void)
{
  capture_traceback ();
}

static MPIP_NOINLINE void
stack_level_2 (void)
{
  stack_level_3 ();
}

static MPIP_NOINLINE void
stack_level_1 (void)
{
  stack_level_2 ();
}

static int
frame_matches_source (const char *file)
{
  return file != NULL && strstr (file, THIS_SOURCE) != NULL;
}

static int
frame_matches_function (const char *func, const char *name)
{
  return func != NULL && strcmp (func, name) == 0;
}

static int
lookup_expected_frame (void *pc, const char *expected_func)
{
  char *file = NULL;
  char *func = NULL;
  int line = 0;
  char addr_buf[24];

  if (mpiP_find_src_loc (pc, &file, &line, &func) != 0)
    {
      fprintf (stderr, "lookup failed for %s\n",
               mpiP_format_address (pc, addr_buf));
      return 1;
    }

  printf ("lookup %s: %s %s:%d %s\n", expected_func,
          mpiP_format_address (pc, addr_buf),
          file != NULL ? file : "(null)", line,
          func != NULL ? func : "(null)");

  if (!frame_matches_source (file) || !frame_matches_function (func, expected_func))
    {
      fprintf (stderr, "unexpected lookup result for %s\n", expected_func);
      return 1;
    }

  return 0;
}

int
main (int argc, char **argv)
{
  char *exe = NULL;
  char exe_path[PATH_MAX];
  char *file = NULL;
  char *func = NULL;
  int i;
  int line = 0;
  int executable_frames = 0;
  int frames_only = 0;
  char addr_buf[24];
  const char *opened_exe = NULL;

  if (argc >= 2)
    {
      char *endptr = NULL;
      long parsed = 0;

      if (strcmp (argv[1], "--frames-only") == 0)
        {
          frames_only = 1;
          if (argc >= 3)
            {
              errno = 0;
              parsed = strtol (argv[2], &endptr, 10);
              if (errno == 0 && endptr != argv[2] && *endptr == '\0'
                  && parsed > 0 && parsed <= MAX_STACK)
                requested_max_back = (int) parsed;
            }
        }
      else
        {
          errno = 0;
          parsed = strtol (argv[1], &endptr, 10);
          if (errno == 0 && endptr != argv[1] && *endptr == '\0'
              && parsed > 0 && parsed <= MAX_STACK)
            requested_max_back = (int) parsed;
        }
    }

  if (argv != NULL)
    exe = argv[0];
  if (exe == NULL)
    exe = mpiP_get_executable_name ();

  if (exe != NULL && realpath (exe, exe_path) != NULL)
    opened_exe = exe_path;
  else
    opened_exe = exe;

  if (opened_exe == NULL || mpiP_open_executable ((char *) opened_exe) != 0)
    {
      fprintf (stderr, "failed to open executable for source lookup: %s\n",
               opened_exe != NULL ? opened_exe : "(null)");
      return 1;
    }

  stack_level_1 ();

  if (captured_frame_count <= 0)
    {
      fprintf (stderr, "traceback capture returned no frames\n");
      mpiP_close_executable ();
      return 1;
    }

  printf ("captured %d frames (max_back=%d)\n", captured_frame_count,
          requested_max_back);
  for (i = 0; i < captured_frame_count && captured_pcs[i] != NULL; i++)
    {
      Dl_info info;
      char frame_path[PATH_MAX];
      const char *frame_file = NULL;
      const char *frame_func = NULL;

      memset (&info, 0, sizeof (info));
      if (dladdr (captured_pcs[i], &info) == 0)
        continue;

      if (info.dli_fname != NULL && realpath (info.dli_fname, frame_path) != NULL)
        frame_file = frame_path;
      else
        frame_file = info.dli_fname;
      frame_func = info.dli_sname;

      if (frame_file == NULL || strcmp (frame_file, opened_exe) != 0)
        {
          printf ("frame %d: %s module=%s func=%s (skipped)\n", i,
                  mpiP_format_address (captured_pcs[i], addr_buf),
                  frame_file != NULL ? frame_file : "(unknown)",
                  frame_func != NULL ? frame_func : "(unknown)");
          continue;
        }

      executable_frames++;
      printf ("frame %d: %s module=%s\n", i,
              mpiP_format_address (captured_pcs[i], addr_buf), frame_file);
      printf ("  function: %s\n",
              frame_func != NULL ? frame_func : "(unknown)");

      if (frames_only)
        {
          if (mpiP_find_src_loc (captured_pcs[i], &file, &line, &func) == 0)
            {
              printf ("  source: %s:%d %s\n",
                      file != NULL ? file : "(null)", line,
                      func != NULL ? func : "(null)");
            }
          else
            {
              printf ("  source: lookup failed\n");
            }
        }

      if (frame_matches_function (frame_func, "main"))
        break;
    }

  if (frames_only)
    {
      mpiP_close_executable ();
      return 0;
    }

  if (executable_frames < 3
      || lookup_expected_frame ((void *) stack_level_1, "stack_level_1") != 0
      || lookup_expected_frame ((void *) stack_level_2, "stack_level_2") != 0
      || lookup_expected_frame ((void *) stack_level_3, "stack_level_3") != 0)
    {
      fprintf (stderr, "expected executable stack frames were not resolved\n");
      mpiP_close_executable ();
      return 1;
    }

  mpiP_close_executable ();

  printf ("source lookup recovered all expected stack frames\n");
  return 0;
}
