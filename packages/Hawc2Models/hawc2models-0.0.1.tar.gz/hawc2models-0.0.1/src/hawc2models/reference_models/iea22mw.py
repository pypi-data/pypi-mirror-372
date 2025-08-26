from pathlib import Path
import shutil


from src.hawc2models.utils import download
from src.hawc2models.reference_models._reference_model import ReferenceModel
from wetb.hawc2.htc_file import HTCFile


class IEA22MW(HTCFile, ReferenceModel):
    def __init__(self, folder='IEA-22-280-RWT-Monopile'):
        folder = Path(folder)
        if not folder.exists():
            f_lst = download('https://github.com/IEAWindSystems/IEA-22-280-RWT/archive/refs/heads/main.zip', unzip=True,
                             known_hash='f42b1b2368a22dfc6a8d340851e1598839df9461bc003d601e95be2d80294971')
            cache_dir = f_lst[0][:f_lst[0].index('IEA-22-280-RWT-main')] + \
                '/IEA-22-280-RWT-main/HAWC2/IEA-22-280-RWT-Monopile'
            shutil.copytree(cache_dir, folder, dirs_exist_ok=True)
            shutil.rmtree(folder / 'htc/_master')
            shutil.rmtree(folder / 'htc/DLC')
        HTCFile.__init__(self, folder / 'htc/iea_22mw_rwt_steps.htc')

        self.set_name('iea_22mw_rwt')

    def make_onshore(self):
        ReferenceModel.make_onshore(self)
        self.new_htc_structure.get_subsection_by_name('monopile').delete()
        base = self.new_htc_structure.orientation.base
        base.mbdy = 'tower'
        base.inipos = [0, 0, 0]
        self.new_htc_structure.orientation.get_subsection_by_name('monopile', field='mbdy1').delete()
        self.new_htc_structure.constraint.fix0.mbdy = 'tower'
        self.new_htc_structure.constraint.get_subsection_by_name('monopile', field='mbdy1').delete()
