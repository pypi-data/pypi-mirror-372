"""@package docstring
Iso2Mesh for Python - Mesh data queries and manipulations

Copyright (c) 2024-2025 Qianqian Fang <q.fang at neu.edu>
"""

__all__ = [
    "finddisconnsurf",
    "surfedge",
    "volface",
    "extractloops",
    "meshconn",
    "nodevolume",
    "elemvolume",
    "neighborelem",
    "layersurf",
    "faceneighbors",
    "edgeneighbors",
    "maxsurf",
    "flatsegment",
    "mesheuler",
    "orderloopedge",
    "bbxflatsegment",
    "surfplane",
    "raytrace",
    "surfinterior",
    "surfpart",
    "surfseeds",
    "meshquality",
    "meshedge",
    "meshface",
    "surfacenorm",
    "nodesurfnorm",
    "uniqedges",
    "uniqfaces",
    "innersurf",
    "advancefront",
    "meshreorient",
    "meshcentroid",
    "elemfacecenter",
    "barydualmesh",
    "highordertet",
    "ismember_rows",
    "ray2surf",
]

##====================================================================================
## dependent libraries
##====================================================================================

import numpy as np
from itertools import combinations

##====================================================================================
## implementations
##====================================================================================


def finddisconnsurf(f):
    """
    Extract disconnected surfaces from a cluster of surfaces.

    Parameters:
    f : numpy.ndarray
        Faces defined by node indices for all surface triangles.

    Returns:
    facecell : list
        Separated disconnected surface node indices.
    """

    facecell = []  # Initialize output list
    subset = np.array([])  # Initialize an empty subset array

    # Loop until all faces are processed
    while f.size > 0:
        # Find the indices of faces connected to the first face
        idx = np.isin(f, f[0, :]).reshape(f.shape)
        ii = np.where(np.sum(idx, axis=1))[0]

        # Continue until all connected faces are processed
        while ii.size > 0:
            # Append connected faces to the subset
            subset = np.vstack((subset, f[ii, :])) if subset.size else f[ii, :]
            f = np.delete(f, ii, axis=0)  # Remove processed faces
            idx = np.isin(f, subset).reshape(f.shape)  # Update connection indices
            ii = np.where(np.sum(idx, axis=1))[0]  # Find next set of connected faces

        # If the subset is non-empty, append it to the output
        if subset.size > 0:
            facecell.append(subset)
            subset = np.array([])  # Reset subset

    return facecell


# _________________________________________________________________________________________________________


def surfedge(f, junction=None):
    """
    Find the edge of an open surface or surface of a volume.

    Parameters:
    f : numpy.ndarray
        Input surface facif f.size == 0:
        return np.array([]), None
    junction : int, optional
        If set to 1, allows finding junctions (edges with more than two connected triangles).

    Returns:
    openedge : numpy.ndarray
        List of edges of the specified surface.
    elemid : numpy.ndarray, optional
        Corresponding index of the tetrahedron or triangle with an open edge.
    """

    if f.size == 0:
        return np.array([]), None

    findjunc = 0

    if f.shape[1] == 3:
        edges = np.vstack(
            (f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]])
        )  # create all the edges
    elif f.shape[1] == 4:
        edges = np.vstack(
            (f[:, [0, 1, 2]], f[:, [1, 0, 3]], f[:, [0, 2, 3]], f[:, [1, 3, 2]])
        )  # create all the edges
    else:
        raise ValueError("surfedge only supports 2D and 3D elements")

    edgesort = np.sort(edges, axis=1)
    _, ix, jx = np.unique(edgesort, axis=0, return_index=True, return_inverse=True)

    vec = np.bincount(jx, minlength=max(jx) + 1)
    if f.shape[1] == 3 and junction is not None:
        qx = np.where(vec > 2)[0]
    else:
        qx = np.where(vec == 1)[0]

    openedge = edges[ix[qx], :]

    elemid, _ = np.unravel_index(ix[qx], f.shape, order="F")

    return openedge, elemid + 1


# _________________________________________________________________________________________________________


def volface(t):
    """
    Find the surface patches of a volume.

    Parameters:
    t : numpy.ndarray
        Input volumetric element list (tetrahedrons), dimension (ne, 4).

    Returns:
    openface : numpy.ndarray
        List of faces of the specified volume.
    elemid : numpy.ndarray, optional
        The corresponding index of the tetrahedron with an open edge or triangle.
    """

    # Use surfedge function to find the boundary faces of the volume
    openface, elemid = surfedge(t)

    return openface, elemid


# _________________________________________________________________________________________________________


def extractloops(edges):
    """
    Extract individual loops or polyline segments from a collection of edges.

    Parameters:
    edges : numpy.ndarray
        A two-column matrix recording the starting/ending points of all edge segments.

    Returns:
    loops : list
        Output list of polyline or loop segments, with NaN separating each loop/segment.
    """

    loops = []

    # Remove degenerate edges (edges where the start and end points are the same)
    edges = edges[edges[:, 0] != edges[:, 1], :]

    if len(edges) == 0:
        return loops

    # Initialize the loop with the first edge
    loops.extend(edges[0, :])
    loophead = edges[0, 0]
    loopend = edges[0, 1]
    edges = np.delete(edges, 0, axis=0)

    while edges.size > 0:
        # Find the index of the edge connected to the current loop end
        idx = np.concatenate(
            [np.where(edges[:, 0] == loopend)[0], np.where(edges[:, 1] == loopend)[0]]
        )

        if len(idx) > 1:
            # If multiple connections found, select the first
            idx = idx[0]

        if not isinstance(idx, np.ndarray):
            idx = np.array(idx)

        if idx.size == 0:
            # If no connection found (open-line segment)
            idx_head = np.concatenate(
                [
                    np.where(edges[:, 0] == loophead)[0],
                    np.where(edges[:, 1] == loophead)[0],
                ]
            )
            if len(idx_head) == 0:
                # If both open ends are found, start a new loop
                loops.append(np.nan)
                loops.extend(edges[0, :])
                loophead = edges[0, 0]
                loopend = edges[0, 1]
                edges = np.delete(edges, 0, axis=0)
            else:
                # Flip and trace the other end of the loop
                loophead, loopend = loopend, loophead
                lp = np.flip(loops)
                seg = np.where(np.isnan(lp))[0]
                if len(seg) == 0:
                    loops = lp.tolist()
                else:
                    loops = (loops[: len(loops) - seg[0]] + lp[: seg[0]]).tolist()
            continue

        # Trace along a single line thread
        if idx.size == 1:
            ed = edges[idx, :].flatten()
            ed = ed[ed != loopend]
            newend = ed[0]
            if newend == loophead:
                # If a loop is completed
                loops.extend([loophead, np.nan])
                edges = np.delete(edges, idx, axis=0)
                if edges.size == 0:
                    break
                loops.extend(edges[0, :])
                loophead = edges[0, 0]
                loopend = edges[0, 1]
                edges = np.delete(edges, 0, axis=0)
                continue
            else:
                loops.append(newend)

            loopend = newend
            edges = np.delete(edges, idx, axis=0)

    return np.array(loops)


# _________________________________________________________________________________________________________


