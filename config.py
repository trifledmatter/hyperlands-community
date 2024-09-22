from loaders import config

def get_config_or_throw(name: str = "token") -> str:
    config_path = "./config.json"
    config_loader = config.ConfigLoader(config_path)

    config_loader.load()
    data = config_loader.get()

    if not config_loader.validate(config_path, ["token", "guild_id", "database"]):
        if not config_loader.has_error:
            print("error - could not find token, guild_id, or database in config.")
        raise LookupError("Config could not be validated.")
    
    if data is None:
        if not config_loader.has_error:
            print("error - could not find config data.")
        raise LookupError("Could not find data in the provided config.")
    
    return data[0].get(name)
    

