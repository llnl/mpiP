#!/usr/local/bin/python
# -*- python -*-
#
#   mpiP MPI Profiler ( http://llnl.github.io/mpiP )
#
#   Please see COPYRIGHT AND LICENSE information at the end of this file.
#
#
#   make-wrappers.py -- parse the mpi prototype file and generate a
#     series of output files, which include the wrappers for profiling
#     layer and other data structures.
#
#   $Id$
#

from __future__ import print_function
import sys
import os
import copy
import re
import time
import getopt
import socket
import pdb

cnt = 0
fdict = {}
lastFunction = "NULL"
verbose = 0
baseID = 1000

messParamDict = {

    ( "MPI_Allgather", "sendcount"):1,
    ( "MPI_Allgather", "sendtype"):2,
    ( "MPI_Allgather_init", "sendcount"):1,
    ( "MPI_Allgather_init", "sendtype"):2,
    ( "MPI_Allgatherv", "sendcount"):1,
    ( "MPI_Allgatherv", "sendtype"):2,
    ( "MPI_Allgatherv_init", "sendcount"):1,
    ( "MPI_Allgatherv_init", "sendtype"):2,
    ( "MPI_Allreduce", "count"):1,
    ( "MPI_Allreduce", "datatype"):2,
    ( "MPI_Alltoall", "sendcount"):1,
    ( "MPI_Alltoall", "sendtype"):2,
    ( "MPI_Bcast", "count"):1,
    ( "MPI_Bcast", "datatype"):2,
    ( "MPI_Bsend", "count"):1,
    ( "MPI_Bsend", "datatype"):2,
    ( "MPI_Gather", "sendcnt"):1,
    ( "MPI_Gather", "sendtype"):2,
    ( "MPI_Gatherv", "sendcnt"):1,
    ( "MPI_Gatherv", "sendtype"):2,
    ( "MPI_Ialltoall", "sendcount"):1,
    ( "MPI_Ialltoall", "sendtype"):2,
    ( "MPI_Ialltoallv", "sendtype"):2,
    ( "MPI_Iallgather", "sendcount"):1,
    ( "MPI_Iallgather", "sendtype"):2,
    ( "MPI_Iallgatherv", "sendcount"):1,
    ( "MPI_Iallgatherv", "sendtype"):2,
    ( "MPI_Iallreduce", "count"):1,
    ( "MPI_Iallreduce", "datatype"):2,
    ( "MPI_Ibcast", "count"):1,
    ( "MPI_Ibcast", "datatype"):2,
    ( "MPI_Iexscan", "count"):1,
    ( "MPI_Iexscan", "datatype"):2,
    ( "MPI_Igather", "sendcount"):1,
    ( "MPI_Igather", "sendtype"):2,
    ( "MPI_Igatherv", "sendcount"):1,
    ( "MPI_Igatherv", "sendtype"):2,
    ( "MPI_Ireduce", "count"):1,
    ( "MPI_Ireduce", "datatype"):2,
    ( "MPI_Ireduce_scatter_block", "recvcount"):1,
    ( "MPI_Ireduce_scatter_block", "datatype"):2,
    ( "MPI_Ireduce_scatter", "datatype"):2,
    ( "MPI_Ibsend", "count"):1,
    ( "MPI_Ibsend", "datatype"):2,
    ( "MPI_Irsend", "count"):1,
    ( "MPI_Irsend", "datatype"):2,
    ( "MPI_Iscan", "count"):1,
    ( "MPI_Iscan", "datatype"):2,
    ( "MPI_Iscatter", "sendcount"):1,
    ( "MPI_Iscatter", "sendtype"):2,
    ( "MPI_Iscatterv", "sendtype"):2,
    ( "MPI_Isend", "count"):1,
    ( "MPI_Isend", "datatype"):2,
    ( "MPI_Issend", "count"):1,
    ( "MPI_Issend", "datatype"):2,
    ( "MPI_Reduce", "count"):1,
    ( "MPI_Reduce", "datatype"):2,
    ( "MPI_Rsend", "count"):1,
    ( "MPI_Rsend", "datatype"):2,
    ( "MPI_Scan", "count"):1,
    ( "MPI_Scan", "datatype"):2,
    ( "MPI_Scatter", "sendcnt"):1,
    ( "MPI_Scatter", "sendtype"):2,
    ( "MPI_Send", "count"):1,
    ( "MPI_Send", "datatype"):2,
    ( "MPI_Sendrecv", "sendcount"):1,
    ( "MPI_Sendrecv", "sendtype"):2,
    ( "MPI_Sendrecv_replace", "count"):1,
    ( "MPI_Sendrecv_replace", "datatype"):2,
    ( "MPI_Ssend", "count"):1,
    ( "MPI_Ssend", "datatype"):2
    }


vectorsendParamDict = {

    ( "MPI_Ialltoallv", "sendcounts"):1,
    ( "MPI_Ialltoallw", "sendcounts"):1,
    ( "MPI_Ireduce_scatter", "recvcounts"):1,
    ( "MPI_Iscatterv", "sendcounts"):1,
    }

vectortypeParamDict = {

    ( "MPI_Ialltoallw", "sendtypes"):2
    }


ioParamDict = {

    ( "MPI_File_read", "count"):1,
    ( "MPI_File_read", "datatype"):2,
    ( "MPI_File_read_all", "count"):1,
    ( "MPI_File_read_all", "datatype"):2,
    ( "MPI_File_read_at", "count"):1,
    ( "MPI_File_read_at", "datatype"):2,
    ( "MPI_File_write", "count"):1,
    ( "MPI_File_write", "datatype"):2,
    ( "MPI_File_write_all", "count"):1,
    ( "MPI_File_write_all", "datatype"):2,
    ( "MPI_File_write_at", "count"):1,
    ( "MPI_File_write_at", "datatype"):2
    }

rmaParamDict = {

    ( "MPI_Accumulate", "target_count"):1,
    ( "MPI_Accumulate", "target_datatype"):2,
    ( "MPI_Compare_and_swap", "datatype"):2,
    ( "MPI_Fetch_and_op", "datatype"):2,
    ( "MPI_Get", "origin_count"):2,
    ( "MPI_Get", "origin_datatype"):2,
    ( "MPI_Get_accumulate", "target_count"):1,
    ( "MPI_Get_accumulate", "target_datatype"):2,
    ( "MPI_Put", "origin_count"):1,
    ( "MPI_Put", "origin_datatype"):2,
    ( "MPI_Raccumulate", "target_count"):1,
    ( "MPI_Raccumulate", "target_datatype"):2,
    ( "MPI_Rget", "origin_count"):1,
    ( "MPI_Rget", "origin_datatype"):2,
    ( "MPI_Rput", "origin_count"):1,
    ( "MPI_Rput", "origin_datatype"):2,
    ( "MPI_Rget_accumulate", "target_count"):1,
    ( "MPI_Rget_accumulate", "target_datatype"):2
    }

noDefineList = [
    "MPI_Pcontrol"
    ]

