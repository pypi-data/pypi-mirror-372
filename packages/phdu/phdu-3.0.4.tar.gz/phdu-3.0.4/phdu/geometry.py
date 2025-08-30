import numpy as np
from numba import njit, prange
from numba.types import boolean
import matplotlib.pyplot as plt

@njit
def is_point_on_line(p0, p1, q):
    """ Check if point q is on line segment p0-p1 """
    return (min(p0[0], p1[0]) <= q[0] <= max(p0[0], p1[0]) and
            min(p0[1], p1[1]) <= q[1] <= max(p0[1], p1[1]))

@njit
def is_point_inside_polygon(point, polygon):
    """Returns True if the point is inside the polygon."""
    n = len(polygon)
    inside = False

    x, y = point
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    else:
                        xints = x # handle horizontal lines
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

@njit(parallel=True)
def is_inside_polygon_parallel(points, polygon):
    """Determine if multiple points are inside a given polygon using parallel processing."""
    results = np.empty(len(points), dtype=np.bool_)
    for i in prange(len(points)):
        results[i] = is_point_inside_polygon(points[i], polygon)
    return results

@njit
def centroid_irregular_polygon(vertices):
    # Ensure vertices form a closed polygon by repeating the first vertex at the end
    if (vertices[0] != vertices[-1]).all():
        vertices = np.vstack((vertices, vertices[:1]))

    # Initialize area and centroid coordinates
    A = 0
    C_x = 0
    C_y = 0

    # Number of vertices (excluding the repeated first vertex at the end)
    N = len(vertices) - 1

    for i in range(N):
        x_i, y_i = vertices[i]
        x_next, y_next = vertices[i + 1]

        common_factor = (x_i * y_next - x_next * y_i)
        A += common_factor
        C_x += (x_i + x_next) * common_factor
        C_y += (y_i + y_next) * common_factor

    A = A / 2
    C_x = C_x / (6 * A)
    C_y = C_y / (6 * A)

    return np.array([C_x, C_y])

def extract_contour_polygons(x, y, z, level=None):
    """
    Extracts contour polygons from a 3D plot.

    Parameters:
    x (1D numpy.ndarray): The x-coordinates of the points on the contour.
    y (1D numpy.ndarray): The y-coordinates of the points on the contour.
    z (2D numpy.ndarray): The z-coordinates of the points on the contour.
    level (float, optional): The level for which to extract the contour polygons. If None, all levels are extracted.

    Returns:
    levels: A numpy array of contour levels (only if level is None).
    polygons: A list of contour polygons. Each polygon is represented by a numpy.ndarray of its vertices.
    """
    fig, ax = plt.subplots()

    if level is None:
        contour = ax.contour(x, y, z)
        levels = []
        polygons = []
        for i, collection in enumerate(contour.collections):
            contour_level = contour.levels[i]
            for path in collection.get_paths():
                vertices = path.vertices
                levels.append(contour_level)
                polygons.append(vertices)
        levels = np.array(levels)
        plt.close()
        return levels, polygons
    else:
        contour = ax.contour(x, y, z, levels=[-1000])
        contour_polygons = []
        for collection in contour.collections:
            for path in collection.get_paths():
                # Step 3: Get the vertices of the polygon (the contour path)
                vertices = path.vertices
                contour_polygons.append(vertices)
        plt.close()
        return contour_polygons
