#!/usr/bin/python
"""Tools for geo-related tasks often used with HYCOM."""

import numpy as np

# 
import math

#
#import pyproj


# ################################################
# CLASSES
# ################################################

class Struct:
    """Create a custom class from a dictionary
    Usage
    =====
    Call with a (non-nested) dictionary as argument.
    """
    def __init__(self, entries={}):
        self.__dict__.update(entries)
    def __setitem__(self, k, v):
        self.__dict__[k] = v
    def __getitem__(self, k):
        return self.__dict__[k]
    def __repr__(self):
        return '\n'.join(
            ['{} : {}'.format(
                k,repr(v)) for k,v in sorted(self.__dict__.iteritems())])
    
# ################################################
# FUNCTIONS
# ################################################

# ########################################################################

def latlen(lat):
    """Return the lenght of one degree of latitude at the given latitude [deg] in metres"""
    lat = np.radians(lat)
    return 111132.954 - 559.822 * np.cos(2.*lat) + 1.175 * np.cos(4.*lat)

def lonlen(lat,
           a=6378137.0, # WGS84 ellipsoid
           b=6356752.3142):
    """Return the lenght of one degree of longitude at the given latitude [deg] in metres"""
    esq = (a**2 - b**2)/a**2
    lat = np.radians(lat)
    return np.pi * a * np.cos(lat) / ( 180. * np.sqrt(1 - esq*np.sin(lat)**2) )

def dist2lon(dist,lat):
    """Convert from distance [m] to decimal degree of longitude"""
    return dist / lonlen(lat)

def dist2lat(dist,lat):
    """Convert from distance [m] to decimal degree of latitude"""
    return dist / latlen(lat)

# ########################################################################
def spherical2cartesian(lon,lat):
    """Convert spherical to cartesian coordinates"""
    rlon,rlat = np.map(np.radians,lon,lat)
    x = np.cos(rlat) * np.cos(rlon)
    y = np.cos(rlat) * np.sin(rlon)
    z = np.sin(rlat)
    return x,y,z

# ########################################################################
def arclength(lon1, lat1, lon2, lat2):
    """Returns arc length [radians] between two points [dec deg]

    Parameters
    ==========
    lon1,lat1,lon2,lat2 : float [dec deg]
        coordinates for two points

    Returns
    =======
    arclength : float [rad]
    
    Credits
    =======
    http://code.google.com/p/pyroms/
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # compute arc length
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    b = 2. * np.arcsin(np.sqrt(a))
    return b


# ########################################################################
def haversine(lon1, lat1, lon2, lat2):
    """Returns the great circle distance between two positions on a sphere.

    Parameters
    ==========
    lon1,lat1,lon2,lat2 : float [dec deg]
        coordinates for two points

    Returns
    =======
    distance [metres]
    
    """
    
    c = arclength(lon1, lat1, lon2, lat2)
    return 6378.1 * 1e3 * c


# ########################################################################
def bearing(lon1, lat1, lon2, lat2):
    """Returns the bearing between two points on a sphere

    Parameters
    ==========
    lon,lat : float [decimal degrees]

    Returns
    =======
    bearing : float [decimal degrees]
    
    Credits
    =======
    http://www.movable-type.co.uk/scripts/latlong.html
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    
    # compute bearing
    return np.degrees(
        np.arctan2(
            (np.sin(lon2-lon1) * np.cos(lat2)),
            (np.cos(lat1) * np.sin(lat2) -
             np.sin(lat1) * np.cos(lat2) * np.cos(lon2-lon1))) )


