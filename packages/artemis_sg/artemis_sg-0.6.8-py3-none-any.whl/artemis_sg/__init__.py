import platformdirs

app_name = "artemis_sg"

data_dir = platformdirs.user_data_dir(app_name, appauthor=False)
conf_dir = platformdirs.user_config_dir(app_name, appauthor=False)
