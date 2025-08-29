
# Python to C++ conversions
from multipers.filtrations cimport One_critical_filtration,Multi_critical_filtration
from libcpp.vector cimport vector
from libcpp cimport bool
cimport numpy as cnp
import numpy as np
from libc.stdint cimport int32_t, int64_t
from cython.operator cimport dereference
###### ------------------- PY TO CPP
#### ---------- 

cdef inline Multi_critical_filtration[int32_t] _py2kc_i32(int32_t[:,:] filtrations) noexcept nogil:
    # cdef int32_t[:,:] filtrations = np.asarray(filtrations_, dtype=np.int32)
    cdef Multi_critical_filtration[int32_t] out
    out.set_num_generators(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out[i].resize(filtrations.shape[1])
        for j in range(filtrations.shape[1]):
            out[i][j] = filtrations[i,j]
    out.simplify()
    return out

cdef inline One_critical_filtration[int32_t] _py21c_i32(int32_t[:] filtration) noexcept nogil:
    # cdef int32_t[:] filtration = np.asarray(filtration_, dtype=np.int32)
    cdef One_critical_filtration[int32_t] out = One_critical_filtration[int32_t](0)
    out.reserve(len(filtration))
    for i in range(len(filtration)):
        out.push_back(filtration[i])
    return out


cdef inline vector[One_critical_filtration[int32_t]] _py2v1c_i32(int32_t[:,:] filtrations) noexcept nogil:
    # cdef int32_t[:,:] filtrations = np.asarray(filtrations_, dtype=np.int32)
    cdef vector[One_critical_filtration[int32_t]] out
    out.reserve(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out.push_back(_py21c_i32(filtrations[i,:]))
    return out


###### ------------------- CPP to PY


## CYTHON BUG: using tuples here will cause some weird issues. 
cdef inline _ff21cview_i32(One_critical_filtration[int32_t]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t num_parameters = dereference(x).num_parameters()
  if copy and duplicate and not dereference(x).is_finite():
    return np.full(shape=duplicate, fill_value=dereference(x)[0])
  cdef int32_t[:] x_view = <int32_t[:num_parameters]>(&(dereference(x)[0]))
  return np.array(x_view) if copy else np.asarray(x_view)

cdef inline _ff2kcview_i32(Multi_critical_filtration[int32_t]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t k = dereference(x).num_generators()
  return [_ff21cview_i32(&(dereference(x)[i]), copy=copy, duplicate=duplicate) for i in range(k)]


cdef inline  _vff21cview_i32(vector[One_critical_filtration[int32_t]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff21cview_i32(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]

cdef inline  _vff2kcview_i32(vector[Multi_critical_filtration[int32_t]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff2kcview_i32(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]
###### ------------------- PY TO CPP
#### ---------- 

cdef inline Multi_critical_filtration[int64_t] _py2kc_i64(int64_t[:,:] filtrations) noexcept nogil:
    # cdef int64_t[:,:] filtrations = np.asarray(filtrations_, dtype=np.int64)
    cdef Multi_critical_filtration[int64_t] out
    out.set_num_generators(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out[i].resize(filtrations.shape[1])
        for j in range(filtrations.shape[1]):
            out[i][j] = filtrations[i,j]
    out.simplify()
    return out

cdef inline One_critical_filtration[int64_t] _py21c_i64(int64_t[:] filtration) noexcept nogil:
    # cdef int64_t[:] filtration = np.asarray(filtration_, dtype=np.int64)
    cdef One_critical_filtration[int64_t] out = One_critical_filtration[int64_t](0)
    out.reserve(len(filtration))
    for i in range(len(filtration)):
        out.push_back(filtration[i])
    return out


cdef inline vector[One_critical_filtration[int64_t]] _py2v1c_i64(int64_t[:,:] filtrations) noexcept nogil:
    # cdef int64_t[:,:] filtrations = np.asarray(filtrations_, dtype=np.int64)
    cdef vector[One_critical_filtration[int64_t]] out
    out.reserve(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out.push_back(_py21c_i64(filtrations[i,:]))
    return out


###### ------------------- CPP to PY


## CYTHON BUG: using tuples here will cause some weird issues. 
cdef inline _ff21cview_i64(One_critical_filtration[int64_t]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t num_parameters = dereference(x).num_parameters()
  if copy and duplicate and not dereference(x).is_finite():
    return np.full(shape=duplicate, fill_value=dereference(x)[0])
  cdef int64_t[:] x_view = <int64_t[:num_parameters]>(&(dereference(x)[0]))
  return np.array(x_view) if copy else np.asarray(x_view)

cdef inline _ff2kcview_i64(Multi_critical_filtration[int64_t]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t k = dereference(x).num_generators()
  return [_ff21cview_i64(&(dereference(x)[i]), copy=copy, duplicate=duplicate) for i in range(k)]


cdef inline  _vff21cview_i64(vector[One_critical_filtration[int64_t]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff21cview_i64(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]

cdef inline  _vff2kcview_i64(vector[Multi_critical_filtration[int64_t]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff2kcview_i64(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]
###### ------------------- PY TO CPP
#### ---------- 

cdef inline Multi_critical_filtration[float] _py2kc_f32(float[:,:] filtrations) noexcept nogil:
    # cdef float[:,:] filtrations = np.asarray(filtrations_, dtype=np.float32)
    cdef Multi_critical_filtration[float] out
    out.set_num_generators(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out[i].resize(filtrations.shape[1])
        for j in range(filtrations.shape[1]):
            out[i][j] = filtrations[i,j]
    out.simplify()
    return out

cdef inline One_critical_filtration[float] _py21c_f32(float[:] filtration) noexcept nogil:
    # cdef float[:] filtration = np.asarray(filtration_, dtype=np.float32)
    cdef One_critical_filtration[float] out = One_critical_filtration[float](0)
    out.reserve(len(filtration))
    for i in range(len(filtration)):
        out.push_back(filtration[i])
    return out


cdef inline vector[One_critical_filtration[float]] _py2v1c_f32(float[:,:] filtrations) noexcept nogil:
    # cdef float[:,:] filtrations = np.asarray(filtrations_, dtype=np.float32)
    cdef vector[One_critical_filtration[float]] out
    out.reserve(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out.push_back(_py21c_f32(filtrations[i,:]))
    return out


###### ------------------- CPP to PY


## CYTHON BUG: using tuples here will cause some weird issues. 
cdef inline _ff21cview_f32(One_critical_filtration[float]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t num_parameters = dereference(x).num_parameters()
  if copy and duplicate and not dereference(x).is_finite():
    return np.full(shape=duplicate, fill_value=dereference(x)[0])
  cdef float[:] x_view = <float[:num_parameters]>(&(dereference(x)[0]))
  return np.array(x_view) if copy else np.asarray(x_view)

cdef inline _ff2kcview_f32(Multi_critical_filtration[float]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t k = dereference(x).num_generators()
  return [_ff21cview_f32(&(dereference(x)[i]), copy=copy, duplicate=duplicate) for i in range(k)]


cdef inline  _vff21cview_f32(vector[One_critical_filtration[float]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff21cview_f32(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]

cdef inline  _vff2kcview_f32(vector[Multi_critical_filtration[float]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff2kcview_f32(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]
###### ------------------- PY TO CPP
#### ---------- 

cdef inline Multi_critical_filtration[double] _py2kc_f64(double[:,:] filtrations) noexcept nogil:
    # cdef double[:,:] filtrations = np.asarray(filtrations_, dtype=np.float64)
    cdef Multi_critical_filtration[double] out
    out.set_num_generators(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out[i].resize(filtrations.shape[1])
        for j in range(filtrations.shape[1]):
            out[i][j] = filtrations[i,j]
    out.simplify()
    return out

cdef inline One_critical_filtration[double] _py21c_f64(double[:] filtration) noexcept nogil:
    # cdef double[:] filtration = np.asarray(filtration_, dtype=np.float64)
    cdef One_critical_filtration[double] out = One_critical_filtration[double](0)
    out.reserve(len(filtration))
    for i in range(len(filtration)):
        out.push_back(filtration[i])
    return out


cdef inline vector[One_critical_filtration[double]] _py2v1c_f64(double[:,:] filtrations) noexcept nogil:
    # cdef double[:,:] filtrations = np.asarray(filtrations_, dtype=np.float64)
    cdef vector[One_critical_filtration[double]] out
    out.reserve(filtrations.shape[0])
    for i in range(filtrations.shape[0]):
        out.push_back(_py21c_f64(filtrations[i,:]))
    return out


###### ------------------- CPP to PY


## CYTHON BUG: using tuples here will cause some weird issues. 
cdef inline _ff21cview_f64(One_critical_filtration[double]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t num_parameters = dereference(x).num_parameters()
  if copy and duplicate and not dereference(x).is_finite():
    return np.full(shape=duplicate, fill_value=dereference(x)[0])
  cdef double[:] x_view = <double[:num_parameters]>(&(dereference(x)[0]))
  return np.array(x_view) if copy else np.asarray(x_view)

cdef inline _ff2kcview_f64(Multi_critical_filtration[double]* x, bool copy=False, int duplicate=0):
  cdef Py_ssize_t k = dereference(x).num_generators()
  return [_ff21cview_f64(&(dereference(x)[i]), copy=copy, duplicate=duplicate) for i in range(k)]


cdef inline  _vff21cview_f64(vector[One_critical_filtration[double]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff21cview_f64(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]

cdef inline  _vff2kcview_f64(vector[Multi_critical_filtration[double]]& x, bool copy = False, int duplicate=0):
  cdef Py_ssize_t num_stuff = x.size()
  return [_ff2kcview_f64(&(x[i]), copy=copy, duplicate=duplicate) for i in range(num_stuff)]
