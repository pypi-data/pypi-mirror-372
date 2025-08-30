import os
import sys
import warnings

import glymur
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from scipy.interpolate import CubicSpline

from structure_tensor.multiprocessing import parallel_structure_tensor_analysis
from tqdm import tqdm

from cardiotensor.colormaps.helix_angle import helix_angle_cmap
from cardiotensor.utils.utils import convert_to_8bit



def interpolate_points(
    points: list[tuple[float, float, float]], N_img: int
) -> np.ndarray:
    """
    Generates interpolated points using cubic spline interpolation for a given set of 3D points.

    Args:
        points (list[tuple[float, float, float]]): A list of (x, y, z) points.
        N_img (int): The number of slices in the z-dimension.

    Returns:
        np.ndarray: Array of interpolated points.
    """
    if len(points) < 2:
        raise ValueError("At least two points are required for interpolation.")

    # Sort based on the third element (z-coordinate)
    points = sorted(points, key=lambda p: p[2])

    # Extract x, y, z coordinates separately
    points_array = np.array(points)
    x_vals, y_vals, z_vals = points_array[:, 0], points_array[:, 1], points_array[:, 2]

    # Define cubic splines for x and y based on given z values
    cs_x = CubicSpline(z_vals, x_vals, bc_type="natural")
    cs_y = CubicSpline(z_vals, y_vals, bc_type="natural")

    # Generate integer z-values from 1 to N_img
    z_interp = np.arange(0, N_img)

    # Compute interpolated x and y values at integer z positions
    x_interp = cs_x(z_interp)
    y_interp = cs_y(z_interp)

    # Stack into an Nx3 array
    interpolated_points = np.column_stack((x_interp, y_interp, z_interp))

    return interpolated_points


def calculate_center_vector(points: np.ndarray) -> np.ndarray:
    """Compute the linear regression vector for a given set of 3D points.

    Args:
        points (np.ndarray): An Nx3 array of (x, y, z) coordinates representing the curved line.

    Returns:
        np.ndarray: A single 3D unit vector representing the direction of the best-fit line.
    """
    if points.shape[1] != 3:
        raise ValueError("Input must be an Nx3 array of (x, y, z) coordinates.")

    # Compute the centroid (mean position of all points)
    centroid = np.mean(points, axis=0)

    # Center the points by subtracting the centroid
    centered_points = points - centroid

    # Perform Singular Value Decomposition (SVD)
    # This decomposes the data into principal components
    _, _, vh = np.linalg.svd(centered_points)

    center_vec = vh[0] / np.linalg.norm(vh[0])

    # Extract the Dominant Direction
    center_vec = -center_vec[[2, 1, 0]]

    return center_vec


def adjust_start_end_index(
    start_index: int,
    end_index: int,
    N_img: int,
    padding_start: int = 0,
    padding_end: int = 0,
    is_test: bool = False,
    n_slice: int = 0,
) -> tuple[int, int]:
    """
    Adjusts start and end indices for image processing, considering padding and test mode.

    Args:
        start_index (int): The initial start index.
        end_index (int): The initial end index.
        N_img (int): Number of images in the volume data.
        padding_start (int): Padding to add at the start.
        padding_end (int): Padding to add at the end.
        is_test (bool): Flag indicating whether in test mode.
        n_slice (int): Test slice index.

    Returns:
        Tuple[int, int]: Adjusted start and end indices.
    """

    # Adjust indices for test condition
    if is_test:
        test_index = n_slice
        # else:
        #     test_index = int(N_img / 1.68)
        #     # test_index = 1723

        start_index_padded = max(test_index - padding_start, 0)
        end_index_padded = min(test_index + 1 + padding_end, N_img)
    else:
        # Adjust start and end indices considering padding
        start_index_padded = max(start_index - padding_start, 0)
        end_index_padded = min(end_index + padding_end, N_img)

    return start_index_padded, end_index_padded


import platform
import subprocess


def get_gpu_count() -> int:
    # Try reading CUDA_VISIBLE_DEVICES
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if visible:
        ids = [x for x in visible.split(",") if x.strip().isdigit()]
        if ids:
            return len(ids)

    # Try nvidia-smi
    try:
        smi_command = "nvidia-smi"
        if platform.system() == "Windows":
            # Use full path if needed
            smi_command = r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"

        result = subprocess.run(
            [smi_command, "-L"],
            capture_output=True,
            text=True,
            check=True,
        )
        return len(
            [line for line in result.stdout.strip().splitlines() if "GPU" in line]
        )
    except Exception:
        return 0


