# standard imports
import logging

logg = logging.getLogger(__name__)

ctx = None


def subparser(argp):
    argp.add_argument('--accept', action='store_true', help='Accept proposed issue')
    argp.add_argument('--block', action='store_true', help='Set issue as blocked')
    argp.add_argument('--unblock', action='store_true', help='Set issue as unblocked')
    argp.add_argument('--finish', action='store_true', help='Set issue as finished (alias of -s finish)')
    argp.add_argument('-s', '--state', type=str, help='Move to state')
    argp.add_argument('-t', '--tag', type=str, action='append', default=[], help='Add tag to issue')
    argp.add_argument('-u', '--untag', type=str, action='append', default=[], help='Remove tag from issue')
    #argp.add_argument('-f', '--file', type=str, action='append', help='Add message file part')
    #argp.add_argument('-m', '--message', type=str, action='append', default=[], help='Add message text part')
    argp.add_argument('-a', '--assign', type=str, action='append', default=[], help='Assign given identity to issue')
    argp.add_argument('--unassign', type=str, action='append', default=[], help='Unassign given identity from issue')
    argp.add_argument('--owner', type=str, help='Set given identity as owner of issue')
    argp.add_argument('--dep', action='append', default=[], type=str, help='Set issue dependency')
    argp.add_argument('--undep', action='append', default=[], type=str, help='Remove issue dependency')
    return argp


def assembler(o, arg):
    o.owner = arg.owner
    o.block = arg.block
    o.unblock = arg.unblock
    o.state = arg.state
    o.finish = arg.finish
    o.accept = arg.accept
    o.tag = arg.tag
    o.untag = arg.untag
    o.assign = arg.assign
    o.unassign = arg.unassign
    o.dep = arg.dep
    o.undep = arg.undep


def main():
    global ctx

    o = ctx.basket.get(ctx.issue_id)

    if ctx.block:
        ctx.basket.block(ctx.issue_id)
    elif ctx.unblock:
        ctx.basket.unblock(ctx.issue_id)

    if ctx.state != None:
        m = getattr(ctx.basket, 'state_' + ctx.state)
        m(ctx.issue_id)
    elif ctx.finish:
        ctx.basket.state_finish(ctx.issue_id)
    elif ctx.accept:
        if ctx.basket.get_state(ctx.issue_id) != 'PROPOSED':
            raise ValueError('Issue already accepted')
        ctx.basket.advance(ctx.issue_id)

    for v in ctx.tag:
        ctx.basket.tag(ctx.issue_id, v)

    for v in ctx.untag:
        ctx.basket.untag(ctx.issue_id, v)

    for v in ctx.unassign:
        ctx.basket.unassign(ctx.issue_id, v)

    for v in ctx.assign:
        ctx.basket.assign(ctx.issue_id, v)
 
    for v in ctx.undep:
        ctx.basket.undep(ctx.issue_id, v)

    for v in ctx.dep:
        ctx.basket.dep(ctx.issue_id, v)

    if ctx.owner:
        ctx.basket.owner(ctx.issue_id, ctx.owner)
