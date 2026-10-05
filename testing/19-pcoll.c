/* Simple MPI persistent collective test. */

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int
main (int argc, char **argv)
{
  MPI_Request request;
  int rank, size;
  int value, result;
  int *gathered;
  int expected_sum;
  int i;
  int rc;

  MPI_Init (&argc, &argv);
  MPI_Comm_rank (MPI_COMM_WORLD, &rank);
  MPI_Comm_size (MPI_COMM_WORLD, &size);

  gathered = (int *) malloc ((size_t) size * sizeof (*gathered));
  if (gathered == NULL)
    MPI_Abort (MPI_COMM_WORLD, 1);

  expected_sum = size * (size - 1) / 2;

  value = rank;
  result = -1;
  rc = MPI_Allreduce_init (&value, &result, 1, MPI_INT, MPI_SUM,
                           MPI_COMM_WORLD, MPI_INFO_NULL, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS && result != expected_sum)
    rc = MPI_ERR_OTHER;
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&request);

  value = rank == 0 ? size : -1;
  if (rc == MPI_SUCCESS)
    rc = MPI_Bcast_init (&value, 1, MPI_INT, 0, MPI_COMM_WORLD,
                         MPI_INFO_NULL, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS && value != size)
    rc = MPI_ERR_OTHER;
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&request);

  if (rc == MPI_SUCCESS)
    rc = MPI_Allgather_init (&rank, 1, MPI_INT, gathered, 1, MPI_INT,
                             MPI_COMM_WORLD, MPI_INFO_NULL, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS)
    for (i = 0; i < size; i++)
      if (gathered[i] != i)
        {
          rc = MPI_ERR_OTHER;
          break;
        }
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&request);

  value = rank;
  result = -1;
  if (rc == MPI_SUCCESS)
    rc = MPI_Reduce_init (&value, &result, 1, MPI_INT, MPI_SUM, 0,
                          MPI_COMM_WORLD, MPI_INFO_NULL, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS && rank == 0 && result != expected_sum)
    rc = MPI_ERR_OTHER;
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&request);

  if (rc == MPI_SUCCESS)
    rc = MPI_Barrier_init (MPI_COMM_WORLD, MPI_INFO_NULL, &request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Start (&request);
  if (rc == MPI_SUCCESS)
    rc = MPI_Wait (&request, MPI_STATUS_IGNORE);
  if (rc == MPI_SUCCESS)
    rc = MPI_Request_free (&request);

  if (rc != MPI_SUCCESS)
    {
      fprintf (stderr, "rank %d: persistent collective failed\n", rank);
      MPI_Abort (MPI_COMM_WORLD, rc);
    }

  free (gathered);
  MPI_Finalize ();
  return 0;
}
