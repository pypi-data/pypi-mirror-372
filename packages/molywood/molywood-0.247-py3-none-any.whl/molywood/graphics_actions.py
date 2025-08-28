import os
from shutil import copy2
from subprocess import call
from collections import namedtuple
try:
    import numpy as np
except ImportError:
    np = None
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
try:
    import seaborn as sns
except ImportError:
    sns = None


def postprocessor(script):
    """
    This is the key function that controls composition
    of the previously rendered scenes. It first applies
    overlays if requested, and then copies/moves/composes
    individual frames so that an initial set of
    scene1...png, sceneX...png files is converted
    into movie_name...png files that can then
    be merged into a file using ffmpeg.
    :param script: Script instance, the master object controlling the movie layout
    :return: None
    """
    try:
        layout_dirs = script.directives['layout']  # layout controls composition of panels
    except KeyError:
        layout_dirs = None
        nrows = 1
        ncols = 1
    else:
        nrows = int(layout_dirs['rows']) if 'rows' in layout_dirs.keys() else 1
        ncols = int(layout_dirs['columns']) if 'columns' in layout_dirs.keys() else 1
    check_overlays(script)
    num_base_scenes = len([sc for sc in script.scenes if not sc.is_overlay and not sc.is_after])
    if num_base_scenes < nrows*ncols:
        print("Please note: grid is supposed to be {} by {}, but only {} base scenes were found, this might be intended"
              " but double-check your `$ layout` settings".format(nrows, ncols, num_base_scenes))
    elif num_base_scenes > nrows*ncols:
        print("Some scenes were not included in the grid definition, please check your `$ layout` settings")
    for scene in sorted(script.scenes, key=lambda sc: int(sc.is_overlay), reverse=True):
        if scene.contour:
            for fr in range(scene.total_frames):
                img = "{}-{}.png".format(scene.name, fr)
                call_moly('{conv} {img} -canny 0x1+10%+40% -negate -transparent white -blur 0x0.75 border.png; '
                          'composite border.png {img} {img}'.format(conv=script.convert, img=img), log=script.log)
        for action in scene.actions:  # due to sorting, scenes without dependencies should be composed first
            if 'add_overlay' in action.action_type:
                for ovl in action.overlays.keys():
                    if 'scene' in action.overlays[ovl].keys():
                        ovl_scene_name = action.overlays[ovl]['scene']
                        ovl_scene = [sc for sc in script.scenes if sc.name == ovl_scene_name][0]
                        overlay_res = calc_ores(action, ovl, range(ovl_scene.total_frames), True)
                        for fr, ores in zip(range(ovl_scene.total_frames), overlay_res):
                            call_moly('{} {}-{}.png -resize {}x{} '
                                      '{}-{}-{}.png'.format(script.convert, ovl_scene_name, fr, *ores, ovl, scene.name,
                                                            fr + action.initframe), log=script.log)
                compose_overlay(action)

    if nrows * ncols == 1:  # simplest case: one scene
        scene = script.scenes[0].name
        for fr in range(np.max([sc.total_frames for sc in script.scenes])):
            if not (script.restart and os.path.exists('{}-{}.png'.format(script.name, fr))):
                os.rename('{}-{}.png'.format(scene, fr), '{}-{}.png'.format(script.name, fr))

    elif layout_dirs and nrows * ncols > 1:  # here we parse multiple scenes
        # if one has less frames than the other, copy last frame (N-n) times to make counts equal:
        if not all([sc.total_frames == script.scenes[0].total_frames for sc in script.scenes if not sc.is_overlay]):
            equalize_frames(script)
        labels_matrix = [[] for _ in range(nrows)]
        all_scenes = [sc.name for sc in script.scenes]
        positions = {}
        for scene in all_scenes:
            try:
                positions[tuple(int(x) for x in script.directives[scene]['position'].split(','))] = scene
            except KeyError:
                raise ValueError('The position for scene {} in the global layout is not specified'.format(scene))
        for r in range(nrows):
            for c in range(ncols):
                try:
                    scene_name = positions[(r, c)]
                except KeyError:
                    labels_matrix[r].append('')
                else:
                    labels_matrix[r].append(scene_name)
        convert_command = ''
        for r in range(nrows):
            convert_command += ' \( '
            for c in range(ncols):
                convert_command += str(labels_matrix[r][c]) + '-{}.png '
            convert_command += ' +append \) '
        convert_command += ' -append '
        for fr in range(script.scenes[0].total_frames):
            frames = [fr] * (nrows * ncols)
            call_moly(script.convert + ' ' + convert_command.format(*frames) + '{}-{}.png'.format(script.name, fr),
                      log=script.log, quiet=True)

    process_audio(script)


def check_overlays(script):
    """
    Ensures that dependent overlays (i.e. Scenes
    that will be rendered atop other Scenes)
    are properly defined, and calculates level
    of nesting for subsequent ordering of
    rounds of Scene composition
    :param script: Script instance, the master object controlling the movie layout
    :return: None
    """

    def return_dependencies(scn):
        dps = []
        for action in scn.actions:
            if 'add_overlay' in action.action_type:
                for ovl in action.overlays.keys():
                    if 'scene' in action.overlays[ovl].keys():
                        ovl_scene_name = action.overlays[ovl]['scene']
                        try:
                            dps.append([sc for sc in script.scenes if sc.name == ovl_scene_name][0])
                        except IndexError:
                            raise RuntimeError("In action {}, scene={} is not a valid scene "
                                               "identifier".format(action.description, ovl_scene_name))
        return dps

    all_deps = []
    for scene in script.scenes:
        all_deps.extend(return_dependencies(scene))
    indeps = [sc for sc in script.scenes if sc not in all_deps]
    for indep in indeps:
        deps = return_dependencies(indep)
        incr = 1
        while deps:
            new_deps = []
            for dep in deps:
                dep.is_overlay += incr
                new_deps.extend(return_dependencies(dep))
            deps = new_deps[:]
            incr += 1


