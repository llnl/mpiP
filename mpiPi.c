/* -*- C -*-

   mpiP MPI Profiler ( http://llnl.github.io/mpiP )

   Please see COPYRIGHT AND LICENSE information at the end of this file.

   -----

   mpiPi.c -- main mpiP internal functions

 */

#ifndef lint
static char *svnid = "$Id$";
#endif

#include <string.h>
#include <float.h>
#include <unistd.h>
#include "mpiPi.h"

mpiPi_fortran_t mpiPi_fortran;


static int
mpiPi_callsite_stats_src_hashkey (const void *p)
{
  int res = 0;
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op ^ res ^ csp->rank ^ csp->csid;
}

static int
mpiPi_callsite_stats_src_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
  express (csid);
  express (rank);
#undef express

  return 0;
}

static int
mpiPi_callsite_stats_src_id_hashkey (const void *p)
{
  int res = 0;
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op ^ res ^ csp->csid;
}

static int
mpiPi_callsite_stats_src_id_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
  express (csid);
#undef express

  return 0;
}

#ifndef ENABLE_API_ONLY		/* { */
/* task level init
   - executed by each MPI task only once immediately after MPI_Init
*/

void
mpiPi_init (char *appName, mpiPi_thr_mode_t thr_mode)
{
  if (time (&mpiPi.start_timeofday) == (time_t) - 1)
    {
      mpiPi_msg_warn ("Could not get time of day from time()\n");
    }

  mpiPi.toolname = "mpiP";
  mpiPi.comm = MPI_COMM_WORLD;
  mpiPi.tag = 9821;
  mpiPi.procID = getpid ();
  mpiPi.appName = strdup (appName);
  PMPI_Comm_rank (mpiPi.comm, &mpiPi.rank);
  PMPI_Comm_size (mpiPi.comm, &mpiPi.size);
  PMPI_Get_processor_name (mpiPi.hostname, &mpiPi.hostnamelen);
  mpiPi.stdout_ = stdout;
  mpiPi.stderr_ = stderr;
  mpiPi.lookup = mpiPi_lookup;

  mpiPi.enabled = 1;
  mpiPi.enabledCount = 1;
  mpiPi.cumulativeTime = 0.0;
  mpiPi.global_app_time = 0.0;
  mpiPi.global_mpi_time = 0.0;
  mpiPi.global_mpi_size = 0.0;
  mpiPi.global_mpi_io = 0.0;
  mpiPi.global_mpi_rma = 0.0;
  mpiPi.global_mpi_msize_threshold_count = 0;
  mpiPi.global_mpi_sent_count = 0;
  mpiPi.global_time_callsite_count = 0;
  mpiPi.global_task_hostnames = NULL;
  mpiPi.global_task_app_time = NULL;
  mpiPi.global_task_mpi_time = NULL;

  /* set some defaults values */
  mpiPi.collectorRank = 0;
  mpiPi.tableSize = 256;
  mpiPi.reportPrintThreshold = 0.0;
  mpiPi.baseNames = 0;
  mpiPi.reportFormat = MPIP_REPORT_SCI_FORMAT;
  mpiPi.calcCOV = 1;
  mpiPi.inAPIrtb = 0;
  mpiPi.do_lookup = 1;
  mpiPi.messageCountThreshold = -1;

  if (DEFAULT_REPORT_FORMAT == mpiPi_style_concise)
    {
      mpiPi.report_style = mpiPi_style_concise;
      mpiPi.reportStackDepth = 0;
      mpiPi.print_callsite_detail = 0;
    }
  else // verbose default
    {
      mpiPi.report_style = mpiPi_style_verbose;
      mpiPi.reportStackDepth = 1;
      mpiPi.print_callsite_detail = 1;
    }

  mpiPi.internalStackDepth = MPIP_INTERNAL_STACK_DEPTH;
  mpiPi.fullStackDepth = mpiPi.reportStackDepth + mpiPi.internalStackDepth;
  if ( mpiPi.fullStackDepth > MPIP_CALLSITE_STACK_DEPTH_MAX )
      mpiPi.fullStackDepth = MPIP_CALLSITE_STACK_DEPTH_MAX;

#ifdef COLLECTIVE_REPORT_DEFAULT
  mpiPi.collective_report = 1;
#else
  mpiPi.collective_report = 0;
#endif
  mpiPi.disable_finalize_report = 0;
  mpiPi.do_collective_stats_report = 0;
  mpiPi.do_pt2pt_stats_report = 0;
#ifdef SO_LOOKUP
  mpiPi.so_info = NULL;
#endif
  mpiPi_getenv ();

  mpiPi_stats_mt_init(&mpiPi.task_stats, thr_mode);

  /* -- get addresses of MPI_IN_PLACE, MPI_BOTTOM, MPI_STATUS_IGNORE
   *    and MPI_STATUSES_IGNORE when profiling Fortran code
   */
  fortran_vars(&mpiPi_fortran.in_place, &mpiPi_fortran.bottom, 
               &mpiPi_fortran.status_ignore, &mpiPi_fortran.statuses_ignore,
               &mpiPi_fortran.status_size);

  /* -- welcome msg only collector  */
  if (mpiPi.collectorRank == mpiPi.rank)
    {
      mpiPi_msg ("%s V%d.%d.%d (Build %s/%s)\n", mpiPi.toolname, mpiPi_vmajor,
                 mpiPi_vminor, mpiPi_vpatch, mpiPi_vdate, mpiPi_vtime);
      mpiPi_msg ("\n");
    }

  mpiPi_msg_debug ("appName is %s\n", appName);
  mpiPi_msg_debug ("sizeof(callsite_stats_t) is %d\n",
                   sizeof (callsite_stats_t));
  mpiPi_msg_debug ("successful init on %d, %s\n", mpiPi.rank, mpiPi.hostname);


  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_start(&mpiPi.task_stats);
    }

  return;
}
#endif /* } ifndef ENABLE_API_ONLY */

