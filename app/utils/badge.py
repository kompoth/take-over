"""
Routines to obtain coverage badges
"""

import numpy as np
import webcolors as wc


def rgb_linear_gradient(rgb1, rgb2, arg1, arg2):
    koef = (rgb1 - rgb2) / (arg1 - arg2)
    const = rgb1 - koef * arg1
    return lambda x: np.rint(koef * x + const).astype("int")


def rgb_polylinear_gradient(rgbs, args):
    inds = np.argsort(args)
    args = args[inds]
    rgbs = rgbs[inds]

    arg_pairs = np.repeat(args, 2, axis=0).reshape(-1, 2)[:-1]
    arg_pairs[:, 1] = args[1:]
    rgb_pairs = np.repeat(rgbs, 2, axis=0).reshape(-1, 2, 3)[:-1]
    rgb_pairs[:, 1, :] = rgbs[1:, :]

    grads = np.array(
        [rgb_linear_gradient(*rp, *ap) for rp, ap in zip(rgb_pairs, arg_pairs)]
    )

    def __grad(val):
        mask = np.logical_and(arg_pairs[:, 0] < val, val <= arg_pairs[:, 1])
        return grads[mask][0](val)

    return __grad


def get_gradient(hex_colors, arguments):
    rgbs = np.array([wc.hex_to_rgb(hc) for hc in hex_colors])
    args = np.array(arguments)
    grad = rgb_polylinear_gradient(rgbs, args)
    return lambda x: wc.rgb_to_hex(grad(x))


def get_badge_url(coverage):
    colors = ["#008000", "#ffa500", "#ff0000"]
    arguments = [100, 70, 0]
    gradient = get_gradient(colors, arguments)
    content = f"coverage-{round(coverage, 2)}%25-0"
    base_url = "https://img.shields.io/badge/"
    color = gradient(coverage).replace("#", "")
    return base_url + content + f"?color={color}"