def meshconn(elem, nn):
    """
    Create a node neighbor list from a mesh.

    Parameters:
    elem : numpy.ndarray
        Element table of the mesh, where each row represents an element and its node indices.
    nn : int
        Total number of nodes in the mesh.

    Returns:
    conn : list
        A list of length `nn`, where each element is a list of all neighboring node IDs for each node.
    connnum : numpy.ndarray
        A vector of length `nn`, indicating the number of neighbors for each node.
    count : int
        Total number of neighbors across all nodes.
    """

    # Initialize conn as a list of empty lists
    conn = [[] for _ in range(nn)]
    dim = elem.shape
    # Loop through each element and populate the conn list
    for i in range(dim[0]):
        for j in range(dim[1]):
            conn[elem[i, j] - 1].extend(
                elem[i, :]
            )  # Adjust for 0-based indexing in Python

    count = 0
    connnum = np.zeros(nn, dtype=int)

    # Loop through each node to remove duplicates and self-references
    for i in range(nn):
        if len(conn[i]) == 0:
            continue
        # Remove duplicates and self-references
        neig = np.unique(conn[i])
        neig = neig[neig != i + 1]  # Remove self-reference, adjust for 0-based indexing
        conn[i] = neig.tolist()
        connnum[i] = len(conn[i])
        count += connnum[i]

    return conn, connnum, count


# _________________________________________________________________________________________________________


def nodevolume(node, elem, evol=None):
    """
    Calculate the volumes of the cells in the barycentric dual-mesh.
    This is different from Voronoi cells, which belong to the circumcentric dual mesh.

    Parameters:
    node : numpy.ndarray
        Node coordinates.
    elem : numpy.ndarray
        Element table of a mesh.
    evol : numpy.ndarray, optional
        Element volumes for each element (if not provided, it will be computed).

    Returns:
    nodevol : numpy.ndarray
        Volume values for all nodes.
    """

    # Determine if the mesh is 3D or 4D based on the number of nodes per element
    dim = 4 if elem.shape[1] == 4 else 3

    # If element volumes (evol) are not provided, calculate them
    if evol is None:
        evol = elemvolume(node, elem[:, :dim])

    elemnum = elem.shape[0]
    nodenum = node.shape[0]

    # Initialize node volume array
    nodevol = np.zeros(nodenum)

    # Loop through each element and accumulate the volumes
    for i in range(elemnum):
        nodevol[elem[i, :dim] - 1] += evol[i]

    # Divide by the dimensionality to get the final node volumes
    nodevol /= dim

    return nodevol


# _________________________________________________________________________________________________________


def elemvolume(node, elem, option=None):
    """
    vol = elemvolume(node, elem, option)

    Calculate the volume for a list of simplexes

    Parameters:
        node:   node coordinates (NumPy array)
        elem:   element table of a mesh (1-based indices)
        option: if option == 'signed', the volume is the raw determinant,
                otherwise, the result will be the absolute values

    Returns:
        vol: volume values for all elements
    """

    # Convert 1-based indices to 0-based for Python indexing
    v1 = node[elem[:, 0] - 1, :3]
    v2 = node[elem[:, 1] - 1, :3]
    v3 = node[elem[:, 2] - 1, :3]

    edge1 = v2 - v1
    edge2 = v3 - v1

    if elem.shape[1] == 3:
        # Triangle area in 2D or area in 3D projected onto a plane
        det12 = np.cross(edge1, edge2)
        det12 = np.sum(det12 * det12, axis=1)
        vol = 0.5 * np.sqrt(det12)
        return vol

    v4 = node[elem[:, 3] - 1, :3]
    edge3 = v4 - v1

    # Compute signed volume of tetrahedron
    vol = -np.einsum("ij,ij->i", edge1, np.cross(edge2, edge3, axis=1))

    if option == "signed":
        vol = vol / np.prod(np.arange(1, node.shape[1] + 1))
    else:
        vol = np.abs(vol) / np.prod(np.arange(1, node.shape[1] + 1))

    return vol


# _________________________________________________________________________________________________________


def neighborelem(elem, nn):
    """
    create node neighbor list from a mesh

    input:
       elem:  element table of a mesh
       nn  :  total node number of the mesh

    output:
       conn:  output, a list of length nn, conn[n]
              contains a list of all neighboring elem ID for node n
       connnum: list of length nn, denotes the neighbor number of each node
       count: total neighbor numbers
    """
    # Initialize conn as a list of empty lists
    conn = [[] for _ in range(nn)]
    dim = elem.shape

    elem = elem - 1
    # Loop through each element and populate the conn list
    for i in range(dim[0]):
        for j in range(dim[1]):
            conn[elem[i, j]].append(i + 1)  # Adjusting for 0-based index in Python

    # Loop through each node to sort neighbors and calculate total counts
    count = 0
    connnum = [0] * nn
    for i in range(nn):
        conn[i] = sorted(conn[i])
        connnum[i] = len(conn[i])
        count += connnum[i]

    return conn, connnum, count


# _________________________________________________________________________________________________________


def layersurf(elem, **kwargs):
    """
    face, labels = layersurf(elem, opt)
    or
    face, labels = layersurf(elem, option1=value1, option2=value2, ...)

    Process a multi-layered tetrahedral mesh to extract the layer surface meshes.

    Arguments:
    elem : an Nx5 integer array representing the tetrahedral mesh element list.
           The first 4 columns represent the tetrahedral element node indices,
           and the last column represents tissue labels.

    Optional kwargs:
    order : str, default '>=', options ['>=', '=', '<=']
        Determines how to process layers:
        '>=' (default): outmost layer has the lowest label count;
        '<=': innermost is lowest;
        '=': surface of each label is extracted individually.
    innermost : array-like, default [0]
        Labels treated as innermost regions, its boundary extracted using '=='.
        By default, label 0 is assumed to be the innermost (i.e., nothing enclosed inside).
    unique : bool, default False
        If True, removes duplicated triangles. If False, keeps all triangles.
    occurrence : str, default 'first', options ['first', 'last']
        If 'first', unique operator keeps the duplicated triangle with the lowest label number;
        otherwise, keeps the triangle with the highest label number.

    Returns:
    face : Nx4 array
        Extracted surface faces.
    labels : list
        Unique sorted labels in the mesh.
    """
    # Process input options
    opt = kwargs
    outsideislower = opt.get("order", ">=")
    dounique = opt.get("unique", False)
    innermost = opt.get("innermost", [0])
    occurrence = opt.get("occurrence", "first")

    labels = np.sort(np.unique(elem[:, 4]))
    face = []

    # Process each label
    for i in range(len(labels)):
        if outsideislower == ">=" and labels[i] not in innermost:
            newface = volface(elem[elem[:, 4] >= labels[i], :4])[0]
        elif outsideislower == "<=" and labels[i] not in innermost:
            newface = volface(elem[elem[:, 4] <= labels[i], :4])[0]
        else:
            newface = volface(elem[elem[:, 4] == labels[i], :4])[0]

        # Add label to faces
        newface = np.hstack((newface, np.full((newface.shape[0], 1), labels[i])))
        face.append(newface)

    face = np.vstack(face)

    # Remove duplicate triangles if unique option is enabled
    if dounique:
        face[:, :3] = np.sort(face[:, :3], axis=1)
        uniqface, idx = np.unique(face[:, :3], axis=0, return_index=True)
        face = np.hstack((uniqface, face[idx, -1].reshape(-1, 1)))

    return face, labels