static int
mpiPi_insert_callsite_records (callsite_stats_t * p)
{
  callsite_stats_t *csp = NULL;

  mpiPi_query_src (p);		/* sets the file/line in p */

  /* If exists, accumulate, otherwise insert. This is
     specifically for optimizations that have multiple PCs for
     one src line. We aggregate across rank after this.

     The collective_report reporting approach does not aggregate individual
     process callsite information at the collector process.
   */
  if (mpiPi.collective_report == 0)
    {
      if (NULL == h_search (mpiPi.global_callsite_stats, p, (void **) &csp))
        {
          callsite_stats_t *newp = NULL;
          newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));

          memcpy (newp, p, sizeof (callsite_stats_t));
          /* insert new record into global */
          h_insert (mpiPi.global_callsite_stats, newp);
        }
      else
        mpiPi_cs_merge(csp, p);
    }

  /* Collect aggregate callsite summary information indpendent of rank. */
  if (NULL == h_search (mpiPi.global_callsite_stats_agg, p, (void **) &csp))
    {
      callsite_stats_t *newp = NULL;
      newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));

      memcpy (newp, p, sizeof (callsite_stats_t));
      newp->rank = -1;

      if (mpiPi.calcCOV)
        {
          newp->siteData = (double *) malloc (mpiPi.size * sizeof (double));
          newp->siteData[0] = p->cumulativeTime;
          newp->siteDataIdx = 1;
        }

      /* insert new record into global */
      h_insert (mpiPi.global_callsite_stats_agg, newp);
    }
  else
    {
      mpiPi_cs_merge(csp, p);

      if (mpiPi.calcCOV)
        {
          csp->siteData[csp->siteDataIdx] = p->cumulativeTime;
          csp->siteDataIdx += 1;
        }
    }

  /* Do global accumulation while we are iterating through individual callsites */
  mpiPi.global_task_mpi_time[p->rank] += p->cumulativeTime;

  mpiPi.global_mpi_time += p->cumulativeTime;
  assert (mpiPi.global_mpi_time >= 0);
  mpiPi.global_mpi_size += p->cumulativeDataSent;
  mpiPi.global_mpi_io += p->cumulativeIO;
  mpiPi.global_mpi_rma += p->cumulativeRMA;
  if (p->cumulativeTime > 0)
    mpiPi.global_time_callsite_count++;

  if (p->cumulativeDataSent > 0)
    {
      mpiPi.global_mpi_msize_threshold_count += p->arbitraryMessageCount;
      mpiPi.global_mpi_sent_count += p->count;
    }

  return 1;
}