def calculate_structure_tensor(
    volume: np.ndarray,
    sigma: float,
    rho: float,
    truncate: float = 4.0,
    devices: list[str] | None = None,
    block_size: int = 200,
    use_gpu: bool = False,
    dtype: type = np.float32,  # Default to np.float64
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculates the structure tensor of a volume.

    Args:
        volume (np.ndarray): The 3D volume data.
        sigma (float): sigma value for Gaussian smoothing.
        rho (float): rho value for Gaussian smoothing.
        devices (Optional[list[str]]): List of devices for parallel processing (e.g., ['cpu', 'cuda:0']).
        block_size (int): Size of the blocks for processing. Default is 200.
        use_gpu (bool): If True, uses GPU for calculations. Default is False.

    Returns:
        tuple[np.ndarray, np.ndarray]: Eigenvalues and eigenvectors of the structure tensor.
    """
    # Filter or ignore specific warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    num_cpus = max(
        os.cpu_count() or 4, 4
    )  # Default to 4 if os.cpu_count() returns None

    devices = devices or []
    num_gpus = 0

    if use_gpu:
        print("🔍 Checking for GPU support...")
        try:
            num_gpus = get_gpu_count()
            print(f"Detected {num_gpus} GPU(s)")
        except Exception as e:
            use_gpu = False
            print(
                f"⚠️ GPU not available or failed to initialize. Using CPU. Reason: {e}"
            )

    if not devices:
        if use_gpu and num_gpus > 0:
            print(f"Using {num_gpus} GPUs for computation")
            devices = []
            for i in range(num_gpus):
                devices.extend([f"cuda:{i}"] * 16)
        else:
            print(f"Using {num_cpus} CPU for computation")
            devices = ["cpu"] * num_cpus

    print("\nStarting structure tensor computation...")
    print(f"---  Volume shape: {volume.shape}")
    print(f"---  sigma: {sigma}, rho: {rho}, Block size: {block_size}")
    if use_gpu and num_gpus > 0:
        device_str = f"{num_gpus} GPU{'s' if num_gpus > 1 else ''}"
    else:
        device_str = f"{num_cpus} CPU{'s' if num_cpus > 1 else ''}"
    print(f"---  Devices: {device_str}")

    class TqdmTotal(tqdm):
        def update_with_total(self, n=1, total=None):
            if total is not None:
                self.total = total
            return self.update(1)

    with TqdmTotal(desc="Computing structure tensors", unit="block") as t:
        S, val, vec = parallel_structure_tensor_analysis(
            volume,
            sigma,
            rho,
            devices=devices,
            block_size=block_size,
            truncate=truncate,
            structure_tensor=None,
            eigenvectors=dtype,
            eigenvalues=dtype,
            progress_callback_fn=t.update_with_total,
        )

    print("Structure tensor computation completed\n")

    # vec has shape =(3,z,y,x) in the order of (x,y,z)

    return val, vec


def remove_padding(
    volume: np.ndarray,
    val: np.ndarray,
    vec: np.ndarray,
    padding_start: int,
    padding_end: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Removes padding from the volume, eigenvalues, and eigenvectors.

    Args:
        volume (np.ndarray): The 3D volume data.
        val (np.ndarray): The eigenvalues.
        vec (np.ndarray): The eigenvectors.
        padding_start (int): Padding at the start to remove.
        padding_end (int): Padding at the end to remove.

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: Adjusted data without padding.
    """
    array_end = vec.shape[1] - padding_end
    volume = volume[padding_start:array_end, :, :]
    vec = vec[:, padding_start:array_end, :, :]
    val = val[:, padding_start:array_end, :, :]

    return volume, val, vec


def compute_fraction_anisotropy(eigenvalues_2d: np.ndarray) -> np.ndarray:
    """
    Computes Fractional Anisotropy (FA) from eigenvalues of a structure tensor.

    Args:
        eigenvalues_2d (np.ndarray): 2D array of eigenvalues (l1, l2, l3).

    Returns:
        np.ndarray: Fractional Anisotropy values.
    """
    l1 = eigenvalues_2d[0, :, :]
    l2 = eigenvalues_2d[1, :, :]
    l3 = eigenvalues_2d[2, :, :]
    mean_eigenvalue = (l1 + l2 + l3) / 3
    numerator = np.sqrt(
        (l1 - mean_eigenvalue) ** 2
        + (l2 - mean_eigenvalue) ** 2
        + (l3 - mean_eigenvalue) ** 2
    )
    denominator = np.sqrt(l1**2 + l2**2 + l3**2) + 1e-10
    img_FA = np.sqrt(3 / 2) * (numerator / denominator)

    return img_FA


def rotate_vectors_to_new_axis(
    vector_field_slice: np.ndarray, new_axis_vec: np.ndarray
) -> np.ndarray:
    """
    Rotates a vector field slice to align with a new axis.

    Args:
        vector_field_slice (np.ndarray): Array of shape (3, Y, X) for a slice.
        new_axis_vec (np.ndarray): The new axis to align vectors with (3,).

    Returns:
        np.ndarray: Rotated vectors with the same shape as input.
    """
    # Normalize the new axis
    new_axis_vec = new_axis_vec / np.linalg.norm(new_axis_vec)

    # Define the original reference axis (X-axis here)
    vec1 = np.array([1, 0, 0], dtype=np.float32)

    # Adjust for sign (optional)
    vec1 = vec1 * np.sign(new_axis_vec[0])

    # Compute rotation matrix using Rodrigues' formula
    a = vec1 / np.linalg.norm(vec1)
    b = new_axis_vec
    v = np.cross(a, b)
    c = np.dot(a, b)

    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

    if np.linalg.norm(v) != 0:
        rotation_matrix = (
            np.eye(3) + kmat + np.dot(kmat, kmat) * ((1 - c) / (np.linalg.norm(v) ** 2))
        )
    else:
        rotation_matrix = np.eye(3)

    # Flatten the vector field to shape (3, N)
    vec_reshaped = np.reshape(vector_field_slice, (3, -1))

    # Normalize safely
    norms = np.linalg.norm(vec_reshaped, axis=0)
    nonzero_mask = norms > 0
    vec_reshaped[:, nonzero_mask] /= norms[nonzero_mask]

    # Rotate
    rotated_vecs = np.dot(rotation_matrix, vec_reshaped)

    # Reshape back
    rotated_vecs = rotated_vecs.reshape(vector_field_slice.shape)

    return rotated_vecs


def compute_helix_and_transverse_angles(
    vector_field_2d: np.ndarray,
    center_point: tuple[int, int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """
    Computes helix and transverse angles from a 2D vector field.

    Args:
        vector_field_2d (np.ndarray): 2D orientation vector field.
        center_point (Tuple[int, int, int]): Coordinates of the center point.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Helix and transverse angle arrays.
    """
    center = center_point[0:2]  # Replace with actual values
    rows, cols = vector_field_2d.shape[1:3]

    reshaped_vector_field = np.reshape(vector_field_2d, (3, -1))

    center_x, center_y = center[0], center[1]

    X, Y = np.meshgrid(np.arange(cols) - center_x, np.arange(rows) - center_y)

    theta = -np.arctan2(Y.flatten(), X.flatten())
    cos_angle = np.cos(theta)
    sin_angle = np.sin(theta)

    # Change coordinate system to cylindrical
    rotated_vector_field = np.copy(reshaped_vector_field)
    rotated_vector_field[0, :] = (
        cos_angle * reshaped_vector_field[0, :]
        - sin_angle * reshaped_vector_field[1, :]
    )
    rotated_vector_field[1, :] = (
        sin_angle * reshaped_vector_field[0, :]
        + cos_angle * reshaped_vector_field[1, :]
    )

    # Reshape rotated vector field to original image dimensions
    reshaped_rotated_vector_field = np.zeros((3, rows, cols))
    for i in range(3):
        reshaped_rotated_vector_field[i] = rotated_vector_field[i].reshape(rows, cols)

    # Calculate helix and transverse angles
    helix_angle = np.arctan(
        reshaped_rotated_vector_field[2, :, :] / reshaped_rotated_vector_field[1, :, :]
    )
    transverse_angle = np.arctan(
        reshaped_rotated_vector_field[0, :, :] / reshaped_rotated_vector_field[1, :, :]
    )
    helix_angle = np.rad2deg(helix_angle)
    transverse_angle = np.rad2deg(transverse_angle)

    return helix_angle, transverse_angle


def plot_images(
    img: np.ndarray,
    img_helix: np.ndarray,
    img_intrusion: np.ndarray,
    img_FA: np.ndarray,
    center_point: tuple[int, int, int],
    colormap_angle=None,
    colormap_FA=None,
) -> None:
    """
    Plots images of the heart with helix, intrusion, and FA annotations.

    Args:
        img (np.ndarray): Grayscale image of the heart.
        img_helix (np.ndarray): Helix angle image.
        img_intrusion (np.ndarray): Intrusion angle image.
        img_FA (np.ndarray): Fractional Anisotropy (FA) image.
        center_point (Tuple[int, int, int]): Coordinates of the center point.
        colormap_angle: Colormap for helix and intrusion angles (default: helix_angle_cmap).
        colormap_FA: Colormap for FA image (default: 'inferno').

    Returns:
        None
    """


    # Default colormaps
    if colormap_angle is None:
        colormap_angle = helix_angle_cmap
    if colormap_FA is None:
        colormap_FA = plt.get_cmap("inferno")

    # Determine display range for original image
    img_vmin, img_vmax = np.nanpercentile(img, (5, 95))

    # Create a figure and axes
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    ax = axes

    # Original Image with Red Point
    ax[0, 0].imshow(img, vmin=img_vmin, vmax=img_vmax, cmap="gray")
    x, y = center_point[0:2]
    ax[0, 0].scatter(x, y, c="red", s=50, marker="o", label="Axis Point")
    ax[0, 0].set_title("Original Image")
    ax[0, 0].legend(loc="upper right")

    # Helix Image
    tmp = ax[0, 1].imshow(img_helix, cmap=colormap_angle, vmin=-90, vmax=90)
    ax[0, 1].set_title("Helix Angle")

    # Intrusion Image
    ax[1, 0].imshow(img_intrusion, cmap=colormap_angle, vmin=-90, vmax=90)
    ax[1, 0].set_title("Intrusion Angle")

    # FA Image
    fa_plot = ax[1, 1].imshow(img_FA, cmap=colormap_FA, vmin=0, vmax=1)
    ax[1, 1].set_title("Fractional Anisotropy")

    # Add colorbars for relevant subplots
    cbar1 = fig.colorbar(tmp, ax=ax[0, 1], orientation="vertical")
    cbar1.set_label("Helix Angle")
    cbar2 = fig.colorbar(fa_plot, ax=ax[1, 1], orientation="vertical")
    cbar2.set_label("Fractional Anisotropy")

    # Hide axes for a cleaner view
    for axis in ax.flat:
        axis.axis("off")

    # Adjust layout to prevent overlap
    fig.tight_layout()
    plt.show()


def write_images(
    img_helix: np.ndarray,
    img_intrusion: np.ndarray,
    img_FA: np.ndarray,
    start_index: int,
    output_dir: str,
    output_format: str,
    output_type: str,
    z: int,
    colormap_angle=None,
    colormap_FA=None,
) -> None:
    """
    Writes processed images to the specified directory.

    Args:
        img_helix (np.ndarray): Image data for helix angles.
        img_intrusion (np.ndarray): Image data for intrusion angles.
        img_FA (np.ndarray): Image data for fractional anisotropy.
        start_index (int): Starting index for filenames.
        output_dir (str): Directory to save the images.
        output_format (str): Format of the output files ('tif' or 'jp2').
        output_type (str): Type of output ('8bit' or 'rgb').
        z (int): Current slice index.
        colormap_angle: Colormap for helix and intrusion angles (default: helix_angle_cmap).
        colormap_FA: Colormap for FA image (default: 'inferno').

    Returns:
        None
    """

    # Default colormaps
    if colormap_angle is None:
        colormap_angle = helix_angle_cmap
    if colormap_FA is None:
        colormap_FA = plt.get_cmap("inferno")

    try:
        os.makedirs(output_dir + "/HA", exist_ok=True)
        os.makedirs(output_dir + "/IA", exist_ok=True)
        os.makedirs(output_dir + "/FA", exist_ok=True)
    except PermissionError:
        print("⚠️ - Permission error during creation of output directories")

    # ---- 8-bit output ----
    if "8bit" in output_type:
        img_helix_8bit = convert_to_8bit(img_helix, min_value=-90, max_value=90)
        img_intrusion_8bit = convert_to_8bit(img_intrusion, min_value=-90, max_value=90)
        img_FA_8bit = convert_to_8bit(img_FA, min_value=0, max_value=1)

        if output_format == "jp2":
            ratio_compression = 10

            ha_path = f"{output_dir}/HA/HA_{(start_index + z):06d}.jp2"
            ia_path = f"{output_dir}/IA/IA_{(start_index + z):06d}.jp2"
            fa_path = f"{output_dir}/FA/FA_{(start_index + z):06d}.jp2"

            for file_path in [ha_path, ia_path, fa_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)

            glymur.Jp2k(
                ha_path,
                data=img_helix_8bit,
                cratios=[ratio_compression],
                numres=8,
                irreversible=True,
            )
            glymur.Jp2k(
                ia_path,
                data=img_intrusion_8bit,
                cratios=[ratio_compression],
                numres=8,
                irreversible=True,
            )
            glymur.Jp2k(
                fa_path,
                data=img_FA_8bit,
                cratios=[ratio_compression],
                numres=8,
                irreversible=True,
            )

        elif output_format == "tif":
            tifffile.imwrite(
                f"{output_dir}/HA/HA_{(start_index + z):06d}.tif", img_helix_8bit
            )
            tifffile.imwrite(
                f"{output_dir}/IA/IA_{(start_index + z):06d}.tif", img_intrusion_8bit
            )
            tifffile.imwrite(
                f"{output_dir}/FA/FA_{(start_index + z):06d}.tif", img_FA_8bit
            )
        else:
            sys.exit(f"I don't recognise the output_format ({output_format})")

    # ---- RGB output ----
    elif "rgb" in output_type:

        def write_img_rgb(
            img: np.ndarray,
            output_path: str,
            cmap: plt.Colormap,
            vmin: float,
            vmax: float,
        ) -> None:
            """
            Writes a single 2D RGB image using a fixed colormap range.

            Args:
                img (np.ndarray): Input scalar image.
                output_path (str): Path to save the RGB image.
                cmap (plt.Colormap): Matplotlib colormap (e.g., inferno, custom HA cmap).
                vmin (float): Minimum value for normalization.
                vmax (float): Maximum value for normalization.
            """
            img_clipped = np.clip(img, vmin, vmax)
            img_norm = (img_clipped - vmin) / (vmax - vmin + 1e-8)

            img_rgb = cmap(img_norm)[..., :3]  # Drop alpha channel
            img_rgb = (img_rgb * 255).astype(np.uint8)

            print(img_rgb.shape, img_rgb.dtype)

            if output_path.endswith(".jp2"):
                ratio_compression = 10
                glymur.Jp2k(
                    output_path,
                    data=img_rgb,
                    cratios=[ratio_compression],
                    numres=8,
                    irreversible=True,
                )
            elif output_path.endswith(".tif"):
                tifffile.imwrite(output_path, img_rgb)
            else:
                sys.exit(f"I don't recognise the output path format: {output_path}")

        if output_format == "jp2":
            write_img_rgb(
                img_helix,
                f"{output_dir}/HA/HA_{(start_index + z):06d}.jp2",
                cmap=colormap_angle,
                vmin=-90,
                vmax=90,
            )
            write_img_rgb(
                img_intrusion,
                f"{output_dir}/IA/IA_{(start_index + z):06d}.jp2",
                cmap=colormap_angle,
                vmin=-90,
                vmax=90,
            )
            write_img_rgb(
                img_FA,
                f"{output_dir}/FA/FA_{(start_index + z):06d}.jp2",
                cmap=colormap_FA,
                vmin=0,
                vmax=1,
            )

        elif output_format == "tif":
            write_img_rgb(
                img_helix,
                f"{output_dir}/HA/HA_{(start_index + z):06d}.tif",
                cmap=colormap_angle,
                vmin=-90,
                vmax=90,
            )
            write_img_rgb(
                img_intrusion,
                f"{output_dir}/IA/IA_{(start_index + z):06d}.tif",
                cmap=colormap_angle,
                vmin=-90,
                vmax=90,
            )
            write_img_rgb(
                img_FA,
                f"{output_dir}/FA/FA_{(start_index + z):06d}.tif",
                cmap=colormap_FA,
                vmin=0,
                vmax=1,
            )

        else:
            sys.exit(f"I don't recognise the output_format ({output_format})")


def write_vector_field(
    vector_field_slice: np.ndarray, start_index: int, output_dir: str, slice_idx: int
) -> None:
    """
    Saves a vector field slice to the specified directory in .npy format.

    Args:
        vector_field_slice (np.ndarray): Vector field data slice.
        start_index (int): Starting index for filenames.
        output_dir (str): Directory to save the vector field.
        slice_idx (int): Current slice index.

    Returns:
        None
    """
    os.makedirs(f"{output_dir}/eigen_vec", exist_ok=True)
    np.save(
        f"{output_dir}/eigen_vec/eigen_vec_{(start_index + slice_idx):06d}.npy",
        vector_field_slice,
    )
    # print(f"Vector field slice saved at index {slice_idx}")