def gen_fig(action):
    """
    Responsible for frame-by-frame generation of files
    associated with (a) external images and (b)
    on-the-fly generated matplotlib plots
    (essentially any graphics that is not rendered
    by TCL/VMD)
    :param action: Action, object to extract info from
    :return: None
    """
    if 'show_figure' in action.action_type:
        gen_fig_show(action)
    if 'add_overlay' in action.action_type:
        for ovl in action.overlays.keys():
            gen_ovl(action, ovl)


def add_master_overlays(script):
    if 'layout' in script.directives.keys():
        resolution = get_resolution(script)
    else:
        resolution = [max([scene.resolution[0] for scene in script.scenes if not scene.is_overlay]),
                      max([scene.resolution[1] for scene in script.scenes if not scene.is_overlay])]
    for ovl_action in script.master_overlays:
        ovl_action.scene.resolution = resolution
        gen_ovl(ovl_action, list(ovl_action.overlays.keys())[0], master=True)
        compose_overlay(ovl_action, master=True)


def get_resolution(script):
    layout_dirs = script.directives['layout']  # layout controls composition of panels
    nrows = int(layout_dirs['rows']) if 'rows' in layout_dirs.keys() else 1
    ncols = int(layout_dirs['columns']) if 'columns' in layout_dirs.keys() else 1
    xres = 0
    yres = 0
    for row in range(nrows):
        scenes_in_row_width = sum([sc.resolution[0] for sc in script.scenes if sc.position[0] == row])
        xres = max([xres, scenes_in_row_width])
    for col in range(ncols):
        scenes_in_col_height = sum([sc.resolution[1] for sc in script.scenes if sc.position[1] == col])
        yres = max([yres, scenes_in_col_height])
    return xres, yres


def gen_fig_show(action):
    """
    Generates a static figure whem action is `show_figure`
    :param action: The Action object to draw data from
    :return: None
    """
    convert = action.scene.script.convert
    if 'figure' in action.parameters.keys():
        fig_file = action.parameters['figure']
        fig_file = action.scene.script.check_path(fig_file)
        for fr in range(action.initframe, action.initframe + action.framenum):
            call_moly('{} {} -resize {}x{} {}-{}.png'.format(convert, fig_file, *action.scene.resolution,
                                                             action.scene.name, fr), log=action.scene.script.log)
    elif 'datafile' in action.parameters.keys():
        df = action.parameters['datafile']
        df = action.scene.script.check_path(df)
        data_simple_plot(action, df, 'spl')
        for fr in range(action.initframe, action.initframe + action.framenum):
            fig_file = '{}-{}.png'.format(action.scene.name, fr)
            call_moly('{} spl-{} -resize {}x{} {}'.format(convert, fig_file, *action.scene.resolution, fig_file),
                      log=action.scene.script.log)


