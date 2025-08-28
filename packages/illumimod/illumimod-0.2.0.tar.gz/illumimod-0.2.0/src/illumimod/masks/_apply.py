import numpy as np
import numpy.typing as npt

def apply(
    img: npt.NDArray,           # (H,W) or (H,W,3)
    mask: npt.NDArray,          # (H,W), same spatial size as img
    *,
    exposure: float = 1.0,
    clip: bool = True,
    out_dtype = np.uint8,
) -> npt.NDArray:
    """
    Add the mask to the image (optionally after an exposure gain), then clip.

    This is an **additive** apply with no automatic scaling. The mask is assumed to be
    in the correct units for the image (e.g., 0–255 for ``uint8`` sRGB). For RGB images,
    the mask is broadcast across channels.

    Parameters
    ----------
    img : ndarray
        Input image, ``(H, W)`` (grayscale) or ``(H, W, 3)`` (RGB).
    mask : ndarray
        Additive mask, shape ``(H, W)``.
    exposure : float, optional
        Global gain applied to the base image before addition (``out = exposure*img + mask``).
    clip : bool, optional
        If ``True``, clamp the result into ``[0, 255]`` for integer inputs, else ``[0, 1]``.
    out_dtype : numpy dtype, optional
        Output dtype (default ``np.uint8``).

    Returns
    -------
    ndarray
        Processed image with the same spatial shape as ``img`` and dtype ``out_dtype``.

    Raises
    ------
    ValueError
        If ``mask`` and ``img`` spatial dimensions differ.

    Notes
    -----
    For more physically plausible results, consider performing apply in **linear light**
    in a future version (convert sRGB ↔ linear around this operation).
    """

    if img.shape[:2] != mask.shape[:2]:
        raise ValueError("apply_additive: mask HxW must match image HxW")

    img_f  = img.astype(np.float32, copy=False)
    add    = mask.astype(np.float32, copy=False)

    # Broadcast to RGB if needed
    if img_f.ndim == 3 and img_f.shape[2] != 1 and add.ndim == 2:
        add = add[..., None]

    out = exposure * img_f + add

    if clip:
        headroom = 255.0 if np.issubdtype(img.dtype, np.integer) else 1.0
        out = np.clip(out, 0.0, headroom)

    return out.astype(out_dtype, copy=False)

# --- sRGB <-> linear helpers (piecewise IEC 61966-2-1) ---
def srgb_to_linear(x):
    x = np.clip(x, 0.0, 1.0)
    a = 0.055
    return np.where(x <= 0.04045, x/12.92, ((x + a)/(1+a))**2.4)

def linear_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    a = 0.055
    return np.where(x <= 0.0031308, 12.92*x, (1+a)*np.power(x, 1/2.4) - a)

def rgb_luma(img):
    if img.ndim == 2: return img
    r,g,b = img[...,0], img[...,1], img[...,2]
    return 0.2126*r + 0.7152*g + 0.0722*b

