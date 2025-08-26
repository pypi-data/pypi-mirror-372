import warnings
import gc
import pathlib
import os
from typing import List, Union, Callable

import numpy as np
import scipy.signal
import cupy as cp
import cupyx
import cupyx.scipy.ndimage
from pydantic import BaseModel, ValidationError
from tqdm.auto import tqdm
import h5py

from .warp import warp_volume
from .utils import create_rgb_video, mips_callback
from .ndimage import (
    accumarray,
    dogfilter,
    gausskernel_sheared,
    infill_nans,
    ndwindow,
    periodic_smooth_decomposition_nd_rfft,
    sliding_block,
    upsampled_dft_rfftn,
    soften_edges,
)

_ArrayType = Union[np.ndarray, cp.ndarray]

class WarpMap:
    """Represents a 3D displacement field

    Args:
        warp_field (numpy.array): the displacement field data (3-x-y-z)
        block_size (3-element list or numpy.array):
        block_stride (3-element list or numpy.array):
        ref_shape (tuple): shape of the reference volume
        mov_shape (tuple): shape of the moving volume
    """

    def __init__(self, warp_field, block_size, block_stride, ref_shape, mov_shape):
        self.warp_field = cp.array(warp_field, dtype="float32")
        self.block_size = cp.array(block_size, dtype="float32")
        self.block_stride = cp.array(block_stride, dtype="float32")
        self.ref_shape = ref_shape
        self.mov_shape = mov_shape

    def warp(self, vol, out=None):
        """Apply the warp to a volume. Can be thought of as pulling the moving volume to the fixed volume space.

        Args:
            vol (cupy.array): the volume to be warped

        Returns:
            cupy.array: warped volume
        """
        if np.any(vol.shape != np.array(self.mov_shape)):
            warnings.warn(f"Volume shape {vol.shape} does not match the expected shape {self.mov_shape}.")
        if out is None:
            out = cp.zeros(self.ref_shape, dtype="float32", order="C")
        vol_out = warp_volume(
            vol, self.warp_field, self.block_stride, cp.array(-self.block_size / self.block_stride / 2), out=out
        )
        return vol_out

    def apply(self, *args, **kwargs):
        """Alias of warp method"""
        return self.warp(*args, **kwargs)

    def fit_affine(self, target=None):
        """Fit affine transformation and return new fitted WarpMap

        Args:
            target (dict): dict with keys "blocks_shape", "block_size", and "block_stride"

        Returns:
            WarpMap:
            numpy.array: affine tranformation coefficients
        """
        if target is None:
            warp_field_shape = self.warp_field.shape
            block_size = self.block_size
            block_stride = self.block_stride
        else:
            warp_field_shape = target["warp_field_shape"]
            block_size = cp.array(target["block_size"]).astype("float32")
            block_stride = cp.array(target["block_stride"]).astype("float32")

        ix = cp.indices(self.warp_field.shape[1:]).reshape(3, -1).T
        ix = ix * self.block_stride + self.block_size / 2
        M = cp.zeros(self.warp_field.shape[1:])
        #M[1:-1, 1:-1, 1:-1] = 1
        M[:,:,:] = 1
        ixg = cp.where(M.flatten() > 0)[0]
        a = cp.hstack([ix[ixg], cp.ones((len(ixg), 1))])
        b = ix[ixg] + self.warp_field.reshape(3, -1).T[ixg]
        coeff = cp.linalg.lstsq(a, b, rcond=None)[0]
        ix_out = cp.indices(warp_field_shape[1:]).reshape(3, -1).T * block_stride + block_size / 2
        linfit = ((ix_out @ (coeff[:3] - cp.eye(3))) + coeff[3]).T.reshape(warp_field_shape)
        return WarpMap(linfit, block_size, block_stride, self.ref_shape, self.mov_shape), coeff

    def median_filter(self):
        """Apply median filter to the displacement field

        Returns:
            WarpMap: new WarpMap with median filtered displacement field
        """
        warp_field = cupyx.scipy.ndimage.median_filter(self.warp_field, size=[1, 3, 3, 3], mode="nearest")
        return WarpMap(warp_field, self.block_size, self.block_stride, self.ref_shape, self.mov_shape)

    def resize_to(self, target):
        """Resize to target WarpMap, using linear interpolation

        Args:
            target (WarpMap or WarpMapper): target to resize to
                or a dict with keys "shape", "block_size", and "block_stride"

        Returns:
            WarpMap: resized WarpMap
        """
        if isinstance(target, WarpMap):
            t_sh, t_bsz, t_bst = target.warp_field.shape[1:], target.block_size, target.block_stride
        elif isinstance(target, WarpMapper):
            t_sh, t_bsz, t_bst = target.blocks_shape[:3], cp.array(target.block_size), cp.array(target.block_stride)
        elif isinstance(target, dict):
            t_sh, t_bsz, t_bst = (
                target["warp_field_shape"][1:],
                cp.array(target["block_size"]),
                cp.array(target["block_stride"]),
            )
        else:
            raise ValueError("target must be a WarpMap, WarpMapper, or dict")
        ix = cp.array(cp.indices(t_sh).reshape(3, -1))
        # ix = (ix + 0.5) / cp.array(self.block_size / t_bsz)[:, None] - 0.5
        ix = (ix * t_bst[:, None] + (t_bsz - self.block_size)[:, None] / 2) / self.block_stride[:, None]
        dm_r = cp.array(
            [
                cupyx.scipy.ndimage.map_coordinates(cp.array(self.warp_field[i]), ix, mode="nearest", order=1).reshape(
                    t_sh
                )
                for i in range(3)
            ]
        )
        return WarpMap(dm_r, t_bsz, t_bst, self.ref_shape, self.mov_shape)

    def chain(self, target):
        """Chain displacement maps

        Args:
            target (WarpMap): WarpMap to be added to existing map

        Returns:
            WarpMap: new WarpMap with chained displacement field
        """
        indices = cp.indices(target.warp_field.shape[1:])
        warp_field = self.warp_field.copy()
        warp_field += target.warp_field
        return WarpMap(warp_field, target.block_size, target.block_stride, self.ref_shape, self.mov_shape)

    def invert(self, **kwargs):
        """alias for invert_fast method"""
        return self.invert_fast(**kwargs)

    def invert_fast(self, sigma=0.5, truncate=20):
        """Invert the displacement field using accumulation and Gaussian basis interpolation.

        Args:
            sigma (float): standard deviation for Gaussian basis interpolation
            truncate (float): truncate parameter for Gaussian basis interpolation

        Returns:
            WarpMap: inverted WarpMap
        """
        warp_field = self.warp_field.get()
        target_coords = np.indices(warp_field.shape[1:]) + warp_field / self.block_stride[:, None, None, None].get()
        wf_shape = np.ceil(np.array(self.mov_shape) / self.block_stride.get() + 1).astype("int")
        num_coords = accumarray(target_coords, wf_shape)
        inv_field = np.zeros((3, *wf_shape), dtype=warp_field.dtype)
        for i in range(3):
            inv_field[i] = -accumarray(target_coords, wf_shape, weights=warp_field[i].ravel())
            with np.errstate(invalid="ignore"):
                inv_field[i] /= num_coords
            inv_field[i][num_coords == 0] = np.nan
            inv_field[i] = infill_nans(inv_field[i], sigma=sigma, truncate=truncate)
        return WarpMap(inv_field, self.block_size, self.block_stride, self.mov_shape, self.ref_shape)

    def push_coordinates(self, coords, negative_shifts=False):
        """Push voxel coordinates from fixed to moving space.

        Args:
            coords (numpy.array): 3D *voxel* coordinates to be warped (3-by-n array)

        Returns:
            numpy.array: transformed voxel coordinates
        """
        assert coords.shape[0] == 3
        coords = cp.array(coords, dtype="float32")
        # coords_blocked = coords / self.block_size[:, None] - 0.5
        coords_blocked = coords / self.block_stride[:, None] - (self.block_size / (2 * self.block_stride))[:, None]
        warp_field = self.warp_field.copy()
        shifts = cp.zeros_like(coords)
        for idim in range(3):
            shifts[idim] = cupyx.scipy.ndimage.map_coordinates(
                warp_field[idim], coords_blocked, order=1, mode="nearest"
            )
        if negative_shifts:
            shifts = -shifts
        return coords + shifts

    def pull_coordinates(self, coords):
        """Pull voxel coordinates through the warp field. Involves inversion, followed by pushing coordinates.

        Args:
            coords (numpy.array): 3D *voxel* coordinates to be warped (3-by-n array)

        Returns:
            numpy.array: transformed voxel coordinates
        """
        return self.invert().push_coordinates(coords, negative_shifts=True)

    def jacobian_det(self, units_per_voxel=[1, 1, 1], edge_order=1):
        """
        Compute det J = det(∇φ) for φ(x)=x+u(x), using np.indices for the identity grid.

        Args:
            edge_order : passed to np.gradient (1 or 2)

        Returns:
            detJ: cp.ndarray of shape spatial
        """
        scaling = cp.array(units_per_voxel, dtype="float32") * self.block_stride
        coords = cp.indices(self.warp_field.shape[1:], dtype="float32") * scaling[:, None, None, None]
        phi = coords + self.warp_field
        J = cp.empty(self.warp_field.shape[1:] + (3, 3), dtype="float32")
        for i in range(3):
            grads = cp.gradient(phi[i], *scaling, edge_order=edge_order)
            for j in range(3):
                J[..., i, j] = grads[j]
        return cp.linalg.det(J)

    def as_ants_image(self, voxel_size_um=1):
        """Convert to ANTsImage

        Args:
            voxel_size_um (scalar or array): voxel size (default is 1)

        Returns:
            ants.core.ants_image.ANTsImage:
        """
        try:
            import ants
        except ImportError:
            raise ImportError("ANTs is not installed. Please install it using 'pip install ants'")

        ants_image = ants.from_numpy(
            self.warp_field.get().transpose(1, 2, 3, 0),
            origin=list((self.block_size.get() - 1) / 2 * voxel_size_um),
            spacing=list(self.block_stride.get() * voxel_size_um),
            has_components=True,
        )
        return ants_image

    def __repr__(self):
        """String representation of the WarpMap object."""
        info = (
            f"WarpMap("
            f"warp_field_shape={self.warp_field.shape}, "
            f"block_size={self.block_size.get()}, "
            f"block_stride={self.block_stride.get()}, "
            f"transformation: {str(self.mov_shape)} --> {str(self.ref_shape)}"
        )
        return info

    def to_h5(self, h5_path, group="warp_map", compression="gzip", overwrite=True):
        """
        Save this WarpMap to an HDF5 file.

        Args:
            h5_path (str or os.PathLike): Path to the HDF5 file.
            group (str): Group path inside the HDF5 file to store the WarpMap (created if missing).
            compression (str or None): Dataset compression (e.g., 'gzip', None).
            overwrite (bool): If True, overwrite existing datasets/attrs inside the group.
        """
        with h5py.File(h5_path, "a") as f:
            if overwrite and (group not in (None, "", "/")) and (group in f):
                del f[group]
            if (not overwrite) and (group in f):
                raise ValueError(f"Group '{group}' already exists in {h5_path}. Set 'overwrite=True' to overwrite it.")
            grp = f.require_group(group) if group not in (None, "", "/") else f
            grp.create_dataset("warp_field", data=self.warp_field.get(), compression=compression)
            grp.create_dataset("block_size", data=self.block_size.get())
            grp.create_dataset("block_stride", data=self.block_stride.get())
            grp.create_dataset("ref_shape", data=np.array(self.ref_shape, dtype="int64"))
            grp.create_dataset("mov_shape", data=np.array(self.mov_shape, dtype="int64"))
            grp.attrs["class"] = "WarpMap"

    @classmethod
    def from_h5(cls, h5_path, group="warp_map"):
        """
        Load a WarpMap from an HDF5 file.

        Args:
            h5_path (str or os.PathLike): Path to the HDF5 file.
            group (str): Group path inside the HDF5 file where the WarpMap is stored.

        Returns:
            WarpMap: The loaded WarpMap object.
        """
        with h5py.File(h5_path, "r") as f:
            grp = f[group]
            warp_field = grp["warp_field"][:]
            block_size = grp["block_size"][:]
            block_stride = grp["block_stride"][:]
            ref_shape = tuple(grp["ref_shape"][:].tolist())
            mov_shape = tuple(grp["mov_shape"][:].tolist())
        return cls(warp_field, block_size, block_stride, ref_shape, mov_shape)