def gen_ovl(action, ovl, master=False):
    """
    Handles the generation of dynamic overlays (figures,
    text, plots, movies) as requested by `add_overlay`
    :param action: The Action object to draw data from
    :param ovl: str, key for the Action.overlays dictionary
    :return: None
    """
    if "scene" not in action.overlays[ovl].keys():
        print("Rendering overlays for scene {}, currently: {}".format(action.scene.name, ovl))
    convert = action.scene.script.convert
    scene = action.scene.name
    res = action.scene.resolution
    frames, actions = calc_frames_ud(action, ovl, master)
    overlay_res = calc_ores(action, ovl, frames, default=True, master=master)
    if 'figure' in action.overlays[ovl].keys():
        fig_file = action.overlays[ovl]['figure']
        if fig_file not in ['f', 'false', 'n', 'no', '0']:
            fig_file = action.scene.script.check_path(fig_file)
            for fr, ores in zip(frames, overlay_res):
                ovl_file = '{}-{}-{}.png'.format(ovl, scene, fr)
                call_moly('{} {} -resize {}x{} {}'.format(convert, fig_file, *ores, ovl_file), log=action.scene.script.log)
    elif 'datafile' in action.overlays[ovl].keys():
        df = action.overlays[ovl]['datafile']
        if df not in ['f', 'false', 'n', 'no', '0']:
            df = action.scene.script.check_path(df)
            data_simple_plot(action, df, ovl, master)
            for fr, ores in zip(frames, overlay_res):
                fig_file = '{}-{}-{}.png'.format(ovl, scene, fr)
                call_moly('{} {} -resize {}x{} {}'.format(convert, fig_file, *ores, fig_file), log=action.scene.script.log)
    elif 'text' in action.overlays[ovl].keys():
        plt.rcParams['mathtext.default'] = 'regular'
        text = action.overlays[ovl]['text']
        scaling_text = ''
        tsize = int(32 * np.sqrt(int(res[0]) * int(res[1])) / (10 ** 3))
        try:
            tsize = int(float(action.overlays[ovl]['textsize']) * tsize)
        except KeyError:
            pass
        textcolors = {'red': 'B22222', 'blue': '2B6CC4', 'green': '008000', 'yellow': 'FFCF48',
                      'orange': 'FF8C00', 'purple': '8F509D'}
        try:
            box_params_raw = action.overlays[ovl]['textbox']
        except KeyError:
            box_params = {}
            text_origin = 0
        else:  # TODO check for correct formatting
            if box_params_raw in ['f', 'false', 'n', 'no', '0']:
                box_params = {}
                text_origin = 0
            else:
                box_params = {'boxstyle': "round", 'ec': (0.0, 0.0, 0.0), 'fc': (1.0, 1.0, 1.0), 'alpha': 0.8,
                              'lw': tsize*0.1}
                text_origin = 0.002 * tsize
                if box_params_raw not in ['t', 'true', 'y', 'yes', '1']:
                    box_params_raw = box_params_raw.split(',')
                    param_maps = {'style': 'boxstyle', 'background_color': 'fc', 'line_color': 'ec'}
                    for param_pair in box_params_raw:
                        boxkey, boxval = param_pair.split(':')
                        bkey = param_maps[boxkey] if boxkey in param_maps.keys() else boxkey
                        try:
                            box_params[bkey] = eval(boxval)
                        except NameError:
                            box_params[bkey] = boxval
        try:
            color = action.overlays[ovl]['textcolor']
        except KeyError:
            tcolor = 'black'
        else:
            if color in ['f', 'false', 'n', 'no', '0']:
                tcolor = 'black'
            else:
                try:
                    tcolor = '#{}'.format(textcolors[color.lower()])
                except KeyError:
                    tcolor = color

        try:
            animation_frames = [float(x) for x in action.overlays[ovl]['dataframes'].split(':')]
            arr = np.linspace(animation_frames[0], animation_frames[1], len(frames))
        except KeyError:
            if '[' in text and ']' in text and '[]' not in text:
                scaling_text = text.split('[')[1].split(']'[0])[0]
                try:
                    _ = [int(x) for x in action.parameters['frames'].split(':')]
                except (KeyError, AttributeError):
                    raise RuntimeError("When the [scaling_factor] syntax is used, an 'animate' action"
                                       "has to specify 'frames' simultaneously")
                else:
                    arr = calc_frames_arr(actions)
            else:
                arr = np.arange(len(frames))
        try:
            fig = plt.figure(figsize=[r / 100 for r in res])
        except RuntimeError:
            plt.switch_backend('agg')
            fig = plt.figure(figsize=[r / 100 for r in res])
        text_dict = {'ha': 'left', 'va': 'bottom', 'ma': 'center', 'clip_on': False, 'size': tsize, 'color': tcolor,
                     'wrap': True}
        if box_params:
            text_dict.update({'bbox': box_params})
        if '[' in text and ']' in text:
            try:
                dpt = action.overlays[ovl]['decimal_points']
            except KeyError:
                dpt = '3'
            for fr in frames:
                scaler = float(scaling_text) if scaling_text else 1.0
                newtext = text.replace('[{}]'.format(scaling_text),
                                       '{:.' + dpt + 'f}').format(arr[fr - action.initframe] * scaler)
                fig_file = '{}-{}-{}.png'.format(ovl, scene, fr)
                plt.clf()
                _ = fig.text(text_origin, text_origin, newtext, **text_dict)
                plt.savefig(fig_file, transparent=True)
        else:
            templ_file = '{}-{}-x.png'.format(ovl, scene)
            plt.clf()
            if '\\n' in text:
                text = text.replace('\\n', '\n')
            _ = fig.text(text_origin, text_origin, text, **text_dict)
            plt.savefig(templ_file, transparent=True)
            for fr in frames:
                fig_file = '{}-{}-{}.png'.format(ovl, scene, fr)
                copy2(templ_file, fig_file)
            os.remove(templ_file)
    elif 'movie' in action.overlays[ovl].keys():
        basename = '{}-{}-%d.png'.format(ovl, scene)
        movie = action.overlays[ovl]['movie']
        try:
            start = action.overlays[ovl]['from'].rstrip('s')
        except KeyError:
            start = 0
        try:
            time = float(action.overlays[ovl]['length'])
        except KeyError:
            time = action.framenum / action.scene.script.fps
        fps = float(action.framenum) / time
        time += 1 / fps
        timespec = "-ss {} -t {} ".format(start, time)
        call_moly('{} -i {} {} -vf fps={} {} -hide_banner'.format(action.scene.script.ffmpeg, movie, timespec, fps,
                                                                  'tmp_' + basename), log=action.scene.script.log)
        initframe = frames[0]
        totalframes = len(frames)
        for i, ores, n in zip(range(totalframes, 0, -1), overlay_res[::-1], range(totalframes)):
            orig = 'tmp_{ov}-{sc}-{nr}.png'.format(ov=ovl, sc=scene, nr=i)
            modd = '{ov}-{sc}-{fr}.png'.format(ov=ovl, sc=scene, fr=i + initframe - 1)
            if n % 10 == 0:
                print('processing frame {} of movie {}'.format(n, movie))
            call_moly('{} {} -resize {}x{} {}'.format(convert, orig, *ores, modd), log=action.scene.script.log)
            os.remove(orig)


def show_grid(action):
    # TODO adjust
    convert = action.scene.script.convert
    frame = action.initframe - 1
    scene = action.scene.name
    call_moly('{cv} {sc}-{fr}.png \( +clone -colorspace gray -fx '
              '"(i==int(w/10)||i==2*int(w/10)||i==3*int(w/10)||i==4*int(w/10)||i==5*int(w/10)||'
              'i==6*int(w/10)||i==7*int(w/10)||i==8*int(w/10)||i==9*int(w/10)||'
              'j==int(h/10)||j==2*int(h/10)||j==3*int(h/10)||j==4*int(h/10)||j==5*int(h/10)||'
              'j==6*int(h/10)||j==7*int(h/10)||j==8*int(h/10)||j==9*int(h/10))?0:1" \)'
              ' -compose darken -composite grid-{sc}-{fr}.png'.format(cv=convert, fr=frame, sc=scene))


