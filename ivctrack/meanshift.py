# -*- coding: utf-8 -*-
'''Test the scipy weave module to the meanshift function (computed on triangles)

.. note::

    use Weave for C compilation
'''
__author__ = 'Copyright (C) 2012, Olivier Debeir <odebeir@ulb.ac.be>'
__license__ ="""
pyrankfilter is a python module that implements 2D numpy arrays rank filters, the filter core is C-code
compiled on the fly (with an ad-hoc kernel).

Copyright (C) 2012  Olivier Debeir

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import numpy as npy
from scipy.weave import inline
from scipy.misc import imread
from cache_decorators import lru_cache

def dtype2ctype(array):
    """convert numpy type in C equivalent type
    """
    types = {
        npy.dtype(npy.float64): 'double',
        npy.dtype(npy.float32): 'float',
        npy.dtype(npy.int32):   'int',
        npy.dtype(npy.uint32):  'unsigned int',
        npy.dtype(npy.int16):   'short',
        npy.dtype(npy.uint8):   'unsigned char',
        npy.dtype(npy.uint16):  'unsigned short',
    }
    return types.get(array.dtype)

def LUT(type,exp=1):
    """Returns a 256 wide numpy array LUT exp allo to enhance the character of the lut
    """
    if type is 'white':
        return (npy.arange(256.0,dtype = 'float64'))**exp
    if type is 'black':
        return (255.0-(npy.arange(256.0,dtype = 'float64')))**exp

meanshift_features = ['xg','yg','surf','surfalpha','totalvalue','vmax','vmin','vmean']

@lru_cache()
def find_c_code(path):
    """search for external c-code
    """
    try:
        import pkgutil
        extra_code = pkgutil.get_data(__name__, path)
    except ImportError:
        import pkg_resources
        extra_code = pkg_resources.resource_string(__name__, path)
    return extra_code

def meanshift(ima,triangleList,offset_x,offset_y,lut=None):
    """compute the meanshift for each triangle in the triangleList

    :param ima: image array
    :type ima: uint8
    :param lut: lookup table applied to each ima pixel
    :type lut: float64 table of lookup (8bit=256 values)
    :param triangleList: list of the triangle to process (array with one line per triangle)
    :type array:
    :param offset_x: constant value added to triangle coordinates
    :type offset_x: float
    :param offset_y: constant value added to triangle coordinates
    :type offset_y: float
    :param verbose: True : displays details during C code executes (default is False)
    :type verbose: Bool
    :returns:  out[]

    |   centroid for each triangle and several statistics such as area, sum,...
    |   out[0] = (double)sumXw;//centroid
    |   out[1] = (double)sumYw;//centroid
    |   out[2] = (double)surf;//surfCrisp
    |   out[3] = (double)surfalpha;//surfAlpha
    |   out[4] = (double)totalvalue;//sum
    |   out[5] = (double)gmax; //max
    |   out[6] = (double)gmin; //min
    |   if(surfalpha>0.0):
    |       out[7] = (double)(totalvalue/surfalpha);//mean
    |   else:
    |       out[7] = (double)0.0;

    :raises: TypeError
    """

    if not isinstance(ima,npy.ndarray):
        raise TypeError('2D numpy.array expected')
    if not (ima.dtype == npy.uint8) :
        raise TypeError('uint8 numpy.array expected')
    if not(len(ima.shape) == 2):
        raise TypeError('2D numpy.array expected')

    #code contains the main watershed C code
    code = \
"""
unsigned char *IN       = (unsigned char *) PyArray_GETPTR1(ima_array,0);
double *OUT      = (double *) PyArray_GETPTR1(out_array,0);
double *LUT      = (double *) PyArray_GETPTR1(lut_array,0);
double *TRIANGLE = (double *) PyArray_GETPTR1(triangle_array,0);

int N_IN = PyArray_SIZE(ima_array);
int m_IN = PyArray_DIM(ima_array,0); 
int n_IN = PyArray_DIM(ima_array,1);
int sizex = n_IN;
int sizey = m_IN;  
int n;  
double off_x = offset_x;
double off_y = offset_y;

// call the function defined in the meanshift.c file
//return an int to Python

n = compute_g(IN,sizex,sizey,off_x,off_y,TRIANGLE,OUT,LUT);

