# -*- coding: utf-8 -*-

"""Test colors."""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import colorcet as cc
import numpy as np
from numpy.testing import assert_almost_equal as ae

from phylib.utils import Bunch
from .._color import (
    _is_bright, _random_bright_color, _spike_colors, add_alpha, selected_cluster_color,
    _hex_to_triplet, _continuous_colormap, _categorical_colormap, ClusterColorSelector,
    colormaps, _add_selected_clusters_colors)


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------

def test_random_color():
    for _ in range(10):
        assert _is_bright(_random_bright_color())


def test_hex_to_triplet():
    assert _hex_to_triplet('#0123ab')


def test_add_alpha():
    assert add_alpha((0, .5, 1), .75) == (0, .5, 1, .75)
    assert add_alpha(np.random.rand(5, 3), .5).shape == (5, 4)


def test_selected_cluster_color():
    c = selected_cluster_color(0)
    assert isinstance(c, tuple)
    assert len(c) == 4


def test_spike_colors():
    assert _spike_colors([0, 1, 10, 1000]).shape == (4, 4)
    assert _spike_colors([0, 1, 10, 1000],
                         alpha=1.).shape == (4, 4)
    assert _spike_colors([0, 1, 10, 1000],
                         masks=np.linspace(0., 1., 4)).shape == (4, 4)
    assert _spike_colors(masks=np.linspace(0., 1., 4)).shape == (4, 4)


def test_colormaps():
    colormap = np.array(cc.glasbey_bw_minc_20_minl_30)
    values = np.random.randint(10, 20, size=100)
    colors = _categorical_colormap(colormap, values)
    assert colors.shape == (100, 3)

    colormap = np.array(cc.rainbow_bgyr_35_85_c73)
    values = np.linspace(0, 1, 100)
    colors = _continuous_colormap(colormap, values)
    assert colors.shape == (100, 3)


def test_cluster_color_selector():
    # Mock ClusterMeta instance, with 'fields' property and get(field, cluster) function.
    cluster_meta = Bunch(fields=('label',), get=lambda f, cl: {1: 10, 2: 20, 3: 30}[cl])
    cluster_metrics = {'quality': lambda c: c * .1}
    cluster_ids = [1, 2, 3]
    c = ClusterColorSelector(
        cluster_meta=cluster_meta,
        cluster_metrics=cluster_metrics,
        cluster_ids=cluster_ids,
    )

    assert len(c.get(1, alpha=.5)) == 4
    ae(c.get_values([None, 0]), np.arange(2))

    for field, colormap in (
            ('label', 'linear'),
            ('quality', 'rainbow'),
            ('cluster', 'categorical'),
            ('nonexisting', 'diverging')):
        c.set_color_mapping(field=field, colormap=colormap)
        colors = c.get_colors(cluster_ids)
        assert colors.shape == (3, 4)

    # Get the state.
    assert c.state == {'color_field': 'nonexisting', 'colormap': 'diverging', 'categorical': True}

    # Set the state.
    state = Bunch(c.state)
    state.color_field = 'label'
    state.colormap = colormaps.rainbow
    state.categorical = False
    c.set_state(state)

    # Check that the state was correctly set.
    assert c._color_field == 'label'
    ae(c._colormap, colormaps.rainbow)
    assert c._categorical is False


def test_cluster_color_group():
    # Mock ClusterMeta instance, with 'fields' property and get(field, cluster) function.
    cluster_meta = Bunch(fields=('group',), get=lambda f, cl: {1: None, 2: 'mua', 3: 'good'}[cl])
    cluster_ids = [1, 2, 3]
    c = ClusterColorSelector(
        cluster_meta=cluster_meta,
        cluster_ids=cluster_ids,
    )

    c.set_color_mapping(field='group', colormap='cluster_group')
    colors = c.get_colors(cluster_ids)
    assert colors.shape == (3, 4)


def test_add_selected_clusters_colors():
    cluster_colors = np.tile(np.c_[np.arange(3)], (1, 3))
    cluster_colors = add_alpha(cluster_colors)
    cluster_colors_sel = _add_selected_clusters_colors([1], [0, 1, 3], cluster_colors)
    ae(cluster_colors_sel[[0]], add_alpha(np.zeros((1, 3))))
    ae(cluster_colors_sel[[2]], add_alpha(2 * np.ones((1, 3))))
    # Cluster at index 0 is selected, should be in blue.
    r, g, b, _ = cluster_colors_sel[1]
    assert b > g > r
