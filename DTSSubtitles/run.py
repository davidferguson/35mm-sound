import click
import sys
import os

from utils import get_header
from sbt import SbtFile

@click.group()
@click.argument('sbt', type=click.File('rb'))
@click.pass_context
def cli(ctx, sbt):
    '''Program for working with DTS SBT files'''
    ctx.ensure_object(dict)
    ctx.obj['sbt'] = sbt

@cli.command('info')
@click.pass_context
def info_cmd(ctx):
    '''Prints information about the provided SBT file'''
    parsed = SbtFile()
    parsed.from_file(ctx.obj['sbt'])
    parsed.print_info()

@cli.command('show')
@click.argument('reel', type=click.INT)
@click.argument('frame', type=click.INT)
@click.pass_context
def show_cmd(ctx, reel, frame):
    '''Displays the subtitle image at a given reel and frame number'''
    parsed = SbtFile()
    parsed.from_file(ctx.obj['sbt'])
    gen = parsed.get_subs_img(reel, frame, reel, frame)
    try:
        img, reel, frame = next(gen)
        img.show()
    except StopIteration:
        print('No subtitle exists at that location')

@cli.command('save')
@click.argument('reel', type=click.INT)
@click.argument('frame', type=click.INT)
@click.argument('output', type=click.STRING)
@click.pass_context
def save_cmd(ctx, reel, frame, output):
    '''Saves the subtitle image at a given reel and frame number'''
    parsed = SbtFile()
    parsed.from_file(ctx.obj['sbt'])
    gen = parsed.get_subs_img(reel, frame, reel, frame)
    try:
        img, reel, frame = next(gen)
        img.save(output)
    except StopIteration:
        print('No subtitle exists at that location')

@cli.command('export')
@click.argument('outdir', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True))
@click.option('--imgext', default='png', show_default=True, type=click.Choice(['png', 'jpeg']), help='The extension of the images to be saved')
@click.option('--startreel', default=1, show_default=True, type=click.INT, help='The reel number to start the export from')
@click.option('--startframe', default=1, show_default=True, type=click.INT, help='The frame number to start the export from')
@click.option('--endreel', default=13, show_default=True, type=click.INT, help='The reel number to end the export at')
@click.option('--endframe', default=2**16, show_default=True, type=click.INT, help='The frame number to end the export at')
@click.pass_context
def export_cmd(ctx, imgext, outdir, startreel, startframe, endreel, endframe):
    '''Exports all subtitle images between a start and end point'''
    parsed = SbtFile()
    parsed.from_file(ctx.obj['sbt'])
    for img, reel, frame in parsed.get_subs_img(startreel, startframe, endreel, endframe):
        name = '%02d_%05d.%s' % (reel, frame, imgext)
        path = os.path.join(outdir, name)
        img.save(path)
        print('written image file "%s"' % name)

if __name__ == '__main__':
    cli()
