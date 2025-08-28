"""
TODO: I don't like the name nor the
location of this file, but it is here
to encapsulate some functionality 
related to combining video frames.
"""
import numpy as np


def blend_alpha(
    bottom,
    top,
    alpha = 0.5
):
    return (alpha * top + (1 - alpha) * bottom).astype(np.uint8)

def blend_add(
    bottom,
    top
):
    """
    Aclara la imagen combinada, como si superpusieras dos proyectores de luz.
    """
    return np.clip(bottom.astype(np.int16) + top.astype(np.int16), 0, 255).astype(np.uint8)

def blend_multiply(
    bottom,
    top
):
    """
    Oscurece, como proyectar dos transparencias juntas.
    """
    return ((bottom.astype(np.float32) * top.astype(np.float32)) / 255).astype(np.uint8)

def blend_screen(
    bottom,
    top
):
    """
    Hace lo contrario a Multiply, aclara la imagen.
    """
    return (255 - ((255 - bottom.astype(np.float32)) * (255 - top.astype(np.float32)) / 255)).astype(np.uint8)

def blend_overlay(
    bottom,
    top
):
    """
    Mezcla entre Multiply y Screen según el brillo de cada píxel.
    """
    b = bottom.astype(np.float32) / 255
    t = top.astype(np.float32) / 255
    mask = b < 0.5
    result = np.zeros_like(b)
    result[mask] = 2 * b[mask] * t[mask]
    result[~mask] = 1 - 2 * (1 - b[~mask]) * (1 - t[~mask])
    return (result * 255).astype(np.uint8)

def blend_difference(
    bottom,
    top
):
    """
    Resalta las diferencias entre los dos frames.
    """
    return np.abs(bottom.astype(np.int16) - top.astype(np.int16)).astype(np.uint8)

# TODO: This one needs a mask, thats why
# it is commented
# def blend_mask(
#     bottom,
#     top,
#     mask
# ):
#     """
#     En lugar de un alpha fijo, puedes pasar una máscara (por ejemplo, un degradado o un canal alfa real)

#     mask: array float32 entre 0 y 1, mismo tamaño que frame.
#     """
#     return (mask * top + (1 - mask) * bottom).astype(np.uint8)