opaqueInArgDict = {
  ("MPI_Abort", "comm"):"MPI_Comm",
  ("MPI_Accumulate", "origin_datatype"):"MPI_Datatype",
  ("MPI_Accumulate", "target_datatype"):"MPI_Datatype",
  ("MPI_Accumulate", "op"):"MPI_Op",
  ("MPI_Accumulate", "win"):"MPI_Win",
  ("MPI_Allgather", "comm"):"MPI_Comm",
  ("MPI_Allgather", "recvtype"):"MPI_Datatype",
  ("MPI_Allgather", "sendtype"):"MPI_Datatype",
  ("MPI_Allgather_init", "comm"):"MPI_Comm",
  ("MPI_Allgather_init", "recvtype"):"MPI_Datatype",
  ("MPI_Allgather_init", "sendtype"):"MPI_Datatype",
  ("MPI_Allgather_init", "info"):"MPI_Info",
  ("MPI_Allgather_init", "request"):"MPI_Request",
  ("MPI_Allgatherv", "comm"):"MPI_Comm",
  ("MPI_Allgatherv", "recvtype"):"MPI_Datatype",
  ("MPI_Allgatherv", "sendtype"):"MPI_Datatype",
  ("MPI_Allgatherv_init", "comm"):"MPI_Comm",
  ("MPI_Allgatherv_init", "recvtype"):"MPI_Datatype",
  ("MPI_Allgatherv_init", "sendtype"):"MPI_Datatype",
  ("MPI_Allgatherv_init", "info"):"MPI_Info",
  ("MPI_Allgatherv_init", "request"):"MPI_Request",
  ("MPI_Allreduce", "comm"):"MPI_Comm",
  ("MPI_Allreduce", "datatype"):"MPI_Datatype",
  ("MPI_Allreduce", "op"):"MPI_Op",
  ("MPI_Allreduce_init", "comm"):"MPI_Comm",
  ("MPI_Allreduce_init", "datatype"):"MPI_Datatype",
  ("MPI_Allreduce_init", "op"):"MPI_Op",
  ("MPI_Allreduce_init", "info"):"MPI_Info",
  ("MPI_Allreduce_init", "request"):"MPI_Request",
  ("MPI_Alltoall", "comm"):"MPI_Comm",
  ("MPI_Alltoall", "recvtype"):"MPI_Datatype",
  ("MPI_Alltoall", "sendtype"):"MPI_Datatype",
  ("MPI_Alltoall_init", "comm"):"MPI_Comm",
  ("MPI_Alltoall_init", "recvtype"):"MPI_Datatype",
  ("MPI_Alltoall_init", "sendtype"):"MPI_Datatype",
  ("MPI_Alltoall_init", "info"):"MPI_Info",
  ("MPI_Alltoall_init", "request"):"MPI_Request",
  ("MPI_Alltoallv", "comm"):"MPI_Comm",
  ("MPI_Alltoallv", "recvtype"):"MPI_Datatype",
  ("MPI_Alltoallv", "sendtype"):"MPI_Datatype",
  ("MPI_Alltoallv_init", "comm"):"MPI_Comm",
  ("MPI_Alltoallv_init", "recvtype"):"MPI_Datatype",
  ("MPI_Alltoallv_init", "sendtype"):"MPI_Datatype",
  ("MPI_Alltoallv_init", "info"):"MPI_Info",
  ("MPI_Alltoallv_init", "request"):"MPI_Request",
  ("MPI_Alltoallw_init", "comm"):"MPI_Comm",
  ("MPI_Alltoallw_init", "recvtype"):"MPI_Datatype",
  ("MPI_Alltoallw_init", "sendtype"):"MPI_Datatype",
  ("MPI_Alltoallw_init", "info"):"MPI_Info",
  ("MPI_Alltoallw_init", "request"):"MPI_Request",
  ("MPI_Barrier", "comm"):"MPI_Comm",
  ("MPI_Barrier_init", "comm"):"MPI_Comm",
  ("MPI_Barrier_init", "info"):"MPI_Info",
  ("MPI_Barrier_init", "request"):"MPI_Request",
  ("MPI_Bcast", "datatype"):"MPI_Datatype",
  ("MPI_Bcast", "comm"):"MPI_Comm",
  ("MPI_Bcast_init", "datatype"):"MPI_Datatype",
  ("MPI_Bcast_init", "comm"):"MPI_Comm",
  ("MPI_Bcast_init", "info"):"MPI_Info",
  ("MPI_Bcast_init", "request"):"MPI_Request",
  ("MPI_Bsend", "comm"):"MPI_Comm",
  ("MPI_Bsend", "datatype"):"MPI_Datatype",
  ("MPI_Bsend_init", "comm"):"MPI_Comm",
  ("MPI_Bsend_init", "datatype"):"MPI_Datatype",
  ("MPI_Cancel", "request"):"MPI_Request",
  ("MPI_Cart_coords", "comm"):"MPI_Comm",
  ("MPI_Cart_create", "comm_old"):"MPI_Comm",
  ("MPI_Cart_get", "comm"):"MPI_Comm",
  ("MPI_Cart_map", "comm_old"):"MPI_Comm",
  ("MPI_Cart_rank", "comm"):"MPI_Comm",
  ("MPI_Cart_shift", "comm"):"MPI_Comm",
  ("MPI_Cart_sub", "comm"):"MPI_Comm",
  ("MPI_Cartdim_get", "comm"):"MPI_Comm",
  ("MPI_Comm_delete_attr", "comm"):"MPI_Comm",
  ("MPI_Comm_get_attr", "comm"):"MPI_Comm",
  ("MPI_Comm_set_attr", "comm"):"MPI_Comm",
  ("MPI_Comm_compare", "comm1"):"MPI_Comm",
  ("MPI_Comm_compare", "comm2"):"MPI_Comm",
  ("MPI_Comm_create", "comm"):"MPI_Comm",
  ("MPI_Comm_create", "group"):"MPI_Group",
  ("MPI_Comm_dup", "comm"):"MPI_Comm",
  ("MPI_Comm_free", "commp"):"MPI_Comm",
  ("MPI_Comm_group", "comm"):"MPI_Comm",
  ("MPI_Comm_rank", "comm"):"MPI_Comm",
  ("MPI_Comm_remote_group", "comm"):"MPI_Comm",
  ("MPI_Comm_remote_size", "comm"):"MPI_Comm",
  ("MPI_Comm_size", "comm"):"MPI_Comm",
  ("MPI_Comm_split", "comm"):"MPI_Comm",
  ("MPI_Comm_test_inter", "comm"):"MPI_Comm",
  ("MPI_Compare_and_swap", "datatype"):"MPI_Datatype",
  ("MPI_Compare_and_swap", "win"):"MPI_Win",
  ("MPI_Comm_get_errhandler", "comm"):"MPI_Comm",
  ("MPI_Comm_set_errhandler", "comm"):"MPI_Comm",
  ("MPI_Exscan_init", "datatype"):"MPI_Datatype",
  ("MPI_Exscan_init", "op"):"MPI_Op",
  ("MPI_Exscan_init", "comm"):"MPI_Comm",
  ("MPI_Exscan_init", "info"):"MPI_Info",
  ("MPI_Exscan_init", "request"):"MPI_Request",
  ("MPI_Fetch_and_op", "datatype"):"MPI_Datatype",
  ("MPI_Fetch_and_op", "op"):"MPI_Op",
  ("MPI_Fetch_and_op", "win"):"MPI_Win",
  ("MPI_File_close", "fh"):"MPI_File",
  ("MPI_File_open", "comm"):"MPI_Comm",
  ("MPI_File_open", "info"):"MPI_Info",
  ("MPI_File_delete", "info"):"MPI_Info",
  ("MPI_File_preallocate", "fh"):"MPI_File",
  ("MPI_File_set_size", "fh"):"MPI_File",
  ("MPI_File_get_group", "fh"):"MPI_File",
  ("MPI_File_get_amode", "fh"):"MPI_File",
  ("MPI_File_set_info", "fh"):"MPI_File",
  ("MPI_File_set_info", "info"):"MPI_Info",
  ("MPI_File_get_info", "fh"):"MPI_File",
  ("MPI_File_read", "fh"):"MPI_File",
  ("MPI_File_read", "datatype"):"MPI_Datatype",
  ("MPI_File_read", "status"):"MPI_Status",
  ("MPI_File_read_all", "fh"):"MPI_File",
  ("MPI_File_read_all", "datatype"):"MPI_Datatype",
  ("MPI_File_read_all", "status"):"MPI_Status",
  ("MPI_File_read_at", "fh"):"MPI_File",
  ("MPI_File_read_at", "datatype"):"MPI_Datatype",
  ("MPI_File_read_at", "status"):"MPI_Status",
  ("MPI_File_read_at_all", "fh"):"MPI_File",
  ("MPI_File_read_at_all", "datatype"):"MPI_Datatype",
  ("MPI_File_read_at_all", "status"):"MPI",
  ("MPI_File_seek", "fh"):"MPI_File",
  ("MPI_File_set_view", "fh"):"MPI_File",
  ("MPI_File_set_view", "etype"):"MPI_Datatype",
  ("MPI_File_set_view", "filetype"):"MPI_Datatype",
  ("MPI_File_set_view", "info"):"MPI_Info",
  ("MPI_File_get_view", "fh"):"MPI_File",
  ("MPI_File_write", "fh"):"MPI_File",
  ("MPI_File_write", "datatype"):"MPI_Datatype",
  ("MPI_File_write", "status"):"MPI_Status",
  ("MPI_File_write_all", "fh"):"MPI_File",
  ("MPI_File_write_all", "datatype"):"MPI_Datatype",
  ("MPI_File_write_all", "status"):"MPI_Status",
  ("MPI_File_write_at", "fh"):"MPI_File",
  ("MPI_File_write_at", "datatype"):"MPI_Datatype",
  ("MPI_File_write_at", "status"):"MPI_Status",
  ("MPI_File_write_at_all", "fh"):"MPI_File",
  ("MPI_File_write_at_all", "datatype"):"MPI_Datatype",
  ("MPI_File_write_at_all", "status"):"MPI_Status",
  ("MPI_File_get_position", "fh"):"MPI_File",
  ("MPI_File_get_byte_offset", "fh"):"MPI_File",
  ("MPI_File_get_size", "fh"):"MPI_File",
  ("MPI_File_sync", "fh"):"MPI_File",
  ("MPI_Gather", "comm"):"MPI_Comm",
  ("MPI_Gather", "recvtype"):"MPI_Datatype",
  ("MPI_Gather", "sendtype"):"MPI_Datatype",
  ("MPI_Gather_init", "comm"):"MPI_Comm",
  ("MPI_Gather_init", "recvtype"):"MPI_Datatype",
  ("MPI_Gather_init", "sendtype"):"MPI_Datatype",
  ("MPI_Gather_init", "info"):"MPI_Info",
  ("MPI_Gather_init", "request"):"MPI_Request",
  ("MPI_Gatherv", "comm"):"MPI_Comm",
  ("MPI_Gatherv", "recvtype"):"MPI_Datatype",
  ("MPI_Gatherv", "sendtype"):"MPI_Datatype",
  ("MPI_Gatherv_init", "comm"):"MPI_Comm",
  ("MPI_Gatherv_init", "recvtype"):"MPI_Datatype",
  ("MPI_Gatherv_init", "sendtype"):"MPI_Datatype",
  ("MPI_Gatherv_init", "info"):"MPI_Info",
  ("MPI_Gatherv_init", "request"):"MPI_Request",
  ("MPI_Get", "origin_datatype"):"MPI_Datatype",
  ("MPI_Get", "target_datatype"):"MPI_Datatype",
  ("MPI_Get", "win"):"MPI_Win",
  ("MPI_Get_accumulate", "origin_datatype"):"MPI_Datatype",
  ("MPI_Get_accumulate", "result_datatype"):"MPI_Datatype",
  ("MPI_Get_accumulate", "target_datatype"):"MPI_Datatype",
  ("MPI_Get_accumulate", "op"):"MPI_Op",
  ("MPI_Get_accumulate", "win"):"MPI_Win",
  ("MPI_Get_count", "datatype"):"MPI_Datatype",
  ("MPI_Get_elements", "datatype"):"MPI_Datatype",
  ("MPI_Graph_create", "comm_old"):"MPI_Comm",
  ("MPI_Graph_get", "comm"):"MPI_Comm",
  ("MPI_Graph_map", "comm_old"):"MPI_Comm",
  ("MPI_Graph_neighbors", "comm"):"MPI_Comm",
  ("MPI_Graph_neighbors_count", "comm"):"MPI_Comm",
  ("MPI_Graphdims_get", "comm"):"MPI_Comm",
  ("MPI_Group_compare", "group1"):"MPI_Group",
  ("MPI_Group_compare", "group2"):"MPI_Group",
  ("MPI_Group_difference", "group1"):"MPI_Group",
  ("MPI_Group_difference", "group2"):"MPI_Group",
  ("MPI_Group_excl", "group"):"MPI_Group",
  ("MPI_Group_free", "group"):"MPI_Group",
  ("MPI_Group_incl", "group"):"MPI_Group",
  ("MPI_Group_intersection", "group1"):"MPI_Group",
  ("MPI_Group_intersection", "group2"):"MPI_Group",
  ("MPI_Group_range_excl", "group"):"MPI_Group",
  ("MPI_Group_range_incl", "group"):"MPI_Group",
  ("MPI_Group_rank", "group"):"MPI_Group",
  ("MPI_Group_size", "group"):"MPI_Group",
  ("MPI_Group_translate_ranks", "group_a"):"MPI_Group",
  ("MPI_Group_translate_ranks", "group_b"):"MPI_Group",
  ("MPI_Group_union", "group1"):"MPI_Group",
  ("MPI_Group_union", "group2"):"MPI_Group",
  ("MPI_Iallgather", "sendtype"):"MPI_Datatype",
  ("MPI_Iallgather", "recvtype"):"MPI_Datatype",
  ("MPI_Iallgather", "comm"):"MPI_Comm",
  ("MPI_Iallgatherv", "sendtype"):"MPI_Datatype",
  ("MPI_Iallgatherv", "recvtype"):"MPI_Datatype",
  ("MPI_Iallgatherv", "comm"):"MPI_Comm",
  ("MPI_Iallreduce", "datatype"):"MPI_Datatype",
  ("MPI_Iallreduce", "op"):"MPI_Op",
  ("MPI_Iallreduce", "comm"):"MPI_Comm",
  ("MPI_Ialltoall", "sendtype"):"MPI_Datatype",
  ("MPI_Ialltoall", "recvtype"):"MPI_Datatype",
  ("MPI_Ialltoall", "comm"):"MPI_Comm",
  ("MPI_Ialltoallv", "sendtype"):"MPI_Datatype",
  ("MPI_Ialltoallv", "recvtype"):"MPI_Datatype",
  ("MPI_Ialltoallv", "comm"):"MPI_Comm",
  ("MPI_Ialltoallw", "sendtype"):"MPI_Datatype",
  ("MPI_Ialltoallw", "recvtype"):"MPI_Datatype",
  ("MPI_Ialltoallw", "comm"):"MPI_Comm",
  ("MPI_Ibarrier", "comm"):"MPI_Comm",
  ("MPI_Ibcast", "datatype"):"MPI_Datatype",
  ("MPI_Ibcast", "comm"):"MPI_Comm",
  ("MPI_Iexscan", "datatype"):"MPI_Datatype",
  ("MPI_Iexscan", "op"):"MPI_Op",
  ("MPI_Iexscan", "comm"):"MPI_Comm",
  ("MPI_Igather", "sendtype"):"MPI_Datatype",
  ("MPI_Igather", "recvtype"):"MPI_Datatype",
  ("MPI_Igather", "comm"):"MPI_Comm",
  ("MPI_Igatherv", "sendtype"):"MPI_Datatype",
  ("MPI_Igatherv", "recvtype"):"MPI_Datatype",
  ("MPI_Igatherv", "comm"):"MPI_Comm",
  ("MPI_Ibsend", "comm"):"MPI_Comm",
  ("MPI_Ibsend", "datatype"):"MPI_Datatype",
  ("MPI_Intercomm_create", "local_comm"):"MPI_Comm",
  ("MPI_Intercomm_create", "peer_comm"):"MPI_Comm",
  ("MPI_Intercomm_merge", "comm"):"MPI_Comm",
  ("MPI_Iprobe", "comm"):"MPI_Comm",
  ("MPI_Iprobe", "status"):"MPI_Status",
  ("MPI_Irecv", "comm"):"MPI_Comm",
  ("MPI_Irecv", "datatype"):"MPI_Datatype",
  ("MPI_Ireduce", "datatype"):"MPI_Datatype",
  ("MPI_Ireduce", "op"):"MPI_Op",
  ("MPI_Ireduce", "comm"):"MPI_Comm",
  ("MPI_Ireduce_scatter_block", "datatype"):"MPI_Datatype",
  ("MPI_Ireduce_scatter_block", "op"):"MPI_Op",
  ("MPI_Ireduce_scatter_block", "comm"):"MPI_Comm",
  ("MPI_Ireduce_scatter", "datatype"):"MPI_Datatype",
  ("MPI_Ireduce_scatter", "op"):"MPI_Op",
  ("MPI_Ireduce_scatter", "comm"):"MPI_Comm",
  ("MPI_Irsend", "comm"):"MPI_Comm",
  ("MPI_Irsend", "datatype"):"MPI_Datatype",
  ("MPI_Iscan", "datatype"):"MPI_Datatype",
  ("MPI_Iscan", "op"):"MPI_Op",
  ("MPI_Iscan", "comm"):"MPI_Comm",
  ("MPI_Iscatter", "sendtype"):"MPI_Datatype",
  ("MPI_Iscatter", "recvtype"):"MPI_Datatype",
  ("MPI_Iscatter", "comm"):"MPI_Comm",
  ("MPI_Iscatterv", "sendtype"):"MPI_Datatype",
  ("MPI_Iscatterv", "recvtype"):"MPI_Datatype",
  ("MPI_Iscatterv", "comm"):"MPI_Comm",
  ("MPI_Isend", "comm"):"MPI_Comm",
  ("MPI_Isend", "datatype"):"MPI_Datatype",
  ("MPI_Isendrecv", "comm"):"MPI_Comm",
  ("MPI_Isendrecv", "recvtag"):"MPI_Datatype",
  ("MPI_Isendrecv", "recvtype"):"MPI_Datatype",
  ("MPI_Isendrecv", "sendtype"):"MPI_Datatype",
  ("MPI_Isendrecv", "request"):"MPI_Request",
  ("MPI_Isendrecv_replace", "comm"):"MPI_Comm",
  ("MPI_Isendrecv_replace", "datatype"):"MPI_Datatype",
  ("MPI_Isendrecv_replace", "request"):"MPI_Request",
  ("MPI_Issend", "comm"):"MPI_Comm",
  ("MPI_Issend", "datatype"):"MPI_Datatype",
  ("MPI_Pack", "comm"):"MPI_Comm",
  ("MPI_Pack", "datatype"):"MPI_Datatype",
  ("MPI_Pack_size", "comm"):"MPI_Comm",
  ("MPI_Pack_size", "datatype"):"MPI_Datatype",
  ("MPI_Parrived", "request"):"MPI_Request",
  ("MPI_Pready", "request"):"MPI_Request",
  ("MPI_Pready_list", "request"):"MPI_Request",
  ("MPI_Pready_range", "request"):"MPI_Request",
  ("MPI_Precv_init", "datatype"):"MPI_Datatype",
  ("MPI_Precv_init", "comm"):"MPI_Comm",
  ("MPI_Precv_init", "info"):"MPI_Info",
  ("MPI_Precv_init", "request"):"MPI_Request",
  ("MPI_Psend_init", "datatype"):"MPI_Datatype",
  ("MPI_Psend_init", "comm"):"MPI_Comm",
  ("MPI_Psend_init", "info"):"MPI_Info",
  ("MPI_Psend_init", "request"):"MPI_Request",
  ("MPI_Probe", "comm"):"MPI_Comm",
  ("MPI_Probe", "status"):"MPI_Status",
  ("MPI_Put", "origin_datatype"):"MPI_Datatype",
  ("MPI_Put", "target_datatype"):"MPI_Datatype",
  ("MPI_Put", "win"):"MPI_Win",
  ("MPI_Raccumulate", "origin_datatype"):"MPI_Datatype",
  ("MPI_Raccumulate", "target_datatype"):"MPI_Datatype",
  ("MPI_Raccumulate", "op"):"MPI_Op",
  ("MPI_Raccumulate", "win"):"MPI_Win",
  ("MPI_Raccumulate", "request"):"MPI_Request",
  ("MPI_Recv", "comm"):"MPI_Comm",
  ("MPI_Recv", "datatype"):"MPI_Datatype",
  ("MPI_Recv", "status"):"MPI_Status",
  ("MPI_Recv_init", "comm"):"MPI_Comm",
  ("MPI_Recv_init", "datatype"):"MPI_Datatype",
  ("MPI_Reduce", "comm"):"MPI_Comm",
  ("MPI_Reduce", "datatype"):"MPI_Datatype",
  ("MPI_Reduce", "op"):"MPI_Op",
  ("MPI_Reduce_init", "comm"):"MPI_Comm",
  ("MPI_Reduce_init", "datatype"):"MPI_Datatype",
  ("MPI_Reduce_init", "op"):"MPI_Op",
  ("MPI_Reduce_init", "info"):"MPI_Info",
  ("MPI_Reduce_init", "request"):"MPI_Request",
  ("MPI_Reduce_scatter", "comm"):"MPI_Comm",
  ("MPI_Reduce_scatter", "datatype"):"MPI_Datatype",
  ("MPI_Reduce_scatter", "op"):"MPI_Op",
  ("MPI_Reduce_scatter_init", "datatype"):"MPI_Datatype",
  ("MPI_Reduce_scatter_init", "op"):"MPI_Op",
  ("MPI_Reduce_scatter_init", "comm"):"MPI_Comm",
  ("MPI_Reduce_scatter_init", "info"):"MPI_Info",
  ("MPI_Reduce_scatter_init", "request"):"MPI_Request",
  ("MPI_Reduce_scatter_block_init", "datatype"):"MPI_Datatype",
  ("MPI_Reduce_scatter_block_init", "op"):"MPI_Op",
  ("MPI_Reduce_scatter_block_init", "comm"):"MPI_Comm",
  ("MPI_Reduce_scatter_block_init", "info"):"MPI_Info",
  ("MPI_Reduce_scatter_block_init", "request"):"MPI_Request",
  ("MPI_Request_free", "request"):"MPI_Request",
  ("MPI_Rget", "origin_datatype"):"MPI_Datatype",
  ("MPI_Rget", "target_datatype"):"MPI_Datatype",
  ("MPI_Rget", "win"):"MPI_Win",
  ("MPI_Rget", "request"):"MPI_Request",
  ("MPI_Rget_accumulate", "origin_datatype"):"MPI_Datatype",
  ("MPI_Rget_accumulate", "result_datatype"):"MPI_Datatype",
  ("MPI_Rget_accumulate", "target_datatype"):"MPI_Datatype",
  ("MPI_Rget_accumulate", "op"):"MPI_Op",
  ("MPI_Rget_accumulate", "win"):"MPI_Win",
  ("MPI_Rget_accumulate", "request"):"MPI_Request",
  ("MPI_Rput", "origin_datatype"):"MPI_Datatype",
  ("MPI_Rput", "target_datatype"):"MPI_Datatype",
  ("MPI_Rput", "win"):"MPI_Win",
  ("MPI_Rput", "request"):"MPI_Request",
  ("MPI_Rsend", "comm"):"MPI_Comm",
  ("MPI_Rsend", "datatype"):"MPI_Datatype",
  ("MPI_Rsend_init", "comm"):"MPI_Comm",
  ("MPI_Rsend_init", "datatype"):"MPI_Datatype",
  ("MPI_Scan", "comm"):"MPI_Comm",
  ("MPI_Scan", "op"):"MPI_Op",
  ("MPI_Scan", "datatype"):"MPI_Datatype",
  ("MPI_Scan_init", "datatype"):"MPI_Datatype",
  ("MPI_Scan_init", "op"):"MPI_Op",
  ("MPI_Scan_init", "comm"):"MPI_Comm",
  ("MPI_Scan_init", "info"):"MPI_Info",
  ("MPI_Scan_init", "request"):"MPI_Request",
  ("MPI_Scatter", "comm"):"MPI_Comm",
  ("MPI_Scatter", "recvtype"):"MPI_Datatype",
  ("MPI_Scatter", "sendtype"):"MPI_Datatype",
  ("MPI_Scatter_init", "comm"):"MPI_Comm",
  ("MPI_Scatter_init", "recvtype"):"MPI_Datatype",
  ("MPI_Scatter_init", "sendtype"):"MPI_Datatype",
  ("MPI_Scatter_init", "info"):"MPI_Info",
  ("MPI_Scatter_init", "request"):"MPI_Request",
  ("MPI_Scatterv", "comm"):"MPI_Comm",
  ("MPI_Scatterv", "recvtype"):"MPI_Datatype",
  ("MPI_Scatterv", "sendtype"):"MPI_Datatype",
  ("MPI_Scatterv_init", "comm"):"MPI_Comm",
  ("MPI_Scatterv_init", "recvtype"):"MPI_Datatype",
  ("MPI_Scatterv_init", "sendtype"):"MPI_Datatype",
  ("MPI_Scatterv_init", "info"):"MPI_Info",
  ("MPI_Scatterv_init", "request"):"MPI_Request",
  ("MPI_Send", "comm"):"MPI_Comm",
  ("MPI_Send", "datatype"):"MPI_Datatype",
  ("MPI_Send_init", "comm"):"MPI_Comm",
  ("MPI_Send_init", "datatype"):"MPI_Datatype",
  ("MPI_Sendrecv", "comm"):"MPI_Comm",
  ("MPI_Sendrecv", "recvtag"):"MPI_Datatype",
  ("MPI_Sendrecv", "recvtype"):"MPI_Datatype",
  ("MPI_Sendrecv", "sendtype"):"MPI_Datatype",
  ("MPI_Sendrecv", "status"):"MPI_Status",
  ("MPI_Sendrecv_replace", "comm"):"MPI_Comm",
  ("MPI_Sendrecv_replace", "datatype"):"MPI_Datatype",
  ("MPI_Sendrecv_replace", "status"):"MPI_Status",
  ("MPI_Ssend", "comm"):"MPI_Comm",
  ("MPI_Ssend", "datatype"):"MPI_Datatype",
  ("MPI_Ssend_init", "comm"):"MPI_Comm",
  ("MPI_Ssend_init", "datatype"):"MPI_Datatype",
  ("MPI_Start", "request"):"MPI_Request",
  ("MPI_Startall", "array_of_requests"):"MPI_Request",
  ("MPI_Test", "request"):"MPI_Request",
  ("MPI_Test", "status"):"MPI_Status",
  ("MPI_Testall", "array_of_requests"):"MPI_Request",
  ("MPI_Testany", "array_of_requests"):"MPI_Request",
  ("MPI_Testany", "status"):"MPI_Status",
  ("MPI_Testsome", "array_of_requests"):"MPI_Request",
  ("MPI_Topo_test", "comm"):"MPI_Comm",
  ("MPI_Type_commit", "datatype"):"MPI_Datatype",
  ("MPI_Type_contiguous", "oldtype"):"MPI_Datatype",
  ("MPI_Type_create_hindexed", "oldtype"):"MPI_Datatype",
  ("MPI_Type_create_hvector", "oldtype"):"MPI_Datatype",
  ("MPI_Type_free", "datatype"):"MPI_Datatype",
  ("MPI_Type_get_contents", "datatype"):"MPI_Datatype",
  ("MPI_Type_get_envelope", "datatype"):"MPI_Datatype",
  ("MPI_Type_get_extent", "datatype"):"MPI_Datatype",
  ("MPI_Type_indexed", "oldtype"):"MPI_Datatype",
  ("MPI_Type_lb", "datatype"):"MPI_Datatype",
  ("MPI_Type_size", "datatype"):"MPI_Datatype",
  ("MPI_Type_create_struct", "array_of_types"):"MPI_Datatype",
  ("MPI_Type_ub", "datatype"):"MPI_Datatype",
  ("MPI_Type_vector", "oldtype"):"MPI_Datatype",
  ("MPI_Unpack", "comm"):"MPI_Comm",
  ("MPI_Unpack", "datatype"):"MPI_Datatype",
  ("MPI_Wait", "request"):"MPI_Request",
  ("MPI_Wait", "status"):"MPI_Status",
  ("MPI_Waitall", "array_of_requests"):"MPI_Request",
  ("MPI_Waitany", "array_of_requests"):"MPI_Request",
  ("MPI_Waitany", "status"):"MPI_Status",
  ("MPI_Waitsome", "array_of_requests"):"MPI_Request",
  ("MPI_Win_allocate", "info"):"MPI_Info",
  ("MPI_Win_allocate", "comm"):"MPI_Comm",
  ("MPI_Win_allocate", "win"):"MPI_Win",
  ("MPI_Win_allocate_shared", "info"):"MPI_Info",
  ("MPI_Win_allocate_shared", "comm"):"MPI_Comm",
  ("MPI_Win_allocate_shared", "win"):"MPI_Win",
  ("MPI_Win_complete", "win"):"MPI_Win",
  ("MPI_Win_create", "info"):"MPI_Info",
  ("MPI_Win_create", "comm"):"MPI_Comm",
  ("MPI_Win_create", "win"):"MPI_Win",
  ("MPI_Win_create_dynamic", "info"):"MPI_Info",
  ("MPI_Win_create_dynamic", "comm"):"MPI_Comm",
  ("MPI_Win_create_dynamic", "win"):"MPI_Win",
  ("MPI_Win_fence", "win"):"MPI_Win",
  ("MPI_Win_flush", "win"):"MPI_Win",
  ("MPI_Win_flush_all", "win"):"MPI_Win",
  ("MPI_Win_flush_local", "win"):"MPI_Win",
  ("MPI_Win_flush_local_all", "win"):"MPI_Win",
  ("MPI_Win_free", "win"):"MPI_Win",
  ("MPI_Win_get_group", "win"):"MPI_Win",
  ("MPI_Win_get_group", "group"):"MPI_Group",
  ("MPI_Win_get_info", "info_used"):"MPI_Info",
  ("MPI_Win_lock_all", "win"):"MPI_Win",
  ("MPI_Win_lock", "win"):"MPI_Win",
  ("MPI_Win_post", "group"):"MPI_Group",
  ("MPI_Win_post", "win"):"MPI_Win",
  ("MPI_Win_set_info", "info"):"MPI_Info",
  ("MPI_Win_start", "group"):"MPI_Group",
  ("MPI_Win_start", "win"):"MPI_Win",
  ("MPI_Win_sync", "win"):"MPI_Win",
  ("MPI_Win_test", "win"):"MPI_Win",
  ("MPI_Win_unlock_all", "win"):"MPI_Win",
  ("MPI_Win_unlock", "win"):"MPI_Win",
  ("MPI_Win_wait", "win"):"MPI_Win"
}