# ########################################################################
def waypoints(lon1, lat1, lon2, lat2, f=0.5, n=None):
    """Returns intermediate waypoints on a great circle

    connecting the two given end points at a fraction f [%]
    of the distance from lon1,lat1.
    
    Parameters
    ==========
    lon1,lat1,lon2,lat2 : float
        start and end point coordinates [deg]
    f : float/array, optional
        fraction (can be a vector)
    n : integer, optinal
        alternatively to f, number of waypoints

    Note
    ====
    Either f or n must be provided. If both are, if is used.
    
    Credits
    =======
    http://williams.best.vwh.net/avform.htm#Intermediate
    """
    # if given, compute f from n
    if n != None:
        f = np.linspace(0,1,n)
    
    # compute arc length between points
    d = arclength(lon1, lat1, lon2, lat2)

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    
    # compute waypoints
    a = np.sin((1.-f)*d) / np.sin(d)
    b = np.sin(f*d) / np.sin(d)
    x = a*np.cos(lat1)*np.cos(lon1) + b*np.cos(lat2)*np.cos(lon2)
    y = a*np.cos(lat1)*np.sin(lon1) + b*np.cos(lat2)*np.sin(lon2)
    z = a*np.sin(lat1)              + b*np.sin(lat2)
    lat = np.arctan2(z,np.sqrt(x**2+y**2.))
    lon = np.arctan2(y,x)
    return map(np.degrees,[lon,lat])


# ########################################################################
def waypoints_segments(lons, lats, f=None, n=10, returndist=False):
    """Refines a given lon-lat section by adding waypoints

    such that the resulting axis has n steps from one given point to the next.

    Parameters
    ==========
    lons,lats : array
        vectors defining a lon,lat track to be refined
    f : array, optional
        fraction at which to insert waypoints (favored over n)
    n : int, optional
        target number of steps from one point to the next
    returndist : bool, optional
        whether or not to return an axis with distance from first point

    Returns
    =======
    lons,lats : tuple of new axes
    lons,lats,dist : if returndist=True

    Dependencies
    ============
    waypoints, haversine
    """

    # generate fraction
    if f == None:
        f = np.linspace(0,1,n)
    else:
        n = len(f)

    # get lengths and initialize
    ntot = (len(lons)-1)*n
    waylons,waylats = np.zeros(ntot),np.zeros(ntot)

    # iterate through segments
    for p in range(len(lons)-1):
        ia = p*n
        io = (p+1)*n
        
        # get waypoints
        waylons[ia:io],waylats[ia:io] = waypoints(lons[p],lats[p],lons[p+1],lats[p+1],f)

    # compute distance
    if returndist:    
        dist = np.cumsum([0.]+[haversine(lon1, lat1, lon2, lat2) for lon1,lat1,lon2,lat2 in zip(waylons[1:],waylats[1:],waylons[:-1],waylats[:-1])])
        
        return waylons,waylats,dist
    else:
        return waylons,waylats