def calc_ores(action, ovl, frames, default=False, master=False):
    """
    Calculates per-frame overlay resolutions
    in case relative size is scaled linearly
    :param action: Action or SimultaneousAction instance
    :param ovl: str, name of the overlay
    :param frames: iterable, enumerates all frames overlay should apply to
    :param default: bool, whether a default should be provided or error raised when relative_size is not defined
    :return: list of 2-element lists: [[x_res, y_res] for frame in frames]
    """
    res = action.scene.resolution
    _, actions = calc_frames_ud(action, ovl, master)
    # try:
    #     scaling = action.overlays[ovl]['relative_size']
    if not any('relative_size' in act.overlays[ovl].keys() for act in actions
               if hasattr(act, 'overlays') and ovl in act.overlays.keys()):
        # except KeyError:
        if default:
            overlay_res = [[r for r in res] for _ in range(len(frames))]
        else:
            raise RuntimeError("With add_overlay, 'relative_size=... has to be specified")
    else:
        sizes = extract_value_actions(actions, ovl, 'relative_size')
        overlay_res = [[r*val[0] for r in res] for val in sizes]
        # if ':' in scaling:
        #     linear = True if '::' in scaling else False
        #     scaling = scaling.replace('::', ':')
        #     initial = float(scaling.split(':')[0])
        #     final = float(scaling.split(':')[1])
        #     if linear:
        #         scale = np.linspace(0, 1, action.framenum)
        #     else:
        #         q = np.linspace(-5, 5, action.framenum)
        #         scale = 1 / (1 + np.exp(-q))
        #     overlay_res = [[sc * r for r in res] for sc in initial + scale * (final - initial)]
        # else:
        #     overlay_res = [[float(scaling) * r for r in res] for _ in range(action.framenum)]
        # if len(frames) > action.framenum:
        #     overlay_res.extend([overlay_res[-1] for _ in range(len(frames) - action.framenum)])
    return overlay_res


def equalize_frames(script):
    """
    If individual scenes have different frame counts,
    this function appends the corresponding last figure
    to the shorter scenes
    :param script: Script instance, the master object controlling the movie layout
    :return: None
    """
    nframes = [sc.total_frames for sc in script.scenes]
    names = [sc.name for sc in script.scenes]
    highest = max(nframes)
    for n, nf in enumerate(nframes):
        if nf < highest:
            for i in range(nf, highest):
                copy2('{}-{}.png'.format(names[n], nf - 1), '{}-{}.png'.format(names[n], i))