opaqueOutArgDict = {
  ("MPI_Bsend_init", "request"):"MPI_Request",
  ("MPI_Cart_create", "comm_cart"):"MPI_Comm",
  ("MPI_Cart_sub", "comm_new"):"MPI_Comm",
  ("MPI_Comm_create", "comm_out"):"MPI_Comm",
  ("MPI_Comm_dup", "comm_out"):"MPI_Comm",
  ("MPI_Comm_free", "commp"):"MPI_Comm",
  ("MPI_Comm_group", "group"):"MPI_Group",
  ("MPI_Comm_remote_group", "group"):"MPI_Group",
  ("MPI_Comm_split", "comm_out"):"MPI_Comm",
  ("MPI_File_close", "fh"):"MPI_File",
  ("MPI_File_open", "fh"):"MPI_File",
  ("MPI_File_get_group", "group"):"MPI_Group",
  ("MPI_File_get_info", "info"):"MPI_Info",
  ("MPI_File_get_view", "etype"):"MPI_Datatpye",
  ("MPI_File_get_view", "filetype"):"MPI_Datatpye",
  ("MPI_File_get_view", "info"):"MPI_Info",
  ("MPI_File_read", "status"):"MPI_Status",
  ("MPI_File_read_all", "status"):"MPI_Status",
  ("MPI_File_read_at", "status"):"MPI_Status",
  ("MPI_File_read_at_all", "status"):"MPI_Status",
  ("MPI_File_write", "status"):"MPI_Status",
  ("MPI_File_write_all", "status"):"MPI_Status",
  ("MPI_File_write_at", "status"):"MPI_Status",
  ("MPI_File_write_at_all", "status"):"MPI_Status",
  ("MPI_Graph_create", "comm_graph"):"MPI_Comm",
  ("MPI_Group_difference", "group_out"):"MPI_Group",
  ("MPI_Group_excl", "newgroup"):"MPI_Group",
  ("MPI_Group_free", "group"):"MPI_Group",
  ("MPI_Group_incl", "group_out"):"MPI_Group",
  ("MPI_Group_intersection", "group_out"):"MPI_Group",
  ("MPI_Group_range_excl", "newgroup"):"MPI_Group",
  ("MPI_Group_range_incl", "newgroup"):"MPI_Group",
  ("MPI_Group_union", "group_out"):"MPI_Group",
  ("MPI_Iallgather", "request"):"MPI_Request",
  ("MPI_Iallgatherv", "request"):"MPI_Request",
  ("MPI_Iallreduce", "request"):"MPI_Request",
  ("MPI_Ialltoall", "request"):"MPI_Request",
  ("MPI_Ialltoallv", "request"):"MPI_Request",
  ("MPI_Ialltoallw", "request"):"MPI_Request",
  ("MPI_Ibarrier", "request"):"MPI_Request",
  ("MPI_Ibcast", "request"):"MPI_Request",
  ("MPI_Iexscan", "request"):"MPI_Request",
  ("MPI_Igather", "request"):"MPI_Request",
  ("MPI_Igatherv", "request"):"MPI_Request",
  ("MPI_Ireduce", "request"):"MPI_Request",
  ("MPI_Ireduce_scatter_block", "request"):"MPI_Request",
  ("MPI_Ireduce_scatter", "request"):"MPI_Request",
  ("MPI_Iscan", "request"):"MPI_Request",
  ("MPI_Iscatter", "request"):"MPI_Request",
  ("MPI_Iscatterv", "request"):"MPI_Request",
  ("MPI_Ibsend", "request"):"MPI_Request",
  ("MPI_Intercomm_create", "comm_out"):"MPI_Comm",
  ("MPI_Intercomm_merge", "comm_out"):"MPI_Comm",
  ("MPI_Iprobe", "status"):"MPI_Status",
  ("MPI_Irecv", "request"):"MPI_Request",
  ("MPI_Irsend", "request"):"MPI_Request",
  ("MPI_Isend", "request"):"MPI_Request",
  ("MPI_Issend", "request"):"MPI_Request",
  ("MPI_Op_create", "op"):"MPI_Op",
  ("MPI_Probe", "status"):"MPI_Status",
  ("MPI_Recv", "status"):"MPI_Status",
  ("MPI_Recv_init", "request"):"MPI_Request",
  ("MPI_Request_free", "request"):"MPI_Request",
  ("MPI_Rsend_init", "request"):"MPI_Request",
  ("MPI_Send_init", "request"):"MPI_Request",
  ("MPI_Sendrecv", "status"):"MPI_Status",
  ("MPI_Sendrecv_replace", "status"):"MPI_Status",
  ("MPI_Ssend_init", "request"):"MPI_Request",
  ("MPI_Start", "request"):"MPI_Request",
  ("MPI_Startall", "array_of_requests"):"MPI_Request",
  ("MPI_Test", "request"):"MPI_Request",
  ("MPI_Test", "status"):"MPI_Status",
  ("MPI_Testall", "array_of_requests"):"MPI_Request",
  ("MPI_Testall", "array_of_statuses"):"MPI_Status",
  ("MPI_Testany", "array_of_requests"):"MPI_Request",
  ("MPI_Testany", "status"):"MPI_Status",
  ("MPI_Testsome", "array_of_requests"):"MPI_Request",
  ("MPI_Testsome", "array_of_statuses"):"MPI_Status",
  ("MPI_Type_commit", "datatype"):"MPI_Datatype",
  ("MPI_Type_contiguous", "newtype"):"MPI_Datatype",
  ("MPI_Type_create_hindexed", "newtype"):"MPI_Datatype",
  ("MPI_Type_create_hvector", "newtype"):"MPI_Datatype",
  ("MPI_Type_free", "datatype"):"MPI_Datatype",
  ("MPI_Type_get_contents", "array_of_datatypes"):"MPI_Datatype",
  ("MPI_Type_indexed", "newtype"):"MPI_Datatype",
  ("MPI_Type_create_struct", "newtype"):"MPI_Datatype",
  ("MPI_Type_vector", "newtype"):"MPI_Datatype",
  ("MPI_Wait", "request"):"MPI_Request",
  ("MPI_Wait", "status"):"MPI_Status",
  ("MPI_Waitall", "array_of_requests"):"MPI_Request",
  ("MPI_Waitall", "array_of_statuses"):"MPI_Status",
  ("MPI_Waitany", "array_of_requests"):"MPI_Request",
  ("MPI_Waitany", "status"):"MPI_Status",
  ("MPI_Waitsome", "array_of_requests"):"MPI_Request",
  ("MPI_Waitsome", "array_of_statuses"):"MPI_Status"
}