# _________________________________________________________________________________________________________


def faceneighbors(t, opt=None):
    """
    facenb = faceneighbors(t, opt)

    Find the 4 face-neighboring elements of a tetrahedron.

    Arguments:
    t   : tetrahedron element list, 4 columns of integers.
    opt : if 'surface', return the boundary triangle list
          (same as face output from v2m).
          if 'rowmajor', return boundary triangles in row-major order.

    Output:
    facenb : If opt is 'surface', returns the list of boundary triangles.
             Otherwise, returns element neighbors for each element. Each
             row contains 4 numbers representing the element indices
             sharing triangular faces [1 2 3], [1 2 4], [1 3 4], and
             [2 3 4]. A 0 indicates no neighbor (i.e., boundary face).
    """
    # Generate faces from tetrahedral elements
    faces = np.vstack(
        (t[:, [0, 1, 2]], t[:, [0, 1, 3]], t[:, [0, 2, 3]], t[:, [1, 2, 3]])
    )
    faces = np.sort(faces, axis=1)

    # Find unique faces and their indices
    _, ix, jx = np.unique(faces, axis=0, return_index=True, return_inverse=True)

    vec = np.histogram(jx, bins=np.arange(max(jx) + 2))[0]
    qx = np.where(vec == 2)[0]

    nn = np.max(t)
    ne = t.shape[0]
    facenb = np.zeros_like(t)

    # Identify duplicate faces and their element pairings
    ujx, ii = np.unique(jx, return_index=True)
    jx2 = jx[::-1]
    _, ii2 = np.unique(jx2, return_index=True)
    ii2 = len(jx2) - 1 - ii2

    # List of element pairs that share a common face
    iddup = np.vstack((ii[qx], ii2[qx])).T
    faceid = np.ceil((iddup + 1) / ne).astype(int)
    eid = np.mod(iddup + 1, ne)
    eid[eid == 0] = ne

    # Handle special cases based on the second argument
    if opt is not None:
        for i in range(len(qx)):
            facenb[eid[i, 0] - 1, faceid[i, 0] - 1] = eid[i, 1]
            facenb[eid[i, 1] - 1, faceid[i, 1] - 1] = eid[i, 0]
        if opt == "surface":
            facenb = faces[np.where(facenb.T.flatten() == 0)[0], :]
        elif opt == "rowmajor":
            index = np.arange(len(faces)).reshape(4, -1).T.flatten()
            faces = faces[index, :]
            facenb = faces[np.where(facenb.flatten() == 0)[0], :]
        else:
            raise ValueError(f'Unsupported option "{opt}".')
    else:
        for i in range(len(qx)):
            facenb[eid[i, 0] - 1, faceid[i, 0] - 1] = eid[i, 1]
            facenb[eid[i, 1] - 1, faceid[i, 1] - 1] = eid[i, 0]

    return facenb


# _________________________________________________________________________________________________________


