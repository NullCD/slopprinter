from IPython.display import display, Image, clear_output
from IPython import get_ipython
from ipywidgets import widgets
from pathlib import Path
import subprocess
import argparse
import shlex
import json
import sys
import os
import re

SyS = get_ipython().system
CD = os.chdir
iRON = os.environ

REPO = {
    'Forge-Classic': '-b classic https://github.com/Haoming02/sd-webui-forge-classic Forge-Classic'
}

WEBUI_LIST = ['Forge-Classic']

def getENV():
    env = {
        'Colab': ('/content', '/content', 'COLAB_JUPYTER_TOKEN'),
        'Kaggle': ('/kaggle', '/kaggle/working', 'KAGGLE_DATA_PROXY_TOKEN')
    }
    for name, (base, home, var) in env.items():
        if var in iRON:
            return name, base, home
    return None, None, None

def getArgs():
    parser = argparse.ArgumentParser(description='WebUI Installer Script for Kaggle and Google Colab')
    parser.add_argument('--webui', required=True, help='Available WebUI: Forge-Classic')
    parser.add_argument('--civitai_key', required=True, help='CivitAI API key (Required)')
    parser.add_argument('--hf_read_token', default=None, help='Huggingface READ Token (Optional)')

    args, unknown = parser.parse_known_args()

    arg1 = args.webui.lower()
    arg2 = args.civitai_key.strip()
    arg3 = args.hf_read_token.strip() if args.hf_read_token else ''

    if not any(arg1 == option.lower() for option in WEBUI_LIST):
        print(f'{ERROR}: invalid webui option: "{args.webui}"')
        print(f'Available webui options: {", ".join(WEBUI_LIST)}')
        return None, None, None

    if not arg2:
        print(f'{ERROR}: CivitAI API key is missing.')
        return None, None, None
    if re.search(r'\s+', arg2):
        print(f'{ERROR}: CivitAI API key contains spaces "{arg2}" - not allowed.')
        return None, None, None
    if len(arg2) < 32:
        print(f'{ERROR}: CivitAI API key must be at least 32 characters long.')
        return None, None, None

    if not arg3: arg3 = ''
    if re.search(r'\s+', arg3): arg3 = ''

    selected_ui = next(option for option in WEBUI_LIST if arg1 == option.lower())
    return selected_ui, arg2, arg3

