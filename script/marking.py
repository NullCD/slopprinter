from IPython.core.magic import register_line_magic
from IPython import get_ipython
from pathlib import Path
from nenen88 import tempe
import json
import os

SM = None

try:
    from KANDANG import TEMPPATH, HOMEPATH
    TMP = Path(TEMPPATH)
    HOME = Path(HOMEPATH)
    SM = False
except ImportError:
    TMP = Path('/tmp')
    HOME = Path.home()
    SM = True

marked = Path(__file__).parent / 'marking.json'

SyS = get_ipython().system
CD = os.chdir

def purgeVAR():
    l = [
        'WebUI', 'Models', 'WebUI_Output', 'Extensions', 'Embeddings', 'UNET', 'VAE',
        'CKPT', 'LORA', 'TMP_CKPT', 'TMP_LORA', 'Forge_SVD', 'Adetailer', 'Upscalers'
    ]
    for v in l:
        if v in globals(): del globals()[v]

def getWebUIName(path):
    return json.load(open(path, 'r')).get('ui', None)

def setWebUIVAR(ui):
    default = ('extensions', 'embeddings', 'VAE', 'Stable-diffusion', 'Lora', 'ESRGAN')

    maps = {
        'Forge-Classic': default
    }

    ext, embed, vae, ckpt, lora, upscaler = maps.get(ui, (None,) * 6)

    WebUI = HOME / ui
    Models = WebUI / models 
    WebUI_Output = WebUI / output
    Extensions = WebUI / ext if ext else None
    Embeddings = Models / embed if embed else None
    VAE = Models / vae if vae else None
    CKPT = Models / ckpt if ckpt else None
    LORA = Models / lora if lora else None
    Upscalers = Models / upscaler if upscaler else None
    Adetailer = Models / adetailer if adetailer else None

    return WebUI, Models, WebUI_Output, Extensions, Embeddings, VAE, CKPT, LORA, Upscalers, Adetailer

if SM:
    @register_line_magic
    def clear_output_images(line):
        ui = getWebUIName(marked)
        # Unpack 10 values now
        _, _, output, _, _, _, _, _, _, _ = setWebUIVAR(ui)
        SyS(f"rm -rf {output}/* {HOME / '.cache/*'}")
        CD(HOME)
        print(f'{ui} outputs cleared.')

    @register_line_magic
    def uninstall_webui(line):
        ui = getWebUIName(marked)
        # Unpack 10 values now
        webui, _, _, _, _, _, _, _, _, _ = setWebUIVAR(ui)
        SyS(f"rm -rf {webui} {HOME / 'tmp'} {HOME / '.cache/*'}")
        print(f'{ui} uninstalled.')
        CD(HOME)
        get_ipython().kernel.do_shutdown(True)

if marked.exists():
    purgeVAR()

    ui = getWebUIName(marked)
    WebUI, Models, WebUI_Output, Extensions, Embeddings, VAE, CKPT, LORA, Upscalers, Adetailer = setWebUIVAR(ui)
    
    TMP_CKPT = TMP / 'ckpt'
    TMP_LORA = TMP / 'lora'

    tempe()
