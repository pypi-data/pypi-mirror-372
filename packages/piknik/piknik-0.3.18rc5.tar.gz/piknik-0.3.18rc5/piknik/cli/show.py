# standard imports
import os
import logging
import importlib
import argparse

# local imports
from piknik import Issue
from piknik.crypto import PGPSigner

ctx = None
accumulator_f = None
accumulator = None

logg = logging.getLogger(__name__)



def set_accumulator(ctx, m, issue_id=None):
    global accumulator_f
    global accumulator
    if ctx.files_dir != None:
        fb = None
        if issue_id == None:
            fb = 'index.html'
        else:
            fb = issue_id + '.html'
        fp = os.path.join(ctx.files_dir, fb)
        accumulator_f = open(fp, 'w')
        accumulator = m.Accumulator(w=accumulator_f)
        return accumulator.add
    return None


def reset_accumulator():
    global accumulator_f
    global accumulator
    if accumulator_f != None:
        accumulator_f.close()
        accumulator_f = None
        issues = accumulator.issues
        accumulator = None
        return issues
    return []


def subparser(argp):
    argp.add_argument('-r', '--renderer', type=str, default='default', help='Renderer module for output')
    argp.add_argument('-s', '--state', type=str, action='append', default=[], help='Limit results to state(s)')
    argp.add_argument('--show-finished', dest='show_finished', action='store_true', help='Include finished issues')
    argp.add_argument('--reverse', action='store_true', help='Sort comments by oldest first')
    return argp


def assembler(o, arg):
    o.renderer = arg.renderer


def main():
    global ctx

    renderer_s = ctx.renderer
    if renderer_s == 'default':
        renderer_s = 'piknik.render.plain'
    elif renderer_s == 'html':
        renderer_s = 'piknik.render.html'

    m = None
    try:
        m = importlib.import_module(renderer_s)
    except ModuleNotFoundError:
        renderer_s = 'piknik.render.' + renderer_s
        m = importlib.import_module(renderer_s)

    accumulator = None
    accumulator_f = None

    issues = []
    if ctx.issue_id:
        issues.append(ctx.issue_id)

    states_skip = []
    if not ctx.show_finished:
        states_skip.append('FINISHED')

    if ctx.issue_id == None:
        accumulator = set_accumulator(ctx, m)
        renderer = m.Renderer(ctx.basket, accumulator=accumulator, states_include=ctx.show_states, states_skip=states_skip)
        renderer.apply()
        issues = reset_accumulator()

    for issue_id in issues:
        accumulator = set_accumulator(ctx, m, issue_id=issue_id)
        issue = ctx.basket.get(issue_id)
        tags = ctx.basket.tags(issue_id)
        state = ctx.basket.get_state(issue_id)
        verifier = PGPSigner(home_dir=ctx.gpg_home, skip_verify=False)
        renderer = m.Renderer(ctx.basket, wrapper=verifier, accumulator=accumulator, states_include=ctx.show_states, states_skip=states_skip)

        renderer.apply_begin()
        renderer.apply_issue_pre(state, issue, tags)
        renderer.apply_issue(state, issue, tags)
        renderer.apply_issue_post(state, issue, tags)
        renderer.apply_end()
        
        reset_accumulator()