def compose_overlay(action, master=False):
    """
    Introduces the overlay provided that the picture
    ('overlay-frame_name.png') was already produced
    and properly scaled by gen_fig
    :param action: Action or SimultaneousAction, object to extract data from
    :param master: bool, whether to compose with the final frames (for master_overlays)
    :return: None
    """
    assert hasattr(action, 'overlays') and isinstance(action.overlays, dict)
    scene = action.scene.name
    res = action.scene.resolution
    for ovl in action.overlays.keys():
        frames, actions = calc_frames_ud(action, ovl, master)
        try:
            sigmoid = action.overlays[ovl]['sigmoid']
        except KeyError:
            sigmoid = False
        else:
            sigmoid = True if sigmoid.lower() in ['true', 't', 'y', 'yes', '1'] else False
        if sigmoid:
            sgm_frames_init = int(0.05 * action.framenum)
            sgm_frames_final = int(0.05 * actions[-1].framenum)
            x_init = np.linspace(-5, 0, sgm_frames_init)
            x_final = np.linspace(0, 5, sgm_frames_final)
            sgm_init = 1 / (1 + np.exp(-x_init))
            sgm_final = 1 / (1 + np.exp(-x_final))
            opacity = np.concatenate((sgm_init, np.ones(len(frames) - (sgm_frames_init + sgm_frames_final)),
                                      sgm_final[::-1]))
        else:
            opacity = np.ones(len(frames))
        try:
            center = True if action.overlays[ovl]['center'].lower() in ['true', 't', 'y', 'yes', '1'] else False
        except KeyError:
            center = False
        if not any('angle' in act.overlays[ovl].keys() for act in actions
                   if hasattr(act, 'overlays') and ovl in act.overlays.keys()):
            angles = [0] * len(frames)
        else:
            angles = [x[0] for x in extract_value_actions(actions, ovl, 'angle', default=0)]
        # else:
            # if ':' in angle:
            #     angle_init, angle_final = [float(x) for x in angle.split(':')]
            #     angles = angle_init + (angle_final - angle_init) * np.array(1/(1+np.exp(-1*np.linspace(-5, 5,
            #                                                                                            len(frames)))))
            # else:
            #     check_if_convertible(angle, float, 'angle')
            #     angles = np.ones(len(frames)) * float(angle)
        if not any('origin' in act.overlays[ovl].keys() for act in actions
                   if hasattr(act, 'overlays') and ovl in act.overlays.keys()):
            # ori_x, ori_y = action.overlays[ovl]['origin'].split(',')
            origin_frac = [[0, 0] for _ in range(len(frames))]
        # except KeyError:
        #     origin_frac = [[0, 0] for _ in range(len(frames))]
        else:
            # def get_range(ori):
            #     linear = True if '::' in ori else False
            #     if ':' in ori:
            #         ori = ori.replace('::', ':')
            #         initial = float(ori.split(':')[0])
            #         final = float(ori.split(':')[1])
            #     else:
            #         initial = final = float(ori)
            #     return linear, ori, initial, final
            #
            # linear_x, ori_x, initial_x, final_x = get_range(ori_x)
            # linear_y, ori_y, initial_y, final_y = get_range(ori_y)
            # if linear_x:
            #     scale_x = np.linspace(0, 1, action.framenum)
            # else:
            #     q = np.linspace(-5, 5, action.framenum)
            #     scale_x = 1 / (1 + np.exp(-q))
            # if linear_y:
            #     scale_y = np.linspace(0, 1, action.framenum)
            # else:
            #     q = np.linspace(-5, 5, action.framenum)
            #     scale_y = 1 / (1 + np.exp(-q))
            # origin_frac = [[x, y] for x, y in zip(initial_x + scale_x * (final_x - initial_x),
            #                                       initial_y + scale_y * (final_y - initial_y))]
            # if len(frames) > action.framenum:
            #     origin_frac.extend([origin_frac[-1] for _ in range(len(frames) - action.framenum)])
            origin_frac = extract_value_actions(actions, ovl, 'origin')
        transp_bg = True if 'transparent_background' in action.overlays[ovl].keys() \
                            and action.overlays[ovl]['transparent_background'] in ['true', 't', 'y', 'yes', '1'] else False
        # try:
        #     alpha = action.overlays[ovl]['alpha']
        # except KeyError:
        if not any('alpha' in act.overlays[ovl].keys() for act in actions
                   if hasattr(act, 'overlays') and ovl in act.overlays.keys()):
            alpha = np.ones(np.sum([act.framenum for act in actions]).astype(int))
        else:
            # if ':' in alpha:
            #     linear_a = True if '::' in alpha else False
            #     alpha = alpha.replace('::', ':')
            #     if linear_a:
            #         alpha = np.linspace(float(alpha.split(':')[0]), float(alpha.split(':')[1]), action.framenum)
            #     else:
            #         q = np.linspace(-5, 5, action.framenum)
            #         sgm = 1 / (1 + np.exp(-q))
            #         alpha = float(alpha.split(':')[0]) + sgm * (float(alpha.split(':')[1]) -
            #         float(alpha.split(':')[0]))
            # else:
            #     alpha = float(alpha) * np.ones(len(frames))
            alpha = [x[0] for x in extract_value_actions(actions, ovl, 'alpha', default=1)]
        # if len(frames) > action.framenum:
        #     alp = [alpha]
        #     for ac in actions[1:-1]:
        #         if ac.framenum > 0:
        #             alp.append(np.ones(ac.framenum) * alp[-1][-1])
        #     completed = False
        #     if hasattr(actions[-1], 'overlays'):
        #         if ovl in actions[-1].overlays.keys():
        #             if actions[-1].overlays[ovl]['mode'] == 'd':
        #                 if 'alpha' in actions[-1].overlays[ovl].keys():
        #                     alp2 = actions[-1].overlays[ovl]['alpha']
        #                     if ':' in alp2:
        #                         alp.append(np.linspace(float(alp2.split(':')[0]), float(alp2.split(':')[1]),
        #                                                actions[-1].framenum))
        #                     else:
        #                         alp.append(np.ones(actions[-1].framenum) * np.array([float(alp2)]))
        #                     completed = True
        #     if not completed:
        #         alp.append(np.ones(actions[-1].framenum) * alp[-1][-1])
        #     alpha = np.concatenate(alp)
        origin_px = [[int(r * o) for r, o in zip(res, ofr)] for ofr in origin_frac]
        for fr, opa, al, opx, ang in zip(frames, opacity, alpha, origin_px, angles):
            if fr % 10 == 0:
                print('composing frame {} of scene {} with {}'.format(fr, action.scene.name, ovl))
            fig_file = '{}-{}-{}.png'.format(ovl, scene, fr)
            if master:
                target_fig = '{}-{}.png'.format(action.scene.script.name, fr)
            else:
                target_fig = '{}-{}.png'.format(scene, fr)
            opa *= al
            if transp_bg:
                call_moly('{} {} -transparent white {}'.format(action.scene.script.convert, fig_file, fig_file),
                          log=action.scene.script.log)
            if opa != 1:
                call_moly('{} {} -alpha set -channel a -evaluate multiply {} '
                          '+channel {}'.format(action.scene.script.convert, fig_file, opa, fig_file),
                          log=action.scene.script.log)
            grav = 'SouthWest' if not center else 'Center'
            opx[1] = opx[1] if not center else -1 * opx[1]
            if 'text' in action.overlays[ovl].keys():
                call_moly('convert {ov} -trim +repage {ov}'.format(ov=fig_file), log=action.scene.script.log)
            if ang > 0.0000001 or ang < -0.0000001:
                xang = ang % 360
                call_moly('convert -background "rgba(0,0,0,0)" -rotate "{ang}" {ov} {ov}'.format(ang=xang, ov=fig_file))
            call_moly('{} -gravity {} -compose atop -geometry +{}+{} '
                      '{} {} {}'.format(action.scene.script.compose, grav, *opx, fig_file, target_fig, target_fig),
                      log=action.scene.script.log)