# ########################################################################
def binary_search_grid(gridlon,gridlat,px,py,returndist=False):
    """Find nearest grid points on a lon-lat grid

    Parameters
    ==========
    gridlon,gridlat : arrays (1D or 2D)
        longitude / latitude grid
    px,py : floats/lists/arrays
        one or more position to be found in the grid
    returndist : bool, optional
        return distance from target point to nearest grid point

    Returns
    =======
    ix,iy : indices for nearest points on grid (default)
    ix,iy,dist : same as above plus distance from given positions (returndist=True)

    Dependencies
    ============
    haversine
    
    Credits
    =======
    Mads Hvid Ribergaard mhri@dmi.dk (MATLAB version)
       
    """
    idm,jdm = np.shape(gridlon)

    def binary_search_grid_single(gridlon,gridlat,x,y):
        # initialize indices
        Lo = np.array([0,0])
        Hi = np.array([idm-1,jdm-1])

        def centerpoints(Lo,Hi):
            imid = np.array([Lo[0] + np.floor(.25*(Hi[0]-Lo[0])),
                             Hi[0] - np.floor(.25*(Hi[0]-Lo[0]))],dtype=int)
            jmid = np.array([Lo[1] + np.floor(.25*(Hi[1]-Lo[1])),
                             Hi[1] - np.floor(.25*(Hi[1]-Lo[1]))],dtype=int)
            return np.ix_(imid,jmid)
        
        imid,jmid = centerpoints(Lo,Hi)

        # Loop: Recrusive decrease square until 2*2 square is found
        while np.diff(imid) > 1 or np.diff(jmid) > 1:

            # calculate distance from point x,y to four corner grid points
            kmin = haversine(gridlon[imid,jmid],gridlat[imid,jmid],x,y).argmin()

            # determine which corner point is nearest
            if kmin == 0:
                Hi = Hi - np.floor(.5*(Hi-Lo))
            elif kmin == 1:
                Lo[0] = Lo[0] + np.floor(.5*(Hi[0]-Lo[0]))
                Hi[1] = Hi[1] - np.floor(.5*(Hi[1]-Lo[1]))
            elif kmin == 2:
                Lo[1] = Lo[1] + np.floor(.5*(Hi[1]-Lo[1]))
                Hi[0] = Hi[0] - np.floor(.5*(Hi[0]-Lo[0]))
            elif kmin == 3:
                Lo = Lo + np.floor(.5*(Hi-Lo))
          
            imid,jmid = centerpoints(Lo,Hi)

        # Find closest point from the remaining 2*2 square
        dist = haversine(gridlon[imid,jmid],gridlat[imid,jmid],x,y); 
        print(dist,dist.argmin())
        kmin = dist.argmin()
        if kmin == 0:
            ele = Lo
        elif kmin == 1:
            ele = np.array([Hi[0],Lo[1]])
        elif kmin == 2:
            ele = np.array([Lo[0],Hi[1]])
        elif kmin == 3:
            ele = Hi

        # Did we find global minimum or just local (weired grid)?
        #check here

        ele = ele.astype(int)
        return ele[0],ele[1],dist.flat[kmin]

    # compute for all given points
    try:
        n=len(px)
        ix,iy = np.zeros((n),np.int),np.zeros((n),np.int)
        dist = np.zeros((n))
        for p in range(n):
            ix[p],iy[p],dist[p] = binary_search_grid_single(gridlon,gridlat,px[p],py[p])
    except TypeError:
        ix,iy,dist = binary_search_grid_single(gridlon,gridlat,px,py)

    if returndist:
        return ix,iy,dist
    else:
        return ix,iy


# ########################################################################
def nearest_gridpt(gridlon,gridlat,px,py,unravel=True):
    """Find nearest points in a lon-lat grid

    computing the distance for each grid point (slow for large grids!).

    Parameters
    ==========
    gridlon,gridlat : arrays (1D or 2D)
        longitude / latitude grid
    px,py : floats/lists/arrays
        one or more position to be found in the grid
    unravel : bool, optional
        whether to return multidimensional or linear index

    Returns
    =======
    ind : array
        linear index, if unravel=False
    ix,iy : tuple of arrays
        multiple indices, if unravel=True (default)

    Dependencies
    ============
    haversine

    """
    try:
        ind = np.array([haversine(gridlon,gridlat,px[p],py[p]).argmin() for p in range(len(px))])
    except TypeError:
        ind = haversine(gridlon,gridlat,px,py).argmin()

    if not unravel or len(gridlon.shape) == 1:
        return ind
    else:
        return np.unravel_index(ind,gridlon.shape)
        


