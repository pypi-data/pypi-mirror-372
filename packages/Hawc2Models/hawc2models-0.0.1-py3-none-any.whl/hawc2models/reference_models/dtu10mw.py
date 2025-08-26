from pathlib import Path
import shutil


from src.hawc2models.utils import download
from src.hawc2models.reference_models._reference_model import ReferenceModel
from wetb.hawc2.htc_file import HTCFile


class DTU10MW(HTCFile, ReferenceModel):
    def __init__(self, folder='DTU_10MW_RWT'):
        folder = Path(folder)
        if not folder.exists():
            f_lst = download(
                'https://gitlab.windenergy.dtu.dk/rwts/dtu-10mw-rwt/-/archive/master/dtu-10mw-rwt-master.zip',
                known_hash='49c589e7a4b07b3c9ab5dbb88485b6a29fc36fb6df0524ad734eaa24ec86125d',
                unzip=True)
            cache_dir = f_lst[0][:f_lst[0].index('.zip.unzip')] + \
                '.zip.unzip/dtu-10mw-rwt-master/aeroelastic_models/hawc2'
            shutil.copytree(cache_dir, folder, dirs_exist_ok=True)
        HTCFile.__init__(self, folder / 'htc/DTU_10MW_RWT_wind_steps.htc')

        self.set_name('dtu_10mw_rwt')
