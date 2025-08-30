import pytest

from optiwindnet.api import (
    EWRouter,
    HGSRouter,
    MILPRouter,
    WindFarmNetwork,
    ModelOptions,
)
from .helpers import assert_graph_equal
# ========== Test Routers ==========


@pytest.mark.parametrize(
    'label, router, ignored_keys',
    [
        ('eagle_EWRouter', None, {'runtime'}),
        ('eagle_EWRouter_straight', EWRouter(feeder_route='straight'), {'runtime'}),
        ('taylor_EWRouter', None, {'runtime'}),
        ('taylor_EWRouter_straight', EWRouter(feeder_route='straight'), {'runtime'}),
        (
            'eagle_HGSRouter',
            HGSRouter(time_limit=2, seed=0),
            {'solution_time', 'runtime'},
        ),
        (
            'eagle_HGSRouter_feeder_limit',
            HGSRouter(time_limit=2, feeder_limit=0, seed=0),
            {'solution_time', 'runtime'},
        ),
        (
            'taylor_HGSRouter',
            HGSRouter(time_limit=2, seed=0),
            {'solution_time', 'runtime'},
        ),
        (
            'taylor_HGSRouter_feeder_limit',
            HGSRouter(time_limit=2, feeder_limit=0, seed=0),
            {'solution_time', 'runtime'},
        ),
        (
            'eagle_MILPRouter',
            MILPRouter(solver_name='ortools', time_limit=5, mip_gap=0.005),
            {'runtime', 'bound', 'pool_count', 'relgap', 'solver_details.strategy'},
        ),
    ],
)
def test_router_variants(LG_from_database, label, router, ignored_keys):
    expected_L, G = LG_from_database(label)

    wfn = WindFarmNetwork(
        cables=G.graph['capacity'],
        L=expected_L,
    )

    wfn.optimize(router=router)

    ignored_keys = ignored_keys or set()
    assert_graph_equal(wfn.G, G, ignored_graph_keys=ignored_keys)


@pytest.mark.parametrize(
    'router_class, init_kwargs, expected_attrs',
    [
        # --- EWRouter Tests ---
        (
            EWRouter,
            {},
            {'maxiter': 10000, 'feeder_route': 'segmented', 'verbose': False},
        ),
        (
            EWRouter,
            {'maxiter': 5000, 'feeder_route': 'straight', 'verbose': True},
            {'maxiter': 5000, 'feeder_route': 'straight', 'verbose': True},
        ),
        # --- HGSRouter Tests ---
        (
            HGSRouter,
            {'time_limit': 1},
            {
                'time_limit': 1,
                'max_retries': 10,
                'feeder_limit': None,
                'balanced': False,
                'seed': None,
                'verbose': False,
            },
        ),
        (
            HGSRouter,
            {
                'time_limit': 2,
                'feeder_limit': 3,
                'max_retries': 7,
                'balanced': True,
                'seed': 42,
                'verbose': True,
            },
            {
                'time_limit': 2,
                'feeder_limit': 3,
                'max_retries': 7,
                'balanced': True,
                'seed': 42,
                'verbose': True,
            },
        ),
        # --- MILPRouter Tests ---
        (
            MILPRouter,
            {'solver_name': 'cbc', 'time_limit': 100, 'mip_gap': 0.05},
            {'solver_name': 'cbc', 'time_limit': 100, 'mip_gap': 0.05},
        ),
        (
            MILPRouter,
            {
                'solver_name': 'cbc',
                'time_limit': 200,
                'mip_gap': 0.01,
                'solver_options': {'threads': 2},
                'model_options': ModelOptions(balanced=True),
                'verbose': True,
            },
            {
                'solver_name': 'cbc',
                'time_limit': 200,
                'mip_gap': 0.01,
                'solver_options': {'threads': 2},
                'verbose': True,
            },
        ),
    ],
)
def test_router_initialization(router_class, init_kwargs, expected_attrs):
    router = router_class(**init_kwargs)
    for attr, expected in expected_attrs.items():
        actual = getattr(router, attr)
        if isinstance(expected, dict):
            assert actual == expected
        else:
            assert actual == expected
