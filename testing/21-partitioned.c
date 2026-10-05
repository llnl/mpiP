/* Simple MPI partitioned communication test. */

#include <mpi.h>
#include <stdio.h>

int
main (int argc, char **argv)
{
  MPI_Request send_request, recv_request;
  int rank;
  int received = -1;
  int arrived;
  int rc;

  MPI_Init (&argc, &argv);
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);

  /* A self transfer also permits this test to run with one MPI process. */
  rc = MPI_Psend_init (&rank, 1, 1, MPI_INT, rank, 0,
                       MPI_COMM_WORLD, MPI_INFO_NULL, &send_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Precv_init (&received, 1, 1, MPI_INT, rank, 0,
                         MPI_COMM_WORLD, MPI_INFO_NULL, &recv_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&recv_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&send_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Pready (0, send_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Parrived (recv_request, 0, &arrived);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&recv_request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&send_request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&recv_request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&send_request);

  if (rc != MPI_SUCCESS || received != rank)
    {
      fprintf (stderr, "rank %d: partitioned communication failed\n", rank);
      MPI_Abort (MPI_COMM_WORLD, rc == MPI_SUCCESS ? 1 : rc);
    }

  MPI_Finalize ();
  return 0;
}