# ########################################################################
def secline(gridlon,gridlat,px,py,f=None,n=50):
    """
    Find nearest point(s) on a grid for a section defined as piecewise Great Circles

    Parameters
    ==========
    gridlon,gridlat : float
        grid longitudes,latitudes
    px,py : array
        fixpoints for new longitude vector
    f : array, optional
        fraction at which to insert waypoints (favored over n)
    n : int, optional
        used to generate f = np.linspace(0,1,n)

    Returns
    =======
    Dictionary with fields
    ind : int array
        linear index for points
    bearing : float [dec deg]
        bearing from one point to next, due north

    Note
    ====
    The linear index is returned in row-major order (C-like).
    MATLAB uses column-major order (Fortran-like)
    
    Dependencies
    ============
    waypoints_segments  nearest_gridpt  secline_uv (inline)
    
    """ 
    SEC = {}
    
    # refine waypoints
    pxx,pyy = waypoints_segments(px, py, f, n)
    
    # find nearest grid points
    ind = nearest_gridpt(gridlon,gridlat,pxx,pyy,unravel=False)
    
    # remove repeating points
    mask = np.insert((ind[1:] != ind[:-1]),0,ind[0])
    ind = ind[mask]
    pxx,pyy = pxx[mask],pyy[mask]
    SEC['ind'] = ind
    SEC['pxx'] = pxx
    SEC['pyy'] = pyy

    # get grid positions
    lons,lats = gridlon.flat[ind],gridlat.flat[ind]
    
    # generate distance axis
    SEC['dist'] = haversine(lons,lats,pxx,pyy)
    
    # compute bearings between consecutive points
    SEC['bearing'] = bearing(lons[:-1], lats[:-1], lons[1:], lats[1:])

    return Struct(SEC)


# ########################################################################
def secline_uv(ind,dim,ijdir=(1,1)):
    """Find indices for (u,v) on a staggered Arakawa C-grid (eg. HYCOM).

    Intended for usage with hc.transport

    """
    in_p = ind
    
    i,j = np.unravel_index(in_p,dim)

    di = ijdir[0]*np.diff(i) ; di = np.append(di,di[-1])
    dj = ijdir[1]*np.diff(j) ; dj = np.append(dj,dj[-1])

    ij = np.hstack((np.array([[di[0],dj[0]]]).T,np.vstack((di,dj))))

    for n in range(len(in_p)):
        k = in_p[n]

    raise NotImplementedError

# ########################################################################
def getEndPoint(lon1,lat1,bearing,xnm):
   """Find (lon2,lat2) at xnm distance from a point (lon1,lat1)

   Use for drawing a storm size (in nautical miles)
	hy Hyun-Sook Kim 8/18/2016
   """
   
   R=6378.1			# Radius of the Earth in km
   brng=math.radians(bearing)	# Convert degrees to radians
   d = xnm*1.852			# Convert nautical miles to km
 
   lon1 = math.radians(lon1)
   lat1 = math.radians(lat1)

     
   lat2 = math.asin( math.sin(lat1)*math.cos(d/R) + math.cos(lat1)*math.sin(d/R)*math.cos(brng) )
  
   xxx = math.sin(brng)*math.sin(d/R)*math.cos(lat1)
   yyy = math.cos(d/R) - math.sin(lat1)*math.sin(lat2)
   lon2 = lon1 + math.atan2(xxx,yyy)

   lat2=math.degrees(lat2)
   lon2=math.degrees(lon2)

   return lon2,lat2

# ########################################################################
def getPointsCircle(lon0,lat0,xnm):
   """Find a set (lons,lats) for a circle with a radius of xnm distance 
      from a point of interest (lon0,lat0)

   Use for drawing a storm size (in nautical miles)
        hy Hyun-Sook Kim 8/18/2016
   """

   R=6378.1                     # Radius of the Earth in km
   d = xnm*1.852                  # Convert nautical miles to km

   # convert degree to radians
   lon0 = math.radians(lon0)
   lat0 = math.radians(lat0)

   lns=[]
   lts=[];
   for x in range(0,75,1):
      brng=math.radians(x*5)   # Convert degrees to radians
      lt = math.asin( math.sin(lat0)*math.cos(d/R) + math.cos(lat0)*math.sin(d/R)*math.cos(brng) )

      xx = math.sin(brng)*math.sin(d/R)*math.cos(lat0)
      yy = math.cos(d/R)-math.sin(lat0)*math.sin(lt)
      ln = lon0 + math.atan2(xx,yy)

      lts.append(math.degrees(lt))
      lns.append(math.degrees(ln))

   return lns,lts

