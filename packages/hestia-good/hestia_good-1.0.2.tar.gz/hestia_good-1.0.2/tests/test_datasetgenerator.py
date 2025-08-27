import os.path as osp

import numpy as np
import pandas as pd

from hestia import HestiaGenerator, SimArguments


def test_hdg_ccpart():
    df = pd.read_csv(osp.join(osp.dirname(__file__), 'biogen_logS.csv'))
    hdg = HestiaGenerator(df)
    mol_args = SimArguments(
        data_type='small molecule',
        field_name='SMILES',
        fingeprint='ecfp',
        radius=2,
        bits=2048,
        verbose=0
    )
    hdg.calculate_partitions(
        sim_args=mol_args,
        min_threshold=0.1,
        threshold_step=0.1,
        test_size=0.2,
        verbose=0,
        valid_size=0.1,
        partition_algorithm='ccpart'
    )

    parts = hdg.get_partition('min', filter=0.185)
    assert len(set(parts[1]['train']) & set(parts[1]['test'])) == 0
    assert len(set(parts[1]['train']) & set(parts[1]['valid'])) == 0
    assert len(set(parts[1]['valid']) & set(parts[1]['test'])) == 0


def test_hdg_graphpart():
    df = pd.read_csv(osp.join(osp.dirname(__file__), 'biogen_logS.csv'))
    hdg = HestiaGenerator(df)
    mol_args = SimArguments(
        data_type='small molecule',
        field_name='SMILES',
        fingeprint='ecfp',
        radius=2,
        bits=2048,
        verbose=0
    )
    hdg.calculate_partitions(
        sim_args=mol_args,
        min_threshold=0.1,
        threshold_step=0.1,
        test_size=0.2,
        verbose=0,
        valid_size=0.1,
        partition_algorithm='graph_part'
    )

    parts = hdg.get_partition('min', filter=0.185)
    assert len(set(parts[1]['train']) & set(parts[1]['test'])) == 0
    assert len(set(parts[1]['train']) & set(parts[1]['valid'])) == 0
    assert len(set(parts[1]['valid']) & set(parts[1]['test'])) == 0


def test_statstical_test():
    model_results = {
        'ecfp:2-1024': [0.8977702729934635, 0.8943281610083677,0.8757335346731827,
                        0.8983843611901466, 0.8683031815495321,0.8733447668526585,
                        0.8870176873540637, 0.9071866896596464,0.868609279318446,
                        0.8740081648260972, 0.8977811345178581,0.8874742729601423,
                        0.8957698647973106, 0.8979619241987561,0.8925127090816556,
                        0.9344516325004248, 0.9203574993133862,0.8947493099499829,
                        0.9175658635604194, 0.9236097500525624,0.95848592158221,
                        0.9602531574269354, 0.9310141523372284,0.9373339406934652,
                        0.969459096045633, 0.945634771936774, 0.975789549437233,
                        0.9713932298786656, 0.9351896366169516, 0.943822438708775,
                        0.9450577939785392, 0.966257429690424, 0.9258755836477696,
                        0.9675502756033236, 0.9741305192490324],
        'MolFormer': [0.9039158294725392, 0.8964922087522572, 0.9205015222454348,
                      0.9236977230284988, 0.9121314770093552, 0.930591012756282,
                      0.9151172959628447, 0.9234917786392768, 0.9053216213661206,
                      0.9324689108540672, 0.90498628638003, 0.911256326467234,
                      0.9076780931375084, 0.8902636875832343, 0.9119186702371316,
                      0.9675130644530784, 0.9445971522873003, 0.966228366063067,
                      0.9618755132240792, 0.95367030742829, 0.9681895637043574,
                      0.9784297527572864, 0.9733951137908984, 0.9796000516474068,
                      0.9948695846702508, 0.9828458951208664, 0.9750480110673216,
                      0.9823335091112269, 0.9933799655648556, 0.9777482236822896,
                      0.975459978426222, 0.9826620632097848, 0.9705715584795264,
                      0.9861668486739892, 0.9710973132511754],
        'ChemBERTa': [0.931725555985716, 0.9399198368200464, 0.9319553921861384,
                      0.9327598971602472, 0.9232211490511064, 0.9146937839830148,
                      0.939771666133736, 0.9304090638876604, 0.9378888178639172,
                      0.9278011002597496, 0.903681846047976, 0.9061579318861388,
                      0.9124073577514482, 0.9120682776930104, 0.9063338806762192,
                      0.9616478032609608, 0.963218070653128, 0.9609226757999556,
                      0.9561422333207096, 0.959672789429146, 0.979182883938292,
                      0.9772462133711494, 0.978647105064495, 0.9898815887496202,
                      0.9775342993097126, 0.9769754125763296, 0.9777033655182144,
                      0.9760160455266264, 0.9746604158175146, 0.990689212080032,
                      0.9761423297987252, 0.9695975419670868, 0.9705329429555928,
                      0.9851714225104776, 0.9774667382817904]
    }
    matrix = HestiaGenerator.compare_models(
        model_results,
        statistical_test='wilcoxon'
    )
    objective = np.array([
        [1., 0.9999, 1.],
        [1.251*1e-9, 1., 0.93662],
        [2.9103*1e-11, 6.54773*1e-2, 1.]]
    )
    np.testing.assert_allclose(matrix, objective, rtol=1e-3)
