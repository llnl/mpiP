/* Simple MPI_Isendrecv test. */

#include <mpi.h>
#include <stdio.h>

int
main (int argc, char **argv)
{
  MPI_Request request;
  int rank;
  int received = -1;
  int rc;

  MPI_Init (&argc, &argv);
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);

  /* Sending to self keeps this test valid with one MPI process as well. */
  rc = MPI_Isendrecv (&rank, 1, MPI_INT, rank, 0,
                      &received, 1, MPI_INT, rank, 0,
                      MPI_COMM_WORLD, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);

  if (rc != MPI_SUCCESS || received != rank)
    {
      fprintf (stderr, "rank %d: MPI_Isendrecv failed\n", rank);
      MPI_Abort (MPI_COMM_WORLD, rc == MPI_SUCCESS ? 1 : rc);
    }

  MPI_Finalize ();
  return 0;
}