incrementFortranIndexDict = {
  ("MPI_Testany"): ("*index", 1),
  ("MPI_Testsome"): ("array_of_indices", "*count"),
  ("MPI_Waitany"): ("*index", 1),
  ("MPI_Waitsome"): ("array_of_indices", "*count")
  }

xlateFortranArrayExceptions = {
  ("MPI_Testany", "array_of_requests"): ("index"),
  ("MPI_Waitany", "array_of_requests"): ("index")
}

collectiveList = [
  "MPI_Allgather",
  "MPI_Allgatherv",
  "MPI_Allreduce",
  "MPI_Alltoall",
  "MPI_Alltoallv",
  "MPI_Barrier",
  "MPI_Bcast",
  "MPI_Gather",
  "MPI_Gatherv",
  "MPI_Iallgather",
  "MPI_Iallgatherv",
  "MPI_Iallreduce",
  "MPI_Ialltoall",
  "MPI_Ialltoallv",
  "MPI_Ialltoallw",
  "MPI_Ibcast",
  "MPI_Ibarrier",
  "MPI_Iexscan",
  "MPI_Igather",
  "MPI_Igatherv",
  "MPI_Ireduce",
  "MPI_Ireduce_scatter_block",
  "MPI_Ireduce_scatter",
  "MPI_Iscan",
  "MPI_Iscatter",
  "MPI_Iscatterv",
  "MPI_Reduce",
  "MPI_Reduce_scatter",
  "MPI_Scatter",
  "MPI_Scatterv"
  ]

