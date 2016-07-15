# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt


def add_beautiful_subplot(fig, subplot, xlim, ylim):

    axes = fig.add_subplot(
        subplot, xlim=xlim, ylim=ylim
    )

    for side in ['bottom', 'right', 'top', 'left']:
        axes.spines[side].set_visible(False)

    plt.xlabel('S', fontsize=18)
    plt.ylabel('C', fontsize=18)

    xmin, xmax = axes.get_xbound()
    ymin, ymax = axes.get_ylim()

    head_width = 1. / 50. * (ymax - ymin)
    head_length = 1. / 100. * (xmax - xmin)

    dps = fig.dpi_scale_trans.inverted()
    bbox = axes.get_window_extent().transformed(dps)
    width, height = bbox.width, bbox.height

    yhead_width = 1. / 50. * (xmax - xmin) * height / width
    yhead_length = 1. / 100. * (ymax - ymin) * width / height

    linewidth = 1.
    xwidth = min(1.0, (ymax - ymin) / 1000.)

    axes.arrow(
        xmin, 0, xmax - xmin, 0, linewidth=linewidth, width=xwidth,
        head_width=head_width, head_length=head_length,
        length_includes_head=True, fc='k', ec='k'
    )

    axes.arrow(
        0, ymin, 0, ymax - ymin, linewidth=1.,
        head_width=yhead_width, head_length=yhead_length,
        length_includes_head=True, fc='k', ec='k'
    )