def getPython():
    v = '3.11'
    BIN = str(PY / 'bin')
    PKG = str(PY / f'lib/python{v}/site-packages')

    url = 'https://huggingface.co/gutris1/webui/resolve/main/env/KC-FC-Python311-Torch260-cu124.tar.lz4'
    fn = Path(url).name

    CD(Path(ENVBASE).parent)
    print(f"\n{ARROW} Installing Python Portable 3.11.13")

    SyS('sudo apt-get -qq -y install aria2 pv lz4 > /dev/null 2>&1')

    aria = f'aria2c --console-log-level=error --stderr=true -c -x16 -s16 -k1M -j5 {url} -o {fn}'
    p = subprocess.Popen(shlex.split(aria), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p.wait()

    SyS(f'pv {fn} | lz4 -d | tar -xf -')
    Path(f'/{fn}').unlink()

    sys.path.insert(0, PKG)
    if BIN not in iRON['PATH']:
        iRON['PATH'] = BIN + ':' + iRON['PATH']
    if PKG not in iRON['PYTHONPATH']:
        iRON['PYTHONPATH'] = PKG + ':' + iRON['PYTHONPATH']

    if ENVNAME == 'Kaggle':
        for cmd in [
            'pip install ipywidgets jupyterlab_widgets --upgrade'
        ]:
            SyS(f'{cmd} > /dev/null 2>&1')

def marking(p, n, u):
    t = p / n
    v = {'ui': u, 'launch_args': '', 'tunnel': ''}

    if not t.exists(): t.write_text(json.dumps(v, indent=4))

    d = json.loads(t.read_text())
    d.update(v)
    t.write_text(json.dumps(d, indent=4))

def key_inject(C, H):
    p = Path(nenen)
    v = p.read_text()
    v = v.replace("TOKET = ''", f"TOKET = '{C}'")
    v = v.replace("TOBRUT = ''", f"TOBRUT = '{H}'")
    p.write_text(v)

def install_tunnel():
    SyS(f'wget -qO {USR}/cl https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64')
    SyS(f'chmod +x {USR}/cl')

    bins = {
        'zrok': {
            'bin': USR / 'zrok',
            'url': 'https://github.com/openziti/zrok/releases/download/v1.1.11/zrok_1.1.11_linux_amd64.tar.gz'
        },
        'ngrok': {
            'bin': USR / 'ngrok',
            'url': 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz'
        }
    }

    for n, b in bins.items():
        if b['bin'].exists(): b['bin'].unlink()

        url = b['url']
        name = Path(url).name

        SyS(f'wget -qO {name} {url}')
        SyS(f'tar -xzf {name} -C {USR}')
        SyS(f'rm -f {name}')

def sym_link(U, M):
    cfg = {
        'sym': [
            f"rm -rf {M / 'Stable-diffusion/tmp_ckpt'} {M / 'Lora/tmp_lora'}"
        ],
        'links': [
            (TMP / 'ckpt', M / 'Stable-diffusion/tmp_ckpt'),
            (TMP / 'lora', M / 'Lora/tmp_lora')
        ]
    }

    [SyS(f'{cmd}') for cmd in cfg['sym']]
    [(M / d).mkdir(parents=True, exist_ok=True) for d in ['Lora', 'ESRGAN']]
    [SyS(f'ln -s {src} {tg}') for src, tg in cfg['links']]

def webui_req(U, W, M):
    CD(W)

    pull(f'https://github.com/NullCD/slopprinter {U.lower()} {W}')

    sym_link(U, M)
    install_tunnel()

    scripts = [
        f'https://github.com/NullCD/slopprinter/raw/main/script/KC/segsmaker.py {W}'
    ]

    u = M / 'ESRGAN'

    upscalers = [
        f'https://huggingface.co/gutris1/webui/resolve/main/misc/4x-UltraSharp.pth {u}',
        f'https://huggingface.co/gutris1/webui/resolve/main/misc/4x-AnimeSharp.pth {u}'
    ]

    line = scripts + upscalers
    for item in line: download(item)

    e = 'jpg'
    SyS(f'rm -f {W}/html/card-no-preview.{e}')

    download(f'https://github.com/NullCD/slopprinter/raw/main/config/user.css {W} user.css')
    download(f'https://huggingface.co/CoreFSX/misc/resolve/main/card-no-preview.png {W}/html card-no-preview.{e}')
    download(f'https://github.com/NullCD/slopprinter/raw/main/config/config.json {W} config.json')

def webui_extension(U, W, M):
    EXT = W / 'extensions'
    CD(EXT)

    say('<br><b>【{red} Installing Extensions{d} 】{red}</b>')
    clone(str(W / 'asd/extension.txt'))
    if ENVNAME == 'Kaggle': clone('https://github.com/gutris1/sd-image-encryption')

def webui_installation(U, W):
    M = W / 'models'
    E = M / 'embeddings'
    V = M / 'VAE'

    webui_req(U, W, M)
    webui_extension(U, W, M)

def webui_selection(ui):
    with output:
        output.clear_output(wait=True)

        if ui in REPO: (WEBUI, repo) = (HOME / ui, REPO[ui])
        say(f'<b>【{{red}} Installing {WEBUI.name}{{d}} 】{{red}}</b>')
        clone(repo)

        webui_installation(ui, WEBUI)

        with loading:
            loading.clear_output(wait=True)
            say('<br><b>【{red} Done{d} 】{red}</b>')
            tempe()
            CD(HOME)

def webui_installer():
    branchs = {
        'Forge-Classic': 'classic'
    }

    CD(HOME)
    ui = (json.load(MARKED.open('r')) if MARKED.exists() else {}).get('ui')
    WEBUI = HOME / ui if ui else None

    if WEBUI is not None and WEBUI.exists():
        git_dir = WEBUI / '.git'
        if git_dir.exists():
            CD(WEBUI)
            with output:
                output.clear_output(wait=True)
                if ui in branchs: SyS(f'git pull origin {branchs[ui]}')
                with loading: loading.clear_output()
    else:
        try:
            webui_selection(webui)
        except KeyboardInterrupt:
            with loading: loading.clear_output()
            with output: print('\nCanceled.')
        except Exception as e:
            with loading: loading.clear_output()
            with output: print(f'\n{ERROR}: {e}')

def notebook_scripts():
    z = [
        (STR / '00-startup.py', f'wget -qO {STR}/00-startup.py https://github.com/gutris1/segsmaker/raw/main/script/KC/00-startup.py'),
        (nenen, f'wget -qO {nenen} https://github.com/gutris1/segsmaker/raw/main/script/nenen88.py'),
        (melon, f'wget -qO {melon} https://github.com/gutris1/segsmaker/raw/main/script/melon00.py'),
        (STR / 'cupang.py', f'wget -qO {STR}/cupang.py https://github.com/gutris1/segsmaker/raw/main/script/cupang.py'),
        (MRK, f'wget -qO {MRK} https://github.com/gutris1/segsmaker/raw/main/script/marking.py')
    ]

    [SyS(y) for x, y in z if not Path(x).exists()]

    j = {'ENVNAME': ENVNAME, 'HOMEPATH': HOME, 'TEMPPATH': TMP, 'BASEPATH': Path(ENVBASE)}
    text = '\n'.join(f"{k} = '{v}'" for k, v in j.items())
    Path(KANDANG).write_text(text)

    key_inject(civitai_key, hf_read_token)
    marking(SRC, MARKED, webui)
    sys.path.append(str(STR))

    for scripts in [nenen, melon, KANDANG, MRK]: get_ipython().run_line_magic('run', str(scripts))

ENVNAME, ENVBASE, ENVHOME = getENV()

if not ENVNAME:
    print('You are not in Kaggle or Google Colab.\nExiting.')
    sys.exit()

RESET = '\033[0m'
RED = '\033[31m'
PURPLE = '\033[38;5;135m'
ORANGE = '\033[38;5;208m'
ARROW = f'{ORANGE}▶{RESET}'
ERROR = f'{PURPLE}[{RESET}{RED}ERROR{RESET}{PURPLE}]{RESET}'
IMG = 'https://github.com/gutris1/segsmaker/raw/main/script/loading.png'

HOME = Path(ENVHOME)
TMP = Path(ENVBASE) / 'temp'

PY = Path('/GUTRIS1')
SRC = HOME / 'gutris1'
MRK = SRC / 'marking.py'
KEY = SRC / 'api-key.json'
MARKED = SRC / 'marking.json'

USR = Path('/usr/bin')
STR = Path('/root/.ipython/profile_default/startup')
nenen = STR / 'nenen88.py'
melon = STR / 'melon00.py'
KANDANG = STR / 'KANDANG.py'

TMP.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

output = widgets.Output()
loading = widgets.Output()

webui, civitai_key, hf_read_token = getArgs()
if civitai_key is None: sys.exit()

display(output, loading)
with loading: display(Image(url=IMG))
with output: PY.exists() or getPython()
notebook_scripts()

from nenen88 import clone, say, download, tempe, pull
webui_installer()