in_place_bottomList = [
  "MPI_Allgather",
  "MPI_Allgatherv",
  "MPI_Allreduce",
  "MPI_Alltoall",
  "MPI_Alltoallv",
  "MPI_Gather",
  "MPI_Gatherv",
  "MPI_Iallgather",
  "MPI_Iallgatherv",
  "MPI_Iallreduce",
  "MPI_Ialltoall",
  "MPI_Ialltoallv",
  "MPI_Ialltoallw",
  "MPI_Igather",
  "MPI_Igatherv",
  "MPI_Ireduce",
  "MPI_Ireduce_scatter_block",
  "MPI_Ireduce_scatter",
  "MPI_Iscan",
  "MPI_Iscatter",
  "MPI_Iscatterv",
  "MPI_Reduce",
  "MPI_Reduce_scatter",
  "MPI_Scatter",
  "MPI_Scatterv"
  ]

status_ignoreList = [
    "MPI_File_read",
    "MPI_File_read_all",
    "MPI_File_read_at",
    "MPI_File_read_at_all",
    "MPI_File_write",
    "MPI_File_write_all",
    "MPI_File_write_at",
    "MPI_File_write_at_all",
    "MPI_Iprobe",
    "MPI_Probe",
    "MPI_Recv",
    "MPI_Sendrecv",
    "MPI_Sendrecv_replace",
    "MPI_Test",
    "MPI_Testany",
    "MPI_Wait",
    "MPI_Waitany"
]

statuses_ignoreList = [
    "MPI_Testall",
    "MPI_Testsome",
    "MPI_Waitall",
    "MPI_Waitsome"
]

pt2ptList = [
    "MPI_Bsend",
    "MPI_Ibsend",
    "MPI_Irsend",
    "MPI_Isend",
    "MPI_Issend",
    "MPI_Rsend",
    "MPI_Send",
    "MPI_Sendrecv",
    "MPI_Sendrecv_replace",
    "MPI_Ssend"
  ]


class VarDesc:
    def __init__ (self,name, basetype, pointerLevel, arrayLevel):
        "initialize a new variable description structure"
        self.name = name
        self.basetype = basetype
        self.pointerLevel = pointerLevel
        self.arrayLevel = arrayLevel
        self.recordIt = 0

class fdecl:
    def __init__ (self,name, id, returntype, paramList, protoline):
        "initialize a new function declaration structure"
        self.name = name
        self.id = id
        self.returntype = returntype
        self.paramList = paramList
        self.paramDict = {}
        self.protoline = protoline
        self.wrapperPreList = []
        self.wrapperPostList = []
        self.nowrapper = 0
        self.paramConciseList = []
        self.extrafields = {}
        self.extrafieldsList = []
        self.sendCountPname = ""
        self.sendTypePname = ""
        self.vectorCountPname = ""
        self.vectorTypePname = ""
        self.recvCountPname = ""
        self.recvTypePname = ""
        self.ioCountPname = ""
        self.ioTypePname = ""
        self.rmaCountPname = ""
        self.rmaTypePname = ""

class xlateEntry:
    def __init__ (self,mpiType,varName):
        "initialize a new Fortran translation structure"
        self.mpiType = mpiType
        self.varName = varName


def ProcessDirectiveLine(lastFunction, line):
    tokens = line.split()
    if tokens[0] == "nowrapper":
        fdict[lastFunction].nowrapper = 1
    elif tokens[0] == "extrafield":
        fdict[lastFunction].extrafieldsList.append(tokens[2])
        fdict[lastFunction].extrafields[tokens[2]] = tokens[1]
    else:
        print("Warning: ",lastFunction," unknown directive [",line.strip(),"]")


def ProcessWrapperPreLine(lastFunction, line):
    #print "Processing wrapper pre [",line.strip(),"] for ",lastFunction
    fdict[lastFunction].wrapperPreList.append(line)


def ProcessWrapperPostLine(lastFunction, line):
    #print "Processing wrapper post [",line.strip(),"] for ",lastFunction
    fdict[lastFunction].wrapperPostList.append(line)


def DumpDict():
    for i in flist:
        print(i)
        if verbose:
            print("\tParams\t",fdict[i].paramList)
            if fdict[i].wrapperPreList:
                print("\tpre\t", fdict[i].wrapperPreList)
            if fdict[i].wrapperPostList:
                print("\tpost\t", fdict[i].wrapperPostList)


#####
##### Some MPI types we want to record. If there are pointers to them, deref them.
##### To simplify, assume that the value can be an 'int' for printing and assignment.
#####
def SpecialParamRecord(funct,param):
    global flist
    global fdict
    basetype = fdict[funct].paramDict[param].basetype
    pointerLevel = fdict[funct].paramDict[param].pointerLevel
    arrayLevel = fdict[funct].paramDict[param].arrayLevel

    simplePointer = (pointerLevel == 1) and (arrayLevel == 0)

    if basetype == "MPI_Request" and simplePointer:
        return 1
    elif basetype == "MPI_Comm" and simplePointer:
        return 1
    elif basetype == "MPI_Datatype" and simplePointer:
        return 1
    elif basetype == "MPI_Group" and simplePointer:
        return 1
    elif basetype == "MPI_Info" and simplePointer:
        return 1
    elif basetype == "int" and simplePointer:
        return 1
    else:
        return 0



#####
##### ParamDictUpdate - updates the datastructures for a function after
#####    the basics have been entered. Must be called for each function.
#####
def ParamDictUpdate(fname):
    global flist
    global fdict
    global messParamDict
    global ioParamDict
    global rmaParamDict
    for p in fdict[fname].paramList:
        ## check for pointers, arrays
        pname = "NULL"
        basetype = "NULL"
        pointerLevel = p.count("*")
        arrayLevel = p.count("[")
        if (pointerLevel > 0) and (arrayLevel > 0):
            ## handle pointers and arrays
            pname = p[p.rfind("*")+1:p.find("[")]
            basetype = p[0:p.find("*")]
        elif pointerLevel > 0:
            ## handle pointers
            pname = p[p.rfind("*")+1:len(p)]
            basetype = p[0:p.find("*")]
        elif arrayLevel > 0:
            ## handle arrays
            pname = p[p.find(" "):p.find("[")]
            basetype = p[0:p.find(" ")]
        else:
            ## normal hopefully :)
            tokens = p.split()
            if len(tokens) == 1:
                ## must be void
                pname = ""
                basetype = "void"
            else:
                pname = tokens[1].strip()
                basetype = tokens[0].strip()

        pname = pname.strip()
        basetype = basetype.strip()
        fdict[fname].paramDict[pname] = VarDesc(pname,basetype,pointerLevel,arrayLevel)
        fdict[fname].paramConciseList.append(pname)

        #  Identify and assign message size parameters
        if (fname,pname) in messParamDict:
            paramMessType = messParamDict[(fname,pname)]
            if paramMessType == 1:
                fdict[fname].sendCountPname = pname
            elif paramMessType == 2:
                fdict[fname].sendTypePname = pname
            elif paramMessType == 3:
                fdict[fname].recvCountPname = pname
            elif paramMessType == 4:
                fdict[fname].recvTypePname = pname

        #  Identify and assign vector message size parameters
        if (fname,pname) in vectorsendParamDict:
            paramMessType = vectorsendParamDict[(fname,pname)]
            if paramMessType == 1:
                fdict[fname].vectorCountPname = pname

        #  Identify and assign vector message datatype parameters
        if (fname,pname) in vectortypeParamDict:
            paramMessType = vectortypeParamDict[(fname,pname)]
            if paramMessType == 2:
                fdict[fname].vectorTypePname = pname

        #  Identify and assign io size parameters
        if (fname,pname) in ioParamDict:
            paramMessType = ioParamDict[(fname,pname)]
            if paramMessType == 1:
                fdict[fname].ioCountPname = pname
            elif paramMessType == 2:
                fdict[fname].ioTypePname = pname

        #  Identify and assign rma size parameters
        if (fname,pname) in rmaParamDict:
            paramMessType = rmaParamDict[(fname,pname)]
            if paramMessType == 1:
                fdict[fname].rmaCountPname = pname
            elif paramMessType == 2:
                fdict[fname].rmaTypePname = pname

        if (fdict[fname].paramDict[pname].pointerLevel == 0) \
           and (fdict[fname].paramDict[pname].arrayLevel == 0) \
           and (fdict[fname].paramDict[pname].basetype != "void"):
            fdict[fname].paramDict[pname].recordIt = 1
        elif SpecialParamRecord(fname,pname):
            fdict[fname].paramDict[pname].recordIt = 1
        else:
            pass

        if verbose:
            #print "\t->",p
            print("\t",pname, basetype, pointerLevel, arrayLevel)


#####
##### Parses the input file and loads the information into the function dict.
#####
def ReadInputFile(f):
    # parser states
    p_start = "start"
    p_directives = "directives"
    p_wrapper_pre = "wrapper_pre"
    p_wrapper_post = "wrapper_post"
    parserState = p_start
    global cnt
    global fdict
    global flist

    fcounter = baseID

    print("-----*----- Parsing input file")
    while 1:
        ##### read a line from input
        rawline = f.readline()
        if not rawline:
            break
        cnt = cnt + 1
        line = re.sub(r"@.*$", "", rawline)

        ##### break it into tokens
        tokens = line.split()
        if not tokens:
            continue

        ##### determine what type of line this is and then parse it as required
        if (line.find("(") != -1) \
           and (line.find(")") != -1) \
           and (line.find("MPI_") != -1) \
           and parserState == p_start:
            ##### we have a prototype start line
            name = tokens[1]
            retype = tokens[0]
            lparen = line.index("(")
            rparen = line.index(")")
            paramstr = line[lparen+1:rparen]
            paramList = list(map(str.strip,paramstr.split(",")))
            #    print cnt, "-->", name,  paramList
            fdict[name] = fdecl(name, fcounter, retype, paramList,line)
            ParamDictUpdate(name)
            lastFunction = name
            if verbose:
                print(name)
        else:
            ##### DIRECTIVES
            if tokens[0] == "directives" and parserState != p_directives:
                ##### beginning of directives
                parserState = p_directives
            elif tokens[0] == "directives" and parserState == p_directives:
                ##### end of directives
                parserState = p_start
            elif parserState == p_directives:
                ##### must be a directive, process it
                ProcessDirectiveLine(lastFunction, line)

            ##### CODE WRAPPER PRE
            elif tokens[0] == "wrapper_pre" and parserState != p_wrapper_pre:
                ##### beginning of wrapper_pre
                parserState = p_wrapper_pre
            elif tokens[0] == "wrapper_pre" and parserState == p_wrapper_pre:
                ##### end of wrapper_pre
                parserState = p_start
            elif parserState == p_wrapper_pre:
                ##### must be a directive, process it
                ProcessWrapperPreLine(lastFunction, line)

            ##### CODE WRAPPER POST
            elif tokens[0] == "wrapper_post" and parserState != p_wrapper_post:
                ##### beginning of wrapper_post
                parserState = p_wrapper_post
            elif tokens[0] == "wrapper_post" and parserState == p_wrapper_post:
                ##### end of wrapper_post
                parserState = p_start
            elif parserState == p_wrapper_post:
                ##### must be a directive, process it
                ProcessWrapperPostLine(lastFunction, line)

            ##### UNKNOWN
            else:
                print("Unknown input line ",cnt, ":", line, end=' ')

    flist = list(fdict.keys())
    flist.sort()
    fcounter = baseID
    for f in flist :
      fdict[f].id = fcounter
      if f not in noDefineList:
        fcounter = fcounter + 1
    print("-----*----- Parsing completed: ", len(fdict), " functions found.")


###
### create a standard file header and return the init list
###
def StandardFileHeader(fname):
    olist = []
    olist.append("/* " + fname + " */\n")
    olist.append("/* DO NOT EDIT -- AUTOMATICALLY GENERATED! */\n")
    if not os.getenv("SOURCE_DATE_EPOCH"):
        olist.append("/* Timestamp: " + time.strftime("%d %B %Y %H:%M", time.localtime(time.time())) + "  */\n")
        olist.append("/* Location: " + socket.gethostname () + " " + os.name + " */\n")
        olist.append("/* Creator: " + os.environ["LOGNAME"] + "  */\n")
    olist.append("\n")
    olist.append("\n")
    return olist


