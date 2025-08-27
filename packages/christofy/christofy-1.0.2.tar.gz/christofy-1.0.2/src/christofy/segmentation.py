import math
import numpy as np
import random
import time
from skimage import io
import matplotlib.pyplot as plt

np.seterr(over='ignore')

# ================================================
# --- Utility Functions ---
# ================================================

def square(value):
    return value * value

def random_rgb():
    return np.array([random.randint(0, 255) for _ in range(3)], dtype=np.uint8)

def diff(red_band, green_band, blue_band, x1, y1, x2, y2):
    return math.sqrt(
        square(red_band[y1, x1] - red_band[y2, x2]) +
        square(green_band[y1, x1] - green_band[y2, x2]) +
        square(blue_band[y1, x1] - blue_band[y2, x2])
    )

def get_threshold(size, c):
    return c / size

# ================================================
# --- Disjoint-set (Union-Find) ---
# ================================================

class universe:
    def __init__(self, n_elements):
        self.num = n_elements
        self.elts = np.empty((n_elements, 3), dtype=int)
        for i in range(n_elements):
            self.elts[i, 0] = 0  # rank
            self.elts[i, 1] = 1  # size
            self.elts[i, 2] = i  # parent

    def size(self, x):
        return self.elts[x, 1]

    def num_sets(self):
        return self.num

    def find(self, x):
        if self.elts[x, 2] != x:
            self.elts[x, 2] = self.find(self.elts[x, 2])
        return self.elts[x, 2]

    def join(self, x, y):
        if self.elts[x, 0] > self.elts[y, 0]:
            self.elts[y, 2] = x
            self.elts[x, 1] += self.elts[y, 1]
        else:
            self.elts[x, 2] = y
            self.elts[y, 1] += self.elts[x, 1]
            if self.elts[x, 0] == self.elts[y, 0]:
                self.elts[y, 0] += 1
        self.num -= 1

# ================================================
# --- Gaussian Smoothing ---
# ================================================

WIDTH = 4.0

def make_fgauss(sigma):
    sigma = max(sigma, 0.01)
    length = int(math.ceil(sigma * WIDTH)) + 1
    mask = np.zeros((length, length), dtype=float)
    for i in range(length):
        for j in range(length):
            mask[i, j] = math.exp(-0.5 * ((i / sigma) ** 2 + (j / sigma) ** 2))
    return mask

def normalize(mask):
    acc = 4 * np.sum(np.abs(mask)) - 3 * abs(mask[0, 0]) - \
          2 * np.sum(np.abs(mask[0, :])) - 2 * np.sum(np.abs(mask[:, 0]))
    return mask / acc

def convolve_even(src, mask):
    output = np.zeros_like(src, dtype=float)
    height, width = src.shape
    length = len(mask)

    for y in range(height):
        for x in range(width):
            acc = float(mask[0, 0] * src[y, x])
            for i in range(length):
                for j in range(length):
                    if i != 0 and j != 0:
                        acc += mask[i, j] * (
                            src[max(y - j, 0), max(x - i, 0)] +
                            src[max(y - j, 0), min(x + i, width - 1)] +
                            src[min(y + j, height - 1), min(x + i, width - 1)] +
                            src[min(y + j, height - 1), max(x - i, 0)]
                        )
            output[y, x] = acc
    return output

def smooth(src, sigma):
    mask = make_fgauss(sigma)
    mask = normalize(mask)
    return convolve_even(src, mask)

# ================================================
# --- Graph Segmentation ---
# ================================================

def segment_graph(num_vertices, num_edges, edges, c):
    edges[0:num_edges, :] = edges[edges[0:num_edges, 2].argsort()]
    u = universe(num_vertices)
    threshold = np.array([get_threshold(1, c) for _ in range(num_vertices)], dtype=float)

    for i in range(num_edges):
        pedge = edges[i, :]
        a = u.find(pedge[0])
        b = u.find(pedge[1])
        if a != b and pedge[2] <= min(threshold[a], threshold[b]):
            u.join(a, b)
            a = u.find(a)
            threshold[a] = pedge[2] + get_threshold(u.size(a), c)
    return u

# ================================================
# --- Image Segmentation Pipeline ---
# ================================================

def segment(in_image, sigma, merge_threshold, min_size):
    start_time = time.time()
    height, width, band = in_image.shape
    print("Height:  ", height)
    print("Width:   ", width)

    # Smooth each channel
    smooth_red = smooth(in_image[:, :, 0], sigma)
    smooth_green = smooth(in_image[:, :, 1], sigma)
    smooth_blue = smooth(in_image[:, :, 2], sigma)

    # Build graph
    edges_size = width * height * 4
    edges = np.zeros((edges_size, 3), dtype=object)
    num = 0

    for y in range(height):
        for x in range(width):
            idx = y * width + x
            if x < width - 1:
                edges[num] = [idx, idx + 1,
                              diff(smooth_red, smooth_green, smooth_blue, x, y, x + 1, y)]
                num += 1
            if y < height - 1:
                edges[num] = [idx, idx + width,
                              diff(smooth_red, smooth_green, smooth_blue, x, y, x, y + 1)]
                num += 1
            if x < width - 1 and y < height - 1:
                edges[num] = [idx, idx + width + 1,
                              diff(smooth_red, smooth_green, smooth_blue, x, y, x + 1, y + 1)]
                num += 1
            if x < width - 1 and y > 0:
                edges[num] = [idx, idx - width + 1,
                              diff(smooth_red, smooth_green, smooth_blue, x, y, x + 1, y - 1)]
                num += 1

    # Segment
    u = segment_graph(width * height, num, edges, merge_threshold)

    # Post-process small components
    for i in range(num):
        a = u.find(edges[i, 0])
        b = u.find(edges[i, 1])
        if a != b and (u.size(a) < min_size or u.size(b) < min_size):
            u.join(a, b)

    num_cc = u.num_sets()
    print("Number of segments:", num_cc)

    # Assign colors
    output = np.zeros((height, width, 3), dtype=int)
    colors = np.array([random_rgb() for _ in range(width * height)])

    for y in range(height):
        for x in range(width):
            comp = u.find(y * width + x)
            output[y, x] = colors[comp]

    elapsed_time = time.time() - start_time
    print("Execution time: {} minute(s) and {} second(s)".format(
        int(elapsed_time / 60), int(elapsed_time % 60)
    ))

    # Display
    fig = plt.figure(figsize=(10, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(in_image)
    ax1.set_title("Original Image")
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(output.astype(np.uint8))
    ax2.set_title("Segmented Image")
    ax2.axis("off")
    plt.tight_layout()
    plt.show()

# ================================================
# --- Public API ---
# ================================================

def segmenter(image_path, sigma=0.5, merge_threshold=500, min_size=50):
    """
    Segments an image using a graph-based segmentation algorithm and displays the result.

    Args:
        image_path (str): Path to the input image.
        sigma (float): Standard deviation for Gaussian smoothing.
        merge_threshold (float): Merge threshold for graph segmentation.
        min_size (int): Minimum size of a segment.
    """
    input_image = io.imread(image_path)
    print("Loading is done.")
    print("processing...")
    segment(input_image, sigma, merge_threshold, min_size)