static int
callsite_sort_by_MPI_op (const void *a, const void *b)
{
  callsite_stats_t **a1 = (callsite_stats_t **) a;
  callsite_stats_t **b1 = (callsite_stats_t **) b;

  /* NOTE: want descending sort, so compares are reveresed */
  if ((*a1)->op < (*b1)->op)
    {
      return 1;
    }
  if ((*a1)->op > (*b1)->op)
    {
      return -1;
    }
  return 0;
}


static int
mpiPi_callsite_stats_MPI_id_hashkey (const void *p)
{
  callsite_stats_t *csp = (callsite_stats_t *) p;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp);
  return 52271 ^ csp->op;
}

static int
mpiPi_callsite_stats_op_comparator (const void *p1, const void *p2)
{
  callsite_stats_t *csp_1 = (callsite_stats_t *) p1;
  callsite_stats_t *csp_2 = (callsite_stats_t *) p2;
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_1);
  MPIP_CALLSITE_STATS_COOKIE_ASSERT (csp_2);

#define express(f) {if ((csp_1->f) > (csp_2->f)) {return 1;} if ((csp_1->f) < (csp_2->f)) {return -1;}}
  express (op);
#undef express

  return 0;
}


/*  Aggregate individual MPI call data by iterating through call sites.  */
static int
mpiPi_insert_MPI_records ()
{
  callsite_stats_t *csp = NULL;
  int i, ac;
  callsite_stats_t **av;
  callsite_stats_t *p;

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      /*  Open hash table for MPI call data.  */
      mpiPi.global_MPI_stats_agg = h_open (mpiPi.tableSize,
                                           mpiPi_callsite_stats_MPI_id_hashkey,
                                           mpiPi_callsite_stats_op_comparator);

      /*  Get individual call data.  */
      h_gather_data (mpiPi.global_callsite_stats_agg, &ac, (void ***) &av);

      /*  Sort by MPI op.  */
      qsort (av, ac, sizeof (void *), callsite_sort_by_MPI_op);

      /*  For each call site, add call site info to hash table entry for MPI op, independent of rank.  */
      for (i = 0; i < ac; i++)
        {
          p = av[i];

          /* Check if there is already an entry for the MPI op. */
          if (NULL ==
              h_search (mpiPi.global_MPI_stats_agg, p, (void **) &csp))
            {
              callsite_stats_t *newp = NULL;
              newp = (callsite_stats_t *) malloc (sizeof (callsite_stats_t));
              memcpy (newp, p, sizeof (callsite_stats_t));
              newp->rank = -1;
              newp->csid = p->op - mpiPi_BASE;

              /* insert new record into global */
              h_insert (mpiPi.global_MPI_stats_agg, newp);
            }
          else
            {
              mpiPi_cs_merge(csp, p);
            }
        }
    }

  return 1;
}

#ifndef ENABLE_API_ONLY		/* { */