"""

    extra_code = find_c_code('c-code/meanshift.c')

    if lut is None:
        lut = npy.arange(256,dtype = 'float64')

    n = triangleList.shape[0]
    shift = npy.ndarray((n,8),dtype = 'float64', order='C')
    out = npy.ndarray(8,dtype = 'float64', order='C')

    force = False
    for i in range(n):
        triangle = triangleList[i,:]
        inline(code, ['ima','out','triangle','lut','offset_x','offset_y'],support_code=extra_code,force=force)
        shift[i,:] = out
        force = False
    return shift

@lru_cache()
def pre_compute_cos_sin_table(N):
    """returns the cos and sin for each sector of 2pi/N
    """
    i = npy.arange(N)
    c = npy.cos(i*2*npy.pi/N)
    s = npy.sin(i*2*npy.pi/N)
    c1 = npy.cos((i+1)*2*npy.pi/N)
    s1 = npy.sin((i+1)*2*npy.pi/N)

    return (c,s,c1,s1)

@lru_cache()
def pre_compute_cos_sin_table2(N):
    """returns the cos and sin for each sector of 2pi/N
    """
    i = npy.arange(N)
    cos_table = npy.cos(i*2*npy.pi/N)
    sin_table = npy.sin(i*2*npy.pi/N)
    cos_table1 = npy.cos((i+1)*2*npy.pi/N)
    sin_table1 = npy.sin((i+1)*2*npy.pi/N)
    cos_table_5 = npy.cos((i+.5)*2*npy.pi/N)
    sin_table_5 = npy.sin((i+.5)*2*npy.pi/N)
    return (cos_table,sin_table,cos_table1,sin_table1,cos_table_5,sin_table_5)

def generate_triangles(x,y,N,R,target=None):
    """Returns an ensemble of triangles centered on xy
    if R is an iterable, each radius may be different
    if target is Nx6 ndarray, the value are copied inplace
    """
    if target is None:
        triangleList = npy.ndarray((N,6))
    else:
        triangleList = target

    #external pies
    cos_table,sin_table,cos_table1,sin_table1 = pre_compute_cos_sin_table(N)
    triangleList[:,0:2] = (x,y)
    triangleList[:,2] = x+R*cos_table
    triangleList[:,3] = y+R*sin_table
    triangleList[:,4] = x+R*cos_table1
    triangleList[:,5] = y+R*sin_table1

    return triangleList

def generate_inverted_triangles(x,y,N,R,target=None):
    """Returns an ensemble of triangles centered on xy but with large base at the center
    if target is Nx6 ndarray, the value are copied inplace
    """
    if target is None:
        triangleList = npy.ndarray((N,6))
    else:
        triangleList = target

    #internal pies
    cos_table,sin_table,cos_table1,sin_table1,cos_table_5,sin_table_5 = pre_compute_cos_sin_table2(N)
    triangleList[:,0] = x-(R*cos_table_5)
    triangleList[:,1] = y-(R*sin_table_5)
    triangleList[:,2] = x+(R*cos_table)
    triangleList[:,3] = y+(R*sin_table)
    triangleList[:,4] = x+(R*cos_table1)
    triangleList[:,5] = y+(R*sin_table1)
    return triangleList  
      
def testMeanshift():
    """open a binarised test image, compute meanshift for some triangle
    """

    import matplotlib.pyplot as plt

    print 'test MS'
    im = imread('../test/data/exp0001.jpg')
    cellLocations = [(340,190),(474,331),(120,231)]
    n = len(cellLocations)
    N = 16
    RWhite = 30
    RBlack = 15
    triangleListBlack = npy.ndarray((0,6))
    triangleListWhite = npy.ndarray((0,6))

    for x,y in cellLocations:
        tWhite = generate_triangles(x,y,N,RWhite)
        tBlack = generate_inverted_triangles(x,y,N,RBlack)
        triangleListWhite = npy.vstack((triangleListWhite,tWhite))
        triangleListBlack= npy.vstack((triangleListBlack,tBlack))

    shift_white = meanshift(im,triangleListWhite,0.0,0.0,lut = LUT('white',10))
    shift_black = meanshift(im,triangleListBlack,0.0,0.0,lut = LUT('black',10))

    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    plt.imshow(im, interpolation='nearest')

    #draw triangle
    idxx = [0,2,4,0] 
    idxy = [1,3,5,1]
    for tri in triangleListBlack:        
        plt.plot(npy.take(tri,idxx),npy.take(tri,idxy),color = [.5,.5,.5])
    for tri in triangleListWhite:
        plt.plot(tri[0:6:2],tri[1:6:2],color = [.5,.5,.5])
        
    #draw centroids
    for sh in shift_white:
        r = plt.Rectangle((sh[0]-1,sh[1]-1),3,3, facecolor=[.8,.8,.8])
        ax.add_artist(r)
    for sh in shift_black:
        r = plt.Rectangle((sh[0]-1,sh[1]-1),3,3, facecolor=[.1,.1,.1])
        ax.add_artist(r)

    plt.show()


if __name__ == "__main__":
    
    testMeanshift()
