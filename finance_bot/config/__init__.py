from omegaconf import OmegaConf

from finance_bot.utility import get_project_folder

# 預設設定檔
DEFAULT_CONFIG = {

}


def load_config():
    """取得設定檔"""
    config = OmegaConf.create(DEFAULT_CONFIG)

    project_folder = get_project_folder()
    config_file = project_folder / 'conf.d' / 'config.yml'
    if not config_file.exists():
        raise ValueError('找不到設定檔 conf.d/config.yml')
    config.merge_with(OmegaConf.load(config_file))
    OmegaConf.set_readonly(config, True)

    return config


def reload():
    """重新取得設定檔"""
    global conf
    conf = load_config()


conf = load_config()