###
### Scan the lists of all functions and look for optimization
### opportunities (in space/speed).
###
### NOT USED
###
def ParameterOptimization():
    global flist
    global fdict
    ##### visit each function and update each functions parameter dictionary
    for funct in flist:
        if verbose:
            print(funct)
        ParamDictUpdate(funct)


###
### Create the structure files.
###
def GenerateStructureFile():
    global flist
    global fdict
    print("-----*----- Generating structure files")
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + "/mpiPi_def.h"
    g = open(sname, "w")
    olist = StandardFileHeader(sname)

    olist.append("\n")
    olist.append("#define mpiPi_BASE " + str(baseID) + "\n")
    olist.append("\n")

    defCount = 0
    for funct in flist:
      if funct not in noDefineList:
        olist.append("#define mpiPi_" + funct + " " + str(fdict[funct].id) + "\n")
        defCount = defCount + 1

    olist.append("#define mpiPi_DEF_END " + str(baseID + defCount) + "\n")
    olist.append("\n\n/* eof */\n")
    g.writelines(olist)
    g.close()


###
### Generate a lookup table where mpiP can grab variables and function pointers.
###
def GenerateLookup():
    global flist
    global fdict

    print("-----*----- Generating the lookup table")
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + "/lookup.c"
    g = open(sname, "w")
    olist = StandardFileHeader(sname)

    olist.append("#include \"mpiPi.h\"\n")
    olist.append("#include \"mpiPi_def.h\"\n")
    olist.append("\n")
    olist.append("\n")

    olist.append("mpiPi_lookup_t mpiPi_lookup [] = {\n")

    counter = 0
    for funct in flist:
        if funct not in noDefineList:
          if counter < len(flist) \
            and counter > 0 :
            olist.append(",\n")
          olist.append("\t{ mpiPi_" + funct)
          olist.append(", \"" + funct + "\"")
          olist.append("}")
          counter = counter + 1

    olist.append(",\n\t{0,NULL}};\n")

    olist.append("\n")
    olist.append("/* eof */\n")
    g.writelines(olist)
    g.close()