static int
mpiPi_mergeResults ()
{
  int ac;
  callsite_stats_t **av;
  int totalCount = 0;
  int maxCount = 0;
  int retval = 1, sendval;
  callsite_stats_t *rawCallsiteData = NULL;

  /* gather local task data */
  mpiPi_stats_mt_cs_gather(&mpiPi.task_stats, &ac, &av);

  /* determine size of space necessary on collector */
  PMPI_Allreduce (&ac, &totalCount, 1, MPI_INT, MPI_SUM, mpiPi.comm);
  PMPI_Reduce (&ac, &maxCount, 1, MPI_INT, MPI_MAX, mpiPi.collectorRank,
               mpiPi.comm);
  if (mpiPi.collectorRank != mpiPi.rank) {
      maxCount = ac;
    }

  if (totalCount < 1)
    {
      if (mpiPi.rank == mpiPi.collectorRank)
        mpiPi_msg_warn
            ("Collector found no records to merge. Omitting report.\n");

      return 0;
    }

  /* Try to allocate space for max count of callsite info from all tasks  */
  rawCallsiteData =
      (callsite_stats_t *) calloc (maxCount, sizeof (callsite_stats_t));
  if (rawCallsiteData == NULL)
    {
      mpiPi_msg_warn
          ("Failed to allocate memory to collect callsite info");
      retval = 0;
    }

  /* gather global data at collector */
  if (mpiPi.rank == mpiPi.collectorRank)
    {
      int i;
      int ndx = 0;

#ifdef ENABLE_BFD
      if (mpiPi.appFullName != NULL)
        {
          if (open_bfd_executable (mpiPi.appFullName) == 0)
            mpiPi.do_lookup = 0;
        }
#elif defined(USE_LIBDWARF)
      if (mpiPi.appFullName != NULL)
        {
          if (open_dwarf_executable (mpiPi.appFullName) == 0)
            mpiPi.do_lookup = 0;
        }
#endif
#if defined(ENABLE_BFD) || defined(USE_LIBDWARF)
      else
        {
          mpiPi_msg_warn
              ("Failed to open executable.  The mpiP -x runtime flag may address this issue.\n");
          mpiPi.do_lookup = 0;
        }
#endif

      /* Open call site hash tables.  */
      mpiPi.global_callsite_stats = h_open (mpiPi.tableSize,
                                            mpiPi_callsite_stats_src_hashkey,
                                            mpiPi_callsite_stats_src_comparator);
      mpiPi.global_callsite_stats_agg = h_open (mpiPi.tableSize,
                                                mpiPi_callsite_stats_src_id_hashkey,
                                                mpiPi_callsite_stats_src_id_comparator);
      mpiPi_cs_cache_init();

      /* Clear global_mpi_time and global_mpi_size before accumulation in mpiPi_insert_callsite_records */
      mpiPi.global_mpi_time = 0.0;
      mpiPi.global_mpi_size = 0.0;

      if (retval == 1)
        {
          /* Insert local callsite information */
          for (ndx = 0; ndx < ac; ndx++)
            {
              mpiPi_insert_callsite_records (av[ndx]);
            }

          /* Collect remote pc data */
          for (i = 1; i < mpiPi.size; i++)	/* n-1 */
            {
              MPI_Status status;
              int count;

              /* okay in any order */
              PMPI_Probe (MPI_ANY_SOURCE, mpiPi.tag, mpiPi.comm, &status);
              PMPI_Get_count (&status, MPI_CHAR, &count);
              PMPI_Recv (rawCallsiteData, count, MPI_CHAR,
                         status.MPI_SOURCE, mpiPi.tag, mpiPi.comm, &status);
              count /= sizeof (callsite_stats_t);

              for (ndx = 0; ndx < count; ndx++)
                {
                  mpiPi_insert_callsite_records (&rawCallsiteData[ndx]);
                }
            }
        }
    }
  else
    {
      int ndx;
      for (ndx = 0; ndx < ac; ndx++)
        {
          bcopy (av[ndx],
                 &(rawCallsiteData[ndx]),
                 sizeof (callsite_stats_t));
        }
      PMPI_Send (rawCallsiteData, ac * sizeof (callsite_stats_t),
                 MPI_CHAR, mpiPi.collectorRank, mpiPi.tag, mpiPi.comm);
    }

  free (rawCallsiteData);

  if (mpiPi.rank == mpiPi.collectorRank && retval == 1)
    {
      if (mpiPi.collective_report == 0)
        mpiPi_msg_debug
            ("MEMORY : Allocated for global_callsite_stats     : %13ld\n",
             h_count (mpiPi.global_callsite_stats) * sizeof (callsite_stats_t));
      mpiPi_msg_debug
          ("MEMORY : Allocated for global_callsite_stats_agg : %13ld\n",
           h_count (mpiPi.global_callsite_stats_agg) *
           sizeof (callsite_stats_t));
    }

  /* TODO: need to free all these pointers as well. */
  free (av);

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      if (mpiPi.do_lookup == 1)
        {
#ifdef ENABLE_BFD
		  /* clean up */
		  close_bfd_executable ();
#elif defined(USE_LIBDWARF)
		  close_dwarf_executable ();
#endif
        }
    }

  /*  Quadrics MPI does not appear to support MPI_IN_PLACE   */
  sendval = retval;
  PMPI_Allreduce (&sendval, &retval, 1, MPI_INT, MPI_MIN, mpiPi.comm);
  return retval;
}