def extract_value_actions(actions, ovl, value, var_type=float, default=0):
    """
    Takes a list of Actions that are spanned by a given overlay and calculates
    a frame-by-frame list of values of a given property (specified by `value`)
    so that intermediate Actions can modify the original value
    :param actions: list of Actions, actions affected by the overlay
    :param ovl: str, alias of the overlay
    :param value: str, name/keyword of the property to extract
    :param var_type: type, variable type (to be checked for compatibility of conversion)
    :param default: any, default value if not specified for 1st action
    :return: list of tuples, length equal to num of frames affected by the overlay
    """
    result = []
    lastval = default

    def generator(lin, start, end, nfr, abruptness=1):
        if lin:
            return np.linspace(start, end, nfr)
        else:
            sigm = np.array(1 / (1 + np.exp(-abruptness * np.linspace(-5, 5, nfr))))
            return start + (end - start) * sigm

    for act in actions:
        try:
            dir = act.overlays[ovl][value]
        except (KeyError, AttributeError):
            for _ in range(act.framenum):
                result.append(lastval)
        else:
            linear = [True if '::' in d else False for d in dir.split(',')]
            dir.replace('::', ':')
            dirs = [(d.split(':')[0], d.split(':')[-1]) for d in dir.split(',')]
            [check_if_convertible(q, var_type, value) for d in dirs for q in d]
            vals = [generator(l, var_type(d[0]), var_type(d[1]), act.framenum) for d, l in zip(dirs, linear)]
            for x in zip(*vals):
                result.append(x)
            if len(result) > 0:
                lastval = result[-1]
            else:  # special case if we have an add_overlay with length 0
                lastval = [generator(l, var_type(d[0]), var_type(d[1]), 1)[0] for d, l in zip(dirs, linear)]
    return result