###
### Create a MPI wrapper for one function using the information in the function dict.
### First, generate a generic wrapper, and then the FORTRAN, C wrappers.
###
def CreateWrapper(funct, olist):
    global fdict
    global arch

    if fdict[funct].nowrapper:
        return

    if verbose:
        print("Wrapping ",funct)

    olist.append("\n\n\n/* --------------- " + funct + " --------------- */\n" )

    #####
    ##### Generic wrapper
    #####

    ##### funct decl
    if ( 'mips' in arch ) :
        olist.append("\nstatic int mpiPif_" + funct + "( void **base_jbuf, " )
    else :
        olist.append("\nstatic int mpiPif_" + funct + "( jmp_buf * base_jbuf, " )
    # add parameters
    for i in fdict[funct].paramConciseList:

        olist.append(fdict[funct].paramDict[i].basetype + ' ')

        if (fdict[funct].paramDict[i].pointerLevel == 0) \
           and (fdict[funct].paramDict[i].arrayLevel == 0) \
           and (fdict[funct].paramDict[i].basetype != "void"):
            olist.append(" * ")

        if (fdict[funct].paramDict[i].pointerLevel > 0):
            for j in range(1,fdict[funct].paramDict[i].pointerLevel+1):
                olist.append(" *")

        olist.append(i)

        if (fdict[funct].paramDict[i].arrayLevel > 0):
            for x in range(0, fdict[funct].paramDict[i].arrayLevel) :
              olist.append('[')
            for x in range(0, fdict[funct].paramDict[i].arrayLevel) :
              olist.append(']')
        else:
            pass
        if fdict[funct].paramConciseList.index(i) < len(fdict[funct].paramConciseList) - 1:
            olist.append(", ")
    olist.append(")")
    # start wrapper code
    olist.append("\n{\n")
    olist.append( " int rc, enabledState;\n double dur;\n int tsize;\n double messSize = 0.;\n double ioSize = 0.;\n double rmaSize =0.;\n mpiPi_TIME start, end;\n void *call_stack[MPIP_CALLSITE_STACK_DEPTH_MAX] = { NULL };\n" )
    olist.append( "  mpiPi_mt_stat_tls_t *hndl;\n" )

    olist.append("\n  hndl = mpiPi_stats_mt_gettls(&mpiPi.task_stats);\n")

    olist.append("\nif (mpiPi_stats_mt_is_on(hndl)) {\n")
    if fdict[funct].wrapperPreList:
        olist.extend(fdict[funct].wrapperPreList)

    # capture timer
    olist.append("mpiPi_GETTIME (&start);\n" )

    # capture call stack
    olist.append("if ( mpiPi.reportStackDepth > 0 ) mpiPi_RecordTraceBack((*base_jbuf), call_stack, mpiPi.fullStackDepth);\n"  )

    # end of enabled check
    olist.append("}\n\n")

    # Mark that we have already entered Profiler to avoid nested invocations
    olist.append("mpiPi_stats_mt_enter(hndl);\n")

    # call PMPI
    olist.append("\nrc = P" + funct + "( " )

    for i in fdict[funct].paramConciseList:
        if (fdict[funct].paramDict[i].pointerLevel == 0) \
           and (fdict[funct].paramDict[i].arrayLevel == 0) \
           and (fdict[funct].paramDict[i].basetype != "void"):
            olist.append(" * " + i)
        elif (fdict[funct].paramDict[i].pointerLevel > 0):
            olist.append(i)
        elif (fdict[funct].paramDict[i].arrayLevel > 0):
            olist.append(i)
        else:
            print("Warning: passing on arg",i,"in",funct)
        if fdict[funct].paramConciseList.index(i) < len(fdict[funct].paramConciseList) - 1:
            olist.append(", ")
    olist.append(");\n\n")

    # Mark that we exited Profiler
    olist.append("mpiPi_stats_mt_exit(hndl);\n")
    olist.append("if (mpiPi_stats_mt_is_on(hndl)) {\n")
    olist.append("\n"
                 + "mpiPi_GETTIME (&end);\n"
                 + "dur = mpiPi_GETTIMEDIFF (&end, &start);\n")

    #  Calculate message size based on count and datatype arguments
    if fdict[funct].sendCountPname != "":
        olist.append( "\n"
                      + "if ( *" + fdict[funct].sendTypePname + " != MPI_DATATYPE_NULL ) { "
                      + "PMPI_Type_size(*" + fdict[funct].sendTypePname + ", "
                      + "&tsize);\n"
                      + "messSize = (double)(tsize * *"
                      +  fdict[funct].sendCountPname + ");}\n"
                      + "else { mpiPi_msg_warn(\"MPI_DATATYPE_NULL encountered.  MPI_IN_PLACE not supported.\\n\");\n"
                      + "mpiPi_msg_warn(\"Values for %s may be invalid for rank %d.\\n\", &(__func__)[7], mpiPi.rank);}\n")

    #  Calculate message size based on array count and datatype arguments
    if fdict[funct].vectorCountPname != "":
      #  Has array of datatypes, as in Ialltoallw
      if fdict[funct].vectorTypePname != "":
        olist.append( "\n"
                      + "  int loc_comm_size, i;\n"
                      + "  int loc_sent = 0;\n\n"
                      + "  PMPI_Comm_size(*comm, &loc_comm_size);\n\n"
                      + "  for ( i = 0; i<loc_comm_size; i++) { \n"
                      + "    if ( " + fdict[funct].vectorTypePname + "[i] != MPI_DATATYPE_NULL ) { \n"
                      + "      PMPI_Type_size(" + fdict[funct].vectorTypePname + "[i], &tsize);\n"
                      + "      loc_sent = " + fdict[funct].vectorCountPname + "[i];\n"
                      + "      messSize += (double)(tsize * loc_sent);\n"
                      + "    }\n"
                      + "    else { mpiPi_msg_warn(\"MPI_DATATYPE_NULL encountered.  MPI_IN_PLACE not supported.\\n\");\n"
                      + "     mpiPi_msg_warn(\"Values for %s may be invalid for rank %d.\\n\", &(__func__)[7], mpiPi.rank);}\n"
                      +  "}\n"
                      )

      #  Scalar datatype handling
      elif ( fdict[funct].sendTypePname != "" ) :
        olist.append( "\n"
                      + "if ( *" + fdict[funct].sendTypePname + " != MPI_DATATYPE_NULL ) { \n"
                      + "  int loc_comm_size, i;\n"
                      + "  int loc_sent = 0;\n\n"
                      + "  PMPI_Comm_size(*comm, &loc_comm_size);\n"
                      + "  PMPI_Type_size(*" + fdict[funct].sendTypePname + ", &tsize);\n"
                      + "  for ( i = 0; i<loc_comm_size; i++) \n"
                      + "    loc_sent += " + fdict[funct].vectorCountPname + "[i];\n"
                      + "  messSize = (double)(tsize * loc_sent);\n"
                      +  "}\n"
                      + "else { mpiPi_msg_warn(\"MPI_DATATYPE_NULL encountered.  MPI_IN_PLACE not supported.\\n\");\n"
                      + "mpiPi_msg_warn(\"Values for %s may be invalid for rank %d.\\n\", &(__func__)[7], mpiPi.rank);}\n")

    if fdict[funct].ioCountPname != "":
        olist.append( "\n"
                      + "PMPI_Type_size(*" + fdict[funct].ioTypePname + ", "
                      + "&tsize);\n"
                      + "ioSize = (double)(tsize * *"
                      +  fdict[funct].ioCountPname + ");\n")

    if fdict[funct].rmaCountPname != "":
        olist.append( "\n"
                      + "PMPI_Type_size(*" + fdict[funct].rmaTypePname + ", "
                      + "&tsize);\n"
                      + "rmaSize = (double)(tsize * *"
                      +  fdict[funct].rmaCountPname + ");\n")

    olist.append("\n" \
                 + "if ( dur < 0 )\n"
                 + "  mpiPi_msg_warn(\"Rank %5d : Negative time difference : %11.9f in %s\\n\", mpiPi.rank, dur, \"" + funct + "\");\n"
                 + "else\n")
    olist.append( "  mpiPi_update_callsite_stats(hndl, " + "mpiPi_" + funct + ", " \
                  + "mpiPi.rank, "
                  + "call_stack, "
                  + "dur, "
                  + "(double)messSize,"
                  + "(double)ioSize,"
                  + "(double)rmaSize"
                  + ");\n" )

    if funct in collectiveList :
      for i in fdict[funct].paramConciseList:
         if (fdict[funct].paramDict[i].basetype == "MPI_Comm"):
           olist.append("\nif (mpiPi.do_collective_stats_report) { mpiPi_update_collective_stats(hndl, " + "mpiPi_" + funct + "," \
              + " dur, " + "(double)messSize," +  " " + i + "); }\n")

    if funct in pt2ptList :
      for i in fdict[funct].paramConciseList:
         if (fdict[funct].paramDict[i].basetype == "MPI_Comm"):
           olist.append("\nif (mpiPi.do_pt2pt_stats_report) { mpiPi_update_pt2pt_stats(hndl, " + "mpiPi_" + funct + "," \
              + " dur, " + "(double)messSize," +  " " + i + "); }\n")

    # end of enabled check
    olist.append("}\n\n")

    olist.append("return rc;\n")

    olist.append("}" + " /* " + funct + " */\n\n")


    if ( 'mips' in arch ) :
            decl =    "\nint rc;\n"
    else :
        decl =    "\nint rc;\njmp_buf jbuf;\n"


    #####
    ##### C wrapper
    #####
    olist.append("\n\nextern " + fdict[funct].protoline + "{" )
    if fdict[funct].wrapperPreList:
        olist.extend(fdict[funct].wrapperPreList)
    olist.append(decl)
    if ( 'mips' in arch ) :
      olist.append("void *saved_ret_addr = __builtin_return_address(0);\n")
      olist.append("\nrc = mpiPif_" + funct + "( &saved_ret_addr, " )
    else :
      if ( useSetJmp == True ) :
        olist.append("setjmp (jbuf);\n\n")
      olist.append("\nrc = mpiPif_" + funct + "( &jbuf, " )

    for i in fdict[funct].paramConciseList:
        if (fdict[funct].paramDict[i].pointerLevel == 0) \
           and (fdict[funct].paramDict[i].arrayLevel == 0) \
           and (fdict[funct].paramDict[i].basetype != "void"):
            olist.append(" & " + i)
        elif (fdict[funct].paramDict[i].pointerLevel > 0):
            olist.append(i)
        elif (fdict[funct].paramDict[i].arrayLevel > 0):
            olist.append(i)
        else:
            pass
        if fdict[funct].paramConciseList.index(i) < len(fdict[funct].paramConciseList) - 1:
            olist.append(", ")

    olist.append(" );\n\n" + "return rc;\n" )
    olist.append("}" + " /* " + funct + " */\n")


    #####
    ##### Fortran wrapper
    #####

    ##### funct decl
    olist.append("\n\nextern void " + "F77_" + funct.upper() + "(" )

    #================================================================================
    # In the case where MPI_Fint and and opaque objects such as MPI_Request are not the same size,
    #   we want to use MPI conversion functions.
    #
    # The most obvious problem we have encountered is for MPI_Request objects,
    #   but Communicators, Group, Datatype, Op, and File are also possibily problems.
    #
    # There are two cases:
    #   1) A single argument needs to be translated.
    #   2) An array of objects needs to be allocated and translated.
    #      This only appears necessary for Request and Datatype
    #
    # The algorithm for processing Fortran wrapper functions is as follows:
    #   1.  Declare all C variable versions for Fortran arguments.
    #   2.  Allocate any arrays to be used.
    #   3.  Perform any necessary pre-call array and scalar xlation.
    #   4.  Make the function call with appropriate C variables.
    #   5.  Perform any necessary post-call array and scalar xlation.
    #   6.  Free any arrays.
    #================================================================================

    ###  Type translation information
    xlateVarName = ""
    xlateVarNames = []
    xlateTypes = []
    xlateCount = 0
    #  Input types to translate
    xlateTargetTypes = [ "MPI_Comm", "MPI_Datatype", "MPI_File", "MPI_Group", "MPI_Info", "MPI_Op", "MPI_Request", "MPI_Status" ]
    stringType = "mpip_const_char_t"
    stringVarNames = []
    freelist = []

    #  Iterate through the arguments for this function
    opaqueFound = 0
    for i in fdict[funct].paramConciseList:

        if ( doOpaqueXlate is True and fdict[funct].paramDict[i].basetype in xlateTargetTypes ) :

            #  Verify that there is a Dictionary entry for translating this argument
            if ( not ( (funct, i) in opaqueInArgDict or (funct, i) in opaqueOutArgDict ) ):
                print("*** Failed to find translation information for " + funct + ":" + i + "\n")

            opaqueFound = 1
            # All Fortran opaque object are of type MPI_Fint
            currBasetype = "MPI_Fint"

            #  Store variable name and type
            xlateTypes.append(fdict[funct].paramDict[i].basetype)
            xlateVarNames.append(i)

            #  Try to identify whether array or single value by whether "array" is in the variable name
            #  and add C declaration to declaration list.
            if ( xlateVarNames[xlateCount].count("array") > 0 ):
                if ( xlateVarNames[xlateCount].count("statuses") > 0 ):
                    decl += xlateTypes[xlateCount] + " *c_" + xlateVarNames[xlateCount] + " = NULL;\n";
                else:
                    decl += xlateTypes[xlateCount] + " *c_" + xlateVarNames[xlateCount] + ";\n";
            #  Do the same for status/statuses
            elif ( xlateVarNames[xlateCount].count("status") > 0 ):
                decl += xlateTypes[xlateCount] + " *c_" + xlateVarNames[xlateCount] + " = NULL;\n";
            else:
                decl += xlateTypes[xlateCount] + " c_" + xlateVarNames[xlateCount] + ";\n";

            xlateCount += 1
        elif ( doOpaqueXlate is True and fdict[funct].paramDict[i].basetype == stringType and
                1 == fdict[funct].paramDict[i].pointerLevel ) :
            stringVarNames.append(i);
            decl += "  char *c_" + i + " = NULL;\n";
            currBasetype = fdict[funct].paramDict[i].basetype
        else:
            #  Not translating this variable
            currBasetype = fdict[funct].paramDict[i].basetype

        #  Add argument to function declaration
        olist.append(currBasetype + ' ')

        if (fdict[funct].paramDict[i].pointerLevel == 0) \
           and (fdict[funct].paramDict[i].arrayLevel == 0) \
           and (fdict[funct].paramDict[i].basetype != "void"):
            olist.append(" * ")

        if (fdict[funct].paramDict[i].pointerLevel > 0):
            for j in range(1,fdict[funct].paramDict[i].pointerLevel+1):
                olist.append(" *")

        olist.append(i)

        if (fdict[funct].paramDict[i].arrayLevel > 0):
            for x in range(0, fdict[funct].paramDict[i].arrayLevel) :
              olist.append('[')
            for x in range(0, fdict[funct].paramDict[i].arrayLevel) :
              olist.append(']')
        else:
            pass
        if fdict[funct].paramConciseList.index(i) < len(fdict[funct].paramConciseList) - 1:
             olist.append(", ")

    #  Add ierr argument and declarations to output list
    olist.append(" , MPI_Fint *ierr")

    # Append all string lengths parameter
    for i in stringVarNames :
        olist.append(" , int " + i + "_len")
    olist.append(")")


    olist.append(" {")
    olist.append(decl)
    olist.append("\n")

    if fdict[funct].wrapperPreList:
            olist.extend(fdict[funct].wrapperPreList)

    if ( 'mips' in arch ) :
      olist.append("void *saved_ret_addr = __builtin_return_address(0);\n")
    else :
      if ( useSetJmp == True ) :
        olist.append("setjmp (jbuf);\n\n")

    #  Allocate any arrays used for translation
    for i in range(len(xlateVarNames)) :
        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        #  A pretty sketchy way of identifying an array size, but as far as I can tell,
        #  only one array is passed as an argument per function.
        if ( fdict[funct].paramConciseList.count("count") > 1 ):
            print("*** Multiple arrays in 1 function!!!!\n");

        if ( "incount" in fdict[funct].paramConciseList ):
            countVar = "incount";
        elif ( "count" in fdict[funct].paramConciseList ):
            countVar = "count";
        else:
            countVar = "max_integers"

        if ( xlateVarName.count("array") > 0 and xlateVarName.count("statuses") == 0) :
            olist.append("c_" + xlateVarName + " = (" + xlateType + "*)malloc(sizeof(" + xlateType + ")*(*" + countVar + "));\n")
            olist.append("if ( c_" + xlateVarName + " == NULL ) mpiPi_abort(\"Failed to allocate memory in " \
                + funct + "\");\n")
            freelist.append("c_"+xlateVarName)


    for i in stringVarNames :
        olist.append("  for(; " + i + "_len > 0; " + i + "_len--){\n")
        olist.append("    if( " + i + "[" + i + "_len] != ' '){\n")
        olist.append("      " + i +"_len++; // The length is last symbol index + 1\n")
        olist.append("      break;\n")
        olist.append("    }\n")
        olist.append("  }\n");
        olist.append("  c_" + i + " = calloc( " + i + "_len + 1, sizeof(char));\n")
        olist.append("  memcpy( c_" + i + ", " + i + ", " + i + "_len);\n")

    #  Generate pre-call translation code if necessary by iterating through arguments that
    #  were identified as opaque objects needing translation above
    for i in range(len(xlateVarNames)) :

        #  Set current argument name and type
        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        #  Check for valid function:argument-name entry for pre-call translation.
        if ( (funct, xlateVarName) in opaqueInArgDict \
            and opaqueInArgDict[(funct, xlateVarName)] == xlateType ) :

            #  Datatype translation is the only call where the translation function
            #  doesn't match the argument type.
            if ( xlateType == "MPI_Datatype" ):
                xlateFuncType = "MPI_Type"
            else:
                xlateFuncType = xlateType

            if ( xlateVarName.count("array") > 0 ):
                olist.append("{\n  int i; \n")
                olist.append("  for (i = 0; i < *" + countVar + "; i++) { \n")
                olist.append("    c_" + xlateVarName + "[i] = " + xlateFuncType + "_f2c(" + xlateVarName + "[i]);\n")
                olist.append("  }\n}\n")
            else:
                if ( xlateVarName.count("status") == 0 ):
                    olist.append("c_" + xlateVarName + " = " + xlateFuncType + "_f2c(*" + xlateVarName + ");\n")

            xlateDone = 1

    #  Add logic for IN_PlACE/MPI_BOTTOM
    if funct in in_place_bottomList:
        olist.append("\nif ((size_t)sendbuf == mpiPi_fortran.in_place)\n")
        olist.append("  sendbuf = MPI_IN_PLACE;\n\n")
        olist.append("if ((size_t)sendbuf == mpiPi_fortran.bottom)\n")
        olist.append("  sendbuf = MPI_BOTTOM;\n\n")
        olist.append("if ((size_t)recvbuf == mpiPi_fortran.bottom)\n")
        olist.append("  recvbuf = MPI_BOTTOM;\n")

    # Add logic for MPI_STATUS_IGNORE
    if funct in status_ignoreList:
        olist.append("\nif ((size_t)status == mpiPi_fortran.status_ignore)\n")
        olist.append("  c_status = MPI_STATUS_IGNORE;\n")
        olist.append("else {\n")
        olist.append("  c_status = (MPI_Status *) malloc(sizeof(MPI_Status));\n")
        olist.append("  if (c_status == NULL)\n")
        olist.append("    mpiPi_abort(\"Failed to allocate memory in " + funct + "\");\n")
        olist.append("}\n")


    # Add logic for MPI_STATUSES_IGNORE
    if funct in statuses_ignoreList:
        olist.append("\nif ((size_t)array_of_statuses == mpiPi_fortran.statuses_ignore)\n")
        olist.append("  c_array_of_statuses = MPI_STATUSES_IGNORE;\n")
        olist.append("else {\n")
        olist.append("  c_array_of_statuses = (MPI_Status *) malloc(sizeof(MPI_Status) * (*" + countVar + "));\n")
        olist.append("  if (c_array_of_statuses == NULL)\n")
        olist.append("    mpiPi_abort(\"Failed to allocate memory in " + funct + "\");\n")
        olist.append("}\n")

     #  Start generating call to C/Fortran common mpiP wrapper function
    if ( 'mips' in arch ) :
        olist.append("\nrc = mpiPif_" + funct + "( &saved_ret_addr, " )
    else :
        olist.append("\nrc = mpiPif_" + funct + "( &jbuf, " )
    argname = ""

    #  Iterate through mpiP wrapper function arguments, replacing argument with C version where appropriate
    for i in fdict[funct].paramConciseList:
        if ( i in xlateVarNames and
            ( (funct, i) in opaqueInArgDict or (funct, i) in opaqueOutArgDict) ):
            if ( i.count("array") > 0 ) or (i.count("status") > 0):
                argname = "c_" + i;
            else:
                argname = "&c_" + i;
        elif ( i in stringVarNames ) :
            argname = "c_" + i;
        else:
            argname = i

        if (fdict[funct].paramDict[i].pointerLevel == 0) \
           and (fdict[funct].paramDict[i].arrayLevel == 0) \
           and (fdict[funct].paramDict[i].basetype != "void"):
            olist.append(argname)
        elif (fdict[funct].paramDict[i].pointerLevel > 0):
            olist.append(argname)
        elif (fdict[funct].paramDict[i].arrayLevel > 0):
            olist.append(argname)
        else:
            pass

        if fdict[funct].paramConciseList.index(i) < len(fdict[funct].paramConciseList) - 1:
            olist.append(", ")

    olist.append(" );\n\n")
    olist.append("*ierr = (MPI_Fint)rc;\n")

    #  Generate post-call translation code if necessary
    xlateCode = []
    xlateDone = 0

    for i in range(len(xlateVarNames)) :

        xlateVarName = xlateVarNames[i]
        xlateType = xlateTypes[i]

        if ( (funct, xlateVarName) in opaqueOutArgDict \
            and opaqueOutArgDict[(funct, xlateVarName)] == xlateType ):

            #  Datatype translation is the only call where the translation function
            #  doesn't match the argument type.
            if ( xlateType == "MPI_Datatype" ):
                xlateFuncType = "MPI_Type"
            else:
                xlateFuncType = xlateType

            #  Generate array or scalar translation code
            if ( (funct, xlateVarName) in xlateFortranArrayExceptions ) :
              xlateCode.append(xlateVarName + "[*" + xlateFortranArrayExceptions[(funct,xlateVarName)] + \
              "] = " + xlateFuncType + "_c2f(c_" + xlateVarName + \
              "[*" + xlateFortranArrayExceptions[(funct, xlateVarName)] + "]);\n")
            elif ( xlateVarName.count("array") > 0 ):
                if ( xlateVarName.count("array_of_statuses") > 0 ):
                    xlateCode.append("{\n  int j; \n")
                    xlateCode.append("\n  if ( (size_t)" + xlateVarName + " != mpiPi_fortran.statuses_ignore ) {\n")
                    xlateCode.append("  for (j = 0; j < *count; j++) {\n")
                    xlateCode.append("    rc = " + xlateFuncType + "_c2f(&c_" + xlateVarName + "[j], &" + xlateVarName + "[j * mpiPi_fortran.status_size]);\n")
                    xlateCode.append("    if (rc != MPI_SUCCESS)\n")
                    xlateCode.append("      break;\n")
                    xlateCode.append("  }\n")
                    xlateCode.append("  free(c_" + xlateVarName + ");\n")
                    xlateCode.append("  }\n}\n\n")
                else:
                    xlateCode.append("{\n  int i; \n")
                    xlateCode.append("  for (i = 0; i < *" + countVar + "; i++) { \n")
                    xlateCode.append("    " + xlateVarName + "[i] = " + xlateFuncType + "_c2f(c_" + xlateVarName + "[i]);\n")
                    xlateCode.append("  }\n}\n")
            else:
                if ( xlateVarName.count("status") > 0 ):
                    xlateCode.append("\nif ( (size_t)" + xlateVarName + " != mpiPi_fortran.status_ignore ) {\n")
                    xlateCode.append("  rc = " + xlateFuncType + "_c2f(c_" + xlateVarName + ", " + xlateVarName + ");\n")
                    xlateCode.append("  free(c_" + xlateVarName + ");\n")
                    xlateCode.append("}\n")
                else:
                    xlateCode.append("*" + xlateVarName + " = " + xlateFuncType + "_c2f(c_" + xlateVarName + ");\n")

            xlateDone = 1

    #  If appropriate, increment any output indices
    if funct in incrementFortranIndexDict :
      if  incrementFortranIndexDict[funct][1] == 1 :
        xlateCode.append("if ( " + incrementFortranIndexDict[funct][0] + " >= 0 ) (" + incrementFortranIndexDict[funct][0] + ")++;\n")
      else:
        xlateCode.append("{ int i; for ( i = 0; i < " + incrementFortranIndexDict[funct][1] + "; i++)  " \
          + incrementFortranIndexDict[funct][0] + "[i]++;}\n")

    if xlateDone == 1 :
      olist.append("if ( rc == MPI_SUCCESS ) { \n")
      #print " xlateCode is ", xlateCode
      olist.extend(xlateCode)
      olist.append("}\n")

    #  Free allocated arrays
    for freeSym in freelist:
        olist.append("free("+freeSym+");\n")

    olist.append("return;\n" + "}" + " /* " + funct.lower() + " */\n")

    #if ( opaqueFound == 1 and xlateDone == 0 ):
    #    print "Function " + funct + " not translated!\n"

    print("   Wrapped " + funct)


