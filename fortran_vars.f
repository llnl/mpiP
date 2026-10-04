! -*- Fortran -*-
!
!   mpiP MPI Profiler ( http://llnl.github.io/mpiP )
!
!   Please see COPYRIGHT AND LICENSE information at the end of this file.
!
!   -----
!
!   fortran_vars.f -- gathers the memory locations of the
!                     pointers MPI_IN_PLACE, MPI_BOTTOM,
!                     MPI_STATUS_IGNORE and MPI_STATUSES_IGNORE,
!                     which are in a COMMON block and therefore 
!                     have different addresses than their 
!                     C equivalents.
! 
!   $Id$
!

      subroutine fortran_vars ( f_in_place, f_bottom, f_status_ignore,
     &                          f_statuses_ignore, f_status_size ) 
     &                          bind ( C, name="fortran_vars" )

      use iso_c_binding, only: c_size_t
      implicit none
      include 'mpif.h'

      integer (kind=c_size_t), intent (inout) :: f_in_place, f_bottom
      integer (kind=c_size_t), intent (inout) :: f_status_ignore, 
     &                                           f_statuses_ignore,
     &                                           f_status_size

      f_in_place = LOC(MPI_IN_PLACE)
      f_bottom = LOC(MPI_BOTTOM)
      f_status_ignore = LOC(MPI_STATUS_IGNORE)
      f_statuses_ignore = LOC(MPI_STATUSES_IGNORE)
      f_status_size = MPI_STATUS_SIZE

      return
      end subroutine fortran_vars