def data_simple_plot(action, datafile, basename, master=False, save_to_file=True):
    """
    Creates a set of customizable 1D line plots
    or 2D hexbin plots based on a provided data file
    to e.g. accompany the display of an
    animated trajectory
    :param action: Action or SimultaneousAction, object to extract data from
    :param datafile: str, file containing the data to be plotted
    :param basename: str, base name of the image to be produced (e.g. 'overlay1')
    :param master: bool, whether corresponds to a master_overlay rather than a regular overlay
    :param save_to_file: bool, whether the plot is saved (for movie-making) or displayed (for preview)
    :return: None
    """
    font = {'size': 18}
    plt.rc('font', **font)
    plt.rc('axes', linewidth=2)
    res = action.scene.resolution
    legend = False
    frames, actions = calc_frames_ud(action, basename, master)
    try:
        asp_ratio = float(action.parameters['aspect_ratio'])
    except KeyError:
        asp_ratio = res[0] / res[1]
    plt.rcParams['figure.figsize'] = [4.8 * np.sqrt(asp_ratio), 4.8 / np.sqrt(asp_ratio)]
    os.environ.pop("XDG_SESSION_TYPE", None)
    try:
        if save_to_file:
            plt.clf()
        else:
            plt.close('all')
        fig = plt.figure()
    except RuntimeError:
        plt.switch_backend('agg')
        if save_to_file:
            plt.clf()
        else:
            plt.close('all')
        fig = plt.figure()
    datasets = []
    flag_setup = False
    raw_data = [line.strip() for line in open(datafile) if line.strip()]
    for line in raw_data:
        if not flag_setup and (line.startswith('#') or line.startswith('!')):
            flag_setup = True
            datasets.append({'setup': [], 'data': []})
        if not datasets:
            datasets.append({'setup': [], 'data': []})
        if flag_setup and not (line.startswith('#') or line.startswith('!')):
            flag_setup = False
        if flag_setup:
            datasets[-1]['setup'].append(line)
        else:
            datasets[-1]['data'].append([float(x) for x in line.split()])
    xmin, ymin, xmax, ymax = np.inf, np.inf, -np.inf, -np.inf
    xlim_set = False
    ylim_set = False
    labels = False
    for dset in datasets:
        dset['data'] = np.array(dset['data'])
        try:
            labels = [x.strip() for x in dset['setup'] if x.strip().startswith('#')][0]
        except IndexError:
            pass
        else:
            labels = labels.strip('#').strip().split(';')
        try:
            mpl_kw = [x.strip() for x in dset['setup'] if x.strip().startswith('!')][0]
        except IndexError:
            mpl_kw = {}
        else:
            mpl_kw = {x.split('=')[0]: x.split('=')[1] for x in mpl_kw.strip('!').strip().split()}
            for kw in mpl_kw.keys():
                try:
                    mpl_kw[kw] = eval(mpl_kw[kw])
                except:
                    pass
        if 'xlim' not in mpl_kw.keys():
            xmin = np.min(dset['data'][:, 0]) if np.min(dset['data'][:, 0]) < xmin else xmin
            xmax = np.max(dset['data'][:, 0]) if np.max(dset['data'][:, 0]) > xmax else xmax
        else:
            xmin, xmax = mpl_kw['xlim']
            mpl_kw.pop('xlim')
            xlim_set = True
        if 'ylim' not in mpl_kw.keys():
            ymin = np.min(dset['data'][:, 1]) if np.min(dset['data'][:, 1]) < ymin else ymin
            ymax = np.max(dset['data'][:, 1]) if np.max(dset['data'][:, 1]) > ymax else ymax
        else:
            ymin, ymax = mpl_kw['ylim']
            mpl_kw.pop('ylim')
            ylim_set = True
        dset['mpl'] = {}
        dset['mpl'].update(mpl_kw)
    if not labels:
        labels = ['Time', 'Value']
    if '2D' in action.overlays[basename].keys() and action.overlays[basename]['2D'].lower() in ['t', 'y',
                                                                                                'true', 'yes', '1']:
        if ('seaborn' in action.overlays[basename].keys() and
                action.overlays[basename]['seaborn'].lower() in ['t', 'y', 'true', 'yes', '1']):
            seaborn = True
        else:
            seaborn = False
            ax = fig.add_subplot(1, 1, 1)
        for dset in datasets:
            grid_x = np.min([int(np.sqrt(len(dset['data']) * asp_ratio) / 2), 100])
            grid_y = np.min([int(grid_x / asp_ratio), 100])
            if 'gridsize' not in dset['mpl'].keys():
                dset['mpl'].update({'gridsize': (grid_x, grid_y)})
            if 'bins' not in dset['mpl'].keys():
                dset['mpl'].update({'bins': 'log'})
            if 'mincnt' not in dset['mpl'].keys():
                dset['mpl'].update({'mincnt': 1})
            if seaborn:
                alpha = 0.6 if len(datasets) > 1 else 1
                ax = sns.kdeplot(*dset['data'].T, shade=True, shade_lowest=False, alpha=alpha)
            else:
                ax.hexbin(*dset['data'].T, zorder=0, **dset['mpl'])
    elif 'custom_plot' in action.overlays[basename].keys():
        plotfile = action.overlays[basename]['custom_plot']
        with open(plotfile, "r") as plfile:
            plotfile_content = plfile.read()
        namespace = {}
        exec(plotfile_content, namespace)
        loaded_function = [obj for obj in namespace.values() if callable(obj)][-1]
        ax = loaded_function()
    else:
        ax = fig.add_subplot(1, 1, 1)
        for nds, dset in enumerate(datasets):
            dset['dynamic'] = True
            if 'dynamic' in dset['mpl'].keys():
                if dset['mpl']['dynamic'] in ['f', 'false', 'n', 'no', '0']:
                    dset['mpl'].pop('dynamic')
                    dset['dynamic'] = False
            if 'lw' not in dset['mpl'].keys() and 'linewidth' not in dset['mpl'].keys():
                dset['mpl'].update({'lw': 3})
            # if cols > 2, we switch to dynamic lines
            if dset['data'].shape[1] == 2:
                if len(dset['data'][:, 0]) == 2 and dset['data'][0,0] == dset['data'][1,0]:
                    dset['dynamic'] = False
                    dx, dymin, dymax = float(dset['data'][0, 0]), float(dset['data'][0, 1]), float(dset['data'][1, 1])
                    ax.vlines(x=dx, ymin=dymin, ymax=dymax, **dset['mpl'])
                    if 'label' in dset['mpl']:
                        ax.text(dx, dymin + 0.05 * (dymax-dymin), dset['mpl']['label'], ha='right', va='bottom',
                                rotation='vertical')
                elif len(dset['data'][:, 0]) == 2 and dset['data'][0,1] == dset['data'][1,1]:
                    dset['dynamic'] = False
                    dy, dxmin, dxmax = float(dset['data'][0, 1]), float(dset['data'][0, 0]), float(dset['data'][1, 0])
                    ax.hlines(y=dy, xmin=dxmin, xmax=dxmax, **dset['mpl'])
                    if 'label' in dset['mpl']:
                        ax.text(dxmin + 0.05 * (dxmax-dxmin), dy, dset['mpl']['label'], ha='left', va='bottom')
                else:
                    if 'label' in dset['mpl']:
                        legend = True
                    ax.plot(dset['data'][:, 0], dset['data'][:, 1], zorder=nds, **dset['mpl'])
        xspread = xmax - xmin
        yspread = ymax - ymin
        xmarg = 0.0 if xlim_set else 0.1 * xspread
        ymarg = 0.0 if ylim_set else 0.025 * yspread
        ax.set_xlim(xmin - xmarg, xmax + xmarg)
        ax.set_ylim(ymin - ymarg, ymax + ymarg)
    draw_dynamic = True
    try:
        animation_frames = [int(x) for x in action.overlays[basename]['dataframes'].split(':')]
        arr = np.linspace(animation_frames[0], animation_frames[1], len(frames)).astype(int)
    except KeyError:
        try:
            arr = np.loadtxt(action.overlays[basename]['dataframes_from_file']).reshape(-1).astype(int)
        except KeyError:
            try:
                _ = [int(x) for x in action.parameters['frames'].split(':') if x != "last"]
            except (KeyError, AttributeError):
                draw_dynamic, arr = False, None
            else:
                maxlen = np.max([len(dset['data']) for dset in datasets])
                arr = calc_frames_arr(actions, maxlen=maxlen)
        else:
            if len(arr) != len(frames):
                arr = [arr[int(i)] for i in np.linspace(0, len(arr)-1, len(frames))]
    xticks, xlim = ax.get_xticks(), ax.get_xlim()  # prevents ticks/scaling from changing from frame to frame
    yticks, ylim = ax.get_yticks(), ax.get_ylim()  # which would normally happen with tight_layout
    xticks = [xt for xt in xticks if xlim[0] < xt < xlim[1]]
    yticks = [yt for yt in yticks if ylim[0] < yt < ylim[1]]
    if not save_to_file:
        frames = [0]
    for fr in frames:
        count = fr - action.initframe
        pts_drawn = 0
        lines_drawn = 0
        if draw_dynamic:
            for col, dset in enumerate(datasets):
                if not dset['dynamic']:
                    continue
                if dset['data'].shape[1] == 2:
                    try:
                        ax.scatter(dset['data'][arr[count], 0], dset['data'][arr[count], 1], ec='k',
                                   s=250, zorder=1, **dset['mpl'])
                    except:
                        pass
                    else:
                        pts_drawn += 1
                elif dset['data'].shape[1] > 2:
                    if 'lc' in dset['mpl'].keys():
                        ln_color = dset['mpl']['lc']
                    elif 'linecolor' in dset['mpl'].keys():
                        ln_color = dset['mpl']['linecolor']
                    else:
                        ln_color = 'C' + str(col)
                    try:
                        arrlen = arr[count].shape // 2
                        ax.plot(dset['data'][arr[count], :arrlen], dset['data'][arr[count], arrlen:], zorder=1, c=ln_color)
                    except:
                        pass
                    else:
                        lines_drawn += 1
        ax.set_xlim(xlim)
        ax.set_xticks(xticks)
        ax.set_ylim(ylim)
        ax.set_yticks(yticks)
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        if legend:
            ax.legend()
            legend = False
        plt.tight_layout(pad=0.5)
        if save_to_file:
            plt.savefig('{}-{}-{}.png'.format(basename, action.scene.name, fr))
        else:
            plt.show()
        for pt in range(pts_drawn):
            ax.collections.pop()
        for ln in range(lines_drawn):
            ax.lines.pop()


