from enum import Enum


class ConfigType(Enum):
    KONECTY = "konecty"
    MONGO = "mongo"
    AI = "ai"


class Config:
    name: str
    type: ConfigType

    def __init__(self, name: str, type: ConfigType):
        self.name = name
        self.type = type

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type.value,
        }

    @classmethod
    def from_json(cls, json: dict):
        match json["type"]:
            case ConfigType.KONECTY.value:
                cfg = ConfigKonecy(name=json["name"], type=ConfigType.KONECTY)
                cfg.konecty_url = json["konecty_url"]
                cfg.konecty_token = json["konecty_token"]
                return cfg
            case ConfigType.MONGO.value:
                cfg = ConfigMongo(name=json["name"], type=ConfigType.MONGO)
                cfg.mongo_url = json["mongo_url"]
                return cfg
            case ConfigType.AI.value:
                cfg = ConfigAi(name=json["name"], type=ConfigType.AI)
                cfg.provider = json["provider"]
                cfg.model = json["model"]
                cfg.api_key = json["api_key"]
                return cfg
            case _:
                raise ValueError(f"Invalid config type: {json['type']}")

    def get_data(self):
        """Get all fields excluding name and type"""
        return {
            key: value
            for key, value in self.__dict__.items()
            if key not in ["name", "type"]
        }

    def to_env(self):
        return {}


class ConfigKonecy(Config):
    konecty_url: str
    konecty_token: str

    def to_dict(self):
        return {
            **super().to_dict(),
            "konecty_url": self.konecty_url,
            "konecty_token": self.konecty_token,
        }

    def to_env(self):
        return {
            "KONECTY_URL": self.konecty_url,
            "KONECTY_TOKEN": self.konecty_token,
        }


class ConfigMongo(Config):
    mongo_url: str

    def to_dict(self):
        return {
            **super().to_dict(),
            "mongo_url": self.mongo_url,
        }

    def to_env(self):
        return {
            "MONGO_URL": self.mongo_url,
        }


class ConfigAi(Config):
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str

    def to_dict(self):
        return {
            **super().to_dict(),
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
        }

    def to_env(self):
        return {
            "OPENAI_API_KEY": self.api_key,
        }