def apply_physmix(
    img: npt.NDArray,          # uint8 [0..255] or float [0..1], gray or RGB
    mask: npt.NDArray,         # float mask same HxW (irradiance field)
    *,
    illum_strength: float = 1.0,      # β: multiplicative illumination gain
    ambient_add: float = 0.0,         # small additive ambient in linear (0..1)
    spec_strength: float = 0.0,       # γ: extra additive “specular/bloom” from mask
    spec_knee: float = 0.9,           # knee in linear (protects bright regions)
    spec_gamma: float = 1.0,          # shape specular from mask (mask^γ)
    normalize_mask: bool = True,      # normalize mask to [0,1] before use
    clip: bool = True,
    out_dtype = np.uint8,
) -> npt.NDArray:
    """
    Apply a physically-inspired lighting mix to an image using a given irradiance mask.

    This function models illumination as a combination of:
    1. **Multiplicative illumination** — scales linear-light intensity by (1 + β·mask).
    2. **Ambient add** — adds a small constant lift to simulate stray light.
    3. **Specular/bloom add** — adds mask-derived highlights with knee-based headroom
       protection to avoid over-saturation.

    The image is internally converted to linear-light space for correct blending and
    returned in sRGB space.

    Parameters
    ----------
    img : ndarray
        Input image, either grayscale or RGB. Can be:
        - uint8 in [0..255], or
        - float in [0..1].
    mask : ndarray
        Float irradiance mask of shape (H, W) or (H, W, 1). Should match the image’s
        spatial dimensions. Used as the illumination field.
    illum_strength : float, optional
        β: multiplicative illumination strength. Default = 1.0.
    ambient_add : float, optional
        Small additive offset in linear space (0..1). Simulates ambient stray light.
        Default = 0.0.
    spec_strength : float, optional
        γ: strength of additional additive specular/bloom from the mask. Default = 0.0.
    spec_knee : float, optional
        Highlight protection threshold in linear [0..1]. Additive specular is clamped
        to not exceed this knee. Default = 0.9.
    spec_gamma : float, optional
        Exponent shaping for the specular term (mask^γ). Default = 1.0.
    normalize_mask : bool, optional
        If True, normalize the mask to [0,1] before use (treat as shape only). Default = True.
    clip : bool, optional
        If True, clip final output to [0,1] before conversion. Default = True.
    out_dtype : dtype, optional
        Output dtype. If integer (e.g., np.uint8), scales to [0..255]. Default = np.uint8.

    Returns
    -------
    ndarray
        Image array with the same shape as input, with lighting effects applied.
        dtype determined by `out_dtype`.

    Notes
    -----
    - The processing is done in linear-light RGB; conversions to/from sRGB are handled
      internally.
    - When `spec_strength` > 0, the specular term is prevented from blowing out highlights
      by limiting additions so that pixel values remain ≤ `spec_knee`.
    - If the input image is grayscale, the operations are applied directly on intensity.
    """
    if img.shape[:2] != mask.shape[:2]:
        raise ValueError("mask HxW must match image HxW")

    # --- bring to float [0,1] ---
    if np.issubdtype(img.dtype, np.integer):
        img01 = img.astype(np.float32) / 255.0
    else:
        img01 = img.astype(np.float32)

    # Expand mask to HxW or HxWx1 for broadcasting
    m = mask.astype(np.float32)
    if img01.ndim == 3 and m.ndim == 2:
        m = m[..., None]

    # Normalize mask (treat it as an *illumination field shape*, not absolute add)
    if normalize_mask:
        mmax = float(np.max(m)) if np.max(m) > 0 else 1.0
        m = m / mmax

    # --- go to linear light ---
    img_lin = srgb_to_linear(img01)

    # Work in luminance to preserve chroma balance
    Y = rgb_luma(img_lin)
    if img_lin.ndim == 3:
        # build a per-pixel gain map from luminance, but apply it to all channels
        pass

    # 1) Multiplicative illumination (dominant, realistic)
    #    I_lin' = I_lin * (1 + β * m)
    gain = 1.0 + illum_strength * m
    img_lin_mul = img_lin * gain

    # 2) Optional additive ambient (very small; acts like uniform stray light)
    if ambient_add != 0.0:
        img_lin_mul = img_lin_mul + ambient_add

    # 3) Optional additive specular/bloom derived from mask with highlight knee
    #    We allow add only where we have headroom below 'spec_knee'
    if spec_strength > 0.0:
        # spec seed from mask (gamma-shaped)
        spec_seed = np.power(np.clip(m, 0.0, 1.0), spec_gamma)

        # per-pixel maximum add so we don't exceed the knee
        headroom = np.clip(spec_knee - img_lin_mul, 0.0, 1.0)
        spec_add = spec_strength * spec_seed
        # clamp with headroom (broadcast-safe)
        spec_add = np.minimum(spec_add, headroom)
        img_lin_mul = img_lin_mul + spec_add

    # --- back to display space ---
    img_out = linear_to_srgb(img_lin_mul)

    if clip:
        img_out = np.clip(img_out, 0.0, 1.0)

    if np.issubdtype(out_dtype, np.integer):
        return (img_out * 255.0 + 0.5).astype(out_dtype)  # round
    return img_out.astype(out_dtype)