def calc_frames_ud(action, ovl, master=False):
    """
    If an action can have modes up (u), down (d) or up-down (ud),
    this function will match 'ups' with 'downs' to return the
    frame numbers and Actions covered by the current action's span
    :param action: Action, contains at least one add_overlay
    :param ovl: str, name of the overlay
    :return: iterator, enumerates frames spanned by the action
             list, contains Actions affected by the overlay
    """
    try:
        mode = action.overlays[ovl]['mode']
    except KeyError:
        mode = 'ud'
    else:
        if mode not in ['u', 'd', 'n', 'ud']:
            raise RuntimeError("In {}, mode should be 'u', 'd', 'n' or 'ud'".format(action.description))
    if mode == 'ud' or master:
        return range(action.initframe, action.initframe + action.framenum), [action]
    elif mode == 'u':
        action_index = action.scene.actions.index(action)
        try:
            alias = action.overlays[ovl]['alias']
        except KeyError:
            return range(action.initframe, action.scene.total_frames), action.scene.actions[action_index:]
        else:
            for act in action.scene.actions[action_index:]:
                try:
                    ovls = list(act.overlays.keys())
                except AttributeError:
                    ovls = []
                for ov in ovls:
                    try:
                        als = act.overlays[ov]['alias']
                    except KeyError:
                        pass
                    else:
                        try:
                            md = act.overlays[ov]['mode']
                        except KeyError:
                            pass
                        else:
                            if als == alias and md == 'd':
                                action_index_last = action.scene.actions.index(act)
                                return range(action.initframe, act.initframe + act.framenum), \
                                    action.scene.actions[action_index:action_index_last + 1]
            return range(action.initframe, action.scene.total_frames), action.scene.actions[action_index:]
    elif mode in 'nd':
        return range(0), []


def calc_frames_arr(actions, maxlen=None):
    arrs = []
    for ac in actions:
        try:
            animation_frames = [int(x) for x in ac.parameters['frames'].split(':')]
        except KeyError:
            animation_frames = 2 * [arrs[-1][-1]]
        except ValueError:
            if maxlen is not None:
                animation_frames = [int(a) if a != "last" else maxlen for a in ac.parameters['frames'].split(':')]
            else:
                raise RuntimeError("When used to guide overlays, 'animate' has to specify numerical values for frames, "
                                   "using 'last' is disallowed")
        if ac.framenum > 0:
            arrs.append(np.linspace(animation_frames[0], animation_frames[1], ac.framenum).astype(int))
    return np.concatenate(arrs)


def process_audio(scr):
    """
    Processes directives for the `add_audio` Action,
    yielding a list of relevant variables like starting
    poits, segment length, name of the file etc. then
    sorts the segments according to their starting times
    :param scr: The top-level Script object
    :return: None
    """
    for scene in scr.scenes:
        for action in scene.actions:
            if 'add_audio' in action.action_type:
                try:
                    audiofile = action.parameters['audiofile']
                except KeyError:
                    raise RuntimeError("To add a soundtrack, specify the audio file using 'audiofile=...'")
                else:
                    if not os.path.exists(os.path.expanduser(audiofile)):
                        raise RuntimeError("Audio file {} was not found in your filesystem".format(audiofile))
                try:
                    starttime = float(action.parameters['from'])
                except KeyError:
                    starttime = 0
                try:
                    length = float(action.parameters['length'])
                except KeyError:
                    length = 3600
                try:
                    volume = float(action.parameters['volume'])
                except KeyError:
                    volume = 1.0
                try:
                    fin = float(action.parameters['fade_in'])
                except KeyError:
                    fin = 1.0
                try:
                    fout = float(action.parameters['fade_out'])
                except KeyError:
                    fout = 1.0
                tp = namedtuple("audio", "audiofile, movie_inittime, file_inittime, length, volume, fadein, fadeout")
                scr.audio.append(tp(audiofile, action.initframe/scr.fps, starttime, length, volume, fin, fout))
    scr.audio.sort(key=lambda x: x[1])


def call_moly(arg, answer=False, log=False, quiet=False):
    """
    A wrapper to consistently take care of all external calls
    :param arg: str, a command to be run from the command line
    :param answer: bool, whether to return the captured output
    :param log: bool, whether to log the command to a file
    :return: str, captured output from the command
    """
    quiet_comm = ' > /dev/null 2>&1' if quiet else ''
    result = call(arg + quiet_comm, shell=True)
    if log:
        with open('command_line_log.moly', 'a') as outfile:
            outfile.write(arg + '\n')
    if answer:
        return result


def check_if_convertible(string, object_type, param_name):
    """
    Checks if the user-specified value can be converted
    to the desired data type
    :param string: user-specified value
    :param object_type: what type should 'string' be convertible to
    :param param_name: name of the parameter in question
    :return: None
    """
    try:
        _ = object_type(string)
    except ValueError:
        raise RuntimeError("'{}' must be {}, instead '{}' was given".format(param_name, object_type, string))