static int
mpiPi_mergeCollectiveStats ()
{
  double *coll_time_results = NULL, *coll_time_local = NULL;
  size_t size;

  if (!mpiPi.do_collective_stats_report)
    {
      return 1;
    }

  if (mpiPi.collectorRank == mpiPi.rank){
      coll_time_results = (double *) malloc (sizeof(mpiPi.coll_time_stats));
    }

  mpiPi_stats_mt_coll_gather(&mpiPi.task_stats, &coll_time_local);

  /*  Collect Collective statistic data were used  */
  size = sizeof(mpiPi.pt2pt_send_stats) / sizeof(double);
  PMPI_Reduce (coll_time_local, coll_time_results,
               size, MPI_DOUBLE, MPI_SUM, mpiPi.collectorRank, mpiPi.comm);
  free (coll_time_local);

  if (mpiPi.collectorRank == mpiPi.rank){
      int i = 0, x, y, z;
      for (x = 0; x < MPIP_NFUNC; x++)
        for (y = 0; y < MPIP_COMM_HISTCNT; y++)
          for (z = 0; z < MPIP_SIZE_HISTCNT; z++)
            mpiPi.coll_time_stats[x][y][z] = coll_time_results[i++];
      free (coll_time_results);
    }
  return 1;
}


static int
mpiPi_mergept2ptStats ()
{
  double *pt2pt_send_results = NULL, *pt2pt_send_local = NULL;
  size_t size;


  if (!mpiPi.do_pt2pt_stats_report)
    {
      return 1;
    }

  if (mpiPi.collectorRank == mpiPi.rank){
      pt2pt_send_results = (double *) malloc (sizeof(mpiPi.pt2pt_send_stats));
    }
  mpiPi_stats_mt_pt2pt_gather(&mpiPi.task_stats, &pt2pt_send_local);

  /*  Collect Collective statistic data were used  */
  size = sizeof(mpiPi.pt2pt_send_stats) / sizeof(double);
  PMPI_Reduce (pt2pt_send_local, pt2pt_send_results,
               size, MPI_DOUBLE, MPI_SUM, mpiPi.collectorRank, mpiPi.comm);
  free(pt2pt_send_local);

  if (mpiPi.collectorRank == mpiPi.rank)
    {
      int i = 0, x, y, z;
      for (x = 0; x < mpiPi_DEF_END - mpiPi_BASE; x++)
        for (y = 0; y < 32; y++)
          for (z = 0; z < 32; z++)
            mpiPi.pt2pt_send_stats[x][y][z] = pt2pt_send_results[i++];

      free (pt2pt_send_results);
    }

  return 1;
}