def GenerateWrappers():
    global flist
    global fdict
    global arch
    global doWeakSymbols

    print("-----*----- Generating profiling wrappers")
    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + "/mpiP-wrappers.c"
    g = open(sname, "w")
    olist = StandardFileHeader(sname)

    olist.append("#include <string.h>\n")
    olist.append("#include \"mpiPi.h\"\n")
    olist.append("#include \"symbols.h\"\n")
    if doWeakSymbols == True :
      olist.append("#include \"weak-symbols.h\"\n")

    olist.append("#include \"mpiPi_def.h\"\n")
    olist.append("\n")

    for funct in flist:
        CreateWrapper(funct, olist)
    olist.append("\n")
    olist.append("\n")
    olist.append("/* eof */\n")
    g.writelines(olist)
    g.close()


def GetFortranSymbol(fsymtp, fsym) :
        ofsym = ""

        if fsymtp == 'symbol':
                        ofsym = fsym.lower()
        elif fsymtp == 'symbol_':
                        ofsym = fsym.lower() + "_"
        elif fsymtp == 'symbol__':
                        ofsym = fsym.lower() + "__"
        elif fsymtp == 'SYMBOL':
                        ofsym = fsym.upper()
        elif fsymtp == 'SYMBOL_':
                        ofsym = fsym.upper() + "_"
        elif fsymtp == 'SYMBOL__':
                        ofsym = fsym.upper() + "__"

        return ofsym


def GenerateWeakSymbols():
    global flist
    global f77symbol

    #
    # Generate Weak Symbols
    #

    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + "/weak-symbols.h"
    g = open(sname, "w")

    sname = cwd + "/weak-symbols-special.h"
    s = open(sname, "w")

    sname = cwd + "/weak-symbols-pcontrol.h"
    p = open(sname, "w")

    fmlist = ['symbol', 'symbol_', 'symbol__', 'SYMBOL', 'SYMBOL_', 'SYMBOL__' ]
    if f77symbol in fmlist :
      fmlist.remove(f77symbol)

    symflist = copy.deepcopy(flist)

    for funct in symflist:
      dfunc = GetFortranSymbol(f77symbol, funct)

      for mt in fmlist:
        wfunc = GetFortranSymbol(mt, funct)
        if funct in [ 'MPI_Init', 'MPI_Init_thread', 'MPI_Finalize'] :
          s.write("#pragma weak " + wfunc + " = " + dfunc + "\n")
        elif 'Pcontrol' in funct :
          p.write("#pragma weak " + wfunc + " = " + dfunc + "\n")
        elif fdict[funct].nowrapper == 0 :
          g.write("#pragma weak " + wfunc + " = " + dfunc + "\n")

    g.close()
    p.close()
    s.close()


def GenerateSymbolDefs():
    global flist
    global f77symbol

    cwd = os.getcwd()
    os.chdir(cwd)
    sname = cwd + "/symbols.h"

    symflist = copy.deepcopy(flist)
    symflist.append('mpipi_get_fortran_argc')
    symflist.append('mpipi_get_fortran_arg')

    g = open(sname, "w")
    for funct in symflist:
        if f77symbol == 'symbol':
            f77funct = funct.lower()
        elif f77symbol == 'symbol_':
            f77funct = funct.lower() + "_"
        elif f77symbol == 'symbol__':
            f77funct = funct.lower() + "__"
        elif f77symbol == 'SYMBOL':
            f77funct = funct.upper()
        elif f77symbol == 'SYMBOL_':
            f77funct = funct.upper() + "_"
        elif f77symbol == 'SYMBOL__':
            f77funct = funct.upper() + "__"
        else:
            f77funct = funct.lower()

        g.write("#define F77_" + funct.upper() + " " + f77funct + "\n")

    g.close()

def main():
    global fdict
    global flist
    global f77symbol
    global doOpaqueXlate
    global arch
    global doWeakSymbols
    global useSetJmp

    opts, pargs = getopt.getopt(sys.argv[1:], '', ['f77symbol=', 'xlate', 'arch=', 'weak', 'usesetjmp'])

    print("MPI Wrapper Generator ($Revision$)")
    #print "opts=",opts
    #print "pargs=",pargs

    f77symbol = 'symbol'
    doOpaqueXlate = False
    doWeakSymbols = False
    useSetJmp = False
    arch = 'unknown'

    for o, a in opts:
        if o == '--f77symbol':
            f77symbol = a
        if o == '--xlate':
            doOpaqueXlate = True
        if o == '--weak':
            doWeakSymbols = True
        if o == '--arch':
            arch = a
        if o == '--usesetjmp':
            useSetJmp = True


    ##### Load the input file
    if len(pargs) < 1:
        f = sys.__stdin__
    else:
        f = open(pargs[0])
    ReadInputFile(f)

    print("-----*----- Beginning parameter optimization")
    #ParameterOptimization()

    GenerateStructureFile()
    GenerateWrappers()
    GenerateSymbolDefs()
    if doWeakSymbols == True :
      GenerateWeakSymbols()
    GenerateLookup()


#####
##### Call main
#####
main()

#
#
#  <license>
#
#  Copyright (c) 2006, The Regents of the University of California.
#  Produced at the Lawrence Livermore National Laboratory
#  Written by Jeffery Vetter and Christopher Chambreau.
#  UCRL-CODE-223450.
#  All rights reserved.
#
#  This file is part of mpiP.  For details, see http://llnl.github.io/mpiP.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#  notice, this list of conditions and the disclaimer below.
#
#  * Redistributions in binary form must reproduce the above copyright
#  notice, this list of conditions and the disclaimer (as noted below) in
#  the documentation and/or other materials provided with the
#  distribution.
#
#  * Neither the name of the UC/LLNL nor the names of its contributors
#  may be used to endorse or promote products derived from this software
#  without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OF
#  THE UNIVERSITY OF CALIFORNIA, THE U.S. DEPARTMENT OF ENERGY OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
#  Additional BSD Notice
#
#  1. This notice is required to be provided under our contract with the
#  U.S. Department of Energy (DOE).  This work was produced at the
#  University of California, Lawrence Livermore National Laboratory under
#  Contract No. W-7405-ENG-48 with the DOE.
#
#  2. Neither the United States Government nor the University of
#  California nor any of their employees, makes any warranty, express or
#  implied, or assumes any liability or responsibility for the accuracy,
#  completeness, or usefulness of any information, apparatus, product, or
#  process disclosed, or represents that its use would not infringe
#  privately-owned rights.
#
#  3.  Also, reference herein to any specific commercial products,
#  process, or services by trade name, trademark, manufacturer or
#  otherwise does not necessarily constitute or imply its endorsement,
#  recommendation, or favoring by the United States Government or the
#  University of California.  The views and opinions of authors expressed
#  herein do not necessarily state or reflect those of the United States
#  Government or the University of California, and shall not be used for
#  advertising or product endorsement purposes.
#
#  </license>
#
#
# --- EOF