class WarpMapper:
    """Class that estimates warp field using cross-correlation, based on a piece-wise rigid model.

    Args:
        ref_vol (numpy.array): The reference volume
        block_size (3-element list or numpy.array): shape of blocks, whose rigid displacement is estimated
        block_stride (3-element list or numpy.array): stride (usually identical to block_size)
        proj_method (str or callable): Projection method
    """

    def __init__(
        self, ref_vol, block_size, block_stride=None, proj_method=None, subpixel=4, epsilon=1e-6, tukey_alpha=0.5
    ):
        if np.any(block_size > np.array(ref_vol.shape)):
            raise ValueError(f"Block size (currently: {block_size}) must be smaller than the volume shape ({np.array(ref_vol.shape)}).")
        self.proj_method = proj_method
        self.plan_rev = [None, None, None]
        self.subpixel = subpixel
        self.epsilon = epsilon
        self.tukey_alpha = tukey_alpha
        self.update_reference(ref_vol, block_size, block_stride)
        self.ref_shape = np.array(ref_vol.shape)

    def update_reference(self, ref_vol, block_size, block_stride=None):
        ft = lambda arr: cp.fft.rfftn(arr, axes=(-2, -1))
        block_size = np.array(block_size)
        block_stride = block_size if block_stride is None else np.array(block_stride)
        ref_blocks = sliding_block(cp.array(ref_vol), block_size=block_size, block_stride=block_stride)
        self.blocks_shape = ref_blocks.shape
        ref_blocks_proj = [self.proj_method(ref_blocks, axis=iax) for iax in [-3, -2, -1]]
        if self.tukey_alpha < 1:
            ref_blocks_proj = [
                ref_blocks_proj[i]
                * cp.array(
                    ndwindow(
                        [1, 1, 1, *ref_blocks_proj[i].shape[-2:]], lambda n: scipy.signal.windows.tukey(n, alpha=0.5)
                    )
                ).astype("float32")
                for i in range(3)
            ]
        self.plan_fwd = [
            cupyx.scipy.fft.get_fft_plan(ref_blocks_proj[i], axes=(-2, -1), value_type="R2C") for i in range(3)
        ]
        self.ref_blocks_proj_ft_conj = [
            cupyx.scipy.fft.rfftn(ref_blocks_proj[i], axes=(-2, -1), plan=self.plan_fwd[i]).conj() for i in range(3)
        ]
        self.block_size = block_size
        self.block_stride = block_stride

    def get_displacement(self, vol, smooth_func=None):
        """Estimate the displacement of vol with the reference volume, via piece-wise rigid cross-correlation with the pre-saved blocks.

        Args:
            vol (numpy.array): Input volume
            smooth_func (callable): Smoothing function to be applied to the cross-correlation volume

        Returns:
            WarpMap
        """
        vol_blocks = sliding_block(vol, block_size=self.block_size, block_stride=self.block_stride)
        vol_blocks_proj = [self.proj_method(vol_blocks, axis=iax) for iax in [-3, -2, -1]]
        del vol_blocks

        disp_field = []
        for i in range(3):
            R = (
                cupyx.scipy.fft.rfftn(vol_blocks_proj[i], axes=(-2, -1), plan=self.plan_fwd[i])
                * self.ref_blocks_proj_ft_conj[i]
            )
            if self.plan_rev[i] is None:
                self.plan_rev[i] = cupyx.scipy.fft.get_fft_plan(R, axes=(-2, -1), value_type="C2R")
            xcorr_proj = cp.fft.fftshift(cupyx.scipy.fft.irfftn(R, axes=(-2, -1), plan=self.plan_rev[i]), axes=(-2, -1))
            if smooth_func is not None:
                xcorr_proj = smooth_func(xcorr_proj, self.block_size)
            xcorr_proj[..., xcorr_proj.shape[-2] // 2, xcorr_proj.shape[-1] // 2] += self.epsilon

            max_ix = cp.array(cp.unravel_index(cp.argmax(xcorr_proj, axis=(-2, -1)), xcorr_proj.shape[-2:]))
            max_ix = max_ix - cp.array(xcorr_proj.shape[-2:])[:, None, None, None] // 2
            del xcorr_proj
            i0, j0 = max_ix.reshape(2, -1)
            shifts = upsampled_dft_rfftn(
                R.reshape(-1, *R.shape[-2:]),
                upsampled_region_size=int(self.subpixel * 2 + 1),
                upsample_factor=self.subpixel,
                axis_offsets=(i0, j0),
            )
            del R
            max_sub = cp.array(cp.unravel_index(cp.argmax(shifts, axis=(-2, -1)), shifts.shape[-2:]))
            max_sub = (
                max_sub.reshape(max_ix.shape) - cp.array(shifts.shape[-2:])[:, None, None, None] // 2
            ) / self.subpixel
            del shifts
            disp_field.append(max_ix + max_sub)

        disp_field = cp.array(disp_field)
        disp_field = (
            cp.array(
                [
                    disp_field[1, 0] + disp_field[2, 0],
                    disp_field[0, 0] + disp_field[2, 1],
                    disp_field[0, 1] + disp_field[1, 1],
                ]
            ).astype("float32")
            / 2
        )
        return WarpMap(disp_field, self.block_size, self.block_stride, self.ref_shape, vol.shape)


class RegistrationPyramid:
    """A class for performing multi-resolution registration.

    Args:
        ref_vol (numpy.array): Reference volume
        settings (pandas.DataFrame): Settings for each level of the pyramid.
            IMPORTANT: the block sizea in the last level cannot be larger than the block_size in any previous level.
        reg_mask (numpy.array): Mask for registration
        clip_thresh (float): Threshold for clipping the reference volume
    """

    def __init__(self, ref_vol, recipe, reg_mask=1):
        recipe.model_validate(recipe.model_dump())
        self.recipe = recipe
        self.reg_mask = cp.array(reg_mask, dtype="float32", copy=False, order="C")
        self.mappers = []
        ref_vol = cp.array(ref_vol, dtype="float32", copy=False, order="C")
        self.ref_shape = ref_vol.shape
        if self.recipe.pre_filter is not None:
            ref_vol = self.recipe.pre_filter(ref_vol, reg_mask=self.reg_mask)
        self.mapper_ix = []
        for i in range(len(recipe.levels)):
            if recipe.levels[i].repeats < 1:
                continue
            block_size = np.array(recipe.levels[i].block_size)
            tmp = np.r_[ref_vol.shape] // -block_size
            block_size[block_size < 0] = tmp[block_size < 0]
            if isinstance(recipe.levels[i].block_stride, (int, float)):
                block_stride = (block_size * recipe.levels[i].block_stride).astype("int")
            else:
                block_stride = np.array(recipe.levels[i].block_stride)
            self.mappers.append(
                WarpMapper(
                    ref_vol,
                    block_size,
                    block_stride=block_stride,
                    proj_method=recipe.levels[i].project,
                    tukey_alpha=recipe.levels[i].tukey_ref,
                )
            )
            self.mapper_ix.append(i)
        assert len(self.mappers) > 0, "At least one level of registration is required"

    def register_single(self, vol, callback=None, verbose=False):
        """Register a single volume to the reference volume.

        Args:
            vol (array_like): Volume to be registered (numpy or cupy array)
            callback (function): Callback function to be called after each level of registration

        Returns:
            - vol (array_like): Registered volume (numpy or cupy array, depending on input)
            - warp_map (WarpMap): Displacement field
            - callback_output (list): List of outputs from the callback function
        """
        was_numpy = isinstance(vol, np.ndarray)
        vol = cp.array(vol, "float32", copy=False, order="C")
        offsets = (cp.array(vol.shape) - cp.array(self.ref_shape)) / 2
        warp_map = WarpMap(offsets[:, None, None, None], cp.ones(3), cp.ones(3), self.ref_shape, vol.shape)
        warp_map = warp_map.resize_to(self.mappers[-1])
        callback_output = []
        vol_tmp0 = self.recipe.pre_filter(vol, reg_mask=self.reg_mask) if self.recipe.pre_filter is not None else vol
        vol_tmp = cp.zeros(self.ref_shape, dtype="float32", order="C")
        warp_map.warp(vol_tmp0, out=vol_tmp)
        min_block_stride = np.min([mapper.block_stride for mapper in self.mappers], axis=0)
        if callback is not None:
            callback_output.append(callback(vol_tmp))

        if np.any(self.mappers[-1].block_stride > min_block_stride[0]):
            warnings.warn(
                "The block stride (in voxels) in the last level should not be larger than the block stride in any previous level (along any axis)."
            )
        for k, mapper in enumerate(tqdm(self.mappers, desc=f"Levels", disable=not verbose)):
            for _ in tqdm(
                range(self.recipe.levels[self.mapper_ix[k]].repeats), leave=False, desc=f"Repeats", disable=not verbose
            ):
                wm = mapper.get_displacement(
                    vol_tmp, smooth_func=self.recipe.levels[self.mapper_ix[k]].smooth  # * self.reg_mask,
                )
                wm.warp_field *= self.recipe.levels[self.mapper_ix[k]].update_rate
                if self.recipe.levels[self.mapper_ix[k]].median_filter:
                    wm = wm.median_filter()
                if self.recipe.levels[self.mapper_ix[k]].affine:
                    if (np.array(mapper.blocks_shape[:3]) < 2).sum() > 1:
                        raise ValueError(
                            f"Affine fit needs at least two axes with at least 2 blocks! Volume shape: {self.ref_shape}; block size: {mapper.block_size}"
                        )
                    wm, _ = wm.fit_affine(
                        target=dict(
                            warp_field_shape=(3, *self.mappers[-1].blocks_shape[:3]),
                            block_size=self.mappers[-1].block_size,
                            block_stride=self.mappers[-1].block_stride,
                        )
                    )
                else:
                    wm = wm.resize_to(self.mappers[-1])

                warp_map = warp_map.chain(wm)
                warp_map.warp(vol_tmp0, out=vol_tmp)
                if callback is not None:
                    # callback_output.append(callback(warp_map.unwarp(vol)))
                    callback_output.append(callback(vol_tmp))
        warp_map.warp(vol, out=vol_tmp)
        if was_numpy:
            vol_tmp = vol_tmp.get()
        return vol_tmp, warp_map, callback_output


def register_volumes(ref, vol, recipe, reg_mask=1, callback=None, verbose=True, video_path=None, vmax=None):
    """Register a volume to a reference volume using a registration pyramid.

    Args:
        ref (numpy.array or cupy.array): Reference volume
        vol (numpy.array or cupy.array): Volume to be registered
        recipe (Recipe): Registration recipe
        reg_mask (numpy.array): Mask to be multiplied with the reference volume. Default is 1 (no mask)
        callback (function): Callback function to be called on the volume after each iteration. Default is None.
            Can be used to monitor and optimize registration. Example: `callback = lambda vol: vol.mean(1).get()`
            (note that `vol` is a 3D cupy array. Use `.get()` to turn the output into a numpy array and save GPU memory).
            Callback outputs for each registration step will be returned as a list.
        verbose (bool): If True, show progress bars. Default is True
        video_path (str): Save a video of the registration process, using callback outputs. The callback has to return 2D frames. Default is None.
        vmax (float): Maximum pixel value (to scale video brightness). If none, set to 99.9 percentile of pixel values.

    Returns:
        - numpy.array or cupy.array (depending on vol input): Registered volume
        - WarpMap: Displacement field
        - list: List of outputs from the callback function
    """
    recipe.model_validate(recipe.model_dump())
    reg = RegistrationPyramid(ref, recipe, reg_mask=reg_mask)
    registered_vol, warp_map, cbout = reg.register_single(vol, callback=callback, verbose=verbose)
    del reg
    gc.collect()
    cp.fft.config.get_plan_cache().clear()

    if video_path is not None:
        try:
            assert cbout[0].ndim == 2, "Callback output must be a 2D array"
            ref = callback(recipe.pre_filter(ref))
            vmax = np.percentile(ref, 99.9).item() if vmax is None else vmax
            create_rgb_video(video_path, ref / vmax, np.array(cbout) / vmax, fps=10)
        except (ValueError, AssertionError) as e:
            warnings.warn(f"Video generation failed with error: {e}")
    return registered_vol, warp_map, cbout


class Projector(BaseModel):
    """A class to apply a 2D projection and filters to a volume block

    Parameters:
        max: if True, apply a max filter to the volume block. Default is True
        normalize: if True, normalize projections by the L2 norm (to get correlations, not covariances). Default is False
        dog: if True, apply a DoG filter to the volume block. Default is True
        low: the lower sigma value for the DoG filter. Default is 0.5
        high: the higher sigma value for the DoG filter. Default is 10.0
        tukey_env: if True, apply a Tukey window to the output. Default is False
        gauss_env: if True, apply a Gaussian window to the output. Default is False
    """

    max: bool = True
    normalize: Union[bool, float] = False
    dog: bool = True
    low: Union[Union[int, float], List[Union[int, float]]] = 0.5
    high: Union[Union[int, float], List[Union[int, float]]] = 10.0
    periodic_smooth: bool = False

    def __call__(self, vol_blocks, axis):
        """Apply a 2D projection and filters to a volume block
        Args:
            vol_blocks (cupy.array): Blocked volume to be projected (6D dataset, with the first 3 dimensions being blocks and the last 3 dimensions being voxels)
            axis (int): Axis along which to project
        Returns:
            cupy.array: Projected volume block (5D dataset, with the first 3 dimensions being blocks and the last 2 dimensions being 2D projections)
        """
        if self.max:
            out = vol_blocks.max(axis)
        else:
            out = vol_blocks.mean(axis)
        if self.periodic_smooth:
            out = periodic_smooth_decomposition_nd_rfft(out)
        low = np.delete(np.r_[1,1,1] * self.low, axis)
        high = np.delete(np.r_[1,1,1] * self.high, axis)
        if self.dog:
            out = dogfilter(out, [0, 0, 0, *low], [0, 0, 0, *high], mode="reflect")
        elif not np.all(np.array(self.low) == 0):
            out = cupyx.scipy.ndimage.gaussian_filter(out, [0, 0, 0, *low], mode="reflect", truncate=5.0)
        if self.normalize > 0:
            out /= cp.sqrt(cp.sum(out**2, axis=(-2, -1), keepdims=True)) ** self.normalize + 1e-9
        return out


class Smoother(BaseModel):
    """Smooth blocks with a Gaussian kernel
    Args:
        sigmas (list): [sigma0, sigma1, sigma2]. If None, no smoothing is applied.
        truncate (float): truncate parameter for gaussian kernel. Default is 5.
        shear (float): shear parameter for gaussian kernel. Default is None.
        long_range_ratio (float): long range ratio for double gaussian kernel. Default is None.
    """

    sigmas: Union[float, List[float]] = [1.0, 1.0, 1.0]
    shear: Union[float, None] = None
    long_range_ratio: Union[float, None] = 0.05

    def __call__(self, xcorr_proj, block_size=None):
        """Apply a Gaussian filter to the cross-correlation data
        Args:
            xcorr_proj (cupy.array): cross-correlation data (5D array, with the first 3 dimensions being the blocks and the last 2 dimensions being the 2D projection)
            block_size (list): shape of blocks, whose rigid displacement is estimated
        Returns:
            cupy.array: smoothed cross-correlation volume
        """
        truncate = 4.0
        if self.sigmas is None:
            return xcorr_proj
        if self.shear is not None:
            shear_blocks = self.shear * (block_size[1] / block_size[0])
            gw = gausskernel_sheared(self.sigma[:2], shear_blocks, truncate=truncate)
            gw = cp.array(gw[:, :, None, None, None])
            xcorr_proj = cupyx.scipy.ndimage.convolve(xcorr_proj, gw, mode="constant")
            xcorr_proj = cupyx.scipy.ndimage.gaussian_filter1d(
                xcorr_proj, self.sigmas[2], axis=2, mode="constant", truncate=truncate
            )
        else:  # shear is None:
            xcorr_proj = cupyx.scipy.ndimage.gaussian_filter(
                xcorr_proj, [*self.sigmas, 0, 0], mode="constant", truncate=truncate
            )
        if self.long_range_ratio is not None:
            xcorr_proj *= 1 - self.long_range_ratio
            xcorr_proj += (
                cupyx.scipy.ndimage.gaussian_filter(
                    xcorr_proj, [*np.array(self.sigmas) * 5, 0, 0], mode="constant", truncate=truncate
                )
                * self.long_range_ratio
            )
        return xcorr_proj


class RegFilter(BaseModel):
    """A class to apply a filter to the volume before registration

    Parameters:
        clip_thresh: threshold for clipping the reference volume. Default is 0
        dog: if True, apply a DoG filter to the volume. Default is True
        low: the lower sigma value for the DoG filter. Default is 0.5
        high: the higher sigma value for the DoG filter. Default is 10.0
    """

    clip_thresh: float = 0
    dog: bool = True
    low: float = 0.5
    high: float = 10.0
    soft_edge: Union[Union[int, float], List[Union[int, float]]] = 0.0

    def __call__(self, vol, reg_mask=None):
        """Apply the filter to the volume
        Args:
            vol (cupy or numpy array): 3D volume to be filtered
            reg_mask (array): Mask for registration
        Returns:
            cupy.ndarray: Filtered volume
        """
        vol = cp.clip(cp.array(vol, "float32", copy=False) - self.clip_thresh, 0, None)
        if np.any(np.array(self.soft_edge) > 0):
            vol = soften_edges(vol, soft_edge=self.soft_edge, copy=False)
        if reg_mask is not None:
            vol *= cp.array(reg_mask, dtype="float32", copy=False)
        if self.dog:
            vol = dogfilter(vol, self.low, self.high, mode="reflect")
        return vol


class LevelConfig(BaseModel):
    """Configuration for each level of the registration pyramid

    Args:
        block_size (list): shape of blocks, whose rigid displacement is estimated
        block_stride (list): stride (usually identical to block_size)
        repeats (int): number of iterations for this level (deisable level by setting repeats to 0)
        smooth (Smoother or None): Smoother object
        project (Projector, callable or None): Projector object. The callable should take a volume block and an axis as input and return a projected volume block.
        tukey_ref (float): if not None, apply a Tukey window to the reference volume (alpha = tukey_ref). Default is 0.5
        affine (bool): if True, apply affine transformation to the displacement field
        median_filter (bool): if True, apply median filter to the displacement field
        update_rate (float): update rate for the displacement field. Default is 1.0. Can be lowered to dampen oscillations.
    """

    block_size: Union[List[int]]
    block_stride: Union[List[int], float] = 1.0
    project: Union[Projector, Callable[[_ArrayType, int], _ArrayType]] = Projector()
    tukey_ref: Union[float, None] = 0.5
    smooth: Union[Smoother, None] = Smoother()
    affine: bool = False
    median_filter: bool = True
    update_rate: float = 1.0
    repeats: int = 5


class Recipe(BaseModel):
    """Configuration for the registration recipe. Recipe is initialized with a single affine level.

    Args:
        reg_filter (RegFilter, callable or None): Filter to be applied to the reference volume
        levels (list): List of LevelConfig objects
    """

    pre_filter: Union[RegFilter, Callable[[_ArrayType], _ArrayType], None] = RegFilter()
    levels: List[LevelConfig] = [
        LevelConfig(block_size=[-1, -1, -1], repeats=3),  # translation level
        LevelConfig(  # affine level
            block_size=[-2, -2, -2],
            block_stride=0.5,
            repeats=10,
            affine=True,
            median_filter=False,
            smooth=Smoother(sigmas=[0.5, 0.5, 0.5]),
        ),
    ]

    def add_level(self, block_size, **kwargs):
        """Add a level to the registration recipe

        Args:
            block_size (list): shape of blocks, whose rigid displacement is estimated
            **kwargs: additional arguments for LevelConfig
        """
        if isinstance(block_size, (int, float)):
            block_size = [block_size] * 3
        if len(block_size) != 3:
            raise ValueError("block_size must be a list of 3 integers")
        self.levels.append(LevelConfig(block_size=block_size, **kwargs))

    def insert_level(self, index, block_size, **kwargs):
        """Insert a level to the registration recipe

        Args:
            index (int): A number specifying in which position to insert the level
            block_size (list): shape of blocks, whose rigid displacement is estimated
            **kwargs: additional arguments for LevelConfig
        """
        if isinstance(block_size, (int, float)):
            block_size = [block_size] * 3
        if len(block_size) != 3:
            raise ValueError("block_size must be a list of 3 integers")
        self.levels.insert(index, LevelConfig(block_size=block_size, **kwargs))

    @classmethod
    def from_yaml(cls, yaml_path):
        """Load a recipe from a YAML file

        Args:
            yaml_path (str): path to the YAML file

        Returns:
            Recipe: Recipe object
        """
        import yaml

        this_file_dir = pathlib.Path(__file__).resolve().parent
        if os.path.isfile(yaml_path):
            yaml_path = yaml_path
        else:
            yaml_path = os.path.join(this_file_dir, "recipes", yaml_path)

        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        return cls.model_validate(data)

    def to_yaml(self, yaml_path):
        """Save the recipe to a YAML file

        Args:
            yaml_path (str): path to the YAML file
        """
        import yaml

        with open(yaml_path, "w") as f:
            yaml.dump(self.model_dump(), f)
        print(f"Recipe saved to {yaml_path}")