static void
mpiPi_publishResults (int report_style)
{
  FILE *fp = NULL;
  static int printCount = 0;

  if (mpiPi.collectorRank == mpiPi.rank)
    {

      /* Generate output filename, and open */
      do
        {
          printCount++;
          snprintf (mpiPi.oFilename, 256, "%s/%s.%d.%d.%d.mpiP",
                    mpiPi.outputDir, mpiPi.appName, mpiPi.size, mpiPi.procID,
                    printCount);
        }
      while (access (mpiPi.oFilename, F_OK) == 0);

      fp = fopen (mpiPi.oFilename, "w");

      if (fp == NULL)
        {
          mpiPi_msg_warn ("Could not open [%s], writing to stdout\n",
                          mpiPi.oFilename);
          fp = stdout;
        }
      else
        {
          mpiPi_msg ("\n");
          mpiPi_msg ("Storing mpiP output in [%s].\n", mpiPi.oFilename);
          mpiPi_msg ("\n");
        }
    }
  mpiPi_profile_print (fp, report_style);
  PMPI_Barrier (mpiPi.comm);
  if (fp != stdout && fp != NULL)
    {
      fclose (fp);
    }
}


/*
 * mpiPi_collect_basics() - all tasks send their basic info to the
 * collectorRank.
 */
static void
mpiPi_collect_basics (int report_style)
{
  mpiPi_msg_debug ("Collect Basics\n");

  if (mpiPi.rank == mpiPi.collectorRank)
    {
      /* In the case where multiple reports are generated per run,
         only allocate memory for global_task_info once */
      if (mpiPi.global_task_app_time == NULL)
        {
          mpiPi.global_task_app_time =
              (double *) calloc (mpiPi.size, sizeof (double));

          if (mpiPi.global_task_app_time == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_app_time");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_app_time :          %13ld\n",
               mpiPi.size * sizeof (double));
        }

      bzero (mpiPi.global_task_app_time, mpiPi.size * sizeof (double));

      if (mpiPi.global_task_mpi_time == NULL)
        {
          mpiPi.global_task_mpi_time =
              (double *) calloc (mpiPi.size, sizeof (double));

          if (mpiPi.global_task_mpi_time == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_mpi_time");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_mpi_time :          %13ld\n",
               mpiPi.size * sizeof (double));
        }

      bzero (mpiPi.global_task_mpi_time, mpiPi.size * sizeof (double));

      //  Only allocate hostname storage if we are doing a verbose report
      if (mpiPi.global_task_hostnames == NULL
          && (report_style == mpiPi_style_verbose
              || report_style == mpiPi_style_both))
        {
          mpiPi.global_task_hostnames =
              (mpiPi_hostname_t *) calloc (mpiPi.size,
                                           sizeof (char) *
                                           MPIPI_HOSTNAME_LEN_MAX);

          if (mpiPi.global_task_hostnames == NULL)
            mpiPi_abort
                ("Failed to allocate memory for global_task_hostnames");

          mpiPi_msg_debug
              ("MEMORY : Allocated for global_task_hostnames :          %13ld\n",
               mpiPi.size * sizeof (char) * MPIPI_HOSTNAME_LEN_MAX);
        }

      if (mpiPi.global_task_hostnames != NULL)
        bzero (mpiPi.global_task_hostnames,
               mpiPi.size * sizeof (char) * MPIPI_HOSTNAME_LEN_MAX);
    }

  PMPI_Gather (&mpiPi.cumulativeTime, 1, MPI_DOUBLE,
               mpiPi.global_task_app_time, 1, MPI_DOUBLE,
               mpiPi.collectorRank, mpiPi.comm);

  if (report_style == mpiPi_style_verbose || report_style == mpiPi_style_both)
    {
      PMPI_Gather (mpiPi.hostname, MPIPI_HOSTNAME_LEN_MAX, MPI_CHAR,
                   mpiPi.global_task_hostnames, MPIPI_HOSTNAME_LEN_MAX,
                   MPI_CHAR, mpiPi.collectorRank, mpiPi.comm);
    }

  return;
}


