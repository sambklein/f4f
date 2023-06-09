import argparse
import os
import pathlib
from hposcripts.hposcripts import generator


def main():
    args = _get_args()
    hpo = generator()

    top_dir = os.path.dirname(os.path.abspath(__file__))
    pyfile = 'run_twobase_cond.py'

    runfile = os.path.join(top_dir, pyfile)
    logdir = os.path.join(top_dir, f'batch/{args.outputname}/')

    sbatch_opts = {
        'job-name': args.outputname,
        'time': args.stime,
        'partition': args.squeue,
        'chdir': logdir,
        'mem': args.smem,
        'gpus': 1,
        # 'exclude' : 'gpu004,gpu005,gpu006,gpu007',
    }

    hpo.set_sbatch_opts(sbatch_opts)

    ###options to test

    # cond = ["'radial'",
    #         "'rotation'"]
    cond = [ "'rotation'"]

    left_data = [
        # "'concentricrings'",
        "'fourcircles'",
        # "'crescentcubed'",
        "'checkerboard'",
        # "'star'",
    ]
    right_data = [
        # "'crescent'",
        "'checkerboard'",
        "'spirals'",
        # "'star'",
        # "'eightstar'",
    ]
    f4f_dir = [
        "'alternate'",
    ]

    penalty = ["None"]
    penalty_weight = ["0"]
    # penalty = ["'l1'", "'l2'"]
    # penalty_weight = ["1", "10", "100"]

    hpo.add_opt('general.n_points', [int(1e5)], True)
    hpo.add_opt('base_dist.left.nepochs', [10], True)
    hpo.add_opt('base_dist.right.nepochs', [10], True)

    # Crescent debugging settings
    # top_dir = '/home/users/k/kleins/scratch/flows4flows/joint_cond_test_crescents/final_r2_0'
    # hpo.add_opt('base_dist.left.load_path',
    #             [f'{top_dir}/base_left/epoch_9_valloss_2.172.pt'],
    #             True)
    # hpo.add_opt('base_dist.right.load_path',
    #             [f'{top_dir}/base_right/epoch_9_valloss_1.148.pt'],
    #             True)
    # hpo.add_opt('top_transformer.load_path',
    #             [f'/home/users/k/kleins/scratch/flows4flows/joint_cond_crescents_fixed/debug_short_1/f4f/epoch_9.pt'],
    #             True)

    hpo.add_opt('top_transformer.nepochs', [10], True)
    hpo.add_opt('base_dist.plot', [1], True)
    hpo.add_opt('general.condition', cond, True)

    hpo.add_opt('base_dist.left.data', left_data, True)
    hpo.add_opt('base_dist.right.data', right_data, True)
    hpo.add_opt('top_transformer.direction', f4f_dir, True)
    hpo.add_opt('top_transformer.penalty', penalty, True)
    hpo.add_opt('top_transformer.penalty_weight', penalty_weight, True)

    hpo.add_script_line('export XDG_RUNTIME_DIR=""')
    hpo.add_script_line('module load GCC/9.3.0 Singularity/3.7.3-Go-1.14', lastline=True)

    # name = hpo.get_name_string(nrandom=args.nrandom)

    cmd = './run_install.sh\n'
    cmd += 'export PYTHONPATH=${PWD}:${PWD}/python_install:${PYTHONPATH}\n'
    cmd += '\nsrun singularity exec --nv'
    if args.singularity_mounts is not None:
        cmd += f' -B {args.singularity_mounts}'
    cmd += f' {args.singularity_instance}\\\n\tpython3 {runfile}\\\n\t\toutput.save_dir={args.outputdir}\\\n\t\toutput.name={args.outputname}_${{SLURM_ARRAY_TASK_ID}}\\\n\t\t'

    pathlib.Path(logdir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.sbatch_output).parent.mkdir(parents=True, exist_ok=True)

    hpo.set_command(cmd)
    hpo.launch(outputfile=args.sbatch_output, submit=args.submit, nrandom=args.nrandom, print=False)

    return


def _get_args():
    parser = argparse.ArgumentParser()

    ##General settings
    parser.add_argument('-d', '--outputdir', type=str,
                        help='Choose the base output directory',
                        required=True)

    parser.add_argument('-n', '--outputname', type=str,
                        help='Set the output name directory',
                        required=True)

    parser.add_argument('--squeue', type=str, default='private-dpnc-gpu,shared-gpu')
    parser.add_argument('--stime', type=str, default='00-12:00:00')
    parser.add_argument('--smem', type=str, default='25GB')

    parser.add_argument('--submit', action='store_true',
                        dest='submit')
    parser.add_argument('--nrandom', type=int, default=-1,
                        help='Run a random grid search with N jobs')

    parser.add_argument('--sbatch-output', type=str, default='gridsearch_submit.txt')

    parser.add_argument('--singularity-instance', type=str,
                        default='/srv/beegfs/scratch/groups/rodem/flows4flows/curtains-flows4flows.simg')
    parser.add_argument('--singularity-mounts', type=str, default='/home,/srv')

    parser.set_defaults(submit=False)
    return parser.parse_args()


if __name__ == '__main__':
    main()