def edgeneighbors(t, opt=None):
    """
    edgenb = edgeneighbors(t, opt)

    Find neighboring triangular elements in a triangular surface.

    Arguments:
    t   : a triangular surface element list, 3 columns of integers.
    opt : (optional) If 'general', return edge neighbors for a general triangular surface.
          Each edge can be shared by more than 2 triangles. If ignored, assumes all
          triangles are shared by no more than 2 triangles.

    Output:
    edgenb : If opt is not supplied, edgenb is a size(t, 1) by 3 array, with each element
             being the triangle ID of the edge neighbor of that triangle. For each row,
             the neighbors are listed in the order of those sharing edges [1, 2], [2, 3],
             and [3, 1] between the triangle nodes.
             If opt = 'general', edgenb is a list of arrays, where each entry lists the edge neighbors.
    """
    # Generate the edges from the triangle elements
    edges = np.vstack([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    edges = np.sort(edges, axis=1)

    # Find unique edges and their indices
    _, ix, jx = np.unique(edges, axis=0, return_index=True, return_inverse=True)

    ne = t.shape[0]  # Number of triangles
    if opt == "general":
        edgenb = [
            np.unique(
                np.mod(
                    np.where(
                        (jx == jx[i]) | (jx == jx[i + ne]) | (jx == jx[i + 2 * ne])
                    )[0],
                    ne,
                )
            )
            for i in range(ne)
        ]
        return [np.setdiff1d(nb, [i]) for i, nb in enumerate(edgenb)]

    # Determine boundary neighbors
    vec = np.bincount(jx)
    qx = np.where(vec == 2)[
        0
    ]  # Get indices where edges are shared by exactly 2 triangles

    edgenb = np.zeros_like(t)

    ujx, first_idx = np.unique(jx, return_index=True)
    _, last_idx = np.unique(jx[::-1], return_index=True)
    last_idx = len(jx) - last_idx - 1

    # Find the element pairs that share an edge
    iddup = np.vstack([first_idx[qx], last_idx[qx]]).T
    faceid = (iddup // ne) + 1
    eid = iddup % ne
    eid += 1
    eid[eid == 0] = ne

    # Assign neighboring elements
    for i in range(len(qx)):
        edgenb[eid[i, 0] - 1, faceid[i, 0] - 1] = eid[i, 1]
        edgenb[eid[i, 1] - 1, faceid[i, 1] - 1] = eid[i, 0]

    # Handle boundary edges (where no neighbor exists)
    return edgenb


# _________________________________________________________________________________________________________


def maxsurf(facecell, node=None):
    """
    f, maxsize = maxsurf(facecell, node)

    Return the surface with the maximum number of elements or total area from a cell array of surfaces.

    Arguments:
    facecell : a list of arrays, each element representing a face array.
    node     : optional, node list. If given, the output is the surface with the largest surface area.

    Output:
    f        : the surface data (node indices) for the surface with the most elements (or largest area if node is given).
    maxsize  : if node is not provided, maxsize is the row number of f.
               If node is given, maxsize is the total area of f.
    """
    maxsize = -1
    maxid = -1

    # If node is provided, calculate area for each surface
    if node is not None:
        areas = np.zeros(len(facecell))
        for i in range(len(facecell)):
            areas[i] = np.sum(elemvolume(node[:, :3], facecell[i]))
        maxsize = np.max(areas)
        maxid = np.argmax(areas)
        f = facecell[maxid]
        return f, maxsize
    else:
        # Find the surface with the most elements
        for i in range(len(facecell)):
            if len(facecell[i]) > maxsize:
                maxsize = len(facecell[i])
                maxid = i

        f = []
        if maxid >= 0:
            f = facecell[maxid]

        return f, maxsize


def flatsegment(node, edge):
    """
    mask = flatsegment(node, edge)

    Decompose edge loops into flat segments along arbitrary planes of the bounding box.

    Arguments:
    node : Nx3 array of x, y, z coordinates for each node of the mesh.
    edge : vector separated by NaN, each segment is a closed polygon consisting of node IDs.

    Output:
    mask : list, each element is a closed polygon on the x/y/z plane.

    Author: Qianqian Fang
    Date: 2008/04/08

    Notes:
    This function is fragile: it cannot handle curves with many collinear nodes near corner points.
    """

    idx = edge
    nn = len(idx)
    val = np.zeros(nn)

    # Check for nearly flat tetrahedrons
    for i in range(nn):
        tet = np.mod(np.arange(i, i + 4), nn)
        tet[tet == 0] = nn
        # Calculate determinant to determine flatness
        val[i] = (
            abs(np.linalg.det(np.hstack((node[idx[tet], :], np.ones((4, 1)))))) > 1e-5
        )

    val = np.concatenate((val, val[:2]))
    mask = []
    oldend = 0
    count = 0

    # Decompose into flat segments
    for i in range(nn):
        if val[i] == 1 and val[i + 1] == 1 and val[i + 2] == 0:
            val[i + 2] = 2
            mask.append(idx[oldend : i + 3])
            count += 1
            oldend = i + 2
        else:
            mask.append(np.concatenate((idx[oldend:], mask[0])))
            break

    return mask


def mesheuler(face):
    """
    X, V, E, F, b, g, C = mesheuler(face)

    Compute Euler's characteristic of a mesh.

    Arguments:
    face : a closed surface mesh (Mx3 array where M is the number of faces and each row contains vertex indices)

    Output:
    X : Euler's characteristic (X = V - E + F - C)
    V : number of vertices
    E : number of edges
    F : number of triangles (if face is tetrahedral mesh, exterior surface)
    b : number of boundary loops (for surfaces)
    g : genus (holes)
    C : number of tetrahedra

    Author: Qianqian Fang
    This function is part of the iso2mesh toolbox (http://iso2mesh.sf.net)
    """

    # Number of vertices
    V = len(np.unique(face))

    # Number of unique edges
    E = uniqedges(face)[0].shape[0]

    b = 0  # open-boundary loops
    g = 0  # genus
    C = 0  # tet cells

    # Number of unique faces
    if face.shape[1] == 4:
        F = uniqfaces(face)[0].shape[0]
        C = face.shape[0]
    else:
        ed = surfedge(face)[0]
        loops = extractloops(ed)
        b = np.sum(np.isnan(loops))
        F = face.shape[0]

    # Euler's formula, X = V - E + F - C - 2*g
    X = V - E + F - C

    if face.shape[1] == 3:
        g = (X + b - 2) // 2

    return X, V, E, F, b, g, C


def orderloopedge(edge):
    """
    newedge = orderloopedge(edge)

    Order the node list of a simple loop based on the connection sequence.

    Arguments:
    edge : an Nx2 array where each row is an edge defined by two integers (start/end node index).

    Output:
    newedge : Nx2 array of reordered edge node list.

    Author: Qianqian Fang
    Date: 2008/05

    Notes:
    This function cannot process bifurcations.
    """

    ne = edge.shape[0]
    newedge = np.zeros_like(edge)
    newedge[0, :] = edge[0, :]

    for i in range(1, ne):
        row, col = np.where(edge[i:, :] == newedge[i - 1, 1])
        if len(row) == 1:
            newedge[i, :] = [newedge[i - 1, 1], edge[row[0] + i, 1 - col[0]]]
            edge[[i, row[0] + i], :] = edge[[row[0] + i, i], :]
        elif len(row) >= 2:
            raise ValueError("Bifurcation is found, exiting.")
        elif len(row) == 0:
            raise ValueError(f"Open curve at node {newedge[i - 1, 1]}")

    return newedge


def bbxflatsegment(node, edge):
    """
    mask = bbxflatsegment(node, edge)

    Decompose edge loops into flat segments along arbitrary planes of the bounding box.

    Arguments:
    node : Nx3 array of x, y, z coordinates for each node of the mesh.
    edge : vector separated by NaN, each segment is a closed polygon consisting of node IDs.

    Output:
    mask : list, each element is a closed polygon on the x/y/z plane.

    Author: Qianqian Fang
    Date: 2008/04/08

    Notes:
    This function is fragile: it cannot handle curves with many collinear nodes near corner points.
    """

    idx = edge
    nn = len(idx)
    val = np.zeros(nn)

    # Check for nearly flat tetrahedrons
    for i in range(nn):
        tet = np.mod(np.arange(i, i + 4), nn)
        tet[tet == 0] = nn
        # Calculate determinant to determine flatness
        val[i] = (
            abs(np.linalg.det(np.hstack((node[idx[tet], :], np.ones((4, 1)))))) > 1e-5
        )

    val = np.concatenate((val, val[:2]))
    mask = []
    oldend = 0
    count = 0

    # Decompose into flat segments
    for i in range(nn):
        if val[i] == 1 and val[i + 1] == 1 and val[i + 2] == 0:
            val[i + 2] = 2
            mask.append(idx[oldend : i + 3])
            count += 1
            oldend = i + 2
        else:
            mask.append(np.concatenate((idx[oldend:], mask[0])))
            break

    return mask


# _________________________________________________________________________________________________________


def surfplane(node, face):
    """
    plane = surfplane(node, face)

    Calculate plane equation coefficients for each face in a surface.

    Parameters:
    node : numpy array
        A list of node coordinates (nn x 3)
    face : numpy array
        A surface mesh triangle list (ne x 3)

    Returns:
    plane : numpy array
        A (ne x 4) array where each row has [a, b, c, d] to represent
        the plane equation as "a*x + b*y + c*z + d = 0"
    """

    # Compute vectors AB and AC from the triangle vertices
    AB = node[face[:, 1] - 1, :3] - node[face[:, 0] - 1, :3]
    AC = node[face[:, 2] - 1, :3] - node[face[:, 0] - 1, :3]

    # Compute normal vectors to the triangles using cross product
    N = np.cross(AB, AC)

    # Compute the plane's d coefficient by taking the dot product of normal vectors with vertex positions
    d = -np.sum(N * node[face[:, 0] - 1, :3], axis=1)

    # Return the plane coefficients [a, b, c, d]
    plane = np.column_stack((N, d))

    return plane


# _________________________________________________________________________________________________________


def raytrace(p0, v0, node, face):
    """
    t, u, v, idx = raytrace(p0, v0, node, face)

    Perform Havel-style ray tracing for a triangular surface.

    Parameters:
        p0: (3,) array, starting point of the ray
        v0: (3,) array, direction vector of the ray
        node: (nn, 3) array of node coordinates
        face: (ne, 3) array of triangle indices (1-based)

    Returns:
        t: signed distance to intersection (Inf if ray is parallel)
        u: barycentric coordinate 1
        v: barycentric coordinate 2
        idx: indices of intersected triangles (optional)
    """

    # Reshape p0 and v0 to row vectors
    p0 = np.asarray(p0).reshape(1, 3)
    v0 = np.asarray(v0).reshape(1, 3)

    # Convert 1-based indices in face to 0-based
    A = node[face[:, 0] - 1, :]
    B = node[face[:, 1] - 1, :]
    C = node[face[:, 2] - 1, :]

    AB = B - A
    AC = C - A

    # Normal vectors of triangles
    N = np.cross(AB, AC)
    d = -np.einsum("ij,ij->i", N, A)

    Rn2 = 1.0 / np.einsum("ij,ij->i", N, N)

    N1 = np.cross(AC, N) * Rn2[:, np.newaxis]
    d1 = -np.einsum("ij,ij->i", N1, A)

    N2 = np.cross(N, AB) * Rn2[:, np.newaxis]
    d2 = -np.einsum("ij,ij->i", N2, A)

    den = np.dot(N, v0.T).flatten()
    t = -(d + np.dot(N, p0.T).flatten())
    P = (np.outer(p0, den) + np.outer(v0, t)).T

    u = np.einsum("ij,ij->i", P, N1) + den * d1
    v = np.einsum("ij,ij->i", P, N2) + den * d2

    idx = den != 0
    den_inv = np.zeros_like(den)
    den_inv[idx] = 1.0 / den[idx]

    t = t * den_inv
    u = u * den_inv
    v = v * den_inv

    # For parallel rays, set t to Inf
    t[~idx] = np.inf

    # Compute intersection index if requested
    idx_out = None
    if u.shape[0] > 0 and v.shape[0] > 0 and t.shape[0] > 0:
        idx_out = np.where((u >= 0) & (v >= 0) & (u + v <= 1.0) & (~np.isinf(t)))[0]

    return t, u, v, idx_out


# _________________________________________________________________________________________________________


def surfinterior(node, face):
    """
    pt, p0, v0, t, idx = surfinterior(node, face)

    Identify a point that is enclosed by the (closed) surface.

    Arguments:
    node : a list of node coordinates (nn x 3)
    face : a surface mesh triangle list (ne x 3)

    Output:
    pt  : the interior point coordinates [x, y, z]
    p0  : ray origin used to determine the interior point
    v0  : the vector used to determine the interior point
    t   : ray-tracing intersection distances (with signs) from p0. The intersection coordinates
          can be expressed as p0 + t[i] * v0
    idx : index to the face elements that intersect with the ray, order matches that of t

    Author: Qianqian Fang
    This function is part of the iso2mesh toolbox (http://iso2mesh.sf.net)
    """

    pt, p0, v0, t, idx = [], [], [], None, []

    len_faces = face.shape[0]

    for i in range(len_faces):
        p0 = np.mean(
            node[face[i, :3] - 1, :], axis=0
        )  # Calculate the centroid of the triangle
        plane = surfplane(
            node, face[i, :].reshape(1, -1)
        )  # Plane equation for the current triangle
        v0 = plane[0][:3]  # Use the plane normal vector as the direction of the ray
        t, u, v, _ = raytrace(p0, v0, node, face[:, :3])  # Perform ray-tracing

        idx = np.where((u >= 0) & (v >= 0) & (u + v <= 1.0) & (~np.isinf(t)))[
            0
        ]  # Filter valid intersections

        # Sort and ensure ray intersections are valid
        ts, uidx = np.unique(np.sort(t[idx]), return_index=True)

        if len(ts) > 0 and len(ts) % 2 == 0:
            ts = ts.reshape((2, len(ts) // 2))
            tdiff = ts[1, :] - ts[0, :]
            maxi = np.argmax(tdiff)
            pt = (
                p0 + v0 * (ts[0, maxi] + ts[1, maxi]) * 0.5
            )  # Calculate the midpoint of the longest segment
            idx = idx[uidx]
            t = t[idx]
            break

    return pt, p0, v0, t, idx


def surfpart(f, loopedge):
    """
    elist = surfpart(f, loopedge)

    Partition a triangular surface using a closed loop defined by existing edges.

    Parameters:
    f : numpy array
        Surface face element list, dimension (n, 3) or (n, 4)
    loopedge : numpy array
        A 2-column array specifying a closed loop in counter-clockwise order.

    Returns:
    elist : numpy array
        List of triangles that is enclosed by the loop.
    """
    elist = []

    # Check if input is empty
    if f.size == 0 or loopedge.size == 0:
        return np.array(elist)

    # Handle triangular or quadrilateral elements
    if f.shape[1] == 3:
        # Create edges from triangles
        edges = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    elif f.shape[1] == 4:
        # Create edges from quadrilaterals
        edges = np.vstack([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 3]], f[:, [3, 0]]])
    else:
        raise ValueError("surfpart only supports triangular and quadrilateral elements")

    # Advance the front using the edges and loop
    elist, front = advancefront(edges, loopedge)

    # Continue advancing the front until no more elements can be added
    while front.size > 0:
        elist0, front0 = advancefront(edges, front)
        elist = np.unique(np.vstack([elist, elist0]), axis=0)
        front = front0

    return elist


def surfseeds(node, face):
    """
    seeds = surfseeds(node, face)

    Calculate a set of interior points, with each enclosed by a closed
    component of a surface.

    Parameters:
    node : numpy array
        A list of node coordinates (nn x 3).
    face : numpy array
        A surface mesh triangle list (ne x 3).

    Returns:
    seeds : numpy array
        Interior point coordinates for each closed surface component.
    """

    # Find disconnected surface components
    fc = finddisconnsurf(face[:, 0:3])
    len_fc = len(fc)

    # Initialize seed points array
    seeds = np.zeros((len_fc, 3))

    # For each disconnected component, calculate the interior point
    for i in range(len_fc):
        seeds[i, :] = surfinterior(node, fc[i])[0]

    return seeds


def meshquality(node, elem, maxnode=4):
    """
    quality = meshquality(node, elem, maxnode=4)

    Compute the Joe-Liu mesh quality measure of an N-D mesh (N <= 3).

    Parameters:
    node : numpy array
        Node coordinates of the mesh (nn x 3).
    elem : numpy array
        Element table of an N-D mesh (ne x (N+1)).
    maxnode : int, optional
        Maximum number of nodes per element (default is 4 for tetrahedral).

    Returns:
    quality : numpy array
        A vector of the same length as size(elem,1), with each element being
        the Joe-Liu mesh quality metric (0-1) of the corresponding element.
        A value close to 1 represents higher mesh quality (1 means equilateral tetrahedron);
        a value close to 0 means a nearly degenerated element.

    Reference:
    A. Liu, B. Joe, Relationship between tetrahedron shape measures,
    BIT 34 (2) (1994) 268-287.
    """

    if elem.shape[1] > maxnode:
        elem = elem[:, :maxnode]

    enum = elem.shape[0]

    # Compute element volume
    vol = elemvolume(node, elem)

    # Compute edge lengths
    edges = meshedge(elem)
    ed = node[edges[:, 0] - 1, :] - node[edges[:, 1] - 1, :]
    ed = np.sum(ed**2, axis=1)
    ed = np.sum(ed.reshape((enum, ed.size // enum), order="F"), axis=1)

    dim = elem.shape[1] - 1
    coeff = 10 / 9  # for tetrahedral elements

    if dim == 2:
        coeff = 1

    # Compute quality metric
    quality = (
        coeff
        * dim
        * 2 ** (2 * (1 - 1 / dim))
        * 3 ** ((dim - 1) / 2)
        * vol ** (2 / dim)
        / ed
    )

    # Normalize quality if max quality > 1
    maxquality = np.max(quality)
    if maxquality > 1:
        quality = quality / maxquality

    return quality


# _________________________________________________________________________________________________________


def meshedge(elem, opt=None):
    """
    edges = meshedge(elem, opt=None)

    Return all edges in a surface or volumetric mesh.

    Parameters:
    elem : numpy array
        Element table of a mesh (supports N-dimensional space elements).
    opt : dict, optional
        Optional input. If opt is provided as a dictionary, it can have the following field:
        - opt['nodeorder']: If 1, assumes the elem node indices are in CCW orientation;
                            if 0, uses combinations to order edges.

    Returns:
    edges : numpy array
        Edge list; each row represents an edge, specified by the starting and
        ending node indices. The total number of edges is size(elem,1) x comb(size(elem,2),2).
        All edges are ordered by looping through each element.
    """
    # Determine element dimension and the combination of node pairs for edges
    dim = elem.shape
    edgeid = np.array(list(combinations(range(dim[1]), 2)))
    len_edges = edgeid.shape[0]

    # Initialize edge list
    edges = np.zeros((dim[0] * len_edges, 2), dtype=elem.dtype)

    # Populate edges by looping through each element
    for i in range(len_edges):
        edges[i * dim[0] : (i + 1) * dim[0], :] = np.column_stack(
            (elem[:, edgeid[i, 0]], elem[:, edgeid[i, 1]])
        )

    return edges


# _________________________________________________________________________________________________________


def meshface(elem, opt=None):
    """
    faces = meshface(elem, opt=None)

    Return all faces in a surface or volumetric mesh.

    Parameters:
    elem : numpy array
        Element table of a mesh (supports N-dimensional space elements).
    opt : dict, optional
        Optional input. If provided, `opt` can contain the following field:
        - opt['nodeorder']: If 1, assumes the elem node indices are in CCW orientation;
                            otherwise, uses combinations to order faces.

    Returns:
    faces : numpy array
        Face list; each row represents a face, specified by node indices.
        The total number of faces is size(elem,1) x comb(size(elem,2),3).
        All faces are ordered by looping through each element.
    """
    dim = elem.shape
    faceid = np.array(list(combinations(range(dim[1]), 3)))
    len_faces = faceid.shape[0]

    # Initialize face list
    faces = np.zeros((dim[0] * len_faces, 3), dtype=elem.dtype)

    # Populate faces by looping through each element
    for i in range(len_faces):
        faces[i * dim[0] : (i + 1) * dim[0], :] = np.array(
            [elem[:, faceid[i, 0]], elem[:, faceid[i, 1]], elem[:, faceid[i, 2]]]
        ).T

    return faces


# _________________________________________________________________________________________________________


def surfacenorm(node, face, normalize=True):
    """
    snorm = surfacenorm(node, face, normalize=True)

    Compute the normal vectors for a triangular surface.

    Parameters:
    node : numpy array
        A list of node coordinates (nn x 3).
    face : numpy array
        A surface mesh triangle list (ne x 3).
    normalize : bool, optional
        If set to True, the normal vectors will be unitary (default is True).

    Returns:
    snorm : numpy array
        Output surface normal vector at each face.
    """

    # Compute the normal vectors using surfplane (function must be defined)
    snorm = surfplane(node, face)
    snorm = snorm[:, :3]

    # Normalize the normal vectors if requested
    if normalize:
        snorm = snorm / np.sqrt(np.sum(snorm**2, axis=1, keepdims=True))

    return snorm


# _________________________________________________________________________________________________________


def nodesurfnorm(node, elem):
    """
    nv = nodesurfnorm(node, elem)

    Calculate a nodal normal for each vertex on a surface mesh (the surface
    can only be triangular or cubic).

    Parameters:
    node : numpy array
        Node coordinates of the surface mesh (nn x 3).
    elem : numpy array
        Element list of the surface mesh (3 columns for triangular mesh,
        4 columns for cubic surface mesh).

    Returns:
    nv : numpy array
        Nodal normals calculated for each node (nn x 3).
    """

    nn = node.shape[0]  # Number of nodes
    ne = elem.shape[0]  # Number of elements
    nedim = elem.shape[1]  # Element dimension

    # Compute element normals
    ev = surfacenorm(node, elem)

    # Initialize nodal normals
    nv = np.zeros((nn, 3))

    # Sum element normals for each node
    for i in range(ne):
        nv[elem[i, :] - 1, :] += ev[i, :]

    # Normalize nodal normals
    nvnorm = np.linalg.norm(nv, axis=1)
    idx = np.where(nvnorm > 0)[0]

    if len(idx) < nn:
        print("Warning: Found interior nodes, their norms will be set to zeros.")
        nv[idx, :] = nv[idx, :] / nvnorm[idx][:, np.newaxis]
    else:
        nv = nv / nvnorm[:, np.newaxis]

    return nv


# _________________________________________________________________________________________________________


def uniqedges(elem):
    """
    edges, idx, edgemap = uniqedges(elem)

    Return the unique edge list from a surface or tetrahedral mesh.

    Parameters:
    elem : numpy array
        A list of elements, where each row is a list of nodes for an element.
        The input `elem` can have 2, 3, or 4 columns.

    Returns:
    edges : numpy array
        Unique edges in the mesh, denoted by pairs of node indices.
    idx : numpy array
        Indices of the unique edges in the raw edge list (returned by meshedge).
    edgemap : numpy array
        Index of the raw edges in the output list (for triangular meshes).
    """

    # Handle cases based on element size
    if elem.shape[1] == 2:
        edges = elem
    elif elem.shape[1] >= 3:
        edges = meshedge(elem)
    else:
        raise ValueError("Invalid input: element size not supported.")

    # Find unique edges and indices
    uedges, idx, jdx = np.unique(
        np.sort(edges, axis=1), axis=0, return_index=True, return_inverse=True
    )
    edges = edges[idx, :]

    # Compute edgemap if requested
    edgemap = np.reshape(
        jdx + 1,
        (-1, elem.shape[0]),
    )
    edgemap = edgemap.T

    return edges, idx + 1, edgemap


# _________________________________________________________________________________________________________


def uniqfaces(elem):
    """
    faces, idx, facemap = uniqfaces(elem)

    Return the unique face list from a surface or tetrahedral mesh.

    Parameters:
    elem : numpy array
        A list of elements, where each row contains node indices for an element.
        The input `elem` can have 2, 3, or 4 columns.

    Returns:
    faces : numpy array
        Unique faces in the mesh, denoted by triplets of node indices.
    idx : numpy array
        Indices of the unique faces in the raw face list (returned by meshface).
    facemap : numpy array
        Index of the raw faces in the output list (for triangular meshes).
    """

    # Determine faces based on element size
    if elem.shape[1] == 3:
        faces = elem
    elif elem.shape[1] >= 4:
        faces = meshface(elem)
    else:
        raise ValueError("Invalid input: element size not supported.")

    # Find unique faces and their indices
    ufaces, idx, jdx = np.unique(
        np.sort(faces, axis=1), axis=0, return_index=True, return_inverse=True
    )
    faces = faces[idx, :]

    # Compute facemap if requested
    facemap = np.reshape(
        jdx + 1,
        (elem.shape[0], np.array(list(combinations(range(elem.shape[1]), 3))).shape[0]),
        order="F",
    )

    return faces, idx + 1, facemap


def innersurf(node, face, outface=None):
    """
    Extract the interior triangles (shared by two enclosed compartments)
    of a complex surface.

    Parameters:
    node: Node coordinates
    face: Surface triangle list
    outface: (Optional) the exterior triangle list, if not provided,
             will be computed using outersurf().

    Returns:
    inface: The collection of interior triangles of the surface mesh
    """

    # If outface is not provided, compute it using outersurf
    if outface is None:
        outface = outersurf(node, face)

    # Check membership of sorted faces in sorted outface, row-wise
    tf, _ = ismember_rows(np.sort(face, axis=1), np.sort(outface, axis=1))

    # Select faces not part of the exterior (tf == 0)
    inface = face[tf == 0, :]

    return inface


def ismember_rows(array1, array2):
    # Ensure arrays are at least 2D and have same shape
    array1 = np.asarray(array1)
    array2 = np.asarray(array2)

    # Create structured view for row-wise comparison
    dtype = np.dtype((np.void, array1.dtype.itemsize * array1.shape[1]))
    a1_view = np.ascontiguousarray(array1).view(dtype)
    a2_view = np.ascontiguousarray(array2).view(dtype)

    isinside = np.isin(a1_view, a2_view)

    # Mapping: initialize with 0 (not found), +1 for 1-based MATLAB-like output
    map = np.zeros(array1.shape[0], dtype=int)
    for i in range(array1.shape[0]):
        matches = np.where((array2 == array1[i]).all(axis=1))[0]
        if matches.size > 0:
            map[i] = matches[0] + 1  # MATLAB-style index (1-based)

    return isinside, map


def advancefront(edges, loop, elen=3):
    """
    advance an edge-front on an oriented surface to the next separated by
    one-element width

    Author: Qianqian Fang
    Date: 2012/02/09

    Input:
    edges: edge list of an oriented surface mesh, must be in CCW order
    loop: a 2-column array, specifying a closed loop in CCW order
    elen: node number inside each element, if ignored, elen is set to 3

    Output:
    elist: list of triangles enclosed between the two edge-fronts
    nextfront: a new edge loop list representing the next edge-front
    """

    # Initialize output variables
    elist = []
    nextfront = []

    # Check if elen is provided, if not, set to 3
    if elen is None:
        elen = 3

    # Find edges that are part of the loop
    hasedge, loc = ismember(loop, edges)

    # If any edges in loop are not in the mesh, raise an error
    if not np.all(hasedge):
        raise ValueError("Loop edge is not defined in the mesh")

    # Calculate number of nodes in the mesh
    nodenum = len(edges) // elen

    # Find unique elements in the loop
    elist = np.unique((loc - 1) % nodenum) + 1

    # Get the corresponding edges for elist
    nextfront = edges[elist, :]

    # Loop through remaining elements
    for i in range(1, elen):
        nextfront = np.vstack([nextfront, edges[elist + nodenum * i, :]])

    # Remove reversed edge pairs
    nextfront = setdiff(nextfront, loop)
    flag, loc = ismember(nextfront, np.flip(nextfront, axis=1))

    id = np.where(flag)[0]
    if len(id) > 0:
        delmark = flag
        delmark[loc[loc > 0]] = 1
        nextfront = np.delete(nextfront, np.where(delmark), axis=0)

    # Reverse this loop as it is reversed relative to the input loop
    nextfront = nextfront[:, [1, 0]]

    return elist, nextfront


def ismember(A, B):
    """
    Check if rows of A are present in B.

    Returns a boolean array indicating membership and the corresponding indices.
    """
    return np.in1d(
        A.view([("", A.dtype)] * A.shape[1]), B.view([("", B.dtype)] * B.shape[1])
    ), np.where(np.in1d(A, B))


def setdiff(A, B):
    """
    Find the set difference between arrays A and B, row-wise.
    """
    dtype = np.dtype((np.void, A.dtype.itemsize * A.shape[1]))
    A_view = np.ascontiguousarray(A).view(dtype)
    B_view = np.ascontiguousarray(B).view(dtype)
    return A[~np.in1d(A_view, B_view)]


# _________________________________________________________________________________________________________


def meshreorient(node, elem):
    """
    Reorder nodes in a surface or tetrahedral mesh to ensure all
    elements are oriented consistently.

    Parameters:
        node: list of nodes
        elem: list of elements (each row are indices of nodes of each element)

    Returns:
        newelem: the element list with consistent ordering
        evol: the signed element volume before reorientation
        idx: indices of the elements that had negative volume
    """
    # Calculate the canonical volume of the element (can be a 2D or 3D)
    evol = elemvolume(node, elem, "signed")

    # Make sure all elements are positive in volume
    idx = np.where(evol < 0)[0]

    # Reorder the last two nodes for elements with negative volume
    elem[np.ix_(idx, [-2, -1])] = elem[np.ix_(idx, [-1, -2])]
    newelem = elem

    return newelem, evol, idx


# _________________________________________________________________________________________________________


def meshcentroid(v, f):
    #
    # centroid=meshcentroid(v,f)
    #
    # compute the centroids of a mesh defined by nodes and elements
    # (surface or tetrahedra) in R^n space
    #
    # input:
    #      v: surface node list, dimension (nn,3)
    #      f: surface face element list, dimension (be,3)
    #
    # output:
    #      centroid: centroid positions, one row for each element
    #
    if not isinstance(f, list):
        ec = v[f[:, :] - 1, :]
        centroid = np.squeeze(np.mean(ec, axis=1))
    else:
        length_f = len(f)
        centroid = np.zeros((length_f, v.shape[1]))
        try:
            for i in range(length_f):
                fc = f[i] - 1
                if fc:  # need to set centroid to NaN if fc is empty?
                    vlist = fc[0]
                    centroid[i, :] = np.mean(
                        v[vlist[~np.isnan(vlist)], :], axis=0
                    )  # Note to Ed check if this is functioning correctly
        except Exception as e:
            raise ValueError("malformed face cell array") from e
    return centroid


# _________________________________________________________________________________________________________


def elemfacecenter(node, elem):
    """
    Generate barycentric dual-mesh face center nodes and indices for each tetrahedral element.

    Args:
        node: List of node coordinates.
        elem: List of elements (each row contains the indices of nodes forming each tetrahedral element).

    Returns:
        newnode: Coordinates of new face-center nodes.
        newelem: Indices of the face-center nodes for each original tetrahedral element.
    """

    # Find unique faces from the elements (tetrahedral mesh)
    faces, idx, newelem = uniqfaces(elem[:, :4])

    # Extract the coordinates of the nodes forming these faces
    newnode = node[faces.T - 1, :3]
    newnode = np.mean(newnode, axis=0)

    return newnode, newelem


# _________________________________________________________________________________________________________


def barydualmesh(node, elem, flag=None):
    """
    Generate barycentric dual-mesh by connecting edge, face, and element centers.

    Parameters:
    node : numpy.ndarray
        List of input mesh nodes.
    elem : numpy.ndarray
        List of input mesh elements (each row contains indices of nodes for each element).
    flag : str, optional
        If 'cell', outputs `newelem` as cell arrays (each with 4 nodes).

    Returns:
    newnode : numpy.ndarray
        All new nodes in the barycentric dual-mesh (made of edge, face, and element centers).
    newelem : numpy.ndarray or list
        Indices of face nodes for each original tet element, optionally in cell array format.
    """

    # Compute edge-centers
    enodes, eidx = highordertet(node, elem)

    # Compute face-centers
    fnodes, fidx = elemfacecenter(node, elem)

    # Compute element centers
    c0 = meshcentroid(node, elem[:, : min(elem.shape[1], 4)])

    # Concatenate new nodes and their indices
    newnode = np.vstack((enodes, fnodes, c0))

    newidx = np.hstack(
        (
            eidx,
            fidx + enodes.shape[0],
            np.arange(1, elem.shape[0] + 1).reshape(-1, 1)
            + enodes.shape[0]
            + fnodes.shape[0],
        )
    )

    # Element connectivity for barycentric dual-mesh (using original indexing)
    newelem = (
        np.array(
            [
                [1, 8, 11, 7],
                [2, 7, 11, 9],
                [3, 9, 11, 8],
                [4, 7, 11, 10],
                [5, 8, 11, 10],
                [6, 9, 11, 10],
            ]
        ).T
        - 1
    )  # Adjust to 0-based indexing for Python

    newelem = newidx[:, newelem.flatten()]
    newelem = newelem.T.reshape(4, -1).T

    # If the 'cell' flag is set, return `newelem` as a list of lists (cells)
    if flag == "cell":
        newelem = [newelem[i, :].tolist() for i in range(newelem.shape[0])]

    return newnode, newelem


# _________________________________________________________________________________________________________


def highordertet(node, elem, order=2, opt=None):
    """
    Generate a higher-order tetrahedral mesh by refining a linear tetrahedral mesh.

    Args:
        node: Nodal coordinates of the linear tetrahedral mesh (n_nodes, 3).
        elem: Element connectivity (n_elements, 4).
        order: Desired order of the output mesh (default is 2 for quadratic mesh).
        opt: Optional dictionary to control mesh refinement options.

    Returns:
        newnode: Nodal coordinates of the higher-order tetrahedral mesh.
        newelem: Element connectivity of the higher-order tetrahedral mesh.
    """

    if order >= 3 or order <= 1:
        raise ValueError("currently this function only supports order=2")

    edges, idx, newelem = uniqedges(elem[:, : min(elem.shape[1], 4)])
    newnode = node[edges.T - 1, :3]  # adjust for 1-based index
    newnode = np.mean(newnode, axis=0)
    return newnode, newelem + 1


def internalpoint(v, aloop):
    """
    Empirical function to find an internal point of a planar polygon.

    Parameters:
        v : ndarray
            Nx3 array of x, y, z coordinates of each node of the mesh.
        aloop : array-like
            A vector of node indices (1-based, as in MATLAB), possibly separated by NaN.

    Returns:
        p : ndarray
            A single [x, y, z] internal point of the polygon loop.

    Raises:
        ValueError: If an internal point cannot be found.

    -- this function is part of iso2mesh toolbox (http://iso2mesh.sf.net)
    """
    from matplotlib.path import Path

    # Adjust aloop to 0-based index
    aloop = np.asarray(aloop, dtype=float)
    aloop = aloop[~np.isnan(aloop)].astype(int) - 1

    p = []
    nd = v[aloop, :]

    # Find if loop is flat along any axis
    boxfacet = np.where(np.sum(np.abs(np.diff(nd, axis=0)), axis=0) < 1e-2)[0]
    if len(boxfacet) > 0:
        bf = boxfacet[0]
        idx = [i for i in [0, 1, 2] if i != bf]

        p0 = (nd[0, :] + nd[1, :]) / 2
        pvec = complex(p0[idx[0]], p0[idx[1]])
        vec = nd[1, :] - nd[0, :]
        vec_mag = np.sqrt(np.sum(vec**2))
        vec = (
            complex(vec[idx[0]], vec[idx[1]])
            * np.exp(1j * np.pi / 2)
            * (1e-5)
            / vec_mag
        )
        testpt = np.array(
            [
                [np.real(pvec + vec), np.imag(pvec + vec)],
                [np.real(pvec - vec), np.imag(pvec - vec)],
            ]
        )

        path = Path(nd[:, idx])
        inside = path.contains_points(testpt)
        p2d = testpt[inside]
        if p2d.size > 0:
            p = np.zeros(3)
            p[[idx[0], idx[1]]] = p2d[0]
            p[bf] = nd[0, bf]

    if len(p) == 0 or len(p) != 3:
        raise ValueError("Fail to find an internal point of curve")

    return p


def ray2surf(node, elem, p0, v0, e0):
    """
    Determine the entry position and element for a ray to intersect a mesh

    Author: Qianqian Fang (q.fang <at> neu.edu)
    Python conversion: Preserves exact algorithm from MATLAB version

    Parameters:
    -----------
    node : ndarray
        The mesh coordinate list
    elem : ndarray
        The tetrahedral mesh element list, 4 columns
    p0 : ndarray
        Origin of the ray
    v0 : ndarray
        Direction vector of the ray
    e0 : str or float
        Search direction: '>' forward search, '<' backward search, '-' bidirectional

    Returns:
    --------: np.ndarray
    p : ndarray
        The intersection position
    e0 : int or float
        If found, the index of the intersecting element ID

    Notes:
    ------
    This file is part of Mesh-based Monte Carlo (MMC)
    License: GPLv3, see http://mcx.sf.net/mmc/ for details
    """

    p = p0.copy()

    if elem.shape[1] == 3:
        face = elem.copy()
    else:
        face = volface(elem)

    t, u, v, idx = raytrace(p0, v0, node, face)

    if len(idx) == 0:  # isempty(idx) in MATLAB
        raise RuntimeError("ray does not intersect with the mesh")
    else:
        t = t[idx]
        if e0 == ">":
            # idx1 = find(t>=0);
            idx1 = np.where(t >= 1e-10)[0]
        elif e0 == "<":
            idx1 = np.where(t <= 0)[0]
        elif np.isnan(e0) or e0 == "-":
            idx1 = np.arange(len(t))
        else:
            raise ValueError("ray direction specifier is not recognized")

        if len(idx1) == 0:  # isempty(idx1) in MATLAB
            raise RuntimeError("no intersection is found along the ray direction")

        t0 = np.abs(t[idx1])
        loc = np.argmin(t0)
        tmin = t0[loc]
        faceidx = idx[idx1[loc]]

        # Update source position
        p = p0 + t[idx1[loc]] * v0

        if elem.shape[1] == 3:
            e0 = faceidx
        else:
            # Convert faceidx to 0-based index when using as array index
            felem = np.sort(face[faceidx, :])
            f = elem.copy()

            # Create face combinations - subtract 1 for 0-based indexing when accessing elem
            f = np.vstack(
                [
                    elem[
                        :, [0, 1, 2]
                    ],  # elem[:, [1, 2, 3]] - 1 (MATLAB 1-based to Python 0-based)
                    elem[:, [1, 0, 3]],  # elem[:, [2, 1, 4]] - 1
                    elem[:, [0, 2, 3]],  # elem[:, [1, 3, 4]] - 1
                    elem[:, [1, 3, 2]],  # elem[:, [2, 4, 3]] - 1
                ]
            )

            # Sort each row for comparison
            f_sorted = np.sort(f, axis=1)

            # Find matching face using ismember equivalent
            tf, loc = ismember_rows(felem.reshape(1, -1), f_sorted)

            if tf[0]:
                loc = loc[0] % elem.shape[0]
                if loc == 0:
                    loc = elem.shape[0]
                e0 = loc
            else:
                # If no match found, return original faceidx
                e0 = faceidx

    return p, e0