void
mpiPi_generateReport (int report_style)
{
  mpiP_TIMER dur;
  mpiPi_TIME timer_start, timer_end;
  int mergeResult;

  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_stop(&mpiPi.task_stats);
    }
  mpiPi_stats_mt_merge(&mpiPi.task_stats);
  mpiPi.cumulativeTime = mpiPi_stats_mt_cum_time(&mpiPi.task_stats);
  assert (mpiPi.cumulativeTime >= 0);
  if (mpiPi.enabled)
    {
      mpiPi_stats_mt_timer_start(&mpiPi.task_stats);
    }

  if (time (&mpiPi.stop_timeofday) == (time_t) - 1)
    {
      mpiPi_msg_warn ("Could not get time of day from time()\n");
    }

  /* collect results and publish */
  mpiPi_msg_debug0 ("starting collect_basics\n");

  mpiPi_GETTIME (&timer_start);
  mpiPi_collect_basics (report_style);
  mpiPi_GETTIME (&timer_end);
  dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);

  mpiPi_msg_debug0 ("TIMING : collect_basics_time is %12.6f\n", dur);

  mpiPi_msg_debug0 ("starting mergeResults\n");

  mpiPi_GETTIME (&timer_start);
  mergeResult = mpiPi_mergeResults ();
  if (mergeResult == 1 && mpiPi.reportStackDepth == 0)
    mergeResult = mpiPi_insert_MPI_records ();
  if (mergeResult == 1)
    mergeResult = mpiPi_mergeCollectiveStats ();
  if (mergeResult == 1)
    mergeResult = mpiPi_mergept2ptStats ();
  mpiPi_GETTIME (&timer_end);
  dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);

  mpiPi_msg_debug0 ("TIMING : merge time is          %12.6f\n", dur);
  mpiPi_msg_debug0 ("starting publishResults\n");

  if (mergeResult == 1)
    {
      mpiPi_GETTIME (&timer_start);
      if (mpiPi.report_style == mpiPi_style_both)
        {
          mpiPi_publishResults (mpiPi_style_concise);
          mpiPi_publishResults (mpiPi_style_verbose);
        }
      else
        mpiPi_publishResults (report_style);
      mpiPi_GETTIME (&timer_end);
      dur = (mpiPi_GETTIMEDIFF (&timer_end, &timer_start) / 1000000.0);
      mpiPi_msg_debug0 ("TIMING : publish time is        %12.6f\n", dur);
    }
}


void
mpiPi_finalize ()
{
  if (mpiPi.disable_finalize_report == 0)
    mpiPi_generateReport (mpiPi.report_style);

  mpiPi_stats_mt_fini(&mpiPi.task_stats);

  if (mpiPi.global_task_app_time != NULL)
    free (mpiPi.global_task_app_time);

  if (mpiPi.global_task_mpi_time != NULL)
    free (mpiPi.global_task_mpi_time);

  if (mpiPi.global_task_hostnames != NULL)
    free (mpiPi.global_task_hostnames);

  /*  Could do a lot of housekeeping before calling PMPI_Finalize()
   *  but is it worth the additional work?
   *  For instance:
   h_gather_data (mpiPi.global_callsite_stats_agg, &ac, (void ***) &av);
   for (i = 0; (i < 20) && (i < ac); i++)
   {
   if (av[i]->siteData != NULL )
   free (av[i]->siteData);
   }
   */

  return;
}


void
mpiPi_update_callsite_stats (mpiPi_mt_stat_tls_t *tls,
                             unsigned op, unsigned rank, void **pc,
                             double dur, double sendSize, double ioSize,
                             double rmaSize)
{
  int i;
  callsite_stats_t *csp = NULL;
  callsite_stats_t key;

  mpiPi_stats_mt_cs_upd(tls, op, rank, pc, dur,
                        sendSize, ioSize, rmaSize);
}

void
mpiPi_update_collective_stats (mpiPi_mt_stat_tls_t *tls, int op, double dur, double size,
                               MPI_Comm * comm)
{
  mpiPi_stats_mt_coll_upd(tls, op, dur, size, comm);
}

void
mpiPi_update_pt2pt_stats (mpiPi_mt_stat_tls_t *tls,
                          int op, double dur, double size,
                          MPI_Comm * comm)
{
  mpiPi_stats_mt_pt2pt_upd(tls, op, dur, size, comm);
}

#endif /* } ifndef ENABLE_API_ONLY */



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
